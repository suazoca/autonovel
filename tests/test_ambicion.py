"""
Test de aceptación de la Tarea 3 (ENCARGO_CLAUDE_CODE.md): campo de
ambición por capítulo (pico | sosten | valle) con umbral propio en vez de
un umbral único (6.0) para toda la novela.

Todo lo probado acá es lógica pura (parsing + comparación de umbrales), no
requiere llamar al juez LLM ni ANTHROPIC_API_KEY.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import evaluate as ev
import run_pipeline as rp


def test_extraer_ambicion_pico():
    assert ev.extraer_ambicion("- **Ambición:** pico\n- otros datos") == "pico"


def test_extraer_ambicion_sosten_con_acento():
    assert ev.extraer_ambicion("ambicion: sostén") == "sosten"


def test_extraer_ambicion_valle_estilo_yaml():
    assert ev.extraer_ambicion("ambicion: valle") == "valle"


def test_extraer_ambicion_ausente_devuelve_none():
    assert ev.extraer_ambicion("### Ch 3: capítulo sin ese campo") is None


def test_umbral_por_ambicion():
    assert ev.umbral_por_ambicion("pico") == 7.5
    assert ev.umbral_por_ambicion("sosten") == 6.5
    assert ev.umbral_por_ambicion("valle") == 6.0
    # Sin ambición declarada: "sosten" (6.5), NUNCA "valle" (6.0, el más
    # laxo) -- si el default fuera el umbral más flojo, cualquier esquema
    # que no declare ambición volvería en silencio al comportamiento viejo.
    assert ev.umbral_por_ambicion(None) == 6.5
    assert ev.umbral_por_ambicion(None) == ev.UMBRAL_POR_DEFECTO_SIN_AMBICION


def test_capitulo_pico_que_puntua_7_0_es_rechazado():
    """Caso de aceptación de la Tarea 3, primera mitad."""
    ambicion = ev.extraer_ambicion("- **Ambición:** pico")
    umbral = ev.umbral_por_ambicion(ambicion)
    overall_score = 7.0
    assert (overall_score >= umbral) is False


def test_mismo_capitulo_marcado_valle_es_aceptado():
    """Caso de aceptación de la Tarea 3, segunda mitad -- mismo score."""
    ambicion = ev.extraer_ambicion("- **Ambición:** valle")
    umbral = ev.umbral_por_ambicion(ambicion)
    overall_score = 7.0
    assert (overall_score >= umbral) is True


ESQUEMA_SIN_PICOS = """
### Ch 1: Uno
- **Ambición:** sosten

### Ch 2: Dos
- **Ambición:** sosten

### Ch 3: Tres
- **Ambición:** valle
"""

ESQUEMA_CON_PICOS_SUFICIENTES = """
### Ch 1: Uno
- **Ambición:** pico

### Ch 2: Dos
- **Ambición:** sosten

### Ch 3: Tres
- **Ambición:** sosten

### Ch 4: Cuatro
- **Ambición:** sosten

### Ch 5: Cinco
- **Ambición:** sosten

### Ch 6: Seis
- **Ambición:** valle
"""


def test_validar_diversidad_esquema_sin_picos_advierte():
    """Caso de aceptación de la Tarea 3, tercera parte."""
    advertencia = ev.validar_diversidad_ambicion(ESQUEMA_SIN_PICOS)
    assert advertencia is not None
    assert "pico" in advertencia.lower()


def test_validar_diversidad_esquema_con_picos_suficientes_no_advierte():
    # 1/6 = 16.7% >= 15%
    advertencia = ev.validar_diversidad_ambicion(ESQUEMA_CON_PICOS_SUFICIENTES)
    assert advertencia is None


def test_validar_diversidad_sin_ninguna_ambicion_declarada_advierte():
    advertencia = ev.validar_diversidad_ambicion(
        "### Ch 1: sin campo\n### Ch 2: tampoco"
    )
    assert advertencia is not None


ESQUEMA_PICOS_CONCENTRADOS_AL_FINAL = """
### Ch 1: Uno
- **Ambición:** sosten

### Ch 2: Dos
- **Ambición:** sosten

### Ch 3: Tres
- **Ambición:** sosten

### Ch 4: Cuatro
- **Ambición:** sosten

### Ch 5: Cinco
- **Ambición:** sosten

### Ch 6: Seis
- **Ambición:** sosten

### Ch 7: Siete
- **Ambición:** sosten

### Ch 8: Ocho
- **Ambición:** pico

### Ch 9: Nueve
- **Ambición:** pico

### Ch 10: Diez
- **Ambición:** pico
"""


def test_validar_diversidad_picos_concentrados_al_final_advierte():
    """Caso de aceptación de la Tarea 3, cuarta parte: 3/10 = 30% de picos
    (bien por encima del 15% mínimo -- la proporción total no es el
    problema), pero los 3 están en el último tercio (Ch 8-10 de 10)."""
    advertencia = ev.validar_diversidad_ambicion(ESQUEMA_PICOS_CONCENTRADOS_AL_FINAL)
    assert advertencia is not None
    assert "distribu" in advertencia.lower() or "concentrad" in advertencia.lower()
    # La proporción total está bien -- no debería quejarse de "esquema plano"
    assert "esquema plano" not in advertencia.lower()


def test_validar_diversidad_picos_bien_repartidos_no_advierte_distribucion():
    """Los picos de ESQUEMA_CON_PICOS_SUFICIENTES (Ch 1 de 6) no caen en
    el último tercio -- no debería dispararse la advertencia de
    distribución (ya cubierto por el test de "no advierte" de arriba, este
    lo hace explícito)."""
    advertencia = ev.validar_diversidad_ambicion(ESQUEMA_CON_PICOS_SUFICIENTES)
    assert advertencia is None


def test_run_pipeline_lee_umbral_aceptacion_del_stdout_de_evaluate():
    """run_pipeline.py ya no usa CHAPTER_THRESHOLD fijo -- lee el umbral
    por capítulo que evaluate.py calcula e imprime."""
    stdout = "---\noverall_score: 7.0\numbral_aceptacion: 7.5\nambicion: pico\n"
    assert rp.parse_score(stdout, "umbral_aceptacion") == 7.5


def test_run_pipeline_detecta_ausencia_de_umbral_para_el_fallback():
    """Si evaluate.py no llegó a calcular el umbral (p.ej. capítulo vacío),
    parse_score devuelve -1.0 (su valor de 'no encontrado'), que es lo que
    run_drafting() usa como señal para caer a CHAPTER_THRESHOLD."""
    stdout = "---\noverall_score: 0.0\nerror: Chapter 3 is empty or missing\n"
    umbral = rp.parse_score(stdout, "umbral_aceptacion")
    assert umbral < 0
