#!/usr/bin/env python3
"""
Pasada de edición adversarial: le pide al juez que CORTE 500 palabras de
cada capítulo. Lo que se corta revela lo más débil. La lista de cortes
ES el plan de revisión.

Uso: python adversarial_edit.py 1        # un solo capítulo
     python adversarial_edit.py all      # todos los capítulos
"""
import os
import sys
import json
import re
from pathlib import Path
from dotenv import load_dotenv

from api_comun import llamar_api

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

JUDGE_MODEL = os.environ.get("AUTONOVEL_JUDGE_MODEL", "claude-opus-4-6")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_BASE = os.environ.get("AUTONOVEL_API_BASE_URL", "https://api.anthropic.com")
CHAPTERS_DIR = BASE_DIR / "chapters"
EDIT_LOG_DIR = BASE_DIR / "edit_logs"
EDIT_LOG_DIR.mkdir(exist_ok=True)

def call_judge(prompt, max_tokens=20000):
    return llamar_api(
        prompt,
        model=JUDGE_MODEL,
        max_tokens=max_tokens,
        system=(
            "Sos un editor literario implacable. Cortás la grasa de la prosa. "
            "No tenés sentimentalismo con oraciones que están 'bastante bien' "
            "-- si una oración no se gana su lugar, se va. Citás exactamente "
            "del texto. Nunca inventás ni parafraseás. Respondés siempre con "
            "JSON válido."
        ),
        api_key=API_KEY,
        api_base=API_BASE,
    )

def parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```\w*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
    start = text.find('{')
    if start == -1:
        start = text.find('[')
    if start == -1:
        raise ValueError("No JSON found")
    # Try direct parse first
    try:
        return json.loads(text[start:], strict=False)
    except json.JSONDecodeError:
        # Find matching brace
        depth = 0
        in_string = False
        escape = False
        open_char = text[start]
        close_char = '}' if open_char == '{' else ']'
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
            if c == open_char:
                depth += 1
            elif c == close_char:
                depth -= 1
                if depth == 0:
                    return json.loads(text[start:i+1], strict=False)
        return json.loads(text[start:], strict=False)

EDIT_PROMPT = """Estás editando un capítulo de novela. Tu trabajo: identificar
exactamente qué cortar o reescribir para que este capítulo quede más
ajustado, más filoso, más vivo.

El texto está en español. Antes de juzgar, tené en cuenta:
- El diálogo se marca con raya (—), no con comillas. Es correcto.
- La subordinación larga y la coordinación con «y» son recursos legítimos
  del castellano, no verbosidad.
- El sujeto pronominal se omite por defecto. Su ausencia es correcta;
  su presencia repetida es un calco del inglés y sí es un defecto.
- El español corre entre 15% y 20% más largo que el inglés para el mismo
  contenido. No penalices por extensión comparándolo con prosa inglesa.

EL CAPÍTULO ({word_count} palabras):
{chapter_text}

TU TAREA:
1. Encontrá entre 10 y 20 pasajes específicos que deberían CORTARSE o
   REESCRIBIRSE. Para cada uno, citá el texto EXACTO (mínimo 10 palabras
   de la cita para que sea inequívoca), explicá por qué es débil, y
   clasificalo.

2. Clasificá cada corte como uno de:
   - FAT: no aporta nada, se podría sacar sin ninguna pérdida
   - REDUNDANT: repite lo que una oración/escena anterior ya mostró
   - OVER-EXPLAIN: el narrador explica lo que la escena ya demostró
   - GENERIC: podría aparecer en cualquier novela, no es específico de
     este mundo/personaje
   - TELL: nombra una emoción o estado en vez de mostrarlo
   - STRUCTURAL: párrafo/sección que interrumpe el ritmo o el pulso

3. Para candidatos a REWRITE (no cortes), dá una revisión específica.

4. Estimá cuántas palabras en total se podrían cortar sin perder nada
   que el capítulo necesite.

Respondé con JSON:
{{
  "cuts": [
    {{
      "quote": "texto exacto del capítulo (10+ palabras)",
      "type": "FAT|REDUNDANT|OVER-EXPLAIN|GENERIC|TELL|STRUCTURAL",
      "reason": "por qué debería irse",
      "action": "CUT o REWRITE",
      "rewrite": "texto de reemplazo si action es REWRITE, null si es CUT"
    }}
  ],
  "total_cuttable_words": N,
  "tightest_passage": "citá las mejores 2-3 oraciones del capítulo -- las que nunca tocarías",
  "loosest_passage": "citá las peores 2-3 oraciones -- las que más necesitan trabajo",
  "overall_fat_percentage": N,
  "one_sentence_verdict": "qué hace bien este capítulo y qué lo atrasa, en una oración"
}}
"""

def edit_chapter(ch_num):
    ch_path = CHAPTERS_DIR / f"ch_{ch_num:02d}.md"
    text = ch_path.read_text()
    word_count = len(text.split())
    
    prompt = EDIT_PROMPT.format(chapter_text=text, word_count=word_count)
    raw = call_judge(prompt)

    # Guardar el texto crudo antes de parsear -- si el parseo falla, el
    # texto queda disponible para diagnóstico sin repetir la llamada.
    raw_path = EDIT_LOG_DIR / f"raw_adversarial_ch{ch_num}.txt"
    raw_path.write_text(raw)

    result = parse_json(raw)
    
    # Save log
    log_path = EDIT_LOG_DIR / f"ch{ch_num:02d}_cuts.json"
    with open(log_path, "w") as f:
        json.dump(result, f, indent=2)
    
    return result, word_count

def main():
    if len(sys.argv) < 2:
        print("Usage: python adversarial_edit.py <chapter_num|all>")
        sys.exit(1)
    
    if sys.argv[1] == "all":
        chapters = list(range(1, 47))
    else:
        chapters = [int(sys.argv[1])]
    
    for ch in chapters:
        print(f"\n{'='*50}")
        print(f"EDITING CH {ch}")
        print(f"{'='*50}")
        
        try:
            result, wc = edit_chapter(ch)
        except Exception as e:
            print(f"  ERROR: {e}")
            continue
        
        cuts = result.get("cuts", [])
        cuttable = result.get("total_cuttable_words", 0)
        fat_pct = result.get("overall_fat_percentage", 0)
        verdict = result.get("one_sentence_verdict", "")
        
        # Count by type
        type_counts = {}
        for c in cuts:
            t = c.get("type", "?")
            type_counts[t] = type_counts.get(t, 0) + 1
        
        print(f"  Words: {wc}")
        print(f"  Cuts found: {len(cuts)}")
        print(f"  Cuttable words: ~{cuttable} ({fat_pct}% fat)")
        print(f"  By type: {type_counts}")
        print(f"  Verdict: {verdict}")
        print(f"  Tightest: {result.get('tightest_passage', '')[:100]}...")
        print(f"  Loosest:  {result.get('loosest_passage', '')[:100]}...")

if __name__ == "__main__":
    main()
