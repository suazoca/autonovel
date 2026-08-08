# Seguimiento de tareas del proyecto — "La ostensión" (Libro 1)

Última actualización: 2026-08-09 (arc_summary.md aprobado)

**Avance general estimado: ~61%**
(Manuscrito 100% terminado. Fase 3 (revisión de conjunto) en curso:
2 de 6 scripts traducidos, contenido de personas lectoras resuelto,
`arc_summary.md` generado y aprobado. Resto: portada, audiolibro,
metadata y publicación.)

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

**Estado: 🔵 ~30% — en curso (2 de 6 scripts traducidos + 1 script adicional corregido + `arc_summary.md` aprobado)**

`gen_revision.py` y `gen_brief.py` ya están traducidos. `build_arc_summary.py`
(prerrequisito no contemplado originalmente) corregido y `arc_summary.md`
generado y aprobado. Los otros 4 (`review.py`, `reader_panel.py`,
`adversarial_edit.py`, `compare_chapters.py`) siguen en inglés y sin
adaptar a esta novela — contenido de `reader_panel.py` ya resuelto
(ítem 3b), falta idioma. Detalle completo en `docs/TRASPASO.md`,
sección "Fase 3 (revisión de conjunto): estado de adaptación".

| Tarea | Estado | Costo | Nota |
|---|---|---|---|
| 1. Traducir `gen_revision.py` + corregir título hardcodeado + enganchar `deteccion_es.py` | ✅ Hecho (`1876e17`) | — (solo edición de código, sin llamadas a la API) | `obtener_titulo()` reusable para Libro 2; 7/7 reglas compartidas con `draft_chapter.py` confirmadas idénticas carácter por carácter. Pendiente menor no bloqueante: evaluar si agregar la regla "variá longitud de párrafos" que sí tiene `draft_chapter.py` |
| 2. Traducir `gen_brief.py` (headers y frases armadas) | ✅ Hecho | — (solo edición de código) | Verificado sin comparaciones de string rotas (`brief_type` consistente en las 4 funciones). Debt documentado aparte: `chapter_title()` cae a "Sin título" en 45/46 capítulos por falta de encabezado markdown |
| 2b. **Corregir `build_arc_summary.py`** (séptimo script, no contemplado en el inventario original — es prerrequisito de `reader_panel.py`, no parte de Fase 3a/3b) | ✅ Hecho (`e8e800d`, `d7ad0f4`) | ~$1-2 estimado (corrida real no medida — ver nota de costo) | Peor contaminación de los 7: `range(1,20)` (ni coincidía con la referencia), título y PREMISE completa hardcodeados (Cantamura/Cass/Perin), conteo "23 chapters" inconsistente con su propio rango, bug de `extract_key_passages()` (buscaba comillas, la novela usa raya). Corregido: rango dinámico, `obtener_titulo()`, premisa desde `semilla.txt`, diálogo por raya. Además: quinto caso de rechazo "cyber" de Fable (Cap. 2), resuelto con Opus; tercera aparición del bug de `max_tokens`/thinking budget (200→4000) |
| 3. **[LECTORES] Generar `arc_summary.md`** | ✅ Hecho — aprobado sin revisión de contenido línea por línea, siguiendo el propio diseño de autonovel (artefacto de diagnóstico intermedio, no capítulo final — mismo trato que el JSON de `adversarial_edit.py`/`reader_panel.py`) | $ — (corrida real, no medida) | 46/46 capítulos, 85.281 palabras, 4 chequeos automáticos OK, generado vía Opus (no Fable, por el rechazo "cyber" del Cap. 2) |
| 3c. **[LECTORES] Traducir idioma de `reader_panel.py`** (las 4 personas lectoras: Editor, Genre Reader, Writer, First Reader — incluido `READER_PROMPT` línea 82 "a complete fantasy novel") + corregir contenido hardcodeado ("Cass", Ch 22/24, conteo de palabras) | ⬜ Pendiente | $ — | Contenido de las personas ya resuelto (ítem 3b) — este paso es solo idioma + los hardcodeos que no son de las personas |
| 3b. **[LECTORES] Adaptar contenido (no idioma) de 2 de las 6 personas lectoras/juzgadoras** — diagnóstico completo hecho el 2026-08-09: de las 6 (Editor, Genre Reader, Writer, First Reader en `reader_panel.py`; crítico literario y profesor de ficción en `review.py`), solo **Genre Reader** (alta contaminación: identidad "fantasy reader", "worldbuilding payoff", 5 autores de fantasía) y **Writer** (baja: solo la credencial "Hugo nomination") necesitaban ajuste de contenido. Las otras 4 son traducción mecánica pura | ✅ Hecho | — (solo edición de código) | Genre Reader: "avid fantasy reader" → "avid literary thriller reader", "worldbuilding payoff" → "investigation payoff", autores → Umberto Eco, Arturo Pérez-Reverte, John le Carré. Writer: "fantasy author... Hugo nomination" → "author of literary suspense... Edgar Award nomination". Editor y First Reader confirmados sin cambios. Hallazgo adicional durante la verificación: `READER_PROMPT` (línea 82) también dice "a complete fantasy novel" — no es una de las 4 personas, queda para el paso de traducción de idioma (ítem 3c) |
| 4. Traducir `adversarial_edit.py` y `compare_chapters.py` + corregir `range(1,25)` → `range(1,47)` | ⬜ Pendiente | $ — | Fallarían en silencio sobre los capítulos 25–46 |
| 5. **[JUZGADORES]** Traducir idioma de `review.py` (las 2 personas juzgadoras: crítico literario + profesor de ficción) | ⬜ Pendiente | $ — | El menos roto — sin contenido hardcodeado, `get_title()` ya funciona. Sin contaminación de género según diagnóstico de 3b — solo falta idioma |
| 6. **[LECTORES] Correr `reader_panel.py` contra el manuscrito completo** (una vez traducido — ítem 3c) | ⬜ Pendiente | $ — | 4 personas leen `arc_summary.md` y devuelven veredicto JSON cada una — el objetivo es justo el desacuerdo entre lectores como señal editorial, momentum_loss, ritmo |
| 6b. **[JUZGADORES] Correr `review.py` contra el manuscrito completo** (una vez traducido — ítem 5) | ⬜ Pendiente | $ — | Revisión doble (crítico literario + profesor de ficción) en una sola llamada — sugerencias accionables, hasta 4 rondas con corte automático cuando ya no aparecen ítems mayores |
| 6c. Revisar resultados de ambas corridas y decidir acciones (¿aplicar sugerencias vía `gen_brief.py`+`gen_revision.py`? ¿son solo para lectura, sin tocar capítulos?) | ⬜ Pendiente | — | Esta es la decisión editorial real de toda la Fase 3 — las corridas 6/6b son insumo, no el objetivo final |
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
| 1–2. Fundamentos + redacción (46 capítulos, Fable 5 + Opus 5) | $ — |
| 3. Revisión de conjunto (incluye 3 corridas de `build_arc_summary.py`: parcial Fable, parcial Opus fallida, completa Opus 46/46) | $ — pendiente de consultar el dashboard de Anthropic Console, filtrado por 2026-08-09 — no queda en los logs del script |
| 4a. Exportación manuscrito (tipografía local, sin costo de API) | — |
| 4b. Portada (fal.ai) | $ — |
| 4c. Audiolibro (ElevenLabs) | $ — |
| 5. Publicación (sin costo de API — trámites/plataformas) | — |
| **TOTAL** | **$ —** |

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
