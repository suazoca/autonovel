#!/usr/bin/env python3
"""
Generate canon.md by extracting all hard facts from world.md + characters.md.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from fundacion_comun import load_file, load_file_bilingue, exigir_semilla
from api_comun import llamar_api

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

WRITER_MODEL = os.environ.get("AUTONOVEL_WRITER_MODEL", "claude-sonnet-4-6")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_BASE = os.environ.get("AUTONOVEL_API_BASE_URL", "https://api.anthropic.com")

def call_writer(prompt, max_tokens=16000):
    return llamar_api(
        prompt,
        model=WRITER_MODEL,
        max_tokens=max_tokens,
        system=(
            "Sos un editor de continuidad que extrae hechos duros de documentos de "
            "planificación de una novela. Sos preciso, exhaustivo, y nunca inventás "
            "hechos que no estén en el material fuente. Cada entrada debe poder "
            "rastrearse a una afirmación específica en los documentos fuente. "
            "Escribís en español."
        ),
        api_key=API_KEY,
        api_base=API_BASE,
    )


def build_prompt(seed, world, characters):
    return f"""Extraé TODO hecho duro de estos documentos de planificación a una base
de datos de canon estructurada. Un "hecho duro" es cualquier cosa que un escritor no
debe contradecir: nombres, edades, fechas, descripciones físicas, reglas de cualquier
sistema excepcional del mundo, geografía, relaciones, eventos ya establecidos.

DOCUMENTOS FUENTE:

=== SEMILLA ===
{seed}

=== MUNDO.MD ===
{world}

=== PERSONAJES.MD ===
{characters}

FORMATEÁ LA SALIDA COMO CANON.MD CON ESTAS CATEGORÍAS:

## Geografía
- Hechos específicos sobre lugares, distancias, propiedades físicas

## Cronología
- Eventos fechados, edades, duraciones

## Reglas excepcionales del mundo
- Reglas duras del sistema de magia u otra capacidad excepcional, si el mundo
  tiene una -- si no, esta sección queda vacía o con "No aplica"

## Hechos de personajes
- Edades, descripciones físicas, hábitos, relaciones
- Una entrada por hecho (no párrafos)

## Político / faccional
- Quién controla qué, alianzas, conflictos, contratos

## Cultural
- Costumbres, tabúes, leyes, festividades, comida, vestimenta

## Establecido en la historia
- Eventos que ya pasaron en el pasado de la historia, según lo que hayan
  establecido mundo.md y personajes.md -- no inventes ejemplos

REGLAS:
- Un hecho por viñeta. Corto. Específico. Verificable.
- Incluí la fuente (mundo.md o personajes.md) entre paréntesis después de
  cada hecho.
- Apuntá a un mínimo de 80-120 entradas. Sé exhaustivo.
- Si los dos documentos dan detalles levemente distintos, anotá la discrepancia.
- NO inventes hechos. Solo registrá lo explícitamente declarado.
"""


def main():
    seed = load_file_bilingue(BASE_DIR, "semilla.txt", "seed.txt")
    exigir_semilla(seed, "extraer canon")

    world = load_file_bilingue(BASE_DIR, "mundo.md", "world.md")
    characters = load_file_bilingue(BASE_DIR, "personajes.md", "characters.md")

    prompt = build_prompt(seed, world, characters)

    print("Calling writer model...", file=sys.stderr)
    result = call_writer(prompt)

    out_path = BASE_DIR / "canon.md"
    out_path.write_text(result, encoding="utf-8")
    print(f"Saved to {out_path}", file=sys.stderr)
    print(result)


if __name__ == "__main__":
    main()
