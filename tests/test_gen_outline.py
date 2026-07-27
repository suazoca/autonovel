"""
Test de aceptación de la Tarea 2b (ENCARGO_CLAUDE_CODE.md) para
gen_outline.py y gen_outline_part2.py: construir el prompt con contenido
inventado (no el de la novela anterior) y verificar que el resultado no
contiene ninguna referencia a "The Second Son of the House of Bells".

El grep de aceptación se corre por separado:
  grep -riE "cass|bell|bronze|under-note|perin|maret|torvald|lenne|tonal" \
      gen_outline.py gen_outline_part2.py
  grep -n "/tmp/" gen_outline_part2.py
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import gen_outline as go
import gen_outline_part2 as gop

PROHIBIDO = ["cass", "bell", "bronze", "under-note", "perin", "maret",
             "torvald", "lenne", "tonal"]

SEED_INVENTADA = "Una farera hereda un faro donde las luces mienten."
MUNDO_INVENTADO = "# Biblia de mundo (prueba)\n\nUn archipiélago sin GPS.\n"
PERSONAJES_INVENTADOS = "# Characters\n\n## Marina Fontán (POV)\n- wound: perdió a su padre en el mar\n- want: controlar el faro sola\n- need: pedir ayuda\n- lie: si no necesito a nadie, no puedo volver a perder a nadie\n"
MISTERIO_INVENTADO = "# Mystery\n\nEl faro no se apagó solo.\n"
CRAFT_INVENTADO = "# Craft\n\nSave the Cat, MICE Quotient.\n"
VOZ_PARTE2_INVENTADA = "## Part 2: Voice Identity\n\n### Tone\nSeca, notarial.\n"


def test_gen_outline_build_prompt_no_referencia_novela_anterior():
    prompt = go.build_prompt(
        SEED_INVENTADA, MUNDO_INVENTADO, PERSONAJES_INVENTADOS,
        MISTERIO_INVENTADO, CRAFT_INVENTADO, VOZ_PARTE2_INVENTADA,
    )
    prompt_lower = prompt.lower()
    for termino in PROHIBIDO:
        assert termino not in prompt_lower, f"'{termino}' apareció en el prompt de gen_outline"


def test_gen_outline_build_prompt_contiene_contenido_inventado():
    prompt = go.build_prompt(
        SEED_INVENTADA, MUNDO_INVENTADO, PERSONAJES_INVENTADOS,
        MISTERIO_INVENTADO, CRAFT_INVENTADO, VOZ_PARTE2_INVENTADA,
    )
    assert "Marina Fontán" in prompt
    assert "farera" in prompt.lower() or "faro" in prompt.lower()


def test_gen_outline_build_prompt_usa_calibracion_no_hardcodeado():
    prompt = go.build_prompt(
        SEED_INVENTADA, MUNDO_INVENTADO, PERSONAJES_INVENTADOS,
        MISTERIO_INVENTADO, CRAFT_INVENTADO, VOZ_PARTE2_INVENTADA,
    )
    palabras_capitulo = go.CALIBRACION["palabras_objetivo_capitulo"]
    palabras_novela = go.CALIBRACION["palabras_objetivo_novela"]
    capitulos = round(palabras_novela / palabras_capitulo)
    assert f"~{capitulos}" in prompt
    assert f"~{palabras_capitulo} words per chapter" in prompt
    # el viejo target hardcodeado no debe aparecer
    assert "22-26 chapters" not in prompt
    assert "80,000 words" not in prompt


def test_gen_outline_extraer_voz_parte2_ingles():
    texto = "# Voice\n## Part 1: Guardrails\nx\n## Part 2: Voice Identity\n### Tone\ny\n"
    resultado = go.extraer_voz_parte2(texto)
    assert "Part 2" in resultado
    assert "Guardrails" not in resultado


def test_gen_outline_extraer_voz_parte2_espanol():
    texto = "# Voz\n## Parte 1: Guardarraíles\nx\n## Parte 2: Identidad de voz\n### Tono\ny\n"
    resultado = go.extraer_voz_parte2(texto)
    assert "Parte 2" in resultado
    assert "Guardarraíles" not in resultado


def test_gen_outline_ruta_bilingue_prefiere_espanol(tmp_path):
    (tmp_path / "semilla.txt").write_text("es", encoding="utf-8")
    (tmp_path / "seed.txt").write_text("en", encoding="utf-8")
    assert go.load_file_bilingue(tmp_path, "semilla.txt", "seed.txt") == "es"


def test_gen_outline_ruta_bilingue_cae_al_ingles(tmp_path):
    (tmp_path / "seed.txt").write_text("en", encoding="utf-8")
    assert go.load_file_bilingue(tmp_path, "semilla.txt", "seed.txt") == "en"


def test_gen_outline_main_sale_si_semilla_vacia(tmp_path, monkeypatch):
    monkeypatch.setattr(go, "BASE_DIR", tmp_path)
    (tmp_path / "seed.txt").write_text("   \n", encoding="utf-8")  # solo espacios
    with pytest.raises(SystemExit):
        go.main()


# --- gen_outline_part2.py ---

OUTLINE_PARCIAL = """# Outline

### Ch 1: La primera guardia
- POV: Marina Fontán
- Beats: sube al faro, encuentra la lámpara apagada
"""


def test_gen_outline_part2_build_prompt_no_referencia_novela_anterior():
    prompt = gop.build_prompt(OUTLINE_PARCIAL, MISTERIO_INVENTADO)
    prompt_lower = prompt.lower()
    for termino in PROHIBIDO:
        assert termino not in prompt_lower, f"'{termino}' apareció en el prompt de gen_outline_part2"


def test_gen_outline_part2_build_prompt_contiene_outline_inventado():
    prompt = gop.build_prompt(OUTLINE_PARCIAL, MISTERIO_INVENTADO)
    assert "Marina Fontán" in prompt
    assert "El faro no se apagó solo" in prompt


def test_gen_outline_part2_build_prompt_usa_calibracion_no_hardcodeado():
    prompt = gop.build_prompt(OUTLINE_PARCIAL, MISTERIO_INVENTADO)
    palabras_capitulo = gop.CALIBRACION["palabras_objetivo_capitulo"]
    palabras_novela = gop.CALIBRACION["palabras_objetivo_novela"]
    capitulos = round(palabras_novela / palabras_capitulo)
    assert f"~{capitulos}" in prompt
    # el viejo hardcode de 24 capítulos / ch 17-24 no debe aparecer
    assert "24-chapter" not in prompt
    assert "Ch 17" not in prompt
    assert "Ch 18" not in prompt


def test_gen_outline_part2_no_lee_de_tmp(tmp_path):
    """El bug original: gen_outline_part2.py leía de una ruta absoluta
    hardcodeada fuera del repo (/tmp/outline_output.md). Ahora lee de
    esquema.md/outline.md dentro de un directorio explícito."""
    (tmp_path / "outline.md").write_text(OUTLINE_PARCIAL, encoding="utf-8")
    ruta = gop.ruta_bilingue(tmp_path, "esquema.md", "outline.md")
    assert ruta == tmp_path / "outline.md"
    assert gop.load_file(ruta) == OUTLINE_PARCIAL


def test_gen_outline_part2_ruta_bilingue_prefiere_esquema(tmp_path):
    (tmp_path / "esquema.md").write_text("es", encoding="utf-8")
    (tmp_path / "outline.md").write_text("en", encoding="utf-8")
    assert gop.load_file_bilingue(tmp_path, "esquema.md", "outline.md") == "es"
