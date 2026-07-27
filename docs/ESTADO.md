# ESTADO — rama `framework/es-multilibro`

Última actualización: 2026-07-27 (tras cerrar la Tarea 2b). Escrito para
retomar en otra sesión sin releer todo el historial de commits.

## Punto de partida que sigue vigente

- **No existe `.env`** en este entorno (ni `ANTHROPIC_API_KEY`). Nada que
  dependa del juez LLM se puede probar hasta que exista.
- **No existe la rama `autonovel/bells`** en este remoto (confirmado con
  `git fetch --all` + `git ls-remote --heads origin`). No hay comparación
  disponible contra la novela anterior en inglés; toda la línea base se
  armó con fixtures de prueba en español, no con capítulos reales.
- **Push: al día.** Todo hasta `648b0c3` está en
  `origin/framework/es-multilibro` (confirmado con `git fetch` +
  `git log origin/framework/es-multilibro..HEAD`, vacío).
  **Cuatro tokens de GitHub distintos quedaron expuestos en el chat
  durante esta sesión** (pegados mal en la terminal, en varios intentos
  de push). El primero fue revocado con confirmación explícita del
  usuario; los otros tres no tienen confirmación explícita en el chat --
  **verificar que estén revocados**, no asumir que sí. Si se necesita
  pushear de nuevo: token nuevo, exportado como variable de entorno en la
  terminal del usuario, nunca pegado en el chat -- o mejor, un credential
  helper de git configurado una sola vez. `gh` no está instalado en este
  entorno (se intentó `gh auth login`, no existe el binario) -- la única
  vía probada es `git push https://$TOKEN@github.com/...`.

## Commits de esta rama (orden cronológico)

```
3ded223 docs: auditoría, plan de adaptación y módulo de detección en español  (llegó por git pull, no generado en esta sesión)
7346d77 Tarea 0: línea base con fixtures en español
214768e fix: IGNORECASE en calcos_detectados + corrección del test 6
625fc7f Tarea 1c (A): flag --solo-mecanico en evaluate.py
975ac18 Tarea 1c (B): integra deteccion_es.py en slop_score()
49a5976 Tarea 1d: fixtures mínimos de voz y mundo en español
76454a5 docs: ESTADO.md para retomar sin releer el historial
04b6439 Tarea 2: descontamina draft_chapter.py y gen_brief.py
4ad802c docs: ESTADO.md al día con el cierre de la Tarea 2
5af3cb9 Tarea 3: campo de ambición por capítulo (pico | sosten | valle)
d3c4c72 fix: palabras_objetivo_capitulo=2000 (era 3800, error de mi sesión anterior)
506f435 Tarea 4: alcance de siembra para series (libro | serie)
df7b06c docs: suma gen_outline_part2.py a la Tarea 2b, documenta dependencia de libros_completos
c513adf docs: ESTADO.md al día con el cierre de la Tarea 4              <- pusheado hasta acá
5a78c52 Tarea 2b: descontamina gen_outline.py y gen_outline_part2.py     <- sin pushear
```

`1c` y `1d` no estaban en el `ENCARGO_CLAUDE_CODE.md` original -- se
agregaron sobre la marcha (documentadas ahí mismo) porque hacían falta
para que los tests 1 y 2 de la Tarea 1 corrieran sin API.

## Qué está hecho y probado

- **`tests/fixtures/cap_dialogado_es.md`** (624 palabras) y
  **`cap_con_slop_es.md`** (587 palabras, slop sembrado a propósito):
  capítulos de prueba en español, verificados contra `deteccion_es.py`.
- **`deteccion_es.py`**: bug de `calcos_detectados()` (faltaba
  `re.IGNORECASE`) corregido y confirmado con test.
- **`evaluate.py`**:
  - Flag `--solo-mecanico` (+ `--archivo <path>`): corre solo
    `slop_score()`, sin LLM, sin API, determinista.
  - `slop_score()` reemplazado: las listas en inglés (TIER1/2/3,
    FICTION_AI_TELLS, STRUCTURAL_AI_TICS, TELLING_PATTERNS,
    TRANSITION_OPENERS, conteo crudo de em-dash) fueron sustituidas por
    las de `deteccion_es.py` (NIVEL1/2/3, CLICHES_FICCION,
    TICS_ESTRUCTURALES, PATRONES_CONTAR, CONECTORES_APERTURA,
    `densidad_raya_parentetica`, `cv_longitud_oracion`) + penalización
    nueva por calcos del inglés (0.5/calco, tope 2.0). Hardcodeado a
    español, sin flag `--idioma` todavía.
  - Medido antes/después con los dos fixtures (docs/BASELINE.md):
    `cap_dialogado_es.md` 1.0 → 0.0 de penalización, `cap_con_slop_es.md`
    0.0 → 2.9. Se corrigió la relación invertida que era el bug original.
- **`tests/test_deteccion_es.py`**: 7 tests, todos en verde sin API
  (`uv run python -m pytest tests/test_deteccion_es.py -v`):
  1. `cap_dialogado_es.md` puntúa más alto que antes de la integración.
  2. `cap_con_slop_es.md` puntúa más bajo que el dialogado.
  3. Test de regresión dedicado que fija la *relación* (no los valores
     absolutos) entre 1 y 2, para que una futura recalibración de
     `CALIBRACION` no pueda invertirla en silencio.
  4-5. `densidad_raya_parentetica()` sobre diálogo limpio (0.0) e incisos
     abusivos (>50).
  6. `calcos_detectados()` insensible a mayúsculas.
  7. `dividir_oraciones()` no corta en "Sr." (caso 6 del encargo original
     estaba mal escrito -- corregido, ver detalle en
     `ENCARGO_CLAUDE_CODE.md` sección 1d).
- **`tests/fixtures/voz_minima_es.md`** y **`mundo_minimo_es.md`**: perfil
  de voz y biblia de mundo mínimos, en español, desacoplados de cualquier
  novela real, con la misma forma que `voice.md`/`world.md`. Creados pero
  **no conectados** todavía a una corrida real de `evaluate_chapter()`.
- **`docs/BASELINE.md`**: línea base completa con los números mecánicos
  antes/después. El `overall_score` del juez LLM sigue **PENDIENTE**
  (requiere `.env`).
- **`docs/HALLAZGOS.md`**: dos hallazgos documentados, sin corregir a
  pedido explícito:
  1. `dividir_oraciones()` descarta oraciones de ≤2 palabras por diseño,
     lo que sesga `cv_longitud_oracion()` hacia arriba (subestima el uso
     de frases cortas como marcador de prosa humana).
  2. `CALIBRACION["umbral_cv_oracion"]` (0.32) no discriminó nada entre
     los dos fixtures (0.686 y 0.591, ambos muy por encima) -- es una
     estimación sin corpus de referencia, pendiente de recalibrar con
     prosa española real.

### Tarea 2 — Descontaminar el redactor (COMPLETA, commit `04b6439`)

- **`draft_chapter.py`**: prompt partido en armazón invariante + reglas
  leídas de archivos. `TITULO` viene de `state.json` clave `"titulo"` (con
  fallback a `"title"` por compatibilidad hacia atrás). `POV` combina el
  nombre desde `personajes.md`/`characters.md` (encabezado `## Nombre
  (POV...)`) y la persona/tiempo desde `voz.md` Parte 2. `POZOS_LEXICOS`
  desde "Registro léxico". `REGLAS_ESPECIFICAS` desde la subsección nueva
  `### Reglas específicas de capítulo` en `voz.md` Parte 2 (acepta también
  el nombre legado en inglés "Chapter-Specific Rules"; lista vacía si no
  existe, no rompe). Objetivo de palabras: `CALIBRACION["palabras_objetivo_capitulo"]`
  (2000 -- corregido en `deteccion_es.py` durante la Tarea 3, ver más
  abajo; el código de `draft_chapter.py` no cambió, ya leía el valor real
  en vez de hardcodear), no hardcodeado.
- **`ultimos_finales(n=3)`**: función nueva en `draft_chapter.py`. Lee el
  párrafo final de los últimos n capítulos ya escritos y se inyecta en el
  prompt con la instrucción de no repetir ese tipo de cierre. Reemplaza el
  antipatrón hardcodeado ("no termines con Cass escuchando a su padre").
  Vacía sin capítulos previos -- no rompe (probado).
- **Prompt completo en español** (system message + instrucciones de
  escritura + patrones a evitar): el modelo escribe en castellano, así que
  pedirle instrucciones en inglés aumentaba la probabilidad de calcos. El
  ítem sobre clichés de IA ahora referencia `CLICHES_FICCION` (español) en
  vez de frases en inglés.
- **Nomenclatura bilingüe**: `draft_chapter.py` (`ruta_bilingue()`/
  `load_file_bilingue()`) y `gen_brief.py` (`_ruta_bilingue()`) buscan
  primero `voz.md`/`personajes.md`/`mundo.md`/`esquema.md`, caen a los
  nombres en inglés si no existen. `canon.md` no cambia.
- **`gen_brief.py::extract_voice_rules()`**: ya no devuelve 7 reglas fijas
  (4 de *Bells*). Ahora parsea `voice.md`/`voz.md` Parte 1 (patrones
  estructurales reales) y Parte 2 (una regla por subsección con contenido
  real, ninguna para subsecciones vacías -- probado explícitamente con un
  `voice.md` a medio llenar, que es el estado normal durante varias
  iteraciones de fundación).
- **Bug propio corregido en el camino**: el helper `_seccion()` (usado en
  los dos archivos) rompía el anclaje `^...$` cuando el patrón de búsqueda
  tenía `|` sin agrupar -- buscar "Guardrails" hacía match con la palabra
  suelta del párrafo introductorio de `voice.md` en vez del encabezado
  `## Part 1`. Corregido envolviendo el patrón en `(?:...)`.
- **Aceptación verificada**: `grep -riE "cass|bell|bronze|under-note"
  draft_chapter.py gen_brief.py` → cero resultados. 24 tests en verde
  (`uv run python -m pytest tests/ -v`), incluyendo tests funcionales con
  `voz.md`/`personajes.md` inventados y el caso de sección vacía.
- **Corrección de registro**: `docs/BASELINE.md` decía que `voice.md`/
  `world.md`/`characters.md` eran los de *Bells* en inglés. Es falso --
  son plantillas, no contenido contaminado. (Esta corrección se corrigió
  otra vez en la Tarea 2b: están vacías no solo "porque son plantillas"
  sino porque el pipeline nunca pudo escribirlas -- ver Tarea 6 abajo.)

### Tarea 3 — Campo de ambición por capítulo (COMPLETA, commit `5af3cb9`)

- **`evaluate.py`**: `UMBRALES_AMBICION = {pico: 7.5, sosten: 6.5, valle:
  6.0}`. `extraer_ambicion()` lee el campo declarado en la entrada del
  esquema del capítulo (acepta `ambicion:`/`ambición:`, con o sin acento,
  formato YAML o bullet en negrita). `umbral_por_ambicion()` devuelve el
  umbral correspondiente -- **sin ambición declarada, cae a
  `UMBRAL_POR_DEFECTO_SIN_AMBICION` ("sosten", 6.5), nunca a "valle" (6.0,
  el más laxo)**. Esto se corrigió a mitad de tarea: el primer intento
  caía al umbral general (6.0, igual a "valle"), lo que habría hecho que
  cualquier esquema sin declarar ambición volviera en silencio al
  comportamiento que esta tarea vino a corregir. `evaluate_chapter()` ahora
  expone `ambicion`/`umbral_aceptacion`/`aceptado` en el resultado.
- **`validar_diversidad_ambicion()`**: dos formas de esquema plano, no una.
  (1) menos del 15% de capítulos son 'pico' (o ninguno declara ambición).
  (2) 80%+ de los picos declarados concentrados en el último tercio del
  esquema -- aunque la proporción total esté bien, si los momentos
  memorables se amontonan al final, el resto sigue siendo plano. Este
  segundo caso también se agregó a mitad de tarea, a pedido explícito del
  usuario (no estaba en mi primera implementación). Se llama desde
  `evaluate_foundation()`.
- **`run_pipeline.py`**: `run_drafting()` lee `umbral_aceptacion` del
  stdout de `evaluate.py` en vez de comparar contra `CHAPTER_THRESHOLD`
  fijo. Esa constante queda solo como último respaldo si `evaluate.py` no
  llega a calcular el umbral (capítulo vacío); subida a 6.5 por la misma
  razón que el default de arriba.
- **`gen_outline.py`** y **`outline.md`**: agregado el campo "Ambición:
  pico | sosten | valle" a la plantilla de salida por capítulo (edición
  mínima -- el resto de `gen_outline.py` sigue contaminado con Bells, ver
  Tarea 2b abajo).
- **Aceptación verificada, los 4 casos con test dedicado**: capítulo
  "pico" con score 7.0 → rechazado; el mismo "valle" → aceptado; esquema
  sin picos → advertencia; esquema con 80%+ de picos en el último tercio →
  advertencia. 38 tests en verde (`uv run python -m pytest tests/ -v`).
- **`gen_outline.py` contaminado con Bells → promovido a Tarea 2b**: no es
  un hallazgo aparte, es Tarea 2 incompleta (se le pasó al usuario en la
  auditoría original). Agregada como Tarea 2b en `ENCARGO_CLAUDE_CODE.md`,
  programada para después de la Tarea 4, mismo tratamiento que A1.
- **Objetivo de palabras corregido**: lo que se había registrado como
  "discrepancia sin resolver" (3800 en `deteccion_es.py` vs. 2000 en el
  encargo) era un error del propio `deteccion_es.py`, no una ambigüedad
  real. El usuario confirmó **2000** como valor correcto -- la novela pasó
  de ~22 capítulos de 3200-3800 palabras a ~45 capítulos de 2000 palabras
  (mismo largo total ~90-92k, más puntos de parada). Corregido en
  `deteccion_es.py` con nota explicando el porqué. `draft_chapter.py` no
  necesitó cambios, ya leía el valor dinámicamente.

### Tarea 4 — Alcance de siembra para series (COMPLETA, commit `506f435`)

- **`evaluate.py`**, sección nueva "Alcance de siembra": `validar_siembra(
  entrada, alcance_serie_disponible_, libros_completos=None)` implementa
  las 4 reglas exactas de la tabla del encargo sobre el esquema JSON del
  encargo (`id`/`siembra`/`pago`/`alcance`/`estado`). `alcance_serie_disponible()`
  chequea si existe `siembras_serie.md`. `validar_libro_de_siembras()` es
  la versión batch.
- **Regla de regresión**: sin `siembras_serie.md`, una entrada `alcance:
  serie` se valida como si fuera `alcance: libro` -- comportamiento
  idéntico al de antes de la tarea. Probado explícitamente.
- **`outline.md`** / **`gen_outline_part2.py`**: columna "Alcance"
  agregada a la tabla del Foreshadowing Ledger (edición mínima, mismo
  criterio que la ambición en la Tarea 3).
- **Decisión de diseño explícita, confirmada por el usuario**: los
  validadores operan sobre dicts ya estructurados, no parsean la tabla
  markdown real de `outline.md` (sigue siendo texto libre de LLM). La
  validación es la parte difícil y ya está probada; el parser depende de
  fijar el formato definitivo del ledger primero, y construir un parser
  confiable de una tabla generada por LLM es un problema aparte con
  riesgo real de bugs silenciosos. Documentado como gap en
  `docs/HALLAZGOS.md`.
- **`libros_completos` (regla 4) sin fuente de datos todavía**: hoy nadie
  llena ese parámetro. Según `AUDITORIA_Y_PLAN.md` B2/B7 vive en
  `estado_serie.json` (`{"libros_completos": [1], ...}`), que es parte de
  la Clase B (capa de serie completa) y **todavía no existe** en este
  repo -- ninguna tarea del encargo actual (0-4) lo crea. `validar_siembra()`
  ya está lista para recibirlo (`libros_completos=None` es un default
  razonable mientras tanto); cuando se construya `estado_serie.json`, el
  único cambio necesario es que el llamador le pase
  `set(estado_serie["libros_completos"])`. Documentado en HALLAZGOS.md.
- **Aceptación verificada, los 4 casos + regresión, cada uno con test
  dedicado**: 50 tests en verde (`uv run python -m pytest tests/ -v`).
- **`gen_outline_part2.py` también contaminado con Bells → sumado a la
  Tarea 2b** (confirmado por el usuario, junto con `gen_outline.py`).
  Además de la contaminación (capítulos 17-24 escritos a mano para la
  trama de Bells), tiene un **bug real independiente**: `part1 =
  open('/tmp/outline_output.md').read()` es una ruta absoluta hardcodeada
  fuera del repo -- con contenedores efímeros eso es una bomba de tiempo.
  La Tarea 2b en `ENCARGO_CLAUDE_CODE.md` ya incluye arreglarlo.

### Tarea 2b — Descontaminar `gen_outline.py`/`gen_outline_part2.py` (COMPLETA, commit `5a78c52`)

- **`gen_outline.py`**: prompt partido en armazón invariante (Save the
  Cat / MICE Quotient / Dan Harmon, formato por capítulo con Ambición y
  tabla de siembras con Alcance ya integradas) + contenido leído de
  `mundo.md`/`personajes.md`/`MISTERIO.md`/`semilla.txt` (bilingüe, mismo
  patrón que `draft_chapter.py`). KEY PLOT ARCHITECTURE y CONSTRAINTS ya
  no asumen personajes ni mecánicas específicas de Bells -- se derivan de
  los documentos cargados. Capítulos/palabras desde `CALIBRACION` (2000
  palabras/capítulo, ~46 capítulos calculados), no hardcodeado a
  "22-26 capítulos, ~80,000 palabras".
- **`gen_outline_part2.py`**: mismo tratamiento, más el fix del bug real:
  ya no lee `/tmp/outline_output.md` -- lee `esquema.md`/`outline.md` con
  el resolver bilingüe.
- **Efecto lateral necesario**: los dos scripts ahora **guardan** su
  resultado en `esquema.md`/`outline.md` (antes solo hacían
  `print(result)`, nada quedaba persistido). Arreglar el `/tmp` sin esto
  no alcanzaba -- seguía sin haber un archivo real del que
  `gen_outline_part2.py` pudiera leer.
- **Aceptación verificada**: `grep -riE "cass|bell|bronze|under-note|
  perin|maret|torvald|lenne|tonal" gen_outline.py gen_outline_part2.py` →
  cero. `grep -n "/tmp/" gen_outline_part2.py` → cero. 62 tests en verde
  (`uv run python -m pytest tests/ -v`), incluyendo tests funcionales con
  seed/mundo/personajes/MISTERIO inventados para los dos scripts.
- **Hallazgo mayor → formalizado como TAREA 6** (prioridad alta,
  confirmada por el usuario) en `ENCARGO_CLAUDE_CODE.md`: el mismo patrón
  "`print(result)` sin guardar" existe en `gen_world.py`,
  `gen_characters.py` y `gen_canon.py`, y `run_pipeline.py` tampoco
  captura su stdout. Tal como está, correr la fase de fundación completa
  **no dejaría nada escrito** en `world.md`/`characters.md`/`canon.md`,
  ni con `.env` configurado. Es la tarea con más impacto de todas las
  pendientes -- bloquea completar la fundación de cualquier novela nueva.
- **Corrección de registro (otra vez)**: `docs/BASELINE.md` y
  `docs/ESTADO.md` decían que `world.md`/`characters.md` estaban vacíos
  "porque son plantillas". Incompleto: están vacíos porque el pipeline
  nunca pudo escribirlos (ver Tarea 6). Corregido en los dos archivos.
- **Cuatro tokens de GitHub expuestos en el chat en total durante la
  sesión** (no durante la ejecución de las tareas en sí, sino en los
  intentos de push en paralelo) -- ver "Punto de partida" arriba. El push
  terminó al día: todo hasta `648b0c3` está en el remoto.

## Qué falta de la Tarea 1

- **1a** (parte no cubierta por 1c): flag `--idioma es|en` para que
  `evaluate.py` no quede hardcodeado a español. El encargo lo marca como
  opcional ("si complica mucho, priorizá que funcione el español") -- se
  priorizó español y esto quedó pendiente.
- **1b**: traducir los prompts del juez LLM a español en `evaluate.py`,
  `adversarial_edit.py`, `reader_panel.py`, `review.py`,
  `compare_chapters.py`, más el bloque de advertencias sobre normas
  castellanas (raya de diálogo, sujeto pronominal omitido, subordinación
  larga, +15-20% de extensión vs. inglés). **Bloqueado por falta de
  `.env`** -- no tiene sentido traducir y no poder probar contra el juez
  real.
- **1d, parte pendiente**: conectar `voz_minima_es.md`/`mundo_minimo_es.md`
  a una corrida real de `evaluate_chapter()`. Hoy `load_layer_files()` en
  `evaluate.py` tiene las rutas de `voice.md`/`world.md`/etc. hardcodeadas
  al directorio raíz -- parametrizarlas (o hacer que `--archivo` cargue un
  set alternativo de capa) es trabajo aparte, y de todos modos requiere
  `.env` para ejecutarse.
- El **`overall_score`** completo de `evaluate.py` (juez LLM + mecánico)
  sobre los dos fixtures sigue **PENDIENTE** en `docs/BASELINE.md`.

## Qué sigue

Las Tareas 0, 1c, 1d, 2, 2b, 3 y 4 están completas. Lo que queda:

- **Tarea 6 — Persistencia de la fase de fundación (prioridad alta,
  NO depende de `.env`).** `gen_world.py`, `gen_characters.py` y
  `gen_canon.py` tienen el mismo bug que tenían `gen_outline.py`/
  `gen_outline_part2.py` antes de la Tarea 2b: terminan con
  `print(result)` y no guardan nada. `run_pipeline.py` tampoco lo
  compensa. Ver detalle completo en `ENCARGO_CLAUDE_CODE.md` (sección
  TAREA 6) y en `docs/HALLAZGOS.md`. **Es la única tarea que queda sin
  bloquear por `.env` -- candidata natural para la próxima sesión sin
  API key.**
- **1a** (flag `--idioma es|en`), **1b** (prompts del juez en español),
  **1d** (conectar los fixtures de voz/mundo a una corrida real), y
  completar el `overall_score` en `docs/BASELINE.md`: todo bloqueado por
  falta de `.env`.

## Cómo retomar

1. Verificar qué falta pushear: `git log origin/framework/es-multilibro..HEAD
   --oneline`. Si hay algo, pushear con un token nuevo, exportado como
   variable de entorno, nunca pegado en el chat.
2. Si se retoma sin `.env` todavía: **Tarea 6** es la única que queda sin
   depender de la API key.
3. Cuando haya `.env` con `ANTHROPIC_API_KEY`: correr `evaluate.py
   --chapter` (sin `--solo-mecanico`) sobre los fixtures para completar
   el `overall_score` pendiente en `docs/BASELINE.md`, y recién ahí
   arrancar la Tarea 1b. Después de la Tarea 6, con `.env` disponible, se
   podría intentar correr `run_pipeline.py --phase foundation` de punta a
   punta por primera vez.
