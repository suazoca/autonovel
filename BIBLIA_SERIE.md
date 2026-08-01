# Biblia de la serie — Ciudades de Honduras (título de trabajo)

> **Nombre del archivo:** “biblia de serie” = documento de continuidad de
> producción (premisa, reglas, catálogo). **No** significa contenido
> bíblico ni religioso.

Serie de cuentos ilustrados para **niños y niñas de 4 a 7 años**.
Cada libro (formato de serie: **álbum medio ~40–48 páginas**; el piloto
*Yamaranguila* va a **~48**) parte del **nombre de una ciudad de Honduras**,
su origen posible y su **significado**, y de ahí nace la aventura.

Base de código: rama `ciudades-hn` (fork de `novela2` / framework autonovel).
Base de storytelling: **no** es la craft de novela adulta de `novela2` —
ver `CRAFT_INFANTIL.md`.

## Qué es y qué no es esta serie

| Sí | No |
|----|-----|
| Cultura local, geografía, naturaleza, comunidad | Serie **bíblica** o de enseñanza religiosa |
| Topónimos, lenguas, leyendas de lugar (laicas) | Alegoría de fe, milagros doctrinales, evangelización |
| Magia suave / misterio del **nombre del lugar** | Trama de conversión, reliquias, escritura sagrada como motor |
| Pertenencia a Honduras | Continuación temática de *La ostensión* u otras novelas de fe del repo |

Si un templo, fiesta o costumbre aparece, es **paisaje cultural** (como un
mercado o un árbol), no el mensaje del libro. El corazón de cada título es
el **significado del nombre de la ciudad** y un problema del tamaño de un
niño, no una lección de catecismo.

## Público y uso

- Edad: 4–7 años.
- Lectura ideal: **en voz alta** (adulto + niño) o lector inicial acompañado.
- Emoción: calidez, curiosidad, humor suave, pertenencia. Sin terror, sin
  violencia gráfica, sin moralina pesada (ni moralina religiosa).
- Duración de lectura: un libro en una o varias sesiones cortas.

## Motor de cada libro

1. Llegan (o viven) en una **ciudad real de Honduras**.
2. Alguien nombra el lugar; el nombre **significa algo** (lectura poética
   declarada en la semilla del libro).
3. Ese significado se vuelve **magia suave / misterio / ayuda concreta**
   (no sistema de magia de fantasía épica).
4. Hay un **problema del tamaño de un niño** (perderse un poco, un amigo
   triste, un árbol en peligro, no entender a los mayores, etc.).
5. Los protagonistas **hacen algo** (no solo reciben el regalo de un adulto).
6. Cierre cálido + eco del nombre +, si aplica, plant del siguiente libro.

### Etimología (regla de honestidad)

Muchos topónimos tienen varias teorías (lenguas indígenas, español, leyenda).
En cada libro:

- Elegir **una lectura** para la historia.
- Declararla en la semilla: *“En este libro decimos que X significa Y.”*
- Opcional: nota breve para adultos al final (otras teorías / fuentes).

No presentar una etimología dudosa como verdad académica en el cuerpo del cuento.

## Continuidad de la serie (fijada en el piloto)

- [x] **Mismos héroes** en cada ciudad: dos hermanos + su abuelo.
- [x] **Viaje / visitas** (con el abuelo o con su consejo): cada libro =
  una ciudad de Honduras. En el piloto Dale está **lejos** y ayuda por
  teléfono; en otros títulos puede ir con ellos.
- [x] Recurrente: el abuelo **nombra** (lectura poética del topónimo);
  objeto de viaje (**jarrito** u similar). Libro 1 añade el **mapa de
  Emilia**. El abuelo ayuda y calma; **los niños resuelven el núcleo**
  del problema.

Héroes fijos: **Noha** e **Ivana** (hermanos) y el **abuelo Dale** —
ver `libros/01-piloto/semilla.md` y `art/STYLE_BIBLE.md`.

## Catálogo (borrador — rellenar)

| # | Ciudad | Significado elegido (provisional) | Estado |
|---|--------|-------------------------------------|--------|
| 1 | **Yamaranguila** (Intibucá) | Agua de la pirámide (*Zabalanquíra*) | álbum ~48; texto+arte; **maqueta PDF** en `libros/01-piloto/maqueta/` |
| 2 | | | |
| 3 | | | |

## Formato de página (álbum medio ~40–48)

Cada libro se planifica por **página o doble página**, no por “capítulo de novela”.
Meta de serie: **álbum medio** (cómodo a 4–7 en una o dos lecturas). Evitar
inflar a 70 solo por relleno.

Archivo canónico por libro: `libros/NN-slug/paginas.md`

Columnas mínimas:

| pág | texto (voz alta) | brief de ilustración | prompt de imagen | page-turn / notas |

Ver plantilla en `libros/_plantilla/paginas.md`.

## Arte

- Biblia visual de la serie: `art/STYLE_BIBLE.md`
- Prompts: base de serie + prompt por página (sin contradecir la bible)
- El dibujo cuenta lo que el texto no dice.

## Relación con el framework autonovel

| Capa | Qué usar |
|------|----------|
| API, scripts, tests | heredados de `novela2` |
| Semilla / fundación | adaptar a infantil; no reusar *La ostensión* |
| Outline 46 caps / Save the Cat denso | **no** para estos libros |
| CRAFT.md adulto | solo referencia; primario = `CRAFT_INFANTIL.md` |
| Revisión / juez | rúbrica infantil (pendiente cablear en evaluate) |
| Canon | útil entre libros de la serie (`canon.md` de serie + emergente) |
