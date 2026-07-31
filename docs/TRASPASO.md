# TRASPASO — rama `novela2` (worktree de `framework/es-multilibro`)

Estado real al cierre de esta sesión (2026-07-29). Este documento
reemplaza la necesidad de releer `ESTADO.md` completo o el historial de
commits para retomar el trabajo -- es la foto actual, no la bitácora
(para eso está `ESTADO.md`, que sí es narrativo y ahora tiene una
sección nueva para esta rama).

**Nota de fusión:** este archivo tuvo dos versiones divergentes -- una
escrita en una sesión anterior de hoy mismo y subida directo a GitHub
(commit `8f9f67d`, "Add files via upload"), y esta reescritura, hecha
sin saber de la otra. Lo que sigue es la fusión de las dos, con el
contenido más al día de cada una.

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

Fundación completa y aprobada (voz, mundo, personajes, esquema de 46
capítulos, canon), Cap. 1 escrito y aprobado, y el cliente de API
(`api_comun.py`) reparado y probado contra la API real tras varios
choques con reglas específicas de Fable 5 que `framework/es-multilibro`
nunca conoció -- esa rama nunca corrió contra la API real. La Tarea 12
encontró que los prompts de juez (y seis generadores más) seguían en
inglés/calibrados contra fantasía pese a que la Tarea 1 se leía como
cerrada -- ver "Tarea 12" abajo. **La Tarea 10 (memoria de canon
durante la redacción) ya está completa** -- ver esa sección. Falta
decidir la Tarea 11 (aprobación por capítulo) antes de seguir
redactando, y de paso quedó una decisión abierta sobre si releer/rehacer
`ch_01.md` (ver "Pendiente" abajo).

## Estado del repositorio

| | |
|---|---|
| Directorio | `/root/novela2` (worktree; confirmado con `git worktree list`) |
| Rama | `novela2`, diverge de `framework/es-multilibro` en `7b81700` (Tarea 7) |
| `.env` / `ANTHROPIC_API_KEY` | **Presente en este entorno** (a diferencia de `framework/es-multilibro`, donde nunca existió). `AUTONOVEL_WRITER_MODEL=claude-fable-5`, `AUTONOVEL_JUDGE_MODEL=claude-opus-5`, `AUTONOVEL_REVIEW_MODEL=claude-opus-5`, `AUTONOVEL_API_BASE_URL=https://api.anthropic.com` |
| Push | Al día con `origin/novela2` una vez fusionado y pusheado este commit. |
| Working tree | Los cambios de la Tarea 10 (ver esa sección abajo) están armados pero **todavía sin commitear** al cierre de esta sesión -- confirmar con `git status` antes de asumir que ya se pusheó. `canon.md` sigue commiteado sin cambios; `world.md.regenerado` (una regeneración fallida, ver Fundación abajo) se borró en la sesión de la Tarea 12 -- nunca estuvo trackeado. |
| Tests | `uv run python -m pytest tests/ -v` -- **237 tests, todos en verde, + 37 xfail esperados** (12 género / 19 idioma / 6 normas del castellano -- Tarea 12: deuda de prompts registrada a propósito, no fallas -- ver "Tarea 12" abajo). Bajó de 40 a 37 xfail porque la Tarea 10 tradujo `CHAPTER_PROMPT` y borró sus tres entradas del registro. No hace falta `.env` (todo mockeado). |
| Token de GitHub | Fine-grained, creado 2026-07-27, alcance `suazoca/autonovel`, permiso `Contents: read/write`, **vence ~2026-08-26**. Al vencer, limpiar la credencial guardada con `git credential reject` (protocol=https, host=github.com) antes de autenticar con uno nuevo. |

## Fundación (completa, aprobada)

| Archivo | Estado |
|---|---|
| `voice.md` | Completo (Parte 1 + Parte 2 generada desde la semilla, commit `61aeee4`) |
| `world.md` | Completo, revisado (último cierre: commit `dde01c4`, "Implicaciones sociales"). **Historia:** una regeneración anterior falló y trajo nombres incorrectos e inconsistentes con el resto de la fundación (`Fondazione Lascaris`/`Horvat Betser`/`Perrin` en vez de `Fondation Cassiodore`/`Horvat Adullam`/`Maître Ansermet`) -- el bueno se recuperó de git a tiempo y quedó commiteado; el archivo suelto de esa regeneración (`world.md.regenerado`) quedó tirado sin trackear hasta que se borró en esta sesión |
| `characters.md` | Vidal, Sandoz, Chiara y Ferrero completos. **Ledda, Ansermet y Ceruti quedan marcados "ficha pendiente de generación"** -- existen en el esquema por función, no tienen ficha propia (commit `6f110dc`) |
| `outline.md` | **46 capítulos**, Save the Cat + MICE anidado, completo (commit `c85b90f`). Se le sacaron dos fragmentos residuales de un empalme roto por `max_tokens` (Ch 23 y Ch 42 -- commits `b0147a1` y `84618e8`) |
| `canon.md` | Regenerado sobre los documentos completos, commiteado (`e2233bc`) |

## Redacción

`chapters/ch_01.md` ("Intervalo") escrito y **aprobado tras lectura** --
la voz se sostiene, el diálogo distingue personajes sin etiquetas, a la
altura del esquema. Commiteado (`aa8efd1`).

**Ojo:** `state.json` sigue en `chapters_drafted: 0` -- no se está
orquestando con `run_pipeline.py`, así que ese contador no refleja la
realidad. No confiar en `state.json` para saber cuántos capítulos hay
escritos; mirar `chapters/` directamente.

## Bugs de compatibilidad con Fable 5 (arreglados hoy, todos commiteados en esta rama)

Ninguno de estos era un problema conocido en `framework/es-multilibro`
porque esa rama nunca corrió contra la API real. Se fueron encontrando
en orden al ejecutar la fundación real por primera vez:

| # | Bug | Commit |
|---|---|---|
| 1 | `temperature` en el payload -- deprecado en Fable 5, tira 400. Quitado de los ~19 scripts | `c8f7b99` |
| 2 | `resp.json()["content"][0]["text"]` asumía que el primer bloque de la respuesta era texto. Fable 5 manda un bloque `thinking` primero, así que esto rompía (bloque equivocado / sin `"text"`) en los ~19 scripts que llamaban a la API directo, antes de que existiera `api_comun.py` | `7b66805` |
| 3 | La plantilla de `voice.md` ("Part 2: Voice Identity...") tenía prosa de ejemplo **fuera** de comentario HTML. La guardia de idempotencia de `gen_voice.py` (línea ~186: saca los `<!-- ... -->` y si queda algo no vacío, asume "ya tiene contenido real, no tocar") confundía esa prosa de plantilla con contenido ya generado y no regeneraba nada -- **en silencio**, sin error. Se corrigió envolviendo esa prosa en un comentario HTML | `7b66805` (mismo commit que el #2) |
| 4 | Tarea 8: streaming centralizado en `api_comun.py` (reemplaza las ~19 copias casi idénticas de `call_writer()`/`call_judge()`/etc. y el timeout fijo bloqueante) | `d03e879` |
| 5 | Tarea 9: continuación automática cuando la respuesta se corta por `stop_reason == "max_tokens"` | `b63a32b` |
| 6 | **Tarea 9b:** el mecanismo de la Tarea 9 usaba *prefill* (terminar la conversación en un turno `assistant`, sin turno de usuario después). Confirmado contra la API real que Fable 5 lo rechaza con 400: *"This model does not support assistant message prefill. The conversation must end with a user message."* Corregido: el texto parcial sigue como turno `assistant`, pero ahora seguido de un turno `user` explícito pidiendo continuar, con recorte de solapamiento sufijo/prefijo en la juntura (`_recortar_solapamiento()`) por si el modelo repite texto al ya no ser prefill literal. Probado contra la API real. De paso se encontró y arregló que `stop_reason == "refusal"` no se manejaba -- el loop lo trataba como `end_turn` y devolvía el texto truncado como si fuera la respuesta completa, sin aviso | `9f28e5f` |

Los fragmentos residuales de `outline.md` (Ch 23, Ch 42) y la
regeneración fallida de `world.md` (Lascaris/Betser) son consecuencia
directa del bug #6 *antes* de corregirse: ambos se generaron con el
prefill viejo.

## Tarea 12 -- guardia de contaminación en los prompts (COMPLETA)

Hallazgo: la Tarea 1 se leía como cerrada porque 1a/1c/1d lo estaban,
pero **1b -- traducir los prompts de juez -- seguía abierta**, y nadie
lo notó porque el encargo agrupa las cuatro bajo un único encabezado. Al
auditar con un chequeo automático en vez de memoria humana, aparecieron
además **seis archivos más** (no jueces) con el mismo problema --
incluidos `gen_outline.py`/`gen_outline_part2.py`, que la Tarea 2b había
declarado cerrados por chequear solo nombres propios de *Bells*, nunca
idioma en general. Detalle completo, con qué se salvó y qué no
(`outline.md` se midió contra el detector mecánico y dio 0 calcos --
no se regenera) en `docs/HALLAZGOS.md`.

**Se agregó `tests/test_guardia_prompts.py`**: descubre automáticamente
(vía `ast`, sin imports ni regex) todo literal de string largo en los
`.py` de la raíz, chequea género (fantasía) e idioma (inglés) sobre todos
esos literales, y exige el bloque de normas del castellano solo en los 7
literales de juez que son la constante `*_PROMPT` con la rúbrica de
evaluación (no en las personas ni en los system prompts sueltos de una
frase, para no incentivar contaminarlos con la frase ancla nada más que
para pasar el guardia). Entre los once archivos afectados quedan 40
literales registrados como deuda conocida con xfail estricto (13 género
/ 20 idioma / 7 normas), clave = hash del contenido, no línea, para que
sobreviva a que un prompt traducido corra las líneas siguientes.

**`tests/test_guardia_prompts.py::DEUDA_CONOCIDA` (y los tres sets de
hashes que la acompañan) es ahora la fuente de verdad de qué prompts
siguen contaminados y qué tarea los arregla -- ya no las notas sueltas
sobre "falta 1b" que había en este documento y en `ESTADO.md`.** No
duplicar ese detalle acá: si un prompt se traduce y alguien olvida
borrar su entrada del registro, el xfail se convierte en XPASS y el
suite se rompe solo -- una nota en prosa en este documento no tiene esa
propiedad, se queda obsoleta en silencio (que es exactamente lo que pasó
con "falta 1b" durante toda esta sesión).

## Tarea 10 -- acumulación de canon durante la redacción (COMPLETA)

Hallazgo de partida: `evaluate.py` reportaba `new_canon_entries` por
capítulo y se tiraban -- un hecho inventado en el Cap. 7 no existía para
el juez ni para el redactor del Cap. 30. `canon.md` era la única
memoria larga del sistema, y era estática (función pura de
semilla+mundo+personajes).

Tres decisiones de diseño, tomadas antes de implementar:

1. **Dos archivos de canon.** `canon.md` sigue siendo función pura de
   semilla+mundo+personajes -- lo pisa `gen_canon.py`, sin tocar. Los
   hechos de redacción van a `canon_emergente.md` (nuevo, formato
   `## Cap. NN` con entradas `[C07-01] (categoría) hecho`, y `CONFLICTO`
   cuando el juez detecta una contradicción). `gen_canon.py` no lo lee
   ni lo escribe nunca -- test dedicado que lo verifica. El archivo
   todavía no existe en el working tree: lo crea `actualizar_canon.py`
   la primera vez que corre (recién con la evaluación del próximo
   capítulo).
2. **`new_canon_entries` pasa a objetos** `{categoria, hecho,
   contradice}` en `CHAPTER_PROMPT` (`evaluate.py`). La detección de
   contradicciones la sigue haciendo el juez -- ya tiene `canon.md` y
   `canon_emergente.md` completos en contexto -- sin ninguna llamada
   extra a la API.
3. **`actualizar_canon.py`** (nuevo, standalone, determinista, sin
   red): `uv run actualizar_canon.py N` busca el eval_log más reciente
   de ese capítulo, reemplaza (no anexa) su sección en
   `canon_emergente.md` -- para que re-evaluar un capítulo (revisión, o
   el bucle de descarte de `run_pipeline.py`) no duplique entradas -- y
   anota los `CONFLICTO` en `state.json::debts` sin frenar la
   ejecución: el juez a veces marca como contradicción una elipsis o el
   mismo hecho dicho distinto, y frenar duro por falsos positivos sería
   peor que anotarlo para revisión manual. Tolera eval_logs viejos con
   `new_canon_entries` en formato de lista de strings (avisa y
   saltea, no rompe).

De paso, `CHAPTER_PROMPT` se tradujo entero al español, se descontaminó
de calibración de fantasía (ahora calibra contra thriller literario
publicado, no contra fantasía) y se le agregó el bloque de normas del
castellano de la sección 1b del encargo -- eso vació las tres entradas
`("evaluate.py", "f645f997")` del registro de `test_guardia_prompts.py`
(ver Tests, arriba).

`draft_chapter.py::build_prompt()` recibe y usa ahora `canon_emergente`
además de `canon`. **Hallazgo colateral importante:** al cablear
`canon_emergente` se descubrió que `canon` (el parámetro ya existente)
se cargaba en `main()` pero **nunca se insertaba en el prompt real** --
bug heredado del primer commit del repo (`4f8f880`), no introducido por
ninguna tarea de esta rama, e invisible a `test_draft_chapter.py`
porque sus llamadas a `build_prompt()` pasaban `canon=""` en los tres
casos. Detalle completo -- cómo se confirmó, en qué commit se originó,
qué capítulos se redactaron a ciegas -- en `docs/HALLAZGOS.md`, entrada
`draft_chapter.py::build_prompt() cargaba canon.md y nunca lo metía en
el prompt`. Ya corregido; no repetir el detalle acá.

`run_pipeline.py` invoca `actualizar_canon.py` después de cada
evaluación de capítulo (líneas ~469, ~643, ~679) -- es secundario, hoy
se sigue redactando con el standalone (`draft_chapter.py` directo, sin
`run_pipeline.py`).

## Pendiente (no bloqueante)

Ordenado por lo que cuesta más si se posterga, no por número de tarea.

- **Decidir qué hacer con `ch_01.md`.** Se redactó con el bug de
  `canon.md` de arriba activo -- el prompt real no tenía ningún hecho
  duro de canon, aunque sí está aprobado por lectura humana. No se
  re-redactó automáticamente. Opciones: dejarlo como está y confiar en
  que el Cap. 2 en adelante ya tiene canon completo (el capítulo de
  apertura tiene poco que contradecir), o releerlo/rehacerlo contra
  `canon.md` antes de escribir el Cap. 2. Sin decidir todavía.
- **Tarea 11** -- punto de aprobación manual por capítulo en
  `run_pipeline.py` (hoy la aprobación del Cap. 1 fue manual/informal,
  leyendo el archivo).
- **Tareas 1b, 1b-bis y 13 -- traducir los prompts contaminados que
  encontró la Tarea 12.** `gen_revision.py` (Tarea 13) es la más urgente
  del grupo: corre en la primera revisión de capítulo real, todavía no
  ejecutada, y sí calibra contra fantasía. El resto del detalle
  (archivo por archivo, qué chequeo falla, qué tarea lo arregla) vive en
  `tests/test_guardia_prompts.py::DEUDA_CONOCIDA` -- no repetirlo acá.
- **Fichas completas** de Ledda, Ansermet y Ceruti en `characters.md`.
  Si aparecen en capítulos redactados antes de tener ficha, el modelo
  les inventa rasgos -- con la Tarea 10 ya completa esos rasgos sí
  quedan registrados en `canon_emergente.md` la próxima vez que se
  evalúe ese capítulo, pero siguen siendo inventados, no lo que el
  usuario habría decidido a mano.
- **Merge de las Tareas 8, 9 y 9b** hacia `framework/es-multilibro` --
  son mejoras al cliente de API en sí, no específicas de esta novela, y
  esa rama todavía tiene el bug de prefill sin corregir si algún día
  corre contra Fable 5.

## Próximo paso

Con la Tarea 10 ya completa, lo que queda por decidir es: qué hacer con
`ch_01.md` (ver "Pendiente" arriba), si hacer la Tarea 11 antes de
seguir (supervisión liviana), o directamente seguir redactando a mano
capítulo por capítulo con el standalone. Si es esto último:

```bash
uv run python draft_chapter.py N
```

**Ojo:** el número de capítulo va **posicional**
(`chapter_num = int(sys.argv[1])` en `draft_chapter.py`) -- **no** hay
flag `--chapter`. Leer cada capítulo antes de avanzar al siguiente, como
se hizo con el Cap. 1.

**Advertencia sobre probar capítulos fuera de orden** (p.ej. uno de Fun
and Games y uno del Acto III, para chequear que la voz aguanta otro
registro antes de decidir): sacados sueltos, esos capítulos se redactan
sin `prev_tail` (el capítulo anterior no existe todavía en esa corrida),
así que no son representativos de la cadena real. Sirven para juzgar
voz, no para juzgar continuidad.

## Herencia del framework (`framework/es-multilibro`)

Tareas 0, 1c, 1d, 2, 2b, 2c, 3, 4, 6 y 7 cerradas y testeadas (113 tests
en verde al cierre de la Tarea 7, ninguno requiere `.env`). Hallazgos
abiertos que siguen vigentes: sesgo de `dividir_oraciones()`,
`umbral_cv_oracion` sin recalibrar, falta de parser del Foreshadowing
Ledger, `libros_completos` sin fuente de datos, y `CRAFT.md` cargado
pero no interpolado en `gen_world.py`/`gen_characters.py`. Detalle
completo en `docs/ESTADO.md` y `docs/HALLAZGOS.md`.

## Cómo retomar

1. `git status` -- confirmar que el working tree sigue limpio.
2. `git log origin/novela2..HEAD --oneline` -- confirmar que no quedó
   nada sin pushear.
3. `uv run python -m pytest tests/ -v` -- confirmar 237 en verde y 37
   xfail esperados (ninguno inesperado) antes de tocar nada.
4. Decidir qué hacer con `ch_01.md` / Tarea 11 / seguir a mano (ver
   "Próximo paso") y, si es lo último,
   `uv run python draft_chapter.py 2` seguido de
   `uv run python actualizar_canon.py 2` una vez evaluado.
