"""
Test de aceptación para gen_voice.py (generador de voz que faltaba, ver
docs/HALLAZGOS.md hallazgo 7). Nada de esto llama a la API ni requiere
ANTHROPIC_API_KEY: call_writer() se parchea siempre, o se verifica que no
se invoque (idempotencia).
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import gen_voice


# ---------------------------------------------------------------------------
# Import no llama a la API
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _httpx_post_rompe_si_se_llama(monkeypatch):
    import httpx

    def _rompe(*args, **kwargs):
        raise AssertionError("httpx.post fue invocado -- no debería pasar en estos tests")

    monkeypatch.setattr(httpx, "post", _rompe)


def test_import_no_llama_api():
    import gen_voice  # noqa: F401 -- solo importar


# ---------------------------------------------------------------------------
# parsear_secciones()
# ---------------------------------------------------------------------------

RESPUESTA_MODELO = """Un poco de texto libre antes, que debería ignorarse.

###TONO###
Seco, casi notarial.

###RITMO###
Oraciones cortas para la tensión, largas para la descripción.

###VOCABULARIO###
Vocabulario portuario: sal, brea, cabos, óxido.

###POV_TIEMPO###
Primera persona, presente.

###DIALOGO###
Solo "dijo", sin adverbios de manera.

###EJEMPLARES###
—No vino nadie —dijo ella.

—¿Estás segura? —Rut cerró la carpeta.

###ANTIEJEMPLARES###
Demasiado florido para este tono: nada de "un manto de niebla dorada".
"""


def test_parsear_secciones_encuentra_las_siete():
    secciones = gen_voice.parsear_secciones(RESPUESTA_MODELO)
    assert set(secciones.keys()) == {
        "TONO", "RITMO", "VOCABULARIO", "POV_TIEMPO",
        "DIALOGO", "EJEMPLARES", "ANTIEJEMPLARES",
    }
    assert secciones["TONO"] == "Seco, casi notarial."
    assert "No vino nadie" in secciones["EJEMPLARES"]


# ---------------------------------------------------------------------------
# llenar_parte2()
# ---------------------------------------------------------------------------

VOZ_TEMPLATE = """# Voice Profile

## Part 1: Guardrails (permanent, all novels)

### Tier 1: Banned words -- kill on sight

delve, utilize, tapestry

---

## Part 2: Voice Identity (generated per novel)

### Tone
<!-- Generated during foundation. -->

### Sentence Rhythm
<!-- Generated during foundation. -->

### Vocabulary Register
<!-- Generated during foundation. -->

### POV and Tense
<!-- Generated during foundation. -->

### Dialogue Conventions
<!-- Generated during foundation. -->

### Reglas específicas de capítulo
<!-- Opcional. Dejar vacío si no aplica ninguna. -->

### Exemplar Passages
<!-- 3-5 paragraphs. -->

### Anti-Exemplars
<!-- 3-5 paragraphs. -->
"""


def test_llenar_parte2_no_toca_parte1():
    secciones = gen_voice.parsear_secciones(RESPUESTA_MODELO)
    resultado = gen_voice.llenar_parte2(VOZ_TEMPLATE, secciones)
    assert "delve, utilize, tapestry" in resultado
    assert "### Tier 1: Banned words -- kill on sight" in resultado


def test_llenar_parte2_llena_las_siete_secciones():
    secciones = gen_voice.parsear_secciones(RESPUESTA_MODELO)
    resultado = gen_voice.llenar_parte2(VOZ_TEMPLATE, secciones)
    assert "Seco, casi notarial." in resultado
    assert "Vocabulario portuario" in resultado
    assert "No vino nadie" in resultado
    assert "Demasiado florido" in resultado
    assert "<!-- Generated during foundation. -->" not in resultado


def test_llenar_parte2_no_toca_reglas_especificas_de_capitulo():
    """Sección opcional -- gen_voice.py no la llena, aunque esté vacía."""
    secciones = gen_voice.parsear_secciones(RESPUESTA_MODELO)
    resultado = gen_voice.llenar_parte2(VOZ_TEMPLATE, secciones)
    assert "<!-- Opcional. Dejar vacío si no aplica ninguna. -->" in resultado


def test_llenar_parte2_no_pisa_seccion_ya_llena():
    voz_a_medias = VOZ_TEMPLATE.replace(
        "### Tone\n<!-- Generated during foundation. -->",
        "### Tone\nYa decidido de antes, no tocar.",
    )
    secciones = gen_voice.parsear_secciones(RESPUESTA_MODELO)
    resultado = gen_voice.llenar_parte2(voz_a_medias, secciones)
    assert "Ya decidido de antes, no tocar." in resultado
    assert "Seco, casi notarial." not in resultado  # no se sobreescribió


# ---------------------------------------------------------------------------
# main(): guard de semilla, idempotencia, resolución bilingüe, Parte 1 intacta
# ---------------------------------------------------------------------------

def _preparar_entradas(tmp_path, voz_texto=VOZ_TEMPLATE):
    (tmp_path / "seed.txt").write_text("Una farera hereda un faro.", encoding="utf-8")
    (tmp_path / "voice.md").write_text(voz_texto, encoding="utf-8")
    (tmp_path / "CRAFT.md").write_text("# Craft\n", encoding="utf-8")


def test_main_sale_si_semilla_vacia(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_voice, "BASE_DIR", tmp_path)
    (tmp_path / "seed.txt").write_text("", encoding="utf-8")
    (tmp_path / "voice.md").write_text(VOZ_TEMPLATE, encoding="utf-8")

    with pytest.raises(SystemExit):
        gen_voice.main()


def test_main_llena_voice_md(tmp_path, monkeypatch):
    _preparar_entradas(tmp_path)
    monkeypatch.setattr(gen_voice, "BASE_DIR", tmp_path)
    monkeypatch.setattr(gen_voice, "call_writer", lambda prompt, **kw: RESPUESTA_MODELO)

    gen_voice.main()

    resultado = (tmp_path / "voice.md").read_text(encoding="utf-8")
    assert "Seco, casi notarial." in resultado
    assert "delve, utilize, tapestry" in resultado  # Parte 1 intacta


def test_main_prefiere_voz_md_si_existe(tmp_path, monkeypatch):
    (tmp_path / "seed.txt").write_text("Una farera hereda un faro.", encoding="utf-8")
    (tmp_path / "voz.md").write_text(VOZ_TEMPLATE, encoding="utf-8")
    (tmp_path / "CRAFT.md").write_text("# Craft\n", encoding="utf-8")
    monkeypatch.setattr(gen_voice, "BASE_DIR", tmp_path)
    monkeypatch.setattr(gen_voice, "call_writer", lambda prompt, **kw: RESPUESTA_MODELO)

    gen_voice.main()

    assert "Seco, casi notarial." in (tmp_path / "voz.md").read_text(encoding="utf-8")
    assert not (tmp_path / "voice.md").exists()


def test_main_es_idempotente_no_llama_call_writer_si_ya_hay_voz(tmp_path, monkeypatch):
    """Caso pedido explícitamente: si la Parte 2 ya tiene contenido real,
    una segunda corrida no debe invocar call_writer en absoluto."""
    voz_ya_decidida = VOZ_TEMPLATE.replace(
        "### Tone\n<!-- Generated during foundation. -->",
        "### Tone\nSeco, casi notarial.",
    ).replace(
        "### Exemplar Passages\n<!-- 3-5 paragraphs. -->",
        "### Exemplar Passages\n—No vino nadie —dijo ella.",
    )
    _preparar_entradas(tmp_path, voz_texto=voz_ya_decidida)
    monkeypatch.setattr(gen_voice, "BASE_DIR", tmp_path)

    def _no_deberia_llamarse(prompt, **kw):
        raise AssertionError("call_writer() fue invocado -- la voz ya estaba decidida")

    monkeypatch.setattr(gen_voice, "call_writer", _no_deberia_llamarse)

    gen_voice.main()  # no debe lanzar

    # el archivo no cambió
    assert (tmp_path / "voice.md").read_text(encoding="utf-8") == voz_ya_decidida
