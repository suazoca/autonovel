# ESTADO — rama `framework/es-multilibro`

Última actualización: 2026-07-27 (tras cerrar la Tarea 6). Escrito para
retomar en otra sesión sin releer todo el historial de commits.

**Nota:** `AUDITORIA_Y_PLAN.md` se movió a `docs/AUDITORIA_Y_PLAN.md` en un
commit hecho directamente por el usuario (`48395a8`, fuera de esta
conversación). Las referencias a `AUDITORIA_Y_PLAN.md` sin prefijo en
commits anteriores de este archivo quedan desactualizadas de ruta; no se
corrigieron retroactivamente.

## Punto de partida que sigue vigente

- **No existe `.env`** en este entorno (ni `ANTHROPIC_API_KEY`). Nada que
  dependa del juez LLM se puede probar hasta que exista.
- **No existe la rama `autonovel/bells`** en este remoto (confirmado con
  `git fetch --all` + `git ls-remote --heads origin`). No hay comparación
  disponible contra la novela anterior en inglés; toda la línea base se
  armó con fixtures de prueba en español, no con capítulos reales.
- **Push: al día hasta `48395a8`** (incluye un commit del usuario hecho
  directamente, fuera de esta conversación: mover `AUDITORIA_Y_PLAN.md` a
  `docs/`). El commit de la Tarea 6 que sigue a este documento **todavía
  no está pusheado** al momento de escribir esto -- confirmar con
  `git log origin/framework/es-multilibro..HEAD --oneline`.
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
c513adf docs: ESTADO.md al día con el cierre de la Tarea 4
5a78c52 Tarea 2b: descontamina gen_outline.py y gen_outline_part2.py
648b0c3 docs: ESTADO.md al día con el cierre de la Tarea 2b
2b31156 docs: TRASPASO.md -- estado real para retomar sin releer ESTADO.md completo
b18ca4a docs: corrige el conteo de tokens expuestos (cuatro, no dos) y el estado del push
48395a8 docs: mueve AUDITORIA_Y_PLAN.md a docs/                          <- del usuario, no de esta conversación; pusheado hasta acá
                                                                          <- Tarea 6 sigue, sin pushear al escribir esto
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

### Tarea 6 — Persistencia en la fase de fundación (COMPLETA, prioridad alta)

**Importante: este commit NO descontamina prompts.** Los nombres de la
novela anterior (Cass, Perin, Maret, Cantamura, Tonal Law, etc.) siguen
intactos en `gen_world.py`, `gen_characters.py` y `gen_canon.py` -- eso
queda para una **Tarea 2c**, todavía sin formalizar en
`ENCARGO_CLAUDE_CODE.md` (solo anotada como hallazgo). La Tarea 6 fue
estrictamente sobre persistencia: que los generadores se guarden a sí
mismos y que `run_pipeline.py` no ignore sus fallos.

- **`fundacion_comun.py` (módulo nuevo)**: `load_file()`, `ruta_bilingue()`,
  `load_file_bilingue()`, `extraer_voz_parte2()` y `exigir_semilla()`,
  compartidas por los cinco generadores de fundación en vez de duplicadas.
  `ruta_bilingue()`/`load_file_bilingue()` toman `base_dir` como parámetro
  explícito (no un global del módulo) -- se puede testear pasando un
  `tmp_path` directo, sin monkeypatch.
- **`gen_world.py`, `gen_characters.py`, `gen_canon.py`**: reescritos
  siguiendo exactamente el patrón de `gen_outline.py` (Tarea 2b) -- todo
  dentro de `main()`, guardia `if __name__ == "__main__":`, sin código a
  nivel de módulo que dispare la API al importar. Arreglado también el
  bug de `next(i for i, l in ... if 'Part 2' in l)` (`StopIteration` si no
  había esa línea, y no reconocía "Parte 2") -- ahora usan
  `extraer_voz_parte2()`. Guardan en:
  - `gen_world.py` → `mundo.md`/`world.md`
  - `gen_characters.py` → `personajes.md`/`characters.md`
  - `gen_canon.py` → `canon.md` (**reescribe entero, no acumula** --
    corrección sobre una versión anterior de `ENCARGO_CLAUDE_CODE.md` que
    decía lo contrario: canon en fundación es derivado de
    semilla+mundo+personajes, sin hechos propios, y el descarte de
    iteración ya lo hace `git reset --hard`. Acumular arrastraría hechos
    de un mundo descartado.)
- **`gen_outline.py` también recibió el guard de semilla vacía** (ya
  existía como archivo de la Tarea 2b, no estaba en el pedido original de
  "los tres", pero consume la semilla igual que los otros -- dejarlo
  como la única excepción sin guard habría sido raro). El guard es
  **una sola función compartida** (`exigir_semilla()` en
  `fundacion_comun.py`), no una cuarta/quinta copia.
  **`gen_outline_part2.py` NO lo recibió**: no carga
  `seed.txt`/`semilla.txt` en absoluto, no le corresponde.
- **`run_pipeline.py::run_foundation()`**:
  - `run_generator(script, state, timeout)`: si el generador falla
    (returncode != 0), **guarda `state` con `save_state()` antes de
    salir** (para poder retomar desde la iteración en curso, no desde
    cero) y aborta **todo el pipeline** con `sys.exit(1)` -- no solo la
    iteración. Decisión corregida a mitad de tarea: la primera versión
    solo abortaba la iteración y dejaba que el loop reintentara hasta
    `MAX_FOUNDATION_ITERS`; el usuario corrigió que un returncode != 0 es
    un fallo de infraestructura (API, archivo faltante), no de calidad, y
    reintentar sobre el mismo estado roto no lo arregla -- la iteración
    es la unidad de reintento para puntaje bajo, no para scripts rotos.
    Imprime el script que falló, su returncode, y su **stderr completo**
    (no truncado) antes de salir.
  - Envuelve **los cinco generadores + `voice_fingerprint.py`** con
    `run_generator()` -- `voice_fingerprint.py` no estaba en el pedido
    original, pero es el mismo loop de fundación: un returncode ignorado
    ahí es el mismo bug que se está arreglando en los otros pasos.
    (Corrección: `voice_fingerprint.py` NO genera nada de `voice.md` --
    es un medidor que analiza capítulos ya escritos y guarda
    `edit_logs/voice_fingerprint.json`, que ni siquiera se versiona
    -`edit_logs/` está en `.gitignore`. Ver el hallazgo nuevo de abajo:
    nada en el repo genera la Parte 2 de `voice.md`.)
  - `verificar_archivos_fundacion(desde)`: antes de llamar a
    `evaluate.py --phase=foundation`, confirma que
    `mundo.md`/`personajes.md`/`esquema.md`/`canon.md` **se modificaron en
    esta iteración** (mtime posterior a `desde`, un timestamp tomado al
    empezar la iteración) y no están vacíos. Corregido a mitad de tarea:
    el primer intento solo chequeaba "existe y no está vacío", pero
    `world.md`/`characters.md`/`outline.md` están trackeados en git como
    plantillas con contenido real (encabezados + comentarios HTML) --
    ese chequeo por sí solo daría verde contra el andamio sin tocar,
    aunque ningún generador hubiera corrido de verdad esta vuelta. El
    chequeo de contenido no vacío se mantiene ADEMÁS del de mtime, no en
    su lugar: un generador puede devolver 0 y haber escrito una respuesta
    vacía de la API sin que `run_generator()` lo detecte (no hay
    excepción de por medio). Si falta algo, también guarda `state` y
    aborta -- una fundación incompleta no debe producir un puntaje que
    entre a `results.tsv`.
- **Aceptación verificada**: 91 tests en verde
  (`uv run python -m pytest tests/ -v`), incluyendo import sin llamadas a
  `httpx.post`, `main()` con `call_writer` parcheado escribiendo en el
  archivo esperado, resolución bilingüe, los guards de semilla vacía, y
  `run_generator()`/`verificar_archivos_fundacion()` con `uv_run()`
  parcheado (nada de esto toca la API).
- **Hallazgos nuevos, sin corregir** (`docs/HALLAZGOS.md`):
  1. `gen_world.py`/`gen_characters.py`/`gen_canon.py` siguen contaminados
     con *Bells* en el contenido de sus prompts (no tocado a pedido
     explícito) -- candidato a **Tarea 2c**, sin formalizar todavía.
  2. No hay ningún mecanismo que devuelva al canon los hechos que los
     capítulos establecen durante la redacción (un nombre de calle
     mencionado al pasar, la edad de un personaje secundario revelada más
     tarde). `PIPELINE.md` da por sentado que esto pasa
     ("Extract new canon entries from eval output → append to canon.md")
     pero no existe el script. Distinto del punto de `gen_canon.py` de
     arriba: esto es acumulación en la fase de **redacción**, no en
     fundación, necesitaría un script propio, y depende de la misma
     decisión de diseño pendiente que el hallazgo de los validadores de
     siembra (Tarea 4): qué tan estructurado tiene que ser `canon.md`
     para que un script pueda leerlo y escribirle de vuelta con
     confianza.
  3. **Nada genera la Parte 2 de `voice.md`/`voz.md`** -- prioridad alta,
     hermano de la Tarea 6 (no la misma: acá no hay un script roto, no
     existe el script). Confirmado con grep: no hay `gen_voice.py`,
     `run_foundation()` no tiene ese paso, y ningún `write_text` en el
     repo apunta a `voice.md`/`voz.md`. `PIPELINE.md` (Fase 1, paso 5)
     documenta "voice discovery" como si existiera. `draft_chapter.py`,
     `gen_brief.py` y `gen_outline.py` leen esa sección esperando
     contenido real; hoy son comentarios HTML vacíos. El pipeline
     redactaría con identidad de voz vacía. Diagnosticado sin `.env`;
     escribir el script (mismo patrón que el resto de la Tarea 6) tampoco
     lo necesitaría, pero validar la calidad de lo que generaría sí.

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

Las Tareas 0, 1c, 1d, 2, 2b, 3, 4 y 6 están completas.

**Se puede seguir escribiendo y testeando código sin `.env`** -- todo lo
de esta sesión (Tareas 2, 2b, 3, 4, 6) se construyó y probó así, con
`call_writer()`/`uv_run()` parcheados. Lo que sin `.env` **no** se puede
hacer es correr una generación real ni ver si el resultado tiene calidad.

- **Sin `.env`, se puede avanzar en escribir código para:**
  - **Tarea 2c (sin formalizar)** -- descontaminar `gen_world.py`,
    `gen_characters.py` y `gen_canon.py` de Bells. Mismo tratamiento y
    mismo patrón de tests con mocks que la Tarea 2b.
  - **El generador de voz que falta** (hallazgo nuevo arriba, prioridad
    alta) -- escribir el script (`gen_voice.py` o similar) que llene
    `voice.md`/`voz.md` Parte 2, con el mismo patrón `main()` +
    `fundacion_comun.py` + tests con `call_writer` parcheado.
  - El script que acumule al canon los hechos de redacción, y el parser
    del Foreshadowing Ledger (Tarea 4) -- ambos esperan primero fijar el
    formato estructurado de esos documentos, que es una decisión de
    diseño, no algo que necesite la API.
- **Bloqueado por `.env` -- no hay código nuevo que escribir, hace falta
  correr contra el modelo real:**
  - Validar que el generador de voz (una vez escrito) produce pasajes de
    calidad real -- eso es juicio, no algo mockeable con sentido.
  - **1a** (flag `--idioma es|en`), **1b** (prompts del juez en español,
    validados contra el juez real), **1d parte final** (conectar los
    fixtures de voz/mundo a una corrida real de `evaluate_chapter()`).
  - Completar el `overall_score` de los fixtures de la Tarea 0 en
    `docs/BASELINE.md`.
  - Intentar `run_pipeline.py --phase foundation` de punta a punta por
    primera vez.

## Cómo retomar

1. Verificar qué falta pushear: `git log origin/framework/es-multilibro..HEAD
   --oneline`. Si hay algo, pushear con un token nuevo, exportado como
   variable de entorno, nunca pegado en el chat.
2. Si no hay `.env` todavía, hay tres frentes para escribir código (ver
   "Qué sigue"): formalizar y ejecutar la **Tarea 2c**, escribir el
   **generador de voz que falta** (hallazgo nuevo, prioridad alta), o
   avanzar el diseño de formato de `canon.md`/Foreshadowing Ledger.
3. Cuando haya `.env` con `ANTHROPIC_API_KEY`:
   a. Correr `evaluate.py --chapter` (sin `--solo-mecanico`) sobre los
      fixtures para completar el `overall_score` pendiente en
      `docs/BASELINE.md`.
   b. Arrancar la Tarea 1b.
   c. Con la Tarea 6 ya resuelta, se puede intentar
      `run_pipeline.py --phase foundation` de punta a punta por primera
      vez (con un `seed.txt`/`semilla.txt` real).
