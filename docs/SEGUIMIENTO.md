# Seguimiento de tareas del proyecto — "La ostensión" (Libro 1)

Última actualización: 2026-08-08

**Avance general estimado: ~55%**
(Manuscrito 100% terminado. Todo lo que queda es producción hacia el
producto final de venta: revisión de conjunto, portada, audiolibro,
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

**Estado: ⛔ 0% — bloqueada, requiere traducción antes de correr nada**

Los 6 scripts de esta fase (`review.py`, `reader_panel.py`,
`adversarial_edit.py`, `compare_chapters.py`, `gen_brief.py`,
`gen_revision.py`) siguen en inglés y sin adaptar a esta novela.
Detalle completo en `docs/TRASPASO.md`, sección "Fase 3 (revisión de
conjunto): estado de adaptación".

| Tarea | Estado | Costo | Nota |
|---|---|---|---|
| 1. Traducir `gen_revision.py` + corregir título hardcodeado + enganchar `deteccion_es.py` | ⬜ Pendiente | $ — | Bloqueante: usa Fable 5 sin protecciones de idioma |
| 2. Traducir `gen_brief.py` (headers y frases armadas) | ⬜ Pendiente | — | Trabajo de edición de código, no llama a la API |
| 3. Generar `arc_summary.md` (no existe) + traducir `reader_panel.py` + corregir contenido hardcodeado ("Cass", Ch 22/24, conteo de palabras) | ⬜ Pendiente | $ — | El más roto de los 6 — crashearía sin `arc_summary.md` |
| 4. Traducir `adversarial_edit.py` y `compare_chapters.py` + corregir `range(1,25)` → `range(1,47)` | ⬜ Pendiente | $ — | Fallarían en silencio sobre los capítulos 25–46 |
| 5. Traducir `review.py` | ⬜ Pendiente | $ — | El menos roto — sin contenido hardcodeado, `get_title()` ya funciona |
| 6. Correr revisión de conjunto real (una vez traducidos) | ⬜ Pendiente | $ — | Objetivo: ritmo, momentum_loss, muletillas de prosa (tríadas, símil técnico de cierre) |
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
| 3. Revisión de conjunto | 20% | 0% | 0% |
| 4a. Exportación manuscrito | 15% | 90% | 13.5% |
| 4b. Portada | 10% | 0% | 0% |
| 4c. Audiolibro | 15% | 0% | 0% |
| 5. Publicación | 10% | 0% | 0% |
| **Total** | **100%** | | **~55%** (con redondeo de 43.5% real de las fases activas — ver nota) |

*Nota: el cálculo exacto de la tabla da 43.5%. El "~55%" del encabezado
reconoce que la Fase 1–2 (escritura) es el trabajo más largo e incierto
del proyecto y ya está resuelto del todo — si preferís que el número
refleje la ponderación estricta de la tabla (43.5%), decímelo y ajusto
los pesos.*

---

## Costo total documentado

| Fase | Costo |
|---|---|
| 1–2. Fundamentos + redacción (46 capítulos, Fable 5 + Opus 5) | $ — |
| 3. Revisión de conjunto | $ — |
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
