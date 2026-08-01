# Publicación — ebook + Amazon KDP

Documento de producción para la serie **Ciudades de Honduras**.
El Libro 1 (*Yamaranguila*) se publicará como **ebook** y vía **Amazon KDP**
(impresión bajo demanda y/o Kindle). Todo el arte, maquetas y correcciones
deben respetar esto.

> No sustituye las guías oficiales de KDP (cambian). Antes de subir,
> revisar: [KDP Help](https://kdp.amazon.com/help) · contenido IA ·
> tamaños de impresión · Kindle Kids / fixed layout.

---

## Canales previstos

| Canal | Producto | Implicación |
|-------|----------|-------------|
| **Kindle (ebook)** | Libro ilustrado infantil | Preferible **fixed layout** (álbum), no reflowable de novela |
| **KDP Print** | Rústica (y opcional tapa dura) | PDF de interiores a **300 DPI**, tamaño de recorte fijo, sangrado |
| **Otros ebook** (opcional) | EPUB fixed-layout | Misma lógica de “página = imagen + texto fijo” |

La **maqueta actual** (`libros/01-piloto/maqueta/`) es de **trabajo interno**,
no el archivo final de KDP.

---

## Decisiones a fijar (antes de archivos finales)

Marcar en la semilla del libro cuando se cierren:

1. **Tamaño de impresión (trim)** — ejemplos habituales infantiles KDP:
   - `8.5" × 8.5"` (cuadrado)
   - `8.5" × 11"` vertical
   - `11" × 8.5"` horizontal (cerca de nuestra maqueta landscape)
   - `10" × 8"` u otros del catálogo KDP
2. **Solo ebook / solo print / ambos** (mismo arte, exports distintos).
3. **Idioma de publicación:** español (mercados ES / US latam / etc.).
4. **Rango de edad en ficha:** 4–7 (como craft de serie).
5. **Portada:** archivo aparte (ebook cover ≠ cubierta con lomo de print).

**Recomendación de serie (provisional):**  
trim **horizontal 11" × 8.5"** o **10" × 8"** para coincidir con álbum landscape;
si se prefiere estantería clásica infantil, **8.5" × 8.5"** y re-exportar arte
a cuadrado. **Decidir antes** de regenerar a 300 DPI masivo.

---

## Arte e inconsistencias (cómo afecta el flujo)

1. **Primero** corregir consistencia de personajes/objetos en los JPG maestros
   (`art/pages/`), siempre con `art/personajes/hoja-serie.jpg`.
2. **No** maquetar KDP final hasta tener un set aprobado (evita rehacer 300 DPI).
3. Tras aprobación visual:
   - export / upscale a **≥ 300 DPI al tamaño de recorte** (print);
   - versión ebook: puede ser un poco más ligera pero **misma composición**.
4. Regenerar maqueta de trabajo y luego el **PDF de impresión** / paquete Kindle.

### Resolución actual (deuda)

Las imágenes Imagine del piloto rondan **1280×720**. Eso **no basta** como
archivo final de impresión a tamaño álbum a 300 DPI (harían falta ~3300 px
en el lado largo, según trim). Plan:

- Correcciones de consistencia en la resolución actual (rápido).
- Pase final de **upscale o regeneración a alta res** solo de páginas
  aprobadas (o de todo el set una vez estable).

### Consistencia (checklist de publicación)

- [ ] Noha / Ivana / Dale: misma cara, edad, ropa de serie
- [ ] Dale **no** aparece en cuerpo donde el texto lo pone lejos (salvo
      teléfono / recuerdo / coda)
- [ ] Jarrito y mapa de Emilia reconocibles página a página
- [ ] Sin texto legible inventado en la ilustración (título va en capa de texto)
- [ ] Sin marcas de agua, logos de IA, UI
- [ ] Misma relación de aspecto en todas las páginas del libro

---

## Texto y maquetación

| Regla | Por qué |
|-------|---------|
| Texto **fuera** de la imagen (capa editable) | Cambios, tipografía KDP, accesibilidad |
| Márgenes de seguridad (print): ~0.5" del borde de recorte; sangrado 0.125" si el color llega al filo | Requisitos KDP Print |
| Evitar texto crítico en el lomo hasta saber el **page count** final | El lomo depende del nº de páginas y papel |
| Tipografía con **licencia de embedding** | PDF/ebook comercial |
| Lectura en voz alta ya validada (v2.1) | Contenido; la maqueta KDP solo empaqueta |

Estructura del álbum medio (~48) se mantiene; el PDF KDP puede ser:

- **una página de libro = una página impresa**, o  
- **doble página (spread)** si el diseño lo pide (decisión de diseño).

---

## Ebook (Kindle)

- Libros ilustrados infantiles: pipeline habitual **fixed layout**
  (Kindle Kids’ Book Creator, o EPUB fixed → KPF, según flujo actual de Amazon).
- Cover ebook: ratio típico orientativo **1.6:1** (p. ej. 2560×1600); no usar
  la cubierta con lomo del paperback.
- Probar en **Kindle Previewer** antes de publicar.
- Table of contents mínima si aplica; en álbum a veces solo portada + inicio.

---

## Amazon KDP — contenido generado con IA

Amazon exige **declarar** si el texto y/o las imágenes fueron generados con IA
(en todo o en parte). Este proyecto usa:

- **Texto:** redactado/editado en proceso creativo humano + herramientas;
  declarar según el porcentaje real al publicar.
- **Imágenes:** generadas/editadas con **xAI Imagine** (y posibles retoques).
  → En la práctica del piloto: **declarar imágenes generadas con IA**.

No falsear derechos. Guardar registro de prompts/refs en el repo
(`paginas.md`, `art/STYLE_BIBLE.md`, hoja de personajes) como expediente
de producción.

*(Revisar el formulario actual de KDP al momento de la subida; la política se actualiza.)*

---

## Metadatos (borrador Libro 1)

| Campo | Valor provisional |
|-------|-------------------|
| Título | Yamaranguila |
| Subtítulo | El agua de la pirámide |
| Serie | Ciudades de Honduras (título de serie por fijar en ficha) |
| Autores / ilustración | Por definir en ficha legal |
| Idioma | Español |
| Categorías | Infantil · geografía/cultura · aventura suave |
| Edad | 4–7 años |
| Keywords | Honduras, Yamaranguila, cuento infantil, pirámide, agua, Intibucá, … |
| ISBN | KDP free ISBN (print) y/o propio |

---

## Checklist pre-subida

### Creativo
- [ ] Texto final aprobado en voz alta
- [ ] Arte consistente aprobado página a página
- [ ] Portada ebook + cubierta print

### Técnico print
- [ ] Trim size elegido
- [ ] PDF interiores 300 DPI, sangrado si aplica, fuentes embebidas
- [ ] Cubierta según plantilla KDP del trim y page count
- [ ] Probar con el **preflight / previewer** de KDP

### Técnico ebook
- [ ] Archivo fixed-layout validado en Kindle Previewer
- [ ] Cover ebook correcto
- [ ] Metadatos y categorías

### Legal / cuenta
- [ ] Declaración de contenido IA
- [ ] Derechos de texto e ilustraciones
- [ ] Precio y regalías

---

## Flujo de trabajo a partir de ahora

```
1. Lista de correcciones de arte (consistencia)
2. Retocar pages en art/pages/ (res actual + ancla de personajes)
3. Aprobar set en maqueta de trabajo
4. Decidir trim KDP + export alta resolución
5. PDF print + paquete ebook
6. Portadas
7. Subida KDP + declaración IA + preview
```

No saltar del paso 2 al 5 sin aprobación visual: el coste de rehacer
48 páginas a 300 DPI es alto.

---

## Archivos del piloto

| Archivo | Rol |
|---------|-----|
| `libros/01-piloto/paginas.md` | Texto canónico |
| `libros/01-piloto/art/pages/` | Maestros de ilustración (trabajo) |
| `libros/01-piloto/maqueta/Yamaranguila-maqueta.pdf` | Maqueta interna |
| `scripts/maqueta_yamaranguila.py` | Regenerar maqueta interna |
| `docs/PUBLICACION_KDP.md` | Este documento |
