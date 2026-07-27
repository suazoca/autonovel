# AUDITORÍA COMPLETA DE NOVEL — 12 de julio

Revisión de punta a punta de la lógica del pipeline buscando (a) piezas
aún cableadas al inglés o a la novela original, (b) desconexiones entre
nuestros agentes nuevos y el orquestador, (c) errores de lógica.

## Hallazgos CRÍTICOS (corregidos en actualizacion-2)

| # | Hallazgo | Riesgo | Corrección |
|---|---|---|---|
| 1 | `run_pipeline.py` Fase 1 llama a `gen_world/gen_characters/gen_outline/gen_canon` — habría REGENERADO y sobrescrito la fundación hecha a mano, con prompts en inglés | Destrucción total de TEOLOGIA, characters, world, outline | Guardia nueva: si existe `TEOLOGIA.md`, la fundación se considera manual y protegida — solo se evalúa, nunca se regenera |
| 2 | El conteo de capítulos (`get_total_chapters`) buscaba `### Ch N` / `### Chapter N` — nuestro outline usa `### Cap. N` → habría contado 0 y usado el default de 24 capítulos (la novela original) | El pipeline habría intentado escribir 24 capítulos de un outline de 23 | Regex ampliado a `Cap./Ch/Chapter` + epílogo renumerado como `Cap. 23` en outline.md (encabezado y tabla) |
| 3 | `gen_revision.py` (el que REESCRIBE capítulos en la fase de revisión) estaba 100% en inglés y pedía reescribir "The Second Son of the House of Bells" | Las revisiones habrían salido en inglés o degradadas | Adaptado completo al español: system prompt, brief, etiquetas, reglas de raya/calcos |
| 4 | `build_arc_summary.py` generaba los resúmenes para el panel de lectores en inglés Y con la PREMISA COMPLETA de la novela original (Cass, Cantamura, campanas) incrustada | El panel de lectores habría evaluado tu novela contra la premisa de otra | Resúmenes en español + premisa reemplazada por la de esta novela |
| 5 | `evaluate.py` (nuestra versión) conservaba 3 referencias a "Cass" en los prompts del juez (comparaba la voz contra un niño de 14 años de la novela original) | El juez de voz calibrado contra el personaje equivocado | Purgadas — referencias genéricas al personaje POV de characters.md |
| 6 | `reader_panel.py` preguntaba por "la decisión de Cass en el cap. 22" y "la imagen del cap. 24" | Panel evaluando estructura de otra novela | Pregunta genérica en español (clímax, espejo cap. 1) |
| 7 | Los agentes nuevos (`realidad.py`, `compulsion.py`) NO estaban en el loop del orquestador — solo funcionaban a mano | En modo automático, novel habría escrito sin informes de realidad | `realidad.py --brief` integrado antes de cada borrador y `--check` tras cada aprobación en `run_pipeline.py` |
| 8 | `typeset/novel.tex` con título/pdftitle "The Second Son of the House of Bells" hardcodeado | El PDF final saldría con el título de otra novela | Placeholder "TÍTULO PENDIENTE" — decisión del autor requerida antes de la Fase 4 |

## Verificación final
- `grep` de remanentes ("Cass", "Bells", "Second Son") en todos los .py
  y typeset: **0 resultados**.
- Sintaxis validada en los 8 scripts modificados.

## Flujo verificado (ver novel-flujo.mermaid)
1. **Fundación**: protegida por guardia; solo se evalúa.
2. **Borradores**: realidad --brief → draft (con TEOLOGIA + CRAFT-ES +
   informe + 33 reglas) → evaluate (slop ES + canon + teología + tabla
   de escenas) → umbral con reintentos → realidad --check → commit.
3. **Revisión**: cortes adversariales → panel de lectores (resúmenes
   ES) → briefs → gen_revision ES → antes/después con revert → hasta
   meseta.
4. **Revisión Opus**: tres personas (crítico + profesor + teólogo)
   sobre el manuscrito completo.
5. **Exportación**: LaTeX español / ePub es. Portada y audiolibro
   pendientes de configurar al llegar.

## Pendientes CONSCIENTES (no bloquean; se atienden al llegar a su fase)

| Pieza | Estado | Cuándo atender |
|---|---|---|
| Título de la novela | "TÍTULO PENDIENTE" en novel.tex y epub | Decisión del autor antes de la Fase 4 |
| `adversarial_edit.py` | Nota ES añadida; su prompt central de marcado sigue en inglés (los marcadores son mecánicos) | Observar en el primer ciclo de revisión; adaptar si los cortes salen torpes |
| `compare_chapters.py` (torneo Elo) | Standalone, no lo llama el pipeline; prompts en inglés | Solo si se decide usarlo |
| `gen_art*`, `gen_cover*` | Prompts de imagen en inglés (correcto para modelos de imagen); referencias visuales a revisar | Fase de exportación |
| `gen_audiobook*` | Parser de rayas ya adaptado; falta elegir voces multilingües y modelo eleven_multilingual_v2 | Fase de audiolibro |
| `landing/index.html` | Página de la novela original | Fase de publicación |
| `compulsion.py` | No integrado al loop automático (por diseño: es herramienta de lectura del autor) | Manual, cuando se quiera |

## Regla de mantenimiento
Cada vez que se añada un agente nuevo, verificar TRES conexiones:
(1) ¿draft_chapter lo consume? (2) ¿run_pipeline lo llama? (3) ¿sus
prompts asumen español y ESTA novela?
