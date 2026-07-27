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
