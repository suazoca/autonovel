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
directorio raíz.

**Corrección sobre lo que decía acá antes:** esta sección afirmaba que esos
archivos "siguen siendo los de Bells (en inglés)". Es falso -- se verificó
al trabajar la Tarea 2 y son **plantillas vacías** (Parte 2 de `voice.md`
son puros comentarios HTML sin llenar, `world.md`/`characters.md`/
`canon.md` son solo encabezados con ejemplos genéricos entre comentarios,
sin una sola referencia a Bells). El problema real no es contaminación de
*Bells*, es que están **vacíos**: evaluar un capítulo contra un `voice.md`
sin Parte 2 rellenada no mide nada (no hay tono, registro ni ejemplares
contra qué comparar). Por eso la Tarea 1d creó fixtures mínimos
(`tests/fixtures/voz_minima_es.md`, `mundo_minimo_es.md`) en vez de asumir
que hacía falta "limpiar" contenido en inglés que en realidad no existe.

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

## Hallazgos durante la preparación

Al armar `tests/test_deteccion_es.py` con los 6 casos de aceptación de la
Tarea 1 aparecieron dos cosas para revisar en `deteccion_es.py`:

1. **`calcos_detectados()` era sensible a mayúsculas** (no usaba
   `re.IGNORECASE`) — el ejemplo del encargo,
   `calcos_detectados("Levantó su mano. Estaba siendo observada.")`, daba 0
   hallazgos en vez de 2. Era un bug real. **Corregido** en el commit
   `214768e` (`fix: IGNORECASE en calcos_detectados + corrección del test 6`).
2. El caso 6 del encargo, `dividir_oraciones("¿Viniste? Sí. El Sr. Pérez no
   vino.")` esperando 3 oraciones, estaba **mal escrito**: `dividir_oraciones()`
   descarta por diseño las oraciones de ≤2 palabras, así que "¿Viniste?" y
   "Sí." nunca iban a contar. No era un bug del módulo. El test se
   reemplazó por un caso que sí verifica lo que importa (no cortar en
   "Sr."), y el efecto secundario real de ese filtro (sesga el CV de
   longitud de oración hacia arriba) quedó documentado en
   `docs/HALLAZGOS.md` sin tocar el código, a pedido explícito.

## Tarea 1c — `--solo-mecanico`: antes y después de integrar deteccion_es.py

`evaluate.py --chapter=N` (o `--full`) siempre llama al juez LLM, así que
no servía para medir el efecto del arreglo de la raya sin gastar API y sin
quedar sujeto a la variabilidad del juez. Se agregó `--solo-mecanico`
(+ `--archivo <path>` para apuntar a un archivo fuera de `chapters/`), que
corre únicamente `slop_score()` -- determinista, sin red, sin API key.

**ANTES** (commit del flag, `slop_score()` todavía con las listas en
inglés del repositorio original):

| Métrica | `cap_dialogado_es.md` (limpio) | `cap_con_slop_es.md` (sembrado) |
|---|---|---|
| `em_dash_density` | 72.12 | 1.7 |
| `sentence_length_cv` | 0.686 | 0.591 |
| `slop_penalty` | **1.0** | **0.0** |

Confirma el problema exacto que motivó la Tarea 1: el capítulo **limpio**
paga penalización por usar la raya de diálogo correctamente (72.12 rayas
por mil palabras según el contador en inglés, que no distingue diálogo de
inciso parentético), mientras el capítulo **con slop sembrado a propósito**
sale con penalización 0, porque ninguna lista en inglés reconoce clichés,
calcos o adverbios en -mente del español. El evaluador mecánico está,
literalmente, al revés de lo que debería premiar.

**DESPUÉS** (integradas las listas ES + calcos de `deteccion_es.py` en
`slop_score()`):

| Métrica | `cap_dialogado_es.md` (limpio) | `cap_con_slop_es.md` (sembrado) |
|---|---|---|
| `em_dash_density` (raya parentética) | 1.6 | 1.7 |
| `sentence_length_cv` | 0.686 | 0.591 |
| `calco_hits` | 0 | 2 |
| `fiction_ai_tells` | 0 | 3 |
| `slop_penalty` | **0.0** | **2.9** |

El delta que importa: `cap_dialogado_es.md` pasa de penalización **1.0 → 0.0**
(dejó de pagar por usar la raya de diálogo correctamente: `em_dash_density`
72.12 → 1.6, muy por debajo del umbral 6.0). `cap_con_slop_es.md` pasa de
**0.0 → 2.9** (ahora sí detecta los 3 clichés, los 2 calcos y el
"no solo…sino que" sembrados). El capítulo limpio quedó mejor que el
sembrado, que es justamente lo que la Tarea 1 pedía arreglar.
