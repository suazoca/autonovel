# TRASPASO — rama `novela2` (worktree de `framework/es-multilibro`)

Estado real al cierre de esta sesión (2026-08-04). Este documento
reemplaza la necesidad de releer `ESTADO.md` completo o el historial de
commits para retomar el trabajo -- es la foto actual, no la bitácora
(para eso está `ESTADO.md`, que sí es narrativo y tiene una sección
nueva para esta rama).

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

Fundación completa y aprobada. **Acto I completo: Cap. 1 a 11
escritos, evaluados y aceptados (11 de 11).** Seis capítulos se
escribieron en una sola sesión (2026-08-04): Cap. 6 a 11, puntajes
7.54 / 7.54 / 7.39 / 7.39 / 7.47 / 7.86, todos sobre umbral, con
cuatro correcciones reales encontradas por el juez o por
`actualizar_canon.py` más allá de la prosa (tic de personaje reusado
en el Cap. 7, cita no textual en el Cap. 8, hueco de calendario en el
Cap. 9, hueco de calendario en el Cap. 11). `state.json::debts` vacío,
sin `CONFLICTO` de canon abiertos. Nuevo: `chapter_to_pdf.py`
versionado, formato cerrado, PDF de lectura entregado para Cap. 9-11.
Listo para **Cap. 12 ("Collegno")**, arranque del Acto II (Fun and
Games) -- ver "Próximo paso".

## Estado del repositorio

| | |
|---|---|
| Directorio | `/root/novela2` (worktree; confirmado con `git worktree list`) |
| Rama | `novela2`, diverge de `framework/es-multilibro` en `7b81700` (Tarea 7) |
| `.env` / `ANTHROPIC_API_KEY` | Presente en este entorno. `AUTONOVEL_WRITER_MODEL=claude-fable-5`, `AUTONOVEL_JUDGE_MODEL=claude-opus-5`, `AUTONOVEL_REVIEW_MODEL=claude-opus-5`, `AUTONOVEL_API_BASE_URL=https://api.anthropic.com` |
| Push | Al día con `origin/novela2` (`git log origin/novela2..HEAD --oneline` vacío). Último commit: el de cierre de esta sesión (Cap. 8 + `docs/`) -- confirmar con `git log -1 --oneline`. |
| Working tree | Limpio -- confirmar con `git status`. |
| Tests | `uv run python -m pytest tests/ -v` -- **248 tests, todos en verde, + 38 xfail esperados** (2 más que a mitad de sesión; no se tocó código de producción, la diferencia es cobertura nueva). No hace falta `.env` (todo mockeado); drafting/evaluar capítulos sí lo necesita. |
| Token de GitHub | Fine-grained, creado 2026-07-27, alcance `suazoca/autonovel`, permiso `Contents: read/write`, **vence ~2026-08-26**. Al vencer, limpiar la credencial guardada con `git credential reject` (protocol=https, host=github.com) antes de autenticar con uno nuevo. Usado sin problemas esta sesión (push directo, sin reingresar credencial). |

## Fundación (completa, aprobada -- sin cambios esta sesión)

| Archivo | Estado |
|---|---|
| `voice.md` | Completo (Parte 1 + Parte 2 generada desde la semilla, commit `61aeee4`) |
| `world.md` | Completo, revisado (último cierre: commit `dde01c4`) |
| `characters.md` | Vidal, Sandoz, Chiara y Ferrero completos. **Ledda, Ansermet y Ceruti siguen "ficha pendiente de generación"** -- sin cambios de archivo esta sesión (commit `6f110dc`), aunque Ansermet ya protagonizó tres capítulos (9, 10, 11) por voz sola, sin ficha formal. Conviene generarle una antes de que aparezca Ledda en Collegno (Cap. 12) para no repetir el mismo hueco con dos personajes a la vez. |
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

## Cap. 5: por qué se reescribió entero (sesión anterior, sin cambios)

Sin novedades esta sesión. Detalle completo en la versión anterior de
este documento / `docs/ESTADO.md`: se reescribió entero porque el
Cap. 46 (Final Image) depende de una primera entrada al edículo que el
borrador original no dramatizaba. `overall_score` final 7.54.

## Bugs de compatibilidad con Fable 5 (sesión anterior, sin cambios)

Sin novedades esta sesión. Detalle completo en versiones anteriores de
este documento / `docs/ESTADO.md`.

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

El mecanismo (`canon_emergente.md` + `actualizar_canon.py`) suma seis
capítulos más esta sesión (6 a 11). Total acumulado: 11 capítulos
(Acto I completo), seis `CONFLICTO` detectados en total a lo largo de
toda la producción y resueltos a mano (Ruti, Zúrich, cronología del
Sepulcro, fundación vs. outline del Cap. 5 -- sesiones anteriores; Cap.
9 y Cap. 11 -- esta sesión), ninguno sin resolver.

De los dos de esta sesión: el del **Cap. 9** era un `CONFLICTO` real
(la restitución prometida "antes" de la inspección del 29, cuando
`world.md` dice que ocurre "durante"). El del **Cap. 11** fue un
**falso positivo** -- el detector cazó "libro anotado a lápiz +
devolución" y lo comparó contra el tic de Sandoz sin poder distinguir
que la regla habla de libros ajenos y este es propio del personaje.
Ambos exigieron lectura humana del `contradice` para decidir si el
texto estaba mal o el detector estaba disparando en falso; el mecanismo
por sí solo no alcanza para esa distinción, hay que seguir revisando
cada `CONFLICTO` a mano en vez de asumir que todos son errores reales.

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

**Escribir el Cap. 12** ("Collegno", Fun and Games -- apertura del
mundo nuevo, ambición "sostén", ~2100 palabras, Yes-but). **Es el
primer capítulo del Acto II** (el Acto I cerró con el Cap. 11).
Laboratorio de Collegno + piso franco en Turín. Doble sorpresa: la
calidad del laboratorio y la identidad del tercer integrante del
equipo. Beats: (1) el laboratorio de Collegno supera lo que ninguna
universidad le dio nunca -- instrumental de 2033, aislamiento,
atmósfera controlada; Vidal audita cada equipo, todo pasa. (2)
presentaciones: **Chiara Fabbri**, conservadora textil formada en el
Opificio (coincide con el perfil sin nombre que Ansermet le mostró en
el Cap. 11), discípula de una conservadora de la intervención de 2002
-- toma el escáner de Vidal con las dos manos, aunque es una máquina.
**Ledda**, seguridad -- habla en procedimientos y plazos, sin
pronombres. (3) el tercero entra y es **Ferrero** -- Vidal cuenta los
segundos de silencio. Ferrero: "Usted necesita mis ojos. Yo necesito
que esto no se haga sin alguien que sepa lo que puede romper." Ninguno
de los dos menciona la denegación del Cap. 8. (4) primera reunión de
protocolo: Ferrero exige custodia compartida de toda muestra; Ledda
fija la regla de oro -- "Una identidad falsa no resiste 2033. Una
verdadera con motivos ocultos, sí" (hilo #19 del Foreshadowing Ledger,
planteado en presencia de Chiara, sin que nadie note que la describe a
ella).

**Plants:** la frase de Ledda sobre identidades verdaderas con motivos
ocultos (hilo #19 -- planta acá, refuerza en 21 y 37, paga en 37-38 y
40 cuando Ledda confirma con nombre: Chiara). El tic de Chiara de
tomar las cosas con las dos manos.
**Payoffs:** el reencuentro con Ferrero paga la reunión del Cap. 7.
**Character movement:** Vidal descubre que no controla la composición
de su propio equipo y lo acepta -- segunda concesión, más barata que la
primera, y eso es lo grave.
**The lie:** operativa -- audita máquinas, no personas. El capítulo
muestra el punto ciego con precisión de plano.

**Antes de escribir:** revisar `outline.md` (Foreshadowing Ledger,
línea ~718) si algún gesto que se le ocurra dar a Ledda o reforzar en
Chiara ya está reservado a otro hilo -- mismo chequeo que se volvió
hábito desde la lección del Cap. 7. Ansermet no aparece en este
capítulo (Vidal no lo vuelve a ver hasta más adelante en el libro).

```bash
uv run python draft_chapter.py 12
uv run python evaluate.py --chapter=12
uv run python actualizar_canon.py 12
uv run python chapter_to_pdf.py 12 "Collegno"
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
3. `uv run python -m pytest tests/ -v` -- confirmar 248 en verde y 38
   xfail esperados (ninguno inesperado) antes de tocar nada.
4. `cat state.json` -- `debts` debería estar `[]`.
5. Leer la entrada de Cap. 12 en `outline.md` (línea ~233, "Ch 12:
   Collegno") antes de redactar, y de paso el Foreshadowing Ledger
   (línea ~718, hilo #19) para Ledda y Chiara.
6. Redactar Cap. 12 a mano con el standalone:
   `uv run python draft_chapter.py 12` → `evaluate.py --chapter=12` →
   `actualizar_canon.py 12` → `chapter_to_pdf.py 12 "Collegno"`. Leer
   el capítulo completo y el `eval_log` entero (no solo el
   `overall_score`) antes de avanzar -- si rechaza, ver "Lección del
   Cap. 6"; si acepta, revisar igual `character_voice`/`continuity` --
   ver "Lección del Cap. 7"; si hay una cita textual de un capítulo
   anterior, verificarla palabra por palabra -- ver "Lección del Cap.
   8"; y si `actualizar_canon.py` marca un `CONFLICTO`, no asumir que
   el texto está mal sin leer el `contradice` completo -- ver "Lección
   del Cap. 9 y el Cap. 11".
7. No tocar el formato de `chapter_to_pdf.py` -- ya está cerrado y
   calibrado, ver "PDF de lectura por capítulo" más arriba.
