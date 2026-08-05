"""
Tests de la agregación de overall_score en evaluate.py.

overall_score dejó de ser un campo que el juez inventa suelto en su JSON
(anclaba en 7.0 sin importar cómo puntuaran las dimensiones individuales
-- ver docs/HALLAZGOS.md, diagnóstico sobre Cap. 1/2/3). Ahora se calcula
en código a partir de las dimensiones que el juez sí puntuó: 70% la media
+ 30% el mínimo. Todo lo de acá es lógica pura (sin API, sin archivos).
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import evaluate as ev


def test_extraer_dimensiones_toma_solo_dicts_con_score_numerico():
    result = {
        "voice_adherence": {"score": 7, "note": "..."},
        "continuity": {"score": 6, "note": "..."},
        "three_weakest_sentences": ["a", "b", "c"],
        "ai_patterns_detected": ["patrón 1"],
        "weakest_dimension": "continuity",
        "new_canon_entries": [{"categoria": "x", "hecho": "y", "contradice": None}],
        "canon_compliance": {"score": 8, "violations": [], "note": "..."},
    }
    extraidas = ev.extraer_dimensiones(result)
    assert extraidas == {"voice_adherence": 7, "continuity": 6, "canon_compliance": 8}


def test_extraer_dimensiones_no_asume_nueve():
    """Si CHAPTER_PROMPT gana o pierde una dimensión, la extracción no
    debe romperse ni ignorar las de más -- no hay ningún nombre de
    dimensión hardcodeado."""
    result = {f"dim_{i}": {"score": i} for i in range(1, 13)}  # 12, no 9
    assert len(ev.extraer_dimensiones(result)) == 12


def test_extraer_dimensiones_ignora_score_no_numerico():
    result = {"weakest_dimension": {"score": "no aplica"}}
    assert ev.extraer_dimensiones(result) == {}


def test_calcular_overall_pondera_70_media_30_minimo():
    dimensiones = {"a": 7, "b": 7, "c": 6}
    # media = 6.6666..., mínimo = 6
    # 0.7 * 6.6666 + 0.3 * 6 = 4.6666 + 1.8 = 6.4666 -> 6.47
    assert ev.calcular_overall(dimensiones) == 6.47


def test_calcular_overall_reproduce_diagnostico_cap02():
    """Regresión: mismas 9 dimensiones del eval_log real del Cap. 2
    (docs/HALLAZGOS.md). Con la agregación vieja daba 7.0 sin importar
    que continuity fuera la más floja de las tres; con la nueva, ese
    mínimo pesa y el capítulo baja del umbral de 6.5."""
    dimensiones_ch02 = {
        "voice_adherence": 7, "beat_coverage": 7, "character_voice": 7,
        "plants_seeded": 7, "prose_quality": 7, "continuity": 6,
        "canon_compliance": 8, "lore_integration": 7, "engagement": 7,
    }
    assert ev.calcular_overall(dimensiones_ch02) == 6.7


def test_calcular_overall_reproduce_diagnostico_cap03():
    dimensiones_ch03 = {
        "voice_adherence": 7, "beat_coverage": 8, "character_voice": 7,
        "plants_seeded": 7, "prose_quality": 7, "continuity": 8,
        "canon_compliance": 9, "lore_integration": 8, "engagement": 7,
    }
    assert ev.calcular_overall(dimensiones_ch03) == 7.39


def test_calcular_overall_dimension_unica_floja_pesa_mas_que_en_un_promedio_simple():
    """El motivo de la fórmula: un promedio simple diluye una sola
    dimensión rota entre las demás; el mínimo ponderado no."""
    ocho_sietes_y_un_tres = {**{f"d{i}": 7 for i in range(8)}, "d8": 3}
    promedio_simple = sum(ocho_sietes_y_un_tres.values()) / len(ocho_sietes_y_un_tres)
    overall = ev.calcular_overall(ocho_sietes_y_un_tres)
    assert overall < promedio_simple


def test_chapter_prompt_ya_no_le_pide_overall_score_al_juez():
    """El juez puntúa dimensiones; overall_score lo agrega el código
    (evaluate_chapter), no lo inventa el LLM como campo suelto."""
    assert '"overall_score"' not in ev.CHAPTER_PROMPT


# ---------------------------------------------------------------------------
# _bloques_cache_chapter_prompt() -- cacheo de prompt. Parte el
# CHAPTER_PROMPT ya formateado en bloques {"text", "cache"} sin tocar la
# plantilla en sí (CHAPTER_PROMPT tiene su propio registro de contenido
# exacto en test_guardia_prompts.py y en test_chapter_prompt_tiene_
# frase_ancla_y_no_menciona_fantasy -- no se puede reescribir la
# plantilla para esto).
# ---------------------------------------------------------------------------

def _chapter_prompt_de_prueba(canon_emergente="EMERGENTE-XYZ"):
    return ev.CHAPTER_PROMPT.format(
        voice="VOZ-XYZ", world="MUNDO-XYZ", characters="PERSONAJES-XYZ",
        canon="CANON-XYZ", canon_emergente=canon_emergente,
        chapter_outline="ESQUEMA-CAP-XYZ", prev_chapter_tail="COLA-ANTERIOR-XYZ",
        chapter_text="TEXTO-DEL-CAPITULO-XYZ",
    )


def test_bloques_cache_chapter_prompt_devuelve_tres_bloques_con_cache_marcado():
    bloques = ev._bloques_cache_chapter_prompt(_chapter_prompt_de_prueba())
    assert len(bloques) == 3
    assert [b["cache"] for b in bloques] == [True, True, False]


def test_bloques_cache_chapter_prompt_bloque_estable_no_tiene_lo_variable():
    estable = ev._bloques_cache_chapter_prompt(_chapter_prompt_de_prueba())[0]["text"]
    assert "VOZ-XYZ" in estable
    assert "MUNDO-XYZ" in estable
    assert "PERSONAJES-XYZ" in estable
    assert "CANON-XYZ" in estable
    assert "EMERGENTE-XYZ" not in estable
    assert "ESQUEMA-CAP-XYZ" not in estable
    assert "TEXTO-DEL-CAPITULO-XYZ" not in estable


def test_bloques_cache_chapter_prompt_bloque_emergente_aislado():
    creciente = ev._bloques_cache_chapter_prompt(_chapter_prompt_de_prueba())[1]["text"]
    assert "EMERGENTE-XYZ" in creciente
    assert "MUNDO-XYZ" not in creciente
    assert "TEXTO-DEL-CAPITULO-XYZ" not in creciente


def test_bloques_cache_chapter_prompt_bloque_volatil_tiene_lo_del_capitulo():
    volatil = ev._bloques_cache_chapter_prompt(_chapter_prompt_de_prueba())[2]["text"]
    assert "ESQUEMA-CAP-XYZ" in volatil
    assert "COLA-ANTERIOR-XYZ" in volatil
    assert "TEXTO-DEL-CAPITULO-XYZ" in volatil
    assert "MUNDO-XYZ" not in volatil


def test_bloques_cache_chapter_prompt_solo_canon_emergente_distinto_no_toca_bloque_estable():
    # El punto entero del cacheo: que crezca canon_emergente entre
    # capítulos no debe tocar ni una letra del bloque estable.
    b1 = ev._bloques_cache_chapter_prompt(_chapter_prompt_de_prueba("EMERGENTE-CORTO"))
    b2 = ev._bloques_cache_chapter_prompt(_chapter_prompt_de_prueba("EMERGENTE-MUCHO-MAS-LARGO-CON-MAS-HECHOS"))
    assert b1[0]["text"] == b2[0]["text"]
    assert b1[1]["text"] != b2[1]["text"]


def test_bloques_cache_chapter_prompt_concatenado_reproduce_el_original():
    original = _chapter_prompt_de_prueba()
    bloques = ev._bloques_cache_chapter_prompt(original)
    assert "".join(b["text"] for b in bloques) == original


def test_bloques_cache_chapter_prompt_revienta_si_no_encuentra_las_anclas():
    with pytest.raises(ValueError):
        ev._bloques_cache_chapter_prompt("un prompt cualquiera sin las secciones esperadas")
