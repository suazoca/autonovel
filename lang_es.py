#!/usr/bin/env python3
"""
lang_es.py — Listas de detección de slop para ESPAÑOL.

Reemplazo directo de las listas en inglés de evaluate.py.
Mantiene los MISMOS nombres de variables, así que evaluate.py
solo necesita: `from lang_es import *` en lugar de definir
las listas en inglés.

Basado en la metodología de slop-forensics / EQ-Bench, adaptada
a los patrones estadísticos del output de LLMs en español.
"""

# ---- NIVEL 1: Prohibidas — reescribir la oración si aparecen ----
# Palabras/frases sobrerrepresentadas en output de LLM en español
# que casi nunca aparecen en prosa humana de ficción.
# NOTA: "utilizar" NO está aquí — en español es palabra normal,
# a diferencia de "utilize" en inglés. No copiar la lista inglesa a ciegas.

TIER1_BANNED = [
    "sumergirse en",        # metafórico ("sumergirse en sus pensamientos")
    "adentrarse en",        # metafórico
    "desentrañar",
    "un sinfín de",
    "una miríada de",
    "plétora",
    "crisol de",
    "tapiz de",
    "un abanico de",
    "una amplia gama de",
    "paradigma",
    "sinergia",
    "holístico",
    "catalizador",
    "yuxtaponer",
    "inquebrantable",
    "un festín para los sentidos",
    "marcar un antes y un después",
    "en el corazón de",     # travel-slop ("en el corazón de la ciudad")
    "se erige",             # travel-slop
    "testimonio de",        # calco de "a testament to"
]

# ---- NIVEL 2: Sospechosas en racimos (3+ en un párrafo = reescribir) ----

TIER2_SUSPICIOUS = [
    "vibrante", "bullicioso", "bulliciosa", "imponente", "majestuoso",
    "majestuosa", "fascinante", "cautivador", "cautivadora", "envolvente",
    "impresionante", "sin igual", "innegable", "palpable", "abrumador",
    "abrumadora", "sobrecogedor", "sobrecogedora", "crucial", "fundamental",
    "profundo", "profunda", "intrincado", "intrincada", "meticuloso",
    "meticulosa", "resonar", "resonaba", "forjar", "albergar", "alberga",
    "dejar huella", "emblemático", "emblemática", "icónico", "icónica",
]

# ---- NIVEL 3: Frases de relleno — borrar siempre ----
# (regex, se evalúan con IGNORECASE | MULTILINE)

TIER3_FILLER = [
    r"cabe (destacar|se\u00f1alar|mencionar|resaltar)( que)?",
    r"es importante (destacar|se\u00f1alar|mencionar|notar|recalcar)( que)?",
    r"vale la pena (mencionar|destacar|se\u00f1alar)",
    r"^adem\u00e1s,?\s",
    r"^asimismo,?\s",
    r"^por otro lado,?\s",
    r"^en primer lugar,?\s",
    r"^en resumen,?\s",
    r"^en conclusi\u00f3n,?\s",
    r"sin m\u00e1s pre\u00e1mbulos",
    r"hoy en d\u00eda",
    r"en la actualidad",
    r"en el mundo (actual|moderno|de hoy)",
    r"en un mundo (donde|en el que)",
    r"al fin y al cabo",
    r"a fin de cuentas",
    r"no es (solo|s\u00f3lo) .+, sino",
    r"como se mencion\u00f3 anteriormente",
    r"dicho esto,?\s",
]

# ---- Conectores de transición al inicio de párrafo ----
# (se mide la PROPORCIÓN de párrafos que abren con estos;
#  "sin embargo" es legítimo en buena prosa, el umbral lo regula)

TRANSITION_OPENERS = [
    "además", "asimismo", "sin", "no", "por", "de", "igualmente",
    "consecuentemente", "adicionalmente", "similarmente",
]
# Nota: "sin embargo", "no obstante", "por lo tanto", "por consiguiente",
# "de igual manera" son bigramas; evaluate.py compara solo la primera
# palabra, por eso arriba aparecen "sin", "no", "por", "de".
# Si prefieres precisión de bigramas, ver TRANSITION_OPENERS_BIGRAM.

TRANSITION_OPENERS_BIGRAM = [
    "sin embargo", "no obstante", "por lo tanto", "por consiguiente",
    "por otro lado", "de igual manera", "de este modo", "dicho esto",
    "además", "asimismo", "igualmente", "adicionalmente",
]

# ---- Clichés de ficción que delatan origen de máquina (español) ----

FICTION_AI_TELLS = [
    r"una sensaci\u00f3n de \w+",
    r"no pud[oa] evitar (sentir|pensar|notar)",
    r"el peso de (la|el|sus?) \w+",
    r"el aire (estaba cargado|era denso|se volvi\u00f3 denso)",
    r"(sus ojos se abrieron|abri\u00f3 los ojos) (de par en par|como platos)",
    r"una (ola|oleada) de \w+ (l[oa]s? )?(invadi\u00f3|recorri\u00f3|inund\u00f3|envolvi\u00f3)",
    r"una punzada de \w+",
    r"el coraz\u00f3n le (lat\u00eda|golpeaba|martilleaba|retumbaba)( con fuerza| en el pecho| desbocado)?",
    r"un escalofr\u00edo (le )?recorri\u00f3 (su |la )?(espalda|columna|cuerpo)",
    r"un nudo en (la garganta|el est\u00f3mago)",
    r"una (sonrisa|mirada) c\u00f3mplice",
    r"sinti\u00f3 (una oleada|un torrente|una punzada|un destello|una descarga) de",
    r"el silencio (era|se volvi\u00f3|se hizo|se torn\u00f3) (pesado|denso|ensordecedor|sepulcral|opresivo)",
    r"dej\u00f3 escapar (un suspiro|el aire) que no sab\u00eda que (conten\u00eda|estaba conteniendo|hab\u00eda estado conteniendo)",
    r"algo (oscuro|antiguo|primitivo|innombrable) (se agit\u00f3|despert\u00f3|se removi\u00f3)",
    r"se le hel\u00f3 la sangre",
    r"el tiempo (pareci\u00f3|pareci\u00f3 que se) (detenerse|deten\u00eda|ralentiz\u00f3)",
    r"un sudor fr\u00edo",
    r"(cabello|melena) (azabache|dorad[oa]|platead[oa]) (ca\u00eda|se derramaba) en cascada",
    r"(penetrantes|profundos) ojos (azules|verdes|grises|oscuros|negros)",
]

# ---- Tics estructurales — fórmulas retóricas de composición IA ----

STRUCTURAL_AI_TICS = [
    r"[Nn]o (digo|estoy diciendo|sugiero) que .{3,40}[.;,] (digo|estoy diciendo|sugiero)",
    r"lo (que|cual) significa que o .{3,40} o ",
    r"[Hh]ay una diferencia\.",
    r"[Nn]o (son|es) lo mismo\.",
    r"[Nn]o (solo|s\u00f3lo|simplemente|meramente) .{3,40}, sino ",
    r"[Nn]o (por|de|desde) .{3,40}, sino (por|de|desde)",
]

# ---- Detectores de CONTAR en vez de MOSTRAR (emociones nombradas) ----

TELLING_PATTERNS = [
    r"\b(?:se sent\u00eda|se sinti\u00f3|estaba|parec\u00eda|se ve\u00eda|luc\u00eda) (?:triste|feliz|content[oa]|enojad[oa]|enfadad[oa]|furios[oa]|nervios[oa]|asustad[oa]|aterrad[oa]|aterrorizad[oa]|ansios[oa]|culpable|celos[oa]|desesperad[oa]|aliviad[oa]|confundid[oa]|avergonzad[oa]|orgullos[oa]|amargad[oa]|derrotad[oa]|esperanzad[oa]|sol[oa]|abatido|abatida|eufóric[oa]|horrorizad[oa]|indignad[oa])\b",
    r"\b(?:tristemente|alegremente|nerviosamente|furiosamente|ansiosamente|desesperadamente|amargamente|felizmente|temerosamente|angustiosamente|melanc\u00f3licamente)\b",
]

# ---- NUEVO (solo español): calcos del inglés ----
# Delatan traducción mental desde el inglés. No existen en el
# framework original porque el inglés no tiene este problema.

CALCOS_INGLES = [
    r"\beventualmente\b",            # falso amigo de "eventually" (= finalmente)
    r"\bhac(e|en|\u00eda|er) sentido\b",  # calco de "make sense" (correcto: tener sentido)
    r"\ben adici\u00f3n\b",              # calco de "in addition" (correcto: además)
    r"al final del d\u00eda",            # calco de "at the end of the day"
    r"\btomar (acci\u00f3n|ventaja|lugar)\b",  # take action/advantage/place
    r"\best(\u00e1|ar|aba) supuesto a\b",     # calco de "supposed to"
    r"\baplicar para\b",             # calco de "apply for" (correcto: solicitar)
    r"\bes acerca de\b",             # calco de "it's about"
    r"(cerr\u00f3|abri\u00f3|entrecerr\u00f3|frot\u00f3) sus ojos",  # posesivo redundante (correcto: los ojos)
    r"sacudi\u00f3 (su|la) cabeza",       # calco de "shook his head" (correcto: negó con la cabeza)
    r"asinti\u00f3 con su cabeza",        # redundante (correcto: asintió)
]

# ---- Densidades específicas del español ----
# Umbrales para métricas nuevas que evaluate.py (versión ES) calcula:
#
#   Adverbios en -mente: > 4 por 1000 palabras = penalizar.
#     (El tic núm. 1 junto con el gerundio de la prosa débil en español.)
#
#   Gerundios (-ando/-iendo/-yendo): > 12 por 1000 palabras = penalizar.
#     (El abuso de gerundio aplana el ritmo y delata prosa de máquina
#      o traducción del inglés, que abusa del progresivo.)

UMBRAL_MENTE_X1000 = 4.0
UMBRAL_GERUNDIO_X1000 = 12.0

# ---- Nota sobre longitud de oraciones ----
# La oración española media es ~15-20% más larga que la inglesa.
# El coeficiente de variación (CV) sigue siendo la métrica correcta
# y el umbral de 0.3 de evaluate.py funciona sin cambios: mide
# UNIFORMIDAD, no longitud absoluta. No requiere ajuste.

# ---- Instrucción de idioma para los jueces LLM ----
# Se antepone a todos los prompts de evaluación (call_judge).

ES_JUDGE_NOTE = """IDIOMA: Esta novela está escrita en ESPAÑOL. Evalúa la prosa
según las normas del español literario, no del inglés:
- El diálogo usa raya (—), no comillas. Esto es CORRECTO, no lo penalices.
- Vigila y penaliza: abuso del gerundio, exceso de adverbios en -mente,
  calcos sintácticos del inglés (voz pasiva excesiva, posesivos
  redundantes como "cerró sus ojos", orden de palabras anglicado),
  falsos amigos ("eventualmente" por "finalmente", "hacer sentido").
- La variedad del español debe ser consistente con lo definido en
  voice.md (variedad narrativa neutra latinoamericana; los diálogos
  pueden variar por personaje según su origen).
- Los signos de apertura ¿ ¡ son obligatorios.
Responde tus evaluaciones en el mismo formato JSON solicitado.

"""
