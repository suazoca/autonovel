# ESTADO — rama `framework/es-multilibro` (+ sección `novela2`, 2026-07-29)

Última actualización de la parte original: 2026-07-27 (tras cerrar la
Tarea 7 -- generador de voz). Escrito para retomar en otra sesión sin
releer todo el historial de commits.

**Nota:** `AUDITORIA_Y_PLAN.md` se movió a `docs/AUDITORIA_Y_PLAN.md` en un
commit hecho directamente por el usuario (`48395a8`, fuera de esta
conversación). Las referencias a `AUDITORIA_Y_PLAN.md` sin prefijo en
commits anteriores de este archivo quedan desactualizadas de ruta; no se
corrigieron retroactivamente.

**Nota (2026-07-29):** todo lo que sigue de acá hasta "Sesión `novela2`"
más abajo es historia de `framework/es-multilibro` tal como estaba al
cerrar la Tarea 7, heredada sin cambios porque `novela2` arrancó como
worktree desde ese mismo commit (`7b81700`). Sigue siendo válida como
historia de cómo se construyó el framework, pero **ya no describe el
estado actual de este directorio** (`/root/novela2`) -- para eso,
saltar directo a "Sesión `novela2` (después de la Tarea 7)" o leer
`docs/TRASPASO.md`, que es la foto corta y al día.

## Sesión `novela2` (después de la Tarea 7) — 2026-07-29

`novela2` es un worktree separado de `framework/es-multilibro`
(confirmado con `git worktree list`) que diverge en `7b81700` (cierre de
la Tarea 7) para escribir una novela concreta con el framework ya
construido: **"La ostensión"** (Libro 1), a partir de `semilla.txt` --
un científico de IA investigando la Sábana Santa antes de la ostensión
de 2033. A diferencia de `framework/es-multilibro`, acá **sí existe
`.env`** con `ANTHROPIC_API_KEY` real (`AUTONOVEL_WRITER_MODEL=claude-fable-5`,
`AUTONOVEL_JUDGE_MODEL`/`AUTONOVEL_REVIEW_MODEL=claude-opus-5`), así que
por primera vez se pudo correr la fundación completa contra la API real
-- y eso destapó una serie de incompatibilidades con Fable 5 que
`framework/es-multilibro` nunca había podido descubrir, porque nunca
corrió contra el modelo real.

### Commits de esta rama (desde que diverge de `framework/es-multilibro`)

```
c8f7b99 fix: elimina temperature del payload (deprecado en Fable 5)
7b66805 fix: compatibilidad con Fable 5 (temperature deprecado, bloque thinking en la respuesta)
61aeee4 voz: Parte 2 generada desde la semilla
d03e879 Tarea 8: streaming en call_writer()/call_judge() vía api_comun.py
b63a32b Tarea 9: continuación automática cuando la respuesta se corta por max_tokens
aab3af4 novela: fundación generada (voz, mundo, personajes, esquema hasta Ch 42)
c85b90f novela: esquema completo, 46 capítulos
b0147a1 esquema: quita fragmento residual de la continuación
9f28e5f Tarea 9b: corrige el mecanismo de continuación (Fable 5 rechazaba el prefill de assistant) y agrega manejo de stop_reason=refusal
dde01c4 world.md: completa el cierre de Implicaciones sociales
6f110dc characters.md: completa secretos de Ferrero, marca Ledda/Ansermet/Ceruti como pendientes
aa8efd1 Cap. 1: Intervalo
84618e8 esquema: quita los dos fragmentos residuales de continuación que quedaron (Ch 23, Ch 42)
```

`origin/novela2` está 4 commits atrás de `HEAD` al cierre de esta sesión
(`dde01c4` en adelante) -- confirmar con
`git log origin/novela2..HEAD --oneline`.

### Bugs de compatibilidad con Fable 5, en el orden en que aparecieron

Todos se dispararon la primera vez que se corrió algo contra la API real
en esta línea de trabajo -- ninguno era detectable sin `.env`, y por eso
`framework/es-multilibro` nunca los vio.

1. **`temperature` deprecado en Fable 5 (400).** El payload de los ~19
   scripts (`call_writer()`/`call_judge()`/etc., todavía sin centralizar
   en este punto) mandaba `"temperature": 0.8` (o `1.0` en `seed.py`).
   Fable 5 rechaza el parámetro directamente. Fix: sacarlo de los 19
   payloads (`c8f7b99`).

2. **Parseo de la respuesta asumía que el primer bloque de contenido era
   texto.** `resp.json()["content"][0]["text"]` funcionaba con modelos
   sin razonamiento extendido, pero Fable 5 manda un bloque `type:
   "thinking"` primero -- `content[0]` deja de ser el texto. Fix:
   filtrar por `b.get("type") == "text"` en vez de indexar por posición
   (`7b66805`).

3. **La guardia de idempotencia de `gen_voice.py` se rompía en
   silencio.** La plantilla de `voice.md`, sección "Part 2: Voice
   Identity (generated per novel)", tenía dos líneas de prosa
   explicativa **fuera** de comentario HTML. `gen_voice.py` decide si ya
   generó la voz sacando los bloques `<!-- ... -->` del cuerpo de esa
   sección y comprobando si queda algo (línea ~186: `sin_comentarios =
   re.sub(r'<!--.*?-->', '', cuerpo_actual, ...).strip(); if
   sin_comentarios: continue`). Esa prosa de plantilla, al no estar
   comentada, contaba como "contenido real" -- el script asumía que la
   voz ya estaba generada y nunca llamaba a la API, sin ningún error ni
   aviso. Fix: envolver esa prosa en el comentario HTML (`7b66805`,
   mismo commit que el bug #2).

4. **Tarea 8 -- streaming centralizado.** Con los tres bugs anteriores
   ya resueltos de forma parchada en cada script, se centralizó todo en
   `api_comun.py::llamar_api()`: streaming (`stream: true`) en vez de
   una sola respuesta no incremental, para no perder generaciones ya
   pagadas si un timeout fijo cortaba antes de que terminara de llegar
   la respuesta completa. Cada script conserva su propio
   `call_writer()`/`call_judge()` como wrapper de una línea sobre
   `llamar_api()` (`d03e879`).

5. **Tarea 9 -- continuación automática por `max_tokens`.** Pasó dos
   veces en la primera corrida real de la fundación: `outline.md` cortó
   en Ch 23 de 46, la segunda mitad del esquema cortó en Ch 42 -- porque
   nada avisaba que `stop_reason == "max_tokens"` significa que la
   respuesta no está completa. `llamar_api()` empezó a seguir pidiendo
   más automáticamente hasta `stop_reason == "end_turn"` (tope
   `max_continuaciones`) (`b63a32b`). El mecanismo elegido en esta
   versión era **prefill**: mandar el texto acumulado como último
   mensaje de la conversación con `role: "assistant"`, sin turno de
   usuario después.

6. **Tarea 9b -- el prefill de la Tarea 9 lo rechazaba Fable 5.**
   Confirmado contra la API real: 400, *"This model does not support
   assistant message prefill. The conversation must end with a user
   message."* Los tests con mock de la Tarea 9 nunca lo habrían
   detectado porque el mock no valida reglas de la API real -- pasaron
   en verde con un mecanismo que la API real rechazaba. Corregido: el
   texto parcial sigue yendo como turno `assistant` (eso la API sí lo
   acepta -- lo que rechaza es que sea el *último* turno), pero ahora
   seguido de un turno `user` explícito (`MENSAJE_CONTINUAR`) pidiendo
   que continúe sin repetir texto ni agregar comentario. Como ya no es
   prefill literal, se agregó `_recortar_solapamiento()`: compara el
   sufijo del texto acumulado contra el prefijo de cada continuación
   nueva y recorta la repetición si el modelo repite la última
   palabra/frase pese a la instrucción. **Probado contra la API real**
   (`claude-fable-5`, `max_tokens` bajo forzado a propósito): confirmó
   que el 400 desapareció en dos continuaciones sucesivas. La misma
   prueba destapó un séptimo bug -- `stop_reason == "refusal"` no se
   manejaba: el loop lo trataba igual que `end_turn` y devolvía el texto
   acumulado como si fuera la respuesta completa, truncado a media
   frase, sin ningún aviso. Se agregó el chequeo explícito con
   `sys.exit` (`9f28e5f`).

Los dos fragmentos residuales que quedaron en `outline.md` (Ch 23 con un
header truncado a media palabra + header duplicado
`*(continuación)*`; Ch 42 con un header vacío duplicado) son la
evidencia directa del bug #6 *antes* de corregirse -- `outline.md` se
generó con el prefill viejo. Uno se había limpiado ya (`b0147a1`); los
dos que quedaban se limpiaron en esta sesión (`84618e8`). En ningún caso
se perdía contenido: `extract_chapter_outline()` en `draft_chapter.py`
igual capturaba el texto completo (el regex no se corta en headers
intermedios), pero el prompt que se le mandaba al modelo para esos dos
capítulos quedaba con el fragmento roto visible.

### Fundación y redacción

- `voice.md`, `world.md`, `characters.md` (salvo tres fichas: **Ledda,
  Ansermet y Ceruti quedan marcadas "ficha pendiente de generación"**),
  `outline.md` (**46 capítulos**) y `canon.md` -- generados y revisados.
- `chapters/ch_01.md` ("Intervalo") escrito y **aprobado tras lectura**
  -- la voz se sostiene, el diálogo distingue personajes sin etiquetas
  (`aa8efd1`).
- `state.json` no se está actualizando (`chapters_drafted: 0` pese a que
  ya hay un capítulo escrito) porque no se está orquestando con
  `run_pipeline.py` -- no confiar en ese archivo para saber cuántos
  capítulos hay, mirar `chapters/` directamente.
- Working tree con dos cosas sin resolver, sin investigar a fondo en
  esta sesión: `canon.md` tiene cambios sin commitear de antes de esta
  sesión, y hay un archivo sin trackear `world.md.regenerado` (una
  regeneración alternativa de `world.md`).

### Tests

`uv run python -m pytest tests/ -v` -- **237 tests pasando + 37 xfail
esperados** (eran 217+40 al cierre de la Tarea 12 -- ver abajo. La
Tarea 10 agregó 17 tests nuevos: 15 en `tests/test_actualizar_canon.py`,
2 en `tests/test_draft_chapter.py`. Además, al traducir `CHAPTER_PROMPT`
se borraron del registro de `test_guardia_prompts.py` las tres entradas
`("evaluate.py", "f645f997")` -- una por cada uno de los tres sets
(género/idioma/normas del castellano) -- que pasaron de xfail a passed:
217+17+3=237 passed, 40-3=37 xfail. De los 37 xfail que quedan, 12 son
de género, 19 de idioma y 6 del bloque de normas del castellano. Son
deuda de prompts registrada a propósito, no fallas: si alguno pasa a
XPASS sin que se haya borrado su entrada del registro, el suite se
rompe). Sigue sin necesitar `.env` -- todo mockeado.

### Tarea 12 -- guardia de contaminación en los prompts (COMPLETA)

La Tarea 1 se leía como cerrada (1a/1c/1d lo estaban) pero **1b --
traducir los prompts de juez a español -- seguía abierta**, sin que nada
lo señalara. Auditar con un chequeo automático (no memoria humana)
encontró además el mismo problema en seis archivos no-juez, incluidos
dos que la Tarea 2b había dado por cerrados (`gen_outline.py`,
`gen_outline_part2.py` -- esa tarea solo chequeó nombres propios de
*Bells*, nunca idioma en general). Detalle completo en
`docs/HALLAZGOS.md`.

`tests/test_guardia_prompts.py` descubre los prompts vía `ast` (no
imports -- estos módulos hacen `load_dotenv()` al importarse -- ni
regex) y chequea género/idioma/normas del castellano automáticamente.
**Su `DEUDA_CONOCIDA` (y los sets de hashes que la acompañan) es ahora
la fuente de verdad de qué prompts siguen contaminados y qué tarea los
arregla -- no lo repitas en prosa acá ni en `TRASPASO.md`.** Una nota
suelta como "falta 1b" puede quedar desactualizada en silencio (pasó
durante toda esta sesión); una entrada de xfail estricto no puede: si el
prompt se traduce y la entrada no se borra, el suite se rompe solo.

### Tarea 10 -- acumulación de canon durante la redacción (COMPLETA)

Hasta esta tarea, `evaluate.py` reportaba `new_canon_entries` por
capítulo y se tiraban: un hecho inventado en el Cap. 7 no existía para
el juez ni para el redactor del Cap. 30. Tres decisiones de diseño (ya
tomadas antes de empezar):

1. **Dos archivos de canon.** `canon.md` sigue siendo función pura de
   semilla+mundo+personajes -- lo pisa `gen_canon.py`, sin tocar. Los
   hechos de redacción van a `canon_emergente.md` (nuevo, formato
   `## Cap. NN` con entradas `[C07-01] (categoría) hecho`), que
   `gen_canon.py` no lee ni escribe nunca -- así se puede regenerar la
   fundación sin perder lo acumulado. Todavía no existe en el
   working tree: lo crea `actualizar_canon.py` la primera vez que corre.
2. **`new_canon_entries` pasa a objetos** `{categoria, hecho,
   contradice}` en `CHAPTER_PROMPT` (`evaluate.py`). La detección de
   contradicciones la sigue haciendo el juez (ya tiene todo el canon --
   fundación y emergente -- en contexto); no se agregó ninguna llamada
   extra a la API.
3. **`actualizar_canon.py`** (nuevo, standalone, sin red): `uv run
   actualizar_canon.py N` busca el eval_log más reciente de ese
   capítulo, reemplaza (no anexa) su sección en `canon_emergente.md` --
   para que re-evaluar un capítulo no duplique entradas -- y anota los
   `CONFLICTO` en `state.json::debts` sin frenar la ejecución: el juez
   a veces marca como contradicción una elipsis o el mismo hecho dicho
   distinto, y frenar duro por falsos positivos sería peor que anotarlo
   para revisión manual.

De paso, `CHAPTER_PROMPT` se tradujo entero al español, se descontaminó
de calibración de fantasía (ahora calibra contra thriller literario
publicado) y se le agregó el bloque de normas del castellano de la
sección 1b del encargo -- ver el diff en `docs/TRASPASO.md` o
directamente `evaluate.py`.

`draft_chapter.py::build_prompt()` recibe y usa ahora `canon_emergente`
además de `canon`. De paso se encontró y corrigió un bug preexistente
en ese mismo archivo (heredado del primer commit del repo, no
introducido por ninguna tarea de esta rama): `canon` se cargaba pero
nunca se insertaba en el prompt de redacción real -- detalle completo,
incluyendo qué capítulos se redactaron sin canon y por qué el suite no
lo agarró, en `docs/HALLAZGOS.md`.

`run_pipeline.py` invoca `actualizar_canon.py` después de cada
evaluación de capítulo (líneas ~469, ~643, ~679) -- es secundario, el
camino real de uso hoy sigue siendo el standalone.

**Pendiente de decisión, no bloqueante:** `ch_01.md` se escribió con el
bug de `canon.md` activo (ver arriba) y **no se re-redactó
retroactivamente**. Falta decidir si conviene releerlo/rehacerlo contra
`canon.md` antes de avanzar al Cap. 2, o si el capítulo se sostiene tal
como está (ya está aprobado por lectura humana) y se sigue para
adelante confiando en que el Cap. 2 en más sí va a tener el canon
completo disponible.

### Qué sigue

- **Tarea 11** (pendiente, no bloqueante): punto de aprobación manual
  por capítulo antes de seguir al siguiente (hoy es informal, leyendo el
  archivo).
- **Tareas 1b, 1b-bis y 13** (pendiente, no bloqueante): traducir los
  once literales que dejó registrados la Tarea 12 -- ver
  `tests/test_guardia_prompts.py::DEUDA_CONOCIDA` para el detalle exacto
  y `docs/HALLAZGOS.md` para el porqué. `gen_revision.py` (Tarea 13) es
  la más urgente: corre en la primera revisión de capítulo real,
  todavía no ejecutada.
- Fichas completas de Ledda, Ansermet y Ceruti en `characters.md`.
- Mergear las Tareas 8, 9 y 9b hacia `framework/es-multilibro` cuando
  convenga -- son mejoras al cliente de API en sí, no específicas de
  esta novela, y esa rama sigue con el bug de prefill sin corregir si
  algún día corre contra Fable 5.
- Seguir escribiendo capítulos: `uv run python draft_chapter.py N`
  (**el número va posicional, `sys.argv[1]` -- no hay flag
  `--chapter`**), leyendo cada uno antes de avanzar (no hay
  automatización de aprobación todavía).

Para el detalle completo con tablas y commits exactos, ver
`docs/TRASPASO.md`.

## Punto de partida que sigue vigente

- **No existe `.env`** en este entorno (ni `ANTHROPIC_API_KEY`). Nada que
  dependa del juez LLM se puede probar hasta que exista.
- **No existe la rama `autonovel/bells`** en este remoto (confirmado con
  `git fetch --all` + `git ls-remote --heads origin`). No hay comparación
  disponible contra la novela anterior en inglés; toda la línea base se
  armó con fixtures de prueba en español, no con capítulos reales.
- **Push: al día hasta `4ad70b7`** (Tarea 2c). Confirmar con
  `git log origin/framework/es-multilibro..HEAD --oneline` si algo quedó
  sin pushear después de este documento.
  **RESUELTO: los cuatro tokens de GitHub que quedaron expuestos en el
  chat en una sesión anterior** (pegados mal en la terminal, en varios
  intentos de push) **están revocados**, confirmado por el usuario. Sin
  verificación pendiente. Queda el registro de que ocurrió y cómo se
  evita, más abajo.

  **Por qué falla `git push` corrido con `!` (y cómo se resuelve):** el
  prefijo `!` ejecuta el comando sin TTY -- `git` no tiene dónde mostrar
  el prompt de usuario/contraseña y aborta con *"could not read Username
  for 'https://github.com': No such device or address"*. No es un
  problema de que el token quede visible; es que no hay terminal
  interactiva para pedirlo. La receta que funcionó para el push de la
  Tarea 6: **salir de Claude Code con Ctrl+D** (misma terminal, no una
  distinta), correr `git push` ahí directamente, pegar el token cuando lo
  pida, volver a entrar con `claude`. Con `credential.helper store` ya
  configurado (`~/.git-credentials`), esto solo hace falta una vez -- los
  próximos `git push` (incluso corridos con `!`) reusan la credencial
  guardada sin pedir nada.

  **Token vigente:** fine-grained, creado el 2026-07-27, alcance limitado
  a `suazoca/autonovel`, permiso `Contents: read/write` únicamente,
  **vence a los 30 días (~2026-08-26)**. Cuando venza, el `git push`
  guardado va a fallar reusando la credencial vieja -- limpiarla primero
  con `git credential reject` (protocol=https, host=github.com) antes de
  autenticar de nuevo con un token nuevo, o `git push` va a seguir
  reintentando la credencial vencida y fallando igual.

## Commits de esta rama (orden cronológico)

```
3ded223 docs: auditoría, plan de adaptación y módulo de detección en español  (llegó por git pull, no generado en esta sesión)
7346d77 Tarea 0: línea base con fixtures en español
214768e fix: IGNORECASE en calcos_detectados + corrección del test 6
625fc7f Tarea 1c (A): flag --solo-mecanico en evaluate.py
975ac18 Tarea 1c (B): integra deteccion_es.py en slop_score()
49a5976 Tarea 1d: fixtures mínimos de voz y mundo en español
76454a5 docs: ESTADO.md para retomar sin releer el historial
04b6439 Tarea 2: descontamina draft_chapter.py y gen_brief.py
4ad802c docs: ESTADO.md al día con el cierre de la Tarea 2
5af3cb9 Tarea 3: campo de ambición por capítulo (pico | sosten | valle)
d3c4c72 fix: palabras_objetivo_capitulo=2000 (era 3800, error de mi sesión anterior)
506f435 Tarea 4: alcance de siembra para series (libro | serie)
df7b06c docs: suma gen_outline_part2.py a la Tarea 2b, documenta dependencia de libros_completos
c513adf docs: ESTADO.md al día con el cierre de la Tarea 4
5a78c52 Tarea 2b: descontamina gen_outline.py y gen_outline_part2.py
648b0c3 docs: ESTADO.md al día con el cierre de la Tarea 2b
2b31156 docs: TRASPASO.md -- estado real para retomar sin releer ESTADO.md completo
b18ca4a docs: corrige el conteo de tokens expuestos (cuatro, no dos) y el estado del push
48395a8 docs: mueve AUDITORIA_Y_PLAN.md a docs/                          <- del usuario, no de esta conversación
bb4c7ce Tarea 6: persistencia en la fase de fundación
4ad70b7 Tarea 2c: descontamina gen_world.py, gen_characters.py, gen_canon.py
40cfbd5 docs: incidente de tokens pasa a RESUELTO, anota vencimiento del token vigente  <- pusheado hasta acá
                                                                          <- Tarea 7 sigue, sin pushear al escribir esto
```

`1c` y `1d` no estaban en el `ENCARGO_CLAUDE_CODE.md` original -- se
agregaron sobre la marcha (documentadas ahí mismo) porque hacían falta
para que los tests 1 y 2 de la Tarea 1 corrieran sin API.

## Qué está hecho y probado

- **`tests/fixtures/cap_dialogado_es.md`** (624 palabras) y
  **`cap_con_slop_es.md`** (587 palabras, slop sembrado a propósito):
  capítulos de prueba en español, verificados contra `deteccion_es.py`.
- **`deteccion_es.py`**: bug de `calcos_detectados()` (faltaba
  `re.IGNORECASE`) corregido y confirmado con test.
- **`evaluate.py`**:
  - Flag `--solo-mecanico` (+ `--archivo <path>`): corre solo
    `slop_score()`, sin LLM, sin API, determinista.
  - `slop_score()` reemplazado: las listas en inglés (TIER1/2/3,
    FICTION_AI_TELLS, STRUCTURAL_AI_TICS, TELLING_PATTERNS,
    TRANSITION_OPENERS, conteo crudo de em-dash) fueron sustituidas por
    las de `deteccion_es.py` (NIVEL1/2/3, CLICHES_FICCION,
    TICS_ESTRUCTURALES, PATRONES_CONTAR, CONECTORES_APERTURA,
    `densidad_raya_parentetica`, `cv_longitud_oracion`) + penalización
    nueva por calcos del inglés (0.5/calco, tope 2.0). Hardcodeado a
    español, sin flag `--idioma` todavía.
  - Medido antes/después con los dos fixtures (docs/BASELINE.md):
    `cap_dialogado_es.md` 1.0 → 0.0 de penalización, `cap_con_slop_es.md`
    0.0 → 2.9. Se corrigió la relación invertida que era el bug original.
- **`tests/test_deteccion_es.py`**: 7 tests, todos en verde sin API
  (`uv run python -m pytest tests/test_deteccion_es.py -v`):
  1. `cap_dialogado_es.md` puntúa más alto que antes de la integración.
  2. `cap_con_slop_es.md` puntúa más bajo que el dialogado.
  3. Test de regresión dedicado que fija la *relación* (no los valores
     absolutos) entre 1 y 2, para que una futura recalibración de
     `CALIBRACION` no pueda invertirla en silencio.
  4-5. `densidad_raya_parentetica()` sobre diálogo limpio (0.0) e incisos
     abusivos (>50).
  6. `calcos_detectados()` insensible a mayúsculas.
  7. `dividir_oraciones()` no corta en "Sr." (caso 6 del encargo original
     estaba mal escrito -- corregido, ver detalle en
     `ENCARGO_CLAUDE_CODE.md` sección 1d).
- **`tests/fixtures/voz_minima_es.md`** y **`mundo_minimo_es.md`**: perfil
  de voz y biblia de mundo mínimos, en español, desacoplados de cualquier
  novela real, con la misma forma que `voice.md`/`world.md`. Creados pero
  **no conectados** todavía a una corrida real de `evaluate_chapter()`.
- **`docs/BASELINE.md`**: línea base completa con los números mecánicos
  antes/después. El `overall_score` del juez LLM sigue **PENDIENTE**
  (requiere `.env`).
- **`docs/HALLAZGOS.md`**: dos hallazgos documentados, sin corregir a
  pedido explícito:
  1. `dividir_oraciones()` descarta oraciones de ≤2 palabras por diseño,
     lo que sesga `cv_longitud_oracion()` hacia arriba (subestima el uso
     de frases cortas como marcador de prosa humana).
  2. `CALIBRACION["umbral_cv_oracion"]` (0.32) no discriminó nada entre
     los dos fixtures (0.686 y 0.591, ambos muy por encima) -- es una
     estimación sin corpus de referencia, pendiente de recalibrar con
     prosa española real.

### Tarea 2 — Descontaminar el redactor (COMPLETA, commit `04b6439`)

- **`draft_chapter.py`**: prompt partido en armazón invariante + reglas
  leídas de archivos. `TITULO` viene de `state.json` clave `"titulo"` (con
  fallback a `"title"` por compatibilidad hacia atrás). `POV` combina el
  nombre desde `personajes.md`/`characters.md` (encabezado `## Nombre
  (POV...)`) y la persona/tiempo desde `voz.md` Parte 2. `POZOS_LEXICOS`
  desde "Registro léxico". `REGLAS_ESPECIFICAS` desde la subsección nueva
  `### Reglas específicas de capítulo` en `voz.md` Parte 2 (acepta también
  el nombre legado en inglés "Chapter-Specific Rules"; lista vacía si no
  existe, no rompe). Objetivo de palabras: `CALIBRACION["palabras_objetivo_capitulo"]`
  (2000 -- corregido en `deteccion_es.py` durante la Tarea 3, ver más
  abajo; el código de `draft_chapter.py` no cambió, ya leía el valor real
  en vez de hardcodear), no hardcodeado.
- **`ultimos_finales(n=3)`**: función nueva en `draft_chapter.py`. Lee el
  párrafo final de los últimos n capítulos ya escritos y se inyecta en el
  prompt con la instrucción de no repetir ese tipo de cierre. Reemplaza el
  antipatrón hardcodeado ("no termines con Cass escuchando a su padre").
  Vacía sin capítulos previos -- no rompe (probado).
- **Prompt completo en español** (system message + instrucciones de
  escritura + patrones a evitar): el modelo escribe en castellano, así que
  pedirle instrucciones en inglés aumentaba la probabilidad de calcos. El
  ítem sobre clichés de IA ahora referencia `CLICHES_FICCION` (español) en
  vez de frases en inglés.
- **Nomenclatura bilingüe**: `draft_chapter.py` (`ruta_bilingue()`/
  `load_file_bilingue()`) y `gen_brief.py` (`_ruta_bilingue()`) buscan
  primero `voz.md`/`personajes.md`/`mundo.md`/`esquema.md`, caen a los
  nombres en inglés si no existen. `canon.md` no cambia.
- **`gen_brief.py::extract_voice_rules()`**: ya no devuelve 7 reglas fijas
  (4 de *Bells*). Ahora parsea `voice.md`/`voz.md` Parte 1 (patrones
  estructurales reales) y Parte 2 (una regla por subsección con contenido
  real, ninguna para subsecciones vacías -- probado explícitamente con un
  `voice.md` a medio llenar, que es el estado normal durante varias
  iteraciones de fundación).
- **Bug propio corregido en el camino**: el helper `_seccion()` (usado en
  los dos archivos) rompía el anclaje `^...$` cuando el patrón de búsqueda
  tenía `|` sin agrupar -- buscar "Guardrails" hacía match con la palabra
  suelta del párrafo introductorio de `voice.md` en vez del encabezado
  `## Part 1`. Corregido envolviendo el patrón en `(?:...)`.
- **Aceptación verificada**: `grep -riE "cass|bell|bronze|under-note"
  draft_chapter.py gen_brief.py` → cero resultados. 24 tests en verde
  (`uv run python -m pytest tests/ -v`), incluyendo tests funcionales con
  `voz.md`/`personajes.md` inventados y el caso de sección vacía.
- **Corrección de registro**: `docs/BASELINE.md` decía que `voice.md`/
  `world.md`/`characters.md` eran los de *Bells* en inglés. Es falso --
  son plantillas, no contenido contaminado. (Esta corrección se corrigió
  otra vez en la Tarea 2b: están vacías no solo "porque son plantillas"
  sino porque el pipeline nunca pudo escribirlas -- ver Tarea 6 abajo.)

### Tarea 3 — Campo de ambición por capítulo (COMPLETA, commit `5af3cb9`)

- **`evaluate.py`**: `UMBRALES_AMBICION = {pico: 7.5, sosten: 6.5, valle:
  6.0}`. `extraer_ambicion()` lee el campo declarado en la entrada del
  esquema del capítulo (acepta `ambicion:`/`ambición:`, con o sin acento,
  formato YAML o bullet en negrita). `umbral_por_ambicion()` devuelve el
  umbral correspondiente -- **sin ambición declarada, cae a
  `UMBRAL_POR_DEFECTO_SIN_AMBICION` ("sosten", 6.5), nunca a "valle" (6.0,
  el más laxo)**. Esto se corrigió a mitad de tarea: el primer intento
  caía al umbral general (6.0, igual a "valle"), lo que habría hecho que
  cualquier esquema sin declarar ambición volviera en silencio al
  comportamiento que esta tarea vino a corregir. `evaluate_chapter()` ahora
  expone `ambicion`/`umbral_aceptacion`/`aceptado` en el resultado.
- **`validar_diversidad_ambicion()`**: dos formas de esquema plano, no una.
  (1) menos del 15% de capítulos son 'pico' (o ninguno declara ambición).
  (2) 80%+ de los picos declarados concentrados en el último tercio del
  esquema -- aunque la proporción total esté bien, si los momentos
  memorables se amontonan al final, el resto sigue siendo plano. Este
  segundo caso también se agregó a mitad de tarea, a pedido explícito del
  usuario (no estaba en mi primera implementación). Se llama desde
  `evaluate_foundation()`.
- **`run_pipeline.py`**: `run_drafting()` lee `umbral_aceptacion` del
  stdout de `evaluate.py` en vez de comparar contra `CHAPTER_THRESHOLD`
  fijo. Esa constante queda solo como último respaldo si `evaluate.py` no
  llega a calcular el umbral (capítulo vacío); subida a 6.5 por la misma
  razón que el default de arriba.
- **`gen_outline.py`** y **`outline.md`**: agregado el campo "Ambición:
  pico | sosten | valle" a la plantilla de salida por capítulo (edición
  mínima -- el resto de `gen_outline.py` sigue contaminado con Bells, ver
  Tarea 2b abajo).
- **Aceptación verificada, los 4 casos con test dedicado**: capítulo
  "pico" con score 7.0 → rechazado; el mismo "valle" → aceptado; esquema
  sin picos → advertencia; esquema con 80%+ de picos en el último tercio →
  advertencia. 38 tests en verde (`uv run python -m pytest tests/ -v`).
- **`gen_outline.py` contaminado con Bells → promovido a Tarea 2b**: no es
  un hallazgo aparte, es Tarea 2 incompleta (se le pasó al usuario en la
  auditoría original). Agregada como Tarea 2b en `ENCARGO_CLAUDE_CODE.md`,
  programada para después de la Tarea 4, mismo tratamiento que A1.
- **Objetivo de palabras corregido**: lo que se había registrado como
  "discrepancia sin resolver" (3800 en `deteccion_es.py` vs. 2000 en el
  encargo) era un error del propio `deteccion_es.py`, no una ambigüedad
  real. El usuario confirmó **2000** como valor correcto -- la novela pasó
  de ~22 capítulos de 3200-3800 palabras a ~45 capítulos de 2000 palabras
  (mismo largo total ~90-92k, más puntos de parada). Corregido en
  `deteccion_es.py` con nota explicando el porqué. `draft_chapter.py` no
  necesitó cambios, ya leía el valor dinámicamente.

### Tarea 4 — Alcance de siembra para series (COMPLETA, commit `506f435`)

- **`evaluate.py`**, sección nueva "Alcance de siembra": `validar_siembra(
  entrada, alcance_serie_disponible_, libros_completos=None)` implementa
  las 4 reglas exactas de la tabla del encargo sobre el esquema JSON del
  encargo (`id`/`siembra`/`pago`/`alcance`/`estado`). `alcance_serie_disponible()`
  chequea si existe `siembras_serie.md`. `validar_libro_de_siembras()` es
  la versión batch.
- **Regla de regresión**: sin `siembras_serie.md`, una entrada `alcance:
  serie` se valida como si fuera `alcance: libro` -- comportamiento
  idéntico al de antes de la tarea. Probado explícitamente.
- **`outline.md`** / **`gen_outline_part2.py`**: columna "Alcance"
  agregada a la tabla del Foreshadowing Ledger (edición mínima, mismo
  criterio que la ambición en la Tarea 3).
- **Decisión de diseño explícita, confirmada por el usuario**: los
  validadores operan sobre dicts ya estructurados, no parsean la tabla
  markdown real de `outline.md` (sigue siendo texto libre de LLM). La
  validación es la parte difícil y ya está probada; el parser depende de
  fijar el formato definitivo del ledger primero, y construir un parser
  confiable de una tabla generada por LLM es un problema aparte con
  riesgo real de bugs silenciosos. Documentado como gap en
  `docs/HALLAZGOS.md`.
- **`libros_completos` (regla 4) sin fuente de datos todavía**: hoy nadie
  llena ese parámetro. Según `AUDITORIA_Y_PLAN.md` B2/B7 vive en
  `estado_serie.json` (`{"libros_completos": [1], ...}`), que es parte de
  la Clase B (capa de serie completa) y **todavía no existe** en este
  repo -- ninguna tarea del encargo actual (0-4) lo crea. `validar_siembra()`
  ya está lista para recibirlo (`libros_completos=None` es un default
  razonable mientras tanto); cuando se construya `estado_serie.json`, el
  único cambio necesario es que el llamador le pase
  `set(estado_serie["libros_completos"])`. Documentado en HALLAZGOS.md.
- **Aceptación verificada, los 4 casos + regresión, cada uno con test
  dedicado**: 50 tests en verde (`uv run python -m pytest tests/ -v`).
- **`gen_outline_part2.py` también contaminado con Bells → sumado a la
  Tarea 2b** (confirmado por el usuario, junto con `gen_outline.py`).
  Además de la contaminación (capítulos 17-24 escritos a mano para la
  trama de Bells), tiene un **bug real independiente**: `part1 =
  open('/tmp/outline_output.md').read()` es una ruta absoluta hardcodeada
  fuera del repo -- con contenedores efímeros eso es una bomba de tiempo.
  La Tarea 2b en `ENCARGO_CLAUDE_CODE.md` ya incluye arreglarlo.

### Tarea 2b — Descontaminar `gen_outline.py`/`gen_outline_part2.py` (COMPLETA, commit `5a78c52`)

- **`gen_outline.py`**: prompt partido en armazón invariante (Save the
  Cat / MICE Quotient / Dan Harmon, formato por capítulo con Ambición y
  tabla de siembras con Alcance ya integradas) + contenido leído de
  `mundo.md`/`personajes.md`/`MISTERIO.md`/`semilla.txt` (bilingüe, mismo
  patrón que `draft_chapter.py`). KEY PLOT ARCHITECTURE y CONSTRAINTS ya
  no asumen personajes ni mecánicas específicas de Bells -- se derivan de
  los documentos cargados. Capítulos/palabras desde `CALIBRACION` (2000
  palabras/capítulo, ~46 capítulos calculados), no hardcodeado a
  "22-26 capítulos, ~80,000 palabras".
- **`gen_outline_part2.py`**: mismo tratamiento, más el fix del bug real:
  ya no lee `/tmp/outline_output.md` -- lee `esquema.md`/`outline.md` con
  el resolver bilingüe.
- **Efecto lateral necesario**: los dos scripts ahora **guardan** su
  resultado en `esquema.md`/`outline.md` (antes solo hacían
  `print(result)`, nada quedaba persistido). Arreglar el `/tmp` sin esto
  no alcanzaba -- seguía sin haber un archivo real del que
  `gen_outline_part2.py` pudiera leer.
- **Aceptación verificada**: `grep -riE "cass|bell|bronze|under-note|
  perin|maret|torvald|lenne|tonal" gen_outline.py gen_outline_part2.py` →
  cero. `grep -n "/tmp/" gen_outline_part2.py` → cero. 62 tests en verde
  (`uv run python -m pytest tests/ -v`), incluyendo tests funcionales con
  seed/mundo/personajes/MISTERIO inventados para los dos scripts.
- **Hallazgo mayor → formalizado como TAREA 6** (prioridad alta,
  confirmada por el usuario) en `ENCARGO_CLAUDE_CODE.md`: el mismo patrón
  "`print(result)` sin guardar" existe en `gen_world.py`,
  `gen_characters.py` y `gen_canon.py`, y `run_pipeline.py` tampoco
  captura su stdout. Tal como está, correr la fase de fundación completa
  **no dejaría nada escrito** en `world.md`/`characters.md`/`canon.md`,
  ni con `.env` configurado. Es la tarea con más impacto de todas las
  pendientes -- bloquea completar la fundación de cualquier novela nueva.
- **Corrección de registro (otra vez)**: `docs/BASELINE.md` y
  `docs/ESTADO.md` decían que `world.md`/`characters.md` estaban vacíos
  "porque son plantillas". Incompleto: están vacíos porque el pipeline
  nunca pudo escribirlos (ver Tarea 6). Corregido en los dos archivos.
- **Cuatro tokens de GitHub expuestos en el chat en total, en una sesión
  anterior** (no durante la ejecución de las tareas en sí, sino en
  intentos de push en paralelo) -- **RESUELTO, los cuatro revocados**,
  confirmado por el usuario. Ver "Punto de partida" arriba. El push
  terminó al día: todo hasta `648b0c3` estaba en el remoto en ese
  momento.

### Tarea 6 — Persistencia en la fase de fundación (COMPLETA, prioridad alta)

**Importante: este commit NO descontamina prompts.** Los nombres de la
novela anterior (Cass, Perin, Maret, Cantamura, Tonal Law, etc.) siguen
intactos en `gen_world.py`, `gen_characters.py` y `gen_canon.py` -- eso
queda para una **Tarea 2c**, todavía sin formalizar en
`ENCARGO_CLAUDE_CODE.md` (solo anotada como hallazgo). La Tarea 6 fue
estrictamente sobre persistencia: que los generadores se guarden a sí
mismos y que `run_pipeline.py` no ignore sus fallos.

- **`fundacion_comun.py` (módulo nuevo)**: `load_file()`, `ruta_bilingue()`,
  `load_file_bilingue()`, `extraer_voz_parte2()` y `exigir_semilla()`,
  compartidas por los cinco generadores de fundación en vez de duplicadas.
  `ruta_bilingue()`/`load_file_bilingue()` toman `base_dir` como parámetro
  explícito (no un global del módulo) -- se puede testear pasando un
  `tmp_path` directo, sin monkeypatch.
- **`gen_world.py`, `gen_characters.py`, `gen_canon.py`**: reescritos
  siguiendo exactamente el patrón de `gen_outline.py` (Tarea 2b) -- todo
  dentro de `main()`, guardia `if __name__ == "__main__":`, sin código a
  nivel de módulo que dispare la API al importar. Arreglado también el
  bug de `next(i for i, l in ... if 'Part 2' in l)` (`StopIteration` si no
  había esa línea, y no reconocía "Parte 2") -- ahora usan
  `extraer_voz_parte2()`. Guardan en:
  - `gen_world.py` → `mundo.md`/`world.md`
  - `gen_characters.py` → `personajes.md`/`characters.md`
  - `gen_canon.py` → `canon.md` (**reescribe entero, no acumula** --
    corrección sobre una versión anterior de `ENCARGO_CLAUDE_CODE.md` que
    decía lo contrario: canon en fundación es derivado de
    semilla+mundo+personajes, sin hechos propios, y el descarte de
    iteración ya lo hace `git reset --hard`. Acumular arrastraría hechos
    de un mundo descartado.)
- **`gen_outline.py` también recibió el guard de semilla vacía** (ya
  existía como archivo de la Tarea 2b, no estaba en el pedido original de
  "los tres", pero consume la semilla igual que los otros -- dejarlo
  como la única excepción sin guard habría sido raro). El guard es
  **una sola función compartida** (`exigir_semilla()` en
  `fundacion_comun.py`), no una cuarta/quinta copia.
  **`gen_outline_part2.py` NO lo recibió**: no carga
  `seed.txt`/`semilla.txt` en absoluto, no le corresponde.
- **`run_pipeline.py::run_foundation()`**:
  - `run_generator(script, state, timeout)`: si el generador falla
    (returncode != 0), **guarda `state` con `save_state()` antes de
    salir** (para poder retomar desde la iteración en curso, no desde
    cero) y aborta **todo el pipeline** con `sys.exit(1)` -- no solo la
    iteración. Decisión corregida a mitad de tarea: la primera versión
    solo abortaba la iteración y dejaba que el loop reintentara hasta
    `MAX_FOUNDATION_ITERS`; el usuario corrigió que un returncode != 0 es
    un fallo de infraestructura (API, archivo faltante), no de calidad, y
    reintentar sobre el mismo estado roto no lo arregla -- la iteración
    es la unidad de reintento para puntaje bajo, no para scripts rotos.
    Imprime el script que falló, su returncode, y su **stderr completo**
    (no truncado) antes de salir.
  - Envuelve **los cinco generadores + `voice_fingerprint.py`** con
    `run_generator()` -- `voice_fingerprint.py` no estaba en el pedido
    original, pero es el mismo loop de fundación: un returncode ignorado
    ahí es el mismo bug que se está arreglando en los otros pasos.
    (Corrección: `voice_fingerprint.py` NO genera nada de `voice.md` --
    es un medidor que analiza capítulos ya escritos y guarda
    `edit_logs/voice_fingerprint.json`, que ni siquiera se versiona
    -`edit_logs/` está en `.gitignore`. Ver el hallazgo nuevo de abajo:
    nada en el repo genera la Parte 2 de `voice.md`.)
  - `verificar_archivos_fundacion(desde)`: antes de llamar a
    `evaluate.py --phase=foundation`, confirma que
    `mundo.md`/`personajes.md`/`esquema.md`/`canon.md` **se modificaron en
    esta iteración** (mtime posterior a `desde`, un timestamp tomado al
    empezar la iteración) y no están vacíos. Corregido a mitad de tarea:
    el primer intento solo chequeaba "existe y no está vacío", pero
    `world.md`/`characters.md`/`outline.md` están trackeados en git como
    plantillas con contenido real (encabezados + comentarios HTML) --
    ese chequeo por sí solo daría verde contra el andamio sin tocar,
    aunque ningún generador hubiera corrido de verdad esta vuelta. El
    chequeo de contenido no vacío se mantiene ADEMÁS del de mtime, no en
    su lugar: un generador puede devolver 0 y haber escrito una respuesta
    vacía de la API sin que `run_generator()` lo detecte (no hay
    excepción de por medio). Si falta algo, también guarda `state` y
    aborta -- una fundación incompleta no debe producir un puntaje que
    entre a `results.tsv`.
- **Aceptación verificada**: 91 tests en verde
  (`uv run python -m pytest tests/ -v`), incluyendo import sin llamadas a
  `httpx.post`, `main()` con `call_writer` parcheado escribiendo en el
  archivo esperado, resolución bilingüe, los guards de semilla vacía, y
  `run_generator()`/`verificar_archivos_fundacion()` con `uv_run()`
  parcheado (nada de esto toca la API).
- **Hallazgos nuevos, sin corregir** (`docs/HALLAZGOS.md`):
  1. `gen_world.py`/`gen_characters.py`/`gen_canon.py` siguen contaminados
     con *Bells* en el contenido de sus prompts (no tocado a pedido
     explícito) -- candidato a **Tarea 2c**, sin formalizar todavía.
  2. No hay ningún mecanismo que devuelva al canon los hechos que los
     capítulos establecen durante la redacción (un nombre de calle
     mencionado al pasar, la edad de un personaje secundario revelada más
     tarde). `PIPELINE.md` da por sentado que esto pasa
     ("Extract new canon entries from eval output → append to canon.md")
     pero no existe el script. Distinto del punto de `gen_canon.py` de
     arriba: esto es acumulación en la fase de **redacción**, no en
     fundación, necesitaría un script propio, y depende de la misma
     decisión de diseño pendiente que el hallazgo de los validadores de
     siembra (Tarea 4): qué tan estructurado tiene que ser `canon.md`
     para que un script pueda leerlo y escribirle de vuelta con
     confianza.
  3. **Nada genera la Parte 2 de `voice.md`/`voz.md`** -- prioridad alta,
     hermano de la Tarea 6 (no la misma: acá no hay un script roto, no
     existe el script). Confirmado con grep: no hay `gen_voice.py`,
     `run_foundation()` no tiene ese paso, y ningún `write_text` en el
     repo apunta a `voice.md`/`voz.md`. `PIPELINE.md` (Fase 1, paso 5)
     documenta "voice discovery" como si existiera. `draft_chapter.py`,
     `gen_brief.py` y `gen_outline.py` leen esa sección esperando
     contenido real; hoy son comentarios HTML vacíos. El pipeline
     redactaría con identidad de voz vacía. Diagnosticado sin `.env`;
     escribir el script (mismo patrón que el resto de la Tarea 6) tampoco
     lo necesitaría, pero validar la calidad de lo que generaría sí.

### Tarea 2c — Descontaminar `gen_world.py`/`gen_characters.py`/`gen_canon.py` (COMPLETA)

- **`gen_characters.py` (el peor de los tres)**: el reparto fijo por
  nombre (Cass Bellwright, Eddan, Perin, Maret Corda, Rector Suvaine,
  Torvald Hess + "1-2 adicionales") se reemplazó por un requisito
  estructural: protagonista (POV) + antagonismo del conflicto central
  como mínimo, más secundarios según la semilla. El número de personajes
  con profundidad completa se deriva de `CALIBRACION` (capítulos
  totales), no está hardcodeado. Los frameworks de oficio (tres sliders
  de Sanderson, wound/want/need/lie, 8 dimensiones de diálogo) **se
  mantienen intactos** -- son método, no trama de la novela anterior.
- **`gen_world.py`**: títulos de sección genéricos ("Reglas excepcionales
  del mundo (si aplica)" en vez de "Magic System / Hard Rules (Tonal
  Law)" / "Soft Magic (Cass's Gift)"). Sacado "Cantamura" y "the natural
  amphitheater's acoustic properties".
- **`gen_canon.py`**: el ejemplo "the Perin contract, the Expansion Wars"
  se reemplazó por una instrucción de no inventar ejemplos.
- **Los tres**: ya no asumen "fantasy novel" ni exigen sistema de magia
  obligatorio -- el género y si hay reglas excepcionales del mundo salen
  de la semilla; si no aplica, el prompt instruye escribir "No aplica".
- **Los tres prompts traducidos al español** (system message + texto de
  usuario), mismo criterio que la Tarea 2: pedir en inglés que el modelo
  escriba en español induce los calcos que `deteccion_es.py` caza.
- **Aceptación verificada**: `grep -in "cass|bellwright|perin|corda|
  suvaine|torvald|cantamura|tonal law|expansion wars" gen_world.py
  gen_characters.py gen_canon.py` → cero. 101 tests en verde
  (`uv run python -m pytest tests/ -v`), incluyendo
  `tests/test_descontaminacion_2c.py` dedicado (10 tests) para que esos
  términos no puedan volver a entrar sin que el suite lo note.
- **Hallazgo nuevo, sin corregir** (`docs/HALLAZGOS.md`): `gen_world.py`
  carga `CRAFT.md` pero nunca lo interpola en el prompt (`{craft}` no
  aparece en el f-string -- bug preexistente, no introducido por esta
  tarea). `gen_characters.py` ni siquiera carga `CRAFT.md`. Fuera de
  alcance de la Tarea 2c (arreglarlo bien es una decisión de diseño:
  resumen manual vs. interpolar el archivo completo).

### Tarea 7 — Generador de voz que faltaba (COMPLETA)

- **`gen_voice.py` (script nuevo)**: mismo patrón que los otros seis --
  `main()`, guardia, `fundacion_comun.py`, `exigir_semilla()`. Insumos:
  **solo** la semilla y `CRAFT.md` -- nada de `mundo.md`/`personajes.md`
  (leerlos crearía dependencia circular con `gen_world.py`/
  `gen_characters.py`, que a su vez leen la voz).
- **Decisión de diseño clave: la voz se genera UNA VEZ.** Si la Parte 2
  ya tiene contenido real, `gen_voice.py` no llama a la API -- informa
  que ya existe y sale (`fundacion_comun.voz_parte2_tiene_contenido()`).
  Motivo: la semilla no cambia entre iteraciones, así que regenerar la
  voz sería ruido, no exploración. Coherente con la regla de serie
  (`AUDITORIA_Y_PLAN.md` B4: la voz no se redescubre entre libros).
- **Llena 7 de las 8 subsecciones de la Parte 2** (Tono, Ritmo de
  oración, Registro léxico, POV y tiempo, Convenciones de diálogo,
  Pasajes ejemplares, Anti-ejemplares) sin tocar la Parte 1 ni la
  subsección opcional "Reglas específicas de capítulo" (se llena más
  tarde, por capítulo). El modelo responde con marcadores propios
  (`###TONO###`, etc., no los encabezados reales del archivo) que
  `parsear_secciones()` interpreta, y `llenar_parte2()` inyecta cada uno
  en el rango exacto de su subsección -- si una subsección ya tiene
  contenido real (no solo el comentario placeholder), no se toca.
- **`run_pipeline.py::run_foundation()`**: `gen_voice.py` corre
  **primero** en el loop, antes de `gen_world.py`, envuelto en
  `run_generator()`.
- **`verificar_archivos_fundacion()` necesitó un criterio distinto para
  `voz.md`**: los otros cuatro archivos (Tarea 6) se verifican por
  `mtime` -- deben haberse modificado en esta iteración. `voz.md` NO
  puede verificarse así: como se congela después de la primera
  iteración que la generó, su `mtime` va a ser viejo a propósito desde
  la iteración 2 en adelante. Verificarla por `mtime` habría abortado
  todas las iteraciones después de la primera sin motivo real. Para
  `voz.md` alcanza con "existe y tiene contenido real", sin importar
  cuándo se escribió.
- **Simplificación consciente respecto a `PIPELINE.md`**: el paso
  documentado ahí ("write 5 trial passages ... select best...") es un
  proceso de explorar-evaluar-elegir en varios pasos. `gen_voice.py` hace
  una sola llamada (mismo patrón de un solo `call_writer()` que los otros
  seis generadores), pidiéndole al modelo en el prompt que considere
  varias direcciones internamente antes de comprometerse a una sola voz
  -- no literalmente 5 pasajes generados y comparados por separado.
- **Aceptación verificada**: 113 tests en verde
  (`uv run python -m pytest tests/ -v`), incluyendo
  `tests/test_gen_voice.py` (idempotencia -- `call_writer` parcheado
  para lanzar si se lo llama, Parte 1 intacta, resolución bilingüe,
  parseo y llenado de secciones) y los 4 tests nuevos de
  `verificar_archivos_fundacion()` sobre el caso de `voz.md` con `mtime`
  viejo (no debe contar como faltante) vs. vacía (sí debe contar, sin
  importar el `mtime`).

## Qué falta de la Tarea 1

- **1a** (parte no cubierta por 1c): flag `--idioma es|en` para que
  `evaluate.py` no quede hardcodeado a español. El encargo lo marca como
  opcional ("si complica mucho, priorizá que funcione el español") -- se
  priorizó español y esto quedó pendiente.
- **1b**: traducir los prompts del juez LLM a español en `evaluate.py`,
  `adversarial_edit.py`, `reader_panel.py`, `review.py`,
  `compare_chapters.py`, más el bloque de advertencias sobre normas
  castellanas (raya de diálogo, sujeto pronominal omitido, subordinación
  larga, +15-20% de extensión vs. inglés). **Bloqueado por falta de
  `.env`** -- no tiene sentido traducir y no poder probar contra el juez
  real.
- **1d, parte pendiente**: conectar `voz_minima_es.md`/`mundo_minimo_es.md`
  a una corrida real de `evaluate_chapter()`. Hoy `load_layer_files()` en
  `evaluate.py` tiene las rutas de `voice.md`/`world.md`/etc. hardcodeadas
  al directorio raíz -- parametrizarlas (o hacer que `--archivo` cargue un
  set alternativo de capa) es trabajo aparte, y de todos modos requiere
  `.env` para ejecutarse.
- El **`overall_score`** completo de `evaluate.py` (juez LLM + mecánico)
  sobre los dos fixtures sigue **PENDIENTE** en `docs/BASELINE.md`.

## Qué sigue

Las Tareas 0, 1c, 1d, 2, 2b, 2c, 3, 4, 6 y 7 están completas.

**Se puede seguir escribiendo y testeando código sin `.env`** -- todo lo
de esta sesión se construyó y probó así, con `call_writer()`/`uv_run()`
parcheados. Lo que sin `.env` **no** se puede hacer es correr una
generación real ni ver si el resultado tiene calidad.

- **Sin `.env`, se puede avanzar en escribir código para:**
  - El script que acumule al canon los hechos de redacción, y el parser
    del Foreshadowing Ledger (Tarea 4) -- ambos esperan primero fijar el
    formato estructurado de esos documentos, que es una decisión de
    diseño, no algo que necesite la API.
  - El hallazgo del `craft` no usado en `gen_world.py`/`gen_characters.py`
    (Tarea 2c) -- decisión de diseño (resumen manual vs. interpolar
    `CRAFT.md` completo), no bloqueado por `.env`.
  - Si se quiere el proceso de "5 pasajes, elegir el mejor" que describe
    `PIPELINE.md` para el descubrimiento de voz (en vez de la llamada
    única que implementa `gen_voice.py` hoy), es un cambio de
    arquitectura, no algo bloqueado por `.env` -- ver Tarea 7.
- **Bloqueado por `.env` -- no hay código nuevo que escribir, hace falta
  correr contra el modelo real:**
  - Validar que `gen_voice.py` produce una voz de calidad real -- eso es
    juicio, no algo mockeable con sentido.
  - **1a** (flag `--idioma es|en`), **1b** (prompts del juez en español,
    validados contra el juez real), **1d parte final** (conectar los
    fixtures de voz/mundo a una corrida real de `evaluate_chapter()`).
  - Completar el `overall_score` de los fixtures de la Tarea 0 en
    `docs/BASELINE.md`.
  - Intentar `run_pipeline.py --phase foundation` de punta a punta por
    primera vez -- ahora sí con los 7 pasos de fundación completos
    (voz, mundo, personajes, esquema x2, canon, fingerprint).

## Cómo retomar

1. Verificar qué falta pushear: `git log origin/framework/es-multilibro..HEAD
   --oneline`. Si hay algo y el credential guardado sigue vigente, `git
   push` debería funcionar directo, incluso corrido con `!`. Si falla con
   "could not read Username": salir con Ctrl+D, `git push` en la terminal
   interactiva, volver a entrar con `claude` (ver "Punto de partida"
   arriba -- no hace falta otra máquina ni otra sesión SSH).
2. Si no hay `.env` todavía: avanzar el diseño de formato de
   `canon.md`/Foreshadowing Ledger es lo único que queda sin bloquear
   (ver "Qué sigue").
3. Cuando haya `.env` con `ANTHROPIC_API_KEY`:
   a. Correr `evaluate.py --chapter` (sin `--solo-mecanico`) sobre los
      fixtures para completar el `overall_score` pendiente en
      `docs/BASELINE.md`.
   b. Arrancar la Tarea 1b.
   c. Con la Tarea 6 y la 7 ya resueltas, se puede intentar
      `run_pipeline.py --phase foundation` de punta a punta por primera
      vez (con un `seed.txt`/`semilla.txt` real).
