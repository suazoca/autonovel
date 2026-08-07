#!/usr/bin/env python3
"""
Generador de capítulos revisados. Reescribe un capítulo a partir de un
brief de revisión específico.
Uso: python gen_revision.py <numero_capitulo> <archivo_brief>
"""
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv

from deteccion_es import calcos_detectados, CLICHES_FICCION
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
            "Sos un escritor de ficción literaria reescribiendo un capítulo "
            "de novela, en español, a partir de un brief de revisión "
            "específico. Seguís el brief al pie de la letra. Preservás la "
            "voz, el mundo y los personajes del borrador existente mientras "
            "hacés los cambios estructurales que pide el brief. Nunca usás "
            "palabras de la lista prohibida. Mostrás, nunca explicás las "
            "emociones. Escribís el capítulo COMPLETO -- no truncás, no "
            "resumís, no saltás adelante."
        ),
        beta="context-1m-2025-08-07",
        api_key=API_KEY,
        api_base=API_BASE,
    )

def obtener_titulo():
    """Título de la novela: primera línea de outline.md, o de ch_01.md si
    no existe -- mismo patrón que review.py::get_title(), para que este
    script no dependa de un título hardcodeado y sirva tal cual para un
    Libro 2 sin volver a tocarlo."""
    outline_path = BASE_DIR / "outline.md"
    if outline_path.exists():
        primera_linea = outline_path.read_text().split("\n")[0]
        titulo = primera_linea.lstrip("# ").strip()
        if titulo:
            return titulo
    ch1 = BASE_DIR / "chapters" / "ch_01.md"
    if ch1.exists():
        primera_linea = ch1.read_text().split("\n")[0]
        return primera_linea.lstrip("# ").strip()
    return ""

def main():
    ch_num = int(sys.argv[1])
    brief_file = sys.argv[2]

    titulo = obtener_titulo()
    voice = (BASE_DIR / "voice.md").read_text()
    characters = (BASE_DIR / "characters.md").read_text()
    world = (BASE_DIR / "world.md").read_text()
    brief = Path(brief_file).read_text()

    # Capítulos vecinos, para continuidad
    prev_path = BASE_DIR / "chapters" / f"ch_{ch_num - 1:02d}.md"
    next_path = BASE_DIR / "chapters" / f"ch_{ch_num + 1:02d}.md"
    prev_tail = prev_path.read_text()[-2000:] if prev_path.exists() else "(primer capítulo)"
    next_head = next_path.read_text()[:1500] if next_path.exists() else "(último capítulo)"

    # Borrador existente, si lo hay
    old_path = BASE_DIR / "chapters" / f"ch_{ch_num:02d}.md"
    old_text = old_path.read_text() if old_path.exists() else "(no hay borrador existente)"

    encabezado = f"Reescribí el Capítulo {ch_num}"
    encabezado += f' de "{titulo}"' if titulo else ""
    encabezado += ", en español."

    prompt = f"""{encabezado}

BRIEF DE REVISIÓN (seguilo exactamente):
{brief}

DEFINICIÓN DE VOZ (seguila exactamente):
{voice}

REGISTRO DE PERSONAJES (referencia para patrones de habla y comportamiento):
{characters}

BIBLIA DE MUNDO (referencia para detalles de ambientación):
{world}

FINAL DEL CAPÍTULO ANTERIOR (mantené la continuidad):
{prev_tail}

APERTURA DEL PRÓXIMO CAPÍTULO (terminá de forma que fluya hacia ahí):
{next_head}

EL BORRADOR EXISTENTE (usalo como materia prima -- guardá lo que funciona, cortá lo que no):
{old_text}

PATRONES A EVITAR:
1. NADA de listas sensoriales triádicas. Nunca "X. Y. Z." ni "X e Y y Z" como tres elementos separados seguidos. Combiná dos, cortá uno, o reestructurá.
2. NO uses "No [verbo]" más de una vez por capítulo. Convertí los negativos en alternativas activas o cortalos directamente.
3. NO uses construcciones tipo "Pensó en [X]." Reemplazalas por: el pensamiento mismo como fragmento, una acción física, o diálogo.
4. NO uses "como [X] hacía [Y]" como conector de símil más de dos veces por capítulo. Usá otras estructuras o cortá la comparación.
5. NO uses la fórmula "no X, sino Y" en la narración -- ni su inversa "X, no Y." Es un tic reconocible; si la comparación importa, mostrala en la acción, no en la sintaxis.
6. NO sobre-expliques después de mostrar. Si una escena demuestra algo, no dejes que el narrador lo repita. Confiá en la escena.
7. NO uses cortes de sección (---) como muleta de ritmo. Solo para saltos genuinos de tiempo/lugar. Máximo 2 por capítulo.
8. INCLUÍ al menos un momento que sorprenda -- un personaje que dice algo equivocado, un beat emocional que llega antes o después de lo esperado, un detalle que no encaja con el patrón esperado. La excelencia predecible sigue siendo predecible.
9. PRIORIZÁ escena sobre resumen. Al menos 70% del capítulo debe estar en escena (momento a momento, con diálogo y acción) y no en resumen (el narrador comprimiendo tiempo).
10. El DIÁLOGO debe sonar a habla, no a prosa. Los personajes deben, de vez en cuando, trabarse, interrumpirse, dejar frases a medias o decir algo levemente equivocado. Que coincida con la edad y el trasfondo real de cada personaje (ver personajes.md) -- que no todos hablen en epigramas pulidos.

Escribí el capítulo revisado ahora. Texto completo, de principio a fin."""

    print(f"Reescribiendo el Capítulo {ch_num}...", file=sys.stderr)
    result = call_writer(prompt)

    out_path = BASE_DIR / "chapters" / f"ch_{ch_num:02d}.md"
    out_path.write_text(result)
    print(f"Guardado en {out_path}", file=sys.stderr)
    print(f"Cantidad de palabras: {len(result.split())}", file=sys.stderr)

    # Verificación de calcos/clichés antes de aceptar la reescritura --
    # no bloquea (la aprobación sigue siendo manual, como el resto del
    # pipeline), pero deja el hallazgo a la vista antes de que alguien
    # revise el archivo.
    hallazgos = calcos_detectados(result)
    cliches = [p[:60] for p in CLICHES_FICCION if re.search(p, result, re.IGNORECASE)]
    if hallazgos or cliches:
        print(
            "\nADVERTENCIA -- deteccion_es.py encontró posibles calcos/clichés "
            "(no bloquea, revisar antes de aceptar la reescritura):",
            file=sys.stderr,
        )
        for descripcion, n in hallazgos:
            print(f"  - calco: {descripcion} ({n}x)", file=sys.stderr)
        for patron in cliches:
            print(f"  - cliché: {patron}", file=sys.stderr)
    else:
        print("deteccion_es.py: sin calcos ni clichés detectados.", file=sys.stderr)

if __name__ == "__main__":
    main()
