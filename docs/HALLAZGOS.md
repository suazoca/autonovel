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

## `gen_world.py`/`gen_characters.py`/`gen_canon.py` también contaminados con *Bells*

**Dónde:** los tres prompts (no tocados en la Tarea 6, a pedido explícito
del usuario -- "sin tocar prompts todavía"). `gen_world.py` pide
"Cantamura", "Tonal Law", "Cass's Gift". `gen_characters.py` pide
personajes por nombre: Cass Bellwright, Eddan Bellwright, Perin
Bellwright, Maret Corda, Rector Suvaine, Torvald Hess. `gen_canon.py`
menciona "Tonal Law", "Cass's gift", "the Perin contract, the Expansion
Wars" como ejemplos en las instrucciones de formato.

**Por qué no se tocó:** la Tarea 6 era específicamente sobre persistencia
(que los scripts se guarden a sí mismos), no sobre descontaminación. El
usuario fue explícito: ningún prompt se toca en este commit.

**Estado:** NO corregido. Es el mismo tipo de problema que A1
(`draft_chapter.py`, Tarea 2) y el de `gen_outline.py`/`gen_outline_part2.py`
(Tarea 2b) -- candidato natural a una **Tarea 2c** con el mismo
tratamiento (armazón invariante + contenido derivado de
`mundo.md`/`personajes.md`/`semilla.txt`, en vez de nombres y lugares
escritos a mano). A confirmar con el usuario si se agrega formalmente al
encargo.

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

## Nada genera la Parte 2 de `voice.md`/`voz.md` -- hermano de la Tarea 6, prioridad alta

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

**Pregunta de diseño abierta, sin resolver:** ¿la voz se genera una sola
vez y se congela desde la iteración 1 de fundación, o se regenera en cada
iteración? `AUDITORIA_Y_PLAN.md` (B4) dice que la voz **no se redescubre
entre libros** de una serie ("voz.md Parte 2 se congela al terminar el
Libro I y se copia idéntica") -- pero no dice nada sobre qué pasa con las
iteraciones **dentro** del Libro I, que es un caso distinto (todavía no
hay libro publicado, el mundo mismo puede cambiar de iteración a
iteración). Si la voz se regenerara cada iteración, cada vuelta del loop
de fundación sonaría distinta, lo cual podría ser deseable (explorar) o
indeseable (inestable) según qué tan madura esté ya la fundación. No
resuelto -- queda para cuando se escriba `gen_voice.py`.

**Estado:** NO corregido, sin tarea formal asignada. Diagnosticar esto no
necesitó `.env`; escribir el script (`gen_voice.py` o similar, con el
mismo patrón main()/`fundacion_comun.py`/tests con `call_writer`
parcheado que el resto de la Tarea 6) tampoco lo necesitaría. Lo que sí
requiere `.env` es validar que los 5 pasajes de prueba que generaría
tengan alguna calidad real -- eso es juicio de un modelo, no algo que se
pueda mockear con sentido.
