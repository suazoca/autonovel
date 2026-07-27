# TRASPASO — rama `framework/es-multilibro`

Estado real al cierre de esta sesión (2026-07-27, tras la Tarea 6). Este
documento reemplaza la necesidad de releer `ESTADO.md` completo o el
historial de commits para retomar el trabajo -- es la foto actual, no la
bitácora de cómo se llegó acá (para eso está `ESTADO.md`, que sí es
narrativo).

## En una línea

Tareas 0, 1c, 1d, 2, 2b, 3, 4 y 6 del `ENCARGO_CLAUDE_CODE.md` están
completas y testeadas (91 tests, todos en verde, sin necesitar API). Toda
esa construcción se hizo **sin `.env`**, con `call_writer()`/`uv_run()`
parcheados -- el mismo patrón sigue disponible para lo que falta: Tarea
2c (sin formalizar) y el generador de voz que falta (hallazgo nuevo,
prioridad alta) se pueden escribir y testear sin API. Lo que sí necesita
`.env` es correr contra el modelo real y validar calidad -- 1a, 1b, 1d
parte final, `overall_score` en BASELINE, y correr la fundación completa
por primera vez.

## Estado del repositorio

| | |
|---|---|
| Rama | `framework/es-multilibro` |
| `.env` / `ANTHROPIC_API_KEY` | No existe en este entorno |
| Rama `autonovel/bells` | No existe en el remoto (verificado con `git fetch --all` + `git ls-remote --heads origin`) |
| Push | Al día hasta `48395a8` (incluye un commit del usuario, hecho fuera de esta conversación: mover `AUDITORIA_Y_PLAN.md` a `docs/`). El commit de la Tarea 6 puede estar sin pushear -- confirmar con `git log origin/framework/es-multilibro..HEAD --oneline` |
| Working tree | Limpio |
| `gh` CLI | No instalado en este entorno |
| Incidentes de seguridad | **Cuatro** tokens de GitHub distintos quedaron expuestos en el chat durante esta sesión (pegados mal en la terminal, en varios intentos de push). El primero fue revocado con confirmación explícita del usuario; para los otros tres no hay confirmación explícita en esta conversación -- **verificar que estén revocados** antes de asumir que sí. Si hace falta pushear de nuevo: token nuevo, **solo** como variable de entorno ya exportada en la terminal del usuario, nunca pegado en el chat. Considerar un credential helper de git configurado una sola vez. |

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
2b31156 docs: TRASPASO.md -- estado real para retomar sin releer ESTADO.md completo
b18ca4a docs: corrige el conteo de tokens expuestos (cuatro, no dos)
48395a8 docs: mueve AUDITORIA_Y_PLAN.md a docs/                       (del usuario, no de esta conversación)
```

El commit de la Tarea 6 (persistencia en la fase de fundación) se hace a
continuación de este documento -- correr `git log -1 --oneline` para ver
su hash real una vez hecho.

`3ded223` (auditoría + plan + `deteccion_es.py`) es el commit base de todo
esto y llegó por `git pull`, no se generó en esta sesión.

## Tests

```bash
uv run python -m pytest tests/ -v
```

**91 tests, todos en verde, ninguno requiere `.env`.**

| Archivo | Qué cubre |
|---|---|
| `tests/test_deteccion_es.py` | Detección mecánica de slop en español (Tarea 0/1c) |
| `tests/test_draft_chapter.py` | Prompt de `draft_chapter.py` (Tarea 2) |
| `tests/test_gen_brief.py` | `extract_voice_rules()` de `gen_brief.py` (Tarea 2) |
| `tests/test_ambicion.py` | Umbrales por ambición y validación de diversidad de picos (Tarea 3) |
| `tests/test_siembras.py` | Validador de alcance de siembra (Tarea 4) |
| `tests/test_gen_outline.py` | Prompts de `gen_outline.py`/`gen_outline_part2.py` (Tarea 2b) |
| `tests/test_fundacion.py` | `fundacion_comun.py` + `gen_world.py`/`gen_characters.py`/`gen_canon.py` (Tarea 6) |
| `tests/test_run_pipeline_fundacion.py` | `run_generator()` + `verificar_archivos_fundacion()` en `run_pipeline.py` (Tarea 6) |

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
| 6 | (este commit) | `gen_world.py`/`gen_characters.py`/`gen_canon.py` se guardan a sí mismos; `gen_outline_part2.py` pasa a usar `fundacion_comun.py` (sin cambio de comportamiento); `run_pipeline.py` aborta y guarda `state` si un generador falla; verifica archivos antes de evaluar. **No descontamina prompts** -- eso es la Tarea 2c. |

Además, `214768e` y `d3c4c72` son fixes puntuales (bug de `calcos_detectados()`,
y el valor correcto de `palabras_objetivo_capitulo`).

## Pendiente

Ninguna tarea numerada está formalmente asignada sin bloquear por `.env`,
pero hay tres frentes donde **sí se puede escribir y testear código ya**
(mismo patrón de mocks que toda esta sesión) -- lo que no se puede hacer
sin `.env` es correr contra el modelo real y juzgar calidad.

### Se puede escribir código sin `.env` (validar calidad sí necesita API)

- **Tarea 2c (candidata, sin formalizar)**: `gen_world.py`,
  `gen_characters.py` y `gen_canon.py` siguen con los prompts
  contaminados de *Bells* (Cass Bellwright, Perin, Maret Corda, Rector
  Suvaine, Torvald Hess, Cantamura, Tonal Law). La Tarea 6 fue
  estrictamente persistencia, no tocó contenido de prompts a pedido
  explícito del usuario. Mismo tratamiento que A1/Tarea 2b cuando se
  formalice.
- **El generador de voz que falta** (hallazgo nuevo, prioridad alta):
  no existe ningún script que llene `voice.md`/`voz.md` Parte 2 --
  confirmado con grep, ni `gen_voice.py` ni ningún `write_text` a ese
  archivo en todo el repo. `draft_chapter.py`, `gen_brief.py` y
  `gen_outline.py` la leen esperando contenido real; hoy es plantilla
  vacía. Se puede escribir el script (mismo patrón `main()` +
  `fundacion_comun.py` + tests con `call_writer` parcheado) sin `.env`;
  validar que los pasajes de prueba generados tengan calidad real sí lo
  necesita.
- **Acumulación de canon en la fase de redacción**: no hay script que
  devuelva al canon los hechos que los capítulos establecen (nombres,
  edades, objetos mencionados al pasar). `evaluate_chapter()` ya devuelve
  `new_canon_entries`, pero nada lo consume. Depende de fijar el formato
  estructurado de `canon.md` primero -- decisión de diseño, no de API.
- **Parser del Foreshadowing Ledger / `libros_completos`** (hallazgos de
  la Tarea 4): los validadores de siembra funcionan sobre dicts, no hay
  parser que los extraiga de la tabla real, y `libros_completos` no tiene
  fuente de datos (`estado_serie.json`, Clase B, no existe todavía).

### Bloqueado por `.env` / `ANTHROPIC_API_KEY` (correr contra el modelo real)

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

1. `dividir_oraciones()` descarta oraciones de ≤2 palabras por diseño,
   sesga `cv_longitud_oracion()` hacia arriba. No corregido a pedido
   explícito.
2. `CALIBRACION["umbral_cv_oracion"]` (0.32) no discriminó nada contra los
   2 fixtures de prueba -- falta corpus real para recalibrar. No corregido
   a pedido explícito.
3. Los validadores de siembra (`validar_siembra()`) operan sobre dicts
   estructurados, no hay parser todavía que los extraiga de la tabla real
   del Foreshadowing Ledger. Decisión de diseño confirmada, no un bug.
4. `libros_completos` (regla 4 de siembras) no tiene fuente de datos
   todavía -- depende de `estado_serie.json` (Clase B), que no existe en
   este repo.
5. `gen_world.py`/`gen_characters.py`/`gen_canon.py` contaminados con
   *Bells* -- candidato a Tarea 2c, sin formalizar.
6. No hay script que acumule al canon los hechos establecidos durante la
   redacción -- ver "Pendiente" arriba.
7. **Nada genera la Parte 2 de `voice.md`/`voz.md`** -- prioridad alta,
   hermano de la Tarea 6 (no la misma: no hay un script roto, no existe
   el script). `draft_chapter.py`/`gen_brief.py`/`gen_outline.py` la leen
   esperando contenido real. Ver "Pendiente" arriba.

## Cómo retomar

1. `git status` y `git log origin/framework/es-multilibro..HEAD --oneline`
   para confirmar que seguimos al día (deberían estar vacíos si nadie más
   tocó la rama).
2. Si no hay `.env` todavía, tres frentes para escribir código: formalizar
   y arrancar la **Tarea 2c**, escribir el **generador de voz que falta**,
   o avanzar el diseño del formato de `canon.md`/Foreshadowing Ledger.
3. Si ya hay `.env` con `ANTHROPIC_API_KEY`:
   a. Correr `evaluate.py --chapter` (sin `--solo-mecanico`) sobre los
      fixtures de `tests/fixtures/` para completar `docs/BASELINE.md`.
   b. Arrancar la Tarea 1b.
   c. Con la Tarea 6 ya resuelta, se puede intentar
      `run_pipeline.py --phase foundation` de punta a punta por primera
      vez (con un `seed.txt`/`semilla.txt` real).
