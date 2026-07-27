#!/usr/bin/env python3
"""
realidad.py — Agente de realidad del pipeline.

Su única función: mantener la novela anclada a la realidad física,
demográfica, geográfica y de escalada del mundo. Nadie más en el
pipeline hace este trabajo (evaluate.py mide prosa y canon; review.py
mide manuscrito; el teólogo mide doctrina).

DOS MODOS:

1. ANTES de redactar (informe de realidad):
       uv run python realidad.py --brief N
   Estudia el estado del mundo en la fecha del capítulo N (D+/T+),
   la geografía real de sus escenarios, la física de sus escenas y
   lo que el personaje POV sabe y no sabe — y escribe un INFORME que
   draft_chapter.py inyecta automáticamente al redactar. El escritor
   nunca vuelve a escribir "sin tomar el contexto de lo que está
   pasando".

2. DESPUÉS de redactar (auditoría de coherencia):
       uv run python realidad.py --check N
   Lee el borrador y lista incoherencias de realidad con severidad:
   física imposible, demografía del rapto violada, geografía
   inventada, escalada inconsistente con la línea de tiempo, o
   conocimiento imposible del personaje.

El informe se guarda en briefs/realidad_chNN.md y la auditoría en
eval_logs/.
"""

import argparse
import json
from datetime import datetime, date, timedelta

from evaluate import call_judge, load_file, BASE_DIR, EVAL_LOG_DIR, CHAPTERS_DIR

BRIEFS_DIR = BASE_DIR / "briefs"
BRIEFS_DIR.mkdir(exist_ok=True)

# Año interno de referencia (nunca explícito en la novela) para
# calcular fechas y estaciones reales. D+0 = 7 de enero.
D0 = date(2030, 1, 7)


def fecha_de_capitulo(num):
    """Extrae la fecha D+/T+ del capítulo desde la tabla del outline."""
    outline = load_file(BASE_DIR / "outline.md")
    for line in outline.splitlines():
        if line.strip().startswith(f"| {num} |"):
            partes = [p.strip() for p in line.split("|")]
            # | num | POV | fecha | estación |
            return partes[2], partes[3], partes[4]
    return str(num), "?", "?"


def calendario_real(fecha_str):
    """Convierte 'D+240' o 'T+750' a fecha real y estación."""
    try:
        s = fecha_str.replace("→", " ").split()[0]
        if s.startswith("T+"):
            dias = int(s[2:].strip("+")) + 90
        elif s.startswith("D+"):
            dias = int(s[2:].strip("+"))
        else:
            return "(fecha no calculable)"
        d = D0 + timedelta(days=dias)
        meses = ["enero","febrero","marzo","abril","mayo","junio","julio",
                 "agosto","septiembre","octubre","noviembre","diciembre"]
        est = ["invierno","invierno","primavera","primavera","primavera",
               "verano","verano","verano","otoño","otoño","otoño","invierno"][d.month-1]
        anio = (d.year - D0.year) + 1
        return f"{d.day} de {meses[d.month-1]} del año {anio} de la novela ({est} boreal)"
    except Exception:
        return "(fecha no calculable)"


BRIEF_PROMPT = """Eres el INVESTIGADOR DE REALIDAD de una novela. Tu único
trabajo: estudiar el estado del mundo en la fecha de este capítulo y
entregarle al escritor un informe que lo ancle a la realidad. El
escritor tiende a redactar escenas sin contexto — bonitas pero
imposibles. Tu informe lo impide ANTES de que escriba.

FECHA DEL CAPÍTULO {num}: {fecha} — equivale a: {fecha_real}
POV y estación según outline: {pov_estacion}

BIBLIA DEL MUNDO (línea de tiempo y reglas duras):
{world}

GEOGRAFÍA VERIFICADA (solo estos datos geográficos son utilizables;
lo que no esté aquí debe quedar vago o genérico):
{geografia}

CANON (hechos duros):
{canon}

RESUMEN DE CAPÍTULOS YA APROBADOS (continuidad — el informe debe
respetar y citar estos estados establecidos):
{resumen}

REGLA DE PRIORIDAD (crítica): outline.md es el PLAN ORIGINAL, escrito
antes de que existiera un solo capítulo. canon.md y el resumen de
capítulos son lo que REALMENTE se escribió y puede haberse desviado
del plan original de forma deliberada y ya aprobada. Si algo en el
outline de abajo contradice un hecho ya establecido en canon.md o en
el resumen de capítulos, CANON.MD Y EL RESUMEN GANAN SIEMPRE. No
reportes como restricción o violación algo que el outline sugiere si
canon.md ya demuestra que ocurrió de otra forma. Ejemplo: si el
outline dice "el personaje X no conoce a Y hasta el capítulo N" pero
canon.md ya registra que se conocieron antes, asume que el canon es
correcto y el outline quedó desactualizado por decisiones de escritura
posteriores.

ENTRADA DEL OUTLINE PARA ESTE CAPÍTULO (los beats que se van a escribir):
{chapter_outline}

FINAL DEL CAPÍTULO ANTERIOR (estado en que quedó el mundo/personaje):
{prev_tail}

Redacta el INFORME DE REALIDAD con EXACTAMENTE estas secciones:

## 1. ESTADO DEL MUNDO EN ESTA FECHA
Qué está pasando globalmente según la línea de tiempo de world.md:
en qué fase estamos (colapso / falsa paz / cápsula / post-punto medio),
qué eventos ya ocurrieron, cuáles NO han ocurrido todavía (lista
explícita de "aún no existe/no ha pasado" para evitar anacronismos),
y el nivel de escalada: cuánta comida hay, cómo está la electricidad,
la señal, el orden público, los precios, los hospitales.

## 2. ESTADO LOCAL (donde ocurre el capítulo)
La situación concreta en la ubicación del POV en esta fecha: clima de
la estación real, hora de luz solar, estado de la infraestructura
local, presencia del régimen en esa zona en esta fase.

## 3. FÍSICA DE LAS ESCENAS PREVISTAS
Para cada beat del outline que implique un evento físico (accidentes,
multitudes, viajes, tecnología, medicina): qué pasaría DE VERDAD.
Ejemplos del estándar exigido: un choque en cadena deja heridos,
gritos, atrapados y sobrevivientes en shock — no silencio; ~1 de cada
8 personas desapareció en el rapto (más en Honduras, menos en Europa),
así que NINGUNA escena puede mostrar el 100% de la gente desaparecida
salvo agrupaciones verosímiles (un bus de iglesia, una vigilia); tres
rastras no atraviesan una carretera bloqueada sin maniobras que
cuestan tiempo; un infarto tiene minutos y síntomas concretos.
Incluye números aproximados donde ayuden (cuántos vehículos, cuántos
sobrevivientes, cuántas horas de viaje).

## 4. LO QUE EL POV SABE Y NO SABE
En esta fecha, con las comunicaciones en el estado que estén: qué
información tiene el personaje, qué rumores circulan, qué es
IMPOSIBLE que sepa todavía. El escritor no puede darle conocimiento
del futuro ni de eventos que no le han llegado.

## 5. RESTRICCIONES DURAS DE ESTE CAPÍTULO
Lista numerada de prohibiciones concretas ("no puede haber X porque
en esta fecha Y") que el escritor debe obedecer.

## 6. TEXTURA REAL DISPONIBLE
5-8 detalles sensoriales/sociales verosímiles de esta fecha y lugar
que el escritor puede usar para que la escena se sienta real (qué se
oye, qué falta en las tiendas, qué hace la gente en la calle, qué
dice la radio).

Sé concreto y útil. Nada de generalidades. Este informe se inyecta
directamente al prompt del escritor."""


CHECK_PROMPT = """Eres el AUDITOR DE REALIDAD de una novela. Lee el borrador
del capítulo {num} y encuentra toda incoherencia con la realidad del
mundo. NO evalúes prosa, ritmo ni doctrina (otros jueces lo hacen).
Solo realidad: física, demografía, geografía, escalada temporal,
conocimiento del personaje.

INFORME DE REALIDAD que el escritor debía obedecer:
{informe}

CANON:
{canon}

BORRADOR DEL CAPÍTULO {num}:
{chapter_text}

Busca específicamente:
1. FÍSICA: eventos que no ocurrirían así en la realidad (desastres
   sin heridos ni caos humano, maniobras imposibles, tecnología usada
   fuera de sus reglas, tiempos de viaje imposibles).
2. DEMOGRAFÍA DEL RAPTO: escenas donde desapareció "todo el mundo"
   (violación: fue ~1 de cada 8; los sobrevivientes y su pánico deben
   estar presentes salvo agrupación verosímil justificada en escena).
3. GEOGRAFÍA: datos geográficos que no están en GEOGRAFIA.md
   (vegetación, distancias, nombres, rutas inventadas).
4. ESCALADA: menciones de cosas que aún no existen en esta fecha, o
   normalidad que ya no existiría (comercio, luz, señal, precios).
5. CONOCIMIENTO: el POV sabe algo que no puede saber todavía.
6. AUSENCIA DE CONSECUENCIA: eventos enormes tratados sin su
   consecuencia humana proporcional (terror, duelo, pánico colectivo).

Devuelve SOLO un JSON válido:
{{
  "coherencia_score": <0-10>,
  "incoherencias": [
    {{"severidad": "CRITICA|ALTA|MEDIA|BAJA",
      "cita": "<frase textual del borrador>",
      "problema": "<qué viola y por qué>",
      "instruccion_para_el_escritor": "<qué regla debe obedecer al
       reescribir — NO reescribas tú la frase>"}}
  ],
  "veredicto": "APROBADO|REESCRIBIR",
  "nota_general": "<patrón de fondo si lo hay>"
}}"""


def generar_brief(num):
    fecha, estacion, _ = ("?", "?", "?")
    outline = load_file(BASE_DIR / "outline.md")
    # Extrae la sección del capítulo y la fila de la tabla
    marker = f"### Cap. {num} "
    idx = outline.find(marker)
    chapter_outline = "(no encontrado en outline)"
    if idx >= 0:
        end = outline.find("### Cap.", idx + 10)
        if end < 0:
            end = outline.find("### Epílogo", idx + 10)
        chapter_outline = outline[idx:end if end > 0 else idx + 3000]
    fecha, estacion, *_ = fecha_de_capitulo(num) if fecha_de_capitulo(num) else ("?", "?", "?")
    row = fecha_de_capitulo(num)
    pov_fecha_estacion = " | ".join(row)

    prev_tail = ""
    prev_path = CHAPTERS_DIR / f"ch_{num-1:02d}.md"
    if prev_path.exists():
        prev_tail = load_file(prev_path)[-2500:]

    prompt = BRIEF_PROMPT.format(
        num=num,
        fecha=row[1] if len(row) > 1 else "?",
        fecha_real=calendario_real(row[1] if len(row) > 1 else ""),
        pov_estacion=pov_fecha_estacion,
        world=load_file(BASE_DIR / "world.md"),
        geografia=load_file(BASE_DIR / "GEOGRAFIA.md") or
                  "(GEOGRAFIA.md no existe aún — TODO dato geográfico debe quedar vago)",
        canon=load_file(BASE_DIR / "canon.md"),
        resumen=(load_file(BASE_DIR / "resumen_capitulos.md") or
                 "(sin capítulos registrados)")[:5000],
        chapter_outline=chapter_outline,
        prev_tail=prev_tail or "(primer capítulo)",
    )
    informe = call_judge(prompt, max_tokens=7000)
    out = BRIEFS_DIR / f"realidad_ch{num:02d}.md"
    out.write_text(informe)
    print(informe)
    print(f"\ninforme guardado: {out}")
    print("draft_chapter.py lo inyectará automáticamente al redactar este capítulo.")


def _parse_json_robusto(raw, num):
    """Extrae el primer objeto JSON balanceado del texto. Si el
    modelo cortó la respuesta a mitad de camino (JSON incompleto),
    guarda el texto crudo en un archivo en vez de morir con un
    traceback, para no perder el contenido de la auditoría."""
    start = raw.find("{")
    if start == -1:
        raise SystemExit(f"El auditor no devolvió JSON reconocible:\n{raw[:800]}")

    depth = 0
    in_string = False
    escape = False
    end = None
    for i, ch in enumerate(raw[start:], start=start):
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == '"' and not escape:
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break

    candidate = raw[start:end + 1] if end is not None else raw[start:]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    # Reintento: pedir al modelo que repare su propio JSON
    try:
        repair_prompt = (
            "El siguiente texto debía ser JSON válido pero está mal "
            "formado (posiblemente truncado). Devuelve ÚNICAMENTE el "
            "JSON corregido y completo, sin explicaciones, sin "
            "markdown, cerrando todas las llaves y comillas "
            "correctamente:\n\n" + candidate[:6000]
        )
        repaired = call_judge(repair_prompt, max_tokens=5000).strip()
        if repaired.startswith("```"):
            repaired = repaired.split("```")[1].lstrip("json").strip()
        return json.loads(repaired)
    except Exception:
        pass

    # Última salida: guardar el crudo para no perder el contenido
    fallback_path = EVAL_LOG_DIR / f"realidad_ch{num:02d}_CRUDO_SIN_PARSEAR.txt"
    fallback_path.write_text(raw)
    raise SystemExit(
        f"No se pudo parsear el JSON del auditor tras reintentar.\n"
        f"El texto completo de la auditoría se guardó en:\n"
        f"  {fallback_path}\n"
        f"Ábrelo y léelo directamente; el contenido no se perdió."
    )


def auditar(num):
    path = CHAPTERS_DIR / f"ch_{num:02d}.md"
    text = load_file(path)
    if not text.strip():
        raise SystemExit(f"No existe {path}")
    informe_path = BRIEFS_DIR / f"realidad_ch{num:02d}.md"
    informe = load_file(informe_path) if informe_path.exists() else "(sin informe previo)"
    canon_completo = load_file(BASE_DIR / "canon.md")
    resumen_novela = load_file(BASE_DIR / "resumen_capitulos.md") or "(sin resumen)"
    prompt = CHECK_PROMPT.format(
        num=num, informe=informe,
        canon=canon_completo + "\n\n# RESUMEN DE CAPITULOS APROBADOS (memoria de la novela)\n" + resumen_novela,
        chapter_text=text,
    )
    raw = call_judge(prompt, max_tokens=5000).strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1].lstrip("json").strip()
    result = _parse_json_robusto(raw, num)

    print("---")
    print(f"COHERENCIA DE REALIDAD: {result['coherencia_score']}/10 — {result['veredicto']}")
    for inc in result.get("incoherencias", []):
        print(f"\n[{inc['severidad']}] «{inc['cita'][:90]}»")
        print(f"  problema: {inc['problema']}")
        print(f"  regla para el escritor: {inc['instruccion_para_el_escritor']}")
    if result.get("nota_general"):
        print(f"\nPatrón de fondo: {result['nota_general']}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log = EVAL_LOG_DIR / f"{timestamp}_realidad_ch{num:02d}.json"
    with open(log, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nlog: {log}")


def main():
    parser = argparse.ArgumentParser(description="Agente de realidad")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--brief", type=int, metavar="N",
                       help="Generar informe de realidad ANTES de redactar el capítulo N")
    group.add_argument("--check", type=int, metavar="N",
                       help="Auditar coherencia de realidad del capítulo N ya redactado")
    args = parser.parse_args()
    if args.brief is not None:
        generar_brief(args.brief)
    else:
        auditar(args.check)


if __name__ == "__main__":
    main()
