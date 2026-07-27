#!/usr/bin/env python3
"""
One-shot world.md generator for foundation phase.
Reads seed.txt + voice.md, calls the writer model, outputs world.md content.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from fundacion_comun import ruta_bilingue, load_file, load_file_bilingue, extraer_voz_parte2, exigir_semilla

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

WRITER_MODEL = os.environ.get("AUTONOVEL_WRITER_MODEL", "claude-sonnet-4-6")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_BASE = os.environ.get("AUTONOVEL_API_BASE_URL", "https://api.anthropic.com")

def call_writer(prompt, max_tokens=16000):
    import httpx
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": WRITER_MODEL,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "system": (
            "Sos un diseñador de mundos con conocimiento profundo de las Leyes de "
            "Sanderson, la filosofía de prosa de Le Guin, y diseño de lore de calidad "
            "TTRPG. Escribís biblias de mundo específicas, interconectadas, que sugieren "
            "profundidad más allá de lo dicho. Nunca usás relleno de IA (profundizar, "
            "entramado, miríada, etc). Escribís en prosa limpia y directa, en español. "
            "Cada regla tiene un costo. Cada detalle cultural implica una historia. "
            "Cada lugar tiene una firma sensorial."
        ),
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = httpx.post(f"{API_BASE}/v1/messages", headers=headers, json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def build_prompt(seed, voice_part2, craft):
    return f"""Construí una biblia de mundo completa para esta novela. Este es el
archivo MUNDO.MD -- la referencia definitiva de todo lo que EXISTE en este mundo.
Un escritor debería poder resolver cualquier pregunta de ambientación a partir de
este documento solo.

El género y el tono salen de la SEMILLA, no de este prompt -- no asumas que es
fantasía ni que necesita un sistema de magia. Si la semilla no plantea reglas
excepcionales (magia, tecnología especulativa, o cualquier otra capacidad que no
existe en el mundo real), no inventes ninguna.

CONCEPTO SEMILLA:
{seed}

IDENTIDAD DE VOZ (tono y registro de esta novela):
{voice_part2}

REQUISITOS DE OFICIO:
- SI el mundo tiene un sistema de magia u otra capacidad excepcional (según lo
  que pida la semilla): reglas duras con COSTOS y LIMITACIONES, según la Segunda
  Ley de Sanderson. Las limitaciones deben pesar tanto o más que los poderes en
  el relato. Rastreá las implicaciones a través de la sociedad, la economía, la
  ley, la religión (al menos 2-3 implicaciones sociales exploradas en profundidad).
- La historia debe crear TENSIONES DEL PRESENTE que impulsen la trama, no ser
  solo telón de fondo.
- La geografía debe ser específica y sensorial.
- Principio del iceberg: sugerí más de lo que decís.
- Interconexión: tirar de un hilo debería mover todo lo demás.

ESTRUCTURÁ EL DOCUMENTO CON ESTAS SECCIONES:

## Cosmología e historia
Una línea de tiempo de eventos mayores. Enfocate en eventos que generen
tensiones del PRESENTE. Incluí el mito fundacional (si aplica), puntos de
quiebre clave, y eventos recientes que importen a la trama.

## Reglas excepcionales del mundo (si aplica)
### Reglas duras
Reglas específicas y comprobables, si la semilla plantea algún sistema de
magia u otra capacidad excepcional. Qué hace qué. Qué las ata. Qué pasa si se
rompen. Costos y limitaciones bien visibles. Si la semilla no pide nada de
esto, escribí "No aplica" y seguí -- no inventes un sistema que nadie pidió.

### Implicaciones sociales
Cómo esas reglas (si existen) moldean: gobierno, comercio, educación,
estructura de clases, delito, vida familiar, infancia, vejez, discapacidad.

## Geografía
Disposición física del lugar central de la historia, zonas o distritos,
lugares vecinos (al menos 2-3). Firma sensorial para cada lugar. Los nombres
de lugares salen de la semilla o se inventan de cero -- nunca de otra novela.

## Facciones y política
Quién tiene poder, quién lo quiere, a quién está aplastando. Al menos 3-4
facciones con intereses opuestos.

## Bestiario / flora / mundo natural
Qué tiene de particular el mundo natural de este lugar. Si la semilla plantea
un mundo contemporáneo realista sin fauna o flora relevante a la trama, esta
sección puede quedar breve o "No aplica".

## Detalles culturales
Costumbres, tabúes, festividades, comida, vestimenta, rituales de paso. Cosas
que hacen que la vida cotidiana se sienta ESPECÍFICA.

## Reglas de consistencia interna
Restricciones duras que un escritor no debe violar. Qué es posible y qué no
en este mundo.

IMPORTANTE:
- Sé ESPECÍFICO. No "la ciudad tiene distritos" sino nombralos, describilos,
  dales firma sensorial.
- Cada regla debería tener un COSTO o LIMITACIÓN al lado.
- Incluí 2-3 datos por sección que queden sin explicar del todo, sugiriendo
  sistemas más profundos (profundidad de iceberg).
- Los datos deben INTERCONECTAR: lo excepcional (si existe) debe moldear la
  política, la geografía debe moldear la cultura, la historia debe explicar
  los conflictos de facciones actuales.
- Escribí en prosa limpia y directa. Nada de relleno de IA. Nada de "rico
  entramado". Nada de "profundizar".
- El mundo debe sentirse habitado, no imaginado. Pensá: ¿a qué huele el
  desayuno? ¿A qué juegan los chicos? ¿De qué se queja la gente mayor?
- Extensión objetivo ~3000-4000 palabras. Denso, no relleno.
"""


def main():
    seed = load_file_bilingue(BASE_DIR, "semilla.txt", "seed.txt")
    exigir_semilla(seed, "generar un mundo")

    voice = load_file_bilingue(BASE_DIR, "voz.md", "voice.md")
    voice_part2 = extraer_voz_parte2(voice)
    craft = load_file(BASE_DIR / "CRAFT.md")

    prompt = build_prompt(seed, voice_part2, craft)

    print("Calling writer model...", file=sys.stderr)
    result = call_writer(prompt)

    out_path = ruta_bilingue(BASE_DIR, "mundo.md", "world.md")
    out_path.write_text(result, encoding="utf-8")
    print(f"Saved to {out_path}", file=sys.stderr)
    print(result)


if __name__ == "__main__":
    main()
