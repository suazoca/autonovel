"""
Test de aceptación de la Tarea 2 (ENCARGO_CLAUDE_CODE.md) para
draft_chapter.py: construir el prompt con un voz.md y un personajes.md
inventados (no los de la novela anterior) y verificar que el resultado
contiene el POV de prueba y ninguna referencia a "The Second Son of the
House of Bells".

El grep de aceptación (cass|bell|bronze|under-note) se corre por separado:
  grep -riE "cass|bell|bronze|under-note" draft_chapter.py gen_brief.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import draft_chapter as dc

PROHIBIDO = ["cass", "bell", "bronze", "under-note"]

VOZ_INVENTADA = """# Perfil de voz (prueba)

## Part 2: Voice Identity (generated per novel)

### POV and Tense
Primera persona, presente. Voz nerviosa, casi sin puntuación en los
momentos de pánico.

### Vocabulary Register
Vocabulario portuario: sal, brea, cabos, óxido. Nada de metáforas de
sonido ni de metal.

### Reglas específicas de capítulo
- Nunca nombrar el mar directamente, solo a través de los sentidos.
- Abrir siempre in medias res, nunca con clima.
"""

PERSONAJES_INVENTADOS = """# Characters

## Marina Fontán (POV)
- Role: farera
- Age: 41
- Speech pattern: frases cortas, jerga portuaria
"""

OUTLINE_INVENTADO = """# Outline

### Ch 1: La primera guardia
- Beat 1: Marina sube al faro de noche.
- Beat 2: encuentra la lámpara apagada.

### Ch 2: El barco fantasma
- Beat 1: aparece una luz en el horizonte.
"""

STATE_INVENTADO = {"titulo": "El Faro de Sal"}


def _build(chapter_num=1):
    return dc.build_prompt(
        chapter_num, STATE_INVENTADO, VOZ_INVENTADA, "", PERSONAJES_INVENTADOS,
        OUTLINE_INVENTADO, "",
    )


def test_build_prompt_incluye_canon_y_canon_emergente_con_encabezados_distintos():
    prompt = dc.build_prompt(
        1, STATE_INVENTADO, VOZ_INVENTADA, "", PERSONAJES_INVENTADOS,
        OUTLINE_INVENTADO, "HECHO-DE-FUNDACION", "HECHO-EMERGENTE-CAP-ANTERIOR",
    )
    assert "HECHO-DE-FUNDACION" in prompt
    assert "HECHO-EMERGENTE-CAP-ANTERIOR" in prompt
    assert prompt.index("CANON EMERGENTE") > prompt.index("CANON (hechos duros de fundación")


def test_build_prompt_canon_emergente_default_vacio():
    # Compatibilidad: llamadas viejas con 7 argumentos posicionales
    # (sin canon_emergente) no deben romper.
    prompt = dc.build_prompt(
        1, STATE_INVENTADO, VOZ_INVENTADA, "", PERSONAJES_INVENTADOS,
        OUTLINE_INVENTADO, "HECHO-DE-FUNDACION",
    )
    assert "HECHO-DE-FUNDACION" in prompt


def test_build_prompt_no_referencia_novela_anterior():
    prompt_lower = _build().lower()
    for termino in PROHIBIDO:
        assert termino not in prompt_lower, f"'{termino}' apareció en el prompt"


def test_build_prompt_contiene_pov_y_titulo_de_prueba():
    prompt = _build()
    assert "Marina Fontán" in prompt
    assert "El Faro de Sal" in prompt
    assert "Vocabulario portuario" in prompt
    assert "Nunca nombrar el mar directamente" in prompt


def test_build_prompt_usa_calibracion_no_hardcodeado():
    prompt = _build()
    assert f"~{dc.CALIBRACION['palabras_objetivo_capitulo']} palabras" in prompt


def test_ultimos_finales_vacio_sin_capitulos_previos(tmp_path, monkeypatch):
    monkeypatch.setattr(dc, "CHAPTERS_DIR", tmp_path)
    assert dc.ultimos_finales(n=3) == []


def test_ultimos_finales_extrae_parrafo_final(tmp_path, monkeypatch):
    monkeypatch.setattr(dc, "CHAPTERS_DIR", tmp_path)
    (tmp_path / "ch_01.md").write_text(
        "Primer párrafo.\n\nÚltimo párrafo del capítulo uno."
    )
    (tmp_path / "ch_02.md").write_text(
        "Otro inicio.\n\nÚltimo párrafo del capítulo dos."
    )
    finales = dc.ultimos_finales(n=3)
    assert finales == [
        "Último párrafo del capítulo uno.",
        "Último párrafo del capítulo dos.",
    ]


def test_build_prompt_incluye_prohibicion_final_cuando_hay_capitulos(tmp_path, monkeypatch):
    monkeypatch.setattr(dc, "CHAPTERS_DIR", tmp_path)
    (tmp_path / "ch_01.md").write_text(
        "Inicio.\n\nY se quedó mirando el mar hasta que oscureció del todo."
    )
    prompt = _build(chapter_num=2)
    assert "No repitas la forma de estos finales" in prompt
    assert "se quedó mirando el mar" in prompt


def test_ruta_bilingue_prefiere_nombre_en_espanol(tmp_path, monkeypatch):
    monkeypatch.setattr(dc, "BASE_DIR", tmp_path)
    (tmp_path / "voz.md").write_text("contenido en español", encoding="utf-8")
    (tmp_path / "voice.md").write_text("contenido en inglés", encoding="utf-8")
    assert dc.load_file_bilingue("voz.md", "voice.md") == "contenido en español"


def test_ruta_bilingue_cae_al_ingles_si_no_hay_espanol(tmp_path, monkeypatch):
    monkeypatch.setattr(dc, "BASE_DIR", tmp_path)
    (tmp_path / "voice.md").write_text("contenido en inglés", encoding="utf-8")
    assert dc.load_file_bilingue("voz.md", "voice.md") == "contenido en inglés"


def test_ruta_bilingue_vacio_si_no_existe_ninguno(tmp_path, monkeypatch):
    monkeypatch.setattr(dc, "BASE_DIR", tmp_path)
    assert dc.load_file_bilingue("voz.md", "voice.md") == ""


def test_build_prompt_usa_titulo_en_espanol():
    prompt = dc.build_prompt(
        1, {"titulo": "El Faro de Sal"}, VOZ_INVENTADA, "", PERSONAJES_INVENTADOS,
        OUTLINE_INVENTADO, "",
    )
    assert "El Faro de Sal" in prompt


def test_build_prompt_cae_a_title_si_no_hay_titulo(monkeypatch):
    """Compatibilidad: state.json viejo con clave 'title' (inglés) en vez
    de 'titulo' no debe romper ni perder el título."""
    prompt = dc.build_prompt(
        1, {"title": "The Salt Lighthouse"}, VOZ_INVENTADA, "", PERSONAJES_INVENTADOS,
        OUTLINE_INVENTADO, "",
    )
    assert "The Salt Lighthouse" in prompt


def test_extraer_reglas_capitulo_acepta_encabezado_en_ingles_legado():
    """El parser debe seguir aceptando 'Chapter-Specific Rules' (nombre
    viejo, en inglés) además de 'Reglas específicas de capítulo'."""
    voz_legado = VOZ_INVENTADA.replace(
        "### Reglas específicas de capítulo", "### Chapter-Specific Rules"
    )
    reglas = dc.extraer_reglas_capitulo(voz_legado)
    assert any("Nunca nombrar el mar directamente" in r for r in reglas)


# ---------------------------------------------------------------------------
# Tarea 9: verificación de longitud del capítulo guardado contra el
# objetivo de palabras del esquema.
# ---------------------------------------------------------------------------

ENTRADA_ESQUEMA_REAL = """### Ch 5: El óstracon
- **POV:** Vidal
- **Location:** Jerusalén
- **~Word count target:** 2000
"""


def test_extraer_word_count_objetivo_formato_real():
    assert dc.extraer_word_count_objetivo(ENTRADA_ESQUEMA_REAL) == 2000


def test_extraer_word_count_objetivo_con_coma_de_miles():
    entrada = "- **~Word count target:** 2,000"
    assert dc.extraer_word_count_objetivo(entrada) == 2000


def test_extraer_word_count_objetivo_sin_tilde_ni_negrita():
    entrada = "Word count target: 1800 words"
    assert dc.extraer_word_count_objetivo(entrada) == 1800


def test_extraer_word_count_objetivo_none_si_no_esta_el_campo():
    entrada = "### Ch 5: El óstracon\n- **POV:** Vidal\n"
    assert dc.extraer_word_count_objetivo(entrada) is None


def test_capitulo_demasiado_corto_por_debajo_del_umbral():
    # 900 / 2000 = 45% < 70%
    assert dc.capitulo_demasiado_corto(900, 2000) is True


def test_capitulo_demasiado_corto_justo_en_el_umbral_no_marca():
    # Exactamente el 70% no es "por debajo" -- el corte es estricto (<).
    assert dc.capitulo_demasiado_corto(1400, 2000) is False


def test_capitulo_demasiado_corto_por_encima_del_umbral_pasa():
    assert dc.capitulo_demasiado_corto(1950, 2000) is False


def test_capitulo_demasiado_corto_sin_objetivo_nunca_marca():
    # None u 0 -- sin nada contra qué comparar, no bloquea el guardado.
    assert dc.capitulo_demasiado_corto(50, None) is False
    assert dc.capitulo_demasiado_corto(50, 0) is False


# ---------------------------------------------------------------------------
# build_prompt_bloques() -- cacheo de prompt. Mismas piezas que
# build_prompt(), reordenadas en bloques {"text", "cache"} para que
# api_comun.llamar_api() arme content blocks con cache_control en el
# prefijo estable. Ver docstring de la función para el porqué del orden.
# ---------------------------------------------------------------------------

MUNDO_INVENTADO = "MUNDO-DE-PRUEBA-XYZ"
CANON_INVENTADO = "HECHO-DE-FUNDACION-XYZ"
CANON_EMERGENTE_INVENTADO = "HECHO-EMERGENTE-XYZ"


def _build_bloques(chapter_num=1):
    return dc.build_prompt_bloques(
        chapter_num, STATE_INVENTADO, VOZ_INVENTADA, MUNDO_INVENTADO,
        PERSONAJES_INVENTADOS, OUTLINE_INVENTADO, CANON_INVENTADO,
        CANON_EMERGENTE_INVENTADO,
    )


def test_build_prompt_bloques_devuelve_tres_bloques_con_cache_marcado():
    bloques = _build_bloques()
    assert len(bloques) == 3
    assert [b["cache"] for b in bloques] == [True, True, False]


def test_build_prompt_bloques_bloque_estable_tiene_voz_mundo_personajes_canon():
    estable = _build_bloques()[0]["text"]
    assert "Marina Fontán" in estable  # personajes
    assert MUNDO_INVENTADO in estable
    assert CANON_INVENTADO in estable
    assert "Vocabulario portuario" in estable  # voz

    # Lo que cambia por capítulo NO debe estar en el bloque cacheado --
    # si estuviera, cada capítulo invalidaría el cache del bloque entero.
    assert CANON_EMERGENTE_INVENTADO not in estable
    assert "La primera guardia" not in estable  # esquema de este capítulo
    assert "Capítulo 1" not in estable


def test_build_prompt_bloques_bloque_canon_emergente_aislado():
    creciente = _build_bloques()[1]["text"]
    assert CANON_EMERGENTE_INVENTADO in creciente
    assert MUNDO_INVENTADO not in creciente
    assert "La primera guardia" not in creciente


def test_build_prompt_bloques_bloque_volatil_tiene_lo_especifico_del_capitulo():
    volatil = _build_bloques()[2]["text"]
    assert "Capítulo 1" in volatil
    assert "La primera guardia" in volatil  # esquema de este capítulo
    assert MUNDO_INVENTADO not in volatil
    assert CANON_INVENTADO not in volatil
    assert CANON_EMERGENTE_INVENTADO not in volatil


def test_build_prompt_bloques_capitulo_distinto_solo_cambia_bloque_volatil():
    # El punto entero del cacheo: reordenar el número de capítulo no debe
    # tocar ni una letra de los bloques 0 y 1.
    b1 = _build_bloques(chapter_num=1)
    b2 = _build_bloques(chapter_num=2)
    assert b1[0]["text"] == b2[0]["text"]
    assert b1[1]["text"] == b2[1]["text"]
    assert b1[2]["text"] != b2[2]["text"]


def test_build_prompt_bloques_concatenado_no_pierde_contenido_de_build_prompt():
    # No es el mismo string (build_prompt_bloques reordena para cacheo),
    # pero no debe faltar nada de lo que build_prompt() incluye.
    prompt_plano = dc.build_prompt(
        1, STATE_INVENTADO, VOZ_INVENTADA, MUNDO_INVENTADO, PERSONAJES_INVENTADOS,
        OUTLINE_INVENTADO, CANON_INVENTADO, CANON_EMERGENTE_INVENTADO,
    )
    concatenado = "".join(b["text"] for b in _build_bloques())
    for fragmento in [MUNDO_INVENTADO, CANON_INVENTADO, CANON_EMERGENTE_INVENTADO,
                      "Marina Fontán", "La primera guardia", "Capítulo 1"]:
        assert fragmento in prompt_plano
        assert fragmento in concatenado
