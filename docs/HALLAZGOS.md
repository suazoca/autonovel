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
