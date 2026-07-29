# TRASPASO — rama `novela2`

Estado real al cierre de la sesión del 2026-07-29 (mañana). Reemplaza la
necesidad de releer `ESTADO.md` completo o el historial de commits: es la
foto actual, no la bitácora.

Para el estado del **framework** (Tareas 0–6, cerradas en
`framework/es-multilibro`), ver la sección "Herencia del framework" al
final. Esta rama es un worktree de esa.

## En una línea

La fundación de *La ostensión* está completa y aprobada, el capítulo 1
está escrito y leído (aprobado), y las Tareas 8 y 9b del framework —
streaming centralizado y continuación automática por truncamiento — están
resueltas y probadas contra la API real. Falta decidir cuánto automatizar
antes de seguir redactando.

## Estado del repositorio

| | |
|---|---|
| Rama | `novela2` (worktree de `framework/es-multilibro`) |
| Push | Al día con `origin/novela2` |
| Working tree | Limpio salvo `chapters/ch_01.md`, sin commitear |
| Merge pendiente | Las Tareas 8 y 9b viven **solo en `novela2`**; hay que mergearlas hacia `framework/es-multilibro` |

## Fundación de *La ostensión* — completa

| Documento | Estado |
|---|---|
| `voice.md` Parte 2 | Generada desde la semilla, aprobada |
| `world.md` | Completo. **Ojo:** una regeneración falló y trajo nombres incorrectos (Lascaris/Betser en vez de Sandoz/Basilea); el bueno se recuperó de git y está commiteado |
| `characters.md` | Vidal, Sandoz, Chiara y Ferrero completos. Ledda, Ansermet y Ceruti marcados como "ficha pendiente de generación": existen en el esquema por función, no tienen ficha propia |
| `outline.md` | 46 capítulos, Save the Cat + MICE anidado, título de trabajo *La ostensión* |
| `canon.md` | Regenerado sobre los documentos completos |
| `chapters/ch_01.md` | Escrito y leído. Aprobado: la voz se sostiene, el diálogo distingue personajes sin etiquetas, calidad a la altura del esquema. **Sin commitear** |

## Bugs del framework arreglados hoy (commiteados en `novela2`)

| # | Qué | Commit |
|---|---|---|
| 1 | `temperature` está deprecado en Fable 5 y devuelve 400 — quitado de los 19 scripts | `TODO` |
| 2 | Los bloques `['thinking','text']` rompían `content[0]["text"]` | `TODO` |
| 3 | La plantilla de voz tenía prosa fuera del comentario HTML, lo que hacía fallar la guardia de idempotencia **en silencio** | `TODO` |
| 4 | Tarea 8: streaming centralizado en `api_comun.py`, reemplaza el timeout fijo bloqueante | `TODO` |
| 5 | Tarea 9b: continuación automática cuando se trunca por `max_tokens` | `TODO` |

Notas sobre la Tarea 9b, que costó más de lo previsto:

- El primer diseño (prefill de turno de assistant) lo rechazó Fable 5 con
  400. Se corrigió a un **turno de usuario explícito** pidiendo continuar,
  con recorte del solapamiento en la juntura.
- Probada contra la API real, no solo contra mocks.
- De paso destapó que `stop_reason == "refusal"` no se manejaba: devolvía
  texto truncado como si estuviera completo. También arreglado.

## Pendiente

Ordenado por lo que cuesta más si se posterga, no por número de tarea.

- **Tarea 10 — acumulación de canon durante la redacción**
  (`new_canon_entries` → `canon.md`). `draft_chapter.py` solo ve la cola
  del capítulo anterior más las entradas de outline del actual y el
  siguiente: `canon.md` es la única memoria larga del sistema. Cada
  capítulo redactado sin la Tarea 10 es deuda a reconstruir leyendo el
  manuscrito, y son justamente los hilos que cruzan 30+ capítulos los que
  se rompen ahí.
- **Tarea 11** — punto de aprobación manual por capítulo en
  `run_pipeline.py`.
- **Fichas completas** de Ledda, Ansermet y Ceruti. Si aparecen en
  capítulos redactados antes de tener ficha, el modelo les inventa
  rasgos, y sin la Tarea 10 esos rasgos no vuelven a ninguna parte.
- **Merge de las Tareas 8–9b** hacia `framework/es-multilibro`.

## Cómo retomar

1. `git add chapters/ch_01.md && git commit -m "Cap. 1: Intervalo"`.
2. `git status` y `git log origin/novela2..HEAD --oneline` para confirmar
   que no quedó nada sin pushear.
3. Decidir el orden: Tarea 10 primero (memoria larga), Tarea 11 primero
   (supervisión liviana), o 2–3 capítulos más a mano
   (`draft_chapter.py N`) para juntar datos antes de automatizar.
4. Advertencia sobre "leer un capítulo de Fun and Games y uno del Acto
   III" antes de decidir: sacados sueltos, esos capítulos se redactan sin
   `prev_tail` (el capítulo anterior no existe todavía), así que no son
   representativos de la corrida real. Sirven para ver si la voz aguanta
   otro registro; no dicen nada sobre cómo se comporta la cadena.

## Herencia del framework (`framework/es-multilibro`)

Tareas 0, 1c, 1d, 2, 2b, 2c, 3, 4 y 6 cerradas y testeadas (101 tests en
verde, ninguno requiere `.env`). Hallazgos abiertos que siguen vigentes:
sesgo de `dividir_oraciones()`, `umbral_cv_oracion` sin recalibrar, falta
de parser del Foreshadowing Ledger, `libros_completos` sin fuente de
datos, y `CRAFT.md` cargado pero no interpolado en `gen_world.py` /
`gen_characters.py`. Detalle completo en el TRASPASO anterior y en
`docs/HALLAZGOS.md`.

**Token de GitHub:** fine-grained, creado 2026-07-27, alcance
`suazoca/autonovel`, `Contents: read/write`, **vence ~2026-08-26**. Al
vencer, limpiar la credencial guardada con `git credential reject`
(protocol=https, host=github.com) antes de autenticar con uno nuevo.
