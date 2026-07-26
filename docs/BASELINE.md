# BASELINE — Tarea 0

**Fecha:** 2026-07-27
**Commit base:** `3ded223185070a05f0b829581c4b60d00cd2a6fc` (rama `framework/es-multilibro`)

## Nota sobre alcance

El encargo original pedía elegir tres capítulos existentes de la novela
anterior (*The Second Son of the House of Bells*) y evaluarlos como parte
de la línea base. **La rama `autonovel/bells` no existe** en este remoto:
se corrió `git fetch --all` y se revisaron ramas locales, remotas y
`git ls-remote --heads origin` sin encontrarla. El README la menciona pero
nunca se subió a este repositorio.

**Por lo tanto: no hay comparación disponible contra la novela en inglés.**
La línea base se arma únicamente con los dos capítulos de prueba en español
que pide la Tarea 0.

## Fixtures creados

- `tests/fixtures/cap_dialogado_es.md` — 624 palabras, mayormente diálogo
  con raya, prosa limpia, sin muletillas ni clichés.
- `tests/fixtures/cap_con_slop_es.md` — 587 palabras, narrativo, con slop
  sembrado a propósito.

## Puntajes mecánicos (sin LLM — `deteccion_es.py`, corridos de forma aislada)

| Métrica | `cap_dialogado_es.md` | `cap_con_slop_es.md` |
|---|---|---|
| Palabras | 624 | 587 |
| Raya parentética / mil palabras | 1.6 | 1.7 |
| CV longitud de oración | 0.686 | 0.591 |
| Calcos del inglés detectados | 0 | 2 (posesivo calcado en parte del cuerpo; «estar siendo») |
| Clichés de ficción detectados | 0 | 3 |
| «no solo…, sino que» | no | sí |
| Adverbios emocionales en -mente | 0 | 2 (nerviosamente, tristemente) |

Estos números confirman que los fixtures están sembrados correctamente
para lo que pide la Tarea 1, pero **no son el puntaje del evaluador**:
`evaluate.py` combina esto con un juicio LLM (`slop_score()` ajusta el
`overall_score` del juez, no lo reemplaza).

## Puntajes de `evaluate.py` (juez LLM + mecánico combinado)

**PENDIENTE.** No existe `.env` con `ANTHROPIC_API_KEY` en este entorno, y
`evaluate.py` llama a la API de Anthropic (`call_judge()` vía `httpx`) en
todos sus modos (`--phase`, `--chapter`, `--full`) — no hay forma de correr
solo la parte mecánica desde el CLI. Además, `evaluate_chapter()` lee
`voice.md`, `world.md`, `characters.md`, `outline.md`, `canon.md` del
directorio raíz, que hoy siguen siendo los de *Bells* (en inglés) porque
todavía no se hizo la fundación en español — evaluar los fixtures tal cual
compararía prosa española contra una biblia de voz en inglés, lo cual
sesgaría el resultado.

Para completar esta sección hace falta, en este orden:
1. Cargar `ANTHROPIC_API_KEY` en `.env`.
2. Decidir contra qué `voice.md`/`world.md` evaluar los fixtures (¿unos de
   prueba neutros, o esperar a la fundación real?) — no improvisado acá,
   a confirmar con el usuario.
3. Correr `evaluate.py` y volcar los 2 puntajes que faltan.

Cuando eso pase, esta tabla se completa:

| Capítulo | `overall_score` (evaluate.py) |
|---|---|
| `cap_dialogado_es.md` | PENDIENTE |
| `cap_con_slop_es.md` | PENDIENTE |

## Hallazgos durante la preparación (no corregidos — fuera de alcance de Tarea 0)

Al armar `tests/test_deteccion_es.py` con los 6 casos de aceptación de la
Tarea 1 se encontraron dos bugs reales en `deteccion_es.py`, confirmados
con pytest (ver commit de Tarea 0):

1. **`calcos_detectados()` es sensible a mayúsculas** (no usa
   `re.IGNORECASE`). El propio ejemplo del encargo,
   `calcos_detectados("Levantó su mano. Estaba siendo observada.")`,
   devuelve 0 hallazgos en vez de 2, porque los patrones están escritos en
   minúscula y las palabras están capitalizadas por ir al inicio de
   oración.
2. **`dividir_oraciones()` descarta oraciones de 2 palabras o menos**
   (filtro `len(limpia.split()) > 2`). El ejemplo del encargo,
   `dividir_oraciones("¿Viniste? Sí. El Sr. Pérez no vino.")`, devuelve 1
   oración en vez de 3: pierde "¿Viniste?" y "Sí." enteras. Esto también
   afecta `cv_longitud_oracion()`, que subestima la variación real al
   ignorar todas las oraciones cortas.

Ambos quedan documentados como tests que fallan a propósito en
`tests/test_deteccion_es.py` (con el motivo en el docstring), listos para
que Tarea 1 los arregle y los deje en verde.
