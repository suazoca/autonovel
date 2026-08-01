# Arte — Libro 1: *Yamaranguila* (álbum medio ~48)

**Estado:** set completo de **48 ilustraciones** + hoja de personajes.

## Dónde están

| Ruta | Contenido |
|------|-----------|
| `pages/p01-*.jpg` … `pages/p48-*.jpg` | **Una imagen por página del libro** |
| `pages/_hoja-serie.jpg` | Copia de la hoja de personajes |
| `00-hoja-personajes.jpg` … `06-*.jpg` | Primera ronda (claves; también en `pages/`) |
| `index-paginas.html` | Galería ligera (rutas relativas a `pages/`) |
| `galeria-album-48.html` | Galería con las 48 **embebidas** (archivo grande, offline) |
| `galeria.html` | Galería antigua de 7 claves |

Ancla de serie (consistencia): `../../art/personajes/hoja-serie.jpg`

## Cómo verlas

```bash
cd libros/01-piloto/art
# opción ligera (mejor en GitHub / servidor local):
python3 -m http.server 8765 --bind 127.0.0.1
# abrir http://127.0.0.1:8765/index-paginas.html

# opción un solo archivo offline:
xdg-open galeria-album-48.html
```

En GitHub: carpeta  
`libros/01-piloto/art/pages/`  
(cada JPG se abre con Raw/Download).

## Inventario p01–p48

| Págs | Archivos (prefijo) |
|------|--------------------|
| 1–6 | titulo, paisaje, camping, cena, carpa-hierba, buenas-noches |
| 7–10 | temblor, noche, luna, duermen |
| 11–15 | manana, rio, pajarito, pueblo-lejos, telefono |
| 16–23 | dale-lejos, caja-secreto, camino-casita, abren-caja, yamaranguila, agua-piramide, emilia, eco-agua |
| 24–27 | plaza, tres-puntos, tres-pruebas, vayan |
| 28–35 | roca-clave, a-las-cinco, forman-y, roca-y, palancas, uno-dos-tres, roca-rueda, piramide |
| 36–39 | punto-dos, escuchar, dos-voces, caminito |
| 40–44 | punto-tres, juntos, agua, jarrito-lleno, lo-logramos |
| 45–48 | pueblo, dicen-tres, buenas-noches, proximo |

## Generación

- Herramienta: **xAI Imagine** (`image_gen` hoja + `image_edit` escenas).
- Referencia fija de personajes para consistencia.
- Estilo: `art/STYLE_BIBLE.md`.

## Siguiente

- Revisar / retocar páginas flojas.
- Maqueta PDF (texto de `paginas.md` + estas imágenes).
