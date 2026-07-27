#!/usr/bin/env python3
"""Complete the outline (remaining chapters + foreshadowing ledger)."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from deteccion_es import CALIBRACION
from fundacion_comun import ruta_bilingue, load_file, load_file_bilingue

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
        "temperature": 0.5,
        "system": (
            "You are a novel architect continuing an outline. Write in the same format "
            "as the preceding chapters. Every chapter needs: POV, Location, Save the Cat beat, "
            "% mark, Ambición (pico/sosten/valle), Emotional arc, Try-fail cycle, Beats, "
            "Plants, Payoffs, Character movement, The lie, Word count target."
        ),
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = httpx.post(f"{API_BASE}/v1/messages", headers=headers, json=payload, timeout=600)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def build_prompt(outline_so_far, mystery):
    palabras_capitulo = CALIBRACION["palabras_objetivo_capitulo"]
    palabras_novela = CALIBRACION["palabras_objetivo_novela"]
    capitulos_totales = round(palabras_novela / palabras_capitulo)

    return f"""Here is a chapter outline in progress, targeting ~{capitulos_totales}
chapters total (~{palabras_capitulo} words per chapter, ~{palabras_novela} words total).
It may be incomplete or cut off mid-chapter.

THE OUTLINE SO FAR:
{outline_so_far}

THE CENTRAL MYSTERY (for reference):
{mystery}

Continue from wherever it left off. Complete the remaining chapters up to
the target chapter count above, then write the Foreshadowing Ledger.

REMAINING STRUCTURE NEEDED (fill with THIS story's specifics, derived from
the outline so far and the central mystery -- do not invent new characters,
locations, or mechanics not already established):

- Complete Act II Part 2 if it isn't finished: pressure mounts, the
  protagonist's lie becomes unsustainable, All Is Lost.
- Dark Night of the Soul: the protagonist processes what they've learned.
- Break Into Three: new information or perspective changes everything.
- Gathering forces, making a plan.
- The climax: the protagonist answers the central question, resolved using
  rules already established in the world bible -- no new powers or
  last-minute exceptions.
- Aftermath and resolution. The Stability Trap: not everything resolves
  cleanly.
- Final Image: mirror the outline's Opening Image (Ch 1), but show
  transformation.

Then write:

## Foreshadowing Ledger

| # | Thread | Planted (Ch) | Reinforced (Ch) | Payoff (Ch) | Alcance | Type |
|---|--------|-------------|-----------------|-------------|---------|------|

Alcance is "libro" (default -- must pay off within THIS book) or "serie"
(allowed to pay off in a later book of the series; only meaningful if this
branch has a siembras_serie.md -- if it doesn't, treat every thread as
"libro" regardless). For "serie" threads, Payoff should name the book too.

Include at LEAST 15 threads. Types: object, dialogue, action, symbolic, structural.
Plant-to-payoff distance must be at least 3 chapters (within the same book;
cross-book "serie" threads are exempt from this distance rule).
At least one chapter in the back half should be "quiet" -- character-focused,
low-action, emotionally rich.
"""


def main():
    outline_path = ruta_bilingue(BASE_DIR, "esquema.md", "outline.md")
    outline_so_far = load_file(outline_path)
    mystery = load_file_bilingue(BASE_DIR, "MISTERIO.md", "MYSTERY.md")

    prompt = build_prompt(outline_so_far, mystery)

    print("Calling writer model...", file=sys.stderr)
    result = call_writer(prompt)

    combined = (outline_so_far.rstrip() + "\n\n" + result) if outline_so_far.strip() else result
    outline_path.write_text(combined, encoding="utf-8")
    print(f"Saved to {outline_path}", file=sys.stderr)
    print(result)


if __name__ == "__main__":
    main()
