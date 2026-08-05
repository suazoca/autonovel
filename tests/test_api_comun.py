"""
Tests de api_comun.llamar_api() -- el cliente de streaming compartido por
los 19 scripts que llaman a la API de Anthropic (Tarea 8). Nada de esto
llama a la red: se mockea httpx.stream() con un stream SSE armado a mano.
"""
import sys
from contextlib import contextmanager
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import api_comun


def _sse(*eventos_data):
    """Arma el cuerpo crudo de un stream SSE a partir de una lista de
    strings JSON ya serializados (uno por evento 'data:')."""
    return "".join(f"data: {d}\n\n" for d in eventos_data)


def _stream_falso(cuerpo, status_ok=True):
    """Reemplazo de httpx.stream(): devuelve un context manager que rinde
    un objeto con .status_code, .read(), .text e .iter_lines() sobre
    `cuerpo`. El mismo cuerpo se devuelve en cada llamada -- para tests
    de una sola llamada HTTP (sin continuación). `status_code` refleja
    el chequeo `if resp.status_code >= 400` de _llamada_streaming (ya no
    usa `raise_for_status()`)."""

    class _RespuestaFalsa:
        status_code = 200 if status_ok else 500
        text = "" if status_ok else "boom"

        def read(self):
            pass

        def iter_lines(self):
            for linea in cuerpo.split("\n"):
                yield linea

    @contextmanager
    def _stream(method, url, headers=None, json=None, timeout=None):
        yield _RespuestaFalsa()

    return _stream


def _stream_secuencia(cuerpos, capturas=None):
    """Como _stream_falso, pero devuelve un cuerpo distinto en cada
    llamada sucesiva a httpx.stream() -- simula una continuación real
    (Tarea 9), donde cada reintento es un POST nuevo. Si se pasa
    `capturas` (lista), guarda ahí el payload completo de cada llamada,
    en orden, para poder inspeccionar qué `messages` se mandó."""
    it = iter(cuerpos)

    class _RespuestaFalsa:
        status_code = 200

        def __init__(self, cuerpo):
            self._cuerpo = cuerpo

        def iter_lines(self):
            for linea in self._cuerpo.split("\n"):
                yield linea

    @contextmanager
    def _stream(method, url, headers=None, json=None, timeout=None):
        if capturas is not None:
            capturas.append(json)
        yield _RespuestaFalsa(next(it))

    return _stream


TEXTO_SIMPLE = _sse(
    '{"type": "message_start", "message": {"usage": {"input_tokens": 10}}}',
    '{"type": "content_block_start", "index": 0, "content_block": {"type": "thinking"}}',
    '{"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "pensando..."}}',
    '{"type": "content_block_stop", "index": 0}',
    '{"type": "content_block_start", "index": 1, "content_block": {"type": "text"}}',
    '{"type": "content_block_delta", "index": 1, "delta": {"type": "text_delta", "text": "Hola"}}',
    '{"type": "content_block_delta", "index": 1, "delta": {"type": "text_delta", "text": " mundo"}}',
    '{"type": "content_block_stop", "index": 1}',
    '{"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 5}}',
    '{"type": "message_stop"}',
)


def _llamar(monkeypatch, cuerpo, **kwargs):
    monkeypatch.setattr(api_comun.httpx, "stream", _stream_falso(cuerpo))
    defaults = dict(
        prompt="hola",
        model="claude-fable-5",
        max_tokens=100,
        api_key="fake-key",
        api_base="https://api.anthropic.com",
    )
    defaults.update(kwargs)
    return api_comun.llamar_api(**defaults)


def test_acumula_solo_los_deltas_de_texto(monkeypatch):
    resultado = _llamar(monkeypatch, TEXTO_SIMPLE)
    assert resultado == "Hola mundo"


def test_ignora_los_deltas_de_thinking(monkeypatch):
    # Si no ignorara 'thinking', "pensando..." aparecería en el resultado.
    resultado = _llamar(monkeypatch, TEXTO_SIMPLE)
    assert "pensando" not in resultado


def test_bloques_de_texto_no_contiguos_se_acumulan_en_orden(monkeypatch):
    cuerpo = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "uno"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "content_block_start", "index": 1, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 1, "delta": {"type": "text_delta", "text": " dos"}}',
        '{"type": "content_block_stop", "index": 1}',
    )
    resultado = _llamar(monkeypatch, cuerpo)
    assert resultado == "uno dos"


def test_sale_con_sys_exit_si_no_hay_bloque_de_texto(monkeypatch):
    # stop_reason=end_turn (no max_tokens) para que no dispare la lógica de
    # continuación de la Tarea 9 -- este test cubre el chequeo final, para
    # cuando la respuesta completa (diga lo que diga stop_reason) nunca
    # trajo ni un bloque de texto.
    cuerpo = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "thinking"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "solo pienso"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 500}}',
    )
    with pytest.raises(SystemExit) as exc:
        _llamar(monkeypatch, cuerpo)
    mensaje = str(exc.value)
    assert "sin bloque de texto" in mensaje
    assert "end_turn" in mensaje


def test_sale_con_sys_exit_si_el_stream_manda_un_evento_de_error(monkeypatch):
    cuerpo = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "algo"}}',
        '{"type": "error", "error": {"type": "overloaded_error", "message": "Overloaded"}}',
    )
    with pytest.raises(SystemExit) as exc:
        _llamar(monkeypatch, cuerpo)
    assert "overloaded_error" in str(exc.value)


def test_no_pasa_texto_parcial_si_el_stream_falla_luego_con_error(monkeypatch):
    # El texto acumulado antes del error no se devuelve -- sys.exit corta
    # la ejecución, no hay riesgo de guardar una respuesta a medias.
    cuerpo = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "algo"}}',
        '{"type": "error", "error": {"type": "api_error", "message": "boom"}}',
    )
    with pytest.raises(SystemExit):
        _llamar(monkeypatch, cuerpo)


def test_header_beta_se_manda_solo_si_se_pide(monkeypatch):
    capturado = {}

    @contextmanager
    def _stream_captura(method, url, headers=None, json=None, timeout=None):
        capturado["headers"] = headers
        capturado["json"] = json

        class _R:
            status_code = 200

            def iter_lines(self):
                for linea in TEXTO_SIMPLE.split("\n"):
                    yield linea

        yield _R()

    monkeypatch.setattr(api_comun.httpx, "stream", _stream_captura)
    api_comun.llamar_api(
        prompt="hola", model="m", max_tokens=10,
        api_key="k", api_base="https://x",
    )
    assert "anthropic-beta" not in capturado["headers"]

    api_comun.llamar_api(
        prompt="hola", model="m", max_tokens=10,
        api_key="k", api_base="https://x", beta="context-1m-2025-08-07",
    )
    assert capturado["headers"]["anthropic-beta"] == "context-1m-2025-08-07"


def test_payload_manda_stream_true_y_no_manda_temperature(monkeypatch):
    capturado = {}

    @contextmanager
    def _stream_captura(method, url, headers=None, json=None, timeout=None):
        capturado["json"] = json

        class _R:
            status_code = 200

            def iter_lines(self):
                for linea in TEXTO_SIMPLE.split("\n"):
                    yield linea

        yield _R()

    monkeypatch.setattr(api_comun.httpx, "stream", _stream_captura)
    api_comun.llamar_api(
        prompt="hola", model="m", max_tokens=10,
        api_key="k", api_base="https://x",
    )
    assert capturado["json"]["stream"] is True
    assert "temperature" not in capturado["json"]


def test_timeout_default_es_120_no_600(monkeypatch):
    # 120s por defecto = silencio entre eventos SSE, no duración total del
    # pedido -- ver docstring de llamar_api(). No debe quedar en el viejo
    # valor de "duración total" (600s), que con el nuevo significado
    # nunca detectaría una conexión muerta.
    capturado = {}

    @contextmanager
    def _stream_captura(method, url, headers=None, json=None, timeout=None):
        capturado["timeout"] = timeout

        class _R:
            status_code = 200

            def iter_lines(self):
                for linea in TEXTO_SIMPLE.split("\n"):
                    yield linea

        yield _R()

    monkeypatch.setattr(api_comun.httpx, "stream", _stream_captura)
    api_comun.llamar_api(
        prompt="hola", model="m", max_tokens=10,
        api_key="k", api_base="https://x",
    )
    assert capturado["timeout"] == 120.0


def test_system_se_omite_del_payload_si_no_se_pasa(monkeypatch):
    capturado = {}

    @contextmanager
    def _stream_captura(method, url, headers=None, json=None, timeout=None):
        capturado["json"] = json

        class _R:
            status_code = 200

            def iter_lines(self):
                for linea in TEXTO_SIMPLE.split("\n"):
                    yield linea

        yield _R()

    monkeypatch.setattr(api_comun.httpx, "stream", _stream_captura)
    api_comun.llamar_api(
        prompt="hola", model="m", max_tokens=10,
        api_key="k", api_base="https://x",
    )
    assert "system" not in capturado["json"]


# ---------------------------------------------------------------------------
# Continuación automática cuando se corta por max_tokens (Tarea 9;
# mecanismo de continuación corregido en la Tarea 9b -- ver docstring de
# api_comun.py: el prefill original quedó rechazado por Fable 5 con 400)
# ---------------------------------------------------------------------------

def test_end_turn_no_dispara_continuacion(monkeypatch):
    # TEXTO_SIMPLE ya termina en end_turn -- confirmar que solo se hace
    # UNA llamada HTTP (si continuara, el iterador de _stream_secuencia
    # reventaría con StopIteration al pedir un segundo cuerpo inexistente).
    monkeypatch.setattr(api_comun.httpx, "stream", _stream_secuencia([TEXTO_SIMPLE]))
    resultado = api_comun.llamar_api(
        prompt="hola", model="m", max_tokens=10, api_key="k", api_base="https://x",
    )
    assert resultado == "Hola mundo"


def test_continua_automaticamente_si_stop_reason_es_max_tokens(monkeypatch):
    primera_llamada = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hola"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "max_tokens"}, "usage": {"output_tokens": 100}}',
    )
    segunda_llamada = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": " mundo"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 3}}',
    )
    monkeypatch.setattr(
        api_comun.httpx, "stream",
        _stream_secuencia([primera_llamada, segunda_llamada]),
    )
    resultado = api_comun.llamar_api(
        prompt="hola", model="m", max_tokens=10, api_key="k", api_base="https://x",
    )
    assert resultado == "Hola mundo"


def test_empalme_no_pierde_ni_duplica_texto_a_mitad_de_palabra(monkeypatch):
    # Se corta literalmente en el medio de "camino" -- la continuación
    # completa la palabra sin repetir "cami" ni perder la "no".
    primera_llamada = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "cami"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "max_tokens"}, "usage": {"output_tokens": 100}}',
    )
    segunda_llamada = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "no al pueblo"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 4}}',
    )
    monkeypatch.setattr(
        api_comun.httpx, "stream",
        _stream_secuencia([primera_llamada, segunda_llamada]),
    )
    resultado = api_comun.llamar_api(
        prompt="hola", model="m", max_tokens=10, api_key="k", api_base="https://x",
    )
    assert resultado == "camino al pueblo"


def test_continuacion_manda_assistant_seguido_de_turno_de_usuario_pidiendo_continuar(monkeypatch):
    # Tarea 9b: Fable 5 rechaza con 400 que la conversación termine en un
    # turno de assistant ("This model does not support assistant message
    # prefill. The conversation must end with a user message."). El texto
    # parcial sigue yendo como turno de assistant -- eso sí lo acepta --
    # pero ahora va seguido de un turno de usuario pidiendo que continúe,
    # para que el assistant nunca sea el último mensaje.
    primera_llamada = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "cami"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "max_tokens"}, "usage": {"output_tokens": 100}}',
    )
    segunda_llamada = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "no"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 1}}',
    )
    capturas = []
    monkeypatch.setattr(
        api_comun.httpx, "stream",
        _stream_secuencia([primera_llamada, segunda_llamada], capturas=capturas),
    )
    api_comun.llamar_api(
        prompt="el prompt original", model="m", max_tokens=10, api_key="k", api_base="https://x",
    )
    assert len(capturas) == 2
    mensajes_segunda = capturas[1]["messages"]
    assert mensajes_segunda == [
        {"role": "user", "content": "el prompt original"},
        {"role": "assistant", "content": "cami"},
        {"role": "user", "content": api_comun.MENSAJE_CONTINUAR},
    ]
    # El último turno es de usuario, no de assistant -- lo que Fable 5 exige.
    assert mensajes_segunda[-1]["role"] == "user"


def test_texto_del_assistant_se_manda_sin_espacio_en_blanco_al_final(monkeypatch):
    # Ya no hace falta para cumplir una regla de la API (el turno de
    # assistant no es el último), pero evita un espacio de más en la
    # juntura si el corte cayó justo después de una palabra completa.
    primera_llamada = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hola   "}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "max_tokens"}, "usage": {"output_tokens": 100}}',
    )
    segunda_llamada = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": " mundo"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 3}}',
    )
    capturas = []
    monkeypatch.setattr(
        api_comun.httpx, "stream",
        _stream_secuencia([primera_llamada, segunda_llamada], capturas=capturas),
    )
    resultado = api_comun.llamar_api(
        prompt="hola", model="m", max_tokens=10, api_key="k", api_base="https://x",
    )
    texto_assistant_mandado = capturas[1]["messages"][-2]["content"]
    assert not texto_assistant_mandado.endswith(" ")
    assert resultado == "Hola mundo"


def test_recorta_solapamiento_si_la_continuacion_repite_la_ultima_palabra(monkeypatch):
    # Ya no es prefill literal (Tarea 9b): el modelo puede repetir la
    # última palabra/frase del texto acumulado para que su continuación
    # "cierre" gramaticalmente. Si "el camino" quedó cortado y la
    # continuación repite "camino" antes de seguir, no debe duplicarse.
    primera_llamada = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "el camino"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "max_tokens"}, "usage": {"output_tokens": 100}}',
    )
    segunda_llamada = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "camino largo"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 2}}',
    )
    monkeypatch.setattr(
        api_comun.httpx, "stream",
        _stream_secuencia([primera_llamada, segunda_llamada]),
    )
    resultado = api_comun.llamar_api(
        prompt="hola", model="m", max_tokens=10, api_key="k", api_base="https://x",
    )
    assert resultado == "el camino largo"


def test_recortar_solapamiento_no_toca_nada_si_no_hay_repeticion():
    assert api_comun._recortar_solapamiento("cami", "no al pueblo") == "no al pueblo"


def test_recortar_solapamiento_primera_llamada_sin_acumulado_previo():
    assert api_comun._recortar_solapamiento("", "cualquier cosa") == "cualquier cosa"


def test_recortar_solapamiento_recorta_el_mayor_sufijo_que_coincide():
    # "camino" coincide como sufijo de "el camino" y como prefijo de
    # "camino largo" -- debe recortar los 6 caracteres, no menos.
    assert api_comun._recortar_solapamiento("el camino", "camino largo") == " largo"


def test_tope_de_continuaciones_agotado_sale_con_sys_exit(monkeypatch):
    cuerpo_max_tokens = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "x"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "max_tokens"}, "usage": {"output_tokens": 100}}',
    )
    # 3 cuerpos alcanza: con max_continuaciones=2 se agota en la 3ra llamada.
    monkeypatch.setattr(
        api_comun.httpx, "stream",
        _stream_secuencia([cuerpo_max_tokens, cuerpo_max_tokens, cuerpo_max_tokens]),
    )
    with pytest.raises(SystemExit) as exc:
        api_comun.llamar_api(
            prompt="hola", model="m", max_tokens=10, api_key="k", api_base="https://x",
            max_continuaciones=2,
        )
    mensaje = str(exc.value)
    assert "max_tokens" in mensaje
    assert "2" in mensaje


def test_max_tokens_sin_texto_alguno_sale_con_sys_exit_sin_loopear(monkeypatch):
    # Todo el presupuesto se va en thinking, cero texto -- no hay con qué
    # armar el turno de assistant de la continuación, así que debe
    # abortar en la primera vuelta en vez de reintentar con un mensaje
    # de assistant vacío.
    cuerpo = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "thinking"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "..."}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "max_tokens"}, "usage": {"output_tokens": 100}}',
    )
    monkeypatch.setattr(api_comun.httpx, "stream", _stream_secuencia([cuerpo]))
    with pytest.raises(SystemExit) as exc:
        api_comun.llamar_api(
            prompt="hola", model="m", max_tokens=10, api_key="k", api_base="https://x",
        )
    assert "sin producir" in str(exc.value) or "prefill" in str(exc.value).lower()


# ---------------------------------------------------------------------------
# stop_reason == "refusal" (hallazgo de la prueba contra la API real de la
# Tarea 9b): el clasificador de seguridad de Fable 5 puede rechazar una
# respuesta -- incluso a mitad de una continuación, con texto real ya
# acumulado en llamadas previas. Sin manejo explícito, el loop lo trataba
# igual que "end_turn" y devolvía ese texto truncado como si fuera la
# respuesta completa, sin ningún aviso.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Cacheo de prompt: `prompt` como str (sin cambios) o como list[dict]
# {"text", "cache"} -- se convierte a content blocks con cache_control en
# los marcados cache=True. Ver api_comun._resolver_content() y el
# docstring del módulo.
# ---------------------------------------------------------------------------

def test_resolver_content_string_pasa_sin_cambios():
    assert api_comun._resolver_content("hola") == "hola"


def test_resolver_content_lista_arma_content_blocks_con_cache_control():
    resultado = api_comun._resolver_content([
        {"text": "estable", "cache": True},
        {"text": "volatil", "cache": False},
    ])
    assert resultado == [
        {"type": "text", "text": "estable", "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": "volatil"},
    ]


def test_resolver_content_lista_sin_cache_no_agrega_cache_control():
    resultado = api_comun._resolver_content([{"text": "sin cachear", "cache": False}])
    assert "cache_control" not in resultado[0]


def test_payload_manda_content_blocks_cuando_prompt_es_lista(monkeypatch):
    capturado = {}

    @contextmanager
    def _stream_captura(method, url, headers=None, json=None, timeout=None):
        capturado["json"] = json

        class _R:
            status_code = 200

            def iter_lines(self):
                for linea in TEXTO_SIMPLE.split("\n"):
                    yield linea

        yield _R()

    monkeypatch.setattr(api_comun.httpx, "stream", _stream_captura)
    api_comun.llamar_api(
        prompt=[{"text": "parte fija", "cache": True}, {"text": "parte que cambia", "cache": False}],
        model="m", max_tokens=10, api_key="k", api_base="https://x",
    )
    content = capturado["json"]["messages"][0]["content"]
    assert content == [
        {"type": "text", "text": "parte fija", "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": "parte que cambia"},
    ]


def test_continuacion_con_prompt_en_bloques_preserva_cache_control_en_reintento(monkeypatch):
    # El primer turno de usuario se reconstruye igual en la continuación
    # (ver mecanismo de Tarea 9b) -- confirmar que sigue siendo content
    # blocks con cache_control, no que se pierda al re-armar `mensajes`.
    primera_llamada = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "cami"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "max_tokens"}, "usage": {"output_tokens": 100}}',
    )
    segunda_llamada = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "no"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 1}}',
    )
    capturas = []
    monkeypatch.setattr(
        api_comun.httpx, "stream",
        _stream_secuencia([primera_llamada, segunda_llamada], capturas=capturas),
    )
    api_comun.llamar_api(
        prompt=[{"text": "estable", "cache": True}, {"text": "volatil", "cache": False}],
        model="m", max_tokens=10, api_key="k", api_base="https://x",
    )
    primer_turno_segunda_llamada = capturas[1]["messages"][0]["content"]
    assert primer_turno_segunda_llamada == [
        {"type": "text", "text": "estable", "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": "volatil"},
    ]


def test_sale_con_sys_exit_si_stop_reason_es_refusal(monkeypatch):
    cuerpo = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "algo"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "refusal", '
        '"stop_details": {"type": "refusal", "category": "cyber"}}, '
        '"usage": {"output_tokens": 10}}',
    )
    with pytest.raises(SystemExit) as exc:
        _llamar(monkeypatch, cuerpo)
    mensaje = str(exc.value)
    assert "refusal" in mensaje
    assert "cyber" in mensaje


def test_refusal_en_continuacion_no_devuelve_el_texto_acumulado_como_si_estuviera_completo(monkeypatch):
    # Reproduce el hallazgo real: la primera llamada corta por max_tokens
    # y deja texto genuino acumulado; la segunda -- ya en modo
    # continuación, con el turno assistant+user de MENSAJE_CONTINUAR --
    # es rechazada por el clasificador. Antes de este fix esto se
    # devolvía como éxito con el texto trunco a media frase.
    primera_llamada = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Había una vez"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "max_tokens"}, "usage": {"output_tokens": 100}}',
    )
    segunda_llamada = _sse(
        '{"type": "message_delta", "delta": {"stop_reason": "refusal"}, "usage": {"output_tokens": 0}}',
    )
    monkeypatch.setattr(
        api_comun.httpx, "stream",
        _stream_secuencia([primera_llamada, segunda_llamada]),
    )
    with pytest.raises(SystemExit) as exc:
        api_comun.llamar_api(
            prompt="hola", model="m", max_tokens=10, api_key="k", api_base="https://x",
        )
    assert "refusal" in str(exc.value)
