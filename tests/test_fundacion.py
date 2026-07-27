"""
Test de aceptación de la Tarea 6 (ENCARGO_CLAUDE_CODE.md): persistencia en
la fase de fundación. gen_world.py, gen_characters.py y gen_canon.py ya no
terminan en print(result) sin guardar, y ya no tienen código a nivel de
módulo que dispare la API al importarlos.

Ninguno de estos tests requiere ANTHROPIC_API_KEY ni red: call_writer()
se parchea siempre a una función que no toca httpx.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import fundacion_comun as fc


# ---------------------------------------------------------------------------
# fundacion_comun.py directamente
# ---------------------------------------------------------------------------

def test_ruta_bilingue_prefiere_espanol(tmp_path):
    (tmp_path / "mundo.md").write_text("es", encoding="utf-8")
    (tmp_path / "world.md").write_text("en", encoding="utf-8")
    assert fc.load_file_bilingue(tmp_path, "mundo.md", "world.md") == "es"


def test_ruta_bilingue_cae_al_ingles(tmp_path):
    (tmp_path / "world.md").write_text("en", encoding="utf-8")
    assert fc.load_file_bilingue(tmp_path, "mundo.md", "world.md") == "en"


def test_load_file_vacio_si_no_existe(tmp_path):
    assert fc.load_file(tmp_path / "no-existe.md") == ""


def test_exigir_semilla_sale_si_vacia():
    with pytest.raises(SystemExit):
        fc.exigir_semilla("   \n", "generar un mundo")


def test_exigir_semilla_sale_si_falsy():
    with pytest.raises(SystemExit):
        fc.exigir_semilla("", "generar un mundo")


def test_exigir_semilla_no_sale_si_hay_contenido():
    fc.exigir_semilla("Una farera hereda un faro.", "generar un mundo")  # no debe lanzar


def test_extraer_voz_parte2_no_rompe_sin_encabezado():
    """Antes: next(...) sin default levantaba StopIteration si no había
    'Part 2'/'Parte 2'. Ahora degrada con gracia."""
    assert fc.extraer_voz_parte2("# Voice\nsolo un párrafo, sin partes\n") == \
        "# Voice\nsolo un párrafo, sin partes\n"


def test_extraer_voz_parte2_reconoce_espanol():
    texto = "## Parte 1: Guardarraíles\nx\n## Parte 2: Identidad de voz\ny\n"
    resultado = fc.extraer_voz_parte2(texto)
    assert resultado.startswith("## Parte 2")


# ---------------------------------------------------------------------------
# Import de los tres módulos no debe llamar a la API
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _httpx_post_rompe_si_se_llama(monkeypatch):
    """Cualquier llamada real a httpx.post durante estos tests es un bug --
    debería estar parcheada en call_writer antes de llegar acá."""
    import httpx

    def _rompe(*args, **kwargs):
        raise AssertionError("httpx.post fue invocado -- no debería pasar en estos tests")

    monkeypatch.setattr(httpx, "post", _rompe)


def test_import_gen_world_no_llama_api():
    import gen_world  # noqa: F401 -- solo importar, sin llamar a main()


def test_import_gen_characters_no_llama_api():
    import gen_characters  # noqa: F401


def test_import_gen_canon_no_llama_api():
    import gen_canon  # noqa: F401


# ---------------------------------------------------------------------------
# main() con call_writer parcheado escribe en el archivo esperado
# ---------------------------------------------------------------------------

def _preparar_entradas_comunes(tmp_path):
    (tmp_path / "seed.txt").write_text("Una farera hereda un faro.", encoding="utf-8")
    (tmp_path / "voice.md").write_text(
        "## Part 2: Voice Identity\n### Tone\nSeca.\n", encoding="utf-8"
    )
    (tmp_path / "CRAFT.md").write_text("# Craft\n", encoding="utf-8")


def test_gen_world_main_escribe_world_md(tmp_path, monkeypatch):
    import gen_world
    _preparar_entradas_comunes(tmp_path)
    monkeypatch.setattr(gen_world, "BASE_DIR", tmp_path)
    monkeypatch.setattr(gen_world, "call_writer", lambda prompt, **kw: "MUNDO GENERADO")

    gen_world.main()

    assert (tmp_path / "world.md").read_text(encoding="utf-8") == "MUNDO GENERADO"


def test_gen_world_prefiere_mundo_md_si_existe(tmp_path, monkeypatch):
    import gen_world
    _preparar_entradas_comunes(tmp_path)
    (tmp_path / "mundo.md").write_text("viejo", encoding="utf-8")
    monkeypatch.setattr(gen_world, "BASE_DIR", tmp_path)
    monkeypatch.setattr(gen_world, "call_writer", lambda prompt, **kw: "MUNDO GENERADO")

    gen_world.main()

    assert (tmp_path / "mundo.md").read_text(encoding="utf-8") == "MUNDO GENERADO"
    assert not (tmp_path / "world.md").exists()


def test_gen_world_main_sale_si_semilla_vacia(tmp_path, monkeypatch):
    import gen_world
    (tmp_path / "seed.txt").write_text("", encoding="utf-8")
    monkeypatch.setattr(gen_world, "BASE_DIR", tmp_path)

    with pytest.raises(SystemExit):
        gen_world.main()

    assert not (tmp_path / "world.md").exists()


def test_gen_world_main_sale_si_no_hay_semilla(tmp_path, monkeypatch):
    import gen_world
    monkeypatch.setattr(gen_world, "BASE_DIR", tmp_path)  # ni seed.txt ni semilla.txt

    with pytest.raises(SystemExit):
        gen_world.main()


def test_gen_characters_main_escribe_characters_md(tmp_path, monkeypatch):
    import gen_characters
    _preparar_entradas_comunes(tmp_path)
    (tmp_path / "world.md").write_text("mundo de prueba", encoding="utf-8")
    monkeypatch.setattr(gen_characters, "BASE_DIR", tmp_path)
    monkeypatch.setattr(gen_characters, "call_writer", lambda prompt, **kw: "PERSONAJES GENERADOS")

    gen_characters.main()

    assert (tmp_path / "characters.md").read_text(encoding="utf-8") == "PERSONAJES GENERADOS"


def test_gen_characters_prefiere_personajes_md_si_existe(tmp_path, monkeypatch):
    import gen_characters
    _preparar_entradas_comunes(tmp_path)
    (tmp_path / "world.md").write_text("mundo de prueba", encoding="utf-8")
    (tmp_path / "personajes.md").write_text("viejo", encoding="utf-8")
    monkeypatch.setattr(gen_characters, "BASE_DIR", tmp_path)
    monkeypatch.setattr(gen_characters, "call_writer", lambda prompt, **kw: "PERSONAJES GENERADOS")

    gen_characters.main()

    assert (tmp_path / "personajes.md").read_text(encoding="utf-8") == "PERSONAJES GENERADOS"
    assert not (tmp_path / "characters.md").exists()


def test_gen_characters_main_sale_si_semilla_vacia(tmp_path, monkeypatch):
    import gen_characters
    (tmp_path / "seed.txt").write_text("   ", encoding="utf-8")
    monkeypatch.setattr(gen_characters, "BASE_DIR", tmp_path)

    with pytest.raises(SystemExit):
        gen_characters.main()


def test_gen_canon_main_escribe_canon_md(tmp_path, monkeypatch):
    import gen_canon
    (tmp_path / "seed.txt").write_text("Una farera hereda un faro.", encoding="utf-8")
    (tmp_path / "world.md").write_text("mundo de prueba", encoding="utf-8")
    (tmp_path / "characters.md").write_text("personajes de prueba", encoding="utf-8")
    monkeypatch.setattr(gen_canon, "BASE_DIR", tmp_path)
    monkeypatch.setattr(gen_canon, "call_writer", lambda prompt, **kw: "CANON GENERADO")

    gen_canon.main()

    assert (tmp_path / "canon.md").read_text(encoding="utf-8") == "CANON GENERADO"


def test_gen_canon_main_sale_si_semilla_vacia(tmp_path, monkeypatch):
    import gen_canon
    (tmp_path / "world.md").write_text("mundo de prueba", encoding="utf-8")
    (tmp_path / "characters.md").write_text("personajes de prueba", encoding="utf-8")
    monkeypatch.setattr(gen_canon, "BASE_DIR", tmp_path)  # sin seed.txt

    with pytest.raises(SystemExit):
        gen_canon.main()
