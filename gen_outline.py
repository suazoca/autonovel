#!/usr/bin/env python3
"""Generate outline.md/esquema.md from seed + world + characters + mystery + craft."""
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
        "anthropic-beta": "context-1m-2025-08-07",
        "content-type": "application/json",
    }
    payload = {
        "model": WRITER_MODEL,
        "max_tokens": max_tokens,
        "temperature": 0.5,
        "system": (
            "You are a novel architect with deep knowledge of Save the Cat beats, "
            "Sanderson's plotting principles, Dan Harmon's Story Circle, and MICE Quotient. "
            "You build outlines that an author can draft from without inventing structure "
            "on the fly. Every chapter has beats, emotional arc, and try-fail cycle type. "
            "You never use AI slop words. You write in clean, direct prose."
        ),
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = httpx.post(f"{API_BASE}/v1/messages", headers=headers, json=payload, timeout=600)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def build_prompt(seed, world, characters, mystery, craft, voice_part2):
    palabras_capitulo = CALIBRACION["palabras_objetivo_capitulo"]
    palabras_novela = CALIBRACION["palabras_objetivo_novela"]
    capitulos_totales = round(palabras_novela / palabras_capitulo)

    return f"""Build a complete chapter outline for this novel. Target: ~{capitulos_totales}
chapters, ~{palabras_novela} words total (~{palabras_capitulo} words per chapter).

SEED CONCEPT:
{seed}

THE CENTRAL MYSTERY (author's eyes only -- reader discovers gradually):
{mystery}

WORLD BIBLE:
{world}

CHARACTER REGISTRY:
{characters}

VOICE (tone and register):
{voice_part2}

CRAFT REFERENCE (structures to follow):
{craft}

BUILD THE OUTLINE WITH:

## Act Structure
Map out Act I (0-23%), Act II Part 1 (23-50%), Act II Part 2 (50-77%), Act III (77-100%).
State the percentage marks for the key novel.

## Chapter-by-Chapter Outline

For EACH chapter, provide:
### Ch N: [Title]
- **POV:** the POV character(s) for this chapter -- pick from CHARACTER
  REGISTRY above (whoever is marked as a POV character there). If the
  novel rotates POV, say whose turn it is.
- **Location:** Which locations, from WORLD BIBLE
- **Save the Cat beat:** Which beat this chapter serves (Opening Image, Setup, Catalyst, etc.)
- **% mark:** Where this falls in the novel
- **Ambición:** pico | sosten | valle -- declare ONE per chapter.
  "pico" = a scene the reader must remember (aim for at least 15% of all
  chapters). "sosten" = a working chapter that advances the plot.
  "valle" = a deliberate breather/transition. Do NOT make every chapter a
  "sosten" -- a flat outline with no peaks reads as competent but forgettable.
- **Emotional arc:** Starting emotion → ending emotion
- **Try-fail cycle:** Yes-but / No-and / No-but / Yes-and
- **Beats:** 3-5 specific scene beats that must happen
- **Plants:** Foreshadowing elements planted in this chapter
- **Payoffs:** Foreshadowing elements that pay off here
- **Character movement:** What changes for the POV character (or others) by chapter's end
- **The lie:** How the POV character's lie -- see their wound/want/need/lie
  chain in CHARACTER REGISTRY -- is reinforced or challenged in this chapter
- **~Word count target:** for pacing, around {palabras_capitulo} words

## Foreshadowing Ledger

A table tracking every planted thread:
| # | Thread | Planted (Ch) | Reinforced (Ch) | Payoff (Ch) | Alcance | Type |

Alcance is "libro" (default -- must pay off within THIS book) or "serie"
(allowed to pay off in a later book of the series; only meaningful if this
branch has a siembras_serie.md -- if it doesn't, treat every thread as
"libro" regardless).

Include at LEAST 15 threads. Types: object, dialogue, action, symbolic, structural.
Plant-to-payoff distance must be at least 3 chapters (within the same book;
cross-book "serie" threads are exempt from this distance rule).

KEY PLOT ARCHITECTURE:

Derive the Act I / Act II Part 1 / Act II Part 2 / Act III beats from the
SEED CONCEPT, WORLD BIBLE, CHARACTER REGISTRY, and CENTRAL MYSTERY above.
Do not invent plot elements, character names, locations, or mechanics that
aren't grounded in those documents -- if something is missing that the
plot needs, that's a gap to flag, not something to make up silently.

As a shape to follow (fill it with THIS story's specifics, not placeholders):
- Act I: establish the protagonist's world and wound. Plant the central
  mystery early. A catalyst forces the protagonist to act.
- Act II Part 1: investigation/escalation using the rules established in
  the world bible. Midpoint: a partial truth changes the approach (false
  victory or false defeat).
- Act II Part 2: pressure mounts, the protagonist's lie becomes
  unsustainable. All Is Lost: a confrontation reveals the full truth.
- Act III: the protagonist must choose how to answer the central question.
  The climax resolves using rules already established -- not new powers or
  information invented at the last minute. Show the aftermath of the choice.

CONSTRAINTS:
- The climax must be mechanically resolvable using rules already
  established in the world bible -- no new powers or last-minute exceptions
- The Stability Trap: bad things must stay bad. Not everything resolves cleanly.
- Every character in CHARACTER REGISTRY with a wound/want/need/lie chain
  should appear in person at least once, not only through memory or other
  characters' accounts
- At least 3 chapters should be "quiet" -- character-focused, low-action, emotionally rich
- Vary the try-fail types: 60%+ should be "yes-but" or "no-and"
- The foreshadowing ledger must have plant-to-payoff distances of at least 3 chapters
"""


def main():
    seed = load_file_bilingue(BASE_DIR, "semilla.txt", "seed.txt")
    exigir_semilla(seed, "generar un esquema")

    world = load_file_bilingue(BASE_DIR, "mundo.md", "world.md")
    characters = load_file_bilingue(BASE_DIR, "personajes.md", "characters.md")
    mystery = load_file_bilingue(BASE_DIR, "MISTERIO.md", "MYSTERY.md")
    craft = load_file(BASE_DIR / "CRAFT.md")
    voice = load_file_bilingue(BASE_DIR, "voz.md", "voice.md")
    voice_part2 = extraer_voz_parte2(voice)

    prompt = build_prompt(seed, world, characters, mystery, craft, voice_part2)

    print("Calling writer model...", file=sys.stderr)
    result = call_writer(prompt)

    out_path = ruta_bilingue(BASE_DIR, "esquema.md", "outline.md")
    out_path.write_text(result, encoding="utf-8")
    print(f"Saved to {out_path}", file=sys.stderr)
    print(result)


if __name__ == "__main__":
    main()
