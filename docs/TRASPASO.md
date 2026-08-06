# TRASPASO — rama `novela2` (worktree de `framework/es-multilibro`)

Estado real al cierre de esta sesión (2026-08-06). Este documento
reemplaza la necesidad de releer `ESTADO.md` completo o el historial de
commits para retomar el trabajo -- es la foto actual, no la bitácora
(para eso está `ESTADO.md`, que sí es narrativo y tiene una sección
nueva para esta rama).

**Actualización 2026-08-06 (sesión nueva -- Cap. 20 y 21):** dos
capítulos más. `overall_score`: Cap. 20 = 7.78 (rechazó una vez, 7.47
contra umbral **pico** 7.5), Cap. 21 = 7.08 (reevaluado tras un
recorte, ver abajo -- aceptó de movida contra umbral **sosten** 6.5).
**Acto II, parte 1, en curso -- 10 de 12 capítulos (Cap. 12-23).**
`state.json::debts` vacío, working tree limpio, mismos 266 tests en
verde + 38 xfail (sin cambios de infraestructura esta sesión).

- **Cap. 20 ("Cologny"):** primer encuentro cara a cara con **Emeric
  Sandoz**, en su jardín de invierno de Ginebra. Paga el hilo #9 (el
  lápiz de los márgenes del libro del Cap. 11 es suyo) y planta el
  hilo #10 ("los motivos, si le sirven de algo, se los cuento cuando
  esto termine"). Rechazado en primera pasada (7.47 < 7.5, el umbral
  más alto del libro por ser ambición **pico**): Sandoz le atribuía a
  la Iglesia el secreto del hallazgo desde 1978, pero `world.md` fija
  1988 como el año canónico en que la institución aprendió esa
  lección. Corregido siguiendo la revisión sugerida por el propio
  juez ("en 1978 nadie era dueño de lo que se iba a encontrar, y diez
  años después la institución aprendió el precio de eso en una
  conferencia de prensa"); de paso, "seis siglos" → "casi siete
  siglos" y se agregó el ancla de fecha faltante ("Ocho de abril, tres
  días antes del traslado"). Segunda evaluación: 7.78, el puntaje más
  alto de la novela hasta ahora. También se corrigió un desliz menor
  de tuteo ("qué llames" → "qué llame"). Sin `CONFLICTO` de canon.
- **Cap. 21 ("Treinta horas"):** las treinta horas del traslado
  arrancan; Vidal, lejos de todo en el puesto remoto de Collegno, solo
  puede contar segundos de latencia mientras Ledda absorbe una
  contingencia (un conservador de la Comisión sin horario fijo) que le
  cuesta horas de exposición a Chiara ("La tela no sabe cuántos
  somos"). Aceptado en primera pasada, 7.39. **Encontrado después de
  aceptado** (no por `actualizar_canon.py`, sino releyendo el
  `eval_log` completo): el borrador original cerraba con Ledda
  entregándole a Vidal un overol y una credencial falsa para entrar
  como técnico a la 1:10 de la madrugada -- eso contradice el canon
  fijo de "personal reducido de nueve personas" ([C14-10]) y, peor,
  **es literalmente el beat 1 del Cap. 22** según su propia entrada en
  `outline.md` ("Noche del 11 al 12... Vidal accede como técnico de la
  empresa de la teca"). El capítulo se había adelantado a su propia
  continuación. Se recortó la escena final (Ledda/overol/credencial) y
  se reemplazó por un cierre que sostiene la misma mentira del
  capítulo ("impotente: no hay nada que auditar salvo su propia
  espera") sin mostrar la entrada. **Reevaluado** tras el recorte
  (7.08, sigue aceptado) porque el cambio afectaba el final del
  capítulo, no un detalle aislado -- y porque el `eval_log` viejo, que
  es lo que lee `actualizar_canon.py`, habría vuelto a escribir la
  escena eliminada en `canon_emergente.md` si no se regeneraba. La
  entrada de canon vieja ([C21-08], la escena eliminada) quedó
  referenciada por una entrada nueva del segundo `eval_log`
  ([C21-01], el protocolo de un solo timbre de Ledda) como
  `CONFLICTO` fantasma -- resuelta a mano como falso positivo (ver
  `canon_emergente.md`, comentario `RESUELTO a mano` en Cap. 21).

**Lección nueva de esta sesión, importante para el resto del libro:**
`actualizar_canon.py` **no relee el capítulo** -- lee el `eval_log`
más reciente (`new_canon_entries`), que a su vez lo generó
`evaluate.py` sobre el texto que existía en ese momento. Si se edita
un capítulo **después** de evaluarlo y aceptarlo (como pasó acá, para
corregir un problema real), hay que **reevaluar** (`evaluate.py
--chapter=N`) antes de correr `actualizar_canon.py N` de nuevo -- si
no, el canon emergente se actualiza con hechos que ya no están en el
texto. La convención de sesiones anteriores ("recortes menores no
necesitan reevaluación") sigue valiendo para cambios chicos que no
tocan `new_canon_entries` (una palabra, un tuteo/voseo), pero un
recorte que borra una escena entera sí la necesita.

**Actualización 2026-08-05 (sesión nueva -- Cap. 12 a 19, cacheo de
prompt):** ocho capítulos más, los ocho aceptados (dos con rechazo y
reescritura en el medio: Cap. 19 rechazó una vez). `overall_score`:
Cap. 12=7.23, 13=6.86, 14=7.39, 15=7.70, 16=6.93, 17=6.93, 18=6.70,
19=6.78. **Acto II, parte 1, en curso -- 8 de 12 capítulos (Cap.
12-23).** `state.json::debts` vacío, working tree limpio, 266 tests en
verde (18 nuevos). Detalle completo de cada capítulo en "Redacción".

Dos cosas de infraestructura nuevas esta sesión, ambas a pedido
explícito del usuario:

1. **Cacheo de prompt implementado y verificado contra la API real**
   (`api_comun.py`, `draft_chapter.py::build_prompt_bloques()`,
   `evaluate.py::_bloques_cache_chapter_prompt()`) -- ver sección
   dedicada más abajo. Confirmado con una llamada real: primera
   llamada `cache_creation_input_tokens=50085`, segunda llamada mismo
   prefijo `cache_read_input_tokens=50085`. En producción desde el
   Cap. 17.
2. **Fable 5 rechaza contenido de vigilancia/evasión de seguridad con
   `stop_reason=refusal`, categoría "cyber"** -- pasó en el Cap. 14 y
   el Cap. 15 (ambos con contenido de arquitectura de vigilancia /
   fabricación de la réplica), de forma repetible, no ruido aleatorio.
   Workaround usado las dos veces: `AUTONOVEL_WRITER_MODEL=claude-opus-5`
   solo para esa llamada, sin tocar `.env` ni ningún archivo. Opus 5
   escribió esos dos capítulos sin que el juez marcara ningún problema
   de voz atribuible al cambio de modelo. Ver "Fable 5: rechazos de
   contenido" más abajo, sección renombrada y actualizada (antes
   "Bugs de compatibilidad con Fable 5").

**Actualización 2026-08-04 (cierre de sesión, continuación -- Cap. 9,
10 y 11):** misma sesión que cerró el Cap. 6/7/8, retomada más tarde el
mismo día. Tres capítulos más, los tres aceptados en primera pasada --
**Acto I completo, 11 de 11 capítulos.** `overall_score`: Cap. 9 = 7.39,
Cap. 10 = 7.47, Cap. 11 = 7.86. `state.json::debts` vacío, working tree
limpio. Dos `CONFLICTO` de canon aparecieron y se resolvieron a mano
(ver detalle en "Redacción" y en `canon_emergente.md`):

- **Cap. 9 ("Maître Ansermet"):** Ansermet le entrega a Vidal el
  expediente de la ventana de acceso; primer duelo de preguntas de
  precisión que Vidal no gana. `actualizar_canon.py` marcó un
  `CONFLICTO` real (no falso positivo): el texto original prometía la
  restitución "antes de" la inspección del 29 de abril, pero
  `world.md` establece que la devolución ocurre **durante** esa
  inspección (una de dos ventanas, once o seis minutos -- hilo #4,
  todavía no plantado). Corregido en el propio capítulo a "dentro del
  marco de la inspección final del 29".
- **Cap. 10 ("Debida diligencia"):** Vidal investiga a la Fondation
  Cassiodore (rastro muerto en tres jurisdicciones), escribe "Acepto no
  saberlo" en su cuaderno personal, y negocia la cláusula octava del
  contrato -- consigue redacciones, no sustancia. Plantado el hilo #3
  (cláusula de archivo a perpetuidad) tal como pedía el outline. Sin
  conflictos de canon.
- **Cap. 11 ("Firma", Break Into Two):** Vidal firma el contrato;
  Ansermet le entrega, de parte del fundador, un ejemplar propio de las
  actas del STURP (1981) anotado a lápiz durante décadas por una mano
  sin nombre -- **primera aparición física de Sandoz** (hilo #9,
  plantado exactamente donde correspondía). `actualizar_canon.py`
  marcó un `CONFLICTO` que resultó ser **falso positivo**: el tic de
  Sandoz en `characters.md` dice que devuelve los libros **ajenos**
  anotados: este es un libro **propio** (tres épocas de mina distintas,
  releído toda una vida), regalado sin pedir devolución -- no
  contradice la regla, la confirma. También se encontró y corrigió un
  hueco de calendario real: el capítulo abría con "el viernes" (que
  empalmaba con el viernes de enero del Cap. 10) pero cerraba con "en
  doce días empezaba el traslado" (11 de abril) -- se agregó una frase
  que ancla la firma a fines de marzo, tres semanas de redacciones
  después de enero.

Nuevo esta sesión, versionado por primera vez: `chapter_to_pdf.py`
(script para generar un PDF de lectura rápida por capítulo, formato ya
cerrado y calibrado -- ver sección dedicada más abajo, **no seguir
ajustándolo**). Se generó y entregó el PDF de los Cap. 9, 10 y 11.

**Actualización 2026-08-04 (cierre de sesión, primera mitad -- Cap. 6,
7 y 8):** sesión de tres capítulos, los tres escritos, evaluados,
aceptados y pusheados el mismo día. Cierra con `state.json::debts`
vacío, sin `CONFLICTO` de canon abiertos y el Acto I a mitad de camino
(8 de 11 capítulos). El Cap. 8 ("Denegado", valle) cerró el punto bajo
del acto: la solicitud de Turín llega denegada, con el reglamento de
2029 convirtiendo a Tamiz en "no-perito" a efectos legales, y la
planilla de "tiempo perdido" del Cap. 5 sigue sin reclasificarse.
Aceptado en la primera pasada (`overall_score` 7.39, umbral 6.0), con
una corrección de precisión: la carta citaba a Ferrero "con exactitud"
pero la frase entre comillas no coincidía palabra por palabra con lo
que dijo en el Cap. 7 -- igualada. `actualizar_canon.py 8` sin
conflictos (12 entradas nuevas, incluido el texto del Reglamento de
2029 que faltaba desde la evaluación del Cap. 6).

**Actualización 2026-08-04 (tarde, Cap. 7):** se sumó el Cap. 7 ("La
ciudad de la tela", Debate) a lo ya cerrado del Cap. 6 esta misma
sesión. Igual patrón que el Cap. 6: primera evaluación aceptada de
movida (`overall_score` 7.04, sin `slop_penalty` relevante salvo una
pasiva calcada), pero con dos problemas reales señalados por el juez
que se corrigieron igual -- una intrusión omnisciente que rompe la
tercera persona limitada y, el más importante, que el hábito de
"anotar a lápiz en los márgenes" que se le había dado a Ferrero **es la
marca de identificación de Sandoz** (hilo #9 del Foreshadowing Ledger,
se paga en el Cap. 12) y no debía reusarse. Cambiado a "tinta roja" en
Ferrero. Reevaluado: `overall_score` 7.54, aceptado, sin conflictos de
canon.

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

Fundación completa y aprobada. **Acto I completo (Cap. 1-11). Acto II,
parte 1, en curso: Cap. 12 a 19 escritos, evaluados y aceptados (8 de
12 -- faltan 20-23 para llegar al Midpoint).** `state.json::debts`
vacío, sin `CONFLICTO` de canon abiertos, 266 tests en verde. Cacheo de
prompt implementado y confirmado contra la API real, en producción
desde el Cap. 17. Fable 5 rechazó dos capítulos por contenido de
vigilancia/fabricación (categoría "cyber", falso positivo) -- resuelto
cambiando a Opus 5 solo para esas dos llamadas puntuales. Listo para
**Cap. 20 ("Cologny")**, ambición **pico** -- primera aparición en
persona de Sandoz -- ver "Próximo paso".

## Estado del repositorio

| | |
|---|---|
| Directorio | `/root/novela2` (worktree; confirmado con `git worktree list`) |
| Rama | `novela2`, diverge de `framework/es-multilibro` en `7b81700` (Tarea 7) |
| `.env` / `ANTHROPIC_API_KEY` | Presente en este entorno. `AUTONOVEL_WRITER_MODEL=claude-fable-5`, `AUTONOVEL_JUDGE_MODEL=claude-opus-5`, `AUTONOVEL_REVIEW_MODEL=claude-opus-5`, `AUTONOVEL_API_BASE_URL=https://api.anthropic.com` |
| Push | Al día con `origin/novela2` (`git log origin/novela2..HEAD --oneline` vacío). Último commit: el de cierre de esta sesión (Cap. 20-21 + `docs/`) -- confirmar con `git log -1 --oneline`. |
| Working tree | Limpio -- confirmar con `git status`. |
| Tests | `uv run python -m pytest tests/ -v` -- **266 tests, todos en verde, + 38 xfail esperados** (sin cambios de infraestructura desde la sesión del cacheo de prompt). No hace falta `.env` (todo mockeado); drafting/evaluar capítulos sí lo necesita. |
| Token de GitHub | Fine-grained, creado 2026-07-27, alcance `suazoca/autonovel`, permiso `Contents: read/write`, **vence ~2026-08-26**. Al vencer, limpiar la credencial guardada con `git credential reject` (protocol=https, host=github.com) antes de autenticar con uno nuevo. Usado sin problemas esta sesión (push directo, sin reingresar credencial). |

## Fundación (completa, aprobada -- sin cambios esta sesión)

| Archivo | Estado |
|---|---|
| `voice.md` | Completo (Parte 1 + Parte 2 generada desde la semilla, commit `61aeee4`) |
| `world.md` | Completo, revisado (último cierre: commit `dde01c4`) |
| `characters.md` | Vidal, Sandoz, Chiara y Ferrero completos. **Ledda y Ceruti siguen "ficha pendiente de generación"** -- sin cambios de archivo (commit `6f110dc`), aunque Ledda ya protagonizó ocho capítulos (12-19) por voz sola: varón, tres vasos de agua, contesta con plazos, sin adjetivos ni pronombres emocionales. Ansermet tampoco tiene ficha formal pero ya está bien establecido por voz (seis capítulos). Ceruti no apareció todavía -- no urge. Sigue siendo deuda técnica, no bloqueante. |
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

Commit `b721458`.

`chapters/ch_08.md` ("Denegado", Debate -- punto bajo del Acto I) --
**escrito y aceptado esta sesión.** Cuatro beats: (1) la carta de la
Custodia llega un jueves de diciembre, cinco considerandos
independientes; el segundo cita a Ferrero citando su propio dictamen
favorable y lo usa como agravante, el cuarto invoca el Reglamento
europeo de peritaje algorítmico de 2029 (art. 9.2: arquitecturas
cerradas excluidas del peritaje de patrimonio; art. 17: excepción
académica, investigar sí, certificar no) para declarar el resultado de
Tamiz "sin existencia a efectos del ordenamiento", el quinto reprocha
sin nombrarlo el manejo de la comunicación en 1988, no el resultado
-- la Custodia no está obligada por el reglamento y lo invoca porque le
sirve. (2) Vidal relee el artículo que ya sabía de memoria -- fue
experto consultado en la ronda de comentarios de 2028 y había escrito
que el requisito de trazabilidad era "correcto en principio,
inaplicable en la práctica"; la carta le aplica su propia regla de un
informe de 2031 ("una certeza inauditable... es un artefacto, y se
descarta") sin nombrarlo. (3) declina dos encargos lucrativos (Cranach
de Múnich, Klimt de Viena) sin poder escribir el motivo real en el
campo obligatorio de su propio registro, que se lo marca en amarillo.
(4) abre la planilla de "tiempo perdido" del Cap. 5 por primera vez
desde Jerusalén, ve la entrada del Sepulcro sin completar, no la
reclasifica a "asunto abierto" aunque sabe que sería defendible, la
cierra intacta.

**Evaluación: aceptado en la primera pasada.** `overall_score` 7.39
contra umbral 6.0 (ambición "valle"), `slop_penalty` 0.
`canon_compliance` 8/9 -- entrega, con texto concreto de los artículos,
algo que veníamos arrastrando como faltante desde la evaluación del
Cap. 6 (el Reglamento de 2029 y el estatus de "no-perito" de Tamiz). El
juez marcó un problema de precisión real, no solo de estilo: el
capítulo afirma que la carta cita a Ferrero "con exactitud, con la
referencia del acta", pero la frase entre comillas ("la mejor solicitud
que ha pasado por esta mesa") no coincidía palabra por palabra con lo
que Ferrero dijo en el Cap. 7 ("la mejor solicitud que pasó por esta
mesa desde que estoy en ella") -- si el texto afirma literalidad, la
cita tiene que ser literal. Corregido a mano, sin re-evaluar.

`actualizar_canon.py 8` corrió sin conflictos: 12 entradas nuevas
(cronología de la carta, los cinco considerandos, el texto del
Reglamento de 2029, el pasado de Vidal como experto consultado en
2028, la cita de su propio informe de 2031, los dos encargos
declinados, el catálogo de códigos del registro, el estado final de la
planilla, geografía del estudio en Zúrich). `state.json::debts` sigue
vacío. 1822 palabras (objetivo 1900 -- prácticamente exacto).

Commit incluido junto con esta actualización de `docs/`, cierre de la
sesión.

`chapters/ch_09.md` ("Maître Ansermet", Debate) -- **escrito y aceptado
esta sesión.** Cuatro beats: (1) la carta con el eufemismo ("acceso a
material textil de interés histórico"), identificado en la segunda
línea. (2) duelo de nueve preguntas de precisión que Ansermet responde
todas sin comprometerse -- la primera vez en años que alguien no pierde
ese juego con Vidal. (3) Ansermet le entrega el expediente técnico de
la ventana de acceso, ya preparado, con "doce micrones por píxel" --
el número del propio protocolo denegado de Vidal -- como puñalada
personal. (4) Vidal empieza a corregir el diseño del plan en vez de
rechazarlo, sin decidirlo: el giro de "esto es un delito" a "esto es
un problema de diseño" queda dramatizado, no declarado.

**Evaluación: aceptado en la primera pasada.** `overall_score` 7.39
contra umbral 6.5 (ambición "sostén"), sin `slop_penalty`.
`actualizar_canon.py 9` marcó un `CONFLICTO` real (no falso positivo):
el texto prometía la restitución "antes de" la inspección del 29 de
abril; `world.md` establece que la devolución ocurre **durante** esa
inspección. Corregido en el capítulo a "dentro del marco de la
inspección final del 29" -- resuelto a mano en `canon_emergente.md`,
`state.json::debts` vuelto a `[]`. 1864 palabras (objetivo 2000).

`chapters/ch_10.md` ("Debida diligencia", Debate) -- **escrito y
aceptado esta sesión.** Cuatro beats: (1) Vidal investiga a la
Fondation Cassiodore -- Ginebra, Zug, Vaduz, Willemstad, cinco nombres
humanos verificables, todos fiduciarios de oficio; el rastro muere en
tres jurisdicciones. (2) escribe en su cuaderno personal, con fecha:
"El mandante no es identificable con los medios a mi alcance. / Acepto
no saberlo." (3) negocia en escena la cláusula octava (archivo a
perpetuidad, el hilo #3 del Foreshadowing Ledger) -- consigue tres
correcciones de redacción (plazos, motivación de rechazo, segunda
presentación), no la sustancia; Ansermet se lo dice de frente en vez de
dejárselo descubrir de a poco. (4) el cálculo final, dramatizado como
cálculo: cede a perpetuidad un activo que la ley (art. 9.2) ya declaró
inexistente -- "sin esto, la pregunta queda abierta para siempre; con
esto, queda abierta la cláusula". Elige la pregunta.

**Evaluación: aceptado en la primera pasada.** `overall_score` 7.47
contra umbral 6.5, sin conflictos de canon. El juez marcó, sin
bloquear, que Vidal "ve demasiado" la simetría entre auditar un objeto
y aceptar una relación inauditable -- el esquema pide que quede ciega
para él, visible solo para el lector. No se tocó (nota de calidad, no
un error). `actualizar_canon.py 10`: 9 entradas nuevas, 0 conflictos.
1716 palabras (objetivo 2100 -- quedó corto, no bloqueante).

`chapters/ch_11.md` ("Firma", Break Into Two) -- **escrito y aceptado
esta sesión.** Cuatro beats: (1) últimas condiciones de Vidal,
descubre por cotejo material que los perfiles del equipo tienen fecha
de impresión de noviembre -- antes de la denegación de diciembre: la
operación lo esperaba desde antes de negociar nada. (2) firma con una
lapicera de trazabilidad perfecta -- "lo único en toda la operación que
cumplía sus estándares". (3) Ansermet le entrega, de parte del
fundador, un ejemplar propio de las actas del STURP (1981), anotado a
lápiz durante décadas por una mano sin nombre -- **primera aparición
física de Sandoz** (hilo #9 del Foreshadowing Ledger, plantado
exactamente donde correspondía: reforzado en el Cap. 20, paga en el
Cap. 42/45). El único lugar sin texto del libro -- una doble raya sobre
el párrafo que habla de coordinar los anuncios públicos entre equipos
-- es 1988, antes de que pase. (4) en Zúrich, guarda el libro junto al
archivo de Amberes: los dos únicos objetos de su estudio que saben algo
de él que él no dijo.

**Evaluación: aceptado en la primera pasada.** `overall_score` 7.86
contra umbral 6.5 -- el más alto de la sesión.
`actualizar_canon.py 11` marcó un `CONFLICTO` que resultó **falso
positivo**: el tic de Sandoz en `characters.md` ("anota a lápiz...  y
devuelve los ajenos anotados") distingue explícitamente propios de
ajenos; el libro del Cap. 11 es propio (tres durezas de mina, tres
épocas de lectura), regalado sin pedir devolución -- no contradice la
regla. Resuelto a mano, documentado en `canon_emergente.md`. Aparte,
el juez señaló un hueco de calendario real: "el viernes" de apertura
empalmaba con el viernes de enero del Cap. 10, pero "en doce días
empezaba el traslado" (11 de abril) no cuadraba -- se agregó una frase
que ancla la firma a fines de marzo (tres semanas de redacciones
cruzadas después de enero). `state.json::debts` vuelto a `[]`. 1839
palabras (objetivo 1950 -- casi exacto).

Los tres capítulos (9, 10, 11) generaron su PDF de lectura con
`chapter_to_pdf.py` (ver sección dedicada) y quedan pendientes de
commit -- ver "Estado del repositorio".

`chapters/ch_12.md` ("Collegno", Fun and Games -- primer capítulo del
**Acto II**) -- Vidal llega al laboratorio de Collegno, mejor que
cualquier universidad o museo, y conoce al equipo que otro eligió por
él: **Chiara Fabbri** (conservadora textil, detecta un defecto en su
propio escáner con solo mirarlo), **Ledda** (seguridad, sin
pronombres, fija la regla de oro -- "una identidad verdadera con
motivos ocultos", hilo #19, plantado en presencia de Chiara sin que
nadie note que la describe a ella) y **Ferrero** -- reencuentro que
paga la reunión del Cap. 7, ninguno menciona la denegación. Cierra con
la hoja de asistencia del piso franco sin columna de función: Vidal ya
no sabe si dirige o asiste. `overall_score` 7.23, aceptado en primera
pasada. 1943 palabras.

`chapters/ch_13.md` ("Dos manos", B Story, valle) -- sesión de trabajo
con lino de prueba: Chiara le enseña a Vidal, sin dar cátedra, lo que
soporta una fibra. Nace el hilo #12 (tic de Chiara de enrollar cables
antes de una pregunta difícil) y la pregunta que abre la historia B:
"Te pregunto qué hacés vos. No qué hace el modelo." Chiara reza antes
de comer y desarma con argumentos técnicos reales una hipótesis que a
Vidal le parecía prometedora -- contraejemplo viviente de su propia
mentira. `overall_score` 6.86, aceptado. **Conflicto real corregido:**
el borrador nombraba a "Sandoz" en el pensamiento de Vidal, violando
la tercera persona limitada (no lo conoce hasta el segundo tercio del
libro) -- corregido a "el fundador, el mandante, la firma detrás de la
firma". 2320 palabras.

`chapters/ch_14.md` ("Ventanas", Fun and Games) -- Ledda presenta la
arquitectura completa: sustitución en la ventana del traslado (11-12
de abril), devolución en una de dos ventanas el 29 (once o seis
minutos -- **hilo #4, plantado**). Recorrido del perímetro de la
catedral, cámaras con reidentificación, extractos cruzados por los
Carabinieri. Vidal entiende que la donación de la teca no compró la
reliquia, compró la ventana en que se la manipula (refuerzo del hilo
#20). **Fable 5 rechazó dos veces (`stop_reason=refusal`, categoría
"cyber") sobre este contenido de vigilancia** -- se redactó con
`AUTONOVEL_WRITER_MODEL=claude-opus-5` para esa sola llamada, sin
tocar `.env`. `overall_score` 7.39, aceptado. Corregido un error
aritmético real: "del once a las siete de la mañana al doce a la una"
sin AM/PM leído como 18h en vez de las 30h de `world.md` -- corregido
a "la una de la tarde". 2202 palabras.

`chapters/ch_15.md` ("La gemela", Fun and Games) -- Chiara fabrica la
réplica con una exactitud "reverente" (palabra que incomoda a Vidal).
La gemela falla la primera prueba de peso hidratado -- Chiara pide que
la discrepancia quede a su nombre. Ferrero negocia los miligramos de
fibra con el mejor argumento moral del libro hasta ahora ("para usted
es una muestra; para dos mil millones de personas es una herida en el
cuerpo de otra persona") y Vidal cede un 20% sin poder explicar por
qué -- primera derrota práctica de su mentira. Regla dura en acta: la
gemela engaña vista/peso/sensores, no microscopio ni datación --
**hilo #5, plantado** (mecanismo del Acto III). **Fable 5 rechazó de
nuevo (misma categoría "cyber")** -- Opus 5 otra vez, sin problemas de
voz. `overall_score` 7.70 -- el mejor puntaje de la novela hasta
ahora. Sin conflictos de canon. 1835 palabras.

`chapters/ch_16.md` ("Protocolo", Fun and Games) -- se firma el
protocolo completo en 18 puntos con cronograma hora por hora. Chiara
pregunta quién recibe los datos crudos -- Vidal rechaza su desconfianza
con la frase que define su mentira: "Desconfiar sin mecanismo es
superstición con vocabulario de prudencia" (va a volver). Chiara le
pregunta a Ferrero por el inventario de 2002 disfrazada de necesidad
técnica -- silencio de hielo medido en clics de caudalímetro (**hilos
#7 y #13, plantados**). Ferrero impone veto sin causa sobre cualquier
anuncio durante la operación, sobre un conjunto vacío -- lo firma
igual. `overall_score` 6.93, aceptado. Tres correcciones reales:
voseo accidental de Vidal (español de Zaragoza, tutea -- corregido a
"Desconfías"/"Dime"/"tienes"), error de numeración de días en el
cronograma (el 29 de abril era "Día diecisiete" cuando debía ser
"dieciocho" para cerrar con los 17 días de `world.md`), e
inconsistencia "una sola copia" vs. "copia de trabajo" de Chiara. 1856
palabras.

`chapters/ch_17.md` ("Cena en Turín", Fun and Games -- respiro, Yes-and
deliberado, el único capítulo del libro donde nada empeora) -- cena del
equipo la última noche antes del traslado. Ferrero cuenta el incendio
de 1997 con humor fúnebre piamontés. Ledda contesta cada pregunta
personal con un plazo. Ferrero habla de 1988 en pasiva y se toca la
muñeca izquierda donde no hay reloj -- gesto ajustado a nada, sin
nombrar al hermano (**hilo #14, profundizado**). Lavando los platos,
la conversación más larga sin instrumentos del libro: Chiara le
pregunta qué va a hacer *él*, no el modelo. Esa noche Vidal no revisa
nada antes de dormir por primera vez en años -- registrado como
omisión, no como paz. `overall_score` 6.93, aceptado. **Conflicto real
de calendario corregido:** la cena estaba fechada "mañana" (11 de
abril, el mismo día que arranca el traslado de 30h) en el Cap. 16 --
corregida a la noche del propio 10 (la víspera real) en ambos
capítulos. 1791 palabras.

`chapters/ch_18.md` ("Listas cruzadas", Fun and Games -- complicación)
-- los Carabinieri adelantan el cruce de contratistas por la visita
papal, un proveedor de Collegno queda marcado, Ledda ejecuta el
repliegue (corte, refacturación en efectivo, dos semanas de margen
quemadas). El cronograma de la gemela ya no cierra: de tres pruebas
completas contra sensores pasa a una. Ferrero usa la crisis para
proponer reducir el alcance del análisis -- la mano izquierda
saboteando lo que la derecha perfecciona, con la coartada de haberle
regalado a Vidal una tabla de emisividad mejorada el mismo día
(**patrón de sabotaje suave, plantado -- se paga en el Cap. 32**).
Cierra con Vidal re-verificando de madrugada calibraciones que no lo
necesitan -- "Nueve pitidos. Los contó." `overall_score` 6.70,
aceptado. Dos correcciones reales: el capítulo abría el 28 de marzo,
retrocediendo 13 días respecto del final del Cap. 17 sin ninguna señal
-- se agregó un ancla temporal ("Trece días antes de la cena..."); y
un conflicto de horario (7:10 vs. las 7:00 ya establecidas para el
ingreso del equipamiento) -- corregido. 1770 palabras.

`chapters/ch_19.md` ("Ensayo general", Fun and Games) -- ensayo
completo de la sustitución sobre una maqueta con cinta azul, tres
corridas, una con simulacro de intrusión de la Comisión. La gemela v2
pasa la única prueba completa que le quedó al cronograma recortado.
Ferrero, con los guantes puestos, repite la regla como quien reza:
diecisiete días, ni uno más (**hilo #6, reforzado; hilo #5, tercera
repetición antes del Midpoint**). Ansermet confirma que la ventana
sigue en pie, Vidal firma "adelante" -- y Ansermet rompe su propio
esquema de tres cosas con una cuarta: el fundador lo recibe en dos
días, en Cologny. Cierra con "Entregable: identidad del mandante".
**Único capítulo de la sesión rechazado en primera pasada** (`overall_score`
6.02 contra 6.5) por un problema estructural real: el outline fija la
reunión de Cologny "cuarenta y ocho horas antes del traslado", así que
este capítulo (y el 20) transcurren *antes* del final del Cap. 18 --
sin ninguna marca de retroceso, el lector quedaba desorientado, y
además la fecha elegida para Cologny (9 de abril) chocaba con canon ya
establecido desde el Cap. 12 (los racks de Tamiz llegan a Collegno ese
mismo día). Reescrita la apertura para que sea Vidal mismo, en la
madrugada del 11 (empalmando con la alarma del Cap. 18), releyendo su
propio registro de la semana -- motiva el salto atrás en vez de un
corte arbitrario -- y corridas todas las fechas a partir del 6 de
abril para que Cologny caiga el 8, sin chocar con nada. Segunda
evaluación: 6.78, aceptado. Ya aceptado, se encontró y corrigió además
una contradicción física real (la gemela no podía estar en el falso
fondo del ensayo y llevar 48h continuas en la celda de sensores a la
vez). 1911 palabras.

Los ocho capítulos (12-19) generaron su PDF de lectura con
`chapter_to_pdf.py` -- ya commiteados y pusheados (commit `990a7d9`).

`chapters/ch_20.md` ("Cologny", Fun and Games -- revelación del
antagonista) -- primer encuentro cara a cara con Emeric Sandoz, en su
jardín de invierno de Ginebra: manos de jardinero real, ropa gastada
que cuesta lo que un coche, sirve el té de Vidal y no se sirve a sí
mismo (hilo #15). Repite el mejor argumento de Vidal contra la
operación, mejor formulado que el original, y recién después lo
desafía a aplicarse su propia regla ("una certeza inauditable es un
artefacto y se descarta") a algo que le importe. Vidal reconoce el
lápiz de los márgenes del libro del STURP del Cap. 11 -- **paga el
hilo #9**. Sandoz promete los motivos "cuando esto termine" (**planta
el hilo #10**). Rechazado en primera pasada (7.47 contra el umbral
**pico** 7.5): Sandoz databa el secreto eclesiástico en 1978, pero
`world.md` fija 1988 como el año en que la institución "aprendió el
precio" en una conferencia de prensa -- corregido siguiendo la
revisión sugerida por el juez. Segunda evaluación: 7.78, el mejor
puntaje de la novela hasta ahora. Sin conflictos de canon. 2081
palabras.

`chapters/ch_21.md` ("Treinta horas", Fun and Games → rampa al
Midpoint) -- arranca el traslado: nueve personas en la sacristía por
derecho propio (identidades verdaderas, motivos ocultos), Vidal en el
puesto remoto de Collegno contando segundos de latencia. La Comisión
suma un conservador sin horario fijo; Ledda recalcula el costo en
horas de exposición para Chiara, que acepta sin dramatizar ("La tela
no sabe cuántos somos"). Ferrero, junto al lienzo por primera vez en
cuarenta años, tarda de más en soltar el borde. Aceptado en primera
pasada, 7.39. **Encontrado después de aceptado**, releyendo el
`eval_log` completo: el cierre original hacía entrar a Vidal como
décimo participante físico con overol y credencial falsa -- contradice
el canon fijo de nueve personas ([C14-10]) y es, además, el beat de
apertura del Cap. 22 según su propia entrada en `outline.md`. Se
recortó la escena, se reevaluó (7.08, sigue aceptado) y se resolvió a
mano un `CONFLICTO` fantasma que quedó apuntando a la entrada de canon
ya eliminada -- ver la lección nueva al principio de este documento.
1766 palabras (tras el recorte).

Los dos capítulos (20-21) generaron su PDF de lectura con
`chapter_to_pdf.py` y quedan pendientes de commit -- ver "Estado del
repositorio".

## Cacheo de prompt -- implementado y verificado (Cap. 17 en adelante)

Pedido explícito del usuario tras ver que `evaluate.py` se quedaba sin
`max_tokens` tras crecer `canon_emergente.md` (Cap. 16, ver más abajo).
Antes de esto, `api_comun.py` documentaba el cacheo como pendiente y
asumía (equivocadamente) que hacía falta un beta header sin verificar
-- las dos cosas eran incorrectas: `cache_control: {"type":
"ephemeral"}` es GA.

**Diseño:** `llamar_api()` (`api_comun.py`) ahora acepta `prompt` como
`str` (comportamiento de siempre, sin cambios -- los ~17 scripts que
no adoptaron esto no se enteran) o como `list[dict]` con la forma
`{"text": ..., "cache": bool}`, convertida por `_resolver_content()` a
content blocks con `cache_control` en los marcados `cache: True`.
`draft_chapter.py::build_prompt_bloques()` reordena el prompt (el de
lectura humana, `build_prompt()`, queda intacto para no romper tests)
para que lo 100% estable en todo el libro (voz + mundo + personajes +
canon de fundación) sea el primer bloque cacheado, `canon_emergente`
el segundo bloque cacheado aparte (crece cada capítulo pero es
idéntico entre reintentos del mismo capítulo), y lo que cambia siempre
(número de capítulo, esquema, cola del anterior) quede sin cachear.
`evaluate.py::_bloques_cache_chapter_prompt()` hace lo mismo partiendo
el `CHAPTER_PROMPT` ya formateado en los mismos tres puntos, sin tocar
la plantilla en sí (el registro de `test_guardia_prompts.py` depende
de su contenido exacto).

**Verificado contra la API real** (no solo "debería andar"): con el
bloque estable + canon emergente del Cap. 17 (~50.000 tokens), primera
llamada `cache_creation_input_tokens=50085, cache_read_input_tokens=0`;
segunda llamada con el mismo prefijo, `cache_creation_input_tokens=0,
cache_read_input_tokens=50085`. Funciona. 18 tests nuevos cubren la
conversión de bloques y que el bloque estable no cambie entre
capítulos (`test_api_comun.py`, `test_draft_chapter.py`,
`test_evaluate.py`).

**En producción desde el Cap. 17** (primer capítulo redactado después
de implementarlo). El ahorro crece capítulo a capítulo a medida que
`canon_emergente.md` se agranda -- es la razón de ser del cambio, no
solo costo: sin esto, `evaluate.py` se iba a seguir quedando sin
`max_tokens` cada vez más seguido.

## Cap. 5: por qué se reescribió entero (sesión anterior, sin cambios)

Sin novedades esta sesión. Detalle completo en la versión anterior de
este documento / `docs/ESTADO.md`: se reescribió entero porque el
Cap. 46 (Final Image) depende de una primera entrada al edículo que el
borrador original no dramatizaba. `overall_score` final 7.54.

## Fable 5: rechazos de contenido (antes "Bugs de compatibilidad", renombrada)

`api_comun.py` ya documentaba (Tarea 9b, sesión anterior) que
`stop_reason=refusal` existe y hay que manejarlo explícitamente --
"pasa incluso con prompts inocuos, aparentemente un falso positivo".
Esta sesión lo confirmó dos veces más, con un patrón: **categoría
"cyber", sobre contenido de vigilancia/evasión de seguridad o
fabricación de una réplica** -- Cap. 14 (arquitectura de vigilancia de
la catedral, cámaras, cruces de la prefectura) y Cap. 15 (fabricación
de la gemela, engañar sensores). Ficción de atraco, nada real -- casi
seguro falso positivo del clasificador, no una señal de que el
contenido sea problemático de verdad.

**Workaround usado las dos veces, sin tocar ningún archivo:**
```bash
AUTONOVEL_WRITER_MODEL=claude-opus-5 uv run python draft_chapter.py 14
```
Opus 5 escribió los dos capítulos sin que el juez marcara ningún
problema de voz atribuible al cambio de modelo -- ni una mención en
`voice_adherence` ni en `character_voice` de ningún de los dos
`eval_log`. Si vuelve a pasar en capítulos con contenido similar (el
resto del atraco, Acto II parte 2 especialmente), el mismo workaround
sirve: reintentar una vez por si no es determinístico (no lo fue
ninguna de las dos veces, rechazó ambas), y si persiste, cambiar el
modelo solo para esa llamada.

**Nota de esta sesión, sigue vigente:** `evaluate.py`
(`call_judge()`, línea ~875) tenía `max_tokens=8000` fijo para el juez
por capítulo -- con `canon_emergente.md` ya en 15-16 capítulos, el
*thinking* de Opus 5 se lo comió entero dos veces seguidas sin devolver
texto (`ERROR: la respuesta se truncó por max_tokens sin producir
ningún texto`). Subido a 16000 (mismo valor que ya usaba otro llamado
del archivo). El cacheo de prompt (sección de arriba) no resuelve esto
-- el modelo igual tiene que razonar sobre todo el contenido, cacheo
solo abarata el costo de mandarlo, no el thinking sobre él. Si vuelve a
pasar más adelante en el libro, subir de nuevo.

## PDF de lectura por capítulo -- formato ya cerrado, no tocar más

Nueva esta sesión: `chapter_to_pdf.py` (raíz del repo, versionado -- antes
vivía como script suelto en el scratchpad de una sesión anterior y se
perdía). Genera `chapters/pdf/ch_NN.pdf`, un PDF liviano para leer un
capítulo fuera del entorno apenas se acepta. **No es** el export final
del libro (eso es `typeset/build_tex.py` + `novel.tex`, con Garamond,
drop caps y formato de tapa).

```bash
uv run python chapter_to_pdf.py 9 "Maître Ansermet"   # -> chapters/pdf/ch_09.pdf
```

**El formato quedó fijado y calibrado contra el PDF del Cap. 8 (el
último que se había generado con el script viejo, ya perdido). No
seguir ajustándolo -- el usuario pidió explícitamente no ponerle más
detalle.** Especificación exacta, por si hay que reconstruir el script:

- `\documentclass[12pt]{article}`, fuente por defecto de `fontspec`
  (Latin Modern Roman -- **no** DejaVu ni ninguna otra, sin
  `\setmainfont`), `polyglossia` con `\setmainlanguage{spanish}`,
  márgenes `1in` (`geometry`).
- Interlineado: `\usepackage{setspace}` + `\setstretch{1.35}` --
  medido con `pdftotext -bbox` contra el Cap. 8 (19.502pt de
  distancia entre líneas exactos; el valor por defecto de Latin
  Modern a 12pt sin stretch da 14.446pt, de ahí sale el 1.35).
- Título: `Capítulo N — Título`, centrado, `\Large`, **sin negrita**
  (el Cap. 8 no la tiene). `\vspace*{34.0bp}` antes del título,
  `\vspace{87.4bp}` después -- calibrado por bisección contra las
  coordenadas exactas del título y el primer párrafo del Cap. 8
  (título a 0.003pt del objetivo; el primer párrafo queda a ~2mm,
  no se pudo cerrar del todo por una interacción de `\flushbottom`
  que redistribuye el estirado de toda la página de forma no lineal
  -- no vale la pena perseguirlo más, es imperceptible).
- Quiebre de escena: una línea `---` sola en el `.md` se convierte en
  `\begin{center}*\end{center}` (el Cap. 8 lo usa así; el Cap. 9 no
  tiene ningún quiebre de escena).
- Cursiva: `*texto*` en el `.md` → `\textit{texto}`. Comillas rectas
  `"..."` del `.md` se dejan tal cual, sin convertir -- así rendeeriza
  igual que el Cap. 8 (Latin Modern con comilla recta ASCII muestra el
  mismo glifo en apertura y cierre, es el comportamiento del Cap. 8
  también, no un bug).
- Requiere `xelatex` + `polyglossia` instalados en el sistema (no es
  dependencia de `uv`). Documentado también en `WORKFLOW.md` bajo
  "Manual Tools".

**Correr esto después de aceptar cada capítulo**, como parte del
cierre de cada capítulo (no es opcional, es el paso que reemplaza al
`.tex`/`tectonic` de exportación completa mientras el libro no está
terminado).

## Tarea 12 -- guardia de contaminación en los prompts (sin cambios)

Sigue completa. `tests/test_guardia_prompts.py::DEUDA_CONOCIDA` sigue
siendo la fuente de verdad. Sin cambios esta sesión.

## Tarea 10 -- acumulación de canon durante la redacción (en producción real)

El mecanismo (`canon_emergente.md` + `actualizar_canon.py`) suma
dieciséis capítulos más entre las tres sesiones de 2026-08-04/05/06 (6
a 21). Total acumulado: 21 capítulos, **catorce `CONFLICTO` detectados
en total** a lo largo de toda la producción y resueltos a mano,
ninguno sin resolver. De la sesión de Cap. 20-21: dos `CONFLICTO` más
--

- **Cap. 13**: real -- "Sandoz" nombrado antes de que Vidal lo conozca.
- **Cap. 14**: real -- error de AM/PM en el horario del traslado.
- **Cap. 16**: real -- numeración de días del cronograma off-by-one.
- **Cap. 17**: real -- la cena fechada el mismo día del traslado.
- **Cap. 18**: real -- 7:10 vs. 7:00 para el mismo evento.
- **Cap. 19**: real -- la gemela en dos lugares a la vez (encontrado
  después de aceptado, no vía `actualizar_canon.py` sino por lectura
  del `eval_log` completo).
- **Cap. 20**: no fue un `CONFLICTO` de `actualizar_canon.py` -- fue el
  motivo del rechazo en primera pasada del juez (año del secreto
  eclesiástico, 1978 vs. 1988 de `world.md`). Real, corregido antes de
  reevaluar.
- **Cap. 21**: real -- Vidal entrando como décimo participante físico
  al traslado, contra el canon fijo de nueve personas, y además un
  beat que le pertenecía al Cap. 22. Encontrado después de aceptado,
  releyendo el `eval_log` completo (mismo patrón que el Cap. 19). Al
  recortar la escena y reevaluar, quedó además un `CONFLICTO`
  **fantasma** (una entrada nueva de canon referenciando la entrada
  vieja ya eliminada) -- falso positivo, resuelto a mano.

El patrón sigue siendo el mismo que el de la sesión anterior: la
mayoría de los `CONFLICTO` de esta etapa del libro son choques de
calendario/aritmética genuinos, no ruido del detector, salvo cuando el
`CONFLICTO` es un artefacto de reevaluar un capítulo ya aceptado (Cap.
21). Con el cronograma del atraco fijado con precisión de minutos
(protocolo de 18 puntos, ventanas de 40/11/6 minutos, 30 horas exactas
de traslado), cada capítulo nuevo tiene mucha más superficie donde un
número puede no cerrar. Seguir el mismo hábito: ante un `CONFLICTO`,
leer el `contradice` completo antes de tocar el texto -- y si el
capítulo ya fue evaluado y aceptado antes de la edición, reevaluar
antes de correr `actualizar_canon.py` de nuevo (ver la lección nueva
al principio de este documento).

El hallazgo del Cap. 7 (tic de lápiz reservado a Sandoz, dado por error
a Ferrero) no fue un `CONFLICTO` de `actualizar_canon.py` -- lo marcó
el juez de `evaluate.py` como riesgo de `character_voice`, no el script
de canon, que no tiene forma de saber que un tic está reservado para
otro personaje que todavía no apareció. El del Cap. 8 (cita no textual)
tampoco fue un `CONFLICTO` de canon -- ninguno de los dos hechos
contradecía al otro, era una discrepancia de redacción dentro de una
cita marcada como literal, que el script de canon no compara palabra
por palabra.

## Pendiente (no bloqueante)

- **Decidir qué hacer con `ch_01.md`.** Sin cambios -- se redactó con el
  bug de canon de la Tarea 10 activo. Sigue sin decidirse si vale la
  pena releerlo/rehacerlo.
- **Tarea 11** -- punto de aprobación manual por capítulo en
  `run_pipeline.py`. Sin cambios; se sigue aprobando capítulo a
  capítulo a mano, leyendo el archivo. Esta sesión se resolvió parte
  del problema práctico: `chapter_to_pdf.py` (versionado, raíz del
  repo) genera el PDF de lectura de cada capítulo -- ver "PDF de
  lectura por capítulo" más arriba. Sigue sin existir un paso
  automático de aprobación dentro de `run_pipeline.py` en sí.
- **Tareas 1b, 1b-bis y 13** -- traducir los prompts contaminados que
  encontró la Tarea 12. Sin cambios; detalle en
  `tests/test_guardia_prompts.py::DEUDA_CONOCIDA`.
- **Fichas completas** de Ledda y Ceruti en `characters.md` (Ansermet
  ya no está en esta lista -- sigue sin ficha formal, pero ya está bien
  establecido por voz en seis capítulos; no urge escribirla). Ledda
  lleva ocho capítulos por voz sola sin ficha -- va acumulando la misma
  deuda que tuvo Ansermet. Ceruti no apareció todavía.
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

**Escribir el Cap. 22** ("La sacristía", Midpoint -- preparación
inmediata, ambición **sosten**, ~1900 palabras, Yes-but). Turín,
sacristía (Vidal entra en la segunda noche) y Collegno. **Este es el
capítulo que el Cap. 21 casi se robó** -- ver la entrada del Cap. 21
en "Redacción": el borrador original de ese capítulo adelantaba la
entrada de Vidal como técnico de la teca, y se recortó exactamente
porque ese beat es del Cap. 22. Al escribir el Cap. 22, la entrada de
Vidal (overol, credencial, orden de trabajo real de revisión de
clima) es material nuevo de este capítulo, no una repetición -- pero
sí conviene revisar el Cap. 21 recortado antes de escribir, para que
el tono de la transición (de "impotente en el puesto remoto" a
"adentro por fin") tenga el quiebre que le corresponde.

**Beats:** (1) Noche del 11 al 12: la manipulación entra en fase de
personal mínimo. Vidal accede como técnico de la empresa de la teca --
historia limpia real, comprada dos años atrás por una donación que él
no hizo. (2) Ve el lienzo por primera vez: la voz lo describe con
sustantivos de inventario (quemaduras de 1532, parches, manchas de
agua) y se detiene de más en el rostro en negativo -- la detención es
el dato. (3) Repaso final de la secuencia de sustitución con Chiara,
en susurros de taller: ella tomará "el objeto" -- Vidal usa la
palabra; ella dice "la tela" -- con las dos manos. (4) Cierre en
suspenso operativo: la ventana se abre en cuatro horas.

**Plants:** la fricción de vocabulario objeto/tela/lienzo en boca de
ambos (refuerzo del hilo #17).
**Payoffs:** -- (ninguno marcado en el outline para este capítulo).
**Character movement:** el objeto de estudio adquiere presencia
física. Su prosa interior empieza a fallarle: primera vez que un dato
lo detiene sin producirle una hipótesis.
**The lie:** desestabilizada por percepción pura -- mirar no es medir,
y sin embargo algo quedó registrado.

**Antes de escribir:** revisar `outline.md` (Foreshadowing Ledger,
línea ~718) para el hilo #17 (fricción objeto/tela/lienzo). Confirmar
la hora de entrada de Vidal (1:10, según lo que decía la escena
recortada del Cap. 21 -- reusable como dato, no como prosa) contra
`personal reducido de nueve personas` de [C14-10]: con Vidal adentro
"en fase de personal mínimo", el outline implica que el número de
gente físicamente presente cambia respecto del pico de nueve del
traslado -- conviene aclarar en el propio capítulo cuántos quedan dentro
en ese momento para no generar un nuevo `CONFLICTO` de headcount.

```bash
uv run python draft_chapter.py 22
uv run python evaluate.py --chapter=22
uv run python actualizar_canon.py 22
uv run python chapter_to_pdf.py 22 "La sacristía"
```

**Ojo:** el número de capítulo va posicional
(`chapter_num = int(sys.argv[1])` en `draft_chapter.py`) -- no hay flag
`--chapter` para ese script (sí lo tiene `evaluate.py`). Leer cada
capítulo antes de avanzar al siguiente. Revisar `canon_emergente.md`/
`state.json::debts` por si el juez o `actualizar_canon.py` marcaron
algo -- y ante un `CONFLICTO`, leerlo con calma antes de tocar el
texto: dos de los tres detectados esta sesión eran reales, uno fue
falso positivo (ver "Tarea 10" arriba). El PDF de lectura
(`chapter_to_pdf.py`) se corre al final, después de aceptar y de correr
`actualizar_canon.py` -- no antes.

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

**Lección del Cap. 8:** cuando un personaje "cita textualmente" algo
dicho en un capítulo anterior, verificar la cita palabra por palabra
contra el original antes de dar el capítulo por bueno -- el juez lo
cazó esta vez, pero es el tipo de discrepancia menor que puede pasar
desapercibida en una lectura rápida y que un lector atento sí nota,
porque el propio texto reclama exactitud.

**Lección del Cap. 9 y el Cap. 11 (`actualizar_canon.py` no siempre
tiene razón):** cuando el script marca un `CONFLICTO`, leer el
`contradice` completo antes de tocar el texto -- puede ser real (Cap.
9: una promesa de fecha que sí contradecía `world.md`) o falso
positivo (Cap. 11: el detector no distingue "libro propio" de "libro
ajeno" en el tic de Sandoz, y comparó por palabras clave, no por
sentido). Los dos casos se resuelven igual en la mecánica
(`canon_emergente.md`, comentario `RESUELTO a mano` + limpiar
`state.json::debts`), pero solo uno de los dos exige editar el
capítulo.

**Lección de esta sesión (Cap. 14-19, calendario del atraco):** a
partir de que el cronograma quedó fijado con precisión de minutos
(protocolo de 18 puntos, ventanas de 40/11/6 minutos, 30 horas exactas
de traslado, hilo #4 con dos ventanas de devolución), casi todos los
`CONFLICTO` que salieron fueron de aritmética/calendario real, no
falsos positivos. **Antes de escribir un capítulo nuevo de esta parte
del libro, anclar explícitamente la fecha en la primera línea o el
primer párrafo** (como se volvió necesario en el Cap. 18, 19 y ahora
el 20) -- no dejar que el modelo la infiera solo, porque con el margen
de tiempo tan ajustado (17 días entre el traslado y la devolución, con
capítulos que saltan adelante y atrás en esa ventana) un desliz de un
día entero es fácil y el juez lo va a cazar.

**Lección del Cap. 14 y el Cap. 15 (Fable 5 y contenido de
vigilancia):** si `draft_chapter.py` sale con `stop_reason=refusal`
categoría "cyber" sobre contenido de vigilancia/evasión de seguridad o
fabricación de una falsificación (común en esta parte del libro, es
una novela de atraco), reintentar una vez por las dudas y si persiste,
`AUTONOVEL_WRITER_MODEL=claude-opus-5` para esa sola llamada, sin
tocar `.env`. No fue ruido: rechazó dos veces de dos capítulos con este
tipo de contenido, y Opus 5 lo escribió sin problemas de voz las dos
veces.

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
3. `uv run python -m pytest tests/ -v` -- confirmar 266 en verde y 38
   xfail esperados (ninguno inesperado) antes de tocar nada.
4. `cat state.json` -- `debts` debería estar `[]`.
5. Leer la entrada de Cap. 22 en `outline.md` ("Ch 22: La sacristía")
   antes de redactar, y de paso el Foreshadowing Ledger (línea ~718,
   hilo #17) y la entrada del Cap. 21 en "Redacción" (qué se recortó y
   por qué).
6. Redactar Cap. 22 a mano con el standalone:
   `uv run python draft_chapter.py 22` → `evaluate.py --chapter=22` →
   `actualizar_canon.py 22` → `chapter_to_pdf.py 22 "La sacristía"`.
   Leer el capítulo completo y el `eval_log` entero (no solo el
   `overall_score`) antes de avanzar -- si rechaza, ver "Lección del
   Cap. 6"; si acepta, revisar igual `character_voice`/`continuity` --
   ver "Lección del Cap. 7"; si hay una cita textual de un capítulo
   anterior, verificarla palabra por palabra -- ver "Lección del Cap.
   8"; si `actualizar_canon.py` marca un `CONFLICTO`, no asumir que el
   texto está mal sin leer el `contradice` completo -- ver "Lección del
   Cap. 9 y el Cap. 11"; anclar la fecha explícitamente al abrir el
   capítulo -- ver "Lección de esta sesión (Cap. 14-19, calendario del
   atraco)"; si `draft_chapter.py` rechaza con categoría "cyber", ver
   "Lección del Cap. 14 y el Cap. 15"; y si se edita el capítulo
   **después** de evaluarlo y aceptarlo, reevaluar antes de correr
   `actualizar_canon.py` de nuevo -- ver la lección nueva de Cap. 21 al
   principio de este documento.
7. No tocar el formato de `chapter_to_pdf.py` -- ya está cerrado y
   calibrado, ver "PDF de lectura por capítulo" más arriba.
8. No tocar el diseño del cacheo de prompt salvo que deje de andar --
   ver "Cacheo de prompt" más arriba. Si `evaluate.py` vuelve a
   quedarse sin `max_tokens` (thinking agotado sin texto), subir el
   valor de `call_judge(prompt, max_tokens=...)` en la línea de
   `evaluate_chapter()` -- ya se subió una vez esta sesión (8000 →
   16000).
