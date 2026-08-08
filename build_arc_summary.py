#!/usr/bin/env python3
"""
Build a condensed arc summary for full-novel evaluation.
For each chapter: first 150 words, last 150 words, plus any dialogue.
Gives the reader panel enough to evaluate the ARC without 72k tokens.
"""
import os
import re
from pathlib import Path
from dotenv import load_dotenv

from api_comun import llamar_api

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

WRITER_MODEL = os.environ.get("AUTONOVEL_WRITER_MODEL", "claude-sonnet-4-6")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_BASE = os.environ.get("AUTONOVEL_API_BASE_URL", "https://api.anthropic.com")
CHAPTERS_DIR = BASE_DIR / "chapters"

def call_writer(prompt, max_tokens=4000):
    return llamar_api(
        prompt,
        model=WRITER_MODEL,
        max_tokens=max_tokens,
        system=(
            "Resumís capítulos de novela con precisión. Contás qué PASA, "
            "qué CAMBIA, y qué PREGUNTAS quedan abiertas. Sin evaluación. "
            "Sin elogios. Solo hechos y cambios."
        ),
        api_key=API_KEY,
        api_base=API_BASE,
    )

def extract_key_passages(text):
    """Get opening, closing, and best dialogue from a chapter."""
    words = text.split()
    opening = ' '.join(words[:150])
    closing = ' '.join(words[-150:])

    # Líneas de diálogo: en español la raya (—/–) abre el diálogo, no las
    # comillas -- misma heurística que
    # deteccion_es.py::densidad_raya_parentetica() ("si una línea empieza
    # con raya, es diálogo").
    dialogue = []
    for linea in text.splitlines():
        limpia = linea.strip()
        if limpia.startswith("—") or limpia.startswith("–"):
            dialogue.append(limpia.lstrip("—–").strip())

    # Pick up to 3 longest dialogue lines
    dialogue.sort(key=len, reverse=True)
    top_dialogue = dialogue[:3]

    return opening, closing, top_dialogue

def obtener_titulo():
    """Título de la novela: primera línea de outline.md, o de ch_01.md si
    no existe -- mismo patrón que gen_revision.py::obtener_titulo() y
    review.py::get_title()."""
    outline_path = BASE_DIR / "outline.md"
    if outline_path.exists():
        primera_linea = outline_path.read_text().split("\n")[0]
        titulo = primera_linea.lstrip("# ").strip()
        if titulo:
            return titulo
    ch1 = CHAPTERS_DIR / "ch_01.md"
    if ch1.exists():
        primera_linea = ch1.read_text().split("\n")[0]
        return primera_linea.lstrip("# ").strip()
    return ""

def _seccion(md, patron_nombre, nivel="##"):
    """Contenido de un encabezado de nivel dado hasta el próximo del mismo
    nivel (o superior), sin incluir el encabezado. Vacío si no existe --
    mismo patrón que gen_brief.py/draft_chapter.py."""
    marca = re.escape(nivel)
    m = re.search(rf'^{marca}\s*(?:{patron_nombre}).*$', md, re.IGNORECASE | re.MULTILINE)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(rf'^{marca}\s', md[start:], re.MULTILINE)
    end = start + nxt.start() if nxt else len(md)
    return md[start:end].strip()

def obtener_premisa():
    """Premisa de la novela: sección '## Premisa' de semilla.txt (o
    seed.txt si no existe la primera). Vacía si no se encuentra -- no
    rompe, solo omite el párrafo introductorio."""
    for nombre in ("semilla.txt", "seed.txt"):
        path = BASE_DIR / nombre
        if path.exists():
            return _seccion(path.read_text(), "Premisa")
    return ""

def main():
    summaries = []
    chapters = range(1, 47)

    for ch in chapters:
        path = CHAPTERS_DIR / f"ch_{ch:02d}.md"
        text = path.read_text()
        wc = len(text.split())
        opening, closing, dialogue = extract_key_passages(text)

        # Get a 100-word summary from the model. max_tokens=4000 (no 200):
        # con modelos de razonamiento extendido (Opus) el presupuesto de
        # "thinking" se come los 200 enteros antes de producir texto --
        # mismo valor que ya usan reader_panel.py/compare_chapters.py
        # para Opus por la misma razón.
        summary = call_writer(
            f"Resumí este capítulo en exactamente 3 oraciones. Qué pasa, "
            f"qué cambia, qué pregunta queda abierta.\n\nCAPÍTULO {ch}:\n{text}",
            max_tokens=4000
        )

        entry = f"""### Chapter {ch} ({wc} words)
**Summary:** {summary}

**Opening:** {opening}...

**Closing:** ...{closing}

**Key dialogue:**
"""
        for d in dialogue:
            entry += f'> "{d}"\n\n'

        summaries.append(entry)
        print(f"Ch {ch}: summarized ({wc}w)")

    # Calculate total word count
    total_wc = sum(len((CHAPTERS_DIR / f"ch_{c:02d}.md").read_text().split()) for c in chapters)

    titulo = obtener_titulo() or "(sin título)"
    premisa = obtener_premisa()

    # Assemble. El armazón (encabezados, "PREMISE:", "Total novel: ...
    # words") queda en inglés por ahora a propósito -- fuera del alcance
    # de esta corrección (que era título/rango/premisa hardcodeados, no
    # traducción); se traduce junto con reader_panel.py, que es quien
    # consume este archivo.
    full = f"""# {titulo}
## Full-Arc Summary for Reader Panel

This document contains chapter summaries, opening/closing passages,
and key dialogue for all {len(chapters)} chapters. Total novel: {total_wc:,} words.
"""
    if premisa:
        full += f"\nPREMISE: {premisa}\n"

    full += "\n---\n\n"
    full += '\n---\n\n'.join(summaries)

    out_path = BASE_DIR / "arc_summary.md"
    out_path.write_text(full)
    print(f"\nSaved to {out_path} ({len(full.split())} words)")

if __name__ == "__main__":
    main()
