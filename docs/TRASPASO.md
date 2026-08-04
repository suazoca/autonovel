# TRASPASO — rama `novela2` (worktree de `framework/es-multilibro`)

Estado real al cierre de esta sesión (2026-08-04). Este documento
reemplaza la necesidad de releer `ESTADO.md` completo o el historial de
commits para retomar el trabajo -- es la foto actual, no la bitácora
(para eso está `ESTADO.md`, que sí es narrativo y tiene una sección
nueva para esta rama).

**Actualización 2026-08-04:** sesión corta, un capítulo. Se escribió,
evaluó y aceptó el Cap. 6 ("Bibliografía hostil", Debate). Primera
pasada rechazada (`overall_score` 6.04 contra umbral 6.5) por dos
apariciones de la locución prohibida "testimonio de" que activaron el
detector mecánico de slop (`slop_penalty` 1.5 sobre un puntaje base del
juez de 7.54). Se corrigieron esas dos frases, un choque de continuidad
(la mujer del avión apoyada contra "la ventanilla del pasillo", que
contradice el asiento 11A -- ventanilla -- de Vidal establecido tres
párrafos antes) y, ya con el capítulo aceptado, tres deslices de
aritmética que el juez marcó como caracterización involuntaria (Vidal
calculaba "cuarenta y cinco años" desde 1988 y "cincuenta años" desde
1978 estando en noviembre de 2032 -- corresponden 44 y 54). Segunda
evaluación: `overall_score` 7.54, aceptado. `actualizar_canon.py` corrió
sin conflictos (8 entradas nuevas). Commit `aecd17e`, pusheado a
`origin/novela2`.

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

Fundación completa y aprobada. **Cap. 1 a 6 escritos, evaluados y
aceptados.** El Cap. 6 pasó en la segunda pasada tras limpiar dos
locuciones prohibidas que penalizaban el `overall_score` mecánicamente
y un error de continuidad de asiento/ventanilla; quedó en 7.54 contra
umbral 6.5. `state.json::debts` vacío, sin `CONFLICTO` de canon abiertos.
Working tree limpio, al día con `origin/novela2` (commit `aecd17e`).
Listo para Cap. 7 ("La ciudad de la tela"), Vidal en Turín con Ferrero
-- ver "Próximo paso".

## Estado del repositorio

| | |
|---|---|
| Directorio | `/root/novela2` (worktree; confirmado con `git worktree list`) |
| Rama | `novela2`, diverge de `framework/es-multilibro` en `7b81700` (Tarea 7) |
| `.env` / `ANTHROPIC_API_KEY` | Presente en este entorno. `AUTONOVEL_WRITER_MODEL=claude-fable-5`, `AUTONOVEL_JUDGE_MODEL=claude-opus-5`, `AUTONOVEL_REVIEW_MODEL=claude-opus-5`, `AUTONOVEL_API_BASE_URL=https://api.anthropic.com` |
| Push | Al día con `origin/novela2` (`git log origin/novela2..HEAD --oneline` vacío). Último commit: `aecd17e`. |
| Working tree | Limpio -- confirmar con `git status`. |
| Tests | `uv run python -m pytest tests/ -v` -- **246 tests, todos en verde, + 38 xfail esperados** (sin cambios esta sesión, no se tocó código). No hace falta `.env` (todo mockeado); drafting/evaluar capítulos sí lo necesita. |
| Token de GitHub | Fine-grained, creado 2026-07-27, alcance `suazoca/autonovel`, permiso `Contents: read/write`, **vence ~2026-08-26**. Al vencer, limpiar la credencial guardada con `git credential reject` (protocol=https, host=github.com) antes de autenticar con uno nuevo. Usado sin problemas esta sesión (push directo, sin reingresar credencial). |

## Fundación (completa, aprobada -- sin cambios esta sesión)

| Archivo | Estado |
|---|---|
| `voice.md` | Completo (Parte 1 + Parte 2 generada desde la semilla, commit `61aeee4`) |
| `world.md` | Completo, revisado (último cierre: commit `dde01c4`) |
| `characters.md` | Vidal, Sandoz, Chiara y Ferrero completos. **Ledda, Ansermet y Ceruti siguen "ficha pendiente de generación"** -- sin cambios (commit `6f110dc`) |
| `outline.md` | 46 capítulos, Save the Cat + MICE anidado (commit `c85b90f`, reestructurado Cap. 5/6 en `52be40f`/`1c5445b`). Sin cambios esta sesión |
| `canon.md` | Regenerado sobre los documentos completos, commiteado (`e2233bc`) |

## evaluate.py: `overall_score` ya no lo inventa el juez (sin cambios esta sesión)

Reparado la sesión anterior (commit `b5ac02d`): se sacó `overall_score`
del JSON pedido al juez y se calcula en código
(`0.7 * media + 0.3 * mínimo` de las dimensiones presentes). El Cap. 6
es el tercer capítulo evaluado con esta fórmula (después de Cap. 4 y
Cap. 5) y confirmó que el `slop_penalty` mecánico puede tumbar un
capítulo con puntaje de juez alto -- ver más abajo. Detalle completo del
diagnóstico y la validación, en la versión anterior de este documento /
`docs/ESTADO.md`.

**Nota importante para leer eval_logs viejos:** los Cap. 1, 2 y 3 tienen
`overall_score` de la fórmula vieja (7.0 plano). Cap. 4 en adelante, ya
con la fórmula corregida.

## Redacción

`chapters/ch_01.md` a `ch_05.md` -- sin cambios esta sesión. Los cinco
están escritos, evaluados y aceptados (detalle completo de cada uno en
versiones anteriores de este documento). Pendiente sin resolver:
si vale la pena re-redactar `ch_01.md`, escrito con el bug de canon de
la Tarea 10 todavía activo (ver "Pendiente").

`chapters/ch_06.md` ("Bibliografía hostil", Debate) -- **escrito y
aceptado esta sesión.** Cuatro beats del outline: (1) en el vuelo de
salida de Jerusalén, Vidal lee y desarma el memorial de d'Arcis con
criterios de peritaje (testigo con interés, testimonio de oídas, sin
cadena de custodia) y descarta la confesión como indicio, no como
prueba; diálogo con una pasajera que vio la ostensión de 2015 y solo
recuerda la fila, no la tela. (2) en Zúrich, Secondo Pia (1898) y el
STURP (1978, "mecanismo desconocido") como vara generacional de los
sindonólogos vivos; anota que el silencio documental de trece siglos es
mejor argumento que el carbono. (3) alimenta a Tamiz con todo el
material público -- el modelo devuelve "se requiere adquisición
directa", corrido tres veces con umbrales cada vez más laxos sin
cambiar la conclusión. (4) descubre 87.5 horas de tres semanas de
noches sin código de facturación; crea uno nuevo y escribe su propio
nombre en el campo "cliente".

**Primera evaluación: rechazado.** `overall_score` 6.04 contra umbral
6.5 (ambición "sostén"), pese a un puntaje base del juez de 7.54 (nueve
dimensiones entre 7 y 9). La diferencia: `slop_penalty` 1.5, entero por
dos apariciones de la locución prohibida `\btestimonio de\b`
(`deteccion_es.py::NIVEL1_LOCUCIONES`) -- "testimonio de confesión" y
"testimonio de oídas", ambas frases legítimas en sentido forense pero
mecánicamente indistinguibles de la locución genérica de IA que la
regla busca cazar. El juez también marcó un choque de continuidad real
(Vidal en el asiento 11A, ventanilla; el texto hacía que la pasajera de
al lado se acomodara contra "la ventanilla del pasillo", geometría
imposible) y señaló `character_voice` como la dimensión más floja, con
una revisión sugerida concreta: cambiar la pregunta de Vidal a la mujer
por una "trampa de precisión" en vez de la pregunta abierta que tenía.

**Arreglo:** se reescribieron ambas frases con "testimonio de" (una
pasó a "confesión del siglo catorce", la otra a fragmentos cortos sin
la locución, rompiendo de paso una enumeración en tríada que el juez
había marcado como tic), se corrigió la geometría del avión (la mujer
se acomoda "contra el respaldo"), se cambió la pregunta de Vidal a
"¿Cuánto tiempo estuvo delante? Exacto, si se acuerda" (fuerza a la
mujer a admitir imprecisión, en vez de responder una pregunta genérica)
y se cortó la glosa explícita sobre n=1 y sesgo de memoria que seguía a
la anécdota, dejando el dato sin procesar. Se rompieron además otras
dos enumeraciones en tríada señaladas por el juez como patrón repetido.

**Segunda evaluación: aceptado.** `overall_score` 7.54 (idéntico al
puntaje base -- `slop_penalty` bajó a 0 tras los cambios).
`canon_compliance` 9/9. El juez marcó, ya sin bloquear la aceptación,
un desliz de aritmética: "cuarenta y cinco años" desde 1988 y "los
últimos cincuenta años" desde el STURP (1978) no cuadran con que el
capítulo transcurre en noviembre de 2032 (corresponden 44 y 54) -- "en
este personaje, el número redondeado de más es caracterización
involuntaria". Se corrigieron los tres usos a mano, sin re-evaluar
(mismo criterio que ediciones menores en capítulos anteriores).

`actualizar_canon.py 6` corrió sin conflictos: 8 entradas nuevas en
`canon_emergente.md` (cronología del vuelo y el memorial, la auditoría
del memorial de d'Arcis, los tres laboratorios de 1988, la primera
ingesta de Tamiz, las 87.5 horas sin código, el corpus de Ferrero, las
réplicas de Pia de 1931, el archivo de notas "lectura"). `state.json::
debts` sigue vacío.

Palabras: 1839 (objetivo del outline: 2450 -- quedó corto, por encima
del umbral mínimo de longitud del script pero sin llegar al target;
no bloqueante, no se forzó a extender).

Commit `aecd17e`, pusheado a `origin/novela2` en esta sesión.

## Cap. 5: por qué se reescribió entero (sesión anterior, sin cambios)

Sin novedades esta sesión. Detalle completo en la versión anterior de
este documento / `docs/ESTADO.md`: se reescribió entero porque el
Cap. 46 (Final Image) depende de una primera entrada al edículo que el
borrador original no dramatizaba. `overall_score` final 7.54.

## Bugs de compatibilidad con Fable 5 (sesión anterior, sin cambios)

Sin novedades esta sesión. Detalle completo en versiones anteriores de
este documento / `docs/ESTADO.md`.

## Tarea 12 -- guardia de contaminación en los prompts (sin cambios)

Sigue completa. `tests/test_guardia_prompts.py::DEUDA_CONOCIDA` sigue
siendo la fuente de verdad. Sin cambios esta sesión.

## Tarea 10 -- acumulación de canon durante la redacción (en producción real)

El mecanismo (`canon_emergente.md` + `actualizar_canon.py`) suma un
sexto capítulo sin `CONFLICTO`: el Cap. 6 no chocó con nada de la
fundación ni del canon emergente previo. Total acumulado: 6 capítulos,
cuatro `CONFLICTO` detectados y resueltos a mano en sesiones anteriores
(Ruti, Zúrich, cronología del Sepulcro, fundación vs. outline del
Cap. 5), ninguno nuevo esta sesión.

## Pendiente (no bloqueante)

- **Decidir qué hacer con `ch_01.md`.** Sin cambios -- se redactó con el
  bug de canon de la Tarea 10 activo. Sigue sin decidirse si vale la
  pena releerlo/rehacerlo.
- **Tarea 11** -- punto de aprobación manual por capítulo en
  `run_pipeline.py`. Sin cambios; se sigue aprobando capítulo a
  capítulo a mano, leyendo el archivo (esta sesión, además, se generó y
  entregó un PDF del Cap. 6 para lectura fuera del entorno).
- **Tareas 1b, 1b-bis y 13** -- traducir los prompts contaminados que
  encontró la Tarea 12. Sin cambios; detalle en
  `tests/test_guardia_prompts.py::DEUDA_CONOCIDA`.
- **Fichas completas** de Ledda, Ansermet y Ceruti en `characters.md`.
  Sin cambios. Ansermet aparece recién en el Cap. 9 -- no urge todavía.
- **Merge de las Tareas 8, 9 y 9b** hacia `framework/es-multilibro`.
  Sin cambios.
- **Calendario de días concretos para el Acto I** (Cap. 1-11, octubre de
  2032). Sin cambios, sigue sin resolverse a pedido explícito. Detalle
  en `docs/HALLAZGOS.md`, última entrada.
- **Revisar `CHEQUEO FINAL` y `CALIBRACIÓN DE PUNTAJE` de
  `CHAPTER_PROMPT`** (`evaluate.py`). Sin cambios -- siguen instruyendo
  al juez con el lenguaje que originó el ancla vieja, aunque ya no
  controlan el campo final.
- **Nueva: las locuciones de `NIVEL1_LOCUCIONES` en `deteccion_es.py`
  no distinguen registro.** `\btestimonio de\b` cazó dos usos forenses
  legítimos en el Cap. 6 (vocabulario normal de un perito hablando de
  pruebas) y tumbó el capítulo bajo el umbral por un `slop_penalty`
  puramente mecánico, pese a un puntaje de juez de 7.54. Se resolvió
  reescribiendo las dos frases, no ajustando la regla -- pero si vuelve
  a pasar en un capítulo con más vocabulario forense (Vidal es perito,
  va a seguir hablando de "testimonio", "custodia", "indicio"), vale la
  pena evaluar si la locución necesita acotarse (p. ej. excluir
  "testimonio de oídas"/"testimonio de parte" como locuciones jurídicas
  fijas) en vez de reescribir cada vez que aparece. No se toca ahora --
  dos ocurrencias en seis capítulos no justifican tocar el detector.

## Próximo paso

**Escribir el Cap. 7** ("La ciudad de la tela", Debate, ambición
"sostén", ~2050 palabras). Vidal viaja a Turín a presentar su solicitud
de acceso en persona; conoce a Ottavio Ferrero (ya sembrado en el
Cap. 6 como autor del corpus fotográfico y, sin que el lector lo supiera
todavía, miembro de la Comisión de Conservación). Beats: la catedral y
el crucero donde la Sábana yace desde 1997; la cortesía a la antigua de
Ferrero, química y liturgia en la misma frase sin comillas; la lección
de 1988 ("en el ochenta y ocho también había un intervalo estrecho,
doctor -- lo que no había era nadie esperando del otro lado del
anuncio"); la mención al pasar de la teca nueva, donación anónima que
Vidal no registra pero el lector sí (plant del hilo #20); la promesa de
elevar la solicitud que ambos saben cómo termina. Primer asomo de un
plant nuevo: la muñeca izquierda de Ferrero, que se toca sin reloj
(hilo #14).

```bash
uv run python draft_chapter.py 7
uv run python evaluate.py --chapter=7
uv run python actualizar_canon.py 7
```

**Ojo:** el número de capítulo va posicional
(`chapter_num = int(sys.argv[1])` en `draft_chapter.py`) -- no hay flag
`--chapter` para ese script (sí lo tiene `evaluate.py`). Leer cada
capítulo antes de avanzar al siguiente. Revisar `canon_emergente.md`/
`state.json::debts` por si el juez marcó algo.

**Lección del Cap. 6, para no repetir el ciclo de rechazo-arreglo:**
antes de dar por bueno o malo un capítulo por su `overall_score`, mirar
el `eval_log` completo -- si `raw_judge_score` y `overall_score`
difieren mucho, el problema casi seguro es mecánico (`slop_penalty`:
locuciones prohibidas, tríadas, rayas parentéticas), no de fondo, y se
arregla más rápido que releer las nueve dimensiones buscando qué falló.

**Advertencia de la sesión del Cap. 5, sigue vigente:** antes de
aceptar un capítulo con puntaje bajo el umbral tras varias rondas de
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
5. Leer la entrada de Cap. 7 en `outline.md` (línea ~116) antes de
   redactar.
6. Redactar Cap. 7 a mano con el standalone:
   `uv run python draft_chapter.py 7` → `evaluate.py --chapter=7` →
   `actualizar_canon.py 7`. Leer el capítulo y el canon emergente antes
   de avanzar. Si el `overall_score` queda bajo el umbral, revisar
   primero el `eval_log` completo (`slop` dict) antes de asumir que es
   un problema de prosa -- ver "Próximo paso".
