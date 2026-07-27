"""
Test de aceptación de la Tarea 4 (ENCARGO_CLAUDE_CODE.md): alcance de
siembra para series ("libro" | "serie"), con las 4 reglas de validación
de la tabla del encargo más el test de regresión (novela suelta sin
siembras_serie.md se comporta exactamente como antes del cambio).

Todo lo probado acá es lógica pura sobre dicts, no requiere API ni
parsear outline.md real (ver nota de alcance en evaluate.py).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import evaluate as ev


def entrada(alcance, siembra_libro=1, pago_libro=None, ident="hilo-1"):
    return {
        "id": ident,
        "siembra": {"libro": siembra_libro, "capitulo": 3},
        "pago": {"libro": pago_libro, "capitulo": 14} if pago_libro is not None else None,
        "alcance": alcance,
        "estado": "pendiente",
    }


# --- Los 4 casos de la tabla del encargo, con alcance de serie disponible ---

def test_caso_1_alcance_libro_sin_pago_en_el_volumen_es_error():
    e = entrada("libro", siembra_libro=1, pago_libro=None)
    error = ev.validar_siembra(e, alcance_serie_disponible_=True)
    assert error is not None
    assert "libro" in error.lower()


def test_caso_1b_alcance_libro_pago_en_otro_libro_tambien_es_error():
    """'sin pago en el volumen' también cubre pago asignado a OTRO libro,
    no solo pago ausente."""
    e = entrada("libro", siembra_libro=1, pago_libro=2)
    error = ev.validar_siembra(e, alcance_serie_disponible_=True)
    assert error is not None


def test_caso_2_alcance_serie_sin_pago_en_el_volumen_con_libro_asignado_es_ok():
    e = entrada("serie", siembra_libro=1, pago_libro=2)
    error = ev.validar_siembra(e, alcance_serie_disponible_=True)
    assert error is None


def test_caso_3_alcance_serie_sin_libro_de_pago_asignado_es_error():
    e = entrada("serie", siembra_libro=1, pago_libro=None)
    error = ev.validar_siembra(e, alcance_serie_disponible_=True)
    assert error is not None
    assert "sin libro de pago" in error.lower()


def test_caso_4_alcance_serie_pago_a_libro_ya_publicado_es_error():
    e = entrada("serie", siembra_libro=1, pago_libro=2)
    error = ev.validar_siembra(
        e, alcance_serie_disponible_=True, libros_completos={2}
    )
    assert error is not None
    assert "ya publicado" in error.lower()


def test_caso_4b_alcance_serie_pago_a_libro_no_publicado_es_ok():
    """Mismo caso que el 4, pero el libro de pago NO está en la lista de
    completos -- no debe dar error."""
    e = entrada("serie", siembra_libro=1, pago_libro=2)
    error = ev.validar_siembra(
        e, alcance_serie_disponible_=True, libros_completos={1}
    )
    assert error is None


# --- Regresión: novela suelta sin siembras_serie.md ---

def test_regresion_sin_siembras_serie_alcance_serie_se_trata_como_libro():
    """Sin siembras_serie.md (alcance_serie_disponible_=False), una entrada
    que declara alcance "serie" debe validarse IGUAL que si dijera "libro"
    -- comportamiento idéntico al de antes de la Tarea 4."""
    e_pagada_en_el_volumen = entrada("serie", siembra_libro=1, pago_libro=1)
    assert ev.validar_siembra(e_pagada_en_el_volumen, alcance_serie_disponible_=False) is None

    e_pago_en_otro_libro = entrada("serie", siembra_libro=1, pago_libro=2)
    error = ev.validar_siembra(e_pago_en_otro_libro, alcance_serie_disponible_=False)
    assert error is not None, (
        "Sin siembras_serie.md, un pago fuera del volumen debe seguir "
        "siendo un error aunque la entrada declare alcance 'serie'."
    )


def test_regresion_novela_suelta_alcance_libro_normal_sigue_igual():
    """Caso base sin ningún cambio de comportamiento: alcance 'libro'
    pagado dentro del volumen, sin siembras_serie.md -- sigue OK."""
    e = entrada("libro", siembra_libro=1, pago_libro=1)
    assert ev.validar_siembra(e, alcance_serie_disponible_=False) is None


# --- alcance_serie_disponible() / SIEMBRAS_SERIE_PATH ---

def test_alcance_serie_disponible_false_sin_archivo(tmp_path, monkeypatch):
    monkeypatch.setattr(ev, "SIEMBRAS_SERIE_PATH", tmp_path / "siembras_serie.md")
    assert ev.alcance_serie_disponible() is False


def test_alcance_serie_disponible_true_con_archivo(tmp_path, monkeypatch):
    ruta = tmp_path / "siembras_serie.md"
    ruta.write_text("# Siembras de serie\n", encoding="utf-8")
    monkeypatch.setattr(ev, "SIEMBRAS_SERIE_PATH", ruta)
    assert ev.alcance_serie_disponible() is True


# --- validar_libro_de_siembras() (batch) ---

def test_validar_libro_de_siembras_agrega_errores(tmp_path, monkeypatch):
    ruta = tmp_path / "siembras_serie.md"
    ruta.write_text("# Siembras de serie\n", encoding="utf-8")
    monkeypatch.setattr(ev, "SIEMBRAS_SERIE_PATH", ruta)

    entradas = [
        entrada("libro", siembra_libro=1, pago_libro=1, ident="ok-1"),
        entrada("libro", siembra_libro=1, pago_libro=None, ident="mal-1"),
        entrada("serie", siembra_libro=1, pago_libro=2, ident="ok-2"),
        entrada("serie", siembra_libro=1, pago_libro=None, ident="mal-2"),
    ]
    errores = ev.validar_libro_de_siembras(entradas)
    assert len(errores) == 2
    assert any("mal-1" in e for e in errores)
    assert any("mal-2" in e for e in errores)


def test_validar_libro_de_siembras_vacio_sin_siembras_serie(tmp_path, monkeypatch):
    monkeypatch.setattr(ev, "SIEMBRAS_SERIE_PATH", tmp_path / "no-existe.md")
    entradas = [entrada("libro", siembra_libro=1, pago_libro=1, ident="ok-1")]
    assert ev.validar_libro_de_siembras(entradas) == []
