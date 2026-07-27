# ENCARGO: adaptar autonovel a español y a series multilibro

Contexto en `docs/AUDITORIA_Y_PLAN.md`. Este archivo es el trabajo concreto.

Cuatro tareas. Hacelas **en orden** y **commiteá cada una por separado**.
Después de cada tarea, corré su test de aceptación y no sigas si falla.

Regla general: no cambies el comportamiento del pipeline más allá de lo
pedido. Si encontrás algo roto que no está en esta lista, anotalo en
`docs/HALLAZGOS.md` y seguí.

---

## TAREA 0 — Línea base (antes de tocar nada)

Necesitamos saber qué puntúa hoy el evaluador, para detectar regresiones.

1. Elegí tres capítulos existentes de la novela anterior.
2. Corré `evaluate.py` sobre cada uno.
3. Guardá los puntajes en `docs/BASELINE.md` con fecha y hash del commit.

Además, creá dos capítulos de prueba en español, en `tests/fixtures/`:

- `cap_dialogado_es.md` — ~800 palabras, mayormente diálogo con raya (—),
  prosa limpia, sin muletillas. Debe ser prosa **buena**.
- `cap_con_slop_es.md` — ~800 palabras, sembrado a propósito con: tres
  clichés de la lista, dos calcos del inglés («levantó su mano», «estaba
  siendo»), un «no solo… sino que», y dos adverbios emocionales en -mente.

Corré `evaluate.py` sobre ambos y anotá los puntajes en `BASELINE.md`.

**Aceptación:** existe `docs/BASELINE.md` con cinco puntajes anotados.
Es esperable que el capítulo dialogado en español puntúe mal. Ese es el bug.

---

## TAREA 1 — Evaluadores en español

### 1a. Integrar `deteccion_es.py` en `evaluate.py`

`deteccion_es.py` ya está en la raíz y probado de forma aislada. Hay que
enchufarlo.

En `evaluate.py`, reemplazá las constantes en inglés por las del módulo:

```python
from deteccion_es import (
    NIVEL1_PROHIBIDAS, NIVEL1_LOCUCIONES, NIVEL2_SOSPECHOSAS,
    NIVEL3_MULETILLAS, CONECTORES_APERTURA, CLICHES_FICCION,
    TICS_ESTRUCTURALES, PATRONES_CONTAR, CALCOS_DEL_INGLES,
    densidad_raya_parentetica, dividir_oraciones, cv_longitud_oracion,
    calcos_detectados, CALIBRACION,
)
```

**El cambio crítico** está en `slop_score()`. Hoy cuenta todas las rayas:

```python
em_dash_density = text.count("—") / len(words) * 1000   # ROTO en español
```

En español la raya es el signo de diálogo. Reemplazar por:

```python
em_dash_density = densidad_raya_parentetica(text)
```

Y el umbral baja de 15 a `CALIBRACION["umbral_raya_parentetica"]` (6.0).

Reemplazá también la segmentación de oraciones por `dividir_oraciones()`,
que respeta ¿ ¡ y las abreviaturas españolas.

Agregá una penalización nueva por calcos del inglés usando
`calcos_detectados()`. Sugerencia: 0.5 puntos por calco, tope 2.0.

Hacé que el idioma sea configurable, no fijo. Lo más limpio es un
parámetro `--idioma es|en` que elija el módulo de constantes, para no
romper el inglés. Si eso complica mucho, priorizá que funcione el español.

### 1b. Prompts de juez en español

Traducir los prompts de LLM en: `evaluate.py`, `adversarial_edit.py`,
`reader_panel.py`, `review.py`, `compare_chapters.py`.

No es traducción literal. Cada prompt de juez necesita este bloque
agregado, porque si no van a marcar como defectos cosas que son norma
castellana:

```
El texto está en español. Antes de juzgar, tené en cuenta:
- El diálogo se marca con raya (—), no con comillas. Es correcto.
- La subordinación larga y la coordinación con «y» son recursos legítimos
  del castellano, no verbosidad.
- El sujeto pronominal se omite por defecto. Su ausencia es correcta;
  su presencia repetida es un calco del inglés y sí es un defecto.
- El español corre entre 15% y 20% más largo que el inglés para el mismo
  contenido. No penalices por extensión comparándolo con prosa inglesa.
```

### 1c. Flag `--solo-mecanico` en `evaluate.py`

Agregado por fuera del texto original del encargo, porque los tests 1 y 2
de abajo no se podían correr sin gastar API ni quedar sujetos a la
variabilidad del juez LLM. `evaluate.py --archivo <path> --solo-mecanico`
corre únicamente `slop_score()` (determinista, sin red) y no depende de
`.env`. La integración de las constantes en español descrita en 1a queda
adentro de esta parte mecánica; los prompts en español (1b) siguen
dependiendo del juez y por lo tanto de la API key.

### 1d. Fixtures mínimos de voz y mundo para tests

`evaluate_chapter()` lee `voice.md`/`world.md`/`characters.md`/`canon.md`
del directorio raíz -- que hoy siguen siendo los de *Bells*, en inglés.
Evaluar un capítulo de prueba en español contra una biblia de voz en
inglés no mide nada real. Se crean, en `tests/fixtures/`:

- `voz_minima_es.md` -- perfil de voz mínimo en español, desacoplado de
  cualquier novela real, con Parte 1 (guardarraíles) y Parte 2 (identidad
  de voz, pasajes ejemplares y anti-ejemplares).
- `mundo_minimo_es.md` -- biblia de mundo mínima, misma forma que
  `world.md` (cosmología, sistema de "magia" -- aquí, reglas documentales
  --, geografía, facciones, bestiario, detalles culturales, consistencia
  interna), con contenido deliberadamente escueto.

Quedan creados como fixtures de prueba; conectarlos a una corrida real de
`evaluate_chapter()` (que hoy tiene las rutas de voice.md/world.md
hardcodeadas al directorio raíz, no parametrizables) es trabajo aparte,
pendiente de `.env` y de decidir cómo parametrizar esas rutas.

### Test de aceptación de la Tarea 1

```bash
uv run python -m pytest tests/test_deteccion_es.py -v
```

Creá ese archivo con estos casos, que deben pasar:

1. `cap_dialogado_es.md` puntúa **más alto** que en BASELINE.
   Este es el test que importa: el texto no cambió, solo dejamos de
   castigarlo por usar bien la puntuación española.
   (Verificado vía `--solo-mecanico`, no contra el `overall_score` del
   juez LLM todavía -- ver docs/BASELINE.md.)
2. `cap_con_slop_es.md` puntúa **más bajo** que `cap_dialogado_es.md`.
3. `densidad_raya_parentetica()` sobre 40 líneas de diálogo con raya
   devuelve 0.0.
4. `densidad_raya_parentetica()` sobre prosa con incisos parentéticos
   abusivos devuelve > 50.
5. `calcos_detectados("Levantó su mano. Estaba siendo observada.")`
   devuelve al menos dos hallazgos.
6. `dividir_oraciones("¿Viniste? Sí. El Sr. Pérez no vino.")` devuelve
   3 oraciones, no 4 (no debe cortar en «Sr.»).
   **Corregido:** este caso estaba mal escrito -- `dividir_oraciones()`
   descarta por diseño las oraciones de ≤2 palabras ("¿Viniste?", "Sí."
   nunca iban a contar), así que nunca iba a dar 3. El caso real en
   `tests/test_deteccion_es.py` usa
   `"El Sr. Pérez no vino a la reunión. ¿Sabés por qué faltó?"` → 2
   oraciones, verificando que no corta en "Sr.".

---

## TAREA 2 — Descontaminar el redactor

`draft_chapter.py` tiene el prompt de la novela anterior escrito a mano.
Cualquier novela que se redacte hoy hereda su protagonista y sus metáforas.

### Qué está hardcodeado

Buscá en el prompt y sacá:
- el título de la novela anterior
- el POV fijado en el personaje «Cass»
- «the under-note» / el dolor detrás del ojo izquierdo
- las metáforas obligatorias de sonido, bronce y campanas
- la instrucción sobre cómo habla un chico de 14 años
- el antipatrón que prohíbe terminar con Cass escuchando a su padre

### Cómo reemplazarlo

Partí el prompt en dos: armazón invariante + bloque de reglas leído de
archivos de la rama.

```python
TITULO             = state["titulo"]
POV                = personajes["pov_principal"]      # nombre, persona, tiempo
POZOS_LEXICOS      = voz["registro_lexico"]           # de voz.md Parte 2
REGLAS_ESPECIFICAS = voz["reglas_de_capitulo"]        # lista, puede ir vacía
PROHIBICION_FINAL  = ultimos_finales(n=3)             # CALCULADO
```

`ultimos_finales(n)` es una función nueva: lee los últimos n capítulos
escritos, extrae el párrafo final de cada uno, y los inyecta en el prompt
con la instrucción de no repetir ese tipo de cierre.

Esto reemplaza el antipatrón hardcodeado por algo que sirve para cualquier
novela. Era la regla correcta implementada de la peor manera.

Aplicá el mismo tratamiento a `gen_brief.py` → `extract_voice_rules()`,
que hoy devuelve siete reglas fijas, cuatro de ellas de la novela anterior.
Debe leer y parsear `voz.md` Parte 2.

Ajustá el objetivo de palabras por capítulo a
`CALIBRACION["palabras_objetivo_capitulo"]`, que ahora es 2000. Capítulos
más cortos, mismo largo total. No lo dejes hardcodeado tampoco.

### Test de aceptación de la Tarea 2

```bash
grep -riE "cass|bell|bronze|under-note" draft_chapter.py gen_brief.py
```

Debe devolver **cero resultados**.

Y un test funcional: construí el prompt con un `voz.md` y un
`personajes.md` de prueba inventados (no los de esta novela), y verificá
que el prompt resultante contiene el POV de prueba y ninguna referencia a
la novela anterior.

---

## TAREA 2b — Descontaminar `gen_outline.py` y `gen_outline_part2.py` (Tarea 2 incompleta)

Encontrado durante la Tarea 3 (`gen_outline.py`) y la Tarea 4
(`gen_outline_part2.py`), no es un hallazgo aparte: se me pasó en la
auditoría original (`AUDITORIA_Y_PLAN.md` Clase A no lista ninguno de los
dos ni como contaminado ni como limpio) y en la Tarea 2 (solo nombraba
`draft_chapter.py`/`gen_brief.py`). Es exactamente el mismo problema que
A1: un prompt hardcodeado a *The Second Son of the House of Bells* que
cualquier novela nueva hereda igual. Confirmado por el usuario: los dos
archivos entran en esta tarea, no solo `gen_outline.py`.

**Orden de ejecución: después de la Tarea 4** (ya completa). Es la última
tarea sin bloquear por `.env`.

### Qué está hardcodeado en `gen_outline.py`

- El comentario `# always Cass, third-person limited` en la plantilla por
  capítulo.
- "Cass's lie" y la instrucción de cómo se refuerza/desafía por capítulo.
- Los nombres Perin, Maret, Torvald, Lenne en KEY PLOT ARCHITECTURE.
- "Tonal Law", "the Bellwrights", "the harmonic", "father's tremor".
- Todo el arco de Actos I-III escrito para la trama específica de Bells.

### Qué está hardcodeado en `gen_outline_part2.py`

- Los capítulos 17-24 escritos a mano para la trama de Bells: la
  confrontación con Maret, "the void", el clímax en "the Bell Tower", el
  Final Image espejado del Ch 1.
- El `system` prompt asume que continúa un esquema de 24 capítulos
  específico.
- **Bug real, no solo contaminación:** `part1 = open('/tmp/outline_output.md').read()`
  es una ruta absoluta hardcodeada fuera del repo. No existe en este
  entorno -- el script rompe si se lo corre tal cual. Con contenedores
  efímeros esto es una bomba de tiempo (el archivo puede no existir nunca,
  o existir con contenido de una corrida anterior sin relación). Arreglar
  esto también, como parte de esta tarea, no como hallazgo aparte:
  `gen_outline.py` ya imprime su resultado por stdout (`print(result)`,
  línea final) -- lo más simple es que `gen_outline_part2.py` lea de
  `outline.md` (si `gen_outline.py` ya lo guardó ahí) o reciba la ruta por
  argumento, nunca una ruta fija en `/tmp`.

### Cómo reemplazarlo

Mismo tratamiento que A1 (`draft_chapter.py` en la Tarea 2): partir cada
prompt en armazón invariante (estructura de Save the Cat / MICE Quotient /
Dan Harmon, formato de salida por capítulo, instrucciones de cantidad de
capítulos y palabras) + bloque de contenido leído de `mundo.md`,
`personajes.md`, `MISTERIO.md` y `seed.txt`/`semilla.txt` (ya se cargan al
principio de `gen_outline.py`, pero el prompt no los usa para nada
específico de la trama -- KEY PLOT ARCHITECTURE debería derivarse de esos
archivos, no estar escrito a mano). Para `gen_outline_part2.py`, lo mismo
aplicado a REMAINING STRUCTURE NEEDED y a los beats del clímax.

### Test de aceptación de la Tarea 2b

```bash
grep -riE "cass|bell|bronze|under-note|perin|maret|torvald|lenne|tonal" gen_outline.py gen_outline_part2.py
grep -n "/tmp/" gen_outline_part2.py
```

Los dos deben devolver **cero resultados**.

Y un test funcional equivalente al de la Tarea 2: construir el prompt de
cada script con un `seed.txt`/`mundo.md`/`personajes.md`/`MISTERIO.md` de
prueba inventados, y verificar que el resultado no contiene ninguna
referencia a la novela anterior.

---

## TAREA 3 — Campo de ambición por capítulo

Hoy todos los capítulos compiten contra un umbral único (6.0), lo que
empuja la novela hacia la media. Las novelas que funcionan tienen picos,
no buen promedio.

### Cambios

En el esquema (`esquema.md` / `gen_outline.py`), cada capítulo declara:

```yaml
ambicion: pico | sosten | valle
```

- **pico**: escena que el lector tiene que recordar. Umbral 7.5.
- **sosten**: capítulo de trabajo, avanza la trama. Umbral 6.5.
- **valle**: respiro deliberado, transición. Umbral 6.0.

En `evaluate.py`, el umbral de aceptación se lee de la ambición declarada
del capítulo, no de una constante global.

En `run_pipeline.py`, el criterio de «avance antes que perfección» pasa a
respetar el umbral por capítulo.

Agregá una validación en la fase de fundación: si un esquema no tiene al
menos un 15% de capítulos marcados como pico, es un esquema plano y hay
que avisar.

### Test de aceptación de la Tarea 3

Un capítulo marcado `pico` que puntúa 7.0 debe ser **rechazado**.
El mismo capítulo marcado `valle` debe ser **aceptado**.
Un esquema sin ningún pico debe emitir advertencia.

---

## TAREA 4 — Alcance de siembra

El libro de siembras exige hoy que toda siembra se pague dentro del mismo
volumen. Para una serie eso es incorrecto: el Libro I tiene que sembrar
para el II sin que el evaluador lo marque como hilo suelto.

### Cambios

En `gen_outline_part2.py` y en el validador correspondiente, la entrada de
siembra pasa a ser:

```json
{
  "id": "identificador-legible",
  "siembra": {"libro": 1, "capitulo": 3},
  "pago":    {"libro": 2, "capitulo": 14},
  "alcance": "libro" | "serie",
  "estado":  "pendiente" | "pagada"
}
```

Reglas de validación:

| Caso | Resultado |
|---|---|
| `alcance: libro`, sin pago en el volumen | ERROR (como hoy) |
| `alcance: serie`, sin pago en el volumen, con libro de pago asignado | OK |
| `alcance: serie`, sin libro de pago asignado | ERROR |
| `alcance: serie`, pago asignado a un libro ya publicado | ERROR |

Las siembras de alcance de serie se escriben también en
`siembras_serie.md`, en la rama de serie. Si el archivo no existe (novela
suelta), el alcance de serie no está disponible y todo es alcance de libro.

### Test de aceptación de la Tarea 4

Cuatro casos de la tabla, cada uno con su test. Y un test de regresión:
una novela suelta sin `siembras_serie.md` debe comportarse exactamente
como antes del cambio.

---

## TAREA 6 — Persistencia de la fase de fundación (prioridad alta)

Encontrado al arreglar el `/tmp/outline_output.md` de la Tarea 2b: **todos**
los scripts de fundación tienen el mismo patrón roto. `gen_world.py`,
`gen_characters.py` y `gen_canon.py` terminan con `print(result)` y nunca
escriben en su archivo destino (`world.md`/`mundo.md`,
`characters.md`/`personajes.md`, `canon.md`). `gen_outline.py` y
`gen_outline_part2.py` tenían el mismo problema y ya se corrigieron en la
Tarea 2b (ahora guardan en `esquema.md`/`outline.md` ellos mismos).

Y `run_pipeline.py::run_foundation()` no lo compensa: llama
`uv_run("gen_world.py")` etc., que corre el script y captura su stdout en
un `subprocess.CompletedProcess`, pero nunca vuelca ese stdout a ningún
archivo.

**Por qué es prioridad alta:** tal como está, correr `run_pipeline.py
--phase foundation` de punta a punta -- con `.env` configurado y todo --
**no dejaría nada escrito** en `world.md`, `characters.md` ni `canon.md`.
El pipeline automatizado que describe `PIPELINE.md` no puede funcionar
sin intervención manual (correr cada script y redirigir el stdout a mano).
Esto bloquea completar la fundación de cualquier novela nueva, incluida
esta rama.

### Cambios

Mismo patrón que se usó para `gen_outline.py`/`gen_outline_part2.py` en la
Tarea 2b: cada script se guarda a sí mismo, con resolución bilingüe
(`ruta_bilingue()`).

- `gen_world.py` → escribe en `mundo.md`/`world.md`.
- `gen_characters.py` → escribe en `personajes.md`/`characters.md`.
- `gen_canon.py` → **reescribe `canon.md` entero, no lo acumula.**
  Corrección sobre una versión anterior de este documento, que decía lo
  contrario. `canon.md`, en la fase de fundación, es una extracción
  derivada de `semilla.txt` + `mundo.md` + `personajes.md` -- no tiene
  hechos propios que no vengan de esos tres archivos. Y el descarte de
  una iteración de fundación ya lo hace `git reset --hard` en
  `run_pipeline.py`: si la iteración N se descarta porque el score no
  mejoró, mundo/personajes vuelven al estado de la iteración N-1.
  Acumular canon entre iteraciones arrastraría hechos de un mundo que
  ya no existe -- canon quedaría corriendo desincronizado de los
  documentos de los que depende. Reescribir entero mantiene canon.md
  siempre consistente con el mundo/personajes actuales.

Guard de semilla vacía: `fundacion_comun.exigir_semilla(seed, accion)`,
compartido (no una cuarta o quinta copia), usado por los **cuatro**
generadores que consumen la semilla -- `gen_world.py`, `gen_characters.py`,
`gen_canon.py`, y **`gen_outline.py`** (ya existía de la Tarea 2b, se le
agregó el guard acá por la misma razón: llama a la API con la semilla como
insumo central). `gen_outline_part2.py` no carga `seed.txt`/`semilla.txt`
en absoluto -- no le corresponde.

`run_pipeline.py::run_foundation()` sí necesitó cambios, más allá de que
cada script se guarde solo: hoy cada `uv_run()` ignoraba el returncode.
Un generador que falla ahora aborta el pipeline entero (no solo la
iteración -- un returncode != 0 es un fallo de infraestructura, reintentar
no lo arregla), guarda `state` antes de salir para poder retomar desde la
iteración en curso, e imprime qué script falló con su stderr completo.
Y antes de llamar a `evaluate.py --phase=foundation`, se verifica que
`mundo.md`/`personajes.md`/`esquema.md`/`canon.md` se modificaron **en
esta iteración** (mtime posterior al inicio de la iteración) y no están
vacíos. "Existe y no está vacío" no alcanza por sí solo:
`world.md`/`characters.md`/`outline.md` están trackeados en git como
plantillas con contenido real (encabezados + comentarios HTML, no bytes
vacíos), así que ese chequeo por sí solo daría verde contra el andamio
sin tocar, sin que ningún generador haya corrido de verdad. Una fundación
incompleta no debe producir un puntaje que entre a `results.tsv`.

### Test de aceptación de la Tarea 6

Para cada script: correr `build_prompt()` (o la función equivalente) con
inputs de prueba, invocar la función de guardado con una respuesta
simulada del modelo, y verificar que el archivo destino (en un `tmp_path`)
contiene esa respuesta. Un test de regresión para `gen_canon.py`: si
`canon.md` ya tiene contenido, guardar debe agregarlo, no reemplazarlo.

---

## ENTREGA

Un commit por tarea, con el test pasando. Al terminar:

1. Actualizá `docs/BASELINE.md` con los puntajes nuevos.
2. Escribí `docs/HALLAZGOS.md` con lo que encontraste roto y no arreglaste.
3. Dejá `README.md` reflejando que el framework ahora soporta español y
   series, y qué falta (capa de serie completa, .tex con polyglossia,
   audiolibro multilingüe).

**No** hagas merge a master. Dejá la rama para revisión.
