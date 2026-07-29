# TRASPASO — rama `novela2` (worktree de `framework/es-multilibro`)

Estado real al cierre de esta sesión (2026-07-29). Este documento
reemplaza la necesidad de releer `ESTADO.md` completo o el historial de
commits para retomar el trabajo -- es la foto actual, no la bitácora
(para eso está `ESTADO.md`, que sí es narrativo y ahora tiene una
sección nueva para esta rama).

## Qué es esta rama

`novela2` es un **worktree separado** (`git worktree list` lo confirma:
`/root/novela2` en la rama `novela2`, junto a `/root/autonovel` en
`novela-es` -- otro libro, no tocar desde acá) que arrancó desde
`framework/es-multilibro` en el commit de cierre de la Tarea 7
(`7b81700`). A partir de ahí dejó de ser trabajo sobre el framework en
sí y pasó a ser la escritura de una novela concreta con ese framework:
**"La ostensión"** (Libro 1), a partir de `semilla.txt` -- un científico
de IA investigando la Sábana Santa antes de la ostensión de 2033.

El framework en sí (Tareas 0-7, `ENCARGO_CLAUDE_CODE.md`) sigue viviendo
en `framework/es-multilibro`; lo que se agregó en esta rama después de
divergir (Tareas 8, 9, 9b -- ver abajo) todavía **no se mergeó de
vuelta**.

## En una línea

Fundación completa y revisada (voz, mundo, personajes, esquema de 46
capítulos, canon), Cap. 1 escrito y aprobado, y el cliente de API
(`api_comun.py`) reparado y probado contra la API real tras varios
choques con reglas específicas de Fable 5 que `framework/es-multilibro`
nunca conoció -- esa rama nunca corrió contra la API real.

## Estado del repositorio

| | |
|---|---|
| Directorio | `/root/novela2` (worktree; confirmado con `git worktree list`) |
| Rama | `novela2`, diverge de `framework/es-multilibro` en `7b81700` (Tarea 7) |
| `.env` / `ANTHROPIC_API_KEY` | **Presente en este entorno** (a diferencia de `framework/es-multilibro`, donde nunca existió). `AUTONOVEL_WRITER_MODEL=claude-fable-5`, `AUTONOVEL_JUDGE_MODEL=claude-opus-5`, `AUTONOVEL_REVIEW_MODEL=claude-opus-5`, `AUTONOVEL_API_BASE_URL=https://api.anthropic.com` |
| Push | `origin/novela2` quedó **4 commits atrás de `HEAD`** al cierre de esta sesión: `dde01c4`, `6f110dc`, `aa8efd1`, `84618e8` (los primeros tres no son de esta sesión; `84618e8` sí). Confirmar con `git log origin/novela2..HEAD --oneline`. |
| Working tree | **No está limpio.** `canon.md` tiene cambios sin commitear, de antes de esta sesión -- no se tocaron. Hay un archivo sin trackear, `world.md.regenerado`, que parece una regeneración alternativa de `world.md` sin resolver -- tampoco se tocó ni se investigó a fondo. Ambos quedan para quien retome. |
| Tests | `uv run python -m pytest tests/ -v` -- **144 tests, todos en verde.** No hace falta `.env` (todo mockeado). |

## Fundación (completa, revisada)

| Archivo | Estado |
|---|---|
| `voice.md` | Completo (Parte 1 + Parte 2 generada desde la semilla, commit `61aeee4`) |
| `world.md` | Completo, revisado (último cierre: commit `dde01c4`, "Implicaciones sociales") |
| `characters.md` | Completo salvo tres fichas: **Ledda, Ansermet y Ceruti quedan marcadas "ficha pendiente de generación"** -- no tienen ficha completa (commit `6f110dc`) |
| `outline.md` | **46 capítulos**, completo (commit `c85b90f`). Se le sacaron dos fragmentos residuales de un empalme roto por `max_tokens` (Ch 23 y Ch 42 -- commits `b0147a1` y `84618e8`, este último de hoy) |
| `canon.md` | Generado y poblado, pero **con cambios sin commitear ahora mismo** (ver fila de Working tree arriba) -- no confundir "existe y tiene contenido" con "el working tree está limpio" |

## Redacción

`chapters/ch_01.md` ("Intervalo") escrito y **aprobado tras lectura** --
la voz se sostiene, el diálogo distingue personajes sin etiquetas.
Commiteado (`aa8efd1`).

**Ojo:** `state.json` sigue en `chapters_drafted: 0` -- no se está
orquestando con `run_pipeline.py`, así que ese contador no refleja la
realidad. No confiar en `state.json` para saber cuántos capítulos hay
escritos; mirar `chapters/` directamente.

## Bugs de compatibilidad con Fable 5 (arreglados hoy, todos commiteados en esta rama)

Ninguno de estos era un problema conocido en `framework/es-multilibro`
porque esa rama nunca corrió contra la API real. Se fueron encontrando
en orden al ejecutar la fundación real por primera vez:

| # | Bug | Commit |
|---|---|---|
| 1 | `temperature` en el payload -- deprecado en Fable 5, tira 400 | `c8f7b99` |
| 2 | `resp.json()["content"][0]["text"]` asumía que el primer bloque de la respuesta era texto. Fable 5 manda un bloque `thinking` primero, así que esto rompía (bloque equivocado / sin `"text"`) en los ~19 scripts que llamaban a la API directo, antes de que existiera `api_comun.py` | `7b66805` |
| 3 | La plantilla de `voice.md` ("Part 2: Voice Identity...") tenía prosa de ejemplo **fuera** de comentario HTML. La guardia de idempotencia de `gen_voice.py` (línea ~186: saca los `<!-- ... -->` y si queda algo no vacío, asume "ya tiene contenido real, no tocar") confundía esa prosa de plantilla con contenido ya generado y no regeneraba nada -- **en silencio**, sin error. Se corrigió envolviendo esa prosa en un comentario HTML | `7b66805` (mismo commit que el #2) |
| 4 | Tarea 8: streaming centralizado en `api_comun.py` (reemplaza las ~19 copias casi idénticas de `call_writer()`/`call_judge()`/etc.) | `d03e879` |
| 5 | Tarea 9: continuación automática cuando la respuesta se corta por `stop_reason == "max_tokens"` | `b63a32b` |
| 6 | **Tarea 9b:** el mecanismo de la Tarea 9 usaba *prefill* (terminar la conversación en un turno `assistant`, sin turno de usuario después). Confirmado contra la API real que Fable 5 lo rechaza con 400: *"This model does not support assistant message prefill. The conversation must end with a user message."* Corregido: el texto parcial sigue como turno `assistant`, pero ahora seguido de un turno `user` explícito pidiendo continuar, con recorte de solapamiento sufijo/prefijo en la juntura (`_recortar_solapamiento()`) por si el modelo repite texto al ya no ser prefill literal. Probado contra la API real. De paso se encontró y arregló que `stop_reason == "refusal"` no se manejaba -- el loop lo trataba como `end_turn` y devolvía el texto truncado como si fuera la respuesta completa, sin aviso | `9f28e5f` |

Los fragmentos residuales de `outline.md` (Ch 23, Ch 42 -- ver tabla de
Fundación arriba) son consecuencia directa del bug #6 *antes* de
corregirse: `outline.md` se generó con el prefill viejo.

## Pendiente (no bloqueante)

- **Tarea 10:** acumulación de canon durante la redacción (que cada
  capítulo escrito alimente `canon.md` con lo que efectivamente quedó
  fijado en la página, no solo lo planeado en el esquema).
- **Tarea 11:** punto de aprobación manual por capítulo antes de seguir
  al siguiente (la aprobación del Cap. 1 fue manual/informal, leyendo el
  archivo -- no hay automatización todavía).
- Fichas completas de **Ledda, Ansermet y Ceruti** en `characters.md`.
- Mergear las Tareas 8, 9 y 9b hacia `framework/es-multilibro` cuando
  convenga -- son mejoras al framework en sí (`api_comun.py` no es
  específico de esta novela), y esa rama todavía tiene el bug de prefill
  sin corregir si algún día corre contra Fable 5.
- Resolver qué hacer con `world.md.regenerado` y con los cambios sin
  commitear en `canon.md` (ninguno de los dos se investigó a fondo en
  esta sesión).

## Próximo paso

Seguir escribiendo capítulos con:

```bash
uv run python draft_chapter.py N
```

**Ojo:** el número de capítulo va **posicional**
(`chapter_num = int(sys.argv[1])` en `draft_chapter.py`) -- **no** hay
flag `--chapter`.

Leer cada capítulo generado antes de avanzar al siguiente (como se hizo
con el Cap. 1) -- no hay automatización de aprobación todavía (Tarea 11
pendiente).

## Cómo retomar

1. `git status` -- confirmar si `canon.md` y `world.md.regenerado`
   siguen igual o si alguien ya los resolvió.
2. `git log origin/novela2..HEAD --oneline` -- confirmar qué falta
   pushear.
3. `uv run python -m pytest tests/ -v` -- confirmar 144 en verde antes
   de tocar nada.
4. `uv run python draft_chapter.py 2` -- seguir con el Cap. 2, leerlo
   antes de avanzar.
