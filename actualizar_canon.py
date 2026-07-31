#!/usr/bin/env python3
"""
actualizar_canon.py -- Vuelca a canon_emergente.md los hechos que el juez
de evaluate.py reportó en new_canon_entries para un capítulo (Tarea 10,
ENCARGO_CLAUDE_CODE.md).

canon.md sigue siendo función pura de semilla+mundo+personajes -- lo pisa
gen_canon.py. Este script escribe canon_emergente.md, un archivo distinto
que gen_canon.py nunca toca, para que la fundación se pueda regenerar sin
perder lo que la redacción fue estableciendo capítulo a capítulo.

No llama a la API: la detección de contradicciones ya la hizo el juez
(evaluate.py), que tiene todo el canon en contexto. Este script solo
estructura lo que el juez ya devolvió -- determinista y testeable sin
mocks.

Uso:
  uv run actualizar_canon.py 7
  uv run actualizar_canon.py 7 --eval-log eval_logs/20260315_143022_ch07.json
"""

import argparse
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
EVAL_LOG_DIR = BASE_DIR / "eval_logs"
CANON_EMERGENTE_PATH = BASE_DIR / "canon_emergente.md"
STATE_PATH = BASE_DIR / "state.json"

ENCABEZADO = (
    "# CANON EMERGENTE -- hechos establecidos durante la redacción\n"
    "\n"
    "<!-- Lo escribe actualizar_canon.py. No editar a mano salvo para\n"
    "     resolver los marcados con CONFLICTO. -->\n"
)

SIN_HECHOS = "(el juez no reportó hechos nuevos en este capítulo)"


def buscar_eval_log_mas_reciente(chapter_num):
    """Más reciente eval_log que matchee eval_logs/*_chNN.json. El nombre
    de archivo lleva un timestamp YYYYMMDD_HHMMSS como prefijo (ver
    evaluate.py), así que ordenar alfabéticamente equivale a ordenar por
    fecha -- no hace falta leer mtime."""
    if not EVAL_LOG_DIR.exists():
        return None
    candidatos = sorted(EVAL_LOG_DIR.glob(f"*_ch{chapter_num:02d}.json"))
    return candidatos[-1] if candidatos else None


def parsear_secciones(texto):
    """(numero_de_capitulo -> contenido de esa sección, sin el encabezado
    '## Cap. NN' ni el encabezado del archivo). Vacío si no hay ninguna
    sección todavía."""
    import re

    secciones = {}
    matches = list(re.finditer(r'^## Cap\.\s*(\d+)\s*$', texto, re.MULTILINE))
    for i, m in enumerate(matches):
        num = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(texto)
        secciones[num] = texto[start:end].strip("\n")
    return secciones


def formatear_seccion(chapter_num, entries):
    """Devuelve (texto_de_la_seccion, lista_de_conflictos). Cada conflicto
    es un dict listo para guardarse en state.json::debts."""
    lineas = []
    conflictos = []
    for idx, entrada in enumerate(entries, start=1):
        categoria = (entrada.get("categoria") or "(sin categoría)").strip()
        hecho = (entrada.get("hecho") or "").strip()
        contradice = entrada.get("contradice")
        id_ = f"C{chapter_num:02d}-{idx:02d}"

        if contradice:
            lineas.append(f"- [{id_}] CONFLICTO ({categoria}) {hecho}")
            lineas.append(f'  <!-- contradice: "{contradice}". Sin resolver. -->')
            conflictos.append({
                "id": id_,
                "capitulo": chapter_num,
                "categoria": categoria,
                "hecho": hecho,
                "contradice": contradice,
                "resuelta": False,
            })
        else:
            lineas.append(f"- [{id_}] ({categoria}) {hecho}")

    if not lineas:
        lineas = [SIN_HECHOS]

    return "\n".join(lineas), conflictos


def render_canon_emergente(secciones):
    partes = [ENCABEZADO.rstrip("\n") + "\n"]
    for num in sorted(secciones):
        partes.append(f"\n## Cap. {num:02d}\n\n{secciones[num]}\n")
    return "".join(partes)


def actualizar_canon_emergente(chapter_num, entries):
    """Reemplaza (no anexa) la sección '## Cap. NN' correspondiente.
    Reemplazo entero, no append: los capítulos se re-evalúan (revisiones,
    bucle de descarte de run_pipeline.py), y con append puro cada
    reintento duplicaría entradas. Devuelve la lista de conflictos
    encontrados en ESTE capítulo."""
    texto_actual = CANON_EMERGENTE_PATH.read_text(encoding="utf-8") \
        if CANON_EMERGENTE_PATH.exists() else ""
    secciones = parsear_secciones(texto_actual)

    contenido_seccion, conflictos = formatear_seccion(chapter_num, entries)
    secciones[chapter_num] = contenido_seccion

    CANON_EMERGENTE_PATH.write_text(render_canon_emergente(secciones), encoding="utf-8")
    return conflictos


def actualizar_debts(chapter_num, conflictos):
    """Reemplaza en state.json los debts de ESTE capítulo (mismo motivo
    que el reemplazo de sección: re-evaluar un capítulo no debe duplicar
    sus conflictos anteriores)."""
    state = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.exists() else {}
    debts = [d for d in state.get("debts", []) if d.get("capitulo") != chapter_num]
    debts.extend(conflictos)
    state["debts"] = debts
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Vuelca new_canon_entries a canon_emergente.md")
    parser.add_argument("chapter", type=int, help="Número de capítulo")
    parser.add_argument("--eval-log", type=str, default=None,
                         help="Ruta a un eval_log específico (por defecto, el más reciente para este capítulo)")
    args = parser.parse_args()

    if args.eval_log:
        eval_log_path = Path(args.eval_log)
        if not eval_log_path.exists():
            sys.exit(f"ERROR: no existe {eval_log_path}")
    else:
        eval_log_path = buscar_eval_log_mas_reciente(args.chapter)
        if eval_log_path is None:
            sys.exit(
                f"ERROR: no se encontró ningún eval_log para el capítulo "
                f"{args.chapter} (patrón eval_logs/*_ch{args.chapter:02d}.json). "
                f"Corré 'evaluate.py --chapter={args.chapter}' primero, o "
                f"pasá --eval-log."
            )

    data = json.loads(eval_log_path.read_text(encoding="utf-8"))
    entries = data.get("new_canon_entries", [])

    if entries and not isinstance(entries[0], dict):
        print(
            f"AVISO: {eval_log_path} tiene new_canon_entries en formato "
            f"viejo (lista de strings, no de objetos categoria/hecho/"
            f"contradice) -- no se puede estructurar por categoría. "
            f"Salteando el Cap. {args.chapter:02d}: canon_emergente.md no "
            f"se modifica.",
            file=sys.stderr,
        )
        return

    conflictos = actualizar_canon_emergente(args.chapter, entries)
    actualizar_debts(args.chapter, conflictos)

    print(f"canon_emergente.md actualizado -- Cap. {args.chapter:02d} "
          f"({len(entries)} entradas, {len(conflictos)} conflicto(s)).")

    for c in conflictos:
        print(
            f"\n*** CONFLICTO [{c['id']}] ({c['categoria']}) ***\n"
            f"    hecho:      {c['hecho']}\n"
            f"    contradice: {c['contradice']}\n"
            f"    Sin resolver -- anotado en state.json::debts.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
