#!/usr/bin/env python3
"""
Draft a single chapter using the writer model.
Usage: python draft_chapter.py 1
"""
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

WRITER_MODEL = os.environ.get("AUTONOVEL_WRITER_MODEL", "claude-sonnet-4-6")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_BASE = os.environ.get("AUTONOVEL_API_BASE_URL", "https://api.anthropic.com")
CHAPTERS_DIR = BASE_DIR / "chapters"

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
        "temperature": 0.8,
        "system": (
            "Eres un escritor literario redactando un capítulo de novela EN ESPAÑOL. "
            "Escribes en tercera persona limitada, tiempo pasado, anclado a UN solo "
            "personaje punto de vista por capítulo. Sigues la definición de voz al pie "
            "de la letra. Cubres todos los beats del outline. Nunca usas palabras de la "
            "lista prohibida. Muestras las emociones, nunca las nombras. Tu prosa es "
            "específica, sensorial, concreta. Las metáforas nacen de la experiencia del "
            "personaje. Varías la longitud de las oraciones. Confías en el lector. "
            "El diálogo usa raya (—) según la convención literaria del español, nunca "
            "comillas inglesas. Escribes el capítulo COMPLETO: no truncas, no resumes, "
            "no saltas escenas."
        ),
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = httpx.post(f"{API_BASE}/v1/messages", headers=headers, json=payload, timeout=600)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]

def load_file(path):
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return ""

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

def main():
    chapter_num = int(sys.argv[1])
    
    # Load all context
    voice = load_file(BASE_DIR / "voice.md")
    world = load_file(BASE_DIR / "world.md")
    characters = load_file(BASE_DIR / "characters.md")
    outline = load_file(BASE_DIR / "outline.md")
    canon = load_file(BASE_DIR / "canon.md")
    teologia = load_file(BASE_DIR / "TEOLOGIA.md")
    craft = load_file(BASE_DIR / "CRAFT-ES.md")
    resumen_caps = load_file(BASE_DIR / "resumen_capitulos.md") or (
        "(Aún no hay capítulos registrados por el cronista.)")
    _brief_path = BASE_DIR / "briefs" / f"realidad_ch{chapter_num:02d}.md"
    informe_realidad = load_file(_brief_path) if _brief_path.exists() else (
        "(No se generó informe de realidad para este capítulo. Correr "
        "'python realidad.py --brief N' antes de redactar es el flujo "
        "recomendado. En su ausencia: máxima cautela con física, "
        "demografía del rapto, geografía y escalada temporal.)")
    
    # Chapter-specific context
    chapter_outline = extract_chapter_outline(outline, chapter_num)
    next_chapter = extract_next_chapter_outline(outline, chapter_num)
    
    # Previous chapter (if exists)
    prev_path = CHAPTERS_DIR / f"ch_{chapter_num - 1:02d}.md"
    if prev_path.exists():
        prev_text = prev_path.read_text()
        prev_tail = prev_text[-2000:] if len(prev_text) > 2000 else prev_text
    else:
        prev_tail = "(first chapter -- no previous)"
    
    prompt = f"""Escribe el Capítulo {chapter_num} de la novela.

DEFINICIÓN DE VOZ (síguela exactamente):
{voice}

OUTLINE DE ESTE CAPÍTULO (cubre todos los beats):
{chapter_outline}

OUTLINE DEL CAPÍTULO SIGUIENTE (para continuidad — cierra este capítulo de modo que fluya hacia el próximo):
{next_chapter}

FINAL DEL CAPÍTULO ANTERIOR (continúa desde aquí):
{prev_tail}

BIBLIA DEL MUNDO (referencia para detalles de worldbuilding):
{world}

REGISTRO DE PERSONAJES (referencia para patrones de habla y conducta):
{characters}

CANON DOCTRINAL (TEOLOGIA.md — NADA en el capítulo puede contradecirlo;
citas bíblicas SIEMPRE textuales RVR1960 con referencia):
{teologia}

LO YA ESTABLECIDO EN CAPÍTULOS ANTERIORES (continuidad OBLIGATORIA —
los nombres, hechos, objetos y estados registrados aquí NO pueden
contradecirse; si un personaje secundario ya tiene nombre, usa ESE
nombre):
{resumen_caps}

INFORME DE REALIDAD (contexto OBLIGATORIO del estado del mundo en la
fecha de este capítulo — obedece sus restricciones duras):
{informe_realidad}

REGLAS DE OFICIO NARRATIVO (CRAFT-ES.md — gobiernan cada escena;
el evaluador clasificará tus escenas contra ellas):
{craft}

INSTRUCCIONES DE ESCRITURA:
1. Escribe el capítulo COMPLETO. Objetivo: ~3,200 palabras. No truncar ni resumir.
2. Tercera persona limitada, tiempo pasado, anclado al personaje POV que indica el outline.
3. Cubre TODOS los beats numerados del outline, en orden.
4. Planta TODOS los elementos de presagio listados bajo "Siembras".
5. Detalle sensorial: qué oye, huele y siente físicamente el personaje POV.
6. El diálogo sigue los patrones de habla definidos en characters.md,
   incluida la variedad dialectal de cada personaje (hondureño, peninsular, etc.).
7. Nada de palabras prohibidas de voice.md Parte 1.
8. Nada de clichés de IA: ni "una sensación de", ni "no pudo evitar sentir",
   ni "sus ojos se abrieron como platos", ni "una ola de X lo invadió".
9. Varía la longitud de las oraciones. Cortas para el impacto. Largas para construir.
10. Metáforas desde la experiencia del personaje POV, no genéricas.
11. Confía en el lector. No expliques qué significan las escenas. Deja que aterricen.
12. Empieza el capítulo EN escena, no con exposición. Termina en un momento, no en un resumen.

REGLAS DEL ESPAÑOL (obligatorias):
13. DIÁLOGO con raya (—): —Súbete —dijo—. Nos queda camino.
    Nunca comillas inglesas para diálogo. Comillas angulares « » solo para
    citas dentro de narración (p. ej., la cita de un letrero o un versículo).
14. Signos de apertura ¿ ¡ siempre.
15. MÁXIMO 3-4 adverbios en -mente por cada mil palabras. Prefiere
    reformular: "caminó lentamente" -> "caminó sin prisa" o muestra el ritmo.
16. GERUNDIO con moderación: nunca gerundio de posterioridad
    ("salió corriendo, chocando luego con..."), nunca dos gerundios seguidos.
17. CERO calcos del inglés: ni "eventualmente" por finalmente, ni "hacer
    sentido", ni posesivos redundantes ("cerró sus ojos" -> "cerró los ojos"),
    ni "sacudió la cabeza" -> "negó con la cabeza".
18. Voz activa por defecto. La pasiva con "ser" solo si el énfasis lo exige;
    prefiere la pasiva refleja ("se distribuyeron los brazaletes").

PATRONES A EVITAR (marcados en capítulos previos por el evaluador):
19. NADA de listas sensoriales triádicas ("X. Y. Z." o "X y Y y Z").
    Combina dos, corta una, o reestructura.
20. "No + verbo" como recurso retórico: máximo una vez por capítulo.
21. Nada de "Pensó en X": usa el pensamiento mismo como fragmento,
    una acción física, o diálogo.
22. NO sobre-expliques después de mostrar. Si la escena lo demuestra,
    el narrador no lo repite.
23. Separadores de sección (---) solo para saltos reales de tiempo/lugar.
    Máximo 2 por capítulo.
24. VARÍA la longitud de párrafos deliberadamente: al menos un párrafo de
    1-2 oraciones y uno de 6+ oraciones. Nunca más de 3 párrafos seguidos
    de longitud similar.
25. TERMINA el capítulo de forma distinta a los anteriores. Busca el final
    que pertenece a ESTE capítulo.
26. INCLUYE al menos un momento que sorprenda: alguien que dice lo
    incorrecto, un beat emocional que llega antes o después de lo esperado,
    un detalle que rompe el patrón.
27. ESCENA sobre resumen: al menos 70% del capítulo en escena (momento a
    momento, con diálogo y acción), no en resumen narrativo.
28. El DIÁLOGO suena a habla, no a prosa: la gente titubea, se interrumpe,
    deja frases a medias, dice algo levemente equivocado.

REGLAS DE REALIDAD (obligatorias — nacidas de la revisión del autor):
29. RAPTO PARCIAL: desapareció ~1 de cada 8 personas (más en Honduras y
    Latinoamérica, menos en Europa/Asia). NINGUNA escena muestra al 100%
    de la gente desaparecida, salvo agrupación verosímil justificada EN
    escena (un bus de iglesia, una vigilia). Todo desastre incluye su
    consecuencia humana: heridos, gritos, sobrevivientes en shock,
    gente buscando a los suyos. El horror del Día 0 es el CONTRASTE
    entre el caos de los que quedaron y los espacios inexplicablemente
    vacíos — nunca una quietud fantasmal total.
30. GEOGRAFÍA: solo usa datos geográficos presentes en GEOGRAFIA.md o
    en el informe de realidad (vegetación, distancias, clima, rutas).
    Si no está verificado, mantenlo vago ("el cerro", "la carretera").
    No inventes paisaje.
31. LÉXICO REGIONAL Y ACCESIBLE: la narración usa el registro del
    personaje POV. Protocolo de radio en español: "copiado" (nunca
    "cópialo"). Los creyentes evangélicos ORAN (nunca "rezan"; "rezar"
    solo en boca de personajes de contexto católico). Evita palabras
    que el lector promedio no usa ("crepitar", "yermo"): di lo mismo
    en llano. Nada de anatomía técnica en narración de personaje no
    médico ("tendones del antebrazo" -> "los brazos").
32. FÍSICA CON COSTO: toda maniobra difícil (mover camiones entre
    choques, cruzar zonas bloqueadas, tratar un herido) se muestra
    COSTANDO tiempo y esfuerzo concreto, nunca resuelta en una frase.
33bis. ORDEN CAUSAL DE BEATS (regla dura): los beats del outline con
    fechas (D+/T+) están en ORDEN CAUSAL OBLIGATORIO. No muevas un
    evento fechado a otra posición del capítulo aunque el arco
    emocional lo sugiera — las dependencias causales (una conversión
    antes de un pacto, una decisión antes de una acción) son canon.
    Si el orden del outline te parece dramáticamente inferior, escribe
    el orden del outline de todas formas: la estructura ya fue
    decidida por el autor.
33. PROVIDENCIA SIN FABRICACIÓN: la fe de esta novela se muestra en lo
    que los personajes ELIGEN mirar y hacer, jamás en coincidencias
    que trabajen por ellos. Prohibido: objetos sagrados que aparecen
    sin explicación mundana, biblias que se abren "solas" en el verso
    perfecto, señales inequívocas que sustituyen la decisión del
    personaje. Las señales legítimas preexisten y están disponibles
    para cualquiera (como las pintas de Miqueas 7:7); la gracia está
    en que el personaje decide atenderlas, con esfuerzo y con costo.

Escribe el capítulo ahora. Texto completo, de principio a fin.
"""

    print(f"Drafting Chapter {chapter_num}...", file=sys.stderr)
    result = call_writer(prompt)
    
    # Save
    out_path = CHAPTERS_DIR / f"ch_{chapter_num:02d}.md"
    out_path.write_text(result)
    print(f"Saved to {out_path}", file=sys.stderr)
    print(f"Word count: {len(result.split())}", file=sys.stderr)
    print(result)

if __name__ == "__main__":
    main()
