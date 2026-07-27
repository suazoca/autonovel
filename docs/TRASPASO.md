# TRASPASO — rama `framework/es-multilibro`

Estado real al cierre de esta sesión (2026-07-27). Este documento reemplaza
la necesidad de releer `ESTADO.md` completo o el historial de commits para
retomar el trabajo -- es la foto actual, no la bitácora de cómo se llegó
acá (para eso está `ESTADO.md`, que sí es narrativo).

## En una línea

Tareas 0, 1c, 1d, 2, 2b, 3 y 4 del `ENCARGO_CLAUDE_CODE.md` están completas
y testeadas (62 tests, todos en verde, sin necesitar API). Falta: Tarea 6
(prioridad alta, no depende de `.env`), y todo lo que sí depende de
`ANTHROPIC_API_KEY` (1a, 1b, 1d parte final, `overall_score` en BASELINE).

## Estado del repositorio

| | |
|---|---|
| Rama | `framework/es-multilibro` |
| `.env` / `ANTHROPIC_API_KEY` | No existe en este entorno |
| Rama `autonovel/bells` | No existe en el remoto (verificado con `git fetch --all` + `git ls-remote --heads origin`) |
| Push | Al día -- todo hasta `648b0c3` está en `origin/framework/es-multilibro` |
| Working tree | Limpio |
| `gh` CLI | No instalado en este entorno |
| Incidentes de seguridad | Dos tokens de GitHub quedaron expuestos en el chat durante esta sesión (pegados mal en la terminal). Ambos revocados por el usuario de inmediato. Si hace falta pushear: token nuevo, **solo** como variable de entorno ya exportada en la terminal del usuario, nunca pegado en el chat. |

## Commits de esta rama (los que no vinieron por `git pull`)

```
7346d77 Tarea 0: línea base con fixtures en español
214768e fix: IGNORECASE en calcos_detectados + corrección del test 6
625fc7f Tarea 1c (A): flag --solo-mecanico en evaluate.py
975ac18 Tarea 1c (B): integra deteccion_es.py en slop_score()
49a5976 Tarea 1d: fixtures mínimos de voz y mundo en español
76454a5 docs: ESTADO.md para retomar sin releer el historial
04b6439 Tarea 2: descontamina draft_chapter.py y gen_brief.py
4ad802c docs: ESTADO.md al día con el cierre de la Tarea 2
5af3cb9 Tarea 3: campo de ambición por capítulo (pico | sosten | valle)
d3c4c72 fix: palabras_objetivo_capitulo=2000 (era 3800, error de sesión anterior)
506f435 Tarea 4: alcance de siembra para series (libro | serie)
df7b06c docs: suma gen_outline_part2.py a Tarea 2b, documenta libros_completos
c513adf docs: ESTADO.md al día con el cierre de la Tarea 4
5a78c52 Tarea 2b: descontamina gen_outline.py y gen_outline_part2.py
648b0c3 docs: ESTADO.md al día con el cierre de la Tarea 2b
```

`3ded223` (auditoría + plan + `deteccion_es.py`) es el commit base de todo
esto y llegó por `git pull`, no se generó en esta sesión.

## Tests

```bash
uv run python -m pytest tests/ -v
```

**62 tests, todos en verde, ninguno requiere `.env`.**

| Archivo | Qué cubre |
|---|---|
| `tests/test_deteccion_es.py` | Detección mecánica de slop en español (Tarea 0/1c) |
| `tests/test_draft_chapter.py` | Prompt de `draft_chapter.py` (Tarea 2) |
| `tests/test_gen_brief.py` | `extract_voice_rules()` de `gen_brief.py` (Tarea 2) |
| `tests/test_ambicion.py` | Umbrales por ambición y validación de diversidad de picos (Tarea 3) |
| `tests/test_siembras.py` | Validador de alcance de siembra (Tarea 4) |
| `tests/test_gen_outline.py` | Prompts de `gen_outline.py`/`gen_outline_part2.py` (Tarea 2b) |

## Tareas cerradas

| Tarea | Commit | Qué hace |
|---|---|---|
| 0 | `7346d77` | Línea base con 2 fixtures en español (sin `autonovel/bells`, no existe) |
| 1c | `625fc7f` + `975ac18` | `--solo-mecanico` en `evaluate.py`; `slop_score()` usa `deteccion_es.py` (ES) en vez de listas en inglés |
| 1d | `49a5976` | Fixtures mínimos de voz/mundo en español (creados, no conectados a una corrida real) |
| 2 | `04b6439` | `draft_chapter.py`/`gen_brief.py` descontaminados de *Bells*, prompt en español, nomenclatura bilingüe |
| 3 | `5af3cb9` | Ambición por capítulo (pico/sosten/valle), umbral por defecto "sosten" (no el más laxo) |
| 4 | `506f435` | Alcance de siembra libro/serie, validadores sobre dicts, regla de regresión sin `siembras_serie.md` |
| 2b | `5a78c52` | `gen_outline.py`/`gen_outline_part2.py` descontaminados, ya no leen de `/tmp`, ahora se guardan a sí mismos |

Además, `214768e` y `d3c4c72` son fixes puntuales (bug de `calcos_detectados()`,
y el valor correcto de `palabras_objetivo_capitulo`).

## Pendiente

### Sin bloquear por `.env` -- la única que queda

**Tarea 6 (prioridad alta)** -- `ENCARGO_CLAUDE_CODE.md`, sección "TAREA 6".
`gen_world.py`, `gen_characters.py` y `gen_canon.py` terminan con
`print(result)` y no guardan en `world.md`/`characters.md`/`canon.md`.
`run_pipeline.py` tampoco captura ese stdout. **Tal como está, correr la
fase de fundación completa no dejaría nada escrito, ni con `.env`
configurado.** Es la tarea de mayor impacto de todas las pendientes.
Mismo patrón de arreglo que ya se aplicó en la Tarea 2b (cada script se
guarda a sí mismo, con `ruta_bilingue()`).

### Bloqueado por `.env` / `ANTHROPIC_API_KEY`

- **1a**: flag `--idioma es|en` en `evaluate.py` (opcional según el
  encargo; se priorizó español).
- **1b**: traducir los prompts del juez LLM (`evaluate.py`,
  `adversarial_edit.py`, `reader_panel.py`, `review.py`,
  `compare_chapters.py`) + bloque de advertencias sobre normas castellanas.
- **1d, parte final**: conectar `voz_minima_es.md`/`mundo_minimo_es.md` a
  una corrida real de `evaluate_chapter()` (rutas hardcodeadas al
  directorio raíz en `load_layer_files()`).
- Completar el `overall_score` de los dos fixtures de la Tarea 0 en
  `docs/BASELINE.md` (hoy solo tiene los números mecánicos).

## Hallazgos abiertos (`docs/HALLAZGOS.md`)

1. **Tarea 6** (ver arriba) -- ya formalizada como tarea, no solo hallazgo.
2. `dividir_oraciones()` descarta oraciones de ≤2 palabras por diseño,
   sesga `cv_longitud_oracion()` hacia arriba. No corregido a pedido
   explícito.
3. `CALIBRACION["umbral_cv_oracion"]` (0.32) no discriminó nada contra los
   2 fixtures de prueba -- falta corpus real para recalibrar. No corregido
   a pedido explícito.
4. Los validadores de siembra (`validar_siembra()`) operan sobre dicts
   estructurados, no hay parser todavía que los extraiga de la tabla real
   del Foreshadowing Ledger. Decisión de diseño confirmada, no un bug.
5. `libros_completos` (regla 4 de siembras) no tiene fuente de datos
   todavía -- depende de `estado_serie.json` (Clase B), que no existe en
   este repo. `validar_siembra()` ya está lista para recibirlo cuando
   exista.

## Cómo retomar

1. `git status` y `git log origin/framework/es-multilibro..HEAD --oneline`
   para confirmar que seguimos al día (deberían estar vacíos si nadie más
   tocó la rama).
2. Si no hay `.env` todavía: arrancar la **Tarea 6**.
3. Si ya hay `.env` con `ANTHROPIC_API_KEY`:
   a. Correr `evaluate.py --chapter` (sin `--solo-mecanico`) sobre los
      fixtures de `tests/fixtures/` para completar `docs/BASELINE.md`.
   b. Arrancar la Tarea 1b.
   c. Si la Tarea 6 ya está resuelta, se puede intentar
      `run_pipeline.py --phase foundation` de punta a punta por primera
      vez.
