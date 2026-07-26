<!--
Fixture de test (Tarea 1d). NO es la voz de ninguna novela real -- es un
perfil mínimo, genérico, en español, para que el juez LLM de evaluate.py
tenga contra qué evaluar capítulos de prueba sin depender de voice.md de
"The Second Son of the House of Bells" (en inglés). Desacoplado a
propósito de cualquier trama, personaje o mundo real.
-->

# Perfil de voz (fixture de prueba)

## Parte 1: Guardarraíles (permanentes, cualquier novela)

Ver `deteccion_es.py` para las listas completas de nivel 1/2/3, clichés,
calcos del inglés y tics estructurales. Resumen para este fixture:

- Nada de vocabulario de nivel 1 (profundizar, tapiz, entramado, crisol,
  holístico, sinergia, palpable, insondable...).
- Sin clichés de ficción de la lista de `CLICHES_FICCION` (escalofrío por
  la espalda, peso de la ausencia, no pudo evitar sentir...).
- Sin calcos del inglés: nada de sujeto pronominal redundante, "estaba
  siendo", posesivo pegado a partes del cuerpo ("levantó su mano").
- Diálogo con raya (—), nunca comillas inglesas para diálogo.
- El sujeto pronominal se omite salvo que haga falta para desambiguar.

## Parte 2: Identidad de voz (mínima, de prueba)

### Tono

Directo, contenido. Observa antes de interpretar. No explica lo que la
escena ya mostró.

### Ritmo de oración

Alterna oraciones cortas (4-8 palabras) con alguna más larga de
acumulación (20+ palabras). Evita que tres oraciones seguidas tengan
estructura idéntica.

### Registro léxico

Vocabulario concreto y cotidiano. Objetos, oficios, lugares con nombre
propio. Nada de abstracciones grandilocuentes ("el vasto silencio del
universo"): si hay silencio, es el silencio de una habitación concreta.

### POV y tiempo verbal

Tercera persona limitada, pretérito. Un único punto de vista por capítulo
(cuál, lo define cada capítulo de prueba en su propio encabezado, no este
fixture).

### Convenciones de diálogo

Raya de apertura. Los incisos del narrador dentro del diálogo también van
con raya, pegados sin espacio antes del segundo guion. Sin adverbios de
manera pegados a los verbos de habla ("dijo tristemente"): si hace falta
la emoción, se muestra en la acción que acompaña la línea.

### Pasajes ejemplares

> —¿Trajiste la carpeta de Ibarra?
>
> —Acá está.
>
> Onofre la abrió sobre el escritorio y pasó las hojas una por una,
> despacio, comparando cada firma con la que tenía en la otra carpeta.

### Anti-ejemplares

> Ella no pudo evitar sentir un escalofrío que le recorrió la espalda,
> cargando el peso de una ausencia insondable, mientras levantaba su mano
> hacia la puerta que estaba siendo, de alguna manera, la última frontera
> entre ella y la verdad.

(Todo lo que hay en ese párrafo es exactamente lo que este perfil prohíbe:
clichés, calco del inglés, adverbio-mente implícito, léxico de nivel 1.)
