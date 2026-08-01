# TRASPASO — rama `ciudades-hn`

Estado al crear el proyecto (2026-08-01).

## Qué es

Worktree `/root/ciudades-hn`, rama `ciudades-hn`, creada desde
`novela2` @ `a3ca435`. **No es** *La ostensión*: se limpió semilla, voz,
mundo, personajes, outline, canon y capítulos de esa novela.

Proyecto creativo: **serie de cuentos infantiles (4–7 años)** basados en
nombres y significados de **ciudades de Honduras**, ~70 páginas por
libro, con plan de **ilustración + prompts por página**.
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
| `semilla.txt` | plantilla del Libro 1 (vacía de ciudad) |

## Herencia técnica (de novela2)

- `api_comun.py`, drafting/eval/canon scripts, tests (~238 pass + xfail)
- `.env` copiado localmente (no trackeado): writer Fable 5, judge/review Opus 5
- Deuda conocida: prompts de juez/revisión aún calibrados en parte a
  adulto/fantasía (`tests/test_guardia_prompts.py`) — para esta serie
  conviene rúbrica infantil nueva antes de evaluar capítulos “en serio”

## Pendiente creativo

1. Elegir ciudad del Libro 1 y significado declarado.
2. Decidir continuidad (mismos héroes vs. antologías por ciudad).
3. Completar `semilla.txt` / `libros/01-piloto/semilla.txt`.
4. Esbozar `paginas.md` (~70) antes de prosa larga.
5. Fijar personajes en `art/STYLE_BIBLE.md`.

## Pendiente técnico (después del piloto en papel)

- Cablear evaluate/revisión a `CRAFT_INFANTIL` (o script aparte).
- Decidir si `chapters/` del framework se usa o solo `libros/.../paginas.md`.
- Generación de imágenes con bible + prompts.

## Próximo paso

Cerrar semilla del piloto (ciudad + héroes + problema) y rellenar el
mapa de páginas. No regenerar fundación de *La ostensión*.

```bash
cd /root/ciudades-hn
# editar semilla + libros/01-piloto/
uv run python -m pytest tests/ -q   # sanidad del framework
```
