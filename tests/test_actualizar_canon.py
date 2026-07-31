"""
Tests de aceptación de la Tarea 10 (ENCARGO_CLAUDE_CODE.md) --
acumulación de canon durante la redacción.

actualizar_canon.py es puramente determinista: la detección de
contradicciones ya la hizo el juez de evaluate.py y viene en el
eval_log. No hace falta mockear ninguna llamada a la API ni tocar
`.env` para nada de este archivo.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import actualizar_canon as ac
import evaluate


def _preparar(tmp_path, monkeypatch):
    eval_dir = tmp_path / "eval_logs"
    eval_dir.mkdir()
    canon_emergente = tmp_path / "canon_emergente.md"
    state_path = tmp_path / "state.json"
    monkeypatch.setattr(ac, "EVAL_LOG_DIR", eval_dir)
    monkeypatch.setattr(ac, "CANON_EMERGENTE_PATH", canon_emergente)
    monkeypatch.setattr(ac, "STATE_PATH", state_path)
    return eval_dir, canon_emergente, state_path


def _escribir_eval_log(eval_dir, chapter_num, entries, timestamp="20260101_000000"):
    path = eval_dir / f"{timestamp}_ch{chapter_num:02d}.json"
    path.write_text(json.dumps({"new_canon_entries": entries}), encoding="utf-8")
    return path


def _correr(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["actualizar_canon.py", *argv])
    ac.main()


ENTRADAS_CH7 = [
    {"categoria": "Hechos de personajes",
     "hecho": "El hermano de Ferrero murió en marzo del 91.",
     "contradice": None},
    {"categoria": "Cultural",
     "hecho": "El reloj es un Omega Seamaster con la correa cambiada.",
     "contradice": None},
]


def test_canon_emergente_se_crea_con_encabezado(tmp_path, monkeypatch):
    eval_dir, canon_emergente, _ = _preparar(tmp_path, monkeypatch)
    _escribir_eval_log(eval_dir, 7, ENTRADAS_CH7)

    _correr(monkeypatch, "7")

    assert canon_emergente.exists()
    texto = canon_emergente.read_text(encoding="utf-8")
    assert texto.startswith("# CANON EMERGENTE")
    assert "No editar a mano salvo para" in texto


def test_reemplazo_no_duplica_al_correr_dos_veces(tmp_path, monkeypatch):
    eval_dir, canon_emergente, _ = _preparar(tmp_path, monkeypatch)
    _escribir_eval_log(eval_dir, 7, ENTRADAS_CH7)

    _correr(monkeypatch, "7")
    _correr(monkeypatch, "7")

    texto = canon_emergente.read_text(encoding="utf-8")
    assert texto.count("[C07-01]") == 1
    assert texto.count("[C07-02]") == 1
    assert texto.count("## Cap. 07") == 1


def test_reemplazo_no_toca_secciones_de_otros_capitulos(tmp_path, monkeypatch):
    eval_dir, canon_emergente, _ = _preparar(tmp_path, monkeypatch)
    _escribir_eval_log(
        eval_dir, 3,
        [{"categoria": "Geografía", "hecho": "Hecho del cap 3.", "contradice": None}],
    )
    _correr(monkeypatch, "3")

    _escribir_eval_log(eval_dir, 7, ENTRADAS_CH7)
    _correr(monkeypatch, "7")

    texto = canon_emergente.read_text(encoding="utf-8")
    assert "Hecho del cap 3." in texto
    assert "## Cap. 03" in texto
    assert "## Cap. 07" in texto

    # Re-evaluar el capítulo 7 (revisión) no debe tocar la sección del 3.
    _correr(monkeypatch, "7")
    texto2 = canon_emergente.read_text(encoding="utf-8")
    assert "Hecho del cap 3." in texto2
    assert texto2.count("## Cap. 03") == 1


def test_numeracion_de_ids_reiniciada_por_capitulo(tmp_path, monkeypatch):
    eval_dir, canon_emergente, _ = _preparar(tmp_path, monkeypatch)
    _escribir_eval_log(eval_dir, 3, ENTRADAS_CH7)
    _correr(monkeypatch, "3")

    _escribir_eval_log(eval_dir, 7, ENTRADAS_CH7)
    _correr(monkeypatch, "7")

    texto = canon_emergente.read_text(encoding="utf-8")
    assert "[C03-01]" in texto and "[C03-02]" in texto
    assert "[C07-01]" in texto and "[C07-02]" in texto


def test_conflicto_marcado_y_anotado_en_debts(tmp_path, monkeypatch):
    eval_dir, canon_emergente, state_path = _preparar(tmp_path, monkeypatch)
    state_path.write_text(json.dumps({"debts": []}), encoding="utf-8")

    entradas = [
        {"categoria": "Cronología",
         "hecho": "Ferrero guardó el reloj en 2011.",
         "contradice": "2010: Ferrero guardó en un cajón el reloj de su hermano"},
    ]
    _escribir_eval_log(eval_dir, 7, entradas)
    _correr(monkeypatch, "7")

    texto = canon_emergente.read_text(encoding="utf-8")
    assert "[C07-01] CONFLICTO (Cronología)" in texto
    assert 'contradice: "2010: Ferrero guardó en un cajón el reloj de su hermano"' in texto

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert len(state["debts"]) == 1
    debt = state["debts"][0]
    assert debt["capitulo"] == 7
    assert debt["id"] == "C07-01"
    assert debt["resuelta"] is False
    assert debt["contradice"] == "2010: Ferrero guardó en un cajón el reloj de su hermano"


def test_conflicto_no_duplica_debts_al_reejecutar(tmp_path, monkeypatch):
    eval_dir, canon_emergente, state_path = _preparar(tmp_path, monkeypatch)
    state_path.write_text(json.dumps({"debts": []}), encoding="utf-8")
    entradas = [
        {"categoria": "Cronología", "hecho": "Ferrero guardó el reloj en 2011.",
         "contradice": "algo"},
    ]
    _escribir_eval_log(eval_dir, 7, entradas)
    _correr(monkeypatch, "7")
    _correr(monkeypatch, "7")

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert len(state["debts"]) == 1


def test_debts_de_otros_capitulos_sobreviven(tmp_path, monkeypatch):
    eval_dir, canon_emergente, state_path = _preparar(tmp_path, monkeypatch)
    state_path.write_text(json.dumps({
        "debts": [{"capitulo": 3, "id": "C03-01", "categoria": "x",
                   "hecho": "y", "contradice": "z", "resuelta": False}],
    }), encoding="utf-8")

    entradas = [
        {"categoria": "Cronología", "hecho": "Otro hecho.", "contradice": "otro"},
    ]
    _escribir_eval_log(eval_dir, 7, entradas)
    _correr(monkeypatch, "7")

    state = json.loads(state_path.read_text(encoding="utf-8"))
    capitulos = {d["capitulo"] for d in state["debts"]}
    assert capitulos == {3, 7}


def test_eval_log_formato_viejo_no_rompe(tmp_path, monkeypatch, capsys):
    eval_dir, canon_emergente, _ = _preparar(tmp_path, monkeypatch)
    _escribir_eval_log(eval_dir, 7, ["Un hecho viejo en formato de string."])

    _correr(monkeypatch, "7")  # no debe lanzar excepción

    assert not canon_emergente.exists()
    captured = capsys.readouterr()
    assert "AVISO" in captured.err or "AVISO" in captured.out


def test_eval_log_vacio_de_entradas_no_rompe(tmp_path, monkeypatch):
    eval_dir, canon_emergente, _ = _preparar(tmp_path, monkeypatch)
    _escribir_eval_log(eval_dir, 7, [])

    _correr(monkeypatch, "7")

    texto = canon_emergente.read_text(encoding="utf-8")
    assert "## Cap. 07" in texto
    assert ac.SIN_HECHOS in texto


def test_flag_eval_log_fuerza_ruta_explicita(tmp_path, monkeypatch):
    eval_dir, canon_emergente, _ = _preparar(tmp_path, monkeypatch)
    otra_carpeta = tmp_path / "otro_lado"
    otra_carpeta.mkdir()
    ruta = otra_carpeta / "manual.json"
    ruta.write_text(json.dumps({"new_canon_entries": ENTRADAS_CH7}), encoding="utf-8")

    _correr(monkeypatch, "7", "--eval-log", str(ruta))

    assert canon_emergente.exists()
    assert "[C07-01]" in canon_emergente.read_text(encoding="utf-8")


def test_busca_el_eval_log_mas_reciente(tmp_path, monkeypatch):
    eval_dir, canon_emergente, _ = _preparar(tmp_path, monkeypatch)
    _escribir_eval_log(
        eval_dir, 7,
        [{"categoria": "Cultural", "hecho": "Versión vieja.", "contradice": None}],
        timestamp="20260101_000000",
    )
    _escribir_eval_log(
        eval_dir, 7,
        [{"categoria": "Cultural", "hecho": "Versión nueva.", "contradice": None}],
        timestamp="20260102_000000",
    )

    _correr(monkeypatch, "7")

    texto = canon_emergente.read_text(encoding="utf-8")
    assert "Versión nueva." in texto
    assert "Versión vieja." not in texto


def test_sin_eval_log_sale_con_error_explicito(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch)
    monkeypatch.setattr(sys, "argv", ["actualizar_canon.py", "7"])
    try:
        ac.main()
        assert False, "debía salir con SystemExit"
    except SystemExit as e:
        assert "no se encontró ningún eval_log" in str(e)


# ---------------------------------------------------------------------------
# Los dos archivos de canon no se pisan entre sí (decisión de diseño 1).
# ---------------------------------------------------------------------------

def test_gen_canon_no_conoce_canon_emergente():
    contenido = (ROOT / "gen_canon.py").read_text(encoding="utf-8")
    assert "canon_emergente" not in contenido


def test_evaluate_chapter_carga_los_dos_archivos_de_canon(tmp_path, monkeypatch):
    monkeypatch.setattr(evaluate, "BASE_DIR", tmp_path)
    (tmp_path / "canon.md").write_text("HECHO-FUNDACION", encoding="utf-8")
    (tmp_path / "canon_emergente.md").write_text("HECHO-EMERGENTE", encoding="utf-8")

    layers = evaluate.load_layer_files()
    assert layers["canon"] == "HECHO-FUNDACION"
    assert layers["canon_emergente"] == "HECHO-EMERGENTE"


# ---------------------------------------------------------------------------
# CHAPTER_PROMPT (Tarea 10, punto 3): traducido, sin calibración de
# fantasía, con el bloque de normas del castellano.
# ---------------------------------------------------------------------------

def test_chapter_prompt_tiene_frase_ancla_y_no_menciona_fantasy():
    texto = evaluate.CHAPTER_PROMPT
    assert "más largo que el inglés" in texto.lower()
    assert "fantasy" not in texto.lower()
    assert "{canon_emergente}" in texto
