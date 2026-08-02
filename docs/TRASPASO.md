# TRASPASO — rama `novela2` (worktree de `framework/es-multilibro`)

Estado real al cierre de esta sesión (2026-08-02). Este documento
reemplaza la necesidad de releer `ESTADO.md` completo o el historial de
commits para retomar el trabajo -- es la foto actual, no la bitácora
(para eso está `ESTADO.md`, que sí es narrativo y tiene una sección
nueva para esta rama).

**Actualización 2026-08-02:** sesión larga con dos ejes. (1) Se
encontró y corrigió un bug de anclaje en `evaluate.py`: `overall_score`
lo inventaba el juez como campo suelto, sin relación con las 9
dimensiones que sí puntuaba, y el propio prompt lo empujaba a 7.0 con
un ancla repetida. Ahora se calcula en código: `0.7 * media + 0.3 *
mínimo` de las dimensiones presentes (sin asumir un número fijo).
(2) Se escribieron, evaluaron y aceptaron los capítulos 3, 4 y 5 --
este último tuvo que reescribirse entero porque el Catalyst, tal como
salió la primera vez, no cumplía lo que el propio outline necesita para
cerrar el libro en el Cap. 46. Las dos decisiones de canon que quedaron
abiertas del Cap. 3/4 (Ruti, cronología del Sepulcro/Zúrich) están
resueltas.

## Qué es esta rama

`novela2` es un **worktree separado** (`git worktree list` lo confirma:
`/root/novela2` en la rama `novela2`, junto a `/root/autonovel` en
`novela-es` -- otro libro, no tocar desde acá) que arrancó desde
`framework/es-multilibro` en el commit de cierre de la Tarea 7
(`7b81700`). A partir de ahí dejó de ser trabajo sobre el framework en
sí y pasó a ser la escritura de una novela concreta con ese framework:
**"La ostensión"** (Libro 1), a partir de `semilla.txt` -- un científico
de IA investigando la Sábana Santa antes de la ostensión de 2033.

El framework en sí (Tareas 0-7, `ENCARGO_CLAUDE_CODE.md`) sigue viviendo
en `framework/es-multilibro`; lo que se agregó en esta rama después de
divergir (Tareas 8, 9, 9b -- ver abajo) todavía **no se mergeó de
vuelta**.

## En una línea

Fundación completa y aprobada. **Cap. 1 a 5 escritos, evaluados y
aceptados.** `evaluate.py` reparado dos veces esta rama: primero la
compatibilidad con Fable 5 (sesión anterior), ahora un bug de
agregación de puntaje que hacía que todo capítulo diera 7.0 sin
importar la calidad real (ver sección dedicada abajo). El Cap. 5 se
reescribió entero a mitad de sesión al descubrir que el Cap. 46 (Final
Image) depende de una escena que la primera versión no tenía. Tres
deudas de canon abiertas durante la sesión (Ruti, cronología del
Sepulcro, planilla de Zúrich) están resueltas a mano. `state.json::debts`
vacío. Listo para Cap. 6, que ya tiene material de apertura preparado
en `briefs/cap06_apertura.md` (ver "Próximo paso").

## Estado del repositorio

| | |
|---|---|
| Directorio | `/root/novela2` (worktree; confirmado con `git worktree list`) |
| Rama | `novela2`, diverge de `framework/es-multilibro` en `7b81700` (Tarea 7) |
| `.env` / `ANTHROPIC_API_KEY` | Presente en este entorno. `AUTONOVEL_WRITER_MODEL=claude-fable-5`, `AUTONOVEL_JUDGE_MODEL=claude-opus-5`, `AUTONOVEL_REVIEW_MODEL=claude-opus-5`, `AUTONOVEL_API_BASE_URL=https://api.anthropic.com` |
| Push | Al día con `origin/novela2` (`git log origin/novela2..HEAD --oneline` vacío). Último commit: `45cc0f1`. |
| Working tree | Limpio -- confirmar con `git status`. |
| Tests | `uv run python -m pytest tests/ -v` -- **246 tests, todos en verde, + 38 xfail esperados** (subió de 238: se agregó `tests/test_evaluate.py`, 8 tests nuevos, para la agregación de `overall_score`). No hace falta `.env` (todo mockeado); drafting/evaluar capítulos sí lo necesita. |
| Token de GitHub | Fine-grained, creado 2026-07-27, alcance `suazoca/autonovel`, permiso `Contents: read/write`, **vence ~2026-08-26**. Al vencer, limpiar la credencial guardada con `git credential reject` (protocol=https, host=github.com) antes de autenticar con uno nuevo. |

## Fundación (completa, aprobada -- sin cambios esta sesión)

| Archivo | Estado |
|---|---|
| `voice.md` | Completo (Parte 1 + Parte 2 generada desde la semilla, commit `61aeee4`) |
| `world.md` | Completo, revisado (último cierre: commit `dde01c4`) |
| `characters.md` | Vidal, Sandoz, Chiara y Ferrero completos. **Ledda, Ansermet y Ceruti siguen "ficha pendiente de generación"** -- sin cambios (commit `6f110dc`) |
| `outline.md` | 46 capítulos, Save the Cat + MICE anidado (commit `c85b90f`). **Modificado esta sesión**: Cap. 5 y Cap. 6 reestructurados -- ver "Redacción" abajo |
| `canon.md` | Regenerado sobre los documentos completos, commiteado (`e2233bc`) |

## evaluate.py: `overall_score` ya no lo inventa el juez (bug de anclaje corregido)

**Diagnóstico:** los Cap. 1, 2 y 3 dieron `overall_score` **7.0 exacto**
pese a que sus 9 dimensiones individuales variaban con sentido (medias
de 7.33 / 7.00 / 7.56 respectivamente). `overall_score` era un campo
suelto en el JSON que el juez armaba, sin ninguna fórmula que lo atara
a las dimensiones que sí puntuaba, y el propio `CHAPTER_PROMPT` lo
anclaba con "el capítulo mediano de IA es un 6, un 8 es excepcional"
repetido dos veces más un `CHEQUEO FINAL` que solo corrige hacia abajo.
Detalle completo del diagnóstico (simulación contra los 3 eval_logs
reales, comparación de fórmulas) en el historial de esta sesión; no se
repite acá.

**Arreglo (commit `b5ac02d`):** se sacó `overall_score` del JSON pedido
al juez. Ahora se calcula en `evaluate_chapter()`:
`extraer_dimensiones(result)` toma cualquier valor con `"score"`
numérico (no asume un set fijo de 9 -- sobrevive a que `CHAPTER_PROMPT`
gane o pierda dimensiones), y `calcular_overall()` aplica
`0.7 * media + 0.3 * mínimo`, para que una sola dimensión floja pese en
vez de diluirse. El `slop_penalty` mecánico se sigue restando después,
igual que antes. `CHEQUEO FINAL` y `CALIBRACIÓN DE PUNTAJE` del prompt
quedaron intactos a propósito -- se evalúan por separado, no se tocaron
esta vez. Umbral de aceptación sin cambios (6.5/7.5/6.0 por ambición).

**Validación:** control negativo con `ch_02.md` degradado a mano
(calcos del inglés, adverbios en acotaciones, tríadas sensoriales,
explicar-tras-mostrar) dio `overall_score` 0.52 contra 6.7 del
original, con las 9 dimensiones y el `slop_penalty` mecánico
coincidiendo en la degradación. Cubierto por `tests/test_evaluate.py`
(incluye regresión contra los valores reales de Cap. 2 y Cap. 3).

**Nota importante para leer eval_logs viejos:** los Cap. 1, 2 y 3 se
evaluaron **antes** de este fix -- sus `eval_logs/*.json` tienen el
`overall_score` viejo (7.0 plano), no el recalculado. No se
re-evaluaron retroactivamente. El Cap. 4 es el primer capítulo
evaluado con la agregación nueva.

## Redacción

`chapters/ch_01.md` ("Intervalo") -- sin cambios esta sesión. Escrito
**antes** del fix de la Tarea 10 (canon.md no llegaba al prompt real).
Sigue sin re-redactarse -- pregunta abierta, ver "Pendiente".

`chapters/ch_02.md` ("La unidad de medida") -- sin cambios esta sesión.
Aceptado (`overall_score` 7.0 con la fórmula vieja; umbral 6.5). Las
dos decisiones creativas que había dejado abiertas (fecha `C02-06`,
hilo de Halevi) siguen resueltas desde la sesión anterior.

`chapters/ch_03.md` ("Ruido") -- escrito y aceptado esta sesión
(`overall_score` 7.0, fórmula vieja -- se evaluó antes del fix). El
juez marcó `CONFLICTO` [C03-07]: Ruti le pregunta un resultado a Vidal
tras dos semanas de no comentar nada, en tensión con [C01-08] ("no
comenta resultados"). **Resuelto**: no es contradicción, es ruptura
deliberada de un patrón -- se ajustó [C01-08] en `canon_emergente.md`
para que declare el patrón "como norma" en vez de regla absoluta, y se
registra la pregunta como la excepción que lo confirma. No se tocó la
prosa de `ch_03.md` (se conservó el párrafo de la abuela/directora/fila
de octubre completo, contra la sugerencia de recorte del juez). Sí se
le sacó el número "cuarenta y una personas" a la línea de la fila de
octubre (quedó "una fila frente a una tumba sin nada adentro") porque
ese número le pertenece al Cap. 5 como Catalyst.

`chapters/ch_04.md` ("Día sin datos") -- escrito y aceptado esta sesión.
**Primer capítulo evaluado con la agregación nueva de `evaluate.py`**:
`overall_score` 6.48 (agregado 6.78, `slop_penalty` 0.3), umbral 6.0
(ambición "valle") -- ya no cae en el 7.0 plano de antes. El juez marcó
`CONFLICTO` [C04-06]: el capítulo decía que la planilla entera replica
a Zúrich, en tensión con el Secreto 2 de Vidal (`characters.md`: la
planilla de "tiempo perdido" es su único archivo sin respaldo).
**Resuelto**: gana la fundación -- se borró de `ch_04.md` la frase que
generalizaba el respaldo a "todo lo suyo"; no se reemplazó por una
admisión explícita de la excepción, para no convertir el plant del
hilo #1 en anuncio antes de tiempo. También se corrigió a mano (fuera
de un `CONFLICTO` formal, señalado solo en la nota de `continuity` del
eval) un choque de cronología: el Cap. 4 hacía que Vidal reconociera la
fachada del Sepulcro "desde octubre" en la misma frase que ya lo hacía
la primera vez -- se dejó como reconocimiento, no descubrimiento.

`chapters/ch_05.md` ("Cuarenta y una personas", Catalyst) -- **se
reescribió entero**, no en parches, después de dos rechazos. Ver
sección dedicada abajo.

## Cap. 5: por qué se reescribió entero

El primer borrador dejaba a Vidal midiendo la fila del Sepulcro desde
afuera, observando salir a una mujer, sin entrar nunca al edículo. Pasó
tres rondas de revisión quirúrgica (fecha, repeticiones, categorías
desiguales, densidad de rayas parentéticas) y quedó rechazado dos
veces: 7.17 y 7.31 contra el umbral de 7.5 (ambición "pico").

Antes de una cuarta ronda de pulido, se revisó el outline completo
(Cap. 6 a 46) para chequear si algo dependía de que Vidal se hubiera
quedado afuera. Encontró lo contrario: **el Cap. 46 ("La fila", Final
Image) depende de una primera entrada al edículo que el Cap. 5 nunca
había dramatizado** -- "Entra al edículo. Adentro no hay nada,
exactamente como la primera vez" no tiene con qué reflejarse si esa
primera vez no ocurrió en la página. El techo de engagement que tres
rondas de pulido no movieron no era un problema de prosa: era que al
beat le faltaba la mitad de la acción que el libro necesita.

Se actualizó `outline.md` (commit `52be40f`) -- Cap. 5 gana un beat
nuevo (entra al edículo, decisión suya, no itinerario; clímax en los
dos minutos adentro) y sube su objetivo de palabras de 1600 a 1900; se
restauró la frase exacta "error de método" en el beat de la mujer que
sale, porque el Cap. 44 la cita casi textual, escalada a "dos millones
de personas" -- vocabulario de perito con eco de arco, no genérico. Con
el outline corregido, se redactó el capítulo de cero (commit `45cc0f1`).

**Lo crítico de la escena nueva, por pedido explícito:** adentro del
edículo no pasa nada -- sin emoción nombrada, sin epifanía, sin nada
que se lea como experiencia religiosa. Lo único que falla es el propio
conteo interno de Vidal (su tic anti-emoción), sin causa asignable. La
formulación tuvo que ajustarse una vez más: "ninguna [causa] alcanzaba
el rango de interrupción" certificaba ausencia de causa y cerraba la
ambigüedad que es el compromiso central del libro; quedó "repasó las
candidatas [...] no cerró en ninguna" -- un perito dice "no la tengo",
no "no existe".

`overall_score` final: **7.54**, aceptado (umbral 7.5).

El bloque que se cortó del borrador viejo (el vuelo, la búsqueda
"resurrección — evidencia", el memorial de d'Arcis, la primera mención
de la Sábana) no se descartó: quedó guardado en
`briefs/cap06_apertura.md` para usarlo como apertura del Cap. 6 --
fusionado con sus beats existentes, no pegado encima (ya cubría el
memorial de d'Arcis y el resultado radiocarbónico de 1988 que el
outline viejo de Cap. 6 iba a redactar de nuevo). El outline de Cap. 6
ya está actualizado para reflejar la fusión (commit `1c5445b`): 2 beats
en vez de 4, objetivo de palabras 2000 -> 2450.

Durante la resolución de canon del Cap. 5 se confirmó que **todo el
Acto I (Cap. 1-11) transcurre en octubre de 2032** -- la fundación
(`canon.md`/`world.md`) ya lo decía en una sola línea compacta, y el
outline no la contradice, solo la reparte en capítulos con referencias
relativas de día ("el jueves", "el viernes"). Ese hallazgo generó una
entrada nueva, no bloqueante, en `docs/HALLAZGOS.md` -- ver "Pendiente".

## Bugs de compatibilidad con Fable 5 (sesión anterior, sin cambios)

Sin novedades esta sesión. Detalle completo en la versión anterior de
este documento / `docs/ESTADO.md`.

## Tarea 12 -- guardia de contaminación en los prompts (sin cambios)

Sigue completa. `tests/test_guardia_prompts.py::DEUDA_CONOCIDA` sigue
siendo la fuente de verdad. Se verificó esta sesión que editar
`CHAPTER_PROMPT` (para sacarle `"overall_score": N`) no rompió el
registro de hashes -- no estaba en la lista de contaminados.

## Tarea 10 -- acumulación de canon durante la redacción (en producción real)

El mecanismo (`canon_emergente.md` + `actualizar_canon.py`) ya tiene
mileage real: 5 capítulos acumulados, con **cuatro** `CONFLICTO`
detectados y resueltos a mano en esta sesión sola (Ruti, Zúrich,
cronología del Sepulcro implícita en `continuity`, y la fundación
compacta vs. outline granular del Cap. 5). El patrón de resolución que
se consolidó: dejar el `CONFLICTO` en el archivo, cambiar la etiqueta
por un comentario `<!-- Resuelto a mano: ... -->` con la razón, y
vaciar la entrada correspondiente de `state.json::debts`. Nunca se editó
a mano ninguna entrada que no estuviera marcada `CONFLICTO`, salvo
[C01-08] (ajuste de redacción justificado por la resolución de
[C03-07]).

## Pendiente (no bloqueante)

- **Decidir qué hacer con `ch_01.md`.** Sin cambios desde la sesión
  anterior -- se redactó con el bug de canon de la Tarea 10 activo.
  Sigue sin decidirse si vale la pena releerlo/rehacerlo.
- **Tarea 11** -- punto de aprobación manual por capítulo en
  `run_pipeline.py`. Sin cambios; se sigue aprobando capítulo a
  capítulo a mano, leyendo el archivo.
- **Tareas 1b, 1b-bis y 13** -- traducir los prompts contaminados que
  encontró la Tarea 12. Sin cambios; detalle en
  `tests/test_guardia_prompts.py::DEUDA_CONOCIDA`.
- **Fichas completas** de Ledda, Ansermet y Ceruti en `characters.md`.
  Sin cambios.
- **Merge de las Tareas 8, 9 y 9b** hacia `framework/es-multilibro`.
  Sin cambios.
- **Nueva: fijar un calendario de días concretos para el Acto I**
  (Cap. 1-11, todo en octubre de 2032). Con tres días de la semana ya
  nombrados en capítulos consecutivos (Cap. 3/4/5: jueves, viernes,
  sábado) y ninguna fecha ancla, la próxima referencia relativa
  ("la semana que viene", "dentro de diez días") no tiene con qué
  cotejarse. Detalle y propuesta de arreglo en `docs/HALLAZGOS.md`,
  última entrada. No se resuelve ahora, a pedido explícito.
- **Nueva: revisar `CHEQUEO FINAL` y `CALIBRACIÓN DE PUNTAJE` de
  `CHAPTER_PROMPT`** (`evaluate.py`). Se dejaron intactos a propósito
  al arreglar la agregación de `overall_score` -- siguen instruyendo al
  juez con el lenguaje que originó el ancla ("el capítulo mediano de IA
  es un 6"), aunque ya no controlan el campo final. Evaluar si conviene
  limpiarlos ahora que no hacen el daño que hacían antes, o si vale la
  pena dejarlos como filtro adicional de calibración.

## Próximo paso

**Escribir el Cap. 6** ("Bibliografía hostil") con el standalone. El
outline ya está actualizado (2 beats, objetivo 2450 palabras) y el
material de apertura (el vuelo, d'Arcis, el resultado de 1988) está
listo en `briefs/cap06_apertura.md` -- fusionarlo con el beat 2
existente (Secondo Pia, STURP), no pegarlo encima del outline viejo.

```bash
uv run python draft_chapter.py 6
uv run python evaluate.py --chapter=6
uv run python actualizar_canon.py 6
```

**Ojo:** el número de capítulo va posicional
(`chapter_num = int(sys.argv[1])` en `draft_chapter.py`) -- no hay flag
`--chapter` para ese script (sí lo tiene `evaluate.py`). Leer cada
capítulo antes de avanzar al siguiente. Revisar `canon_emergente.md`/
`state.json::debts` por si el juez marcó algo -- no se resuelve solo, y
esta sesión mostró que puede haber más de un `CONFLICTO` por capítulo.

**Advertencia que ya costó una reescritura entera esta sesión:** antes
de aceptar un capítulo con puntaje bajo el umbral tras varias rondas de
pulido, revisar si el problema es de prosa o si el propio outline (en
particular capítulos lejanos, como pasó con el Cap. 46 respecto del
Cap. 5) exige un beat que el capítulo actual no tiene. Pulir prosa
sobre una estructura incompleta no mueve el puntaje.

## Cómo retomar

1. `git status` -- confirmar que el working tree sigue limpio.
2. `git log origin/novela2..HEAD --oneline` -- confirmar que no quedó
   nada sin pushear.
3. `uv run python -m pytest tests/ -v` -- confirmar 246 en verde y 38
   xfail esperados (ninguno inesperado) antes de tocar nada.
4. `cat state.json` -- `debts` debería estar `[]`.
5. Leer `briefs/cap06_apertura.md` y la entrada de Ch. 6 en
   `outline.md` antes de redactar, para fusionar en vez de acumular.
6. Redactar Cap. 6 a mano con el standalone:
   `uv run python draft_chapter.py 6` → `evaluate.py --chapter=6` →
   `actualizar_canon.py 6`. Leer el capítulo y el canon emergente antes
   de avanzar.
