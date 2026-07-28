#!/usr/bin/env python3
"""
Cliente HTTP compartido para las llamadas a la API de Anthropic.

Reemplaza las 19 copias casi idénticas de call_writer()/call_judge()/
call_opus()/call_claude()/call_model()/call_reader() que tenía cada
script -- todas armaban el mismo POST a /v1/messages; lo único que
cambiaba entre ellas era `model`, `system`, `max_tokens`, `timeout` y a
veces el header `anthropic-beta`. Eso se sigue pasando como parámetro
por script, no se centraliza -- cada script conserva su propio
`call_writer()`/`call_judge()` como un wrapper de una línea sobre
`llamar_api()`, así que ningún sitio de llamada (`call_writer(prompt)`,
`call_writer(prompt, max_tokens=8000)`, etc.) cambia.

No es fundacion_comun.py porque ese módulo declara explícitamente "nada
de lo que hay acá llama a la API ni tiene efectos de red" y está acotado
a los generadores de fundación. Esto es lo opuesto: es la única red que
tocan los 19 scripts (fundación, redacción, evaluación, revisión).

Por qué streaming: con razonamiento adaptativo y max_tokens alto, una
respuesta puede tardar más que cualquier timeout fijo razonable -- se
genera igual, se cobra igual, y si el timeout salta antes de que
termine de llegar, se pierde sin dejar rastro (pasó: cuatro llamadas
pagadas sin archivo generado). En modo streaming el timeout que importa
es el de inactividad entre eventos, no la duración total del pedido --
httpx aplica sus timeouts por operación de red individual, así que cada
delta que llega lo resetea.

`timeout` default = 120s, igual para los 19 scripts (antes variaba
120/180/300/600s según cuánto tardaba esa llamada completa en la
práctica). OJO: el número bajó pero el timeout es más estricto, no más
laxo -- antes medía duración total del pedido, ahora mide silencio
entre eventos SSE. Un stream sano de un modelo con razonamiento
adaptativo manda un evento cada pocos segundos como mucho, nunca hay un
hueco de varios minutos con la conexión viva; 600s de "sin eventos"
nunca detectaría nada porque para cuando se cumplieran ya hace rato que
no hay nada escuchando del otro lado. 120s alcanza de sobra para el
hueco más largo esperable entre eventos y corta una conexión muerta en
dos minutos en vez de en diez.

Anthropic no está entre las dependencias del proyecto (solo httpx +
python-dotenv, ver pyproject.toml) -- se parsea SSE a mano en vez de
sumar el SDK oficial solo por esto.
"""
import json
import sys

import httpx


def llamar_api(prompt, *, model, max_tokens, api_key, api_base, system=None,
                beta=None, timeout=120.0):
    """Llama a POST /v1/messages en modo streaming y devuelve el texto
    acumulado (concatenación de todos los deltas de bloques tipo 'text').

    Ignora por completo los deltas de bloques 'thinking' -- Fable 5 (y
    cualquier modelo con razonamiento extendido) manda esos bloques
    primero, y lo único que le importa a los scripts es el texto final.

    Aborta con sys.exit (nunca con StopIteration/KeyError sin contexto)
    en dos casos, ambos con stop_reason/usage en el mensaje para poder
    diagnosticar sin tener que repetir la llamada -- ya se cobró:
      1. El stream manda un evento 'error' (p.ej. overloaded_error a
         mitad de generación, que puede pasar incluso después de un 200).
      2. El stream termina sin haber acumulado ningún bloque de texto.

    Errores HTTP (4xx/5xx) siguen sin capturarse acá -- se propaga la
    excepción de httpx tal como antes, sin cambio de comportamiento.
    """
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    if beta:
        headers["anthropic-beta"] = beta

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "stream": True,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        payload["system"] = system

    texto = []
    tipos_bloque = {}
    stop_reason = None
    usage = None

    with httpx.stream(
        "POST", f"{api_base}/v1/messages", headers=headers, json=payload, timeout=timeout,
    ) as resp:
        resp.raise_for_status()
        for evento in _eventos_sse(resp):
            tipo = evento.get("type")

            if tipo == "content_block_start":
                tipos_bloque[evento["index"]] = evento["content_block"]["type"]

            elif tipo == "content_block_delta":
                if tipos_bloque.get(evento["index"]) == "text":
                    delta = evento["delta"]
                    if delta.get("type") == "text_delta":
                        texto.append(delta["text"])

            elif tipo == "message_delta":
                stop_reason = evento.get("delta", {}).get("stop_reason", stop_reason)
                usage = evento.get("usage", usage)

            elif tipo == "error":
                sys.exit(
                    f"ERROR: el stream de la API devolvió un evento de error -- "
                    f"{evento.get('error')} (stop_reason={stop_reason} usage={usage})"
                )

    if not texto:
        sys.exit(
            f"ERROR: sin bloque de texto en la respuesta. "
            f"stop_reason={stop_reason} usage={usage}"
        )

    return "".join(texto)


def _eventos_sse(resp):
    """Parsea las líneas 'event: ...' / 'data: ...' de un stream SSE de
    /v1/messages a dicts. Ignora las líneas 'event:' -- el JSON de 'data:'
    ya trae su propio campo "type", que es lo único que se usa. Junta
    varias líneas 'data:' seguidas con '\\n' antes de decodificar, como
    exige la spec de SSE (Anthropic manda una sola por evento en la
    práctica, pero no vale asumirlo)."""
    data_lines = []
    for line in resp.iter_lines():
        if line == "":
            if data_lines:
                yield json.loads("\n".join(data_lines))
                data_lines = []
            continue
        if line.startswith("data:"):
            data_lines.append(line[len("data:"):].lstrip(" "))
    if data_lines:
        yield json.loads("\n".join(data_lines))
