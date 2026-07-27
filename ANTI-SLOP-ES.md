# REFERENCIA ANTI-SLOP — ESPAÑOL

Guía de campo para detectar y eliminar patrones de escritura generada por IA **en español**. Reemplaza a `ANTI-SLOP.md` (que documenta el slop del inglés y no aplica aquí).

"Slop" = texto que se lee como output de LLM sin editar: baja densidad de información, estructura predecible, y vocabulario que ningún humano usaría en ese contexto.

**Advertencia clave:** el slop del español NO es la traducción del slop del inglés. "Utilizar" es slop en inglés ("utilize") pero palabra perfectamente normal en español. En cambio, el español tiene categorías de slop que el inglés no tiene: el abuso del gerundio, los adverbios en -mente en racimo, y los **calcos del inglés**.

---

## NIVEL 1: Prohibidas — reescribir la oración

Estadísticamente sobrerrepresentadas en output de LLM en español. Si aparece una, reescribe la oración.

| Mata esto | Escribe esto |
|---|---|
| sumergirse en (metafórico) | describir la acción concreta |
| adentrarse en (metafórico) | entrar, meterse, empezar |
| desentrañar | descubrir, entender, resolver |
| un sinfín de | muchos, incontables (o el número real) |
| una miríada de | muchos |
| plétora | abundancia, montón |
| crisol de | (describe la mezcla real) |
| tapiz de | (describe la cosa real) |
| un abanico de | varias, distintas |
| una amplia gama de | varios, muchos |
| paradigma | modelo, esquema |
| sinergia | (borra la oración y empieza de nuevo) |
| holístico | completo, integral |
| catalizador | detonante, causa, chispa |
| yuxtaponer | contrastar, poner junto a |
| inquebrantable | firme (o muestra la firmeza) |
| un festín para los sentidos | (describe qué se ve, huele, oye) |
| marcar un antes y un después | (di qué cambió, concretamente) |
| en el corazón de | en el centro de, en medio de |
| se erige | está, se levanta |
| testimonio de ("es testimonio de") | demuestra, prueba |

## NIVEL 2: Sospechosas en racimos

Bien aisladas. Tres en un párrafo = reescribir el párrafo.

vibrante, bullicioso, imponente, majestuoso, fascinante, cautivador,
envolvente, impresionante, sin igual, innegable, palpable, abrumador,
sobrecogedor, crucial, fundamental, profundo, intrincado, meticuloso,
resonar (metafórico), forjar (metafórico), albergar (travel-slop),
dejar huella, emblemático, icónico

## NIVEL 3: Frases de relleno — borrar siempre

| Frase | Qué hacer |
|---|---|
| "Cabe destacar que..." | Di la cosa y ya. |
| "Es importante mencionar/señalar que..." | Di la cosa y ya. |
| "Vale la pena destacar..." | Di la cosa y ya. |
| "Además, ..." / "Asimismo, ..." (inicio de párrafo) | Borra o une las ideas. |
| "En resumen, ..." / "En conclusión, ..." | Borra. El lector sabe que termina. |
| "Sin más preámbulos..." | Borra. |
| "Hoy en día..." / "En la actualidad..." / "En el mundo actual..." | Borra la cláusula entera. |
| "En un mundo donde..." | (apertura de tráiler de cine; borra) |
| "Al fin y al cabo..." / "A fin de cuentas..." (en narración) | Borra. |
| "No es solo X, sino Y" | Fórmula retórica de IA. Reestructura. |
| "Dicho esto, ..." | Borra. |

---

## CALCOS DEL INGLÉS (categoría exclusiva del español)

Delatan que la prosa fue "pensada en inglés". Los LLM los producen constantemente porque su entrenamiento está dominado por el inglés.

| Calco | Español correcto |
|---|---|
| eventualmente (por "eventually") | finalmente, al final, con el tiempo |
| hacer sentido | tener sentido |
| en adición | además |
| al final del día (metafórico) | a fin de cuentas (o borra) |
| tomar acción | actuar |
| tomar ventaja de | aprovechar |
| tomar lugar | ocurrir, celebrarse |
| estar supuesto a | deber, tener que |
| aplicar para (un puesto) | solicitar, postularse |
| es acerca de | trata de, se trata de |
| cerró sus ojos | cerró los ojos |
| lavó sus manos | se lavó las manos |
| sacudió la cabeza (por "shook his head") | negó con la cabeza |
| asintió con su cabeza | asintió |
| Voz pasiva calcada: "el brazalete fue entregado por el dron" | pasiva refleja o activa: "el dron entregó el brazalete" |

## GERUNDIO: el tic número uno

El inglés vive del progresivo (-ing); el español no. El abuso de gerundio aplana el ritmo y delata traducción mental.

- **Gerundio de posterioridad (siempre incorrecto):** "Disparó, matándolo al instante." → "Disparó y lo mató al instante."
- **Dos gerundios seguidos:** "Salió corriendo, gritando su nombre." → reestructura.
- **Gerundio como conector perezoso:** "Caminaba pensando que..., sintiendo que..., recordando que..." → oraciones plenas.
- **Umbral mecánico:** más de ~12 gerundios por mil palabras dispara penalización en `evaluate.py`.

## ADVERBIOS EN -MENTE

El equivalente español de los "-ly adverbs". Uno de vez en cuando está bien; en racimo, la prosa suena a manual.

- "Caminó lentamente hacia la puerta, abriéndola cuidadosamente y mirando nerviosamente hacia atrás." → tres pecados en una oración.
- Reemplaza con: verbo más preciso ("caminó" lento → "se arrastró"), detalle físico, o simplemente corta.
- **Umbral mecánico:** más de ~4 por mil palabras dispara penalización.

---

## CLICHÉS DE FICCIÓN (los delatores narrativos)

Fórmulas que ningún buen narrador humano escribiría dos veces. `evaluate.py` los caza con regex:

- "una sensación de X"
- "no pudo evitar sentir/pensar"
- "el peso de la situación / de sus palabras"
- "el aire estaba cargado de tensión"
- "sus ojos se abrieron como platos / de par en par"
- "una ola de pánico lo invadió / la recorrió"
- "una punzada de culpa"
- "el corazón le latía con fuerza / le martilleaba en el pecho"
- "un escalofrío le recorrió la espalda"
- "un nudo en la garganta / el estómago"
- "una sonrisa cómplice" / "una mirada cómplice"
- "sintió una oleada / un torrente / un destello de"
- "el silencio era ensordecedor / se volvió sepulcral"
- "dejó escapar un suspiro que no sabía que contenía"
- "algo oscuro/antiguo despertó en su interior"
- "se le heló la sangre"
- "el tiempo pareció detenerse"
- "un sudor frío"

**La cura es siempre la misma:** en lugar de nombrar la emoción o usar la fórmula, muestra el efecto físico específico DE ESTE personaje EN ESTA escena. El empresario no siente "una ola de pánico": aprieta el volante hasta que la costura del cuero le marca la palma.

## CONTAR vs. MOSTRAR (patrones de "telling")

Detectados mecánicamente:

- "se sentía / estaba / parecía + [emoción]": *se sentía culpable, estaba furioso, parecía nervioso*
- Adverbios emocionales: *tristemente, nerviosamente, desesperadamente*

## FÓRMULAS RETÓRICAS ESTRUCTURALES

- "No digo que X. Digo que Y."
- "Hay una diferencia."
- "No son lo mismo."
- "No solo X, sino Y."
- "No por X, sino por Y." (en narración)

Una vez puede ser voz. Tres veces es plantilla.

---

## CONVENCIONES DEL ESPAÑOL LITERARIO (no negociables)

1. **Diálogo con raya (—):** `—Súbete —dijo—. Nos queda camino.` Sin espacio entre la raya y la primera palabra. Los incisos del narrador van entre rayas.
2. **Comillas angulares « »** para citas dentro de la narración (un letrero, un versículo: «Pero yo a Jehová miraré...»). Comillas inglesas " " solo como tercer nivel de anidación.
3. **Signos de apertura ¿ ¡** siempre.
4. **Los diálogos NO llevan comillas inglesas.** Este es el error número uno de la prosa traducida del inglés.
