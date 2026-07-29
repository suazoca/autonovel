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

Continuación automática cuando se corta por max_tokens (Tarea 9): pasó
dos veces en la primera corrida real -- outline.md cortó en Ch 23 de 46,
part2 cortó en Ch 42 -- porque nada avisaba que `stop_reason ==
"max_tokens"` significa "esto no es todo el texto". `llamar_api()` ahora
seguí pidiendo más hasta `stop_reason == "end_turn"` (o hasta agotar
`max_continuaciones`).

El mecanismo NO es "mandale la respuesta parcial y un mensaje de usuario
pidiendo que siga" -- es *prefill*: el texto acumulado se manda como el
último mensaje de la conversación con `role: "assistant"` (sin ningún
turno de usuario después). La API interpreta eso como "el asistente ya
dijo esto, seguí escribiendo esta misma respuesta" y el texto que
devuelve es pura continuación -- nunca repite el prefijo. Importa por
dos motivos:
  1. Cero riesgo de duplicar texto en la juntura: no hay nada que
     deduplicar porque el modelo nunca vuelve a generar lo que ya
     generó, a diferencia de pedirle "continuá" como mensaje nuevo (ahí
     sí podría reformular o repetir la última frase para que "cierre"
     gramaticalmente).
  2. Corta a mitad de palabra sin problema: si el texto quedó en "cami"
     (de "camino"), la continuación llega literalmente como "no..." y
     concatenar sin separador da "camino..." -- porque para el modelo
     no hay un límite de mensaje ahí, es la misma respuesta en curso.
     Pedirle que "continúe" como turno nuevo casi seguro reinicia la
     palabra en vez de completarla.
Antes de mandar el prefill se le aplica `.rstrip()`: la API rechaza un
mensaje de assistant que termine en espacio en blanco, y de paso evita
un doble espacio en la juntura si el corte cayó justo después de una
palabra completa (la continuación provee su propio espacio inicial si
hace falta).

Costo: cada continuación reenvía el prompt original completo como
input (la API no tiene sesiones -- no hay forma de decir "seguí donde
estábamos" sin reenviar el contexto). Con `max_continuaciones` alto y
prompts grandes (outline con mundo+personajes completos, capítulos con
esquema+voz+mundo+personajes) esto multiplica el costo de entrada por
cada vuelta. **No se implementó `cache_control` para la parte fija**
(el `system` y el prompt inicial, idénticos en cada reintento, son
candidatos obvios): el mecanismo es agregar `cache_control: {"type":
"ephemeral"}` al bloque de contenido a cachear, pero no hay forma de
verificar desde acá si el header beta que exige (y su compatibilidad
con `anthropic-beta: context-1m-2025-08-07`, que varios scripts ya
mandan) funciona con los modelos configurados en este entorno
(`claude-fable-5`/`claude-opus-5`) sin poder probar contra la API real.
Meter una beta sin verificar en un script que gasta plata de verdad es
peor que no cachear. Si se implementa: marcar el bloque de `system`
(cuando exista) y el prompt inicial con `cache_control`, confirmar con
una llamada barata que `usage.cache_read_input_tokens` > 0 en la
segunda vuelta antes de confiar en que está funcionando, y decidir qué
pasa con los headers `anthropic-beta` combinados.
"""
import json
import sys

import httpx


def llamar_api(prompt, *, model, max_tokens, api_key, api_base, system=None,
                beta=None, timeout=120.0, max_continuaciones=5):
    """Llama a POST /v1/messages en modo streaming y devuelve el texto
    completo -- pidiendo continuaciones automáticas si la respuesta se
    corta por `stop_reason == "max_tokens"` (ver docstring del módulo
    para el mecanismo de prefill y por qué no duplica ni pierde texto en
    la juntura). `max_continuaciones` limita cuántas veces se puede
    volver a pedir más antes de rendirse -- 5 por defecto: cada vuelta
    reenvía el prompt completo, así que no es gratis dejarlo sin tope.

    Ignora por completo los deltas de bloques 'thinking' -- Fable 5 (y
    cualquier modelo con razonamiento extendido) manda esos bloques
    primero, y lo único que le importa a los scripts es el texto final.
    Cada continuación puede traer su propio bloque de thinking nuevo
    (es una llamada nueva a la API); también se ignora.

    Aborta con sys.exit (nunca con StopIteration/KeyError sin contexto)
    en cuatro casos, todos con stop_reason/usage en el mensaje para
    poder diagnosticar sin tener que repetir la llamada -- ya se cobró:
      1. El stream manda un evento 'error' (p.ej. overloaded_error a
         mitad de generación, que puede pasar incluso después de un 200).
      2. Se agotan las `max_continuaciones` sin llegar a "end_turn".
      3. Se corta por max_tokens sin haber generado ni un carácter de
         texto (todo el presupuesto se fue en thinking) -- no hay nada
         con qué armar el prefill de la continuación.
      4. El stream (tras juntar todas las continuaciones) termina sin
         haber acumulado ningún bloque de texto.

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

    mensajes = [{"role": "user", "content": prompt}]
    texto_acumulado = ""
    continuaciones = 0
    stop_reason = None
    usage = None

    while True:
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "stream": True,
            "messages": mensajes,
        }
        if system:
            payload["system"] = system

        texto_nuevo, stop_reason, usage = _llamada_streaming(headers, api_base, payload, timeout)
        texto_acumulado += texto_nuevo

        if stop_reason != "max_tokens":
            break

        continuaciones += 1
        if continuaciones > max_continuaciones:
            sys.exit(
                f"ERROR: la respuesta se truncó por max_tokens "
                f"{max_continuaciones} veces seguidas sin llegar a "
                f"stop_reason=end_turn -- se aborta en vez de seguir "
                f"gastando. {len(texto_acumulado)} caracteres acumulados "
                f"hasta el corte. usage={usage}"
            )

        prefill = texto_acumulado.rstrip()
        if not prefill:
            sys.exit(
                f"ERROR: la respuesta se truncó por max_tokens sin producir "
                f"ningún texto (todo el presupuesto se fue en thinking) -- "
                f"no hay contenido con el que armar la continuación. "
                f"usage={usage}"
            )
        texto_acumulado = prefill
        mensajes = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": texto_acumulado},
        ]

    if not texto_acumulado:
        sys.exit(
            f"ERROR: sin bloque de texto en la respuesta. "
            f"stop_reason={stop_reason} usage={usage}"
        )

    return texto_acumulado


def _llamada_streaming(headers, api_base, payload, timeout):
    """Una sola llamada POST /v1/messages en modo streaming. Devuelve
    (texto, stop_reason, usage) de ESTA llamada nada más -- acumular
    entre llamadas (para las continuaciones) es responsabilidad de
    llamar_api(), no de acá."""
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

    return "".join(texto), stop_reason, usage


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
