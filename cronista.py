#!/usr/bin/env python3
"""
cronista.py — Agente cronista del pipeline.

Cierra la brecha de continuidad entre capítulos: cada capítulo se
escribe sin releer los anteriores (solo recibe la fundación), así que
los datos que nacen DENTRO de un capítulo (nombres de secundarios,
objetos, horas, detalles establecidos) no existen para el siguiente
salvo que alguien los registre. Ese alguien es este agente.

USO (después de aprobar cada capítulo):
    uv run python cronista.py --registrar N

Hace dos cosas:
1. Extrae los HECHOS DUROS nuevos del capítulo N (personajes nuevos
   con nombre, edades, lugares, objetos, horas, eventos establecidos)
   y los añade a canon.md bajo "## Hechos registrados por capítulo".
2. Escribe/actualiza resumen_capitulos.md con un resumen de
   continuidad del capítulo (qué ocurre, qué cambia, qué queda
   abierto, en qué estado terminan personajes y objetos).

resumen_capitulos.md se inyecta luego en draft_chapter.py,
realidad.py y evaluate.py — así el escritor, el agente de realidad y
el juez conocen lo ya establecido.

Es idempotente: si el capítulo ya fue registrado, reemplaza su
sección (útil tras una revisión con gen_revision.py).
"""

import argparse
import re

from evaluate import call_judge, load_file, BASE_DIR, CHAPTERS_DIR

RESUMEN_PATH = BASE_DIR / "resumen_capitulos.md"
CANON_PATH = BASE_DIR / "canon.md"
CANON_SECCION = "## Hechos registrados por capítulo"

EXTRACT_PROMPT = """Eres el CRONISTA de una novela en producción. Tu único
trabajo: leer el capítulo recién aprobado y extraer lo que los
capítulos FUTUROS necesitan saber para no contradecirlo. No evalúas
calidad — solo registras hechos.

CANON EXISTENTE (para NO repetir lo que ya está registrado):
{canon}

CAPÍTULO {num} (texto completo):
{chapter_text}

Produce EXACTAMENTE estas dos secciones, en español, sin comentarios
adicionales:

=== HECHOS ===
Lista de viñetas con los hechos duros NUEVOS que este capítulo
establece y que no están ya en el canon. Solo hechos falsables que un
capítulo futuro podría contradecir:
- Personajes nuevos con nombre (nombre, edad aproximada, rol, rasgo
  distintivo, relación con el POV) — INCLUYE a los secundarios menores
  (un chofer, un soldado, una enfermera CON NOMBRE cuentan; extras sin
  nombre no).
- Datos nuevos sobre personajes existentes (algo que se fija aquí:
  una cicatriz, un hábito, un número de teléfono guardado, un objeto
  que poseen).
- Objetos con continuidad (dónde quedó cada objeto importante al final
  del capítulo).
- Lugares/rutas/horas establecidos con precisión.
- Estados al cierre: dónde está físicamente cada personaje con nombre
  al terminar el capítulo, qué sabe y qué no sabe.
Formato de cada viñeta: "- <hecho>. (cap. {num})"
Si el capítulo no establece hechos nuevos (raro), escribe "- (sin
hechos nuevos)".

=== RESUMEN ===
Un solo párrafo de 120-180 palabras, denso y factual: qué OCURRE (en
orden), qué CAMBIA (estado del personaje/mundo del inicio al final),
y qué queda ABIERTO (preguntas, promesas, objetos en tránsito). Sin
valoraciones, sin adjetivos de calidad. Este párrafo es la memoria
que los capítulos siguientes tendrán de este."""


def _reemplazar_seccion(texto, encabezado, nuevo_contenido):
    """Reemplaza (o añade) una sección '### Cap. N' dentro de un bloque."""
    patron = re.compile(
        rf"(^{re.escape(encabezado)}\n)(.*?)(?=^###\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    if patron.search(texto):
        return patron.sub(nuevo_contenido + "\n", texto, count=1)
    return texto + "\n" + nuevo_contenido + "\n"


def registrar(num):
    path = CHAPTERS_DIR / f"ch_{num:02d}.md"
    text = load_file(path)
    if not text.strip():
        raise SystemExit(f"No existe {path}")

    canon = load_file(CANON_PATH)
    raw = call_judge(
        EXTRACT_PROMPT.format(canon=canon[:9000], num=num, chapter_text=text),
        max_tokens=4000,
    )

    # Separar las dos secciones
    try:
        hechos = raw.split("=== HECHOS ===")[1].split("=== RESUMEN ===")[0].strip()
        resumen = raw.split("=== RESUMEN ===")[1].strip()
    except IndexError:
        # Fallback: el modelo pudo haber devuelto JSON en vez del formato esperado
        import json as _json
        limpio = raw.strip()
        if limpio.startswith("```"):
            limpio = re.sub(r"^```(json)?\s*|```\s*$", "", limpio.strip(), flags=re.MULTILINE).strip()
        try:
            data = _json.loads(limpio)
            hechos_list = data.get("hechos", [])
            hechos = "\n".join(hechos_list) if isinstance(hechos_list, list) else str(hechos_list)
            resumen = data.get("resumen", "").strip()
            if not hechos or not resumen:
                raise ValueError("JSON incompleto")
        except Exception:
            raise SystemExit("El cronista no devolvió el formato esperado:\n" + raw[:800])

    # ---- 1. Actualizar canon.md ----
    if CANON_SECCION not in canon:
        canon += f"\n\n{CANON_SECCION}\n\n"
    encabezado_cap = f"### Cap. {num}"
    bloque = f"{encabezado_cap}\n{hechos}\n"
    # ¿ya existe la sección de este capítulo? -> reemplazar
    patron = re.compile(
        rf"^### Cap\. {num}\n.*?(?=^### Cap\.|\Z)", re.MULTILINE | re.DOTALL
    )
    if patron.search(canon):
        canon = patron.sub(bloque, canon, count=1)
        accion_canon = "reemplazada"
    else:
        canon += bloque + "\n"
        accion_canon = "añadida"
    CANON_PATH.write_text(canon)

    # ---- 2. Actualizar resumen_capitulos.md ----
    if RESUMEN_PATH.exists():
        res = RESUMEN_PATH.read_text()
    else:
        res = ("# Resumen de capítulos aprobados\n\n"
               "Memoria de continuidad del manuscrito. Lo mantiene "
               "cronista.py; se inyecta al escritor, al agente de "
               "realidad y al evaluador.\n\n")
    encabezado_res = f"## Cap. {num}"
    bloque_res = f"{encabezado_res}\n{resumen}\n"
    patron_res = re.compile(
        rf"^## Cap\. {num}\n.*?(?=^## Cap\.|\Z)", re.MULTILINE | re.DOTALL
    )
    if patron_res.search(res):
        res = patron_res.sub(bloque_res, res, count=1)
        accion_res = "reemplazado"
    else:
        res += bloque_res + "\n"
        accion_res = "añadido"
    RESUMEN_PATH.write_text(res)

    print(f"canon.md: sección del cap. {num} {accion_canon}")
    print(f"resumen_capitulos.md: resumen del cap. {num} {accion_res}")
    print("\n--- HECHOS REGISTRADOS ---")
    print(hechos)
    print("\n--- RESUMEN ---")
    print(resumen)


def main():
    parser = argparse.ArgumentParser(description="Agente cronista")
    parser.add_argument("--registrar", type=int, metavar="N", required=True,
                        help="Registrar hechos y resumen del capítulo N aprobado")
    args = parser.parse_args()
    registrar(args.registrar)


if __name__ == "__main__":
    main()
