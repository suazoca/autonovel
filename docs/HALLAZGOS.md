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

## `gen_outline.py` está contaminado con contenido de *Bells* (no estaba en la Tarea 2)

**Dónde:** `gen_outline.py`, todo el prompt (título de acto, comentario
`# always Cass, third-person limited`, "Cass's lie", Perin/Maret/Torvald/
Lenne, "Tonal Law", "the Bellwrights", "father's tremor", "the harmonic").

**Por qué no se tocó:** `ENCARGO_CLAUDE_CODE.md` Tarea 2 solo nombra
`draft_chapter.py` y `gen_brief.py`, y `AUDITORIA_Y_PLAN.md` (Clase A) no
incluye `gen_outline.py` ni en la lista de contaminados ni en la de
"archivos limpios" -- quedó afuera de la auditoría original. Es
exactamente el mismo tipo de problema que A1 (`draft_chapter.py`): un
prompt hardcodeado a una novela específica, que cualquier serie nueva
heredaría igual.

**Qué se hizo en la Tarea 3:** se agregó el campo `Ambición` a la plantilla
de salida por capítulo (edición mínima, sin tocar el resto del prompt),
porque era necesario para que `gen_outline.py` empiece a generar ese campo.
El resto del contenido de *Bells* en este archivo sigue ahí.

**Estado:** NO corregido -- descontaminar `gen_outline.py` completo (mismo
tratamiento que A1: armazón + reglas leídas de `mundo.md`/`personajes.md`/
`MISTERIO.md`) es trabajo del tamaño de la Tarea 2, no algo para hacer de
paso dentro de la Tarea 3.

---

## Discrepancia sin resolver: objetivo de palabras por capítulo

**Dónde:** `deteccion_es.py`, `CALIBRACION["palabras_objetivo_capitulo"]`
vale **3800** (comentario: `# era 3200`, consistente con "el español corre
15-20% más largo" documentado en el resto del mismo archivo).
`ENCARGO_CLAUDE_CODE.md`, Tarea 2, dice en cambio: *"Ajustá el objetivo de
palabras por capítulo a CALIBRACION["palabras_objetivo_capitulo"], que
ahora es **2000**. Capítulos más cortos, mismo largo total."*

**Por qué importa:** son números opuestos con justificaciones opuestas --
uno implica capítulos más largos (3200→3800, por la extensión del
español), el otro capítulos más cortos (→2000, "mismo largo total"
sugeriría más capítulos, no necesariamente más cortos por igual). No se
puede satisfacer las dos afirmaciones a la vez.

**Qué se hizo:** `draft_chapter.py` (Tarea 2) lee el valor real de
`CALIBRACION` en vez de hardcodear ninguno de los dos números, así que no
se tomó partido -- pero el valor que efectivamente se usa hoy es **3800**,
porque es el que está en el archivo.

**Estado:** sin resolver. Si la intención era 2000, hay que editar
`deteccion_es.py`; si era 3800 (y la prosa del encargo tiene un error de
tipeo), no hay que tocar nada. Confirmar con el usuario antes de cambiar
`CALIBRACION`.
