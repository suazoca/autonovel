"""
Tests de aceptación de la Tarea 1 (ENCARGO_CLAUDE_CODE.md).

Casos 1 y 2 se verifican contra slop_score() (evaluate.py) directamente,
sin pasar por el juez LLM -- eso es lo que permite --solo-mecanico: son
deterministas y no gastan API. El juicio LLM (overall_score completo,
--chapter sin --solo-mecanico) sigue pendiente de ANTHROPIC_API_KEY, pero
ya no bloquea estos dos casos.

Casos 3 a 6 son puramente mecánicos (funciones de deteccion_es.py, sin LLM)
y corren hoy sin configuración adicional.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from deteccion_es import (
    densidad_raya_parentetica,
    dividir_oraciones,
    calcos_detectados,
)
from evaluate import slop_score

FIXTURES = Path(__file__).parent / "fixtures"

# Penalización de cap_dialogado_es.md ANTES de integrar deteccion_es.py en
# slop_score() (commit 625fc7f, constantes en inglés). Ver docs/BASELINE.md.
PENALTY_DIALOGADO_ANTES = 1.0


def test_cap_dialogado_puntua_mas_alto_que_baseline():
    """Caso 1: el capítulo dialogado debe puntuar más alto (= menos
    penalización) que antes de integrar deteccion_es.py. El texto no
    cambia, solo se deja de castigar la raya de diálogo."""
    texto = (FIXTURES / "cap_dialogado_es.md").read_text()
    resultado = slop_score(texto)
    assert resultado["slop_penalty"] < PENALTY_DIALOGADO_ANTES
    assert resultado["em_dash_density"] < 6.0  # bajo el umbral ES, no el 15 en inglés


def test_cap_con_slop_puntua_mas_bajo_que_dialogado():
    """Caso 2: el capítulo sembrado de slop debe puntuar más bajo (= más
    penalización) que el limpio."""
    limpio = slop_score((FIXTURES / "cap_dialogado_es.md").read_text())
    sembrado = slop_score((FIXTURES / "cap_con_slop_es.md").read_text())
    assert sembrado["slop_penalty"] > limpio["slop_penalty"]


def test_regresion_no_invertir_penalizacion_dialogo_vs_slop():
    """Guarda de regresión, no caso de aceptación: el bug original era que
    un capítulo de diálogo LIMPIO salía peor puntuado que uno con slop
    sembrado a propósito (docs/BASELINE.md, tabla "ANTES": 1.0 vs 0.0).
    Este test fija la RELACIÓN -- no los valores absolutos -- para que si
    alguien en el futuro toca CALIBRACION, reintroduce el conteo crudo de
    rayas, o afloja algún umbral, la suite falle en vez de dejar que la
    inversión vuelva a pasar en silencio."""
    limpio = slop_score((FIXTURES / "cap_dialogado_es.md").read_text())
    sembrado = slop_score((FIXTURES / "cap_con_slop_es.md").read_text())
    assert limpio["slop_penalty"] < sembrado["slop_penalty"], (
        f"Se invirtió la relación: el capítulo limpio "
        f"(penalización={limpio['slop_penalty']}) salió igual o peor que "
        f"el sembrado (penalización={sembrado['slop_penalty']}). "
        f"Ese es el bug original de la Tarea 1."
    )


def test_densidad_raya_dialogo_limpio_es_cero():
    """Caso 3: 40 líneas de diálogo con raya -> densidad 0.0 (todas exentas)."""
    dialogo = "\n".join(
        f"—Línea de diálogo número {i}, con contenido variado y natural."
        for i in range(40)
    )
    assert densidad_raya_parentetica(dialogo) == 0.0


def test_densidad_raya_incisos_abusivos_supera_50():
    """Caso 4: prosa narrativa con incisos parentéticos abusivos -> densidad > 50."""
    prosa = (
        "Ella caminó — despacio, casi sin ganas — hasta la puerta — la misma "
        "de siempre — y se detuvo — como tantas otras veces — antes de "
        "girar la llave — vieja y pesada — en la cerradura."
    ) * 3
    assert densidad_raya_parentetica(prosa) > 50


def test_calcos_detectados_encuentra_al_menos_dos():
    """Caso 5. calcos_detectados() debe ser insensible a mayúsculas: el mismo
    calco vale al inicio de oración (mayúscula) que en medio de ella."""
    hallazgos = calcos_detectados("Levantó su mano. Estaba siendo observada.")
    assert len(hallazgos) >= 2


def test_dividir_oraciones_no_corta_en_abreviatura():
    """Caso 6 (corregido). El original ("¿Viniste? Sí. El Sr. Pérez no
    vino.") estaba mal escrito: dividir_oraciones() descarta por diseño las
    oraciones de <=2 palabras (ver docs/HALLAZGOS.md), así que "¿Viniste?"
    y "Sí." nunca iban a contar como oraciones propias, sin que eso sea un
    bug. Lo que hay que verificar es que "Sr." no corte la oración -- no el
    conteo total."""
    oraciones = dividir_oraciones(
        "El Sr. Pérez no vino a la reunión. ¿Sabés por qué faltó?"
    )
    assert len(oraciones) == 2
    # si hubiera cortado en "Sr." la primera oración terminaría ahí,
    # en vez de seguir hasta "reunión."
    assert oraciones[0] == "El Sr. Pérez no vino a la reunión."
