#!/usr/bin/env python3
"""
Parse novel chapters into speaker-attributed audiobook scripts.

For each chapter, uses Claude to:
  - Identify every dialogue line and its speaker
  - Tag narration as NARRATOR
  - Add [audio tags] for emotional delivery based on context

Usage:
  python gen_audiobook_script.py           # All chapters
  python gen_audiobook_script.py 1         # Single chapter
  python gen_audiobook_script.py 1 5       # Range of chapters
"""
import os
import sys
import json
import re
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env", override=True)

WRITER_MODEL = os.environ.get("AUTONOVEL_WRITER_MODEL", "claude-sonnet-4-6")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_BASE = os.environ.get("AUTONOVEL_API_BASE_URL", "https://api.anthropic.com")

CHAPTERS_DIR = BASE_DIR / "chapters"
AUDIO_DIR = BASE_DIR / "audiobook"
SCRIPTS_DIR = AUDIO_DIR / "scripts"

# Personajes de la novela — RELLENAR en la fase de fundación
# (nombre -> descripción de voz para el actor/narrador)
CHARACTERS = {
    "NARRADOR": "La voz narrativa — medida, cálida, precisa. Español neutro latinoamericano.",
    # "EMPRESARIO": "50s, hondureño-americano. Voz grave, práctica, acento hondureño suave.",
    # "LIMPIADOR": "30s, afgano. Español con acento extranjero, frases cortas, cauteloso.",
    # "AGRICULTOR": "60, ucraniano. Voz áspera, pausada, español rudimentario con acento eslavo.",
    # "CIENTIFICA": "28, estadounidense. Precisa, rápida, tecnicismos naturales.",
    # "YOUTUBER": "25, española. Castellano peninsular, enérgica, registro coloquial.",
    # "CARDIOLOGO": "48, hondureño de San Pedro Sula. Culto, seguro de sí, voseo ocasional.",
    # "PILOTO": "32, israelí. Directa, militar, español funcional con acento.",
    # "ANTICRISTO": "Grimaldi, monegasco. Suave, magnético, dicción impecable.",
}

AUDIO_TAG_GUIDE = """
Available ElevenLabs v3 audio tags (use sparingly, only when the emotion is CLEAR):

Emotions: [happy] [sad] [angry] [excited] [nervous] [calm] [worried] [frustrated] [hopeful] [tense]
Delivery: [whisper] [softly] [firmly] [hesitantly] [sarcastically] [matter-of-factly] [gently]
Reactions: [gasp] [sigh] [laughs] [clears throat]
Volume: [quietly] [loudly]
Pacing: [slowly] [quickly] [pause]

Rules:
- Narration: use tags VERY sparingly. Mostly just read it straight. Use [softly] for tender moments, [slowly] for revelations, [tense] for suspense.
- Dialogue: use tags to match the speaker's emotional state in context. A worried father sounds different from an angry teenager.
- Don't over-tag. One tag per segment is usually enough. None is fine for neutral delivery.
- [pause] before revelations or after devastating lines.
- [whisper] for secrets, locked-room scenes, late-night moments.
"""


def call_claude(prompt, max_tokens=8000):
    import httpx
    resp = httpx.post(
        f"{API_BASE}/v1/messages",
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "anthropic-beta": "context-1m-2025-08-07",
            "content-type": "application/json",
        },
        json={
            "model": WRITER_MODEL,
            "max_tokens": max_tokens,
            "temperature": 0.1,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def parse_chapter(ch_num):
    """Parse a chapter into speaker-attributed segments."""
    ch_path = CHAPTERS_DIR / f"ch_{ch_num:02d}.md"
    if not ch_path.exists():
        print(f"  Chapter {ch_num} not found", file=sys.stderr)
        return None

    text = ch_path.read_text()
    title = text.split("\n")[0].lstrip("# ").strip()
    wc = len(text.split())

    prompt = f"""You are parsing a novel chapter into an audiobook script. Your job is to break the text into segments, each attributed to a speaker, with optional audio delivery tags.

CHARACTERS IN THIS NOVEL:
{json.dumps(CHARACTERS, indent=2)}

AUDIO TAG GUIDE:
{AUDIO_TAG_GUIDE}

REGLAS (la novela está EN ESPAÑOL y el diálogo usa RAYA —):
1. Todo fragmento de texto se atribuye a un hablante. Narración = "NARRADOR".
2. El diálogo en español abre con raya (—) al inicio de línea. Atribuye cada
   línea al personaje que habla usando el contexto y los incisos.
3. ELIMINA las rayas del texto a locutar — el actor de voz las interpreta.
4. Los incisos del narrador dentro del diálogo (—dijo el empresario—) son
   segmentos del NARRADOR, separados de la línea del personaje:
   "—Súbete —dijo—. Nos queda camino." se divide en:
   {{"speaker": "EMPRESARIO", "text": "Súbete."}},
   {{"speaker": "NARRADOR", "text": "dijo."}},
   {{"speaker": "EMPRESARIO", "text": "Nos queda camino."}}
   (Si el inciso es trivial como "dijo", puedes omitirlo.)
5. Segmentos de narración de tamaño razonable (2-4 oraciones). Divide párrafos largos.
6. Los separadores de escena (---) se convierten en {{"speaker": "NARRADOR", "text": "[pause]"}}
7. El título del capítulo es el primer segmento: {{"speaker": "NARRADOR", "text": "[slowly] Capítulo uno: ..."}}
8. Añade etiquetas de audio según el contexto emocional. Sé sutil — la mayoría de líneas no necesitan etiqueta.
9. Los pensamientos internos en *cursivas* los lee el PERSONAJE POV, con [softly] o [whisper].
10. Las citas entre comillas angulares « » (versículos, letreros) las lee el NARRADOR con [slowly].

OUTPUT FORMAT: A JSON array of objects, each with:
  "speaker": character name (from the list above)
  "text": the text to speak (with optional [audio tags] at the start)

CHAPTER {ch_num}: "{title}" ({wc} words)

{text}

Output the JSON array only. No other text."""

    print(f"  Ch {ch_num}: parsing '{title}' ({wc}w)...", end="", flush=True)
    result = call_claude(prompt)

    # Extract JSON from response
    result = result.strip()
    if result.startswith("```"):
        result = re.sub(r'^```\w*\n?', '', result)
        result = re.sub(r'\n?```$', '', result)

    try:
        segments = json.loads(result)
    except json.JSONDecodeError:
        # Try to fix common JSON issues from LLM output
        # 1. Remove trailing commas before ] or }
        cleaned = re.sub(r',\s*([}\]])', r'\1', result)
        # 2. Fix unescaped newlines in strings
        cleaned = cleaned.replace('\n', '\\n')
        # 3. Re-add structural newlines (between array elements)
        cleaned = cleaned.replace('\\n{', '\n{').replace('\\n]', '\n]')
        try:
            segments = json.loads(cleaned)
        except json.JSONDecodeError:
            # Last resort: extract individual objects
            print(f" (fixing JSON...)", end="", flush=True)
            segments = []
            for m in re.finditer(r'\{\s*"speaker"\s*:\s*"([^"]+)"\s*,\s*"text"\s*:\s*"((?:[^"\\]|\\.)*)"\s*\}', result):
                segments.append({
                    "speaker": m.group(1),
                    "text": m.group(2).replace('\\n', '\n').replace('\\"', '"'),
                })
            if not segments:
                print(f" PARSE ERROR", file=sys.stderr)
                (SCRIPTS_DIR / f"ch{ch_num:02d}_raw.txt").write_text(result)
                return None

    print(f" → {len(segments)} segments")
    return {
        "chapter": ch_num,
        "title": title,
        "segments": segments,
        "total_segments": len(segments),
        "speakers": list(set(s["speaker"] for s in segments)),
        "total_chars": sum(len(s["text"]) for s in segments),
    }


def main():
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    # Parse args for chapter range
    chapters = sorted(CHAPTERS_DIR.glob("ch_*.md"))
    total = len(chapters)

    if len(sys.argv) == 2:
        start = end = int(sys.argv[1])
    elif len(sys.argv) == 3:
        start, end = int(sys.argv[1]), int(sys.argv[2])
    else:
        start, end = 1, total

    print(f"Parsing chapters {start}-{end} into audiobook scripts...")

    all_scripts = []
    for ch_num in range(start, end + 1):
        script = parse_chapter(ch_num)
        if script:
            # Save individual chapter script
            out_path = SCRIPTS_DIR / f"ch{ch_num:02d}_script.json"
            out_path.write_text(json.dumps(script, indent=2))
            all_scripts.append(script)

    # Summary
    print(f"\n{'='*50}")
    print(f"AUDIOBOOK SCRIPT SUMMARY")
    print(f"  Chapters: {len(all_scripts)}")
    total_segs = sum(s["total_segments"] for s in all_scripts)
    total_chars = sum(s["total_chars"] for s in all_scripts)
    all_speakers = set()
    for s in all_scripts:
        all_speakers.update(s["speakers"])
    print(f"  Total segments: {total_segs}")
    print(f"  Total characters: {total_chars:,}")
    print(f"  Speakers found: {sorted(all_speakers)}")
    print(f"  Scripts saved to: {SCRIPTS_DIR}/")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
