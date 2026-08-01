# TRASPASO — rama `ciudades-hn`

Estado al día (2026-08-01): piloto Libro 1 en **trama híbrida C**.

## Qué es

Worktree `/root/ciudades-hn`, rama `ciudades-hn`, creada desde
`novela2` @ `a3ca435`. **No es** *La ostensión*: se limpió semilla, voz,
mundo, personajes, outline, canon y capítulos de esa novela.

Proyecto creativo: **serie de cuentos infantiles (4–7 años)** basados en
nombres y significados de **ciudades de Honduras**, álbum medio
(~40–48 páginas; piloto ~48), con plan de **ilustración + prompts por
página**.
**No es serie bíblica ni religiosa** (cultura local y topónimos; ver
`BIBLIA_SERIE.md` § “Qué es y qué no es”).

## Worktrees (no mezclar)

| Ruta | Rama | Proyecto |
|------|------|----------|
| `/root/novela2` | `novela2` | *La ostensión* (adulto) — no tocar desde acá |
| `/root/autonovel` | `novela-es` | otro libro |
| `/root/ciudades-hn` | `ciudades-hn` | **esta serie infantil** |

## En una línea

Framework/código de `novela2` (API Fable 5, pipeline, tests) + pizarra
creativa limpia + docs de serie infantil. Storytelling primario:
`CRAFT_INFANTIL.md`. Arte: `art/STYLE_BIBLE.md`. Plan por libro:
`libros/`.

## Archivos clave nuevos

| Archivo | Rol |
|---------|-----|
| `BIBLIA_SERIE.md` | reglas de la serie, catálogo, formato |
| `CRAFT_INFANTIL.md` | craft 4–7 (no usar CRAFT adulto como guía) |
| `ANTI-SLOP_INFANTIL.md` | anti-patrones infantiles |
| `art/STYLE_BIBLE.md` | look + prompt base de serie |
| `libros/_plantilla/` | semilla + `paginas.md` (texto/brief/prompt) |
| `libros/01-piloto/` | carpeta del primer libro |
| `semilla.txt` | plantilla del Libro 1 |

## Herencia técnica (de novela2)

- `api_comun.py`, drafting/eval/canon scripts, tests (~238 pass + xfail)
- `.env` copiado localmente (no trackeado): writer Fable 5, judge/review Opus 5
- Deuda conocida: prompts de juez/revisión aún calibrados en parte a
  adulto/fantasía (`tests/test_guardia_prompts.py`) — para esta serie
  conviene rúbrica infantil nueva antes de evaluar capítulos “en serio”

## Libro 1 — estado creativo

1. ~~Ciudad + significado.~~ **Yamaranguila** = Agua de la pirámide (*Zabalanquíra*).
2. ~~Héroes.~~ **Noha**, **Ivana**, abuelo **Dale**; mapa de **bisabuela Emilia**.
3. ~~Problema.~~ No había agua (río callado; pueblo con preocupación suave).
4. ~~Trama.~~ **Híbrido C** (idea del autor + craft 4–7):
   - camping + susto nocturno breve (no apocalipsis);
   - Dale lejos por teléfono; caja de herramientas + mapa de Emilia;
   - pueblo confía en los niños;
   - **3 pruebas:** roca de la Y (atardecer) · voz del cerro (dos voces, sin morse) · dos manijas del ojo de agua;
   - agua vuelve; eco del nombre; plant libro 2.
5. ~~`semilla.md` + `paginas.md` + texto corrido.~~
6. ~~Segunda lectura en voz alta (v2.1).~~ Texto aprobado.
7. ~~Título definitivo: **Yamaranguila**.~~ Subtítulo/eco: *El agua de la pirámide*.
8. ~~Primera ronda de arte~~ ✓ `libros/01-piloto/art/` (hoja + 6 claves).
9. ~~Formato álbum medio~~ ✓ **~48 páginas** (re-paginado desde plan de 70).
10. ~~Ilustraciones ~48~~ ✓ `libros/01-piloto/art/pages/`
11. ~~Maqueta PDF~~ ✓ `libros/01-piloto/maqueta/Yamaranguila-maqueta.pdf`
12. Retocar ilustraciones flojas y re-generar maqueta si hace falta.

## Pendiente técnico (después del piloto en papel)

- Cablear evaluate/revisión a `CRAFT_INFANTIL` (o script aparte).
- Decidir si `chapters/` del framework se usa o solo `libros/.../paginas.md`.
- Generación de imágenes con bible + prompts.

## Publicación (fijado)

| Campo | Valor |
|-------|--------|
| Canales | **Ebook (Kindle) + KDP Print** |
| Trim | **11" × 8.5" horizontal** (álbum) |
| Autor | **Chris Suazo** |
| Guía | `docs/PUBLICACION_KDP.md` |

Implica: corregir consistencia de arte antes del export final; alta
resolución (~300 DPI) al cerrar; declarar contenido IA en KDP; maqueta
actual = trabajo, no archivo final.

## Próximo paso

1. Lista de correcciones de arte (consistencia) con KDP en mente.
2. Retocar `art/pages/`; regenerar maqueta de trabajo.
3. Más adelante: trim size KDP + export alta res + portadas + subida.

```bash
cd /root/ciudades-hn
# texto corrido al final de libros/01-piloto/paginas.md
uv run python -m pytest tests/ -q   # sanidad del framework
```
