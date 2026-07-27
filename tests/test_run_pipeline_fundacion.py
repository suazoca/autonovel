"""
Test de aceptación de la Tarea 6 (ENCARGO_CLAUDE_CODE.md), parte de
run_pipeline.py: un generador que falla debe abortar en vez de que
run_foundation() siga de largo ignorando el returncode, y hay que
verificar que los archivos de fundación se escribieron EN ESTA ITERACIÓN
(no que ya existiera una plantilla vieja tirada ahí) antes de gastar una
llamada al juez LLM evaluándolos.

Nada de esto llama a la API: uv_run() se parchea siempre.
"""

import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import run_pipeline as rp


def _fake_result(returncode, stdout="", stderr=""):
    return subprocess.CompletedProcess(
        args="uv run python fake.py", returncode=returncode, stdout=stdout, stderr=stderr,
    )


def test_run_generator_aborta_si_falla(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(rp, "uv_run", lambda script, timeout=300: _fake_result(1, stderr="boom detallado"))
    monkeypatch.setattr(rp, "STATE_FILE", tmp_path / "state.json")
    estado = {"iteration": 3, "phase": "foundation"}

    with pytest.raises(SystemExit):
        rp.run_generator("gen_world.py", estado)

    salida = capsys.readouterr()
    assert "gen_world.py" in salida.err
    assert "boom detallado" in salida.err  # stderr completo, no truncado


def test_run_generator_guarda_state_antes_de_salir(monkeypatch, tmp_path):
    monkeypatch.setattr(rp, "uv_run", lambda script, timeout=300: _fake_result(1, stderr="boom"))
    state_file = tmp_path / "state.json"
    monkeypatch.setattr(rp, "STATE_FILE", state_file)
    estado = {"iteration": 3, "phase": "foundation"}

    with pytest.raises(SystemExit):
        rp.run_generator("gen_world.py", estado)

    assert state_file.exists()
    guardado = rp.json.loads(state_file.read_text())
    assert guardado["iteration"] == 3


def test_run_generator_devuelve_result_si_ok(monkeypatch):
    ok = _fake_result(0, stdout="listo")
    monkeypatch.setattr(rp, "uv_run", lambda script, timeout=300: ok)

    resultado = rp.run_generator("gen_world.py", {})

    assert resultado is ok


def test_verificar_archivos_fundacion_todo_falta(tmp_path, monkeypatch):
    monkeypatch.setattr(rp, "BASE_DIR", tmp_path)
    desde = time.time()

    faltantes = rp.verificar_archivos_fundacion(desde)

    assert "mundo.md/world.md" in faltantes
    assert "personajes.md/characters.md" in faltantes
    assert "esquema.md/outline.md" in faltantes
    assert "canon.md" in faltantes


def test_verificar_archivos_fundacion_vacios_cuentan_como_faltantes(tmp_path, monkeypatch):
    monkeypatch.setattr(rp, "BASE_DIR", tmp_path)
    desde = time.time()
    (tmp_path / "world.md").write_text("   \n", encoding="utf-8")  # solo espacios
    (tmp_path / "characters.md").write_text("", encoding="utf-8")
    (tmp_path / "outline.md").write_text("", encoding="utf-8")
    (tmp_path / "canon.md").write_text("", encoding="utf-8")

    faltantes = rp.verificar_archivos_fundacion(desde)

    assert len(faltantes) == 4


def test_verificar_archivos_fundacion_todo_presente_lista_vacia(tmp_path, monkeypatch):
    monkeypatch.setattr(rp, "BASE_DIR", tmp_path)
    desde = time.time() - 1  # margen: precisión de mtime del filesystem
    (tmp_path / "world.md").write_text("mundo real", encoding="utf-8")
    (tmp_path / "characters.md").write_text("personajes reales", encoding="utf-8")
    (tmp_path / "outline.md").write_text("esquema real", encoding="utf-8")
    (tmp_path / "canon.md").write_text("canon real", encoding="utf-8")

    assert rp.verificar_archivos_fundacion(desde) == []


def test_verificar_archivos_fundacion_prefiere_nombre_en_espanol(tmp_path, monkeypatch):
    monkeypatch.setattr(rp, "BASE_DIR", tmp_path)
    desde = time.time() - 1  # margen: precisión de mtime del filesystem
    (tmp_path / "mundo.md").write_text("mundo real", encoding="utf-8")
    (tmp_path / "personajes.md").write_text("personajes reales", encoding="utf-8")
    (tmp_path / "esquema.md").write_text("esquema real", encoding="utf-8")
    (tmp_path / "canon.md").write_text("canon real", encoding="utf-8")

    assert rp.verificar_archivos_fundacion(desde) == []


def test_verificar_archivos_fundacion_mtime_anterior_aborta(tmp_path, monkeypatch):
    """Caso pedido explícitamente: archivo presente, no vacío, pero con
    mtime ANTERIOR al inicio de la iteración -- debe abortar igual.
    world.md/characters.md/outline.md son plantillas trackeadas en git
    con contenido real pero viejo; 'existe y no está vacío' no prueba que
    el generador haya escrito algo esta vuelta."""
    monkeypatch.setattr(rp, "BASE_DIR", tmp_path)
    world = tmp_path / "world.md"
    characters = tmp_path / "characters.md"
    outline = tmp_path / "outline.md"
    canon = tmp_path / "canon.md"
    world.write_text("plantilla vieja de mundo", encoding="utf-8")
    characters.write_text("plantilla vieja de personajes", encoding="utf-8")
    outline.write_text("plantilla vieja de esquema", encoding="utf-8")
    canon.write_text("plantilla vieja de canon", encoding="utf-8")

    # La iteración "empieza" después de que estos archivos viejos ya
    # existían -- ninguno se tocó en la corrida actual.
    desde = max(
        world.stat().st_mtime, characters.stat().st_mtime,
        outline.stat().st_mtime, canon.stat().st_mtime,
    ) + 1

    faltantes = rp.verificar_archivos_fundacion(desde)

    assert len(faltantes) == 4
