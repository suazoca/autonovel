"""
Guardia de contaminación de prompts (Tarea 12, ENCARGO_CLAUDE_CODE.md).

Hallazgo: las Tareas 2, 2b y 2c descontaminaron y tradujeron los
generadores, pero nadie auditó los prompts de juez -- evaluate.py,
reader_panel.py, adversarial_edit.py, compare_chapters.py y review.py
seguían en inglés, y los primeros cuatro calibran contra fantasía. Se
pasó porque el ENCARGO agrupa 1a/1b/1c/1d bajo "TAREA 1": al cerrarse 1c
y 1d, la Tarea 1 empezó a leerse como completa aunque 1b (traducción de
los prompts de juez) seguía abierta. docs/HALLAZGOS.md documenta el
hallazgo completo, incluyendo que auditar con este mismo guardia encontró
además 6 archivos más (generadores, no jueces) con el mismo problema.

Este archivo no traduce nada. Hace que la contaminación de género y de
idioma en los prompts sea detectable por el suite sin depender de que
alguien recuerde qué letra de qué tarea quedó abierta.

Por qué `ast` y no imports ni regex sobre el texto:
- Imports: varios de estos módulos hacen load_dotenv() y leen variables
  de entorno apenas se importan -- correrlos como parte de un import es
  un efecto secundario que este test no necesita y no debe pagar.
- Regex sobre el archivo entero: no distingue un literal de string de
  código, comentarios o nombres de variable, y no sabe qué es un
  docstring. `ast` parsea la estructura real y permite recolectar
  *cualquier* literal de string largo -- constantes de módulo (los
  *_PROMPT) y también literales sueltos como las cuatro personas de
  reader_panel.py, que viven dentro de un dict y no son constantes de
  módulo.

Granularidad de la deuda -- por literal, no por archivo: un archivo
puede tener varios prompts (evaluate.py tiene tres: FOUNDATION_PROMPT,
CHAPTER_PROMPT, FULL_NOVEL_PROMPT) que se arreglan en tareas distintas y
en momentos distintos -- la Tarea 10 va a traducir únicamente
CHAPTER_PROMPT. Si el registro marcara xfail el archivo entero, traducir
uno solo de los tres no se notaría (los otros dos seguirían fallando y
tapando el XPASS). Por eso cada literal se parametriza por separado.

La clave de cada entrada del registro es (archivo, hash8_del_texto), NO
(archivo, línea). Motivo concreto: cuando la Tarea 10 traduzca
CHAPTER_PROMPT, el resultado en español sale 15-20% más largo (esa misma
norma que exige el bloque de normas del castellano), así que
FULL_NOVEL_PROMPT -- que hoy empieza en la línea 834 -- se corre hacia
abajo. Con clave por línea, la entrada de FULL_NOVEL_PROMPT quedaría
huérfana: ya no identificaría a ningún literal real, ese literal
correría sin marca y fallaría en rojo con un mensaje que no explica por
qué (parece contaminación nueva cuando en realidad es solo un
corrimiento de línea). Con clave por hash del contenido, la entrada
sigue apuntando al literal correcto se mueva donde se mueva -- y deja de
apuntar a nada el día que ESE literal cambie de contenido, que es
exactamente cuando hay que revisar el registro. El id que pytest muestra
en la salida (`archivo.py:línea[:NOMBRE_DE_CONSTANTE]`) es solo para
lectura humana del reporte, no la clave real.

El chequeo del bloque de normas del castellano (ancla) se parametriza
solo sobre los 7 literales de juez que son una constante con nombre
(*_PROMPT) -- el prompt que lleva la rúbrica de evaluación. Las 4
personas de reader_panel.py y los 2 system prompts sueltos de
adversarial_edit.py/compare_chapters.py quedan afuera: son frases de una
o dos líneas, no la rúbrica, y exigirles el bloque de normas ahí
generaría un incentivo perverso -- la única forma de hacerlos pasar
sería pegar "más largo que el inglés" dentro de la definición de una
persona, contaminando el prompt en vez de traducirlo. Esos 6 literales
siguen cubiertos por género e idioma; solo quedan afuera de la exigencia
de rúbrica.

Limitación conocida del chequeo de idioma: gen_revision.py:26 y
seed.py:86 tienen calibración de género explícita pero su literal es
corto y solo alcanza 2 palabras función distintas ("the", "you"), no las
3 que exige el umbral -- así que el chequeo de idioma no los detecta,
solo el de género. No es un bug: el umbral de 3 palabras existe para no
disparar con las claves de los esquemas JSON (ver más abajo), y ese
mismo umbral sub-detecta prosa inglesa corta que no tenga además una
palabra de género. Un prompt corto, en inglés, sin "fantasy" ni las
otras tres palabras de género, pasaría este guardia sin ser detectado.
"""

import ast
import hashlib
import os
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directorios que no son parte de la generación/evaluación de la novela:
# tests/ es este mismo suite, landing/ es la página de promoción del
# libro, typeset/ es la maquetación para imprenta.
EXCLUDED_DIRS = {"tests", "landing", "typeset"}

MIN_LITERAL_LEN = 200
MIN_PALABRAS_INGLES = 3

GENRE_WORDS = ("fantasy", "magic system", "wizard", "dragon")

# Palabras función, no vocabulario: las claves de los esquemas JSON que
# devuelve el juez (overall_score, weakest_moment, etc.) van a seguir en
# inglés para siempre -- son contrato de código, no prosa -- y no deben
# disparar este chequeo. "the", "you", "with", etc. en cambio solo
# aparecen en prosa inglesa real.
FUNC_WORDS = ("the", "you", "your", "with", "which", "does", "should", "would")

ARCHIVOS_JUEZ = {
    "evaluate.py",
    "reader_panel.py",
    "adversarial_edit.py",
    "compare_chapters.py",
    "review.py",
}

# Frase ancla del bloque de normas del castellano exigido en
# ENCARGO_CLAUDE_CODE.md, sección "1b. Prompts de juez en español"
# (raya de diálogo, subordinación con «y», sujeto pronominal omitido,
# 15-20% más largo que el inglés). Se verifica por esta frase -- la
# cláusula de extensión, la más específica y menos parafraseable de las
# cuatro normas -- y no por el bloque entero, porque una traducción real
# puede reordenar o reformular el resto sin dejar de cumplir la norma.
ANCLA_NORMAS_CASTELLANO = "más largo que el inglés"

# Registro humano: qué archivo, qué tarea lo arregla. Es la referencia
# para leer el porqué de cada entrada (docs/HALLAZGOS.md la desarrolla).
# La aplicación real del xfail es por literal (ver los tres sets de
# líneas más abajo) -- este dict solo provee el texto de la razón.
#
# Se marcan xfail ESTRICTO (strict=True): si un literal se
# traduce/descontamina y el chequeo empieza a pasar, pytest lo reporta
# como XPASS y rompe el suite -- a propósito, para obligar a borrar esa
# entrada en vez de dejarla como deuda muerta que ya nadie lee. Los
# literales que NO están registrados deben pasar en verde; si alguno
# empieza a fallar, es contaminación nueva y el suite debe avisar de
# inmediato, no quedar en silencio como pasó con la Tarea 1b.
DEUDA_CONOCIDA = {
    "evaluate.py": "Tarea 10 (CHAPTER_PROMPT, ya traducido) + 1b "
                   "(FOUNDATION_PROMPT, FULL_NOVEL_PROMPT, y el system= "
                   "de call_judge -- este último recién cruzó el umbral "
                   "de 200 caracteres al agregarle la instrucción de "
                   "escapado de JSON en la Tarea 10, ver HALLAZGOS.md)",
    "review.py": "Tarea 1b, solo traducir (no tiene género)",
    "seed.py": "Tarea 13 -- antes de la semilla del libro 2",
    "gen_outline.py": "Tarea 13 -- solo idioma, producto ya validado (outline.md: 0 calcos en 15.911 palabras)",
    "gen_outline_part2.py": "Tarea 13 -- solo idioma, ídem",
    "gen_art_directions.py": "Tarea 1b-bis, diferible: post-producción",
    "gen_audiobook_script.py": "Tarea 1b-bis, diferible: post-producción",
}

# Snapshot estático de qué literal (archivo, hash8 de su texto) falla
# cada chequeo HOY, relevado a mano en docs/HALLAZGOS.md. hash8 son los
# primeros 8 hex de sha256(texto) -- identifica el CONTENIDO del
# literal, no dónde vive en el archivo (ver docstring del módulo: por
# qué no es (archivo, línea)). No se derivan corriendo el propio
# chequeo: si se derivaran así, el xfail nunca podría convertirse en
# XPASS -- se recalcularía en el momento de correr el test y siempre
# coincidiría con la realidad actual, con lo cual traducir un literal
# pasaría desapercibido en vez de romper el suite. Por eso quedan
# desincronizados a propósito hasta que alguien los actualice a mano al
# cerrar la tarea correspondiente -- esa actualización manual es la
# señal misma de que la tarea se cerró. La línea y el nombre de
# constante en el comentario son solo para ubicar el literal a simple
# vista; no los lee el test.
_DEUDA_GENERO_HASHES = {
    ("evaluate.py", "b4d3cbf7"),  # línea 455 FOUNDATION_PROMPT
    ("evaluate.py", "9396bbad"),  # línea 834 FULL_NOVEL_PROMPT
    ("seed.py", "b04f9b6c"),  # línea 35, system
    ("seed.py", "3f08e081"),  # línea 48, GENERATE_PROMPT
    ("seed.py", "194be2e6"),  # línea 86, RIFF_PROMPT
    ("gen_art_directions.py", "92e72978"),  # línea 97, task de mapas
}
_DEUDA_IDIOMA_HASHES = {
    ("evaluate.py", "b4d3cbf7"),  # línea 455
    ("evaluate.py", "9396bbad"),  # línea 834
    ("seed.py", "b04f9b6c"),  # línea 35
    ("seed.py", "3f08e081"),  # línea 48
    ("gen_outline.py", "a5aa81d5"),  # línea 25, system
    ("gen_outline.py", "ffe50170"),  # línea 61, BUILD THE OUTLINE WITH
    ("gen_outline.py", "2cd18d0f"),  # línea 92, Foreshadowing Ledger
    ("gen_outline_part2.py", "70c91cfe"),  # línea 48, continuación del esquema
    ("gen_art_directions.py", "b3ca68df"),  # línea 45, task de portadas
    ("gen_audiobook_script.py", "af6b9f28"),  # línea 98, RULES del guion
    ("evaluate.py", "942a279a"),  # línea 409, system de call_judge --
    # literal nuevo en este registro: siempre estuvo en inglés (169
    # caracteres), pero por debajo de MIN_LITERAL_LEN=200 el guardia no
    # lo veía. La Tarea 10 le agregó la instrucción de escapado de JSON
    # (nada que ver con traducir), quedó en 302 caracteres, y recién ahí
    # el guardia lo descubrió. Sin género (no menciona fantasía). Ver
    # docs/HALLAZGOS.md para el hallazgo sobre el umbral en sí.
    # seed.py:86 (RIFF_PROMPT) y gen_revision.py:26 tienen género pero
    # solo 2 palabras función ("the", "you") -- no cruzan el umbral de 3,
    # no entran acá. Ver limitación conocida en el docstring del módulo.
}
# Solo los 7 literales de juez que son la constante *_PROMPT que lleva
# la rúbrica de evaluación -- no las personas ni los system prompts de
# una o dos frases (reader_panel.py:30/43/56/69, adversarial_edit.py:34,
# compare_chapters.py:35). El ancla se exige en el prompt que contiene la
# rúbrica, no en cualquier literal largo del archivo. Motivo de excluir
# a los demás: la Tarea 1b ya tradujo las 4 personas de reader_panel.py
# (sus 4 entradas se borraron de _DEUDA_GENERO_HASHES/_DEUDA_IDIOMA_HASHES
# una vez confirmado que sus hashes viejos ya no correspondían a ningún
# literal del repo -- ver git log de reader_panel.py, commit f1a2602).
# El único arreglo posible para exigirles el ancla sería pegar "más
# largo que el inglés" dentro de la definición de una persona: eso no
# traduce nada, contamina el prompt para hacer pasar al guardia. Por
# eso quedan afuera de este set a propósito, no por descuido.
_DEUDA_ANCLA_HASHES = {
    ("evaluate.py", "b4d3cbf7"),  # línea 455, FOUNDATION_PROMPT
    ("evaluate.py", "9396bbad"),  # línea 834, FULL_NOVEL_PROMPT
    ("review.py", "13c7a1a3"),  # línea 36, REVIEW_PROMPT
}


def _docstring_ids(tree):
    """IDs de los nodos Constant que son el docstring de Module/Def/Class."""
    ids = set()
    for nodo in ast.walk(tree):
        if isinstance(nodo, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            cuerpo = getattr(nodo, "body", None)
            if not cuerpo:
                continue
            primero = cuerpo[0]
            if (
                isinstance(primero, ast.Expr)
                and isinstance(primero.value, ast.Constant)
                and isinstance(primero.value.value, str)
            ):
                ids.add(id(primero.value))
    return ids


def _nombres_de_constantes(tree):
    """Mapea id(nodo) -> nombre para literales asignados a un solo NAME
    (los *_PROMPT de módulo). Los literales sueltos -- kwargs, valores de
    dict, como las personas de reader_panel.py -- no tienen entrada y
    quedan identificados solo por línea."""
    nombres = {}
    for nodo in ast.walk(tree):
        if (
            isinstance(nodo, ast.Assign)
            and len(nodo.targets) == 1
            and isinstance(nodo.targets[0], ast.Name)
            and isinstance(nodo.value, ast.Constant)
            and isinstance(nodo.value.value, str)
        ):
            nombres[id(nodo.value)] = nodo.targets[0].id
    return nombres


def _literales_con_nombre(ruta):
    """Literales de string de más de 200 caracteres en un .py, vía ast,
    sin docstrings de módulo/función/clase. Devuelve (línea, texto,
    nombre_de_constante_o_None)."""
    arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=str(ruta))
    docstring_ids = _docstring_ids(arbol)
    nombres = _nombres_de_constantes(arbol)
    literales = []
    for nodo in ast.walk(arbol):
        if (
            isinstance(nodo, ast.Constant)
            and isinstance(nodo.value, str)
            and len(nodo.value) > MIN_LITERAL_LEN
            and id(nodo) not in docstring_ids
        ):
            literales.append((nodo.lineno, nodo.value, nombres.get(id(nodo))))
    return sorted(literales)


def _iter_repo_py_files():
    archivos = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [
            d for d in dirnames
            if d not in EXCLUDED_DIRS and not d.startswith(".") and d != "__pycache__"
        ]
        for nombre in filenames:
            if nombre.endswith(".py"):
                archivos.append(Path(dirpath) / nombre)
    return sorted(archivos)


def _terminos_genero(texto):
    bajo = texto.lower()
    return [palabra for palabra in GENRE_WORDS if palabra in bajo]


def _palabras_ingles(texto):
    encontradas = set()
    for palabra in FUNC_WORDS:
        if re.search(r"\b" + re.escape(palabra) + r"\b", texto, re.IGNORECASE):
            encontradas.add(palabra)
    return encontradas


def _hash8(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:8]


ARCHIVOS_RAIZ = _iter_repo_py_files()
NOMBRES_RELATIVOS = [str(p.relative_to(REPO_ROOT)) for p in ARCHIVOS_RAIZ]

# (archivo, línea, texto, nombre_o_None) de todo literal largo del repo.
LITERALES = [
    (archivo, lineno, texto, nombre)
    for archivo in NOMBRES_RELATIVOS
    for lineno, texto, nombre in _literales_con_nombre(REPO_ROOT / archivo)
]
LITERALES_JUEZ = [lit for lit in LITERALES if lit[0] in ARCHIVOS_JUEZ]

# Subconjunto de LITERALES_JUEZ que además es una constante con nombre
# (*_PROMPT) -- el prompt que lleva la rúbrica de evaluación, no una
# persona ni un system prompt suelto. Solo estos 7 se parametrizan en
# test_prompt_de_juez_tiene_normas_del_castellano (ver el comentario de
# _DEUDA_ANCLA_HASHES para el motivo).
LITERALES_JUEZ_CON_RUBRICA = [lit for lit in LITERALES_JUEZ if lit[3] is not None]

# Mismas claves (archivo, hash8) que usan los sets de deuda, para poder
# comparar "¿esta entrada del registro corresponde a algún literal que
# existe hoy en el repo?" sin volver a parsear nada.
_CLAVES_LITERALES_EXISTENTES = {(archivo, _hash8(texto)) for archivo, _, texto, _ in LITERALES}


def _id_literal(archivo, lineno, nombre):
    base = f"{archivo}:{lineno}"
    return f"{base}:{nombre}" if nombre else base


def _parametros_literales(literales, deuda_hashes):
    parametros = []
    for archivo, lineno, texto, nombre in literales:
        marks = []
        if (archivo, _hash8(texto)) in deuda_hashes:
            marks.append(
                pytest.mark.xfail(
                    strict=True,
                    reason=f"Deuda conocida ({DEUDA_CONOCIDA[archivo]})",
                )
            )
        parametros.append(
            pytest.param((archivo, lineno, texto), marks=marks, id=_id_literal(archivo, lineno, nombre))
        )
    return parametros


def test_hay_archivos_para_auditar():
    """Guarda mínima del propio descubrimiento: si esto da 0, el walk
    está mal configurado y el resto de los tests de este archivo pasan
    en falso por falta de parámetros, no porque el repo esté limpio."""
    assert len(NOMBRES_RELATIVOS) > 20
    assert "evaluate.py" in NOMBRES_RELATIVOS
    assert not any(n.startswith("tests/") for n in NOMBRES_RELATIVOS)
    assert not any(n.startswith("landing/") for n in NOMBRES_RELATIVOS)
    assert not any(n.startswith("typeset/") for n in NOMBRES_RELATIVOS)
    # Subió de 13 a 14 a propósito: el system= de call_judge en
    # evaluate.py (línea 409) siempre estuvo contaminado en inglés, pero
    # con 169 caracteres quedaba por debajo de MIN_LITERAL_LEN=200 y el
    # guardia no lo veía. La Tarea 10 le agregó la instrucción de
    # escapado de comillas/saltos de línea para JSON (nada que ver con
    # traducir prompts) y quedó en 302 caracteres -- recién ahí cruzó el
    # umbral y el guardia lo descubrió por primera vez. Ver
    # docs/HALLAZGOS.md: el umbral de 200 puede estar ocultando otros
    # literales cortos contaminados que todavía no crecieron lo
    # suficiente como para ser vistos.
    assert len(LITERALES_JUEZ) == 14, (
        "cambió la cantidad de prompts largos en los archivos de juez -- "
        "revisar si DEUDA_CONOCIDA y los sets de hashes siguen alineados"
    )
    assert len(LITERALES_JUEZ_CON_RUBRICA) == 7, (
        "cambió la cantidad de constantes *_PROMPT con nombre en los "
        "archivos de juez -- revisar _DEUDA_ANCLA_HASHES"
    )


def test_registro_de_deuda_apunta_a_archivos_existentes():
    """Si un archivo del registro se borra o se mueve, la entrada de
    DEUDA_CONOCIDA debe notarse -- si no, deja de proteger nada y nadie
    se entera."""
    faltantes = set(DEUDA_CONOCIDA) - set(NOMBRES_RELATIVOS)
    assert not faltantes, f"DEUDA_CONOCIDA referencia archivos que ya no existen: {faltantes}"


def test_registro_de_hashes_sincronizado_con_deuda_conocida():
    """Todo archivo en DEUDA_CONOCIDA debe tener al menos una entrada
    registrada en alguno de los tres sets (si no, la entrada del archivo
    no protege nada), y ninguno de los tres sets debe mencionar un
    archivo que no está en DEUDA_CONOCIDA (si no, falta la razón/tarea)."""
    archivos_con_entrada = (
        {archivo for archivo, _ in _DEUDA_GENERO_HASHES}
        | {archivo for archivo, _ in _DEUDA_IDIOMA_HASHES}
        | {archivo for archivo, _ in _DEUDA_ANCLA_HASHES}
    )
    assert archivos_con_entrada == DEUDA_CONOCIDA.keys(), (
        "DEUDA_CONOCIDA y los sets de hashes se desincronizaron: "
        f"{set(DEUDA_CONOCIDA) ^ archivos_con_entrada}"
    )


def test_registro_sin_entradas_huerfanas():
    """Toda entrada (archivo, hash8) de los tres sets de deuda debe
    corresponder a algún literal que existe hoy en el repo. Si no
    coincide ninguno, el literal que esa entrada describía cambió --
    probablemente porque alguien lo tradujo -- y la entrada quedó
    apuntando a nada. Esto es justamente lo que debía pasar (es la señal
    de que hay que revisar el registro), pero tiene que fallar fuerte y
    explícito, no quedar como un xfail que ya no protege nada."""
    huerfanas = []
    for nombre_set, deuda_hashes in (
        ("_DEUDA_GENERO_HASHES", _DEUDA_GENERO_HASHES),
        ("_DEUDA_IDIOMA_HASHES", _DEUDA_IDIOMA_HASHES),
        ("_DEUDA_ANCLA_HASHES", _DEUDA_ANCLA_HASHES),
    ):
        for clave in deuda_hashes:
            if clave not in _CLAVES_LITERALES_EXISTENTES:
                huerfanas.append((nombre_set, clave))
    assert not huerfanas, (
        "entrada huérfana -- el literal cambió (probablemente se tradujo): "
        f"borrala del registro: {huerfanas}"
    )


@pytest.mark.parametrize("literal", _parametros_literales(LITERALES, _DEUDA_GENERO_HASHES))
def test_sin_contaminacion_de_genero(literal):
    archivo, lineno, texto = literal
    terminos = _terminos_genero(texto)
    assert not terminos, f"{archivo}:{lineno} calibra contra fantasía: {terminos}"


@pytest.mark.parametrize("literal", _parametros_literales(LITERALES, _DEUDA_IDIOMA_HASHES))
def test_sin_prosa_en_ingles(literal):
    archivo, lineno, texto = literal
    palabras = _palabras_ingles(texto)
    assert len(palabras) < MIN_PALABRAS_INGLES, (
        f"{archivo}:{lineno} tiene prosa en inglés: {sorted(palabras)}"
    )


@pytest.mark.parametrize("literal", _parametros_literales(LITERALES_JUEZ_CON_RUBRICA, _DEUDA_ANCLA_HASHES))
def test_prompt_de_juez_tiene_normas_del_castellano(literal):
    archivo, lineno, texto = literal
    assert ANCLA_NORMAS_CASTELLANO in texto.lower(), (
        f"{archivo}:{lineno}: el prompt no contiene la frase ancla "
        f"{ANCLA_NORMAS_CASTELLANO!r} del bloque de normas del castellano "
        "(ENCARGO_CLAUDE_CODE.md, sección 1b)"
    )
