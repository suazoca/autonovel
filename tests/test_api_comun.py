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
    un objeto con .raise_for_status() e .iter_lines() sobre `cuerpo`."""

    class _RespuestaFalsa:
        def raise_for_status(self):
            if not status_ok:
                import httpx
                raise httpx.HTTPStatusError("500 boom", request=None, response=self)

        def iter_lines(self):
            for linea in cuerpo.split("\n"):
                yield linea

    @contextmanager
    def _stream(method, url, headers=None, json=None, timeout=None):
        yield _RespuestaFalsa()

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
    cuerpo = _sse(
        '{"type": "content_block_start", "index": 0, "content_block": {"type": "thinking"}}',
        '{"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "solo pienso"}}',
        '{"type": "content_block_stop", "index": 0}',
        '{"type": "message_delta", "delta": {"stop_reason": "max_tokens"}, "usage": {"output_tokens": 500}}',
    )
    with pytest.raises(SystemExit) as exc:
        _llamar(monkeypatch, cuerpo)
    mensaje = str(exc.value)
    assert "sin bloque de texto" in mensaje
    assert "max_tokens" in mensaje


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
            def raise_for_status(self):
                pass

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
            def raise_for_status(self):
                pass

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
            def raise_for_status(self):
                pass

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
            def raise_for_status(self):
                pass

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
