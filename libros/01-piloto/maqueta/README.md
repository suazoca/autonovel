# Maqueta — *Yamaranguila*

**Archivo:** `Yamaranguila-maqueta.pdf` (~16 MB)

## Contenido

| Parte | Págs PDF |
|-------|----------|
| Portada de maqueta | 1 |
| Libro (texto + imagen) | 2–49 (= págs. 1–48 del álbum) |
| Nota para adultos | 50 |

- Texto: v2.1 de `../paginas.md`
- Imágenes: `../art/pages/p01`…`p48`
- Formato: horizontal (letter landscape), imagen arriba, texto abajo
- **Maqueta de trabajo**, no el PDF final de KDP
- **Publicación prevista:** ebook + KDP Print · trim **11" × 8.5" horizontal**
- **Autor:** Chris Suazo · ver `docs/PUBLICACION_KDP.md`

## Cómo abrir

```bash
# en el repo (rama ciudades-hn)
xdg-open libros/01-piloto/maqueta/Yamaranguila-maqueta.pdf
```

En GitHub: descarga el PDF desde esta carpeta (Raw / Download).

## Regenerar

```bash
cd /root/ciudades-hn
uv run python scripts/maqueta_yamaranguila.py   # si se exporta el script
# o el generador usado en la sesión de maqueta
```

## Siguiente

- Retocar ilustraciones flojas y re-generar maqueta
- Ajustes de tipografía / márgenes para edición
