# TRASPASO — rama `framework/es-multilibro`

Estado real al cierre de esta sesión (2026-07-27, tras la Tarea 7 --
generador de voz). Este documento reemplaza la necesidad de releer
`ESTADO.md` completo o el historial de commits para retomar el trabajo --
es la foto actual, no la bitácora de cómo se llegó acá (para eso está
`ESTADO.md`, que sí es narrativo).

## En una línea

Tareas 0, 1c, 1d, 2, 2b, 2c, 3, 4, 6 y 7 del `ENCARGO_CLAUDE_CODE.md`
están completas y testeadas (113 tests, todos en verde, sin necesitar
API). Toda esa construcción se hizo **sin `.env`**, con
`call_writer()`/`uv_run()` parcheados. Lo que sí necesita `.env` es
correr contra el modelo real y validar calidad -- 1a, 1b, 1d parte final,
`overall_score` en BASELINE, y correr la fundación completa (7 pasos, de
punta a punta) por primera vez.

## Estado del repositorio

| | |
|---|---|
| Rama | `framework/es-multilibro` |
| `.env` / `ANTHROPIC_API_KEY` | No existe en este entorno |
| Rama `autonovel/bells` | No existe en el remoto (verificado con `git fetch --all` + `git ls-remote --heads origin`) |
| Push | Al día hasta `40cfbd5`. El commit de la Tarea 7 puede estar sin pushear -- confirmar con `git log origin/framework/es-multilibro..HEAD --oneline` |
| Working tree | Limpio |
| `gh` CLI | No instalado en este entorno |
| Incidentes de seguridad | **RESUELTO.** Cuatro tokens de GitHub distintos quedaron expuestos en el chat en una sesión anterior (pegados mal en la terminal, en varios intentos de push). **Los cuatro están revocados**, confirmado por el usuario -- sin verificación pendiente. |
| Por qué falla `git push` con `!` | El prefijo `!` corre el comando sin TTY -- `git` no tiene dónde pedir usuario/token y aborta con "could not read Username ... No such device or address". No es un problema de que el token se vea; es que no hay terminal interactiva. Receta: `Ctrl+D` para salir de Claude Code (**misma terminal**, no otra máquina), `git push` ahí directo, pegar el token cuando lo pida, volver a entrar con `claude`. Con `credential.helper store` ya configurado, solo hace falta una vez -- después, hasta los `git push` corridos con `!` reusan la credencial guardada. |
| Token vigente | Fine-grained, creado 2026-07-27, alcance solo a `suazoca/autonovel`, permiso `Contents: read/write` únicamente, **vence a los 30 días (~2026-08-26)**. Al vencer, el `git push` guardado va a fallar reusando la credencial vieja -- limpiarla con `git credential reject` (protocol=https, host=github.com) antes de autenticar con un token nuevo. |

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
bb4c7ce Tarea 6: persistencia en la fase de fundación
4ad70b7 Tarea 2c: descontamina gen_world.py, gen_characters.py, gen_canon.py
40cfbd5 docs: incidente de tokens pasa a RESUELTO, anota vencimiento del token vigente
```

El commit de la Tarea 7 (`gen_voice.py`) se hace a continuación de este
documento -- correr `git log -1 --oneline` para ver su hash real.

`3ded223` (auditoría + plan + `deteccion_es.py`) es el commit base de todo
esto y llegó por `git pull`, no se generó en esta sesión.

## Tests

```bash
uv run python -m pytest tests/ -v
```

**113 tests, todos en verde, ninguno requiere `.env`.**

| Archivo | Qué cubre |
|---|---|
| `tests/test_deteccion_es.py` | Detección mecánica de slop en español (Tarea 0/1c) |
| `tests/test_draft_chapter.py` | Prompt de `draft_chapter.py` (Tarea 2) |
| `tests/test_gen_brief.py` | `extract_voice_rules()` de `gen_brief.py` (Tarea 2) |
| `tests/test_ambicion.py` | Umbrales por ambición y validación de diversidad de picos (Tarea 3) |
| `tests/test_siembras.py` | Validador de alcance de siembra (Tarea 4) |
| `tests/test_gen_outline.py` | Prompts de `gen_outline.py`/`gen_outline_part2.py` (Tarea 2b) |
| `tests/test_fundacion.py` | `fundacion_comun.py` + `gen_world.py`/`gen_characters.py`/`gen_canon.py` (Tarea 6) |
| `tests/test_run_pipeline_fundacion.py` | `run_generator()` + `verificar_archivos_fundacion()`, incluyendo mtime (Tarea 6) y la excepción de `voz.md` (Tarea 7) |
| `tests/test_descontaminacion_2c.py` | Ausencia de términos de *Bells* en `gen_world.py`/`gen_characters.py`/`gen_canon.py` (Tarea 2c) |
| `tests/test_gen_voice.py` | `gen_voice.py`: idempotencia, Parte 1 intacta, resolución bilingüe, parseo/llenado de secciones (Tarea 7) |

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
| 6 | `bb4c7ce` | `gen_world.py`/`gen_characters.py`/`gen_canon.py` se guardan a sí mismos; `gen_outline_part2.py` pasa a usar `fundacion_comun.py` (sin cambio de comportamiento); `run_pipeline.py` aborta y guarda `state` si un generador falla; verifica archivos antes de evaluar (por mtime, no solo "no vacío"). **No descontamina prompts** -- eso es la Tarea 2c. |
| 2c | `4ad70b7` | `gen_world.py`/`gen_characters.py`/`gen_canon.py` descontaminados de *Bells*: reparto fijo reemplazado por requisito estructural, secciones genéricas, género y sistema de magia condicionados a la semilla, prompts traducidos al español. |
| 7 | (pendiente de commitear) | `gen_voice.py` nuevo: genera la Parte 2 de `voz.md`/`voice.md` una sola vez (idempotente, no regenera si ya hay contenido real); `run_pipeline.py` lo corre como paso 0 de `run_foundation()`, antes que el resto; `verificar_archivos_fundacion()` chequea la voz por contenido, no por mtime (se congela a propósito). |

Además, `214768e` y `d3c4c72` son fixes puntuales (bug de `calcos_detectados()`,
y el valor correcto de `palabras_objetivo_capitulo`).

## Pendiente

Ninguna tarea numerada está formalmente asignada sin bloquear por `.env`,
pero hay dos frentes donde **sí se puede escribir y testear código ya**
(mismo patrón de mocks que toda esta sesión) -- lo que no se puede hacer
sin `.env` es correr contra el modelo real y juzgar calidad.

### Se puede escribir código sin `.env` (validar calidad sí necesita API)

- **Acumulación de canon en la fase de redacción**: no hay script que
  devuelva al canon los hechos que los capítulos establecen (nombres,
  edades, objetos mencionados al pasar). `evaluate_chapter()` ya devuelve
  `new_canon_entries`, pero nada lo consume. Depende de fijar el formato
  estructurado de `canon.md` primero -- decisión de diseño, no de API.
- **Parser del Foreshadowing Ledger / `libros_completos`** (hallazgos de
  la Tarea 4): los validadores de siembra funcionan sobre dicts, no hay
  parser que los extraiga de la tabla real, y `libros_completos` no tiene
  fuente de datos (`estado_serie.json`, Clase B, no existe todavía).
- **`craft` (CRAFT.md) no se usa realmente** en `gen_world.py` (se carga
  pero nunca se interpola en el prompt) ni en `gen_characters.py` (ni se
  carga). Encontrado al reescribir los prompts en la Tarea 2c, no
  corregido -- decisión de diseño (resumen manual vs. interpolar el
  archivo completo), no un fix mecánico.

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
5. **RESUELTO** -- `gen_world.py`/`gen_characters.py`/`gen_canon.py`
   contaminados con *Bells*: era la Tarea 2c, ya completa.
6. No hay script que acumule al canon los hechos establecidos durante la
   redacción -- ver "Pendiente" arriba.
7. **RESUELTO** -- Nada generaba la Parte 2 de `voice.md`/`voz.md`: era
   la Tarea 7, ya completa (`gen_voice.py`, generación única e idempotente).

## Cómo retomar

1. `git status` y `git log origin/framework/es-multilibro..HEAD --oneline`
   para confirmar que seguimos al día (deberían estar vacíos si nadie más
   tocó la rama).
2. Si no hay `.env` todavía, un frente para escribir código: avanzar el
   diseño del formato de `canon.md`/Foreshadowing Ledger (acumulación de
   canon en la fase de redacción).
3. Si ya hay `.env` con `ANTHROPIC_API_KEY`:
   a. Correr `evaluate.py --chapter` (sin `--solo-mecanico`) sobre los
      fixtures de `tests/fixtures/` para completar `docs/BASELINE.md`.
   b. Arrancar la Tarea 1b.
   c. Con la Tarea 6 ya resuelta, se puede intentar
      `run_pipeline.py --phase foundation` de punta a punta por primera
      vez (con un `seed.txt`/`semilla.txt` real).
