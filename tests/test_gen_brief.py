"""
Test de aceptación de la Tarea 2 (ENCARGO_CLAUDE_CODE.md) para
gen_brief.py::extract_voice_rules(): debe leer y parsear voice.md Parte 2,
no devolver una lista fija de reglas de la novela anterior.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import gen_brief

PROHIBIDO = ["cass", "bell", "bronze", "under-note"]

VOZ_INVENTADA = """# Perfil de voz (prueba)

## Part 1: Guardrails (permanent, all novels)

### Structural slop patterns

**Paragraph template machine**: Don't repeat the same paragraph structure.

## Part 2: Voice Identity (generated per novel)

### Tone
Seca, casi notarial. Nunca exclama.

### Vocabulary Register
Vocabulario portuario: sal, brea, cabos, óxido.
"""


def test_extract_voice_rules_lee_contenido_inventado(tmp_path, monkeypatch):
    voice_file = tmp_path / "voice.md"
    voice_file.write_text(VOZ_INVENTADA, encoding="utf-8")
    monkeypatch.setattr(gen_brief, "VOICE_PATH", voice_file)

    rules = gen_brief.extract_voice_rules()

    rules_lower = " ".join(rules).lower()
    for termino in PROHIBIDO:
        assert termino not in rules_lower, f"'{termino}' apareció en las reglas extraídas"

    assert any("Seca, casi notarial" in r for r in rules), rules
    assert any("Vocabulario portuario" in r for r in rules), rules
    assert any("Paragraph template machine" in r for r in rules), rules


def test_extract_voice_rules_no_rompe_si_voice_md_vacio(tmp_path, monkeypatch):
    voice_file = tmp_path / "voice.md"
    voice_file.write_text("# Voice Profile\n", encoding="utf-8")
    monkeypatch.setattr(gen_brief, "VOICE_PATH", voice_file)

    rules = gen_brief.extract_voice_rules()
    assert isinstance(rules, list)
    assert len(rules) >= 1  # mensaje de fallback, no una excepción


VOZ_A_MEDIO_LLENAR = """# Perfil de voz (fundación en progreso)

## Part 1: Guardrails (permanent, all novels)

### Structural slop patterns

**Em dash overload**: One or two per page is fine.

## Part 2: Voice Identity (generated per novel)

### Tone
<!-- Generated during foundation. Examples: "Mythic and weighty." -->

### Sentence Rhythm
Frases cortas para tensión, largas para descripción.

### Vocabulary Register
<!-- Generated during foundation. -->

### POV and Tense
<!-- Generated during foundation. -->
"""


def test_extract_voice_rules_no_inventa_para_secciones_vacias(tmp_path, monkeypatch):
    """La fundación corre con voice.md a medio llenar durante varias
    iteraciones: algunas subsecciones de Parte 2 tienen contenido real,
    otras son solo el comentario HTML placeholder de la plantilla. No debe
    romper, y no debe inventar una regla para las que están vacías."""
    voice_file = tmp_path / "voice.md"
    voice_file.write_text(VOZ_A_MEDIO_LLENAR, encoding="utf-8")
    monkeypatch.setattr(gen_brief, "VOICE_PATH", voice_file)

    rules = gen_brief.extract_voice_rules()

    # La única subsección de Parte 2 con contenido real generó su regla
    assert any(r.startswith("Sentence Rhythm:") for r in rules), rules
    # Ninguna subsección vacía (solo comentario HTML) inventó una regla
    for vacio in ("Tone:", "Vocabulary Register:", "POV and Tense:"):
        assert not any(r.startswith(vacio) for r in rules), (
            f"Se inventó una regla para una sección vacía ({vacio}): {rules}"
        )
    # Y el patrón estructural real de Parte 1 sí se extrajo
    assert any("Em dash overload" in r for r in rules), rules


def test_ruta_bilingue_prefiere_voz_md_sobre_voice_md(tmp_path):
    (tmp_path / "voz.md").write_text("contenido en español", encoding="utf-8")
    (tmp_path / "voice.md").write_text("contenido en inglés", encoding="utf-8")
    assert gen_brief._ruta_bilingue(tmp_path, "voz.md", "voice.md").read_text(
        encoding="utf-8"
    ) == "contenido en español"


def test_ruta_bilingue_cae_a_voice_md_si_no_hay_voz_md(tmp_path):
    (tmp_path / "voice.md").write_text("contenido en inglés", encoding="utf-8")
    assert gen_brief._ruta_bilingue(tmp_path, "voz.md", "voice.md").read_text(
        encoding="utf-8"
    ) == "contenido en inglés"
