# Voice Profile

This file has two parts:
1. **Guardrails** -- universal rules to avoid AI-generated slop. These
   apply to ALL voices and are non-negotiable.
2. **Voice Identity** -- the specific voice for THIS novel. Generated
   during the foundation phase. Could be anything: dense and mythic,
   spare and brutal, warm and whimsical. The voice emerges from the
   story's needs.

---

## Part 1: Guardrails (permanent, all novels)

These are the cliff edges. Stay away from them regardless of voice.

### Tier 1: Banned words -- kill on sight

These are statistically overrepresented in LLM output vs. human writing.
If one appears, rewrite the sentence. No exceptions.

| Kill this         | Use instead                                    |
|-------------------|------------------------------------------------|
| delve             | dig into, examine, look at                     |
| utilize           | use                                            |
| leverage (verb)   | use, take advantage of                         |
| facilitate        | help, enable, make possible                    |
| elucidate         | explain, clarify                               |
| embark            | start, begin                                   |
| endeavor          | effort, try                                    |
| encompass         | include, cover                                 |
| multifaceted      | complex, varied                                |
| tapestry          | (describe the actual thing)                    |
| testament to      | shows, proves, demonstrates                    |
| paradigm          | model, approach, framework                     |
| synergy           | (delete the sentence and start over)           |
| holistic          | whole, complete, full-picture                  |
| catalyze          | trigger, cause, spark                          |
| juxtapose         | compare, contrast, set against                 |
| nuanced (filler)  | (cut it -- if it's nuanced, show how)          |
| realm             | area, field, domain                            |
| landscape (metaphorical) | field, space, situation                 |
| myriad            | many, lots of                                  |
| plethora          | many, a lot                                    |

### Tier 2: Suspicious in clusters

Fine alone. Three in one paragraph = rewrite that paragraph.

robust, comprehensive, seamless, cutting-edge, innovative, streamline,
empower, foster, enhance, elevate, optimize, pivotal, intricate,
profound, resonate, underscore, harness, navigate (metaphorical),
cultivate, bolster, galvanize, cornerstone, game-changer, scalable

### Tier 3: Filler phrases -- delete on sight

These add zero information. The sentence is always better without them.

- "It's worth noting that..." -> just state it
- "It's important to note that..." -> just state it
- "Importantly, ..." / "Notably, ..." / "Interestingly, ..." -> just state it
- "Let's dive into..." / "Let's explore..." -> start with the content
- "As we can see..." -> they can see
- "Furthermore, ..." / "Moreover, ..." / "Additionally, ..." -> and, also, or just start
- "In today's [fast-paced/digital/modern] world..." -> delete the clause
- "At the end of the day..." -> delete
- "It goes without saying..." -> then don't say it
- "When it comes to..." -> just talk about the thing
- "One might argue that..." -> argue it or don't
- "Not just X, but Y" -> restructure (the #1 LLM rhetorical crutch)

### Structural slop patterns

These are the shapes that betray machine origin. Avoid them in any voice.

**Paragraph template machine**: Don't repeat the same paragraph
structure (topic sentence -> elaboration -> example -> wrap-up).
Vary it. Sometimes the point comes last. Sometimes a paragraph is
one sentence. Sometimes three long ones in a row.

**Sentence length uniformity**: If every sentence is 15-25 words,
it reads as synthetic. Mix in fragments. And long, winding,
clause-heavy sentences that carry the reader through a thought
the way a river carries a leaf. Then a short one.

**Transition word addiction**: If consecutive paragraphs start with
"However," "Furthermore," "Additionally," "Moreover," "Nevertheless"
-- rewrite. Start with the subject. Start with action. Start with
dialogue. Start with a sense detail.

**Symmetry addiction**: Don't balance everything. Three pros, three
cons, five steps -- that's a tell. Real writing is lumpy. Some
sections are long because they need to be. Some are two lines.

**Hedge parade**: "may," "might," "could potentially," "it's possible
that" -- pick one per page, max. State things or don't.

**Em dash overload**: One or two per page is fine. Five per paragraph
is a dead giveaway. Use commas, parentheses, or two sentences instead.

**List abuse**: Prose, not bullets. If the scene calls for a list
(a merchant's inventory, a spell's components), earn it. Don't
default to bullet points because it's easy.

### The smell test

After writing any passage, ask:
- Read it aloud. Does it sound like a person talking?
- Is there a single surprising sentence? Human writing surprises.
- Does it say something specific? Could you swap the topic and the
  words would still work? Specificity kills slop.
- Would a reader think "AI wrote this"? If yes, rewrite.

---

## Part 2: Voice Identity (generated per novel)

<!-- Everything below is discovered during the foundation phase.
The agent proposes a voice that serves THIS story, writes exemplar
passages, and calibrates against them throughout drafting. -->

### Tone
Frío de laboratorio con una grieta que crece. La voz suena a informe pericial escrito por alguien que empieza a no confiar en sus propios instrumentos: precisa, escéptica, sin adorno, y por eso mismo cada vez que se detiene de más en algo, el lector sabe que ahí duele.

### Sentence Rhythm
La narración avanza por mediciones: oraciones medianas, declarativas, que acumulan datos concretos hasta que uno no cierra. Cuando algo desestabiliza al protagonista, el ritmo no se acelera: se corta. Frases de tres, cuatro palabras. Verificaciones. Como quien repite un cálculo esperando otro resultado. Los párrafos técnicos pueden ser largos porque él piensa largo; los momentos emocionales son los más cortos del libro, porque él no tiene lenguaje para eso y la voz tampoco se lo presta. Nada de crescendos: la tensión sube por sustracción, por lo que la voz deja de decir.

### Vocabulary Register
Dos pozos léxicos en fricción, y esa fricción es el libro. Por un lado el vocabulario del protagonista: concreto, técnico, verificable —trama, fibra, datación, espectro, umbral de confianza, falso positivo, trazabilidad—. Por otro, el vocabulario del mundo que invade el suyo: ostensión, reliquia, custodia, lienzo, sepulcro. La voz usa el segundo con la incomodidad de él, casi entre comillas al principio, sin comillas al final: la conversión se mide en qué palabras dejan de resultarle ajenas. Prohibido el léxico devocional ornamental (sagrado misterio, luz divina) y prohibido el tecnicismo decorativo que no significa nada. Cada palabra técnica que aparece debe poder auditarse, como sus resultados. Español neutro con temperatura baja en la narración y en la mayoría de los diálogos; nada de castellano de traducción. EXCEPCIÓN deliberada: Chiara Fabbri (y Vidal, cuando le responde a ella) usan voseo rioplatense sostenido -- es marca de caracterización, la informalidad de Chiara ("informal con todos, incluido el abogado de Ginebra", ver characters.md) contra el "usted" de Ferrero, no un desliz de idioma. Confirmado en 10 de 46 capítulos (12, 13, 16, 17, 18, 22, 24, 28, 29, 30, 31, 34, 36, 37, 40, 45); el resto del reparto y la narración se mantienen neutros.

### POV and Tense
Tercera persona limitada, pegada al cráneo del protagonista, en pretérito. Indirecto libre frecuente: sus razonamientos entran en la narración sin marcas, de modo que el lector hereda sus sesgos y descubre los engaños cuando él los descubre. La cámara nunca sabe más que él: no vemos al financista pensar, no vemos al traidor decidir. Regla dura: la voz registra lo que él percibe y lo que él calcula, nunca lo que él siente con nombre propio. Si está asustado, se le seca la boca o repite un control innecesario; la palabra "miedo" no aparece.

### Dialogue Conventions
Acotaciones mínimas: "dijo", a veces nada, a veces una acción física que reemplaza al adverbio. Los personajes no explican sus posiciones: las defienden de costado, y lo importante queda en lo que evitan contestar. Cada voz es distinguible sin etiqueta: el protagonista habla en condicionales y correcciones ("no exactamente", "depende de qué llames prueba"); la creyente hace preguntas simples que él tarda páginas en poder responder; el que se opone habla en consecuencias ("si esto sale mal, ¿quién lo paga?"); el técnico habla en procedimientos y plazos, sin pronombres emocionales; el abogado del financista habla perfecto, completo, sin una sola frase que pueda usarse en su contra. El financista, cuando aparece, es el que mejor conversa del libro: cita bien, escucha mejor, y tiene razón con una frecuencia incómoda.

### Reglas específicas de capítulo
<!-- Opcional. Reglas discrecionales para los capítulos de ESTA novela,
     más allá de Tono/Ritmo/Registro/Diálogo de arriba -- una por línea,
     texto plano. Las leen draft_chapter.py y gen_brief.py. Dejar vacío si
     no aplica ninguna; nada más abajo exige que esta sección esté llena. -->

### Exemplar Passages
Contó la fila porque contar era lo que hacía cuando algo no cerraba. Cuarenta y una personas entre la puerta y el edículo, avance promedio de un metro cada tres minutos, y adentro —lo había leído en el panel de la entrada, en tres idiomas— no había nada. Ese era el dato que no lograba ubicar. Una tumba vacía era, en su campo, la definición exacta de evidencia negativa: la ausencia de un cuerpo no prueba una resurrección igual que la ausencia de cerámica no prueba un incendio. Y sin embargo la fila existía. Cuarenta y una personas esperaban para ver un lugar donde no había nada, y ninguna parecía estar cometiendo un error de método. Se quedó veinte minutos más de lo que había planeado. Después, en el hotel, anotó la visita en la columna de tiempo perdido y no volvió a abrir esa planilla.

El modelo devolvió el resultado a las 4:12. Lino: siglo I, intervalo de confianza estrecho, compatible con la cuenca de Jerusalén. Hasta ahí, nada que un buen falsificador medieval no pudiera haber conseguido con una tela antigua. El problema empezaba en la segunda línea. Formación de imagen: el sistema había evaluado las once hipótesis de la literatura —contacto, vapor, pigmento, bajorrelieve calentado, radiación, las otras seis— y las había descartado todas. No proponía una duodécima. Vidal conocía ese comportamiento: era el que exhibía el modelo frente a datos corruptos. Corrió el diagnóstico de integridad. Limpio. Lo corrió de nuevo. Limpio. Eran las cinco menos cuarto y en algún punto de la última hora había dejado de buscar el error en los datos.

—¿Y si el resultado te dice que es del siglo XIII? —dijo Chiara. Estaba enrollando el cable del escáner, sin mirarlo, con el cuidado de quien guarda algo que no es suyo.
—Entonces es del siglo XIII.
—Te pregunto qué hacés vos. No qué hace el modelo.
Vidal revisó una calibración que ya había revisado.
—Publico —dijo.
—¿Y si te dice que no puede explicarlo?
—Los modelos no dicen eso.
Ella terminó con el cable, lo colgó del gancho, y recién entonces lo miró.
—Los tuyos tampoco, ¿no?

Quedaban nueve días para la ostensión y el punto 4 del protocolo seguía sin resolverse: la devolución. Ledda había calculado dos ventanas, una de once minutos durante el cambio de guardia y otra de seis durante la revisión del sistema de clima, y había recomendado la de seis porque tenía menos variables humanas. Vidal aprobó la de seis. Lo anotó en el registro con la fecha y la hora, como todo, y le llamó la atención su propia letra: firme, prolija, la letra de un hombre que documenta un procedimiento. En algún momento habría que ponerle otro nombre a lo que estaban documentando. Todavía no.

El certificado de confianza decía 0,97 y no había manera de saber por qué. Vidal pasó la noche tratando de extraer el razonamiento: qué rasgos había pesado el modelo, qué combinación de señales lo llevaba a esa cifra. Las herramientas de auditoría devolvían ruido. Un colega honesto —él mismo, seis meses atrás, frente al trabajo de otro— habría dicho que una certeza inauditable no es una certeza: es un artefacto, y se descarta. Escribió esa frase en el informe. La leyó. Era correcta. La dejó, porque era correcta, y se quedó mirándola un rato largo sin poder firmar debajo.

### Anti-Exemplars
*Demasiado místico —la voz nunca sugiere presencia sobrenatural ni la prosa se pone reverente:*
Al desplegar el lienzo, Vidal sintió que algo antiguo y enorme lo observaba desde la trama del lino. El rostro impreso en la tela parecía mirarlo a través de los siglos, y un escalofrío le recorrió la espalda: la ciencia, comprendió, tenía un límite, y él acababa de cruzarlo.

*Demasiado thriller de aeropuerto —la tensión de este libro nunca viene de la acción física ni de frases de teaser:*
Sesenta segundos. Eso era todo lo que tenían. Ledda desactivó el sensor con dedos de cirujano mientras las gotas de sudor le corrían por la sien. Si fallaban, no solo perderían la Síndone: perderían la vida. Vidal apretó los dientes. Que empiece el juego.

*Demasiado explicado —nadie, ni el narrador, formula el sentido de lo que pasa; la conversión se muestra en decisiones, no se declara:*
Fue entonces cuando Vidal entendió que la fe no era la conclusión de un razonamiento sino un salto, una decisión que se toma precisamente donde la evidencia termina. Toda su vida había exigido mecanismos, y ahora comprendía que había preguntas cuya respuesta no era un dato sino una entrega.

*Financista legible como villano —en esta voz es el hombre más razonable de cada escena, no una amenaza envuelta en cortesía:*
El hombre sonrió con frialdad desde el otro lado del escritorio, y en sus ojos grises Vidal creyó ver algo reptil, un cálculo sin fondo. "Usted trabajará para mí, doctor", dijo con voz sedosa, "y le conviene no hacer preguntas". Vidal supo, con una certeza helada, que acababa de firmar un pacto con el diablo.

*Emoción con nombre propio —la voz nunca etiqueta lo que él siente; lo registra en conducta:*
Vidal estaba profundamente perturbado. Una mezcla de miedo y fascinación lo invadió mientras leía el resultado, y sintió que su mundo racional se derrumbaba. La ansiedad no lo dejó dormir: por primera vez en su vida, el gran científico dudaba.

