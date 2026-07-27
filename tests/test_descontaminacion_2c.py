"""
Test de aceptación de la Tarea 2c (ENCARGO_CLAUDE_CODE.md): descontaminar
gen_world.py, gen_characters.py y gen_canon.py de "The Second Son of the
House of Bells". El grep de aceptación se corre por separado:

  grep -in "cass|bellwright|perin|corda|suvaine|torvald|cantamura| \
      tonal law|expansion wars" gen_world.py gen_characters.py gen_canon.py

Este archivo existe para que esos términos no puedan volver a entrar sin
que el suite lo note -- build_prompt() se llama con inputs de prueba
mínimos e inventados, no con contenido real de ninguna novela.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import gen_world
import gen_characters
import gen_canon

PROHIBIDO_2C = [
    "cass", "bellwright", "perin", "corda", "suvaine", "torvald",
    "cantamura", "tonal law", "expansion wars",
]

SEMILLA_PRUEBA = "Una farera hereda un faro donde las luces mienten."
VOZ_PRUEBA = "Seca, notarial."
CRAFT_PRUEBA = "Save the Cat, MICE Quotient."
MUNDO_PRUEBA = "Un archipiélago sin GPS, sin sistema de magia."
PERSONAJES_PRUEBA = "Marina Fontán (POV), farera."


def _sin_terminos_prohibidos(texto):
    texto_lower = texto.lower()
    return [t for t in PROHIBIDO_2C if t in texto_lower]


def test_gen_world_build_prompt_no_referencia_novela_anterior():
    prompt = gen_world.build_prompt(SEMILLA_PRUEBA, VOZ_PRUEBA, CRAFT_PRUEBA)
    encontrados = _sin_terminos_prohibidos(prompt)
    assert encontrados == [], f"Términos de la novela anterior en gen_world.py: {encontrados}"


def test_gen_characters_build_prompt_no_referencia_novela_anterior():
    prompt = gen_characters.build_prompt(SEMILLA_PRUEBA, MUNDO_PRUEBA, VOZ_PRUEBA)
    encontrados = _sin_terminos_prohibidos(prompt)
    assert encontrados == [], f"Términos de la novela anterior en gen_characters.py: {encontrados}"


def test_gen_canon_build_prompt_no_referencia_novela_anterior():
    prompt = gen_canon.build_prompt(SEMILLA_PRUEBA, MUNDO_PRUEBA, PERSONAJES_PRUEBA)
    encontrados = _sin_terminos_prohibidos(prompt)
    assert encontrados == [], f"Términos de la novela anterior en gen_canon.py: {encontrados}"


def test_gen_world_no_exige_fantasia_ni_sistema_de_magia():
    prompt = gen_world.build_prompt(SEMILLA_PRUEBA, VOZ_PRUEBA, CRAFT_PRUEBA)
    prompt_lower = prompt.lower()
    assert "fantasy novel" not in prompt_lower
    assert "si aplica" in prompt_lower or "si la semilla" in prompt_lower


def test_gen_characters_no_exige_fantasia():
    prompt = gen_characters.build_prompt(SEMILLA_PRUEBA, MUNDO_PRUEBA, VOZ_PRUEBA)
    assert "fantasy novel" not in prompt.lower()


def test_gen_canon_no_exige_fantasia():
    prompt = gen_canon.build_prompt(SEMILLA_PRUEBA, MUNDO_PRUEBA, PERSONAJES_PRUEBA)
    assert "fantasy novel" not in prompt.lower()


def test_gen_characters_cuenta_personajes_no_hardcodeada():
    """La lista fija de 6-7 personajes con nombre propio ya no debe existir
    -- el conteo se deriva de CALIBRACION, no de un reparto escrito a mano."""
    prompt = gen_characters.build_prompt(SEMILLA_PRUEBA, MUNDO_PRUEBA, VOZ_PRUEBA)
    capitulos = round(
        gen_characters.CALIBRACION["palabras_objetivo_novela"]
        / gen_characters.CALIBRACION["palabras_objetivo_capitulo"]
    )
    assert f"~{capitulos}" in prompt


def test_gen_world_contiene_semilla_inventada():
    prompt = gen_world.build_prompt(SEMILLA_PRUEBA, VOZ_PRUEBA, CRAFT_PRUEBA)
    assert SEMILLA_PRUEBA in prompt


def test_gen_characters_contiene_mundo_inventado():
    prompt = gen_characters.build_prompt(SEMILLA_PRUEBA, MUNDO_PRUEBA, VOZ_PRUEBA)
    assert MUNDO_PRUEBA in prompt


def test_gen_canon_contiene_personajes_inventados():
    prompt = gen_canon.build_prompt(SEMILLA_PRUEBA, MUNDO_PRUEBA, PERSONAJES_PRUEBA)
    assert PERSONAJES_PRUEBA in prompt
