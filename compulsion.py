#!/usr/bin/env python3
"""
compulsion.py — Agente medidor de compulsión narrativa (page-turner).

Mide el "narrative drive" de cada capítulo: la fuerza que hace que el
lector no pueda parar. Complementa a evaluate.py (que mide calidad de
prosa y consistencia); este agente mide DESEO DE SEGUIR LEYENDO.

Uso:
    uv run python compulsion.py --chapter 1
    uv run python compulsion.py --full        (todos los capítulos + curva)

Reutiliza la infraestructura de evaluate.py (juez, rutas, logs).
"""

import argparse
import json
from datetime import datetime

from evaluate import call_judge, load_file, BASE_DIR, EVAL_LOG_DIR, CHAPTERS_DIR

COMPULSION_PROMPT = """Eres un editor de adquisiciones veterano y un lector
compulsivo de thrillers. Tu única especialidad: medir la COMPULSIÓN
NARRATIVA de un capítulo — la fuerza que impide soltar el libro. NO
evalúes calidad de prosa, gramática ni consistencia (otro juez hace
eso). Solo mide el deseo de seguir leyendo.

Lee el capítulo simulando una lectura real: página a página, notando
dónde tu atención sube, dónde se estanca y dónde (si pasa) querrías
dejar el libro en la mesa de noche.

CONTEXTO DE LA NOVELA (para calibrar ironía dramática — el lector
creyente conoce el marco profético y sabe cosas que los personajes no):
{contexto}

CAPÍTULO {num} A EVALUAR:
{chapter_text}

CAPÍTULO SIGUIENTE EN EL OUTLINE (para juzgar si el cierre empuja
hacia él):
{next_outline}

Evalúa estas dimensiones (0-10 cada una):

1. GANCHO DE APERTURA: ¿Las primeras 300 palabras plantean una
   pregunta, una tensión o una anomalía que obliga a seguir? ¿O abren
   con contexto/descripción que se puede saltar sin perder nada?

2. LIBRO MAYOR DE PREGUNTAS: lista las preguntas abiertas que el
   capítulo PLANTEA (nuevas) y las que RESPONDE (heredadas). Un
   capítulo compulsivo abre más de las que cierra, y las nuevas son
   más grandes que las respondidas. Puntúa el saldo.

3. MICRO-TENSIÓN: ¿Cada escena contiene fricción (deseo bloqueado,
   información incompleta, peligro latente, subtexto en el diálogo)?
   Identifica las escenas SIN fricción — los valles donde el lector
   puede soltar el libro.

4. IRONÍA DRAMÁTICA: ¿El capítulo explota lo que el lector sabe y el
   personaje no? En esta novela el lector creyente conoce la profecía:
   ¿el capítulo usa esa ventaja (el lector gritándole a la página) o
   la desperdicia?

5. FUERZA DEL CIERRE: ¿La última escena termina en un momento que
   empuja al capítulo siguiente (pregunta nueva, decisión pendiente,
   giro, amenaza en marcha)? ¿O cierra "resuelto", dando permiso de
   parar? Un final puede ser tranquilo Y compulsivo si deja una
   pregunta cargada.

6. PUNTO DE ABANDONO: la métrica reina. ¿En qué punto exacto del
   capítulo (cita textual de la frase) un lector cansado a las 11 pm
   diría "hasta aquí por hoy"? Si no existe tal punto, dilo — eso es
   un 10. Si existe, cita la frase y explica por qué ahí se afloja la
   tensión.

7. PROMESAS: ¿qué promete este capítulo que el lector va a cobrar
   después? (La compulsión de novela larga vive de promesas
   pendientes, no solo de tensión inmediata.)

Devuelve SOLO un JSON válido con esta estructura exacta:
{{
  "compulsion_score": <0-10, promedio ponderado; el punto de abandono
                       pesa doble>,
  "gancho_apertura": {{"score": <0-10>, "nota": "<por qué>"}},
  "preguntas_abiertas": ["<lista de preguntas nuevas que plantea>"],
  "preguntas_respondidas": ["<preguntas heredadas que cierra>"],
  "saldo_preguntas": {{"score": <0-10>, "nota": "<análisis del saldo>"}},
  "micro_tension": {{"score": <0-10>, "escenas_valle": ["<escenas sin fricción>"]}},
  "ironia_dramatica": {{"score": <0-10>, "nota": "<qué explota / qué desperdicia>"}},
  "fuerza_cierre": {{"score": <0-10>, "nota": "<empuja o da permiso de parar>"}},
  "punto_abandono": {{"score": <0-10>, "frase": "<cita textual o 'no existe'>",
                      "razon": "<por qué ahí>"}},
  "promesas_pendientes": ["<qué queda prometido para después>"],
  "tres_arreglos_de_mayor_impacto": ["<cambios concretos ordenados por
                                      impacto en compulsión>"]
}}"""


def load_context():
    """Contexto mínimo para calibrar ironía dramática."""
    teologia = load_file(BASE_DIR / "TEOLOGIA.md")
    mystery = load_file(BASE_DIR / "MYSTERY.md")
    return (teologia[:3000] + "\n\n" + mystery[:3000])


def get_next_outline(num):
    outline = load_file(BASE_DIR / "outline.md")
    marker = f"### Cap. {num + 1}"
    if marker in outline:
        start = outline.index(marker)
        end = outline.find("### Cap.", start + 10)
        return outline[start:end if end > 0 else start + 2000][:2000]
    return "(último capítulo / epílogo)"


def measure_chapter(num):
    path = CHAPTERS_DIR / f"ch_{num:02d}.md"
    text = load_file(path)
    if not text.strip():
        raise SystemExit(f"No existe {path}")
    prompt = COMPULSION_PROMPT.format(
        contexto=load_context(),
        num=num,
        chapter_text=text,
        next_outline=get_next_outline(num),
    )
    raw = call_judge(prompt, max_tokens=3000)
    # Extraer JSON de la respuesta
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1].lstrip("json").strip()
    start, end = raw.find("{"), raw.rfind("}")
    return json.loads(raw[start:end + 1])


def main():
    parser = argparse.ArgumentParser(description="Medidor de compulsión narrativa")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--chapter", type=int, help="Medir un capítulo")
    group.add_argument("--full", action="store_true",
                       help="Medir todos los capítulos existentes y dibujar la curva")
    args = parser.parse_args()

    if args.chapter is not None:
        result = measure_chapter(args.chapter)
        print("---")
        print(f"COMPULSIÓN: {result['compulsion_score']}/10")
        for k in ["gancho_apertura", "saldo_preguntas", "micro_tension",
                  "ironia_dramatica", "fuerza_cierre", "punto_abandono"]:
            v = result.get(k, {})
            print(f"{k}: {v.get('score','?')} — {v.get('nota', v.get('razon',''))}")
        pa = result.get("punto_abandono", {})
        if pa.get("frase") and pa.get("frase") != "no existe":
            print(f"\n>>> PUNTO DE ABANDONO: «{pa['frase']}»")
        print("\nPreguntas que abre:")
        for q in result.get("preguntas_abiertas", []):
            print(f"  + {q}")
        print("Promesas pendientes:")
        for p in result.get("promesas_pendientes", []):
            print(f"  → {p}")
        print("\nARREGLOS DE MAYOR IMPACTO:")
        for i, fix in enumerate(result.get("tres_arreglos_de_mayor_impacto", []), 1):
            print(f"  {i}. {fix}")
        mode = f"compulsion_ch{args.chapter:02d}"
        results = {f"ch{args.chapter:02d}": result}
    else:
        results = {}
        chapters = sorted(CHAPTERS_DIR.glob("ch_*.md"))
        for p in chapters:
            num = int(p.stem.split("_")[1])
            print(f"Midiendo capítulo {num}...")
            results[f"ch{num:02d}"] = measure_chapter(num)
        print("\n--- CURVA DE COMPULSIÓN ---")
        for key in sorted(results):
            score = results[key]["compulsion_score"]
            bar = "█" * int(round(score))
            print(f"{key}: {bar} {score}")
        mode = "compulsion_full"

    EVAL_LOG_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = EVAL_LOG_DIR / f"{timestamp}_{mode}.json"
    with open(log_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nlog: {log_path}")


if __name__ == "__main__":
    main()
