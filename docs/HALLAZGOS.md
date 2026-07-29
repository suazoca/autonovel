# HALLAZGOS

Cosas encontradas rotas o cuestionables que no estaban en el alcance de la
tarea en curso, o que se decidió no corregir todavía.

---

## `dividir_oraciones()` — el filtro de ≤2 palabras sesga el CV hacia arriba

**Dónde:** `deteccion_es.py`, función `dividir_oraciones()`, línea
`if len(limpia.split()) > 2: oraciones.append(limpia)`.

**Qué hace:** cualquier oración de una o dos palabras ("¿Viniste?", "Sí.",
"No.", "Basta.") se descarta silenciosamente y nunca llega a la lista de
oraciones devuelta. Esto es diseño intencional (documentado y confirmado
con el usuario, no un bug), pero tiene un efecto secundario real:

**Por qué importa:** `cv_longitud_oracion()` calcula el coeficiente de
variación de longitud de oración a partir de esa lista. Las oraciones muy
cortas son precisamente el recurso que más varianza aporta -- una prosa
humana alterna oraciones largas con golpes cortos deliberados. Al
descartarlas, el cálculo de CV queda hecho solo sobre las oraciones medias
y largas, lo que **sesga el CV hacia arriba respecto de lo que realmente
haría un capítulo con muchas frases cortas de impacto** (falsamente
sugiriendo más variación real de la que el texto tiene, o subestimando el
uso de frases cortas como marcador de humanidad en la prosa).

**Estado:** NO corregido a pedido explícito ("no lo cambies todavía").
Queda anotado acá para cuando se revise la calibración del CV en Tarea 1c
o posterior. Si se decide corregir, la opción más simple es contar las
oraciones cortas para el CV pero no exigirles longitud mínima para el
propósito de "oración humana", separando el filtro de longitud del cálculo
de variación.

---

## `CALIBRACION["umbral_cv_oracion"]` (0.32) no discrimina en la práctica

**Dónde:** `deteccion_es.py`, `CALIBRACION["umbral_cv_oracion"]`, usado en
`evaluate.py::slop_score()` como corte para penalizar oraciones demasiado
uniformes (`if sentence_length_cv < CALIBRACION["umbral_cv_oracion"]:
penalty += 1.0`).

**Qué se observó:** al medir `sentence_length_cv` de los dos fixtures de
Tarea 0/1c (docs/BASELINE.md, tabla "DESPUÉS"):

| Capítulo | `sentence_length_cv` |
|---|---|
| `cap_dialogado_es.md` (limpio) | 0.686 |
| `cap_con_slop_es.md` (sembrado, con oraciones repetitivas a propósito) | 0.591 |

Ambos quedan muy por encima de 0.32 -- ni siquiera el capítulo sembrado,
que tiene varias oraciones de estructura parecida, se acerca al umbral. Con
una muestra de 2 fixtures no se puede concluir que el umbral esté mal, pero
sí que **no se probó contra prosa española real** antes de fijarlo: el
valor 0.32 en `CALIBRACION` es una estimación del autor de `deteccion_es.py`
(documentada como tal: "sube a 0,32" en `AUDITORIA_Y_PLAN.md`, sin corpus
de referencia citado).

**Estado:** NO corregido a pedido explícito ("no lo cambies ahora"). Antes
de tocar el número hace falta un corpus más grande de prosa española real
(idealmente capítulos ya evaluados por el juez LLM como buenos vs. flojos)
para calibrar el umbral con datos, no con una estimación a ojo.

---

## `gen_outline.py` contaminado con *Bells* -- promovido a Tarea 2b

Encontrado durante la Tarea 3: `gen_outline.py` tiene todo el prompt
hardcodeado a *The Second Son of the House of Bells* (POV fijado a Cass,
"Cass's lie", Perin/Maret/Torvald/Lenne, "Tonal Law", "the Bellwrights",
"the harmonic"). Se me había pasado en la auditoría original
(`AUDITORIA_Y_PLAN.md` Clase A no lo lista ni como contaminado ni como
limpio) y en la Tarea 2 (solo nombraba `draft_chapter.py`/`gen_brief.py`).

El usuario confirmó que esto NO es un hallazgo aparte sino Tarea 2
incompleta, y lo agregó como **Tarea 2b** en `ENCARGO_CLAUDE_CODE.md`
(mismo tratamiento que A1: armazón invariante + reglas leídas de
`mundo.md`/`personajes.md`/`MISTERIO.md`, grep de aceptación en cero),
programada para después de la Tarea 4. Ver ese archivo para el detalle;
esta entrada queda solo como puntero.

---

## RESUELTO: objetivo de palabras por capítulo

Lo que en la sesión anterior se registró acá como "discrepancia sin
resolver" (3800 en `deteccion_es.py` vs. 2000 en `ENCARGO_CLAUDE_CODE.md`)
era un error del propio `deteccion_es.py`, no una ambigüedad real. El
usuario lo confirmó: **2000 es el valor correcto**. La novela pasó de
~22 capítulos de 3200-3800 palabras a ~45 capítulos de 2000 palabras --
mismo largo total (~90-92k), pero más puntos de parada (abandonar un
libro hoy cuesta cero, y un capítulo de 4000 palabras es una barrera para
retomar). El 3800 era un número transitorio de cuando la novela tenía 22
capítulos, que quedó mal actualizado.

**Corregido** en `deteccion_es.py` (`CALIBRACION["palabras_objetivo_capitulo"]
= 2000`, con la nota de por qué). `draft_chapter.py` no necesitó cambios:
ya leía el valor de `CALIBRACION` dinámicamente en vez de hardcodear
ninguno de los dos números.

---

## Tarea 4: los validadores de siembra no están conectados a un parser real

**Dónde:** `evaluate.py`, `validar_siembra()` / `validar_libro_de_siembras()`.

**Qué falta:** las funciones validan entradas ya estructuradas (dicts con
`id`/`siembra`/`pago`/`alcance`/`estado`, el esquema exacto del encargo),
y están completamente probadas contra los 4 casos de la tabla + la
regresión. Pero **no hay todavía un parser** que extraiga esas entradas
desde la tabla real del "Foreshadowing Ledger" en `outline.md`/`esquema.md`
(que sigue siendo texto libre generado por un LLM, ahora con una columna
"Alcance" agregada a la plantilla). Sin ese parser, `evaluar_foundation()`
no puede llamar a estos validadores contra un esquema real todavía.

**Por qué no se hizo ahora:** construir un parser confiable de una tabla
markdown generada por LLM (formato variable) es un problema aparte, con
riesgo real de bugs silenciosos si el formato no coincide exactamente con
lo esperado. Los 5 tests de aceptación de la Tarea 4 (los 4 casos + la
regresión) no lo exigían -- pedían la lógica de validación, no el parser.
Mismo criterio que se usó en la Tarea 1d (fixtures de voz/mundo creados
pero no conectados a una corrida real de `evaluate_chapter()`).

**Estado:** pendiente. Cuando se construya, probablemente conviene
escribirlo con el mismo estilo que `extraer_ambicion()` (regex tolerante,
degrada con gracia si faltan columnas) y agregar sus propios tests con
tablas reales generadas por `gen_outline_part2.py`.

---

## `gen_outline_part2.py` también está contaminado con *Bells* (más que `gen_outline.py`)

**Dónde:** `gen_outline_part2.py`, todo el prompt: capítulos 17-24
escritos a mano para la trama específica de Bells (Maret, "the void", "the
Bell Tower", el clímax de Cass), y además **un bug real** independiente de
la contaminación -- `part1 = open('/tmp/outline_output.md').read()` es una
ruta absoluta hardcodeada fuera del repo, que no existe en este entorno
(el script rompe si se lo corre tal cual).

**Qué se hizo en la Tarea 4:** edición mínima -- se agregó la columna
"Alcance" a la tabla del Foreshadowing Ledger que el prompt le pide al
modelo, sin tocar el resto.

**Estado:** confirmado por el usuario -- sumado al alcance de la Tarea 2b
en `ENCARGO_CLAUDE_CODE.md` (mismo grep de aceptación, más la corrección
de la ruta hardcodeada). Esta entrada queda como puntero; ver ese archivo
para el detalle. Pendiente de ejecutar.

---

## `libros_completos` en `validar_siembra()` no tiene de dónde salir todavía

**Dónde:** `evaluate.py`, parámetro `libros_completos` de `validar_siembra()`
/ `validar_libro_de_siembras()` (regla 4 de la Tarea 4: alcance "serie" con
pago asignado a un libro ya publicado → error).

**Qué falta:** hoy nadie llena ese parámetro -- por diseño, ningún llamador
real lo provee todavía, así que la regla 4 solo se ejerció en los tests
(pasando el set a mano). Según `AUDITORIA_Y_PLAN.md` sección B2/B7, esa
información vive en `estado_serie.json`, con la forma
`{"libros_completos": [1], "libro_actual": 2, ...}` -- pero ese archivo es
parte de la Clase B (la capa de serie completa: `serie.md`,
`arco_serie.md`, `canon_serie.md`, `personajes_serie.md`, `estado_serie.json`,
etc.), que todavía no existe en este repositorio. Ninguna tarea del
encargo actual (0-4) crea `estado_serie.json`.

**Estado:** dependencia documentada, no bloqueante. `validar_siembra()`
funciona hoy con `libros_completos=None` (equivalente a "no hay libros
publicados todavía", razonable como default mientras la Clase B no
exista). Cuando se implemente `estado_serie.json`, el único cambio
necesario es que quien llame a `validar_libro_de_siembras()` le pase
`set(estado_serie["libros_completos"])` -- la función ya está lista para
recibirlo, no hace falta tocar la lógica de validación.

---

## Bug sistémico: los `gen_*.py` de fundación no guardaban su propio resultado

**Dónde:** encontrado al arreglar el `/tmp/outline_output.md` de
`gen_outline_part2.py` en la Tarea 2b. Resulta que **todos** los scripts
de la fase de fundación tenían el mismo patrón: `gen_world.py`,
`gen_characters.py`, `gen_canon.py` (y `gen_outline.py`/
`gen_outline_part2.py`, ya corregidos) terminan con `print(result)` y
nunca escriben en su archivo destino (`world.md`, `characters.md`,
`canon.md`). Y `run_pipeline.py::run_foundation()` tampoco lo hace por
ellos -- llama `uv_run("gen_world.py")` etc., que captura el stdout en un
`CompletedProcess`, pero nunca lo vuelca a ningún archivo.

**Por qué importa:** tal como está, correr `run_pipeline.py --phase
foundation` de punta a punta **no dejaría nada escrito** en `world.md`,
`characters.md` ni `canon.md` -- el pipeline automatizado que describe
`PIPELINE.md` no puede funcionar hoy sin intervención manual (correr cada
script y redirigir su stdout a mano, que es exactamente el flujo que
`/tmp/outline_output.md` delataba).

**Qué se corrigió:** solo `gen_outline.py` y `gen_outline_part2.py`
(Tarea 2b) -- ahora escriben en `esquema.md`/`outline.md` ellos mismos.
`gen_world.py`, `gen_characters.py` y `gen_canon.py` **siguen sin
guardar**.

**Estado:** confirmado por el usuario como **prioridad alta** -- formalizado
como **Tarea 6** en `ENCARGO_CLAUDE_CODE.md` (`gen_world.py` →
`mundo.md`/`world.md`, `gen_characters.py` → `personajes.md`/`characters.md`,
`gen_canon.py` agrega a `canon.md` en vez de reemplazarlo). Esta entrada
queda como puntero; ver ese archivo para el detalle. Pendiente de ejecutar.

Nota aparte: en `docs/BASELINE.md` y `docs/ESTADO.md` había quedado
registrado que `world.md`/`characters.md` estaban vacíos "porque son
plantillas" -- cierto pero incompleto. Están vacíos porque **el pipeline
nunca pudo escribirlos**, ni siquiera con `.env` configurado. Corregido en
los dos archivos.

**Estado de la Tarea 6, actualizado:** implementada en un commit propio.
`gen_world.py`, `gen_characters.py` y `gen_canon.py` ya se guardan a sí
mismos (mismo patrón que `gen_outline.py`/`gen_outline_part2.py` de la
Tarea 2b), con las cuatro funciones compartidas movidas a
`fundacion_comun.py` en vez de duplicadas en cinco archivos.
`run_pipeline.py::run_foundation()` aborta si un generador falla (antes
ignoraba el returncode) y verifica que los archivos de fundación existen
y no están vacíos antes de gastar una llamada al juez LLM evaluándolos.

---

## RESUELTO: `gen_world.py`/`gen_characters.py`/`gen_canon.py` contaminados con *Bells*

**Lo que decía esta entrada:** los tres prompts tenían contenido de *The
Second Son of the House of Bells* escrito a mano -- `gen_world.py` pedía
"Cantamura", "Tonal Law", "Cass's Gift"; `gen_characters.py` exigía el
reparto entero por nombre (Cass Bellwright, Eddan, Perin, Maret Corda,
Rector Suvaine, Torvald Hess) más "1-2 personajes adicionales";
`gen_canon.py` mencionaba "the Perin contract, the Expansion Wars" como
ejemplos.

**Corregido** como Tarea 2c (mismo tratamiento que A1/Tarea 2b): armazón
invariante + contenido derivado de `semilla.txt`/`mundo.md`/`personajes.md`.
El reparto fijo de `gen_characters.py` se reemplazó por un requisito
estructural (mínimo protagonista + antagonismo del conflicto central, más
secundarios según la semilla; el número de personajes con profundidad
completa se deriva de `CALIBRACION` en vez de estar hardcodeado). Los
títulos de sección de `gen_world.py` pasaron a ser genéricos ("Reglas
excepcionales del mundo" en vez de "Magic System / Hard Rules (Tonal
Law)"). Los tres además exigían "fantasy novel" y un sistema de magia
obligatorio -- ahora el género sale de la semilla, y el sistema de magia
es condicional ("si aplica"). Los tres prompts se tradujeron al español,
mismo motivo que la Tarea 2: pedir en inglés que el modelo escriba en
español induce los calcos que `deteccion_es.py` caza.

**Aceptación verificada:** `grep -in "cass|bellwright|perin|corda|
suvaine|torvald|cantamura|tonal law|expansion wars" gen_world.py
gen_characters.py gen_canon.py` → cero resultados. Test dedicado
(`tests/test_descontaminacion_2c.py`) para que esos términos no puedan
volver a entrar sin que el suite lo note.

---

## `gen_world.py` cargaba `craft` (CRAFT.md) pero nunca lo usaba en el prompt

**Encontrado al reescribir el prompt para la Tarea 2c, no corregido --
fuera de alcance de esa tarea.** `gen_world.py::main()` carga
`CRAFT.md` y lo pasa a `build_prompt(seed, voice_part2, craft)` como
tercer parámetro, pero el f-string de `build_prompt()` nunca interpola
`{craft}` en ningún lado -- el contenido real de `CRAFT.md` se descarta,
reemplazado por un resumen escrito a mano dentro del prompt. Bug
preexistente, no introducido por la Tarea 2c (ya estaba así antes de
tocar el archivo).

`gen_characters.py` tiene una variante del mismo problema, más completa:
ni siquiera carga `CRAFT.md` -- `main()` no lo lee, `build_prompt()` no
lo recibe como parámetro. Los frameworks de personaje (sliders,
wound/want/need/lie, las 8 dimensiones de diálogo) están escritos a mano
dentro del prompt en vez de derivarse del archivo.

**Por qué no se corrige ahora:** no estaba en el pedido de la Tarea 2c
(descontaminación de Bells, no arquitectura de cómo se usa CRAFT.md).
Arreglarlo bien implica decidir si el resumen manual actual es preferible
a interpolar `CRAFT.md` completo (que es mucho más largo y genérico,
cubre las tres capas del framework -- plot, character, world, prose --
no solo lo relevante a cada script), lo cual es una decisión de diseño,
no un fix mecánico.

**Estado:** NO corregido, sin tarea asignada.

---

## No hay mecanismo que devuelva al canon los hechos establecidos durante la redacción

**Dónde:** `gen_canon.py` (fundación) + el flujo de redacción en general.
`gen_canon.py` reescribe `canon.md` entero a partir de
`semilla.txt`/`mundo.md`/`personajes.md` -- eso está bien para la fase de
fundación (ver la corrección de la Tarea 6 arriba: canon ahí es derivado,
no tiene hechos propios).

**El hallazgo real:** una vez que empieza la redacción, los capítulos van
a establecer hechos que **no** están en `mundo.md` ni en `personajes.md`
-- un nombre de calle mencionado al pasar en el Ch 3, la edad exacta de un
personaje secundario revelada en el Ch 7, un objeto que resulta
importante en el Ch 12. `PIPELINE.md` (Fase 2, paso 5) da por sentado que
esto pasa ("Extract new canon entries from eval output → append to
canon.md"), pero **no existe ningún script que lo haga**. `evaluate.py`
ya devuelve `new_canon_entries` en el JSON de `evaluate_chapter()` (se
puede confirmar leyendo el prompt), pero nada lee ese campo y lo escribe
en ningún lado.

**Por qué es distinto del hallazgo de arriba:** esto no es "gen_canon.py
mal diseñado" -- es una **fase distinta** (redacción, no fundación), que
necesita un script propio (algo como `actualizar_canon.py`, corriendo
después de cada capítulo aceptado) que sí sea acumulativo, a diferencia
de `gen_canon.py`.

**Por qué no se corrige ahora:** depende de fijar primero el formato
definitivo de `canon.md` como estructura parseable (hoy es prosa/bullets
libres generados por LLM) -- el mismo problema de fondo que bloquea el
hallazgo de los validadores de siembra más arriba (`libros_completos` /
parser del Foreshadowing Ledger). Los dos esperan la misma decisión de
diseño: qué tan estructurado tiene que ser un documento que hoy es texto
libre para que un script pueda leerlo y escribirle de vuelta con
confianza.

**Estado:** NO corregido, sin tarea formal asignada todavía.

---

## RESUELTO: nada generaba la Parte 2 de `voice.md`/`voz.md`

**Corregido como Tarea 7** (`gen_voice.py`, mismo patrón que el resto de
la Tarea 6). Lo que decía esta entrada, para referencia:

**Confirmado con grep, no requiere `.env` para diagnosticarse:**

- No existe `gen_voice.py` (ni ningún script equivalente) en el repo.
- `run_pipeline.py::run_foundation()` no tiene ningún paso que llene
  `voice.md`/`voz.md` -- solo `gen_world.py`, `gen_characters.py`,
  `gen_outline.py`, `gen_outline_part2.py`, `gen_canon.py` y
  `voice_fingerprint.py`.
- `voice_fingerprint.py` (el único script relacionado con "voice" en el
  loop) **no escribe en `voice.md`**: escribe
  `edit_logs/voice_fingerprint.json`, y `edit_logs/` está en
  `.gitignore`. Es un medidor de patrones sobre capítulos YA escritos
  (frecuencia de diálogo, longitud de oración, etc.), no un generador de
  identidad de voz. No hay ningún `write_text` en todo el repo que
  apunte a `voice.md`/`voz.md`.
- `PIPELINE.md` (Fase 1, paso 5) documenta este paso como si existiera:
  *"Voice discovery: write 5 trial passages in different registers,
  select best, fill voice.md Part 2 with exemplars + anti-exemplars"* --
  pero no hay ningún script que lo implemente.

**Por qué importa:** `draft_chapter.py`, `gen_brief.py` y `gen_outline.py`
leen `voice.md`/`voz.md` Parte 2 esperando tono, registro léxico y
pasajes ejemplares reales. Hoy esa sección es pura plantilla (comentarios
HTML sin contenido -- confirmado, no son hechos inventados). El pipeline
redactaría con identidad de voz vacía, y `voice_fingerprint.py` mediría
los capítulos resultantes contra un documento en blanco, sin nada contra
qué comparar.

**Por qué es hermano de la Tarea 6, no la misma tarea:** la Tarea 6 fue
sobre scripts que generan algo pero no lo guardan. Este hallazgo es sobre
un paso del pipeline que **no existe en absoluto** -- no hay nada que
arreglarle a un script porque el script nunca se escribió.

**Restricción de orden, no obvia:** `gen_world.py` **lee** la Parte 2 de
`voice.md` como insumo (vía `extraer_voz_parte2()`, para que el mundo se
construya en el tono correcto). Eso significa que un futuro `gen_voice.py`
tendría que correr **primero** en `run_foundation()`, antes que
`gen_world.py` -- y solo puede depender de la semilla (`seed.txt`/
`semilla.txt`), porque leer `mundo.md`/`personajes.md` para generar la
voz crearía una dependencia circular con `gen_world.py`/`gen_characters.py`,
que a su vez leen la voz. El orden actual del loop es
`gen_world.py -> gen_characters.py -> gen_outline.py ->
gen_outline_part2.py -> gen_canon.py -> voice_fingerprint.py`
(confirmado en `run_pipeline.py::run_foundation()`); la voz entraría
antes que todo eso.

**Pregunta de diseño que estaba abierta, ya resuelta:** ¿la voz se genera
una sola vez y se congela desde la iteración 1 de fundación, o se
regenera en cada iteración? **Decisión: se genera una sola vez.**
`gen_voice.py` es idempotente -- si la Parte 2 ya tiene contenido real, no
llama a la API, informa que ya existe y sale. Motivo: la voz solo puede
depender de la semilla (no de `mundo.md`/`personajes.md`, por la
restricción de orden de arriba), y la semilla no cambia entre
iteraciones -- regenerarla sería ruido, no exploración. Coherente con la
regla de `AUDITORIA_Y_PLAN.md` B4 (la voz no se redescubre entre libros
de una serie).

**Estado:** RESUELTO. `gen_voice.py` corre PRIMERO en
`run_pipeline.py::run_foundation()`, antes de `gen_world.py`, solo con
la semilla y `CRAFT.md` como insumos. Llena 7 de las 8 subsecciones de la
Parte 2 (Tono, Ritmo de oración, Registro léxico, POV y tiempo,
Convenciones de diálogo, Pasajes ejemplares, Anti-ejemplares) sin tocar
la Parte 1 ni la subsección opcional "Reglas específicas de capítulo"
(que se llena más tarde, por capítulo, no en el descubrimiento de voz).

**Ajuste necesario en `verificar_archivos_fundacion()`:** como la voz se
congela, su `mtime` queda viejo a propósito desde la iteración 2 en
adelante -- el criterio de mtime que sí aplica a
mundo/personajes/esquema/canon (Tarea 6) le haría creer, en toda
iteración después de la primera, que nadie escribió la voz esta vuelta, y
abortaría el pipeline sin motivo real. `voz.md`/`voice.md` se verifica
aparte, solo por contenido (`fundacion_comun.voz_parte2_tiene_contenido()`),
sin importar su mtime.

**Simplificación consciente respecto a `PIPELINE.md`:** el paso documentado
ahí ("write 5 trial passages ... select best ...") es un proceso de
explorar-evaluar-elegir en varios pasos. `gen_voice.py` hace una sola
llamada al modelo (mismo patrón de una llamada que los otros seis
generadores), pidiéndole en el prompt que considere internamente varias
direcciones antes de comprometerse a una sola voz coherente -- no
literalmente 5 pasajes generados y comparados por separado. Si en algún
momento se quiere el proceso completo de exploración, es un cambio de
arquitectura (multi-llamada), no algo que quepa en "mismo método de
siempre".

---

## `voz_parte2_tiene_contenido()` verifica la Parte 2 como un todo, no subsección por subsección

**Dónde:** `fundacion_comun.py::voz_parte2_tiene_contenido()`, usada como
guardia de idempotencia en `gen_voice.py::main()` y como criterio de
"voz completa" en `run_pipeline.py::verificar_archivos_fundacion()`.

**Qué falta:** la función mira si HAY contenido real en algún lugar de la
Parte 2 (le basta con que sobreviva algo después de sacar comentarios HTML
y encabezados), pero `gen_voice.py::llenar_parte2()` escribe subsección
por subsección (Tono, Ritmo de oración, Registro léxico, POV y tiempo,
Convenciones de diálogo, Pasajes ejemplares, Anti-ejemplares), usando el
parseo por rangos que ya existe en `_rango_subseccion()`.

**Por qué importa:** si una corrida real llena algunas de las 7
subsecciones y se corta a mitad de camino (respuesta del modelo truncada,
faltan algunos de los marcadores `###...###` esperados), `parsear_secciones()`
devuelve un dict parcial, `llenar_parte2()` llena solo lo que recibió, pero
`voz_parte2_tiene_contenido()` ya encuentra contenido real en las
subsecciones que sí se llenaron y devuelve `True`. Consecuencia doble:

1. `gen_voice.py::main()`, en la siguiente corrida, ve que "ya tiene
   contenido" y sale sin volver a llamar a la API -- las subsecciones que
   quedaron en placeholder (`<!-- Generated during foundation. -->`) se
   quedan así **para siempre**, no hay ningún mecanismo que las complete.
2. `run_pipeline.py::verificar_archivos_fundacion()` usa el mismo criterio
   para decidir si la voz está lista antes de gastar la llamada al juez
   LLM -- también da la voz por buena, aunque le falten subsecciones
   enteras.

**Arreglo propuesto (no implementado):** que la guardia mire subsección
por subsección en vez de la Parte 2 como bloque único, apoyándose en el
mismo parseo por rangos que `llenar_parte2()` ya usa (`_rango_subseccion()`
por cada entrada de `SECCIONES`) -- solo dar la voz por completa si las 7
subsecciones obligatorias tienen contenido real, no solo alguna.

**Estado:** NO corregido, anotado como hallazgo abierto a pedido explícito.

---

## RESUELTO: cuatro incompatibilidades con Fable 5 encontradas en la primera corrida real

La primera corrida real contra la API (Fable 5 como escritor, Opus 5 como
juez, tras configurar `.env` en la rama `novela2`) reveló cuatro problemas
que ningún test podía haber atrapado -- todos los tests de este repo
mockean `call_writer()`/`httpx`, así que nunca ejercitan la forma real de
un payload o de una respuesta de Fable 5. Se documentan acá los cuatro
juntos porque los tres primeros solo existían, hasta ahora, en el mensaje
de dos commits (`c8f7b99`, `7b66805`) -- sin esta entrada, nadie iba a
saber por qué el payload no lleva `temperature` o por qué el texto se
busca por tipo de bloque en vez de por índice fijo.

### 1. `temperature` deprecado en Fable 5 -- devolvía 400

**Qué pasaba:** los 19 scripts mandaban `"temperature": <algo>` en el
payload de `/v1/messages` (heredado de cuando el escritor era Sonnet).
Fable 5 rechaza ese parámetro con `400 Bad Request` -- la llamada nunca
llegaba a generar nada.

**Corregido en** `c8f7b99` ("fix: elimina temperature del payload
(deprecado en Fable 5)") -- se sacó la clave `temperature` del payload en
los 19 scripts. Con la Tarea 8 (`api_comun.py`, este commit), el payload
de `llamar_api()` directamente nunca tuvo esa clave -- no hay forma de
reintroducir el bug por accidente en un script nuevo que use el módulo
compartido.

### 2. Bloques `['thinking', 'text']` rompían `content[0]["text"]`

**Qué pasaba:** los 19 scripts leían el texto de la respuesta como
`resp.json()["content"][0]["text"]` -- asumiendo que el primer bloque del
array `content` es siempre el de texto. Fable 5, con razonamiento
adaptativo, antepone un bloque `{"type": "thinking", ...}` (sin clave
`"text"`) antes del bloque de texto real. `content[0]["text"]` explotaba
con `KeyError: 'text'` en cada llamada.

**Corregido en** `7b66805` ("fix: compatibilidad con Fable 5 (temperature
deprecado, bloque thinking en la respuesta)") -- se cambió a
`next(b["text"] for b in resp.json()["content"] if b.get("type") ==
"text")` en los 19 scripts: busca el bloque por tipo, no por posición.
Con la Tarea 8, `api_comun.py::llamar_api()` hace lo mismo pero sobre
deltas de streaming (`content_block_start`/`content_block_delta`
indexados), ignorando explícitamente los deltas de bloques `thinking` --
ver su docstring.

### 3. Prosa de plantilla fuera de comentario HTML en `voice.md` -- `gen_voice.py` nunca generaba, en silencio

**Qué pasaba:** la Parte 2 de `voice.md` empezaba con tres líneas de
prosa explicativa ("Everything below is discovered during the foundation
phase. The agent proposes a voice that serves THIS story...") que **no**
estaban envueltas en un comentario HTML, a diferencia del resto de la
plantilla (cada subsección sí tenía su placeholder en `<!-- ... -->`).
`fundacion_comun.voz_parte2_tiene_contenido()` saca los comentarios HTML y
los encabezados de la Parte 2 y devuelve `True` si sobrevive algo -- esas
tres líneas de prosa sobrevivían al filtro, así que la función siempre
devolvía `True`, incluso en un `voice.md` recién creado desde la
plantilla, sin una sola subsección real generada. `gen_voice.py::main()`
interpretaba eso como "la voz ya está decidida" y salía sin llamar a la
API -- **sin ningún mensaje de error**, porque desde su lógica no era un
error: es exactamente el comportamiento correcto para el caso real de
idempotencia (no regenerar una voz ya elegida). El bug era indistinguible
de un funcionamiento normal hasta que alguien miraba `voice.md` a mano y
notaba que las 7 subsecciones seguían siendo placeholder.

**Corregido en** `7b66805` -- esas tres líneas de prosa se envolvieron en
`<!-- ... -->`, igual que el resto de la plantilla. No hubo cambio de
código en `gen_voice.py`/`fundacion_comun.py`: el bug estaba en el
contenido de `voice.md`, no en la lógica de detección.

**Por qué importa más allá de esta corrida:** `voz_parte2_tiene_contenido()`
confía en que *toda* la plantilla siga la misma convención (todo lo que no
sea contenido generado va en comentario HTML). Si en el futuro se edita
`voice.md`/`voz.md` a mano y se agrega texto explicativo fuera de un
comentario, el mismo silencio se repite. Ver también el hallazgo de
arriba ("`voz_parte2_tiene_contenido()` verifica la Parte 2 como un todo,
no subsección por subsección") -- son la misma función, dos maneras
distintas de que un falso positivo pase desapercibido.

### 4. Timeout sin streaming perdía respuestas ya generadas y cobradas

**Qué pasaba:** `call_writer()`/`call_judge()`/equivalentes hacían un
`httpx.post()` bloqueante con un timeout fijo por script (120-600s según
la llamada). Con razonamiento adaptativo y `max_tokens` alto, Fable 5
podía tardar más que ese timeout en terminar de generar -- la respuesta
se generaba igual (y se cobraba igual), pero si el timeout saltaba antes
de que `httpx` terminara de recibirla completa, la excepción cortaba la
llamada sin devolver nada. Pasó en la práctica: cuatro llamadas pagadas
sin ningún archivo generado.

**Corregido en la Tarea 8** (`api_comun.py`, este commit) -- los 19
scripts pasaron a usar `llamar_api()`, que llama a `/v1/messages` en modo
streaming (`"stream": True`) y acumula los deltas de texto a medida que
llegan. El timeout pasó a significar "silencio entre eventos SSE", no
"duración total del pedido" -- unificado en 120s para los 19 (antes
variaba 120-600s). Ver el docstring de `llamar_api()` en `api_comun.py`
para el detalle de por qué el número más chico es, en este caso, más
estricto y no más laxo.

**Estado:** las cuatro RESUELTAS. Los tres primeros fixes viven en
`c8f7b99`/`7b66805` (ya en el historial de `novela2` antes de esta
sesión); el cuarto es `api_comun.py` + el rewiring de los 19 scripts
(Tarea 8, este commit).

---

## Pendiente de validar contra la API real: continuación automática por prefill (Tarea 9)

**Dónde:** `api_comun.py::llamar_api()`. Corrige el hallazgo de que
`gen_outline.py`/`gen_outline_part2.py` cortaban a mitad de generación
sin avisar cuando la salida excedía `max_tokens` -- pasó dos veces
seguidas en la primera corrida real (`outline.md` cortó en Ch 23 de 46,
`gen_outline_part2.py` cortó en Ch 42). Ahora, si `stop_reason ==
"max_tokens"`, `llamar_api()` reenvía el texto acumulado como el último
mensaje de la conversación con `role: "assistant"` (sin turno de usuario
después -- técnica de *prefill*) y pide que la API continúe, hasta
`stop_reason == "end_turn"` o hasta agotar `max_continuaciones` (default
5).

**Qué está probado y qué no:** los 7 tests de `tests/test_api_comun.py`
cubren la lógica de acumulación, el tope de reintentos, y que el
`.rstrip()` antes de mandar el prefill evita el doble espacio -- pero
todos mockean `httpx.stream()` con un cuerpo SSE armado a mano. Un mock
prueba que *este código* concatena bien lo que sea que reciba; no prueba
que Fable 5, al recibir un prefill que corta literalmente a mitad de
palabra (p.ej. `"...cami"`), efectivamente complete con `"no..."` en vez
de reformular la oración, repetir el fragmento, o agregar una muletilla
de transición. Eso depende de que el modelo real respete la semántica de
prefill de la API, algo que no se puede confirmar sin gastar una llamada
real.

**Cómo validarlo:** correr `gen_outline.py` o `gen_outline_part2.py`
contra la API real con un `max_tokens` deliberadamente bajo (lo
suficiente para forzar `stop_reason=max_tokens` a las pocas centenas de
palabras, muy por debajo de las ~32000 que usan en producción) y
revisar a mano el `outline.md`/`esquema.md` resultante en la juntura
exacta entre la primera respuesta y la continuación: que no haya
palabras repetidas, que no falte texto, y que un corte a mitad de
palabra (si se da naturalmente) haya quedado bien empalmado.

**Estado:** implementado y probado con mocks; NO validado contra la API
real todavía. No bloqueante -- si el prefill no empalmara bien en la
práctica, el síntoma sería visible a simple vista en el archivo
resultante (palabra partida o repetida en la juntura), no un fallo
silencioso.
