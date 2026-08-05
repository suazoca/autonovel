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

Mecanismo (Tarea 9b -- corregido; la versión original de la Tarea 9 usaba
prefill y quedó rota): NO es prefill. El primer intento (Tarea 9) mandaba
el texto acumulado como último mensaje de la conversación con
`role: "assistant"`, sin turno de usuario después, para que la API lo
interpretara como "el asistente ya dijo esto, seguí escribiendo esta
misma respuesta". Confirmado contra la API real que Fable 5 lo rechaza
con 400: "This model does not support assistant message prefill. The
conversation must end with a user message." Los tests con mock nunca lo
habrían detectado porque el mock no valida reglas de la API real -- por
eso el chequeo contra la API real (ver abajo) es parte del criterio de
"terminado" para este mecanismo, no un extra.

Mecanismo actual: el texto acumulado va como contenido de un turno
`role: "assistant"` igual que antes (eso sí lo acepta la API -- lo que
rechaza es que sea el ÚLTIMO turno), seguido de un turno `role: "user"`
pidiendo explícitamente que continúe sin repetir texto ni agregar
comentario (`MENSAJE_CONTINUAR`). Como ya no es prefill literal, el
modelo ve el corte como el final de un turno propio y puede repetir la
última palabra o frase para que la continuación "cierre"
gramaticalmente -- exactamente el riesgo que el prefill evitaba por
construcción. `_recortar_solapamiento()` compara el sufijo del texto
acumulado contra el prefijo de cada continuación nueva y recorta la
parte repetida antes de concatenar, como red de seguridad para cuando la
instrucción no alcanza. Sigue sin garantizar que un corte a mitad de
palabra ("cami" de "camino") se complete correctamente -- eso dependía
del prefill literal y ya no está garantizado por la API; en la práctica
el modelo suele completar la palabra igual porque ve el corte en el
texto que "ya escribió", pero no es un contrato de la API como lo era el
prefill.

Antes de armar cada continuación se le aplica `.rstrip()` al texto
acumulado: ya no hace falta para cumplir una regla de la API (el turno
de assistant no es el último), pero evita un espacio de más en la
juntura si el corte cayó justo después de una palabra completa y la
continuación no aporta uno propio.

Costo: cada continuación reenvía el prompt original completo como
input (la API no tiene sesiones -- no hay forma de decir "seguí donde
estábamos" sin reenviar el contexto). Con `max_continuaciones` alto y
prompts grandes esto multiplica el costo de entrada por cada vuelta.

Cacheo de prompt (implementado y confirmado contra la API real -- antes
decía acá que faltaba, y que hacía falta una beta sin verificar; las
dos cosas eran incorrectas): `cache_control: {"type": "ephemeral"}` es
GA, no beta -- no hace falta ningún header extra ni decidir nada sobre
`anthropic-beta: context-1m-2025-08-07`. `llamar_api()` acepta `prompt`
como `str` (como siempre, sin cambios de comportamiento) o como
`list[dict]` con la forma `{"text": ..., "cache": bool}` -- ver
`_resolver_content()` más abajo. `draft_chapter.py::
build_prompt_bloques()` y `evaluate.py::_bloques_cache_chapter_prompt()`
arman esa lista separando lo estable en todo el libro (voz, mundo,
personajes, canon de fundación) de lo que cambia cada capítulo.
Verificado con una llamada de `max_tokens=16` real (Cap. 17, bloque
estable + canon emergente, ~50.000 tokens): primera llamada
`cache_creation_input_tokens=50085, cache_read_input_tokens=0`; segunda
llamada con el mismo prefijo, `cache_creation_input_tokens=0,
cache_read_input_tokens=50085`. Funciona.
"""
import json
import sys

import httpx


MENSAJE_CONTINUAR = (
    "Continuá exactamente desde donde quedaste, sin repetir ninguna "
    "palabra ni frase que ya hayas escrito y sin agregar comentarios, "
    "saludos ni explicaciones -- seguí la prosa directamente desde el "
    "corte."
)


def _resolver_content(prompt):
    """Convierte `prompt` al valor que va en `content` del turno de
    usuario. Dos formas de entrada:

    - `str` (comportamiento de siempre, sin cambios): se devuelve tal
      cual, como texto plano. Es lo que mandan los scripts que todavía
      no adoptaron cacheo de prompt.
    - `list[dict]` con la forma `{"text": ..., "cache": bool}` (nueva,
      Tarea de cacheo de prompt): se convierte a la lista de content
      blocks que espera la API, con `cache_control: {"type":
      "ephemeral"}` en los bloques marcados `cache: True`. Ver
      shared/prompt-caching.md del skill claude-api -- el cacheo es un
      *prefix match*: los bloques `cache: True` tienen que ir primero,
      en el mismo orden y con el mismo contenido byte a byte en cada
      llamada para pegarle al caché. `draft_chapter.py::
      build_prompt_bloques()` y `evaluate.py::evaluate_chapter()` arman
      esta lista poniendo primero lo que no cambia en todo el libro
      (voz, mundo, personajes, canon de fundación) y al final lo que
      cambia siempre (número de capítulo, esquema, texto del capítulo).

    No hace falta beta header: el cacheo con `cache_control: {"type":
    "ephemeral"}` es GA, no beta (a diferencia de lo que asumía una
    versión anterior de este docstring, que por eso nunca lo había
    implementado -- confirmado contra la documentación de la API, no
    contra una llamada real todavía; ver el chequeo de
    `cache_read_input_tokens` que hace `draft_chapter.py`/`evaluate.py`
    en el primer capítulo que lo use)."""
    if isinstance(prompt, str):
        return prompt
    bloques = []
    for seg in prompt:
        bloque = {"type": "text", "text": seg["text"]}
        if seg.get("cache"):
            bloque["cache_control"] = {"type": "ephemeral"}
        bloques.append(bloque)
    return bloques


def llamar_api(prompt, *, model, max_tokens, api_key, api_base, system=None,
                beta=None, timeout=120.0, max_continuaciones=5):
    """Llama a POST /v1/messages en modo streaming y devuelve el texto
    completo -- pidiendo continuaciones automáticas si la respuesta se
    corta por `stop_reason == "max_tokens"` (ver docstring del módulo
    para el mecanismo de continuación -- ya no es prefill -- y por qué
    `_recortar_solapamiento()` existe). `max_continuaciones` limita
    cuántas veces se puede volver a pedir más antes de rendirse -- 5 por
    defecto: cada vuelta reenvía el prompt completo, así que no es
    gratis dejarlo sin tope.

    Ignora por completo los deltas de bloques 'thinking' -- Fable 5 (y
    cualquier modelo con razonamiento extendido) manda esos bloques
    primero, y lo único que le importa a los scripts es el texto final.
    Cada continuación puede traer su propio bloque de thinking nuevo
    (es una llamada nueva a la API); también se ignora.

    Aborta con sys.exit (nunca con StopIteration/KeyError sin contexto)
    en cinco casos, todos con stop_reason/usage en el mensaje para
    poder diagnosticar sin tener que repetir la llamada -- ya se cobró:
      1. El stream manda un evento 'error' (p.ej. overloaded_error a
         mitad de generación, que puede pasar incluso después de un 200).
      2. Se agotan las `max_continuaciones` sin llegar a "end_turn".
      3. Se corta por max_tokens sin haber generado ni un carácter de
         texto (todo el presupuesto se fue en thinking) -- no hay nada
         con qué armar el turno de assistant de la continuación.
      4. El stream (tras juntar todas las continuaciones) termina sin
         haber acumulado ningún bloque de texto.
      5. `stop_reason == "refusal"` -- el clasificador de seguridad de
         Fable 5 rechazó la respuesta (confirmado en pruebas reales:
         pasa incluso con prompts inocuos, aparentemente un falso
         positivo). Sin este chequeo, el loop lo trataba igual que
         "end_turn" y devolvía el texto acumulado hasta ahí como si
         fuera la respuesta completa -- truncado a media frase, sin
         ningún aviso (hallazgo de la prueba contra la API real de la
         Tarea 9b, no algo que los tests con mock detectaran).

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

    prompt = _resolver_content(prompt)
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

        texto_nuevo, stop_reason, usage, stop_details = _llamada_streaming(
            headers, api_base, payload, timeout
        )

        if stop_reason == "refusal":
            sys.exit(
                f"ERROR: la API rechazó la respuesta (stop_reason=refusal) -- "
                f"el clasificador de seguridad la declinó, posiblemente un "
                f"falso positivo sobre contenido inocuo. No se devuelve texto: "
                f"{len(texto_acumulado)} caracteres acumulados en llamadas "
                f"previas quedarían truncados a media frase sin aviso si se "
                f"devolvieran como si fuera la respuesta completa. "
                f"stop_details={stop_details} usage={usage}"
            )

        texto_acumulado += _recortar_solapamiento(texto_acumulado, texto_nuevo)

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

        texto_acumulado = texto_acumulado.rstrip()
        if not texto_acumulado:
            sys.exit(
                f"ERROR: la respuesta se truncó por max_tokens sin producir "
                f"ningún texto (todo el presupuesto se fue en thinking) -- "
                f"no hay contenido con el que armar la continuación. "
                f"usage={usage}"
            )
        mensajes = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": texto_acumulado},
            {"role": "user", "content": MENSAJE_CONTINUAR},
        ]

    if not texto_acumulado:
        sys.exit(
            f"ERROR: sin bloque de texto en la respuesta. "
            f"stop_reason={stop_reason} usage={usage}"
        )

    return texto_acumulado


def _recortar_solapamiento(acumulado, nuevo, max_solapamiento=300):
    """Busca el mayor sufijo de `acumulado` que también aparece como
    prefijo de `nuevo` (hasta `max_solapamiento` caracteres) y lo recorta
    de `nuevo` antes de concatenar. Existe por la Tarea 9b: el mecanismo
    de continuación ya no es prefill literal (ver docstring del módulo),
    así que el modelo puede repetir la última palabra o frase de la
    continuación anterior para que el nuevo turno "cierre"
    gramaticalmente -- justo lo que el prefill evitaba por construcción.
    `MENSAJE_CONTINUAR` ya le pide explícitamente que no repita nada;
    esto es la red de seguridad para cuando no alcanza.

    Coincidencia exacta de caracteres nada más -- no intenta detectar
    paráfrasis ni reformulaciones. Con `acumulado == ""` (primera
    llamada, sin continuación previa) no hay nada que recortar y
    devuelve `nuevo` sin tocar."""
    limite = min(len(acumulado), len(nuevo), max_solapamiento)
    for longitud in range(limite, 0, -1):
        if acumulado[-longitud:] == nuevo[:longitud]:
            return nuevo[longitud:]
    return nuevo


def _llamada_streaming(headers, api_base, payload, timeout):
    """Una sola llamada POST /v1/messages en modo streaming. Devuelve
    (texto, stop_reason, usage, stop_details) de ESTA llamada nada más --
    acumular entre llamadas (para las continuaciones) es responsabilidad
    de llamar_api(), no de acá. `stop_details` solo viene poblado cuando
    `stop_reason == "refusal"` (categoría del rechazo, p.ej. "cyber" o
    "bio") -- en cualquier otro caso queda en None; llamar_api() lo usa
    nada más que para el mensaje de error si el clasificador de
    seguridad rechaza la respuesta."""
    texto = []
    tipos_bloque = {}
    stop_reason = None
    stop_details = None
    usage = None

    with httpx.stream(
        "POST", f"{api_base}/v1/messages", headers=headers, json=payload, timeout=timeout,
    ) as resp:
        if resp.status_code >= 400:
            resp.read()
            sys.exit(f"ERROR {resp.status_code} de la API: {resp.text}")
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
                delta = evento.get("delta", {})
                stop_reason = delta.get("stop_reason", stop_reason)
                stop_details = delta.get("stop_details", stop_details)
                usage = evento.get("usage", usage)

            elif tipo == "error":
                sys.exit(
                    f"ERROR: el stream de la API devolvió un evento de error -- "
                    f"{evento.get('error')} (stop_reason={stop_reason} usage={usage})"
                )

    return "".join(texto), stop_reason, usage, stop_details


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
