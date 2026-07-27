# Perfil de Voz

Este archivo tiene dos partes:
1. **Barandillas** — reglas universales para evitar slop de IA en español.
   Aplican a TODAS las voces y no son negociables.
2. **Identidad de Voz** — la voz específica de ESTA novela. Se genera
   durante la fase de fundación. La voz emerge de las necesidades de
   la historia.

---

## Parte 1: Barandillas (permanentes, todas las novelas)

Estos son los acantilados. Mantente lejos de ellos sin importar la voz.

### Nivel 1: Palabras prohibidas — matar al verlas

Sobrerrepresentadas en output de LLM en español. Si aparece una,
reescribe la oración. Sin excepciones.

| Mata esto              | Usa esto                                    |
|------------------------|---------------------------------------------|
| sumergirse/adentrarse en (metafórico) | la acción concreta           |
| desentrañar            | descubrir, entender, resolver               |
| un sinfín de           | muchos (o el número real)                   |
| una miríada de         | muchos                                      |
| plétora                | montón, abundancia                          |
| crisol de              | (describe la mezcla real)                   |
| tapiz de               | (describe la cosa real)                     |
| un abanico de          | varias, distintas                           |
| una amplia gama de     | varios                                      |
| paradigma              | modelo, esquema                             |
| sinergia               | (borra la oración y empieza de nuevo)       |
| holístico              | completo, integral                          |
| catalizador            | detonante, causa                            |
| inquebrantable         | firme (o muestra la firmeza)                |
| marcar un antes y un después | (di qué cambió, en concreto)          |
| en el corazón de       | en el centro de, en medio de                |
| testimonio de          | demuestra, prueba                           |

### Nivel 2: Sospechosas en racimos

Bien aisladas. Tres en un párrafo = reescribir ese párrafo.

vibrante, bullicioso, imponente, majestuoso, fascinante, cautivador,
envolvente, impresionante, sin igual, innegable, palpable, abrumador,
sobrecogedor, crucial, fundamental, profundo, intrincado, meticuloso,
resonar (metafórico), albergar, dejar huella, emblemático, icónico

### Nivel 3: Relleno — borrar al verlo

- "Cabe destacar que..." → di la cosa y ya
- "Es importante mencionar que..." → di la cosa y ya
- "Además, ..." / "Asimismo, ..." al abrir párrafo → borra o une
- "En resumen..." / "En conclusión..." → borra
- "Hoy en día..." / "En un mundo donde..." → borra la cláusula
- "No es solo X, sino Y" → reestructura

### Calcos del inglés — prohibidos

- eventualmente (por *eventually*) → finalmente
- hacer sentido → tener sentido
- tomar acción / ventaja / lugar → actuar / aprovechar / ocurrir
- cerró **sus** ojos → cerró **los** ojos (posesivo redundante)
- sacudió la cabeza → negó con la cabeza
- asintió con su cabeza → asintió
- pasiva calcada ("fue entregado por") → activa o pasiva refleja

### Gerundio y -mente

- Gerundio de posterioridad: NUNCA ("disparó, matándolo" → "disparó y lo mató")
- Dos gerundios seguidos: NUNCA
- Máximo ~12 gerundios por mil palabras
- Máximo ~4 adverbios en -mente por mil palabras

### Clichés de ficción — prohibidos

una sensación de X · no pudo evitar sentir · el peso de X · el aire
cargado de tensión · ojos como platos / de par en par · una ola de X
lo invadió · una punzada de X · el corazón le martilleaba · un
escalofrío recorrió su espalda · un nudo en la garganta · sonrisa
cómplice · el silencio ensordecedor · un suspiro que no sabía que
contenía · algo oscuro despertó · se le heló la sangre · el tiempo
pareció detenerse · sudor frío

La cura: el efecto físico específico de ESTE personaje en ESTA escena.

### Emociones: mostrar, no nombrar

Prohibido: "se sentía culpable", "estaba furioso", "parecía nervioso",
"tristemente", "nerviosamente". Muestra el cuerpo, la acción, el diálogo.

### Léxico regional y accesibilidad (reglas del autor)

- Radio/comunicaciones: "copiado", nunca "cópialo".
- Los creyentes evangélicos ORAN. "Rezar" solo para personajes de
  contexto católico. (Distinción de registro crucial para el público
  de la obra.)
- Palabras que alejan al lector promedio: prohibidas cuando existe la
  forma llana ("crepitar" -> estática, sonar; "yermo" -> seco, vacío).
- La narración usa el registro léxico del personaje POV: un camionero
  no dice "tendones del antebrazo"; un médico sí puede.
- Verbos de máquina en registro latinoamericano: los motores rugen o
  rechinan (no "gruñen").

### Convenciones tipográficas del español

1. Diálogo con raya: —Súbete —dijo—. Nos queda camino.
2. Comillas angulares « » para citas dentro de narración.
3. Signos de apertura ¿ ¡ siempre.
4. Nunca comillas inglesas para diálogo.

---

## Parte 2: Identidad de Voz (generada en fundación — POR COMPLETAR)

> Variedad narrativa: español neutro latinoamericano.
> Diálogos: variedad dialectal por personaje (voseo hondureño para el
> empresario y el cardiólogo; castellano peninsular para la youtuber;
> español con interferencias para el limpiador afgano, el agricultor
> ucraniano y la piloto israelí).
>
> [El resto se genera con gen_world.py / voice_fingerprint.py durante
> la Fase 1 de la fundación.]
