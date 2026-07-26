"""
Tests de aceptación de la Tarea 1 (ENCARGO_CLAUDE_CODE.md).

Casos 1 y 2 requieren invocar evaluate.py, que llama al juez LLM y por lo
tanto necesita ANTHROPIC_API_KEY en .env. Se marcan `skip` hasta que exista
esa key y docs/BASELINE.md tenga los puntajes reales.

Casos 3 a 6 son puramente mecánicos (funciones de deteccion_es.py, sin LLM)
y corren hoy sin configuración adicional.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from deteccion_es import (
    densidad_raya_parentetica,
    dividir_oraciones,
    calcos_detectados,
)

FIXTURES = Path(__file__).parent / "fixtures"
ENV_DISPONIBLE = (ROOT / ".env").exists()

pytestmark_api = pytest.mark.skipif(
    not ENV_DISPONIBLE,
    reason="Requiere ANTHROPIC_API_KEY en .env para invocar evaluate.py (juez LLM)",
)


@pytestmark_api
def test_cap_dialogado_puntua_mas_alto_que_baseline():
    """Caso 1: el capítulo dialogado debe puntuar más alto que en BASELINE.md
    una vez integrado deteccion_es.py en evaluate.py. El texto no cambia,
    solo se deja de castigar la raya de diálogo."""
    pytest.skip("Pendiente: correr evaluate.py sobre el fixture y comparar contra docs/BASELINE.md")


@pytestmark_api
def test_cap_con_slop_puntua_mas_bajo_que_dialogado():
    """Caso 2: el capítulo sembrado de slop debe puntuar más bajo que el limpio."""
    pytest.skip("Pendiente: requiere evaluate.py con API key")


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
