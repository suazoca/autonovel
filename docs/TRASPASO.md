# TRASPASO — rama `novela2` (worktree de `framework/es-multilibro`)

Estado real al cierre de esta sesión (2026-08-04). Este documento
reemplaza la necesidad de releer `ESTADO.md` completo o el historial de
commits para retomar el trabajo -- es la foto actual, no la bitácora
(para eso está `ESTADO.md`, que sí es narrativo y tiene una sección
nueva para esta rama).

**Actualización 2026-08-04 (tarde):** se sumó el Cap. 7 ("La ciudad de
la tela", Debate) a lo ya cerrado del Cap. 6 esta misma sesión. Igual
patrón que el Cap. 6: primera evaluación aceptada de movida
(`overall_score` 7.04, sin `slop_penalty` relevante salvo una pasiva
calcada), pero con dos problemas reales señalados por el juez que se
corrigieron igual -- una intrusión omnisciente que rompe la tercera
persona limitada y, el más importante, que el hábito de "anotar a
lápiz en los márgenes" que se le había dado a Ferrero **es la marca de
identificación de Sandoz** (hilo #9 del Foreshadowing Ledger, se paga
en el Cap. 12) y no debía reusarse. Cambiado a "tinta roja" en Ferrero.
Reevaluado: `overall_score` 7.54, aceptado, sin conflictos de canon.
Ambos capítulos (6 y 7) comiteados y pusheados en esta sesión -- ver
tabla "Estado del repositorio" para el hash exacto del cierre.

**Actualización 2026-08-04 (anterior, Cap. 6):** se escribió, evaluó y
aceptó el Cap. 6 ("Bibliografía hostil", Debate). Primera pasada
rechazada (`overall_score` 6.04 contra umbral 6.5) por dos apariciones
de la locución prohibida "testimonio de" que activaron el detector
mecánico de slop (`slop_penalty` 1.5 sobre un puntaje base del juez de
7.54). Se corrigieron esas dos frases, un choque de continuidad (la
mujer del avión apoyada contra "la ventanilla del pasillo", que
contradice el asiento 11A -- ventanilla -- de Vidal establecido tres
párrafos antes) y, ya con el capítulo aceptado, tres deslices de
aritmética que el juez marcó como caracterización involuntaria. Segunda
evaluación: `overall_score` 7.54, aceptado. Commit `aecd17e`.

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

Fundación completa y aprobada. **Cap. 1 a 7 escritos, evaluados y
aceptados.** Cap. 6 y Cap. 7 se escribieron en la misma sesión
(2026-08-04), los dos en 7.54 contra umbral 6.5, los dos tras una
segunda pasada de correcciones -- en el Cap. 6 por un `slop_penalty`
mecánico, en el Cap. 7 por un conflicto real de continuidad (un tic de
personaje reusado por error). `state.json::debts` vacío, sin
`CONFLICTO` de canon abiertos. Working tree limpio, pusheado a
`origin/novela2`. Listo para Cap. 8 ("Denegado"), el punto bajo del
Acto I -- ver "Próximo paso".

## Estado del repositorio

| | |
|---|---|
| Directorio | `/root/novela2` (worktree; confirmado con `git worktree list`) |
| Rama | `novela2`, diverge de `framework/es-multilibro` en `7b81700` (Tarea 7) |
| `.env` / `ANTHROPIC_API_KEY` | Presente en este entorno. `AUTONOVEL_WRITER_MODEL=claude-fable-5`, `AUTONOVEL_JUDGE_MODEL=claude-opus-5`, `AUTONOVEL_REVIEW_MODEL=claude-opus-5`, `AUTONOVEL_API_BASE_URL=https://api.anthropic.com` |
| Push | Al día con `origin/novela2` (`git log origin/novela2..HEAD --oneline` vacío). Último commit: el de cierre de esta sesión (Cap. 7 + `docs/`) -- confirmar con `git log -1 --oneline`. |
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

Commit `aecd17e`.

`chapters/ch_07.md` ("La ciudad de la tela", Debate) -- **escrito y
aceptado esta sesión.** Cinco beats: (1) Vidal llega temprano a la
catedral de Turín, ve la caja sellada tapada por un paño y, a un
costado, una reproducción fotográfica a la que la gente le reza en su
lugar. (2) lo recibe Ottavio Ferrero -- química y liturgia en la misma
frase, sin comillas. (3) Ferrero le explica la herida operativa de
1988 en cuatro intercambios: "un intervalo puede ser verdadero y hacer
daño", "¿quién administra ese resultado?". (4) menciona al pasar la
teca nueva -- donación anónima de 2031, especificaciones de telemetría
mejores de lo que la Comisión sabría pedir; Vidal se distrae con el
dato técnico (acceso al histórico) y no con el dinero, que es
exactamente la ironía dramática que pide el beat. (5) Ferrero promete
elevar la solicitud con nota favorable en lo técnico; anticipa una
carta de rechazo "con cosas ciertas en los considerandos".

**Evaluación (primera pasada): aceptado, con reparos.** `overall_score`
7.04 contra umbral 6.5, `slop_penalty` 0.5 por una única pasiva calcada
("fue cuestionado por"). El juez señaló además, sin bloquear, dos
problemas de oficio: una intrusión omnisciente que rompe la tercera
persona limitada (el narrador juzgaba "clasificó mal" un gesto de
Ferrero antes de que Vidal mismo lo descubriera) y una acotación de
manual ("sonrió sin humor"). **El hallazgo importante:** el juez marcó
como "nota de riesgo" que "leyó el protocolo... la segunda con lápiz" y
"anotaciones a lápiz en los márgenes" en Ferrero **es el tic de
identificación reservado a Sandoz** (`outline.md`, hilo #9 del
Foreshadowing Ledger: se planta en el Cap. 11 -- "el libro anotado a
lápiz, la primera aparición física de Sandoz, sin cuerpo" -- y se paga
en el Cap. 12 cuando "Vidal reconoce el lápiz"). Dárselo también a
Ferrero le habría restado unicidad a esa seña más adelante en el libro.

**Arreglo:** se cambió el tic de Ferrero de lápiz a tinta roja (dos
apariciones en diálogo + una en descripción), se reescribió la pasiva
calcada en voz activa, se sacó la intrusión omnisciente ("tardó en
clasificar y clasificó mal: le pareció cansancio" → "tardó en
clasificar y archivó como cansancio"), se cortó el "sonrió sin humor" y
una frase redundante sobre el paño que tapa la caja. También se
encontró y corrigió, de nuevo, un error de aritmética de años (Ferrero
decía "cuarenta y cinco años" desde el último instrumento serio que
tocó la tela -- el STURP de 1978, canon `[C06 acceso científico con
instrumentos, 1978]` -- corresponden 54, no 45).

**Segunda evaluación: `overall_score` 7.54, aceptado, `slop_penalty` 0.**
`canon_compliance` 9/9. `actualizar_canon.py 7` corrió sin conflictos:
9 entradas nuevas (geografía de la catedral, cronología del viaje, el
protocolo de 22 páginas, la resolución del instrumento hiperespectral,
el circuito de la solicitud, la teca nueva, el pasado de Ferrero con
Amberes, la evaluación descartada de 2020, la tira de 1988).
`state.json::debts` sigue vacío. 2025 palabras (objetivo 2050 --
prácticamente exacto).

Commit incluido junto con esta actualización de `docs/`.

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

El mecanismo (`canon_emergente.md` + `actualizar_canon.py`) suma dos
capítulos más sin `CONFLICTO`: ni el Cap. 6 ni el Cap. 7 chocaron con
la fundación ni con el canon emergente previo. Total acumulado: 7
capítulos, cuatro `CONFLICTO` detectados y resueltos a mano en sesiones
anteriores (Ruti, Zúrich, cronología del Sepulcro, fundación vs.
outline del Cap. 5), ninguno nuevo desde entonces. El hallazgo del
Cap. 7 (tic de lápiz reservado a Sandoz) no fue un `CONFLICTO` de
`actualizar_canon.py` -- lo marcó el juez de `evaluate.py` como riesgo
de `character_voice`, no el script de canon, que no tiene forma de
saber que un tic está reservado para otro personaje que todavía no
apareció.

## Pendiente (no bloqueante)

- **Decidir qué hacer con `ch_01.md`.** Sin cambios -- se redactó con el
  bug de canon de la Tarea 10 activo. Sigue sin decidirse si vale la
  pena releerlo/rehacerlo.
- **Tarea 11** -- punto de aprobación manual por capítulo en
  `run_pipeline.py`. Sin cambios; se sigue aprobando capítulo a
  capítulo a mano, leyendo el archivo (esta sesión, además, se generó y
  entregó PDF de los Cap. 6 y 7 para lectura fuera del entorno --
  `md_to_tex.py` en el scratchpad de la sesión, no versionado en el
  repo, compilado con `xelatex`).
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
- **Nueva: tics de personaje únicos pueden filtrarse a personajes
  secundarios sin que ningún mecanismo automático lo note.** El Cap. 7
  le dio a Ferrero el hábito de anotar a lápiz en los márgenes -- tic
  reservado a Sandoz en `outline.md` (hilo #9, Foreshadowing Ledger),
  que Sandoz ni siquiera apareció todavía en la novela. Ni
  `actualizar_canon.py` ni `evaluate.py::canon_compliance` lo cazan
  porque ninguno de los dos cruza contra el Foreshadowing Ledger, solo
  contra `canon.md`/`canon_emergente.md`; lo detectó el juez por
  intuición de personaje (`character_voice`), no por regla. Se corrigió
  a mano. No hay acción pendiente concreta -- es una clase de error que
  puede repetirse con otros hilos del Ledger (la muñeca de Ferrero, el
  tic de Chiara de enrollar cables) y conviene tenerlo presente al leer
  cada capítulo nuevo, no solo confiar en el juez para cazarlo.

## Próximo paso

**Escribir el Cap. 8** ("Denegado", Debate -- punto bajo del Acto I,
ambición "valle", ~1900 palabras). Zúrich. La denegación llega por
carta: motivos técnicos (Tamiz es, ante el reglamento de 2029, un
no-perito -- su resultado sería legalmente inexistente) y de fondo
(1988, sin nombrarlo -- esta es la "carta muy bien redactada" que
Ferrero anticipó al cierre del Cap. 7, "a veces ponemos cosas ciertas
en los considerandos"). Beats: (1) la carta y sus dos motivos. (2) la
ironía documentada -- Vidal relee el reglamento que lo excluye, ya de
memoria, y lo relee igual: verificar en vez de sentir. (3) rechaza dos
contratos lucrativos sin poder anotar la razón. (4) abre la planilla de
"tiempo perdido" por primera vez desde Jerusalén, mira la entrada del
Sepulcro, no la reclasifica, la cierra. Sin plants nuevos; paga el
hilo #1 (la planilla). Es el capítulo bisagra del Acto I: "la puerta
institucional está cerrada para siempre -- lo que sigue solo puede
llegar por fuera de las instituciones, y él ya lo desea."

```bash
uv run python draft_chapter.py 8
uv run python evaluate.py --chapter=8
uv run python actualizar_canon.py 8
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

**Lección del Cap. 7:** un capítulo aceptado en la primera pasada
igual puede tener un problema real -- leer siempre `character_voice` y
`continuity` del `eval_log` aunque el `overall_score` ya esté sobre el
umbral, no solo cuando rechaza. El tic de lápiz de Ferrero pasó el
umbral (7.04) y era, aun así, un error que iba a costar caro más
adelante en el libro (Cap. 11/12, hilo #9). Antes de escribir un
capítulo con un personaje secundario nuevo, conviene chequear rápido en
`outline.md` si alguno de sus gestos ya está reservado a otro personaje
del Foreshadowing Ledger.

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
5. Leer la entrada de Cap. 8 en `outline.md` (línea ~131) antes de
   redactar.
6. Redactar Cap. 8 a mano con el standalone:
   `uv run python draft_chapter.py 8` → `evaluate.py --chapter=8` →
   `actualizar_canon.py 8`. Leer el capítulo completo y el `eval_log`
   entero (no solo el `overall_score`) antes de avanzar -- si rechaza,
   ver "Lección del Cap. 6"; si acepta, revisar igual
   `character_voice`/`continuity` -- ver "Lección del Cap. 7".
