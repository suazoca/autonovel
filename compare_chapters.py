#!/usr/bin/env python3
"""
Ranking comparativo: enfrenta capítulos de a pares.
El juez elige un ganador y cita los momentos decisivos.
Produce un orden real a partir de un torneo round-robin.

Uso: python compare_chapters.py          # torneo completo
     python compare_chapters.py 1 10     # un solo enfrentamiento
"""
import os
import sys
import json
import re
import random
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from api_comun import llamar_api

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

JUDGE_MODEL = os.environ.get("AUTONOVEL_JUDGE_MODEL", "claude-opus-4-6")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_BASE = os.environ.get("AUTONOVEL_API_BASE_URL", "https://api.anthropic.com")
CHAPTERS_DIR = BASE_DIR / "chapters"

def call_judge(prompt, max_tokens=4000):
    return llamar_api(
        prompt,
        model=JUDGE_MODEL,
        max_tokens=max_tokens,
        system=(
            "Sos un editor literario comparando dos capítulos de la misma "
            "novela. Elegís el mejor. No tenés permitido declarar un empate. "
            "Citás pasajes específicos para justificar tu elección. "
            "Respondés solo con JSON válido."
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
        raise ValueError("No JSON found")
    try:
        return json.loads(text[start:], strict=False)
    except json.JSONDecodeError:
        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(text)):
            c = text[i]
            if escape: escape = False; continue
            if c == '\\' and in_string: escape = True; continue
            if c == '"' and not escape: in_string = not in_string; continue
            if in_string: continue
            if c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return json.loads(text[start:i+1], strict=False)
        return json.loads(text[start:], strict=False)

COMPARE_PROMPT = """Comparás estos dos capítulos de la misma novela.
Los dos son primeros borradores. Elegí el MEJOR. Tenés que elegir un
ganador -- no hay empates.

El texto está en español. Antes de juzgar, tené en cuenta:
- El diálogo se marca con raya (—), no con comillas. Es correcto.
- La subordinación larga y la coordinación con «y» son recursos legítimos
  del castellano, no verbosidad.
- El sujeto pronominal se omite por defecto. Su ausencia es correcta;
  su presencia repetida es un calco del inglés y sí es un defecto.
- El español corre entre 15% y 20% más largo que el inglés para el mismo
  contenido. No penalices por extensión comparándolo con prosa inglesa.

CAPÍTULO A (Cap. {ch_a}):
{text_a}

CAPÍTULO B (Cap. {ch_b}):
{text_b}

Comparalos en estos ejes:
- ¿Cuál tiene prosa más filosa (más específica, menos genérica)?
- ¿Cuál tiene mejor diálogo (suena a habla, no a prosa escrita)?
- ¿Cuál genera más tensión o sorpresa genuina?
- ¿Cuál confía más en el lector (menos sobre-explicación)?
- ¿Cuál tiene menos patrones de escritura de IA?

Tenés que elegir uno. Si están parejos, elegí el que tiene el mejor
momento único -- la oración que te hubiera gustado escribir vos.

Respondé con JSON:
{{
  "winner": "A" or "B",
  "winner_chapter": N,
  "margin": "claro" o "ajustado" o "por un pelo",
  "decisive_moment": "citá el pasaje que lo definió -- del GANADOR",
  "winner_strength": "qué hace el ganador que el perdedor no",
  "loser_weakness": "qué específicamente atrasa al perdedor",
  "best_sentence_a": "citá la mejor oración de A",
  "best_sentence_b": "citá la mejor oración de B"
}}
"""

def compare(ch_a, ch_b):
    text_a = (CHAPTERS_DIR / f"ch_{ch_a:02d}.md").read_text()
    text_b = (CHAPTERS_DIR / f"ch_{ch_b:02d}.md").read_text()
    
    # Truncate to ~3000 words each to fit context
    words_a = text_a.split()
    words_b = text_b.split()
    if len(words_a) > 3000:
        text_a = ' '.join(words_a[:3000]) + "\n[truncated]"
    if len(words_b) > 3000:
        text_b = ' '.join(words_b[:3000]) + "\n[truncated]"
    
    prompt = COMPARE_PROMPT.format(
        ch_a=ch_a, ch_b=ch_b,
        text_a=text_a, text_b=text_b
    )
    raw = call_judge(prompt)

    # Guardar el texto crudo antes de parsear -- si el parseo falla, el
    # texto queda disponible para diagnóstico sin repetir la llamada.
    raw_path = BASE_DIR / "edit_logs" / f"raw_compare_{ch_a}_{ch_b}.txt"
    raw_path.write_text(raw)

    result = parse_json(raw)
    result["ch_a"] = ch_a
    result["ch_b"] = ch_b
    return result

def run_tournament(chapters):
    """Swiss-style tournament: pair by similar Elo, run enough rounds to rank."""
    # Initialize Elo ratings
    elo = {ch: 1500 for ch in chapters}
    K = 32
    matchups = []
    
    # Run 3-4 rounds of Swiss pairings
    n_rounds = 4
    for round_num in range(n_rounds):
        # Sort by Elo, pair adjacent
        ranked = sorted(chapters, key=lambda c: elo[c], reverse=True)
        pairs = []
        used = set()
        for i in range(0, len(ranked) - 1, 2):
            a, b = ranked[i], ranked[i+1]
            if (a, b) not in used and (b, a) not in used:
                pairs.append((a, b))
                used.add((a, b))
        
        print(f"\n--- Round {round_num + 1} ({len(pairs)} matchups) ---")
        for ch_a, ch_b in pairs:
            try:
                result = compare(ch_a, ch_b)
                winner = result.get("winner_chapter", result.get("winner"))
                margin = result.get("margin", "?")
                
                # Handle "A"/"B" vs chapter number
                if winner == "A":
                    winner = ch_a
                elif winner == "B":
                    winner = ch_b
                else:
                    winner = int(winner)
                
                loser = ch_b if winner == ch_a else ch_a
                
                # Update Elo
                exp_a = 1 / (1 + 10 ** ((elo[ch_b] - elo[ch_a]) / 400))
                score_a = 1.0 if winner == ch_a else 0.0
                elo[ch_a] += K * (score_a - exp_a)
                elo[ch_b] += K * ((1 - score_a) - (1 - exp_a))
                
                result["winner_resolved"] = winner
                matchups.append(result)
                
                print(f"  Ch {ch_a} vs Ch {ch_b}: winner=Ch {winner} ({margin})")
                
            except Exception as e:
                print(f"  Ch {ch_a} vs Ch {ch_b}: ERROR ({e})")
    
    # Final ranking
    ranking = sorted(chapters, key=lambda c: elo[c], reverse=True)
    
    return ranking, elo, matchups

def main():
    if len(sys.argv) == 3:
        # Single matchup
        ch_a, ch_b = int(sys.argv[1]), int(sys.argv[2])
        result = compare(ch_a, ch_b)
        print(json.dumps(result, indent=2))
    else:
        # Full tournament
        chapters = list(range(1, 47))
        ranking, elo, matchups = run_tournament(chapters)
        
        print(f"\n{'='*50}")
        print("FINAL RANKING")
        print(f"{'='*50}")
        for i, ch in enumerate(ranking):
            print(f"  {i+1:2d}. Ch {ch:2d}  (Elo: {elo[ch]:.0f})")
        
        # Save results
        results = {
            "ranking": ranking,
            "elo": {str(k): round(v) for k, v in elo.items()},
            "matchups": matchups,
            "timestamp": datetime.now().isoformat()
        }
        out_path = BASE_DIR / "edit_logs" / "tournament_results.json"
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved to {out_path}")

if __name__ == "__main__":
    main()
