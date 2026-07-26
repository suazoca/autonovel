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

### Test de aceptación de la Tarea 1

```bash
uv run python -m pytest tests/test_deteccion_es.py -v
```

Creá ese archivo con estos casos, que deben pasar:

1. `cap_dialogado_es.md` puntúa **más alto** que en BASELINE.
   Este es el test que importa: el texto no cambió, solo dejamos de
   castigarlo por usar bien la puntuación española.
2. `cap_con_slop_es.md` puntúa **más bajo** que `cap_dialogado_es.md`.
3. `densidad_raya_parentetica()` sobre 40 líneas de diálogo con raya
   devuelve 0.0.
4. `densidad_raya_parentetica()` sobre prosa con incisos parentéticos
   abusivos devuelve > 50.
5. `calcos_detectados("Levantó su mano. Estaba siendo observada.")`
   devuelve al menos dos hallazgos.
6. `dividir_oraciones("¿Viniste? Sí. El Sr. Pérez no vino.")` devuelve
   3 oraciones, no 4 (no debe cortar en «Sr.»).

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

## ENTREGA

Un commit por tarea, con el test pasando. Al terminar:

1. Actualizá `docs/BASELINE.md` con los puntajes nuevos.
2. Escribí `docs/HALLAZGOS.md` con lo que encontraste roto y no arreglaste.
3. Dejá `README.md` reflejando que el framework ahora soporta español y
   series, y qué falta (capa de serie completa, .tex con polyglossia,
   audiolibro multilingüe).

**No** hagas merge a master. Dejá la rama para revisión.
