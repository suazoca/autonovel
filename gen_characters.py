#!/usr/bin/env python3
"""
One-shot characters.md generator for foundation phase.
Reads seed.txt + voice.md + world.md + CRAFT.md, calls writer model.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from deteccion_es import CALIBRACION
from fundacion_comun import ruta_bilingue, load_file, load_file_bilingue, extraer_voz_parte2, exigir_semilla

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

WRITER_MODEL = os.environ.get("AUTONOVEL_WRITER_MODEL", "claude-sonnet-4-6")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_BASE = os.environ.get("AUTONOVEL_API_BASE_URL", "https://api.anthropic.com")

def call_writer(prompt, max_tokens=16000):
    import httpx
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": WRITER_MODEL,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "system": (
            "Sos un diseñador de personajes de ficción literaria con conocimiento "
            "profundo de los frameworks herida/quiere/necesita/mentira, los tres "
            "sliders de Sanderson, y distintividad de diálogo. Creás personajes que se "
            "sienten personas reales, con contradicciones, secretos y patrones de habla "
            "que se pueden escuchar. Nunca usás relleno de IA. Escribís en prosa limpia "
            "y directa, en español."
        ),
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = httpx.post(f"{API_BASE}/v1/messages", headers=headers, json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def build_prompt(seed, world, voice_part2):
    palabras_capitulo = CALIBRACION["palabras_objetivo_capitulo"]
    palabras_novela = CALIBRACION["palabras_objetivo_novela"]
    capitulos_totales = round(palabras_novela / palabras_capitulo)

    return f"""Construí un registro de personajes completo para esta novela. Este es el
archivo PERSONAJES.MD -- la referencia definitiva de QUIÉN existe en esta historia,
qué los mueve, cómo hablan, y qué secretos cargan.

El género sale de la SEMILLA y del MUNDO cargados abajo, no de este prompt. Los
nombres, roles y relaciones deben derivarse de esos documentos -- no inventes un
reparto genérico de fantasía ni reutilices nombres de ninguna otra novela.

CONCEPTO SEMILLA:
{seed}

BIBLIA DE MUNDO (el mundo que habitan estos personajes):
{world}

IDENTIDAD DE VOZ (el tono de la novela):
{voice_part2}

REQUISITOS DE OFICIO:

### Los tres sliders (Sanderson)
Cada personaje tiene tres diales independientes (0-10):
  PROACTIVIDAD -- ¿impulsa la trama o reacciona a ella?
  SIMPATÍA     -- ¿el lector empatiza con él/ella?
  COMPETENCIA  -- ¿es bueno/a en lo que hace?
Regla: un personaje atractivo tiene ALTO en al menos dos, o ALTO en uno con
crecimiento claro.

### Framework fantasma/herida/quiere/necesita/mentira
Una cadena causal:
  FANTASMA (evento de trasfondo) -> HERIDA (daño persistente)
    -> MENTIRA (creencia falsa para sobrellevarlo)
    -> QUIERE (objetivo externo impulsado por la mentira)
    -> NECESITA (verdad interna, opuesta a la mentira)
Reglas: quiere y necesita deben estar EN TENSIÓN. La mentira debe poder decirse
en una oración. La verdad es su opuesto directo.

### Distintividad de diálogo (8 dimensiones)
1. Nivel de vocabulario  2. Longitud de oración  3. Contracciones/formalidad
4. Muletillas  5. Proporción pregunta/afirmación  6. Patrones de interrupción
7. Dominio metafórico  8. Directo vs. indirecto
Prueba: quitá las acotaciones de diálogo. ¿Se puede saber quién habla?

CUÁNTOS PERSONAJES:

Construí el registro con los personajes que la trama necesite -- ni un reparto
fijo ni una lista mínima arbitraria. Como mínimo: el/la protagonista (POV) y
quien encarna el antagonismo del conflicto central (no necesariamente un
villano: alguien cuyos intereses chocan con los del protagonista). Para una
novela de ~{capitulos_totales} capítulos, esto suele significar entre 5 y 9
personajes con profundidad completa, más los secundarios que la semilla y el
mundo pidan. Los nombres salen de la semilla/mundo, nunca de otra novela.

PARA CADA PERSONAJE INCLUÍ:
- Nombre, edad, rol
- Cadena fantasma/herida/quiere/necesita/mentira (para los principales)
- Los tres sliders (proactividad/simpatía/competencia) con números y
  justificación
- Tipo y trayectoria de arco
- Patrón de habla (las 8 dimensiones, con líneas de ejemplo)
- Apariencia física (específica, no genérica)
- Hábitos físicos y tics inconscientes
- Secretos (lo que el lector no sabe de entrada)
- Relaciones clave (mapeadas a otros personajes)
- Rol temático (¿qué pregunta encarna este personaje?)

IMPORTANTE:
- Los personajes deben INTERCONECTAR. Sus deseos deberían chocar entre sí.
- Cada secreto debería ser algo que CAMBIARÍA la historia si se revelara.
- Los patrones de habla deben ser lo bastante distintos para pasar la prueba
  sin acotaciones.
- Los hábitos físicos de cada personaje deberían conectar con algo específico
  de su historia o su mundo -- no ser decorativos.
- Quien encarne el antagonismo debería estar tan bien realizado/a como el/la
  protagonista.
- Extensión objetivo ~3000-4000 palabras. Trabajo de personaje denso, no relleno.
"""


def main():
    seed = load_file_bilingue(BASE_DIR, "semilla.txt", "seed.txt")
    exigir_semilla(seed, "generar personajes")

    world = load_file_bilingue(BASE_DIR, "mundo.md", "world.md")
    voice = load_file_bilingue(BASE_DIR, "voz.md", "voice.md")
    voice_part2 = extraer_voz_parte2(voice)

    prompt = build_prompt(seed, world, voice_part2)

    print("Calling writer model...", file=sys.stderr)
    result = call_writer(prompt)

    out_path = ruta_bilingue(BASE_DIR, "personajes.md", "characters.md")
    out_path.write_text(result, encoding="utf-8")
    print(f"Saved to {out_path}", file=sys.stderr)
    print(result)


if __name__ == "__main__":
    main()
