#!/usr/bin/env python3
"""
Helpers compartidos por los generadores de la fase de fundación
(gen_world.py, gen_characters.py, gen_canon.py, gen_outline.py,
gen_outline_part2.py). Sin este módulo, cada script duplicaba las mismas
funciones -- ver ENCARGO_CLAUDE_CODE.md, Tarea 6.

exigir_semilla() la usan los cuatro generadores que consumen la semilla
(gen_world.py, gen_characters.py, gen_canon.py, gen_outline.py).
gen_outline_part2.py no carga seed.txt/semilla.txt en absoluto -- no le
aplica.

gen_voice.py (Tarea "generador de voz") también importa de acá:
extraer_voz_parte2(), voz_parte2_tiene_contenido() y exigir_semilla().

Nada de lo que hay acá llama a la API ni tiene efectos de red.
"""
import re
import sys
from pathlib import Path


def load_file(path):
    """Lee un archivo como texto. Vacío ("") si no existe -- nunca rompe."""
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return ""


def ruta_bilingue(base_dir, nombre_es, nombre_en):
    """Nomenclatura de AUDITORIA_Y_PLAN.md: preferí el nombre en español si
    existe; si no, caé al nombre en inglés (compatibilidad con ramas/
    plantillas viejas). base_dir explícito (no un global del módulo) para
    que sea trivial de testear -- pasá un tmp_path y listo, sin monkeypatch."""
    ruta_es = Path(base_dir) / nombre_es
    if ruta_es.exists():
        return ruta_es
    return Path(base_dir) / nombre_en


def load_file_bilingue(base_dir, nombre_es, nombre_en):
    return load_file(ruta_bilingue(base_dir, nombre_es, nombre_en))


def extraer_voz_parte2(voice_text):
    """Solo la Parte 2 (identidad de voz) de voz.md/voice.md. Si no
    encuentra el encabezado de Parte 2 (archivo vacío, formato distinto),
    devuelve el texto completo tal cual -- no rompe con StopIteration."""
    lines = voice_text.split('\n')
    for i, line in enumerate(lines):
        if 'Part 2' in line or 'Parte 2' in line:
            return '\n'.join(lines[i:])
    return voice_text


def voz_parte2_tiene_contenido(voice_text):
    """True si la Parte 2 de voz.md/voice.md ya tiene contenido real --
    no solo los comentarios HTML placeholder y los encabezados de la
    plantilla. Usado para la idempotencia de gen_voice.py (no regenerar
    una voz que ya se decidió) y por run_pipeline.py::verificar_archivos_fundacion()
    (voz.md se congela después de la primera iteración que la generó, así
    que no se puede verificar por mtime como los demás archivos de
    fundación -- ver Tarea "generador de voz")."""
    parte2 = extraer_voz_parte2(voice_text)
    sin_comentarios = re.sub(r'<!--.*?-->', '', parte2, flags=re.DOTALL)
    sin_encabezados = re.sub(r'^#{1,6}\s.*$', '', sin_comentarios, flags=re.MULTILINE)
    return bool(sin_encabezados.strip())


def exigir_semilla(seed, accion):
    """Aborta con sys.exit si la semilla está vacía o no existe. Una
    semilla vacía no debe llegar a la API -- fallar es más barato que
    generar sobre la nada. Usado por los cuatro generadores que consumen
    la semilla (gen_world.py, gen_characters.py, gen_canon.py,
    gen_outline.py). gen_outline_part2.py no la consume -- no le aplica."""
    if not seed.strip():
        sys.exit(f"ERROR: semilla.txt/seed.txt está vacío o no existe -- "
                  f"no se puede {accion} desde la nada.")
