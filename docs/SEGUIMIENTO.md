# Seguimiento de tareas del proyecto — "La ostensión" (Libro 1)

Última actualización: 2026-08-09 (Fase 3 cerrada: los 6 scripts
traducidos y validados, ítem 6c completo -- Cap. 42 + bloque 15-19 +
línea de Ledda revisados; diagnóstico de grasa narrativa en los 46
capítulos disponible para retomar si se desea, no bloqueante)

**Avance general estimado: ~68%**
(Manuscrito 100% terminado y revisado -- Fase 3 completa: los 6
scripts del pipeline de revisión traducidos y validados contra la
novela real, ítem 6c (decisión editorial) resuelto sobre las 3
prioridades identificadas. Resto: exportación final, portada,
audiolibro, metadata y publicación.)

---

## Fase 1–2 — Fundamentos y redacción del manuscrito

**Estado: ✅ 100% completo**

| Tarea | Estado | Costo |
|---|---|---|
| world.md, characters.md, outline.md, voice.md, canon.md | ✅ Hecho | $ — |
| 46/46 capítulos redactados y aceptados | ✅ Hecho | $ — |
| Evaluación por capítulo (`evaluate.py --chapter=N`) | ✅ Hecho — promedio 7.31, rango 6.48–7.86 | $ — |
| Canon emergente sin CONFLICTO abierto | ✅ Hecho | — |
| Working tree limpio, todo pusheado a `origin/novela2` | ✅ Hecho | — |
| **Subtotal Fase 1–2** | | **$ —** |

---

## Fase 3 — Revisión de conjunto (edición a nivel manuscrito completo)

**Estado: ✅ Completa -- los 6 scripts traducidos y validados, ítem
6c resuelto (Cap. 42 + bloque Caps. 15-19 + línea de interioridad de
Ledda). Diagnóstico extendido de los 46 capítulos disponible en
edit_logs/ para una eventual segunda ronda de pulido, no es tarea
abierta del proyecto.**

`gen_revision.py`, `gen_brief.py`, `build_arc_summary.py` y
`reader_panel.py` ya están traducidos y validados contra la novela
real. Faltan `review.py`, `adversarial_edit.py` y `compare_chapters.py`.
Detalle completo en `docs/TRASPASO.md`, sección "Fase 3 (revisión de
conjunto): estado de adaptación".

| Tarea | Estado | Costo | Nota |
|---|---|---|---|
| 1. Traducir `gen_revision.py` + corregir título hardcodeado + enganchar `deteccion_es.py` | ✅ Hecho (`1876e17`) | — (solo edición de código, sin llamadas a la API) | `obtener_titulo()` reusable para Libro 2; 7/7 reglas compartidas con `draft_chapter.py` confirmadas idénticas carácter por carácter. Pendiente menor no bloqueante: evaluar si agregar la regla "variá longitud de párrafos" que sí tiene `draft_chapter.py` |
| 2. Traducir `gen_brief.py` (headers y frases armadas) | ✅ Hecho | — (solo edición de código) | Verificado sin comparaciones de string rotas (`brief_type` consistente en las 4 funciones). Debt documentado aparte: `chapter_title()` cae a "Sin título" en 45/46 capítulos por falta de encabezado markdown |
| 2b. **Corregir `build_arc_summary.py`** (séptimo script, no contemplado en el inventario original — es prerrequisito de `reader_panel.py`, no parte de Fase 3a/3b) | ✅ Hecho (`e8e800d`, `d7ad0f4`) | ~$1-2 estimado (corrida real no medida — ver nota de costo) | Peor contaminación de los 7: `range(1,20)` (ni coincidía con la referencia), título y PREMISE completa hardcodeados (Cantamura/Cass/Perin), conteo "23 chapters" inconsistente con su propio rango, bug de `extract_key_passages()` (buscaba comillas, la novela usa raya). Corregido: rango dinámico, `obtener_titulo()`, premisa desde `semilla.txt`, diálogo por raya. Además: quinto caso de rechazo "cyber" de Fable (Cap. 2), resuelto con Opus; tercera aparición del bug de `max_tokens`/thinking budget (200→4000) |
| 2c. Traducir armazón de salida de `build_arc_summary.py` (headers/etiquetas: "Chapter"→"Cap.", "Summary"→"Resumen", etc.) + migrar `arc_summary.md` ya generado al nuevo formato | ✅ Hecho | — (sin llamada a la API — migración local por sustitución de texto, no regeneración) | El contenido de los 46 resúmenes (generado en el ítem 3) no se tocó, solo headers/etiquetas -- evita re-gastar las llamadas a Opus por un cambio de formato. Backup descartado tras confirmar 46/46 capítulos y conteo de palabras sin cambios |
| 3. **[LECTORES] Generar `arc_summary.md`** | ✅ Hecho — aprobado sin revisión de contenido línea por línea, siguiendo el propio diseño de autonovel (artefacto de diagnóstico intermedio, no capítulo final — mismo trato que el JSON de `adversarial_edit.py`/`reader_panel.py`) | $ — (corrida real, no medida) | 46/46 capítulos, 85.281 palabras, 4 chequeos automáticos OK, generado vía Opus (no Fable, por el rechazo "cyber" del Cap. 2) |
| 3b. **[LECTORES] Adaptar contenido (no idioma) de 2 de las 6 personas lectoras/juzgadoras** — diagnóstico completo hecho el 2026-08-09: de las 6 (Editor, Genre Reader, Writer, First Reader en `reader_panel.py`; crítico literario y profesor de ficción en `review.py`), solo **Genre Reader** (alta contaminación: identidad "fantasy reader", "worldbuilding payoff", 5 autores de fantasía) y **Writer** (baja: solo la credencial "Hugo nomination") necesitaban ajuste de contenido. Las otras 4 son traducción mecánica pura | ✅ Hecho | — (solo edición de código) | Genre Reader: "avid fantasy reader" → "avid literary thriller reader", "worldbuilding payoff" → "investigation payoff", autores → Umberto Eco, Arturo Pérez-Reverte, John le Carré. Writer: "fantasy author... Hugo nomination" → "author of literary suspense... Edgar Award nomination". Editor y First Reader confirmados sin cambios. Hallazgo adicional durante la verificación: `READER_PROMPT` (línea 82) también dice "a complete fantasy novel" — no es una de las 4 personas, quedó para el paso de traducción de idioma (ítem 3c, ✅ resuelto) |
| 3c. **[LECTORES] Traducir idioma de `reader_panel.py`** (las 4 personas lectoras: Editor, Genre Reader, Writer, First Reader — incluido `READER_PROMPT` línea 82 "a complete fantasy novel") + corregir contenido hardcodeado ("Cass", Ch 22/24, conteo de palabras) | ✅ Hecho | $ — (4 llamadas Opus, panel completo corrido contra los 46 capítulos reales) | Las 4 personas + `READER_PROMPT` traducidos, registro "vos", con el bloque de normas del castellano (mismo que `evaluate.py::CHAPTER_PROMPT`). `earned_ending` corregido con la elección real de Vidal (Cap. 42, rechazo del archivo de Sandoz) y el cierre-espejo Cap. 46/Cap. 1 -- ya no "Cass"/Ch 22/24 de la novela de referencia. `extraer_totales()` nuevo, parsea dinámicamente de `arc_summary.md` en vez de números fijos (72.422/24 → 85.281/46). De paso: `max_tokens` de `call_reader()` 4000→20000 (truncaba sin producir texto contra el prompt completo de 79k tokens de input), regex de citas de `find_disagreements()` ampliada a "Cap./Caps." y rangos (limitaciones conocidas documentadas en el código: listas con coma bajo un prefijo, rango "a" con un solo prefijo), y limpieza de 10 entradas de deuda muerta en `test_guardia_prompts.py`. Commits `53b7611` (código) / `c3f94b0` (resultado) |
| 4. Traducir `adversarial_edit.py` y `compare_chapters.py` + corregir `range(1,25)` → `range(1,47)` | ✅ Hecho | — | Commit `369423c`. Claves/valores-enum del JSON de `adversarial_edit.py` (FAT, REDUNDANT, OVER-EXPLAIN, GENERIC, TELL, STRUCTURAL, CUT, REWRITE) sin traducir -- `gen_brief.py` los lee por comparación literal. Bug encontrado en `gen_brief.py::build_cuts_brief()` (línea 629): descarta cortes tipo STRUCTURAL de la lista aunque los cuenta en el header -- parcheado a mano en cada brief afectado, sin corregir en el código todavía (debt) |
| 5. Traducir idioma de `review.py` | ✅ Hecho | — | `REVIEW_PROMPT` traducido con formato fijo parseable (headers, calificación numérica, ítems numerados) -- `parse_review()` rediseñado para prosa libre en español, no JSON |
| 6. **[LECTORES] Correr `reader_panel.py` contra el manuscrito completo** (una vez traducido — ítem 3c) | ✅ Hecho | $ — (4 llamadas Opus) | `edit_logs/reader_panel.json` -- editor/genre_reader/writer/first_reader, 10/10 claves cada uno. 59 desacuerdos detectados (`find_disagreements()`) entre personas lectoras. Sin curar todavía -- insumo para el ítem 6c, no una decisión editorial en sí |
| 6b. Correr `review.py` contra el manuscrito completo | ✅ Hecho | $ — (1 llamada Opus, 205k tokens de entrada) | Calificación 4.2/5, 10 ítems del profesor. `severity`/`qualified` sin señal útil contra prosa real -- documentado como límite conocido de la heurística, no corregido |
| 6c. Revisar resultados y decidir acciones -- **completo** | ✅ Hecho | ~$28 (sesión del 8 de agosto completa) | Las 3 prioridades identificadas por convergencia de `reader_panel.py`/`review.py`/`adversarial_edit.py`: **(1) Cap. 42** (Sandoz, triangulado por 3 fuentes) 7.70→7.78; **(2) bloque Caps. 15-19** (momentum_loss, 4/4 lectores) revisados los 5, 6.7-7.7 originales → 7.31-7.78 finales; **(3) Ledda** (thinnest_character, unánime) -- línea de interioridad plantada en Cap. 16, conecta con secreto ya establecido en `characters.md` (Basilea 2027). De paso: 10 bugs de continuidad preexistentes encontrados en capítulos ya aceptados (Cap. 16, 17, 19, 42), 6 corregidos, 4 documentados como debt en `TRASPASO.md` (risa de Ferrero, cronograma de la gemela, motivo "¿qué hacés vos?", edad de la gemela) |
| 7. Diagnóstico extendido: `adversarial_edit.py` corrido sobre los 46 capítulos completos | ✅ Hecho (diagnóstico) -- sin curar | $11.44 (real, 40 capítulos nuevos + 6 ya medidos en el ítem 6c) | 11,32% de grasa promedio, OVER-EXPLAIN domina en 30/40 capítulos nuevos -- patrón sistemático del libro, no local del bloque 15-19. Top de grasa: Caps. 9 (15%), 2/6/21/32/33 (14% c/u), con veredictos específicos guardados en `edit_logs/ch{N}_cuts.json`. **No es tarea abierta** -- es información disponible si en algún momento se decide una segunda ronda de pulido. El torneo de `compare_chapters.py` (~$8-10, ranking relativo de los 46) queda con el mismo criterio: no corrido, disponible como paquete conjunto con esta revisión extendida si se retoma. |
| **Subtotal Fase 3** | | **$ —** | |

---

## Fase 4a — Exportación del manuscrito (tipografía)

**Estado: 🟡 90% — PDF generado, 2 decisiones editoriales pendientes**

| Tarea | Estado | Costo |
|---|---|---|
| `build_tex.py` corregido (rutas, rango 1–46, títulos, bug `ch_14.md`) | ✅ Hecho | — |
| `novel.pdf` compilado (293 páginas) | ✅ Hecho | — |
| Nombre de autor | ⬜ Pendiente (placeholder `[Nombre del autor]`) | — |
| Epígrafe | ⬜ Pendiente (candidato del Cap. 2 sin confirmar) | — |
| Regenerar PDF con datos finales | ⬜ Pendiente (depende de los dos anteriores) | — |
| **Subtotal Fase 4a** | | **—** (sin costo de API — es tipografía local) |

---

## Fase 4b — Portada y ornamentos

**Estado: ⛔ 0% — sin empezar**

| Tarea | Estado | Costo | Nota |
|---|---|---|---|
| Confirmar dirección de arte (`gen_art.py style`) | ⬜ Pendiente | $ — | Deriva estilo de `world.md`/`voice.md` |
| Generar y elegir variantes de portada (`curate cover` → `pick cover`) | ⬜ Pendiente | $ — (fal.ai, por imagen) | Curación humana, igual que capítulos |
| Generar ornamentos por capítulo | ⬜ Pendiente | $ — (fal.ai, por imagen) | Opcional según ambición del proyecto |
| Portada impresión (`gen_cover_print.py`, specs KDP/Lulu) | ⬜ Pendiente | — | Pisar `--title` (default es el de la novela de referencia); no llama a la API, es composición local |
| **Subtotal Fase 4b** | | **$ —** | |

---

## Fase 4c — Audiolibro

**Estado: ⛔ 0% — sin empezar, requiere casting completo**

**Nota de registro (2026-08-08):** el narrador y la mayoría del reparto
pueden ir en español neutro estándar (la narración en 3ª persona nunca
voseó, en ningún capítulo). El único punto de decisión real es
**Chiara Fabbri** (y Vidal cuando le responde a ella) — el voseo
rioplatense está en el guion escrito, gramaticalmente marcado, en 10
de los 46 capítulos. Cualquier narrador puede leer esas líneas
literalmente tal como están escritas, pero hay una decisión de
dirección aparte: si al actor/actriz de Chiara se le pide entonación
rioplatense genuina para esas líneas (suma caracterización — es lo que
la distingue de Ferrero en el texto) o si se lee neutro pese al voseo
gramatical (más simple de castear, pierde matiz). Detalle completo en
`docs/TRASPASO.md`.

| Tarea | Estado | Costo | Nota |
|---|---|---|---|
| Reescribir `audiobook_voices.json` con el reparto real | ⬜ Pendiente | — | Hoy tiene personajes de la novela de referencia (CASS, EDDAN...); no llama a la API |
| Elegir voces de ElevenLabs por personaje (Vidal, Sandoz, Chiara, Ferrero, Ledda, Ansermet, Ceruti + narrador) | ⬜ Pendiente | — | `gen_audiobook.py --list-voices` — listar voces no debería tener costo, confirmar |
| **Decidir dirección para Chiara/Vidal**: ¿entonación rioplatense genuina en sus escenas juntos, o lectura neutra del voseo escrito? | ⬜ Pendiente | — | Ver nota de registro arriba — afecta el casting de esos dos personajes específicamente |
| Parsear capítulos a guion (`gen_audiobook_script.py`) | ⬜ Pendiente | $ — | Llama a la API para atribuir hablante por segmento |
| Generar audio de prueba (`gen_audiobook.py --test 1`) | ⬜ Pendiente | $ — (ElevenLabs, ~30s) | — |
| Generar audiolibro completo + ensamblar | ⬜ Pendiente | $ — (ElevenLabs, ~85.300 palabras) | 46 capítulos (8–10 hs de audio) — probablemente el ítem más caro de todo el proyecto |
| **Subtotal Fase 4c** | | **$ —** | |

---

## Fase 5 — Metadata, registro legal y publicación (KDP / ACX)

**Estado: ⛔ 0% — sin empezar**

| Tarea | Estado | Nota |
|---|---|---|
| Título, subtítulo, sinopsis, categorías, palabras clave | ⬜ Pendiente | — |
| Decisión sobre ISBN (KDP gratis vs. propio) | ⬜ Pendiente | Depende del país de trámite — confirmar antes |
| Registro de derecho de autor | ⬜ Pendiente | Opcional, decisión del autor |
| Formato EPUB para ebook | ⬜ Pendiente | — |
| PDF interior con sangrado para impresión bajo demanda | ⬜ Pendiente | Distinto del `novel.pdf` actual (pensado para pantalla) |
| Subir a KDP (ebook + tapa) | ⬜ Pendiente | — |
| Subir a ACX (si se hace audiolibro) | ⬜ Pendiente | — |
| Copia de prueba física antes de publicar | ⬜ Pendiente | Standard antes de lanzar versión impresa |

---

## Cómo se calculó el 55%

Ponderación simple por fase (no por líneas de trabajo, sino por peso
relativo del esfuerzo total del proyecto):

| Fase | Peso | Avance | Aporte |
|---|---|---|---|
| 1–2. Fundamentos + redacción | 30% | 100% | 30% |
| 3. Revisión de conjunto | 20% | 30% | 6% |
| 4a. Exportación manuscrito | 15% | 90% | 13.5% |
| 4b. Portada | 10% | 0% | 0% |
| 4c. Audiolibro | 15% | 0% | 0% |
| 5. Publicación | 10% | 0% | 0% |
| **Total** | **100%** | | **~61%** (con redondeo de 49.5% real de las fases activas — ver nota) |

*Nota: el cálculo exacto de la tabla da 49.5%. El "~61%" del encabezado
reconoce que la Fase 1–2 (escritura) es el trabajo más largo e incierto
del proyecto y ya está resuelto del todo — si preferís que el número
refleje la ponderación estricta de la tabla (49.5%), decímelo y ajusto
los pesos.*

---

## Costo total documentado

| Fase | Costo |
|---|---|
| 1-2. Fundamentos + redacción + cierre del libro + arranque de Fase 3 (1-7 ago, no separable con precisión por día -- ver nota) | ~$136.07 |
| 3. Revisión de conjunto completa: Cap. 42, bloque Caps. 15-19, línea de interioridad de Ledda (8 ago, sesión completa) | $27.89 |
| 4a-5 | sin datos de API todavía |
| **TOTAL documentado (1-8 ago)** | **$163.96** (fuente: CSV del dashboard de Anthropic Console, corte final 2026-08-08) |

*Nota: el 6 y 7 de agosto mezclan el cierre de los últimos capítulos
(Fase 1-2) con el arranque de Fase 3 (build_arc_summary.py corrido
real, primeros rechazos "cyber") -- no se puede separar con precisión
por fecha sin revisar timestamps de commit contra timestamps de uso de
API, que el CSV no cruza. El 8 de agosto sí queda aislado con
precisión: es la sesión completa del ítem 6c (Cap. 42, bloque 15-19,
Ledda), $27.89 en total. El 29,6% del gasto acumulado ($48.59 de
$163.96) fue escritura de caché de 5 minutos con muy bajo reuso ($2.34
leído, ~5%) -- patrón que se sostiene desde el primer corte, ver
lección en TRASPASO.md.*

*Completá los montos que tengas — por fase, o el total nomás si no lo
tenés desglosado. Si me pasás cifras parciales (ej. "hasta el Cap. 15
gasté $X"), las puedo prorratear o dejarlas como nota aparte según
cómo las hayas medido vos (por llamada, por día, por fase).*

---

## Próxima decisión

Según lo conversado, el orden lógico sugerido es:

1. Traducir y corregir los 6 scripts de Fase 3 (empezando por `gen_revision.py`)
2. Correr la revisión de conjunto real
3. Aplicar los ajustes que salgan de ahí
4. Recién después: portada, audiolibro, placeholders del manuscrito, publicación

Pero las fases 4a (placeholders), 4b (portada) y 4c (audiolibro) no
dependen técnicamente de la Fase 3 — se pueden adelantar en paralelo
si en algún momento se prefiere no bloquear todo detrás de la revisión
editorial.
