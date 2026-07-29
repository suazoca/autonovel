#!/usr/bin/env python3
"""
Draft a single chapter using the writer model.
Usage: python draft_chapter.py 1
"""
import json
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv

from deteccion_es import CALIBRACION
from api_comun import llamar_api

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

WRITER_MODEL = os.environ.get("AUTONOVEL_WRITER_MODEL", "claude-sonnet-4-6")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_BASE = os.environ.get("AUTONOVEL_API_BASE_URL", "https://api.anthropic.com")
CHAPTERS_DIR = BASE_DIR / "chapters"
STATE_PATH = BASE_DIR / "state.json"

def call_writer(prompt, max_tokens=16000):
    return llamar_api(
        prompt,
        model=WRITER_MODEL,
        max_tokens=max_tokens,
        system=(
            "Sos un escritor de ficción literaria redactando un capítulo de "
            "novela, en español. Seguís la definición de voz exactamente. "
            "Cumplís cada beat del esquema. Nunca usás palabras de la lista "
            "prohibida. Mostrás, nunca explicás las emociones. Tu prosa es "
            "específica, sensorial, concreta. Las metáforas salen de la "
            "experiencia del personaje. Variás la longitud de las oraciones. "
            "Confiás en el lector. Escribís el capítulo COMPLETO -- no "
            "truncás, no resumís, no saltás adelante."
        ),
        beta="context-1m-2025-08-07",
        api_key=API_KEY,
        api_base=API_BASE,
    )

def load_file(path):
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return ""

def ruta_bilingue(nombre_es, nombre_en):
    """Nomenclatura de AUDITORIA_Y_PLAN.md: los archivos de contenido se
    renombran al español (voz.md, mundo.md, personajes.md, esquema.md).
    Preferí el nombre en español si existe; si no, caé al nombre en
    inglés (compatibilidad con ramas/plantillas viejas)."""
    ruta_es = BASE_DIR / nombre_es
    if ruta_es.exists():
        return ruta_es
    return BASE_DIR / nombre_en

def load_file_bilingue(nombre_es, nombre_en):
    return load_file(ruta_bilingue(nombre_es, nombre_en))

def load_state():
    try:
        return json.loads(STATE_PATH.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def extract_chapter_outline(outline_text, chapter_num):
    """Extract a specific chapter's outline entry."""
    pattern = rf'### Ch {chapter_num}:.*?(?=### Ch {chapter_num + 1}:|## Foreshadowing|$)'
    match = re.search(pattern, outline_text, re.DOTALL)
    return match.group(0).strip() if match else "(not found)"

def extract_next_chapter_outline(outline_text, chapter_num):
    """Extract the next chapter's outline (just first few lines for continuity)."""
    next_entry = extract_chapter_outline(outline_text, chapter_num + 1)
    if next_entry == "(not found)":
        return "(final chapter)"
    lines = next_entry.split('\n')[:10]
    return '\n'.join(lines)


UMBRAL_LONGITUD_MINIMA = 0.70


def extraer_word_count_objetivo(chapter_outline_text):
    """Objetivo de palabras de este capítulo, del campo '~Word count
    target' que gen_outline.py/gen_outline_part2.py escriben en cada
    entrada (ver esos scripts, build_prompt()). None si no se encuentra
    -- un esquema viejo o con formato distinto no debe romper la
    verificación de longitud, solo desactivarla (best-effort, como el
    resto de los parsers de este archivo)."""
    m = re.search(r'Word count target\**:?\**\s*~?\s*([\d.,]+)', chapter_outline_text, re.IGNORECASE)
    if not m:
        return None
    digitos = re.sub(r'[^\d]', '', m.group(1))
    return int(digitos) if digitos else None


def capitulo_demasiado_corto(word_count, objetivo, umbral=UMBRAL_LONGITUD_MINIMA):
    """True si word_count queda por debajo de `umbral` del objetivo. Un
    capítulo corto puede ser legítimo (una elección deliberada de ritmo);
    uno que es la mitad de su objetivo, no -- eso se lee como final
    abrupto y pasa la evaluación sin que nadie lo note. Sin objetivo
    (None o 0), nunca marca corto -- no hay nada contra qué comparar."""
    if not objetivo:
        return False
    return word_count < objetivo * umbral


# ---------------------------------------------------------------------------
# Parsing helpers -- pull novel-specific facts out of voice.md/characters.md
# instead of hardcoding them in the prompt. Everything here is best-effort:
# missing sections just yield empty strings/lists, they never raise.
# ---------------------------------------------------------------------------

def _seccion(md, patron_nombre, nivel="##"):
    """Contenido de un encabezado de nivel dado hasta el próximo del mismo
    nivel (o superior), sin incluir el encabezado."""
    marca = re.escape(nivel)
    m = re.search(rf'^{marca}\s*(?:{patron_nombre}).*$', md, re.IGNORECASE | re.MULTILINE)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(rf'^{marca}\s', md[start:], re.MULTILINE)
    end = start + nxt.start() if nxt else len(md)
    return md[start:end].strip()

def _primera_linea_util(texto):
    """Primera línea no vacía que no sea un comentario HTML <!-- -->."""
    sin_comentarios = re.sub(r'<!--.*?-->', '', texto, flags=re.DOTALL)
    for line in sin_comentarios.splitlines():
        line = line.strip().lstrip('-*').strip()
        if line:
            return line
    return ""

def extraer_pov(characters_text):
    """Nombre del personaje POV: encabezado '## Nombre (POV...)' en characters.md."""
    m = re.search(r'^##\s*([^(\n]+?)\s*\(POV', characters_text, re.IGNORECASE | re.MULTILINE)
    return m.group(1).strip() if m else ""

def extraer_persona_tiempo(voice_text):
    seccion = _seccion(voice_text, r'POV and Tense|POV y [Tt]iempo', nivel="###")
    return _primera_linea_util(seccion)

def extraer_registro_lexico(voice_text):
    seccion = _seccion(voice_text, r'Vocabulary Register|Registro l[ée]xico', nivel="###")
    return _primera_linea_util(seccion)

def extraer_reglas_capitulo(voice_text):
    """Reglas discrecionales de esta novela, si voice.md las define. Lista
    vacía si la sección no existe o está vacía -- no es un error."""
    seccion = _seccion(
        voice_text,
        r'Chapter-Specific Rules|Reglas espec[íi]ficas de cap[íi]tulo|Reglas por cap[íi]tulo',
        nivel="###",
    )
    if not seccion:
        return []
    sin_comentarios = re.sub(r'<!--.*?-->', '', seccion, flags=re.DOTALL)
    reglas = []
    for line in sin_comentarios.splitlines():
        line = line.strip().lstrip('-*').strip()
        if line:
            reglas.append(line)
    return reglas

def ultimos_finales(n=3):
    """Párrafo final de cada uno de los últimos n capítulos ya escritos, en
    orden. Lista vacía si no hay capítulos previos -- no debe romper."""
    if not CHAPTERS_DIR.exists():
        return []
    archivos = sorted(CHAPTERS_DIR.glob("ch_*.md"))
    finales = []
    for path in archivos[-n:]:
        texto = path.read_text().strip()
        if not texto:
            continue
        parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
        if parrafos:
            finales.append(parrafos[-1])
    return finales


def build_prompt(chapter_num, state, voice, world, characters, outline, canon):
    titulo = (state.get("titulo") or state.get("title") or "").strip()
    pov_nombre = extraer_pov(characters)
    persona_tiempo = extraer_persona_tiempo(voice)
    registro_lexico = extraer_registro_lexico(voice)
    reglas_especificas = extraer_reglas_capitulo(voice)
    prohibicion_final = ultimos_finales(n=3)

    chapter_outline = extract_chapter_outline(outline, chapter_num)
    next_chapter = extract_next_chapter_outline(outline, chapter_num)

    prev_path = CHAPTERS_DIR / f"ch_{chapter_num - 1:02d}.md"
    if prev_path.exists():
        prev_text = prev_path.read_text()
        prev_tail = prev_text[-2000:] if len(prev_text) > 2000 else prev_text
    else:
        prev_tail = "(first chapter -- no previous)"

    encabezado = f"Escribí el Capítulo {chapter_num}"
    encabezado += f' de "{titulo}"' if titulo else ""
    encabezado += ", en español."

    pov_linea = "Tercera persona limitada, pretérito"
    if persona_tiempo:
        pov_linea = persona_tiempo
    if pov_nombre:
        pov_linea += f", con narración cerrada al punto de vista de {pov_nombre}."
    else:
        pov_linea += " (ver personajes.md para el personaje POV)."

    vocab_linea = (
        f"Pozos léxicos: {registro_lexico}"
        if registro_lexico
        else "Pozos léxicos: ver voz.md Parte 2, Registro léxico."
    )

    palabras_objetivo = CALIBRACION["palabras_objetivo_capitulo"]

    instrucciones = [
        f"Escribí el capítulo COMPLETO. Objetivo: ~{palabras_objetivo} palabras. "
        "No trunques ni resumas.",
        pov_linea,
        "Cumplí TODOS los beats numerados del esquema, en orden.",
        'Sembrá TODOS los elementos de anticipación listados bajo "Plants" / "Siembras".',
        "Mostrá detalle sensorial: qué escucha, huele y siente físicamente el personaje POV.",
        "El diálogo sigue los patrones de habla definidos en personajes.md.",
        "Nada de palabras prohibidas de los guardarraíles de voz.md Parte 1.",
        'Nada de clichés de IA en español: nada de "no pudo evitar sentir", '
        'nada de "un escalofrío le recorrió la espalda", nada de "el peso '
        'de su/la ausencia" (ver deteccion_es.py, CLICHES_FICCION).',
        "Variá la longitud de las oraciones. Cortas para impacto. Más largas para construir tensión.",
        vocab_linea,
        "Confiá en el lector. No expliques qué significan las escenas. Dejá que aterricen solas.",
        "Empezá el capítulo en escena, no con exposición. Terminá en un momento, no en un resumen.",
    ]

    for regla in reglas_especificas:
        instrucciones.append(regla)

    patrones_a_evitar = [
        'NADA de listas sensoriales triádicas. Nunca "X. Y. Z." ni "X e Y y '
        'Z" como tres elementos separados seguidos. Combiná dos, cortá uno, '
        "o reestructurá.",
        'NO uses "No [verbo]" más de una vez por capítulo. Convertí los '
        "negativos en alternativas activas o cortalos directamente.",
        'NO uses construcciones tipo "Pensó en [X]." Reemplazalas por: el '
        "pensamiento mismo como fragmento, una acción física, o diálogo.",
        'NO uses "como [X] hacía [Y]" como conector de símil más de dos '
        "veces por capítulo. Usá otras estructuras o cortá la comparación.",
        "NO sobre-expliques después de mostrar. Si una escena demuestra "
        "algo, no dejes que el narrador lo repita. Confiá en la escena.",
        "NO uses cortes de sección (---) como muleta de ritmo. Solo para "
        "saltos genuinos de tiempo/lugar. Máximo 2 por capítulo.",
        "VARIÁ la longitud de los párrafos deliberadamente. Nunca más de 3 "
        "párrafos consecutivos de longitud similar. Incluí al menos un "
        "párrafo de 1-2 oraciones y uno de 6+ oraciones.",
        "INCLUÍ al menos un momento que sorprenda -- un personaje que dice "
        "algo equivocado, un beat emocional que llega antes o después de lo "
        "esperado, un detalle que no encaja con el patrón esperado. La "
        "excelencia predecible sigue siendo predecible.",
        "PRIORIZÁ escena sobre resumen. Al menos 70% del capítulo debe "
        "estar en escena (momento a momento, con diálogo y acción) y no en "
        "resumen (el narrador comprimiendo tiempo).",
        "El DIÁLOGO debe sonar a habla, no a prosa. Los personajes deben, "
        "de vez en cuando, trabarse, interrumpirse, dejar frases a medias o "
        "decir algo levemente equivocado. Que coincida con la edad y el "
        "trasfondo real de cada personaje (ver personajes.md) -- que no "
        "todos hablen en epigramas pulidos.",
    ]

    if prohibicion_final:
        finales_listados = "\n".join(f'  - "{p[:200]}"' for p in prohibicion_final)
        patrones_a_evitar.append(
            "TERMINÁ este capítulo de forma distinta a como terminaron los "
            "capítulos recientes. No repitas la forma de estos finales:\n"
            + finales_listados
        )

    instrucciones_texto = "\n".join(f"{i+1}. {t}" for i, t in enumerate(instrucciones))
    patrones_texto = "\n".join(
        f"{i+1}. {t}" for i, t in enumerate(patrones_a_evitar, start=len(instrucciones))
    )

    return f"""{encabezado}

DEFINICIÓN DE VOZ (seguila exactamente):
{voice}

ESQUEMA DE ESTE CAPÍTULO (cumplí cada beat):
{chapter_outline}

ESQUEMA DEL PRÓXIMO CAPÍTULO (para la continuidad -- terminá este capítulo de forma que fluya hacia el siguiente):
{next_chapter}

FINAL DEL CAPÍTULO ANTERIOR (continuá desde acá):
{prev_tail}

BIBLIA DE MUNDO (referencia para detalles de ambientación):
{world}

REGISTRO DE PERSONAJES (referencia para patrones de habla y comportamiento):
{characters}

INSTRUCCIONES DE ESCRITURA:
{instrucciones_texto}

PATRONES A EVITAR:
{patrones_texto}

Escribí el capítulo ahora. Texto completo, de principio a fin.
"""


def main():
    chapter_num = int(sys.argv[1])

    state = load_state()
    voice = load_file_bilingue("voz.md", "voice.md")
    world = load_file_bilingue("mundo.md", "world.md")
    characters = load_file_bilingue("personajes.md", "characters.md")
    outline = load_file_bilingue("esquema.md", "outline.md")
    canon = load_file(BASE_DIR / "canon.md")

    prompt = build_prompt(chapter_num, state, voice, world, characters, outline, canon)

    print(f"Drafting Chapter {chapter_num}...", file=sys.stderr)
    result = call_writer(prompt)

    # Save
    out_path = CHAPTERS_DIR / f"ch_{chapter_num:02d}.md"
    out_path.write_text(result)
    word_count = len(result.split())
    print(f"Saved to {out_path}", file=sys.stderr)
    print(f"Word count: {word_count}", file=sys.stderr)

    objetivo = extraer_word_count_objetivo(extract_chapter_outline(outline, chapter_num))
    if capitulo_demasiado_corto(word_count, objetivo):
        umbral_palabras = objetivo * UMBRAL_LONGITUD_MINIMA
        sys.exit(
            f"ERROR: {out_path} tiene {word_count} palabras -- por debajo "
            f"del {UMBRAL_LONGITUD_MINIMA:.0%} de su objetivo en el esquema "
            f"({objetivo} palabras, umbral {umbral_palabras:.0f}). El "
            f"archivo quedó guardado para inspección, pero el capítulo no "
            f"pasa: puede ser un corte silencioso o un capítulo "
            f"genuinamente débil -- revisalo a mano antes de seguir."
        )

    print(result)

if __name__ == "__main__":
    main()
