# AUDITORÍA DE AUTONOVEL Y PLAN DE MIGRACIÓN

Objetivo: convertir el repositorio en un framework reutilizable, en español,
capaz de sostener una serie de varios volúmenes.

Los problemas se dividen en tres clases, y conviene atacarlos en este orden
porque el segundo depende del primero:

- **Clase A — Contaminación.** Master contiene la novela anterior escrita a
  mano. Esto rompe la reutilización en cualquier idioma.
- **Clase B — Ausencia de capa de serie.** El modelo de datos asume una
  novela autoconclusiva por rama. No hay memoria entre volúmenes.
- **Clase C — Castellano.** Los evaluadores están calibrados para inglés.

---

## CLASE A — Descontaminar master

Master debe poder generar cualquier novela. Hoy no puede.

### A1. `draft_chapter.py` — CRÍTICO

El prompt es el de *The Second Son of the House of Bells*, no una plantilla.

Hardcodeado dentro del prompt:

| Línea | Qué fija |
|---|---|
| `Write Chapter {n} of "The Second Son..."` | el título |
| instrucción 2 | el POV: «locked to Cass's POV» |
| instrucción 6 | «the under-note», dolor detrás del ojo izquierdo |
| instrucción 11 | metáforas de sonido, bronce, campanas |
| instrucción 24 | «un chico de 14 años no habla en epigramas» |
| antipatrón 21 | «no termines con Cass escuchando a su padre» |

**Reparación.** Partir el prompt en dos: un armazón invariante y un bloque
`reglas_novela` que se lea de `voz.md` Parte 2 y de `personajes.md`.

```python
TITULO       = state["titulo"]
POV          = personajes["pov_principal"]          # nombre + persona + tiempo
POZOS_LEXICOS = voz["registro_lexico"]              # de voz.md Parte 2
REGLAS_ESPECIFICAS = voz["reglas_de_capitulo"]      # lista, puede ir vacía
PROHIBICION_FINAL  = ultimos_finales(n=3)           # calculado, no escrito
```

`PROHIBICION_FINAL` merece atención: la regla 21 existe porque los capítulos
tendían a terminar igual. La solución correcta no es escribir a mano el final
prohibido, sino leer los últimos tres capítulos y pasarle al redactor cómo
terminaron, con la instrucción de no repetirlo. Eso sirve para toda novela.

### A2. `typeset/novel.tex` — CRÍTICO

No es plantilla. Extraer a `typeset/libro.yaml` y generar el .tex:

titulo, subtitulo, autor, epígrafe y su atribución, encabezado par e impar,
línea de cierre, URL del colofón, logo, ornamento de capítulo, asunto del
PDF, numeración de capítulo (romana o arábiga).

`\bellornament` debe pasar a `\ornamentocapitulo`, definido desde el YAML.

### A3. `gen_brief.py` → `extract_voice_rules()`

Devuelve siete reglas fijas, de las cuales cuatro son de *Bells*
(«vocabulario de oficio, cuerpo y artesanía», emoción corporal primero).
Debe leer `voz.md` Parte 2 y extraerlas, no inventarlas.

### A4. `typeset/epub_metadata.yaml`

`lang: en` fijo. Título y autor como marcador de posición. Alimentar desde
el mismo `libro.yaml` de A2.

### A5. `landing/index.html`

Copia escrita para el libro anterior. Convertir a plantilla con variables.

### A6. Archivos limpios (no tocar por Clase A)

`evaluate.py`, `adversarial_edit.py`, `compare_chapters.py`,
`reader_panel.py`, `review.py`, `apply_cuts.py`, `run_pipeline.py`,
`build_outline.py`, `build_arc_summary.py` no contienen material de la
novela anterior. Solo necesitan Clase B y C.

---

## CLASE B — La capa de serie

Este es el trabajo nuevo. No existe nada de esto en el repositorio.

### B1. Estructura de ramas

```
master                        framework limpio, sin contenido
  └─ serie/sellos             biblia de serie, canon persistente
       ├─ serie/sellos/l1     Libro I
       ├─ serie/sellos/l2     Libro II
       └─ …
```

La rama de serie es la que persiste. Cada libro se ramifica desde ella y,
al terminar, devuelve a la serie su canon nuevo y su resumen de arco.

### B2. Archivos nuevos, en la rama de serie

```
serie.md                biblia de serie: premisa, reglas del mundo que no
                        cambian nunca, tono, promesa al lector
arco_serie.md           qué pasa en cada volumen, en dos páginas
canon_serie.md          hechos duros que valen para todos los libros
personajes_serie.md     quién vive, quién murió y en qué libro, edades,
                        estado del arco al cerrar cada volumen
MISTERIO_SERIE.md       el secreto central y el reloj de revelación
siembras_serie.md       libro de siembras con alcance entre volúmenes
estado_serie.json       { "libros_completos": [1], "libro_actual": 2 }
```

### B3. Modificación del libro de siembras

Hoy toda siembra debe pagarse dentro de la misma novela, y el evaluador
castiga las que quedan abiertas. Para una serie hace falta un campo de
alcance:

```json
{
  "id": "firma-diecisiete",
  "siembra": {"libro": 1, "capitulo": 3},
  "pago":    {"libro": 2, "capitulo": 14},
  "alcance": "serie",
  "estado":  "pendiente"
}
```

Y la regla de validación pasa a ser:

- `alcance: "libro"` sin pago dentro del volumen → error, como hoy.
- `alcance: "serie"` sin pago dentro del volumen → correcto, siempre que
  el pago esté registrado en `siembras_serie.md` con libro asignado.
- Siembra de alcance de serie sin libro de pago asignado → error.

Sin esto, el evaluador de fundación va a rechazar la estructura del Libro I
por «desequilibrio de siembras», que es justamente lo que debe tener.

### B4. Fundación heredada

Para el Libro I, la fase de fundación genera todo. Del Libro II en adelante
debe **heredar y extender**, no regenerar:

| Herramienta | Libro I | Libro II en adelante |
|---|---|---|
| `gen_mundo.py` | genera | lee `canon_serie.md`, genera solo lo nuevo |
| `gen_personajes.py` | genera | carga `personajes_serie.md`, avanza arcos |
| `gen_esquema.py` | genera | recibe `arco_serie.md` y las siembras abiertas |
| `gen_canon.py` | genera | añade a `canon_serie.md`, no lo reescribe |
| voz | descubre | **hereda sin cambios**: la voz no se redescubre |

Ese último punto es el que más se suele romper. Si el Libro III vuelve a
correr el descubrimiento de voz, la serie deja de sonar a la misma persona.
`voz.md` Parte 2 se congela al terminar el Libro I y se copia idéntica.

### B5. Umbral de continuidad entre volúmenes

Herramienta nueva, `verificar_continuidad.py`. Antes de redactar el Libro N,
corre contra `canon_serie.md` y falla si el esquema nuevo contradice un
hecho establecido: una edad imposible, un personaje muerto que habla, una
regla del mundo que cambió sin justificación en escena.

Es el equivalente entre libros de lo que `canon.md` hace dentro de uno.

### B6. Panel de lectores y revisión, adaptados a serie

`reader_panel.py` juzga una novela autoconclusiva. Para un volumen de serie
hay que añadir dos dimensiones y modificar una:

- **Reentrada**: ¿funciona para alguien que leyó el volumen anterior hace
  dos años? ¿Recuerda lo necesario sin resumen expositivo?
- **Puerta abierta**: ¿el final abre una puerta o deja un agujero? Un
  agujero es un final incompleto; una puerta es un final cerrado que
  promete. Hoy el panel penalizaría ambos por igual.
- **`earned_ending`** debe evaluarse contra la promesa de *este volumen*,
  no contra la de la serie.

`review.py` debe recibir `arco_serie.md` y los resúmenes de los volúmenes
anteriores, nunca los manuscritos completos. Al cuarto libro serían casi
cuatrocientas mil palabras por llamada.

### B7. `state.json` y el orquestador

```json
{ "serie": "sellos", "libro": 2, "fase": "fundacion", "iteracion": 0,
  "deudas": [], "deudas_de_serie": [] }
```

`run_pipeline.py` necesita `--libro N` y `--serie <tag>`, y una fase 0 nueva
que cargue el contexto de serie antes de la fundación.

---

## CLASE C — Castellano

### C1. `evaluate.py`

Reemplazar las constantes por las de `deteccion_es.py`. Lo importante:

- La raya (—) es signo de diálogo. El contador actual penaliza escribir bien.
  Usar `densidad_raya_parentetica()`.
- Las listas de nivel 1, 2 y 3 se reconstruyen, no se traducen.
- Añadir el detector de calcos del inglés: sujeto pronominal redundante,
  posesivo calcado en partes del cuerpo, «estar siendo», pasiva perifrástica,
  dequeísmo. Es la huella más delatora de un modelo que piensa en inglés.
- Segmentación de oraciones que respete ¿ ¡ y las abreviaturas.

### C2. Prompts de juez y revisor

Escribirlos en español y advertirles de las normas castellanas, o van a
penalizar como defectos la subordinación larga y el diálogo con raya.
Afecta a `evaluate.py`, `adversarial_edit.py`, `reader_panel.py`,
`review.py`, `compare_chapters.py`.

### C3. `typeset/novel.tex`

Con `fontspec` y tectonic, el camino limpio es polyglossia:

```latex
\usepackage{polyglossia}
\setmainlanguage{spanish}
```

Y además: `\chaptername` a «capítulo», comillas latinas «» para citas,
sangría francesa en los párrafos de diálogo con raya, y revisar la
versalita del encabezado con vocales acentuadas. La letra capital de
`lettrine` necesita prueba con Á, É, Í, Ó, Ú.

### C4. Calibración numérica

El español corre entre un 15 % y un 20 % más largo. Objetivo por capítulo
de 3.200 a 3.800 palabras. El coeficiente de variación de longitud de
oración sube a 0,32. Los umbrales de aceptación (6,0 y 7,5) no cambian.

### C5. Audiolibro

`gen_audiobook.py` debe usar el modelo multilingüe de ElevenLabs y
`audiobook_voices.json` necesita reparto en español, con una decisión previa
de registro: neutro latinoamericano o peninsular. Para una serie, ese
reparto vive en la rama de serie, no en la del libro.

---

## NOMENCLATURA

Recomendación: renombrar los archivos de **contenido** al español, porque el
agente lee el nombre como pista semántica y escribe mejor.

```
voice.md → voz.md          world.md → mundo.md
characters.md → personajes.md   outline.md → esquema.md
MYSTERY.md → MISTERIO.md   seed.txt → semilla.txt
```

Los scripts `.py` conservan el nombre en inglés. Renombrarlos no mejora la
prosa y complica traer cambios del repositorio original.

---

## ORDEN DE EJECUCIÓN

1. **Clase A completa.** Sin esto, todo lo demás se construye sobre arena.
2. **C1 y C2**, los evaluadores en español. Se pueden probar de inmediato
   contra prosa castellana existente.
3. **B1, B2 y B3**: capa de serie y siembras de alcance largo. Necesario
   antes de generar la fundación del Libro I, porque el esquema del Libro I
   ya tiene que sembrar para el Libro V.
4. **Fundación del Libro I**: mundo, personajes, esquema.
5. **B4, B5 y B6** antes de empezar el Libro II. No urge todavía.
6. **C3, C4 y C5** antes de exportar.
