#!/usr/bin/env python3
"""
evaluate.py -- Novel evaluation harness.

Usage:
  python evaluate.py --phase=foundation    # Score planning docs only
  python evaluate.py --chapter=5           # Score a single chapter
  python evaluate.py --full                # Score the entire novel

Output: structured scores to stdout + eval_logs/<timestamp>.json

This file is READ-ONLY during autonomous runs. The human edits it
to tune what "good" means. The agent treats it as a black box.
"""

import argparse
import json
import os
import sys
import glob
import re
from datetime import datetime
from pathlib import Path

# --- Configuration ---
BASE_DIR = Path(__file__).parent

# Load .env file if present
from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

from api_comun import llamar_api

# Judge uses Opus 4.6 (harsh, critical). Writer uses Sonnet 4.6 (fast, long context).
# Intentionally different to avoid self-congratulation.
JUDGE_MODEL = os.environ.get("AUTONOVEL_JUDGE_MODEL", "claude-opus-4-6")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_BASE_URL = os.environ.get("AUTONOVEL_API_BASE_URL", "https://api.anthropic.com")

# Beta header to unlock 1M context window on both Opus 4.6 and Sonnet 4.6
ANTHROPIC_BETA = "context-1m-2025-08-07"
CHAPTERS_DIR = BASE_DIR / "chapters"
EVAL_LOG_DIR = BASE_DIR / "eval_logs"
EVAL_LOG_DIR.mkdir(exist_ok=True)


# ---- Mechanical Slop Detection (no LLM needed) ----
#
# Constantes en español (deteccion_es.py). Reemplazan las listas en inglés
# del repositorio original -- no es traducción, son huellas de IA distintas
# por idioma. Ver ENCARGO_CLAUDE_CODE.md, Tarea 1a/1c.

from deteccion_es import (
    NIVEL1_PROHIBIDAS,
    NIVEL1_LOCUCIONES,
    NIVEL2_SOSPECHOSAS,
    NIVEL3_MULETILLAS,
    CONECTORES_APERTURA,
    CLICHES_FICCION,
    TICS_ESTRUCTURALES,
    PATRONES_CONTAR,
    CALCOS_DEL_INGLES,
    densidad_raya_parentetica,
    dividir_oraciones,
    cv_longitud_oracion,
    calcos_detectados,
    CALIBRACION,
)

_PUNTUACION = ".,;:!?\"'()¿¡«»"


# ---- Ambición por capítulo (Tarea 3) ----
#
# Un umbral único (6.0) empuja la novela hacia la media. Cada capítulo del
# esquema declara su propia ambición y compite contra su propio umbral.

UMBRALES_AMBICION = {
    "pico": 7.5,     # escena que el lector tiene que recordar
    "sosten": 6.5,   # capítulo de trabajo, avanza la trama
    "valle": CALIBRACION["umbral_aceptacion_capitulo"],  # respiro deliberado
}

# Sin ambición declarada, el umbral por defecto NO puede ser el más flojo
# ("valle", 6.0): eso haría que cualquier esquema que no se moleste en
# declarar ambición vuelva en silencio al comportamiento que esta tarea
# vino a corregir. "sosten" (6.5) es el default -- un capítulo de trabajo
# normal, ni el más exigente ni el más laxo.
UMBRAL_POR_DEFECTO_SIN_AMBICION = UMBRALES_AMBICION["sosten"]

PROPORCION_MINIMA_PICOS = 0.15
PROPORCION_MAXIMA_PICOS_ULTIMO_TERCIO = 0.80


def extraer_ambicion(chapter_outline_text):
    """Ambición declarada del capítulo (pico|sosten|valle) desde su entrada
    en el esquema. None si no está declarada -- esquemas viejos sin este
    campo siguen funcionando, no rompen (ver UMBRAL_POR_DEFECTO_SIN_AMBICION)."""
    m = re.search(
        r'ambici[oó]n\W{0,6}(pico|sost[ée]n|valle)',
        chapter_outline_text, re.IGNORECASE,
    )
    if not m:
        return None
    return m.group(1).lower().replace('é', 'e')


def umbral_por_ambicion(ambicion):
    """Umbral de aceptación según la ambición declarada. Sin ambición
    (esquemas viejos, o campo ausente en este capítulo) usa
    UMBRAL_POR_DEFECTO_SIN_AMBICION ("sosten", 6.5) -- nunca el umbral más
    laxo, para no revertir en silencio al comportamiento anterior."""
    return UMBRALES_AMBICION.get(ambicion, UMBRAL_POR_DEFECTO_SIN_AMBICION)


def validar_diversidad_ambicion(outline_text):
    """Dos formas en que un esquema puede fallar en tener picos reales:

    1. Esquema plano: menos del 15% de los capítulos son 'pico' (o ninguno
       declara ambición). Empuja la novela hacia el promedio.
    2. Picos mal distribuidos: 80%+ o más de los picos declarados están
       amontonados en el último tercio del esquema. Aunque la proporción
       total esté bien, si todos los momentos memorables se acumulan al
       final, el resto de la novela sigue siendo plano.

    Devuelve un mensaje de advertencia (puede combinar ambos problemas) o
    None si el esquema está bien."""
    ambiciones = re.findall(
        r'ambici[oó]n\W{0,6}(pico|sost[ée]n|valle)', outline_text, re.IGNORECASE,
    )
    if not ambiciones:
        return ("El esquema no declara ambición por capítulo (pico/sostén/"
                "valle) en ningún capítulo -- no se puede validar la "
                "proporción ni la distribución de picos.")
    ambiciones = [a.lower().replace('é', 'e') for a in ambiciones]
    total = len(ambiciones)
    picos_totales = sum(1 for a in ambiciones if a == "pico")

    advertencias = []

    proporcion = picos_totales / total
    if proporcion < PROPORCION_MINIMA_PICOS:
        advertencias.append(
            f"Esquema plano: solo {picos_totales}/{total} capítulos "
            f"({proporcion:.0%}) están marcados como 'pico'. Se recomienda "
            f"al menos {PROPORCION_MINIMA_PICOS:.0%}."
        )

    if picos_totales > 0:
        inicio_ultimo_tercio = (2 * total) // 3
        picos_ultimo_tercio = sum(
            1 for a in ambiciones[inicio_ultimo_tercio:] if a == "pico"
        )
        concentracion = picos_ultimo_tercio / picos_totales
        if concentracion >= PROPORCION_MAXIMA_PICOS_ULTIMO_TERCIO:
            advertencias.append(
                f"Picos mal distribuidos: {picos_ultimo_tercio}/{picos_totales} "
                f"picos ({concentracion:.0%}) están concentrados en el último "
                f"tercio del esquema. Deberían repartirse a lo largo de la "
                f"novela, no acumularse al final."
            )

    return " ".join(advertencias) if advertencias else None


# ---- Alcance de siembra (Tarea 4) ----
#
# Hoy toda siembra del libro de siembras debe pagarse dentro del mismo
# volumen, y el evaluador castiga las que quedan abiertas. Para una serie
# eso está mal: el Libro I tiene que poder sembrar para el Libro V sin que
# lo marquen como hilo suelto. Cada entrada de siembra:
#
#   {
#     "id": "identificador-legible",
#     "siembra": {"libro": 1, "capitulo": 3},
#     "pago":    {"libro": 2, "capitulo": 14},   # o None si no está asignado
#     "alcance": "libro" | "serie",
#     "estado":  "pendiente" | "pagada",
#   }
#
# NOTA DE ALCANCE: estas funciones validan entradas ya estructuradas
# (dicts). Todavía no hay un parser que las extraiga de la tabla del
# Foreshadowing Ledger en outline.md/esquema.md -- ver docs/HALLAZGOS.md.

SIEMBRAS_SERIE_PATH = BASE_DIR / "siembras_serie.md"


def alcance_serie_disponible():
    """True si existe siembras_serie.md (estamos en una rama de serie).
    Si no existe, la novela es suelta: el alcance de serie no está
    disponible y toda siembra se trata como alcance 'libro', sin importar
    lo que declare -- comportamiento idéntico al de antes de esta tarea."""
    return SIEMBRAS_SERIE_PATH.exists()


def validar_siembra(entrada, alcance_serie_disponible_, libros_completos=None):
    """Valida una entrada del libro de siembras contra las 4 reglas de la
    Tarea 4. Devuelve un mensaje de error, o None si está bien.

    alcance_serie_disponible_: si es False (no existe siembras_serie.md),
    la entrada se valida como si fuera alcance "libro" sin importar lo que
    declare -- es la regla de regresión: novela suelta = comportamiento de
    siempre.
    libros_completos: colección de números de libro ya publicados/cerrados
    (para la regla 4). None o vacío si no aplica."""
    libros_completos = libros_completos or set()
    ident = entrada.get("id", "?")
    alcance = entrada.get("alcance", "libro")
    if not alcance_serie_disponible_:
        alcance = "libro"

    siembra_libro = entrada["siembra"]["libro"]
    pago = entrada.get("pago") or {}
    pago_libro = pago.get("libro")
    pagada_en_el_volumen = pago_libro is not None and pago_libro == siembra_libro

    if alcance == "libro":
        if not pagada_en_el_volumen:
            return f'"{ident}": alcance "libro" sin pago dentro del volumen.'
        return None

    # alcance == "serie"
    if pago_libro is None:
        return f'"{ident}": alcance "serie" sin libro de pago asignado.'
    if pago_libro in libros_completos:
        return (f'"{ident}": alcance "serie" con pago asignado al libro '
                f'{pago_libro}, ya publicado.')
    return None


def validar_libro_de_siembras(entradas, libros_completos=None):
    """Valida todas las entradas del libro de siembras. Devuelve la lista
    de mensajes de error (vacía si todo está bien). Consulta
    alcance_serie_disponible() una sola vez para todas las entradas."""
    disponible = alcance_serie_disponible()
    return [
        error
        for entrada in entradas
        if (error := validar_siembra(entrada, disponible, libros_completos))
    ]


def slop_score(text):
    """
    Detección mecánica de slop (español -- deteccion_es.py). Devuelve un dict:
      - tier1_hits: list of (word_or_locucion, count)
      - tier2_hits: list of (word, count)
      - tier3_hits: list of (pattern, count)
      - calco_hits: list of (descripción, count)
      - em_dash_density: raya PARENTÉTICA por mil palabras (no cuenta diálogo)
      - sentence_length_cv: coeficiente de variación (más alto = más humano)
      - transition_opener_ratio: fracción de párrafos que abren con conector
      - slop_penalty: 0-10 deducción (0 = limpio, 10 = puro slop)
    """
    words = text.lower().split()
    word_count = len(words) or 1

    # Nivel 1: palabras prohibidas + locuciones (necesitan regex)
    tier1_hits = []
    for w in NIVEL1_PROHIBIDAS:
        c = sum(1 for token in words if token.strip(_PUNTUACION) == w)
        if c > 0:
            tier1_hits.append((w, c))
    for pattern in NIVEL1_LOCUCIONES:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            tier1_hits.append((pattern[:40], len(matches)))

    # Nivel 2 -- cuenta por párrafo, marca racimos (3+ por párrafo)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    tier2_hits = []
    tier2_cluster_count = 0
    for w in NIVEL2_SOSPECHOSAS:
        c = sum(1 for token in words if token.strip(_PUNTUACION) == w)
        if c > 0:
            tier2_hits.append((w, c))
    for para in paragraphs:
        para_lower = para.lower()
        hits_in_para = sum(1 for w in NIVEL2_SOSPECHOSAS if w in para_lower)
        if hits_in_para >= 3:
            tier2_cluster_count += 1

    # Nivel 3: muletillas
    tier3_hits = []
    for pattern in NIVEL3_MULETILLAS:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        if matches:
            tier3_hits.append((pattern, len(matches)))

    # Raya parentética (no la de diálogo) por mil palabras
    em_dash_density = densidad_raya_parentetica(text)

    # Variación de longitud de oración (segmentación que respeta ¿ ¡ y abreviaturas)
    sentence_length_cv = cv_longitud_oracion(text)

    # Conectores de apertura de párrafo
    transition_starts = 0
    for para in paragraphs:
        first_word = para.split()[0].lower().strip(_PUNTUACION) if para.split() else ""
        if first_word in CONECTORES_APERTURA:
            transition_starts += 1
    transition_ratio = transition_starts / len(paragraphs) if paragraphs else 0

    # Clichés de ficción
    fiction_tells = []
    for pattern in CLICHES_FICCION:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            fiction_tells.append((pattern[:40], len(matches)))
    fiction_tell_count = sum(c for _, c in fiction_tells)

    # Contar en vez de mostrar (show-don't-tell)
    telling_count = 0
    for pattern in PATRONES_CONTAR:
        telling_count += len(re.findall(pattern, text, re.IGNORECASE))

    # Tics estructurales (fórmulas retóricas)
    structural_tics = []
    for pattern in TICS_ESTRUCTURALES:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            structural_tics.append((pattern[:40], len(matches)))
    structural_tic_count = sum(c for _, c in structural_tics)

    # Calcos del inglés
    calco_hits = calcos_detectados(text)
    calco_count = sum(c for _, c in calco_hits)

    # Penalización compuesta (0 = limpio, 10 = desastre)
    penalty = 0.0
    penalty += min(len(tier1_hits) * 1.5, 4.0)       # nivel 1: hasta 4 pts
    penalty += min(tier2_cluster_count * 1.0, 2.0)    # racimos nivel 2: hasta 2 pts
    penalty += min(sum(c for _, c in tier3_hits) * 0.3, 2.0)  # nivel 3: hasta 2 pts
    if em_dash_density > CALIBRACION["umbral_raya_parentetica"]:
        penalty += min((em_dash_density - CALIBRACION["umbral_raya_parentetica"]) * 0.3, 1.0)
    if sentence_length_cv < CALIBRACION["umbral_cv_oracion"]:
        penalty += 1.0  # oraciones muy uniformes: 1 pt
    if transition_ratio > 0.3:
        penalty += min(transition_ratio * 2, 1.0)  # abuso de conectores: hasta 1 pt
    penalty += min(fiction_tell_count * 0.3, 2.0)     # clichés de ficción: hasta 2 pts
    penalty += min(telling_count * 0.2, 1.5)          # contar-no-mostrar: hasta 1.5 pts
    penalty += min(structural_tic_count * 0.5, 2.0)   # tics estructurales: hasta 2 pts
    penalty += min(calco_count * 0.5, 2.0)            # calcos del inglés: hasta 2 pts

    penalty = min(penalty, 10.0)

    return {
        "tier1_hits": tier1_hits,
        "tier2_hits": tier2_hits,
        "tier2_clusters": tier2_cluster_count,
        "tier3_hits": tier3_hits,
        "fiction_ai_tells": fiction_tells,
        "structural_ai_tics": structural_tics,
        "telling_violations": telling_count,
        "calco_hits": calco_hits,
        "em_dash_density": round(em_dash_density, 2),
        "sentence_length_cv": round(sentence_length_cv, 3),
        "transition_opener_ratio": round(transition_ratio, 3),
        "slop_penalty": round(penalty, 2),
    }


def load_file(path):
    """Load a text file, return empty string if missing."""
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return ""


def load_layer_files():
    """Load all planning layer files."""
    return {
        "voice": load_file(BASE_DIR / "voice.md"),
        "world": load_file(BASE_DIR / "world.md"),
        "characters": load_file(BASE_DIR / "characters.md"),
        "outline": load_file(BASE_DIR / "outline.md"),
        "canon": load_file(BASE_DIR / "canon.md"),
        # Hechos establecidos durante la redacción (Tarea 10) -- los
        # escribe actualizar_canon.py a partir de new_canon_entries.
        # canon.md sigue siendo función pura de semilla+mundo+personajes
        # (lo pisa gen_canon.py); este es el otro archivo, nunca tocado
        # por gen_canon.py, para que uno se pueda regenerar sin perder
        # el otro.
        "canon_emergente": load_file(BASE_DIR / "canon_emergente.md"),
    }


def load_chapter(n):
    """Load a single chapter file."""
    return load_file(CHAPTERS_DIR / f"ch_{n:02d}.md")


def load_all_chapters():
    """Load all chapter files in order."""
    chapters = {}
    for f in sorted(glob.glob(str(CHAPTERS_DIR / "ch_*.md"))):
        num = int(re.search(r'ch_(\d+)', f).group(1))
        chapters[num] = Path(f).read_text()
    return chapters


def call_judge(prompt, max_tokens=2000):
    """Call the Anthropic judge LLM and return its response text."""
    return llamar_api(
        prompt,
        model=JUDGE_MODEL,
        max_tokens=max_tokens,
        system="You are a literary critic and novel editor. "
               "You evaluate fiction with precision. Return valid JSON only. "
               "Escape double quotes and newlines within any string value, "
               "including verbatim quotes from canon.md, canon_emergente.md, "
               "or the chapter text. "
               "No markdown fences, no preamble -- just the JSON object.",
        beta=ANTHROPIC_BETA,
        api_key=ANTHROPIC_API_KEY,
        api_base=API_BASE_URL,
    )


def parse_json_response(text):
    """Extract JSON from a response that might have markdown fences or trailing text."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```\w*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
    # Find the outermost JSON object
    start = text.find('{')
    if start == -1:
        raise ValueError("No JSON object found in response")
    # Walk forward to find the matching closing brace
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        c = text[i]
        if escape:
            escape = False
            continue
        if c == '\\' and in_string:
            escape = True
            continue
        if c == '"' and not escape:
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i+1], strict=False)
    # Fallback: try loading as-is, with strict=False to handle control chars
    try:
        return json.loads(text, strict=False)
    except json.JSONDecodeError:
        # Last resort: fix common issues (literal newlines in strings)
        fixed = re.sub(r'(?<!\\)\n', '\\n', text)
        return json.loads(fixed, strict=False)


# --- Foundation Evaluation ---

FOUNDATION_PROMPT = """Evaluate these fantasy novel planning documents.

SCORING CALIBRATION (read this before scoring anything):

  9-10: Could not improve this with a month of focused editorial work.
        Published-novel quality. You can name the specific published
        novel it competes with. Reserve 10 for work that SURPRISES you.
  7-8:  Strong. A skilled author could draft from this document with
        minimal invention. Gaps exist but are minor and enumerable.
  5-6:  Functional but thin. A writer would need to invent significant
        material on the fly. Major gaps or generic choices.
  3-4:  Sketchy. More questions than answers. Would require heavy
        supplementation before drafting.
  1-2:  Placeholder or stub. Not usable for drafting.
  0:    Empty or missing.

  A score of 8+ requires ZERO major gaps. A score of 9+ requires
  that you genuinely struggled to find flaws. Err toward lower scores.

MANDATORY: For EVERY dimension, before scoring, you must identify:
  (a) The single biggest GAP or WEAKNESS in that area
  (b) A specific, actionable improvement that would raise the score
  If you cannot find a gap, explain why you believe one doesn't exist.

VOICE DEFINITION:
{voice}

WORLD BIBLE:
{world}

CHARACTER REGISTRY:
{characters}

OUTLINE:
{outline}

CANON (established facts):
{canon}

CROSS-CHECKS (perform these before scoring):
1. Check all example dialogue lines against ANTI-SLOP patterns:
   - Look for structural formulas repeated across characters
     ("not X, but Y" / "either X, or Y" / "there's a difference")
   - Check for AI rhetorical tics disguised as character voice
   - Deduct from character_distinctiveness if multiple characters
     share the same sentence structures
2. Check for missing NEGATIVE SPACE -- what's absent?
   - Are there gaps in the magic system that would block a specific
     plot scene? (e.g., can Cass hear lies in written documents?
     What happens during the climax -- what rule resolves it?)
   - Are there characters needed for the plot who don't exist?
   - Are there scenes the outline demands that the world can't support?
3. Check for CONVENIENT GAPS vs DELIBERATE MYSTERY:
   - Convenient: "the details are unclear" where specifics are needed
   - Deliberate: withholding information from the READER while the
     AUTHOR knows the answer. If the planning docs dodge a question
     that a writer would need answered to draft a scene, that's a gap,
     not an iceberg.
4. Check the canon for INTERNAL CONTRADICTIONS:
   - Cross-reference dates, ages, and timelines
   - Check if character abilities match magic system rules
   - Look for factual conflicts between documents

Score these dimensions (gap + improvement required for each):

LORE & WORLDBUILDING:
- magic_system: Hard rules with COSTS and LIMITATIONS per Sanderson's
  Second Law. Could a writer resolve the CLIMACTIC CONFLICT using only
  rules already established? Are costs plot-driving, not decorative?
  Are there at least 3 societal implications explored with specificity?
  Is the system TESTABLE -- could you write a courtroom scene, a
  contract negotiation, and a magical confrontation without inventing
  new rules?
- world_history: Timeline of events creating PRESENT-DAY tensions.
  Each historical event should map to a current faction conflict or
  character motivation. Decorative history (cool but plot-irrelevant)
  counts against the score, not for it.
- geography_and_culture: Locations distinct with sensory signatures.
  Cultures with specific customs that GENERATE CONFLICT. Economy that
  creates class tension. Check: could two different scenes set in two
  different locations feel meaningfully different based on what's here?
- lore_interconnection: Does changing one element force changes in
  at least two others? Test by mentally removing the magic system --
  does the political structure collapse? Does the class system change?
  If elements are modular/detachable, score low.
- iceberg_depth: Implied depth vs stated depth. But CHECK: does the
  author actually know the answers to the mysteries, or are they
  handwaving? If a planning doc says "the answer will be revealed"
  without specifying WHAT the answer is, that's a gap wearing an
  iceberg costume.

CHARACTER:
- character_depth: Wound/want/need/lie chains that are CAUSALLY LINKED
  (not just thematically associated). The lie must logically follow
  from the wound. The want must be the wrong solution to the lie.
  The need must directly oppose the want. Check each chain for
  logical gaps. Also check: are ANY characters missing wound/want/need
  chains who probably need them?
- character_distinctiveness: Remove all dialogue tags from the example
  lines. Can you identify the speaker from sentence structure alone?
  Check for REPEATED STRUCTURAL FORMULAS across characters (e.g.,
  multiple characters using "X. Not Y." or balanced antithesis).
  Check that metaphor domains don't overlap. Check that speech
  patterns reflect character background (a 14-year-old should not
  sound like a 60-year-old merchant).
- character_secrets: Each major character's secret should be something
  that, if revealed, changes the plot's trajectory. Vague secrets
  ("he knows more than he says") score lower than specific ones
  ("he knows the harmonic means X, which would invalidate Y").

STRUCTURE:
- outline_completeness: Chapters with beats, POV, emotional arc,
  try-fail cycle type. Save the Cat beats at correct % marks.
  Score 0 if empty. Score 5+ only if act structure exists.
- foreshadowing_balance: Every planted thread has a planned payoff.
  Score 0 if ledger is empty regardless of implicit threads in
  other documents -- foreshadowing must be TRACKED to count.

CRAFT:
- internal_consistency: Actively hunt for contradictions. Cross-ref
  dates, ages, character counts, named locations. Flag any case
  where documents disagree. A single major contradiction caps this
  at 6. Three or more caps at 4.
- voice_clarity: Voice definition must be specific and ACTIONABLE.
  Exemplar passages must demonstrate the voice. Anti-exemplars must
  define boundaries. Check exemplar dialogue for AI slop patterns.
  A voice doc that is beautiful but contains slop in its own examples
  is undermined -- deduct.
- canon_coverage: Facts logged, sourced, and sufficient to catch
  contradictions. Check: if a writer introduced a NEW fact in
  chapter 5, could they verify it against the canon? Is the canon
  granular enough? Are there known facts from other docs that
  AREN'T in the canon?

Respond with JSON:
{{
  "magic_system": {{"score": N, "gap": "biggest weakness", "fix": "specific improvement", "note": "..."}},
  "world_history": {{"score": N, "gap": "...", "fix": "...", "note": "..."}},
  "geography_and_culture": {{"score": N, "gap": "...", "fix": "...", "note": "..."}},
  "lore_interconnection": {{"score": N, "gap": "...", "fix": "...", "note": "..."}},
  "iceberg_depth": {{"score": N, "gap": "...", "fix": "...", "note": "..."}},
  "character_depth": {{"score": N, "gap": "...", "fix": "...", "note": "..."}},
  "character_distinctiveness": {{"score": N, "gap": "...", "fix": "...", "note": "..."}},
  "character_secrets": {{"score": N, "gap": "...", "fix": "...", "note": "..."}},
  "outline_completeness": {{"score": N, "gap": "...", "fix": "...", "note": "..."}},
  "foreshadowing_balance": {{"score": N, "gap": "...", "fix": "...", "note": "..."}},
  "internal_consistency": {{"score": N, "gap": "...", "fix": "...", "note": "..."}},
  "voice_clarity": {{"score": N, "gap": "...", "fix": "...", "note": "..."}},
  "canon_coverage": {{"score": N, "gap": "...", "fix": "...", "note": "..."}},
  "slop_in_planning_docs": {{"found": ["list any AI slop patterns found in exemplar dialogue, voice examples, or character descriptions"], "note": "..."}},
  "contradictions_found": ["list any factual contradictions between documents"],
  "overall_score": N,
  "lore_score": N,
  "weakest_dimension": "...",
  "top_3_improvements": ["ranked list of the 3 highest-leverage improvements"]
}}

WEIGHTING: lore/worldbuilding 40%, character 30%, structure 20%, craft 10%.
A novel with thin worldbuilding but a complete outline is WORSE than deep
worldbuilding with an incomplete outline.

FINAL CHECK: If your overall_score is above 7, re-read your gap lists.
If any gap describes a problem that would force a writer to stop and
invent something during drafting, your score is too high. Revise down.
"""


def evaluate_foundation():
    layers = load_layer_files()
    prompt = FOUNDATION_PROMPT.format(**layers)
    raw = call_judge(prompt, max_tokens=16000)
    result = parse_json_response(raw)

    advertencia = validar_diversidad_ambicion(layers["outline"])
    if advertencia:
        result["advertencia_ambicion"] = advertencia

    return result


# --- Chapter Evaluation ---

CHAPTER_PROMPT = """Evaluá este capítulo de novela contra los documentos de planificación.

El texto está en español. Antes de juzgar, tené en cuenta:
- El diálogo se marca con raya (—), no con comillas. Es correcto.
- La subordinación larga y la coordinación con «y» son recursos legítimos
  del castellano, no verbosidad.
- El sujeto pronominal se omite por defecto. Su ausencia es correcta;
  su presencia repetida es un calco del inglés y sí es un defecto.
- El español corre entre 15% y 20% más largo que el inglés para el mismo
  contenido. No penalices por extensión comparándolo con prosa inglesa.

CALIBRACIÓN DE PUNTAJE:
  9-10: Entre los mejores capítulos que hayas leído en un thriller
        literario publicado. Nombrá un capítulo publicado específico
        con el que compite, o no des 9+.
  7-8:  Sólido, publicable con pulido editorial. Existen fallas
        puntuales pero no rompen la experiencia de lectura.
  5-6:  Funcional pero chato. Un borrador competente que necesita
        revisión sustancial. Genérico donde debería ser específico.
        Prudente donde debería arriesgar.
  3-4:  Problemas significativos. Se rompe la voz, faltan beats,
        prosa genérica.
  1-2:  No usable. Reescribir desde cero.

  El puntaje MEDIANO para un capítulo competente generado por IA debe
  ser 6. Un 7 significa que hace algo que un borrador de IA genérico
  no haría. Un 8 significa que un editor humano lo dejaría con notas
  menores. La mayoría de las dimensiones deberían puntuar 6-7.
  Reservá 8+ para excelencia genuina.

OBLIGATORIO: para cada dimensión tenés que identificar:
  (a) El MOMENTO MÁS DÉBIL -- citá la oración o el pasaje específico
  (b) Qué lo mejoraría -- una revisión concreta, no una nota vaga
  Si cada oración te parece perfecta, no estás leyendo con suficiente
  atención.

DEFINICIÓN DE VOZ:
{voice}

BIBLIA DE MUNDO (resumen):
{world}

REGISTRO DE PERSONAJES:
{characters}

CANON (hechos duros establecidos -- las violaciones son bugs):
{canon}

CANON EMERGENTE (hechos establecidos durante la redacción de capítulos
anteriores -- misma fuerza que el canon de arriba; un hecho inventado
en un capítulo previo no puede contradecirse acá):
{canon_emergente}

ENTRADA DEL ESQUEMA PARA ESTE CAPÍTULO:
{chapter_outline}

CAPÍTULO ANTERIOR (últimas 1500 palabras):
{prev_chapter_tail}

EL CAPÍTULO A EVALUAR:
{chapter_text}

CHEQUEOS CRUZADOS (hacé esto antes de puntuar):
1. PRUEBA DE CITA: Encontrá las 3 mejores oraciones y las 3 más
   débiles. Si no podés encontrar 3 débiles, estás bajando el
   estándar -- todo capítulo tiene momentos flojos. Buscá: frases
   genéricas donde había lugar para ser específico, monotonía rítmica
   en algún párrafo, metáforas que no salen de la experiencia del
   personaje, momentos emocionales que se cuentan en vez de mostrarse,
   transiciones que resumen en vez de dramatizar.
2. REALISMO DEL DIÁLOGO: Leé todo el diálogo en voz alta (mentalmente).
   ¿Suena a habla o a prosa escrita? ¿Los personajes dicen cosas que
   dirían de verdad, dada su edad y trasfondo?
3. ESCENA VS RESUMEN: ¿Cuánto del capítulo está en escena (momento a
   momento, con diálogo y acción) vs en resumen (el narrador
   comprimiendo tiempo)? Los capítulos cargados de resumen puntúan más
   bajo en enganche sin importar la calidad de la prosa.
4. CHEQUEO DE PATRONES DE IA: Buscá estos patrones comunes de
   escritura de IA:
   - Todos los párrafos de la misma longitud
   - Observaciones siempre de a tres (X, Y y Z)
   - Beats emocionales que llegan justo cuando se los espera, en vez de sorprender
   - Personajes que nunca dicen algo equivocado ni hablan cruzado
   - Descripción que cataloga en vez de seleccionar (cinco detalles
     sensoriales listados cuando dos específicos serían más filosos)
   - Monólogo interior que explica lo que la escena ya mostró
5. GANADO VS REGALADO: ¿La tensión se gana con trabajo de escena o se
   le entrega al lector a través de las afirmaciones del narrador? ¿El
   misterio se sostiene con una omisión genuina, o porque el personaje
   convenientemente no piensa en cosas que pensaría?

Puntuá estas dimensiones:

- voice_adherence: ¿La prosa coincide con voz.md Parte 2? Chequeá:
  variación del ritmo de las oraciones, pozos léxicos, el principio de
  cuerpo-antes-que-emoción, el tono específico descrito. Citá el mejor
  momento de voz Y el más débil. ¿Algún pasaje suena a prosa genérica
  que podría aparecer en cualquier novela? Si sí, puntaje máximo 7.

- beat_coverage: ¿Cumplió cada beat del esquema? ¿Los beats se
  dramatizaron o solo se mencionaron? Un beat resumido en una oración
  en vez de vivido en una escena cuenta como medio cumplido. El
  puntaje refleja la CALIDAD de la ejecución del beat, no solo su
  presencia.

- character_voice: Sacá mentalmente todas las acotaciones de diálogo.
  ¿Podés distinguir quién habla? ¿Algún personaje suena como otro? ¿El
  diálogo se lee como habla o como prosa escrita? ¿El personaje POV
  suena a una persona específica con su edad y trasfondo reales, o a
  "protagonista genérico"? ¿Alguien dice algo sorprendente -- no solo
  lo correcto, sino algo REAL? Los personajes que nunca se traban,
  dudan o dicen algo levemente equivocado son personajes con patrón de
  IA.

- plants_seeded: ¿Los elementos de anticipación se ubicaron con
  naturalidad? Una siembra obvia es peor que una siembra invisible. El
  puntaje se basa en QUÉ TAN BIEN están integrados, no solo en si
  están presentes.

- prose_quality: Variedad de oraciones (medida: ¿3 o más oraciones
  consecutivas empiezan igual?). Especificidad (sustantivos concretos
  por sobre abstractos). Metáforas que salen de la experiencia del
  personaje, no de un diccionario de sinónimos. Mostrar-no-contar en
  los picos emocionales. CITÁ la oración más débil y explicá por qué.
  Chequeá también: frases repetidas, construcciones muy usadas,
  párrafos que se podrían cortar sin pérdida.

- continuity: ¿Sigue lógicamente del capítulo anterior? Continuidad
  emocional además de continuidad de trama. ¿El estado de ánimo del
  personaje se sostiene?

- canon_compliance: Chequeá TODOS los hechos contra el canon (el de
  fundación y el emergente, arriba). Listá violaciones. Una violación
  mayor limita el puntaje a 6 como máximo. Chequeá: nombres de
  personajes, lugares, reglas establecidas del mundo, cronología,
  eventos ya establecidos, descripciones físicas. Si un hecho nuevo de
  este capítulo contradice algo del canon o del canon emergente,
  repórtalo tanto acá como en new_canon_entries (con "contradice"
  apuntando a la entrada de canon que contradice).

- lore_integration: ¿El mundo hace TRABAJO en este capítulo, o es
  decorado? Una escena que podría pasar en cualquier ciudad con
  buscar-y-reemplazar en los nombres propios saca 5 como máximo.

- engagement: ¿Un lector pasaría la página? ¿De dónde viene la tensión
  -- trama, personaje, misterio, prosa? ¿Hay un momento que SORPRENDA?
  La excelencia predecible sigue siendo predecible. Puntaje 8+ solo si
  el capítulo hace algo inesperado.

Respondé con JSON:
{{
  "voice_adherence": {{"score": N, "weakest_moment": "cita del pasaje débil específico", "fix": "cómo mejorarlo", "note": "..."}},
  "beat_coverage": {{"score": N, "weakest_moment": "...", "fix": "...", "note": "..."}},
  "character_voice": {{"score": N, "weakest_moment": "...", "fix": "...", "note": "..."}},
  "plants_seeded": {{"score": N, "weakest_moment": "...", "fix": "...", "note": "..."}},
  "prose_quality": {{"score": N, "weakest_sentence": "cítala", "fix": "sugerencia de reescritura", "strongest_sentence": "cítala", "note": "..."}},
  "continuity": {{"score": N, "note": "..."}},
  "canon_compliance": {{"score": N, "violations": ["listá las encontradas"], "note": "..."}},
  "lore_integration": {{"score": N, "weakest_moment": "...", "fix": "...", "note": "..."}},
  "engagement": {{"score": N, "weakest_moment": "...", "fix": "...", "note": "..."}},
  "three_weakest_sentences": ["cita 1", "cita 2", "cita 3"],
  "three_strongest_sentences": ["cita 1", "cita 2", "cita 3"],
  "ai_patterns_detected": ["listá los patrones de escritura de IA encontrados"],
  "overall_score": N,
  "weakest_dimension": "...",
  "top_3_revisions": ["revisión concreta y accionable 1", "revisión 2", "revisión 3"],
  "new_canon_entries": [
    {{"categoria": "una de: Geografía, Cronología, Reglas excepcionales del mundo, Hechos de personajes, Político / faccional, Cultural, Establecido en la historia", "hecho": "el hecho nuevo, corto y verificable", "contradice": "texto exacto de la entrada de canon.md o canon_emergente.md que contradice, o null si no hay contradicción"}}
  ]
}}

CHEQUEO FINAL: Si tu overall_score es mayor a 7, releé tus citas de
weakest_moment. Si alguna describe un problema que un editor marcaría,
tu puntaje es demasiado alto. El capítulo mediano de IA es un 6. Un 8
es excepcional. Un 9 es raro. Un 10 no existe para un primer borrador.
"""


def evaluate_chapter(chapter_num):
    layers = load_layer_files()
    chapter_text = load_chapter(chapter_num)
    if not chapter_text.strip():
        return {"error": f"Chapter {chapter_num} is empty or missing",
                "overall_score": 0.0}

    # Extract this chapter's outline entry (rough heuristic)
    outline = layers["outline"]
    ch_pattern = rf'###\s*Ch\s*{chapter_num}\b.*?(?=###\s*Ch\s*\d|## Act|## Foreshadowing|$)'
    ch_match = re.search(ch_pattern, outline, re.DOTALL)
    chapter_outline = ch_match.group(0) if ch_match else "(outline entry not found)"

    # Load previous chapter tail
    prev_text = load_chapter(chapter_num - 1) if chapter_num > 1 else "(first chapter)"
    prev_tail = prev_text[-3000:] if len(prev_text) > 3000 else prev_text

    prompt = CHAPTER_PROMPT.format(
        voice=layers["voice"],
        world=layers["world"][:4000],  # truncate world bible
        characters=layers["characters"],
        canon=layers["canon"],
        canon_emergente=layers["canon_emergente"] or "(sin hechos emergentes todavía)",
        chapter_outline=chapter_outline,
        prev_chapter_tail=prev_tail,
        chapter_text=chapter_text,
    )
    raw = call_judge(prompt, max_tokens=8000)
    try:
        result = parse_json_response(raw)
    except (ValueError, json.JSONDecodeError) as e:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_path = EVAL_LOG_DIR / f"{timestamp}_ch{chapter_num:02d}_RAW_FALLIDO.txt"
        raw_path.write_text(raw, encoding="utf-8")
        sys.exit(
            f"ERROR: la respuesta del juez para el Cap. {chapter_num} no es "
            f"JSON válido ({e}). La llamada ya se pagó -- se guardó sin "
            f"parsear en {raw_path} para inspección, en vez de perderse."
        )

    # Mechanical slop check -- adjusts score independently of judge
    slop = slop_score(chapter_text)
    result["slop"] = slop
    if "overall_score" in result:
        adjusted = max(0, result["overall_score"] - slop["slop_penalty"])
        result["raw_judge_score"] = result["overall_score"]
        result["overall_score"] = round(adjusted, 2)

    # Umbral de aceptación por ambición del capítulo (Tarea 3), no una
    # constante global -- ver UMBRALES_AMBICION.
    ambicion = extraer_ambicion(chapter_outline)
    umbral = umbral_por_ambicion(ambicion)
    result["ambicion"] = ambicion or "(no declarada)"
    result["umbral_aceptacion"] = umbral
    if "overall_score" in result:
        result["aceptado"] = result["overall_score"] >= umbral

    return result


# --- Full Novel Evaluation ---

FULL_NOVEL_PROMPT = """Evaluate this complete fantasy novel holistically.
You have the planning docs and ALL chapter summaries with their individual scores.

VOICE DEFINITION:
{voice}

WORLD BIBLE:
{world_summary}

CHARACTER REGISTRY:
{characters}

OUTLINE + FORESHADOWING LEDGER:
{outline}

CHAPTER SUMMARIES AND SCORES:
{chapter_summaries}

Score these novel-level dimensions 0-10:
- arc_completion: Do character arcs resolve satisfyingly?
- pacing_curve: Does tension build properly across the book?
- theme_coherence: Are themes explored consistently?
- foreshadowing_resolution: Are all planted threads harvested?
- world_consistency: Any lore contradictions across chapters?
- voice_consistency: Is the voice steady throughout?
- overall_engagement: Is this a compelling read start to finish?

Respond with JSON:
{{
  "arc_completion": {{"score": N, "note": "..."}},
  "pacing_curve": {{"score": N, "note": "..."}},
  "theme_coherence": {{"score": N, "note": "..."}},
  "foreshadowing_resolution": {{"score": N, "note": "..."}},
  "world_consistency": {{"score": N, "note": "..."}},
  "voice_consistency": {{"score": N, "note": "..."}},
  "overall_engagement": {{"score": N, "note": "..."}},
  "novel_score": N,
  "weakest_dimension": "...",
  "weakest_chapter": N,
  "top_suggestion": "..."
}}
"""


def evaluate_full():
    layers = load_layer_files()
    chapters = load_all_chapters()

    if not chapters:
        return {"error": "No chapters found", "novel_score": 0.0}

    # Build chapter summaries (first/last 500 chars of each)
    summaries = []
    for num in sorted(chapters.keys()):
        text = chapters[num]
        word_count = len(text.split())
        head = text[:500]
        tail = text[-500:] if len(text) > 500 else ""
        summaries.append(
            f"Chapter {num} ({word_count} words):\n"
            f"  Opening: {head}...\n"
            f"  Closing: ...{tail}\n"
        )

    prompt = FULL_NOVEL_PROMPT.format(
        voice=layers["voice"],
        world_summary=layers["world"][:3000],
        characters=layers["characters"],
        outline=layers["outline"],
        chapter_summaries="\n".join(summaries),
    )
    raw = call_judge(prompt)
    return parse_json_response(raw)


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Evaluate the novel")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--phase", choices=["foundation"],
                       help="Evaluate planning documents")
    group.add_argument("--chapter", type=int,
                       help="Evaluate a specific chapter number")
    group.add_argument("--full", action="store_true",
                       help="Evaluate the entire novel")
    parser.add_argument("--archivo", type=str,
                       help="Ruta a un archivo de texto a evaluar "
                            "(solo válido junto con --solo-mecanico)")
    parser.add_argument("--solo-mecanico", action="store_true",
                       dest="solo_mecanico",
                       help="Corre solo slop_score() (sin LLM, sin API, "
                            "determinista). Usar con --chapter o --archivo.")
    args = parser.parse_args()

    if args.archivo and not args.solo_mecanico:
        parser.error("--archivo solo es válido junto con --solo-mecanico")

    if args.solo_mecanico:
        if args.archivo:
            chapter_text = Path(args.archivo).read_text()
            mode = Path(args.archivo).stem
        elif args.chapter is not None:
            chapter_text = load_chapter(args.chapter)
            mode = f"ch{args.chapter:02d}"
        else:
            parser.error("--solo-mecanico requiere --chapter o --archivo")

        result = slop_score(chapter_text)
        score_key = "slop_penalty"

        print("---")
        print(f"[solo-mecanico] {mode}")
        for key, val in result.items():
            print(f"{key}: {val}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = EVAL_LOG_DIR / f"{timestamp}_mecanico_{mode}.json"
        with open(log_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\neval_log: {log_path}")
        return

    if not (args.phase or args.chapter is not None or args.full):
        parser.error("Debe indicar --phase, --chapter, --full, o --archivo "
                     "con --solo-mecanico")

    if args.phase == "foundation":
        result = evaluate_foundation()
        score_key = "overall_score"
    elif args.chapter is not None:
        result = evaluate_chapter(args.chapter)
        score_key = "overall_score"
    elif args.full:
        result = evaluate_full()
        score_key = "novel_score"

    # Print structured output
    print("---")
    if score_key in result:
        print(f"{score_key}: {result[score_key]}")
    for key, val in result.items():
        if key == score_key:
            continue
        if isinstance(val, dict):
            print(f"{key}: {val.get('score', 'N/A')} -- {val.get('note', '')}")
        else:
            print(f"{key}: {val}")

    # Save full eval log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mode = args.phase or (f"ch{args.chapter:02d}" if args.chapter else "full")
    log_path = EVAL_LOG_DIR / f"{timestamp}_{mode}.json"
    with open(log_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\neval_log: {log_path}")


if __name__ == "__main__":
    main()
