#!/usr/bin/env python3
"""
Revisión profunda del manuscrito vía Opus.

Envía la novela completa a Claude Opus para una revisión de dos
personas:
  1. Crítico literario (estilo reseña de diario)
  2. Profesor de escritura (sugerencias de oficio específicas y
     accionables)

Uso:
  python review.py                      # Revisión, guarda en edit_logs/
  python review.py --output reviews.md  # También guarda copia legible
  python review.py --parse              # Parsea la última revisión en ítems accionables
"""
import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from api_comun import llamar_api

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env", override=True)

# Use Opus for reviews — it's the best at literary analysis
REVIEW_MODEL = os.environ.get("AUTONOVEL_REVIEW_MODEL", "claude-opus-4-6")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_BASE = os.environ.get("AUTONOVEL_API_BASE_URL", "https://api.anthropic.com")

CHAPTERS_DIR = BASE_DIR / "chapters"
LOGS_DIR = BASE_DIR / "edit_logs"

# La calificación pide punto decimal ("4.2/5"), no coma, aunque no sea
# la convención habitual del español -- rompe la convención a propósito
# porque parse_review() necesita un separador decimal inequívoco: una
# coma sería ambigua contra la coma de miles o de enumeración en prosa
# libre, y el regex de calificación (más abajo) exige el punto.
REVIEW_PROMPT = """Leé la siguiente novela, "{title}". Revisala primero como
crítico literario (estilo reseña de diario) y después como profesor de
escritura. En la segunda revisión, dá sugerencias específicas y
accionables para cualquier defecto que encuentres. Sé justo pero
honesto. No *tenés* que encontrar defectos.

El texto está en español. Antes de juzgar, tené en cuenta:
- El diálogo se marca con raya (—), no con comillas. Es correcto.
- La subordinación larga y la coordinación con «y» son recursos legítimos
  del castellano, no verbosidad.
- El sujeto pronominal se omite por defecto. Su ausencia es correcta;
  su presencia repetida es un calco del inglés y sí es un defecto.
- El español corre entre 15% y 20% más largo que el inglés para el mismo
  contenido. No penalices por extensión comparándolo con prosa inglesa.

Estructurá tu respuesta así, exactamente:

## CRÍTICA LITERARIA
[tu reseña, estilo crítico de diario]

Calificación: X.X/5 estrellas

## ANÁLISIS DEL PROFESOR DE ESCRITURA
[tus sugerencias específicas y accionables]

1. **[Título del ítem]**
[descripción del problema]
Sugerencia: [sugerencia concreta]

2. **[Título del ítem]**
...

{manuscript}"""


def call_opus(prompt, max_tokens=32000):
    """Call Opus with the full manuscript."""
    print(f"Enviando a {REVIEW_MODEL} ({len(prompt):,} caracteres)...", file=sys.stderr)
    return llamar_api(
        prompt,
        model=REVIEW_MODEL,
        max_tokens=max_tokens,
        beta="context-1m-2025-08-07",
        api_key=API_KEY,
        api_base=API_BASE,
    )


def get_title():
    """Extract novel title from first chapter or outline."""
    outline = BASE_DIR / "outline.md"
    if outline.exists():
        first_line = outline.read_text().split("\n")[0]
        title = first_line.lstrip("# ").strip()
        if title:
            return title
    ch1 = CHAPTERS_DIR / "ch_01.md"
    if ch1.exists():
        first_line = ch1.read_text().split("\n")[0]
        return first_line.lstrip("# ").strip()
    return "Novela sin título"


def build_manuscript():
    """Concatenate all chapters into a single text."""
    chapters = sorted(CHAPTERS_DIR.glob("ch_*.md"))
    if not chapters:
        print("ERROR: no se encontraron capítulos.", file=sys.stderr)
        sys.exit(1)

    parts = []
    for ch in chapters:
        parts.append(ch.read_text())

    manuscript = "\n\n---\n\n".join(parts)
    wc = len(manuscript.split())
    print(f"Manuscrito: {len(chapters)} capítulos, {wc:,} palabras", file=sys.stderr)
    return manuscript


def parse_review(review_text):
    """Parse a review into structured actionable items."""
    items = []
    
    # Split into critic and professor sections -- header fijo, exigido
    # por el formato de REVIEW_PROMPT, sin depender de variantes.
    sections = re.split(r'##\s*ANÁLISIS DEL PROFESOR', review_text, maxsplit=1)

    critic_text = sections[0] if sections else review_text
    professor_text = sections[1] if len(sections) > 1 else ""

    # Extract rating -- formato fijo "Calificación: X.X/5" (ver comentario
    # sobre el punto decimal junto a REVIEW_PROMPT).
    rating_match = re.search(r'Calificación:\s*(\d+\.?\d*)\s*/\s*5', critic_text)
    stars = float(rating_match.group(1)) if rating_match else None

    # Extract professor's numbered items
    # Look for patterns like "1. **Título**" o "**1. Título**" o
    # "Sugerencia:" -- la clase de caracteres incluye vocales acentuadas
    # y Ñ porque muchos títulos en español arrancan así (p. ej.
    # "3. Álbum de personajes secundarios"). \*{0,2} antes y después del
    # número tolera las dos variantes reales de markdown que produce el
    # modelo -- pedimos "N. **Título**" mecánico y en la práctica Opus
    # también entrega "**N. Título**" (negrita envolviendo el número),
    # confirmado en la corrida real del 2026-08-08.
    prof_items = re.split(r'\n(?=\*{0,2}\d+\.\s+\*{0,2}[A-ZÁÉÍÓÚÑ])', professor_text)

    for section in prof_items:
        if not section.strip():
            continue

        # Extract the item title/number
        title_match = re.match(r'\*{0,2}(\d+)\.\s+(.+?)(?:\n|$)', section)
        if not title_match:
            continue

        num = int(title_match.group(1))
        title = title_match.group(2).strip().strip('*').strip()

        # Heurística aproximada -- en la corrida real del 2026-08-08
        # contra el manuscrito completo, ningún ítem cayó en
        # "major"/"minor" ni "qualified" pese a haber lenguaje de matiz
        # real en el texto (ver edit_logs/raw_review.txt). No es una
        # clasificación confiable, es una señal de apoyo -- leer el
        # texto completo de cada ítem antes de decidir, no filtrar por
        # esta etiqueta.
        # Classify severity based on language
        text_lower = section.lower()
        if any(w in text_lower for w in ['mayor', 'significativo', 'principal', 'más importante']):
            severity = "major"
        elif any(w in text_lower for w in ['menor', 'pequeño', 'leve', 'cosmético']):
            severity = "minor"
        else:
            severity = "moderate"

        # Classify type. Formas conjugadas ("cortá", vos imperativo)
        # agregadas junto al infinitivo -- confirmado en la corrida real
        # del 2026-08-08 que "Sugerencia:" viene casi siempre en
        # imperativo vos ("cortá", "dale"), no en infinitivo. 'dar' y
        # 'más' se sacaron de "addition": son substrings demasiado
        # comunes en prosa española (aparecen dentro de "guardar",
        # "recordar", "más importante", comparativos en general) y
        # producían falsos positivos sistemáticos en la corrida real.
        if any(w in text_lower for w in ['cortar', 'cortá', 'comprimir', 'comprimí', 'recortar', 'recortá', 'reducir', 'reducí', 'consolidar', 'consolidá']):
            fix_type = "compression"
        elif any(w in text_lower for w in ['agregar', 'agregá', 'expandir', 'expandí', 'introducir', 'introducí']):
            fix_type = "addition"
        elif any(w in text_lower for w in ['repetitiv', 'recurrente', 'frecuencia', 'tic', 'gesto']):
            fix_type = "mechanical"
        elif any(w in text_lower for w in ['reestructur', 'reorganiz', 'mueve', 'moví']):
            fix_type = "structural"
        else:
            fix_type = "revision"
        
        # Check if this is qualified/hedged (diminishing returns signal)
        qualified = any(phrase in text_lower for phrase in [
            'por separado, funciona', 'en gran medida logrado', 'cada instancia funciona',
            'menor en comparación con', 'objeción menor', 'el costo de la ambición',
            'no es un defecto', 'una elección deliberada', 'coherente temáticamente'
        ])

        # Extract specific suggestion. \*{0,2} antes y después de
        # "Sugerencia" tolera "**Sugerencia:**" (confirmado en la
        # corrida real) además del "Sugerencia:" liso que pide el
        # prompt.
        suggestion = ""
        sugg_match = re.search(r'\*{0,2}(?:[Ee]specífica\s+)?[Ss]ugerencia[s]?:?\*{0,2}\s*\n?(.*?)(?=\n\*{0,2}\d+\.|\n\n[A-ZÁÉÍÓÚÑ]|\Z)',
                               section, re.DOTALL)
        if sugg_match:
            suggestion = sugg_match.group(1).strip()[:500]
        
        items.append({
            "number": num,
            "title": title,
            "severity": severity,
            "type": fix_type,
            "qualified": qualified,
            "suggestion": suggestion,
            "full_text": section.strip()[:1000],
        })
    
    return {
        "stars": stars,
        "critic_summary": critic_text.strip()[:500],
        "professor_items": items,
        "total_items": len(items),
        "major_items": sum(1 for i in items if i["severity"] == "major"),
        "qualified_items": sum(1 for i in items if i["qualified"]),
        "raw_text": review_text,
    }


def should_stop(parsed_review):
    """Determine if the novel is done being revised.
    
    Stopping conditions:
    - Stars >= 4
    - No major unqualified items
    - More than half the items are qualified/hedged
    """
    stars = parsed_review.get("stars", 0) or 0
    total = parsed_review["total_items"]
    major = parsed_review["major_items"]
    qualified = parsed_review["qualified_items"]
    
    if stars >= 4.5 and major == 0:
        return True, "4.5/5 sin ítems mayores"
    if stars >= 4 and total > 0 and qualified / total > 0.5:
        return True, f"{stars}/5 con {qualified}/{total} ítems relativizados"
    if total <= 2:
        return True, f"Solo se encontraron {total} ítems"

    return False, f"{major} ítems mayores, {total - qualified} sin relativizar"


def cmd_review(args):
    """Generate a review."""
    title = get_title()
    manuscript = build_manuscript()
    
    prompt = REVIEW_PROMPT.format(title=title, manuscript=manuscript)
    
    review_text = call_opus(prompt)

    # Guardar el texto crudo antes de parsear -- si el parseo falla, el
    # texto queda disponible para diagnóstico sin repetir la llamada.
    LOGS_DIR.mkdir(exist_ok=True)
    (LOGS_DIR / "raw_review.txt").write_text(review_text)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOGS_DIR / f"{timestamp}_review.json"

    parsed = parse_review(review_text)
    parsed["timestamp"] = timestamp
    parsed["title"] = title
    parsed["word_count"] = len(manuscript.split())

    log_path.write_text(json.dumps(parsed, indent=2, default=str))
    print(f"\nReseña guardada en {log_path}", file=sys.stderr)

    # Save human-readable copy
    if args.output:
        Path(args.output).write_text(review_text)
        print(f"Copia legible: {args.output}", file=sys.stderr)

    # Print summary
    stop, reason = should_stop(parsed)
    print(f"\n{'='*50}")
    print(f"RESUMEN DE LA RESEÑA")
    print(f"  Calificación: {parsed['stars']}")
    print(f"  Ítems: {parsed['total_items']} ({parsed['major_items']} mayores)")
    print(f"  Relativizados: {parsed['qualified_items']}/{parsed['total_items']}")
    print(f"  ¿Frenar la revisión? {'SÍ — ' + reason if stop else 'NO — ' + reason}")
    print(f"{'='*50}")

    return parsed


def cmd_parse(args):
    """Parse the most recent review into actionable items."""
    LOGS_DIR.mkdir(exist_ok=True)
    reviews = sorted(LOGS_DIR.glob("*_review.json"), reverse=True)
    if not reviews:
        print("No se encontraron reseñas. Corré primero: review.py")
        sys.exit(1)

    latest = json.loads(reviews[0].read_text())

    print(f"Última reseña: {latest.get('timestamp', 'desconocida')}")
    print(f"Calificación: {latest.get('stars', '?')}")
    print(f"\nÍTEMS ACCIONABLES ({latest['total_items']}):")

    for item in latest.get("professor_items", []):
        qual = " [RELATIVIZADO]" if item["qualified"] else ""
        print(f"\n  {item['number']}. [{item['severity'].upper()}] [{item['type']}]{qual}")
        print(f"     {item['title']}")
        if item["suggestion"]:
            print(f"     Sugerencia: {item['suggestion'][:120]}...")

    stop, reason = should_stop(latest)
    print(f"\n{'='*50}")
    print(f"¿Frenar la revisión? {'SÍ — ' + reason if stop else 'NO — ' + reason}")
    print(f"{'='*50}")


def main():
    parser = argparse.ArgumentParser(description="Deep manuscript review via Opus")
    parser.add_argument("--output", "-o", default=None, help="Save human-readable review to file")
    parser.add_argument("--parse", action="store_true", help="Parse most recent review")
    
    args = parser.parse_args()
    
    if not API_KEY:
        print("ERROR: ANTHROPIC_API_KEY no está seteado en .env", file=sys.stderr)
        sys.exit(1)
    
    if args.parse:
        cmd_parse(args)
    else:
        cmd_review(args)


if __name__ == "__main__":
    main()
