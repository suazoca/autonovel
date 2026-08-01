# STYLE_BIBLE — serie Ciudades de Honduras

Documento vivo. Fijar el look **antes** de generar páginas del Libro 1
para no romper continuidad.

## Público visual

- 4–7 años: formas claras, caras legibles, emociones obvias.
- Calidez diurna preferente; noche solo si es segura (lámparas, luna
  amable, adultos cerca).
- Sin terror, sin sangre, sin armas reales como foco.

## Estilo (provisional — ajustar en el piloto)

- Ilustración editorial infantil contemporánea.
- Línea suave; color luminoso; textura ligera (no hiperrealismo).
- Proporciones: niños con cabezas un poco grandes, manos expresivas;
  no “anime” extremo ni realismo adulto.
- Fondos con **lugar reconocible de Honduras** cuando el libro lo pida
  (árbol, costa, montaña, mercado, plaza, casa de adobe, etc.) sin
  convertirse en foto turística fría.
- La serie **no es bíblica**: un templo o fiesta solo como paisaje cultural
  si el libro lo pide, nunca como mensaje de fe.

## Paleta (provisional)

- Verdes de vegetación tropical / pino según región del libro.
- Cielos azules o atardeceres suaves (naranja-rosa, no apocalipsis).
- Acentos de color en ropa del protagonista (fijo por serie).
- Evitar neón y grain de cine noir.

## Personajes de serie

Héroes fijos en todos los libros (nombres de trabajo del piloto;
cambiar en semilla y aquí a la vez).

| Personaje | Edad aparente | Rasgos fijos (pelo, ropa, objeto) | No hacer |
|-----------|---------------|-------------------------------------|----------|
| **Noha** | ~6–7 | Pelo oscuro corto; **suéter coral/rojo** + **chaqueta oliva**; pantalón gris; zapatos café; a veces jarrito | No adultizar; no “elegido/a” con brillo mágico |
| **Ivana** | ~4–5 | Más baja; **dos moños/coletas con lazos mostaza**; camisa **mostaza** + chaqueta **lila**; pantalón morado; tenis rojos; mochila café | No solo cómica/torpe; ella también resuelve |
| **Abuelo Dale** | mayor, cálido | **Gorra gris** suave; chaqueta **azul** (parche en codo ok); bastón de apoyo; cara amable | No resuelve él solo el final; no caricatura de viejo frágil o gruñón |

**Ancla visual de serie:** `art/personajes/hoja-serie.jpg`  
(usar como referencia en `image_edit` para no romper caras/ropa).

**Objeto de serie:** jarrito de barro naranja con flores azules suaves.
En Yamaranguila empieza vacío y al final lleva agua.

**Libro 1 — objetos extra:** mapa viejo de la bisabuela Emilia (papel
doblado, dibujos suaves, sin texto legible en imagen); caja de herramientas
de madera del abuelo; carpa de camping; roca con Y en relieve; dos palancas;
dos manijas del ojo de agua. **Dale** en este libro suele verse en
llamada/recuerdo (vive lejos); silueta fija cuando aparece.

**Libro 1 (Yamaranguila) — clima de vestuario:** capas, chamarras, mejillas
rosas por el frío de altura; ropa de camping/camino; no ropa de playa.
Atardecer dorado en la prueba de la roca (≈ las 5).

## Prompt base de serie (plantilla)

Usar como prefijo de cada página; la página solo añade lo local.

```
Children's picture-book illustration, soft editorial style, warm light,
clear shapes, expressive friendly faces, ages 4-7 audience, Honduras
setting details when relevant, consistent characters, no text in image,
no watermark, no logo, no horror, no blood, no weapons focus
```

### Negativos sugeridos

```
text, caption, watermark, logo, photorealistic, horror, gore, scary face,
weapon focus, dark grim atmosphere, chaotic composition, extra fingers,
deformed hands, adult romance, brand names
```

## Publicación (ebook + KDP)

Ver `docs/PUBLICACION_KDP.md`. Resumen para quien genera arte:

- Texto del cuento **no** va pintado en la imagen (capa aparte en maqueta/KDP).
- Misma relación de aspecto en todo el libro.
- Consistencia de héroes/objetos > detalle de fondo.
- Los JPG actuales son **maestros de trabajo**; el print final pedirá
  ~300 DPI al tamaño de recorte (upscale o regeneración al cerrar).
- Contenido de imagen con IA: se declara al publicar en Amazon.

## Por página

1. Respetar esta bible.
2. Brief en español en `paginas.md` (qué se ve, encuadre, emoción).
3. Prompt en inglés o español según el generador; **misma información**
   que el brief + anclas de personaje.
4. No inventar personajes nuevos en el prompt si no están en el texto
   del libro.

## Continuidad entre libros

Misma silueta de héroes; puede cambiar ropa de viaje o un accesorio por
ciudad (gorra, mochila, flor local) sin reescribir la cara.
