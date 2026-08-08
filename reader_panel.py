#!/usr/bin/env python3
"""
4-reader panel for full-arc novel evaluation.
Each reader has a distinct persona and evaluates the NOVEL, not chapters.
The disagreements between readers are where editorial decisions live.

Usage: python reader_panel.py
"""
import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from api_comun import llamar_api

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

JUDGE_MODEL = os.environ.get("AUTONOVEL_JUDGE_MODEL", "claude-opus-4-6")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_BASE = os.environ.get("AUTONOVEL_API_BASE_URL", "https://api.anthropic.com")

READERS = {
    "editor": {
        "name": "The Editor",
        "system": (
            "Sos un editor de ficción senior en una editorial importante. "
            "Editaste más de 200 novelas. Te importa la textura de la prosa, "
            "el subtexto, el oficio a nivel de oración, y si la voz es "
            "consistente y está ganada. Notás cuando el narrador "
            "sobre-explica, cuando el diálogo suena escrito en vez de "
            "hablado, cuando una metáfora es prestada en vez de ganada. No "
            "sos cruel pero sos preciso. Viste suficiente prosa competente "
            "para saber la diferencia entre buena y viva. Respondés solo "
            "con JSON válido."
        ),
    },
    "genre_reader": {
        "name": "The Genre Reader",
        "system": (
            "Sos un lector voraz de thriller literario, leés más de 50 "
            "novelas por año. Te importa el ritmo, el misterio, si la "
            "investigación paga lo que promete, y si querés seguir dando "
            "vuelta las páginas. Te aburre la prosa hermosa que no VA a "
            "ningún lado. Notás cuando una investigación se estanca, "
            "cuando la tensión se aplana, cuando el autor está más "
            "enamorado de su mundo que de su historia. Comparás todo con "
            "Umberto Eco, Arturo Pérez-Reverte, John le Carré. Sos "
            "generoso con lo que te gusta y directo sobre lo que te "
            "aburre. Respondés solo con JSON válido."
        ),
    },
    "writer": {
        "name": "The Writer",
        "system": (
            "Sos un autor publicado de suspenso literario, con 5 novelas y "
            "una nominación al Premio Edgar. Leés como quien conoce el "
            "oficio. Notás la estructura: dónde caen los beats, si el "
            "foreshadowing paga, si los arcos de personaje se completan. "
            "Notás cuándo se nota la técnica y cuándo desaparece dentro de "
            "la historia. El mayor elogio que das es 'me olvidé de que "
            "estaba leyendo'. Lo peor que podés decir es 'se nota el "
            "esquema'. Te importa la brecha entre lo que una novela "
            "intenta y lo que logra. Respondés solo con JSON válido."
        ),
    },
    "first_reader": {
        "name": "The First Reader",
        "system": (
            "Sos un lector general, reflexivo. No sos escritor, ni editor, "
            "ni experto en el género. Leés por la experiencia. Sabés lo "
            "que sentís pero no siempre por qué. Notás cuándo te "
            "conmovés, cuándo te aburrís, cuándo te confundís, cuándo "
            "querés contarle a alguien lo que acabás de leer. No usás "
            "terminología de oficio. Decís cosas como 'esta parte no me "
            "importó' y 'tuve que dejar el libro después de esta escena "
            "porque necesitaba un minuto'. Tu feedback es emocional y "
            "honesto, no analítico. Respondés solo con JSON válido."
        ),
    },
}

# JSON schema keys ("momentum_loss", "worst_scene", etc.) quedan en
# inglés a propósito -- gen_brief.py::panel_mentions_for_chapter() las
# lee tal cual (mentions: dict con esas mismas claves). Traducir las
# claves acá rompería esa lectura sin avisar. Solo se traduce el texto
# en español de cada pregunta (los VALORES del schema).
READER_PROMPT = """Acabás de leer una novela completa en forma de resumen.
Los resúmenes incluyen los eventos capítulo por capítulo, los pasajes de
apertura y cierre de cada capítulo, y diálogo clave. La novela completa
tiene {palabras_totales} palabras en {capitulos_totales} capítulos.

El texto está en español. Antes de juzgar, tené en cuenta:
- El diálogo se marca con raya (—), no con comillas. Es correcto.
- La subordinación larga y la coordinación con «y» son recursos legítimos
  del castellano, no verbosidad.
- El sujeto pronominal se omite por defecto. Su ausencia es correcta;
  su presencia repetida es un calco del inglés y sí es un defecto.
- El español corre entre 15% y 20% más largo que el inglés para el mismo
  contenido. No penalices por extensión comparándolo con prosa inglesa.

{arc_summary}

Ahora respondé estas preguntas sobre la NOVELA COMO UN TODO. Sé
específico. Citá pasajes cuando puedas. Nombrá números de capítulo.
Citá siempre los capítulos como "Cap. N" (ej. "Cap. 12").

Respondé con JSON:
{{
  "momentum_loss": "¿Dónde pierde impulso la historia? Nombrá el/los capítulo(s) específico(s) y qué causa el estancamiento. Si nunca pierde impulso, decilo y explicá por qué.",

  "earned_ending": "¿El final se siente ganado por todo lo que vino antes? ¿La elección de Vidal en el Cap. 42 -- negarse a la oferta de Sandoz y pedir dos cosas puntuales en su lugar -- cierra? ¿La imagen final del Cap. 46 (la segunda lasca, la camisa gris, las baldosas contadas, la taza boca abajo, la columna sin nombre) resuena con la apertura del Cap. 1 de un modo que satisface? ¿Qué, si acaso algo, se siente no ganado?",

  "cut_candidate": "Si la novela tuviera que ser 10% más corta (~8.500 palabras), ¿qué capítulo o sección cortarías primero? ¿Por qué? ¿Qué se perdería?",

  "missing_scene": "¿Hay una escena que la novela NECESITA y no tiene? ¿Una conversación que debería pasar, un momento que está ganado pero nunca se entrega, un personaje que merece más páginas? Sé específico sobre dónde iría.",

  "thinnest_character": "¿Qué personaje se siente más débil hacia el final? ¿De quién querés saber más? ¿A quién se podría cortar sin que la novela sufra?",

  "best_scene": "¿Cuál es la mejor escena de la novela? Citá el momento que te hizo sentir algo. ¿Por qué funciona?",

  "worst_scene": "¿Cuál es la escena más débil? ¿Qué sale mal? ¿Cómo la arreglarías?",

  "would_recommend": "¿Recomendarías esta novela? ¿A quién? ¿Qué dirías sobre ella en una oración?",

  "haunts_you": "¿Hay una línea o un momento que se te queda después de leer? Citalo.",

  "next_book": "¿Leerías el próximo libro del autor? ¿Por qué sí o por qué no?"
}}
"""
# TODO(pendiente de decisión editorial, no traducir mecánicamente):
# "earned_ending" sigue en inglés y con "Cass"/"Ch 22"/"Ch 24" de la
# novela de referencia -- ver mensaje aparte, es una pregunta sobre la
# ESTRUCTURA de esta novela (clímax real, imagen que cierra el libro),
# no una traducción de nombres.

def extraer_totales(arc_summary):
    """Palabras y capítulos totales, parseados del propio arc_summary
    recibido (que build_arc_summary.py ya calculó dinámicamente) -- no
    hardcodeados acá. "?" si no se encuentran -- no debe romper."""
    m_palabras = re.search(r'Total de\s+la novela:\s*([\d.]+)\s*palabras', arc_summary)
    m_capitulos = re.search(r'de los (\d+) capítulos', arc_summary)
    palabras = m_palabras.group(1) if m_palabras else "?"
    capitulos = m_capitulos.group(1) if m_capitulos else "?"
    return palabras, capitulos

def call_reader(reader_key, arc_summary, max_tokens=20000):
    reader = READERS[reader_key]
    palabras_totales, capitulos_totales = extraer_totales(arc_summary)
    raw = llamar_api(
        READER_PROMPT.format(
            arc_summary=arc_summary,
            palabras_totales=palabras_totales,
            capitulos_totales=capitulos_totales,
        ),
        model=JUDGE_MODEL,
        max_tokens=max_tokens,
        system=reader["system"],
        api_key=API_KEY,
        api_base=API_BASE,
    )

    # Guardar el texto crudo antes de parsear -- si el parseo falla, el
    # texto queda disponible para diagnóstico sin tener que repetir la
    # llamada a la API.
    raw_path = BASE_DIR / "edit_logs" / f"raw_{reader_key}.txt"
    raw_path.write_text(raw)

    # Parse JSON
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r'^```\w*\n?', '', raw)
        raw = re.sub(r'\n?```$', '', raw)
    start = raw.find('{')
    if start >= 0:
        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(raw)):
            c = raw[i]
            if escape: escape = False; continue
            if c == '\\' and in_string: escape = True; continue
            if c == '"' and not escape: in_string = not in_string; continue
            if in_string: continue
            if c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return json.loads(raw[start:i+1], strict=False)
    return json.loads(raw, strict=False)

def find_disagreements(results):
    """Find where readers disagree -- that's where the editorial decisions live.

    Limitaciones conocidas de la extracción de capítulos, no cubiertas:
    - Lista con comas bajo un solo prefijo (ej. "Caps. 12, 24 y 35") -- solo
      captura el primer número, 24 y 35 quedan invisibles.
    - Rango con "a" y un solo prefijo (ej. "Caps. 22 a 34") -- solo captura
      22, pierde 23-33 (distinto del rango que sí se cubre, que exige "Cap."
      repetido en ambos extremos: "del Cap. 15 al Cap. 19").
    """
    disagreements = []
    
    for question in ["momentum_loss", "cut_candidate", "thinnest_character", "worst_scene"]:
        answers = {k: v.get(question, "") for k, v in results.items()}
        # Extract chapter numbers mentioned (números sueltos, plural "Caps.",
        # y rangos -- con guion "Cap. N-M" o en prosa "del Cap. N al Cap. M")
        chapters_mentioned = {}
        for reader, answer in answers.items():
            chs = set()
            rangos = list(re.finditer(r'Caps?\.?\s*(\d+)\s*[-–—]\s*(\d+)', answer, re.IGNORECASE))
            rangos += list(re.finditer(r'Caps?\.?\s*(\d+)\s+(?:al|a)\s+Caps?\.?\s*(\d+)', answer, re.IGNORECASE))
            for m in rangos:
                inicio, fin = int(m.group(1)), int(m.group(2))
                if inicio > fin:
                    inicio, fin = fin, inicio
                chs.update(range(inicio, fin + 1))
            for m in re.finditer(r'Caps?\.?\s*(\d+)', answer, re.IGNORECASE):
                if any(r.start() <= m.start() < r.end() for r in rangos):
                    continue
                chs.add(int(m.group(1)))
            chapters_mentioned[reader] = chs
        
        # Find chapters where only some readers flagged an issue
        all_chs = set()
        for chs in chapters_mentioned.values():
            all_chs.update(chs)
        
        for ch in all_chs:
            flagged_by = [r for r, chs in chapters_mentioned.items() if ch in chs]
            not_flagged = [r for r, chs in chapters_mentioned.items() if ch not in chs]
            if flagged_by and not_flagged:
                disagreements.append({
                    "question": question,
                    "chapter": int(ch),
                    "flagged_by": flagged_by,
                    "not_flagged": not_flagged,
                    "details": {r: answers[r][:200] for r in flagged_by}
                })
    
    return disagreements

def main():
    arc_summary = (BASE_DIR / "arc_summary.md").read_text()
    
    results = {}
    for reader_key, reader_info in READERS.items():
        print(f"\n{'='*50}")
        print(f"READING: {reader_info['name']}")
        print(f"{'='*50}")
        
        try:
            result = call_reader(reader_key, arc_summary)
            results[reader_key] = result
            
            # Print highlights
            print(f"  Momentum loss: {result.get('momentum_loss', '')[:150]}...")
            print(f"  Best scene: {result.get('best_scene', '')[:150]}...")
            print(f"  Would recommend: {result.get('would_recommend', '')[:150]}...")
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Find disagreements
    disagreements = find_disagreements(results)
    
    # Print consensus and disagreement
    print(f"\n{'='*60}")
    print("READER PANEL RESULTS")
    print(f"{'='*60}")
    
    for question in ["momentum_loss", "earned_ending", "cut_candidate", "missing_scene", 
                      "thinnest_character", "best_scene", "worst_scene", "would_recommend",
                      "haunts_you", "next_book"]:
        print(f"\n--- {question.upper()} ---")
        for reader_key in READERS:
            if reader_key in results:
                answer = results[reader_key].get(question, "N/A")
                print(f"  [{READERS[reader_key]['name']}]: {answer[:300]}")
    
    if disagreements:
        print(f"\n{'='*60}")
        print("DISAGREEMENTS (editorial decisions needed)")
        print(f"{'='*60}")
        for d in disagreements:
            print(f"\n  {d['question']} -- Ch {d['chapter']}")
            print(f"    Flagged by: {', '.join(d['flagged_by'])}")
            print(f"    Not flagged: {', '.join(d['not_flagged'])}")
    
    # Save full results
    output = {
        "readers": results,
        "disagreements": disagreements,
        "timestamp": datetime.now().isoformat()
    }
    out_path = BASE_DIR / "edit_logs" / "reader_panel.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to {out_path}")

if __name__ == "__main__":
    main()
