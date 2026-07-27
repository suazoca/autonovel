# ESTADO — rama `framework/es-multilibro`

Última actualización: 2026-07-27 (tras cerrar la Tarea 2). Escrito para
retomar en otra sesión sin releer todo el historial de commits.

## Punto de partida que sigue vigente

- **No existe `.env`** en este entorno (ni `ANTHROPIC_API_KEY`). Nada que
  dependa del juez LLM se puede probar hasta que exista.
- **No existe la rama `autonovel/bells`** en este remoto (confirmado con
  `git fetch --all` + `git ls-remote --heads origin`). No hay comparación
  disponible contra la novela anterior en inglés; toda la línea base se
  armó con fixtures de prueba en español, no con capítulos reales.
- **Los commits de esta rama están solo en local, sin pushear.** Se
  intentó `git push` y un token de GitHub quedó expuesto por accidente en
  el chat durante el intento (pegado mal en la terminal). El usuario lo
  revocó de inmediato. El push queda pendiente para la próxima sesión, con
  un token nuevo y cuidado de no volver a pegarlo en el chat -- pasarlo
  solo como variable de entorno ya exportada en la terminal del usuario.

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
  (2000), no hardcodeado.
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
  son plantillas vacías (Parte 2 sin llenar), no contenido contaminado.
  Corregido en `docs/BASELINE.md` durante esta tarea.

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

## Qué sigue (Tareas 3 y 4 del encargo, sin empezar)

Ver `ENCARGO_CLAUDE_CODE.md` para el detalle completo de cada una. La
Tarea 2 ya está completa (ver arriba).

- **Tarea 3 — Campo de ambición por capítulo.** Cada capítulo del esquema
  declara `ambicion: pico | sosten | valle` con umbral propio (7.5 / 6.5 /
  6.0) en vez de un umbral único de 6.0. Toca `gen_outline.py`,
  `evaluate.py` (el umbral de aceptación deja de ser una constante
  global) y `run_pipeline.py`. Incluye validación: esquema con <15% de
  picos debe advertir. No depende de `.env` para la lógica del umbral,
  aunque `evaluate.py` sigue necesitando la API para el resto. **En curso
  ahora mismo, siguiente después de este ESTADO.md.**
- **Tarea 4 — Alcance de siembra (serie).** El libro de siembras hoy
  exige que todo se pague dentro del mismo volumen; para una serie hace
  falta `alcance: "libro" | "serie"` con las 4 reglas de validación de la
  tabla del encargo, más `siembras_serie.md` en la rama de serie (si no
  existe, todo es alcance de libro -- comportamiento actual sin cambios).
  Toca `gen_outline_part2.py`. Tampoco depende de `.env`.

Ninguna de las dos está bloqueada por la falta de `.env` -- son las
candidatas naturales mientras no haya API key.

## Cómo retomar

1. Cuando haya `.env` con `ANTHROPIC_API_KEY`: correr `evaluate.py
   --chapter` (sin `--solo-mecanico`) sobre los fixtures para completar
   el `overall_score` pendiente en `docs/BASELINE.md`, y recién ahí
   arrancar la Tarea 1b.
2. Push pendiente: `git push origin framework/es-multilibro` (o a la URL
   con token, nunca pegado en el chat -- solo como variable de entorno ya
   exportada).
3. Si se retoma sin `.env` todavía, la Tarea 3 (en curso) o la Tarea 4 son
   las que se pueden avanzar.
