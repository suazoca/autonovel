#!/usr/bin/env python3
"""
deteccion_es.py — Detección mecánica de prosa sintética en español.

Reemplaza las constantes de evaluate.py, que estaban calibradas para inglés.
No es una traducción: las huellas de IA son distintas en cada idioma.

Integración en evaluate.py:

    from deteccion_es import (
        NIVEL1_PROHIBIDAS as TIER1_BANNED,
        NIVEL2_SOSPECHOSAS as TIER2_SUSPICIOUS,
        NIVEL3_MULETILLAS as TIER3_FILLER,
        CONECTORES_APERTURA as TRANSITION_OPENERS,
        CLICHES_FICCION as FICTION_AI_TELLS,
        TICS_ESTRUCTURALES as STRUCTURAL_AI_TICS,
        PATRONES_CONTAR as TELLING_PATTERNS,
        CALCOS_DEL_INGLES,
        densidad_raya_parentetica,
        dividir_oraciones,
    )

Y en slop_score(), sustituir el conteo de rayas por:

    em_dash_density = densidad_raya_parentetica(text)

CRÍTICO: en español la raya (—) es el signo de diálogo. El contador
original de evaluate.py penalizaba cada capítulo dialogado por usar
correctamente la puntuación castellana. Aquí solo se penaliza la raya
parentética, que sí es un tic de IA.
"""

import re
import statistics

# ---------------------------------------------------------------------------
# NIVEL 1 — prohibidas
# ---------------------------------------------------------------------------

NIVEL1_PROHIBIDAS = [
    "profundizar", "abordar", "tapiz", "entramado", "crisol",
    "multifacético", "multifacética", "holístico", "holística",
    "catalizador", "catalizar", "sinergia", "innegable", "innegablemente",
    "palpable", "inefable", "indescriptible", "indecible", "yuxtaponer",
    "yuxtaposición", "insondable", "inconmensurable",
]

# Locuciones prohibidas (necesitan regex, no coinciden por token suelto)
NIVEL1_LOCUCIONES = [
    r"\bun abanico de\b",
    r"\bun sinf[íi]n de\b",
    r"\buna sinfon[íi]a de\b",
    r"\buna danza de\b",
    r"\bun ballet de\b",
    r"\btestimonio de\b",
    r"\ben [úu]ltima instancia\b",
    r"\bvasto[as]? (?:abismo|mundo|universo|silencio|espacio|paisaje)\b",
    r"\bpaisaje (?:emocional|pol[íi]tico|social|mental)\b",
]

# ---------------------------------------------------------------------------
# NIVEL 2 — sospechosas en racimo (3+ por párrafo)
# ---------------------------------------------------------------------------

NIVEL2_SOSPECHOSAS = [
    "robusto", "robusta", "integral", "fluido", "innovador", "innovadora",
    "potenciar", "fomentar", "impulsar", "optimizar", "crucial",
    "intrincado", "intrincada", "profundo", "profunda", "subrayar",
    "cultivar", "forjar", "tejer", "transformador", "transformadora",
    "revelador", "reveladora", "conmovedor", "conmovedora",
    "escalofriante", "sobrecogedor", "sobrecogedora", "inquietante",
    "imponente", "atemporal", "etéreo", "etérea", "ancestral", "primigenio",
]

# ---------------------------------------------------------------------------
# NIVEL 3 — muletillas
# ---------------------------------------------------------------------------

NIVEL3_MULETILLAS = [
    r"\bcabe (?:destacar|se[ñn]alar|mencionar|notar) que\b",
    r"\bvale la pena (?:mencionar|destacar|se[ñn]alar)\b",
    r"\bes importante (?:notar|destacar|se[ñn]alar|mencionar) que\b",
    r"\bno (?:es|era|fue) s[óo]lo .{3,60}?, sino\b",
    r"\bno s[óo]lo .{3,60}?, sino (?:que|tambi[ée]n)\b",
    r"\bm[áa]s que .{3,40}?, (?:es|era|fue)\b",
    r"\ben un mundo donde\b",
    r"\badentr[ée]monos en\b",
    r"\bexploremos\b",
    r"\bcomo podemos ver\b",
    r"\bal final del d[íi]a\b",
    r"\ben definitiva\b",
    r"\ba fin de cuentas\b",
    r"\bpor as[íi] decirlo\b",
    r"\ben cierto modo\b",
    r"\bde alguna manera\b",
    r"\blo cierto es que\b",
    r"\bsin lugar a dudas\b",
    r"\bno pudo evitar\b",
    r"^\s*(?:Adem[áa]s|Asimismo|Por otro lado|Sin embargo|No obstante|Por consiguiente),",
]

CONECTORES_APERTURA = [
    "sin", "además", "asimismo", "no", "por", "igualmente",
    "consecuentemente", "efectivamente", "ciertamente",
]

# ---------------------------------------------------------------------------
# Clichés de ficción
# ---------------------------------------------------------------------------

CLICHES_FICCION = [
    r"una sensaci[óo]n de \w+",
    r"no pudo evitar (?:sentir|pensar|preguntarse)",
    r"el peso de (?:la|el|los|las|su|sus) \w+",
    r"el aire (?:estaba|se sent[íi]a) (?:cargado|espeso|denso|pesado)",
    r"(?:sus |los )?ojos se (?:abrieron|agrandaron) como platos",
    r"una oleada de \w+ (?:lo|la|le|los|las)? ?(?:invadi[óo]|recorri[óo]|golpe[óo])",
    r"una punzada de \w+",
    r"(?:su |el )?coraz[óo]n (?:le )?(?:lat[íi]a|golpeaba|martilleaba) (?:con fuerza )?en (?:su|el) pecho",
    r"un escalofr[íi]o (?:le )?recorri[óo] (?:la espalda|la columna|el cuerpo)",
    r"solt[óo] (?:un|el) suspiro que no sab[íi]a que (?:estaba )?(?:conten[íi]a|conteniendo)",
    r"el silencio era (?:ensordecedor|sepulcral|absoluto|opresivo)",
    r"algo (?:antiguo|oscuro|primitivo|innombrable) se (?:agit[óo]|remov[íi]ó|despert[óo])",
    r"(?:cabello|pelo|melena) .{0,20}(?:ca[íi]a en cascada|cascada)",
    r"ojos (?:penetrantes|de un (?:azul|verde|gris) intenso)",
    r"una sonrisa (?:c[óo]mplice|de complicidad|enigm[áa]tica|ladeada)",
    r"un nudo en la garganta",
    r"se le hel[óo] la sangre",
    r"el tiempo pareci[óo] detenerse",
    r"contuvo (?:la|el) (?:respiraci[óo]n|aliento)",
    r"trag[óo] saliva",
    r"asinti[óo] (?:lentamente|despacio)",
    r"(?:sus|las) miradas se (?:encontraron|cruzaron)",
    r"(?:solt[óo]|dej[óo] escapar) un suspiro",
]

# ---------------------------------------------------------------------------
# Tics estructurales
# ---------------------------------------------------------------------------

TICS_ESTRUCTURALES = [
    r"[Nn]o (?:estoy|est[áa]s) diciendo .{3,50}[.,] (?:estoy|digo)",
    r"[Ll]o cual significa (?:que )?o bien .{3,50} o ",
    r"[Hh]ay una diferencia\.",
    r"[Nn]o son lo mismo\.",
    r"[Nn]o (?:por|desde|a causa de) .{3,50}, sino (?:por|desde|a causa de)",
    r"[Ee]so (?:no )?(?:era|es) (?:todo|lo [úu]nico)\. (?:Era|Es) ",
]

# ---------------------------------------------------------------------------
# Contar en vez de mostrar
# ---------------------------------------------------------------------------

_EMOCIONES = (
    "triste|feliz|enojad[oa]|furios[oa]|nervios[oa]|ansios[oa]|asustad[oa]|"
    "aterrad[oa]|culpable|sol[oa]|desesperad[oa]|emocionad[oa]|celos[oa]|"
    "avergonzad[oa]|orgullos[oa]|amarg[oa]|aliviad[oa]|confundid[oa]|"
    "horrorizad[oa]|abatid[oa]|eufóric[oa]|melancólic[oa]|angustiad[oa]"
)

PATRONES_CONTAR = [
    rf"\bse s(?:inti[óo]|entía) (?:muy |bastante |profundamente )?(?:{_EMOCIONES})\b",
    rf"\b(?:estaba|estuvo|parec[íi]a|se ve[íi]a) (?:muy |bastante |realmente )?(?:{_EMOCIONES})\b",
    r"\b(?:nerviosa|triste|alegre|furiosa|desesperada|ansiosa|culpable|"
    r"amarga|melancólica|angustiada|tímida|orgullosa)mente\b",
]

# ---------------------------------------------------------------------------
# Calcos del inglés — la huella más delatora en español
# ---------------------------------------------------------------------------

CALCOS_DEL_INGLES = [
    # sujeto pronominal redundante en oraciones consecutivas
    (r"\b(Él|Ella|Ellos|Ellas)\s+\w+.{0,60}?\.\s+\1\s+\w+",
     "sujeto pronominal redundante"),
    # posesivo calcado con partes del cuerpo
    (r"\b(?:levant[óo]|baj[óo]|movi[óo]|extendi[óo]|cerr[óo]|abri[óo]) su[s]? "
     r"(?:mano|manos|brazo|brazos|cabeza|ojos|pierna|piernas|hombros)\b",
     "posesivo calcado en parte del cuerpo"),
    (r"\bmeti[óo] sus manos en sus bolsillos\b", "posesivo calcado"),
    # pasiva perifrástica con agente
    (r"\bfue \w+ad[oa]s? por (?:el|la|los|las|un|una)\b", "pasiva calcada"),
    (r"\bfue \w+id[oa]s? por (?:el|la|los|las|un|una)\b", "pasiva calcada"),
    # continuo calcado
    (r"\bestaba siendo\b", "«estar siendo» (calco del continuo)"),
    (r"\best[áa] siendo\b", "«estar siendo» (calco del continuo)"),
    # dequeísmo / queísmo
    (r"\b(?:pienso|creo|opino|considero|dijo|dice) de que\b", "dequeísmo"),
    (r"\bme di cuenta que\b", "queísmo"),
    (r"\bdarse cuenta que\b", "queísmo"),
]


# ---------------------------------------------------------------------------
# Tolerancia a saltos de línea
# ---------------------------------------------------------------------------
#
# La prosa llega con las líneas cortadas a 72-80 columnas, así que un patrón
# con espacios literales falla cuando la frase cruza un salto de línea. Se
# convierte cada espacio del patrón en \s+ al cargar el módulo.

def _flexibilizar(patrones):
    return [re.sub(r"(?<!\\)\s+", r"\\s+", p) for p in patrones]


NIVEL1_LOCUCIONES = _flexibilizar(NIVEL1_LOCUCIONES)
NIVEL3_MULETILLAS = _flexibilizar(NIVEL3_MULETILLAS)
CLICHES_FICCION = _flexibilizar(CLICHES_FICCION)
TICS_ESTRUCTURALES = _flexibilizar(TICS_ESTRUCTURALES)
PATRONES_CONTAR = _flexibilizar(PATRONES_CONTAR)
CALCOS_DEL_INGLES = [(_flexibilizar([p])[0], d) for p, d in CALCOS_DEL_INGLES]


# ---------------------------------------------------------------------------
# Raya: diálogo frente a inciso parentético
# ---------------------------------------------------------------------------

def densidad_raya_parentetica(texto: str) -> float:
    """
    Rayas parentéticas por cada mil palabras.

    En español la raya abre el diálogo y encierra los incisos del narrador
    dentro del diálogo. Ese uso es correcto y no se penaliza. Solo se cuenta
    la raya usada como paréntesis dentro de prosa narrativa, que sí es tic
    de IA (calco del em dash inglés).

    Heurística: si una línea empieza con raya, es diálogo y todas sus rayas
    quedan exentas. Las rayas en líneas narrativas se cuentan.
    """
    total_palabras = len(texto.split()) or 1
    parenteticas = 0

    for linea in texto.splitlines():
        limpia = linea.strip()
        if not limpia:
            continue
        if limpia.startswith("—") or limpia.startswith("–"):
            continue  # línea de diálogo: exenta
        parenteticas += limpia.count("—") + limpia.count("–")

    return (parenteticas / total_palabras) * 1000


UMBRAL_RAYA_PARENTETICA = 6.0  # por mil palabras; más bajo que el inglés


# ---------------------------------------------------------------------------
# Segmentación de oraciones en español
# ---------------------------------------------------------------------------

_ABREVIATURAS = {
    "sr", "sra", "srta", "dr", "dra", "lic", "ing", "etc", "p.ej",
    "ee", "uu", "núm", "pág", "vol", "cap",
}


def dividir_oraciones(texto: str) -> list[str]:
    """
    Divide en oraciones respetando la puntuación española.

    Mejoras sobre el re.split(r'[.!?]+') original:
      - ignora los signos de apertura ¿ ¡
      - no corta en abreviaturas frecuentes
      - trata los puntos suspensivos como un solo corte
      - excluye las rayas de diálogo del recuento
    """
    texto = re.sub(r"\.{3,}", "…", texto)
    piezas = re.split(r"(?<=[.!?…])\s+", texto)

    oraciones = []
    buffer = ""
    for pieza in piezas:
        candidata = (buffer + " " + pieza).strip() if buffer else pieza.strip()
        ultima = candidata.rstrip(".").split()[-1].lower() if candidata.split() else ""
        if ultima in _ABREVIATURAS:
            buffer = candidata
            continue
        buffer = ""
        limpia = candidata.lstrip("—–¿¡ ").strip()
        if len(limpia.split()) > 2:
            oraciones.append(limpia)
    if buffer:
        oraciones.append(buffer)
    return oraciones


def cv_longitud_oracion(texto: str) -> float:
    """Coeficiente de variación de la longitud de oración. Más alto = más humano."""
    oraciones = dividir_oraciones(texto)
    if len(oraciones) < 3:
        return 0.5
    largos = [len(o.split()) for o in oraciones]
    media = statistics.mean(largos)
    if media == 0:
        return 0.5
    return statistics.pstdev(largos) / media


# El español corre entre 15% y 20% más largo que el inglés para el mismo
# contenido. Los umbrales del repositorio original se recalibran así:
CALIBRACION = {
    "palabras_objetivo_capitulo": 3800,      # era 3200
    "umbral_cv_oracion": 0.32,               # era 0.30
    "umbral_raya_parentetica": 6.0,          # era 15 (contando todas las rayas)
    "umbral_aceptacion_capitulo": 6.0,       # sin cambio
    "umbral_fundacion": 7.5,                 # sin cambio
    "palabras_objetivo_novela": 92000,
}


def calcos_detectados(texto: str) -> list[tuple[str, int]]:
    """Devuelve [(descripción, ocurrencias)] de calcos del inglés."""
    hallazgos = []
    for patron, descripcion in CALCOS_DEL_INGLES:
        n = len(re.findall(patron, texto))
        if n:
            hallazgos.append((descripcion, n))
    return hallazgos


if __name__ == "__main__":
    muestra = """—No vino nadie —dijo ella.
—¿Estás segura? —Rut cerró la carpeta—. Revisé dos veces.

Las luces estaban todas encendidas. Rut las contó desde la ventana, y no
faltaba ninguna. Ella levantó su mano. Ella miró el registro. Un escalofrío
le recorrió la espalda y no pudo evitar sentir el peso de la ausencia.
"""
    print("raya parentética por mil:", round(densidad_raya_parentetica(muestra), 2))
    print("cv longitud oración:", round(cv_longitud_oracion(muestra), 3))
    print("calcos:", calcos_detectados(muestra))
    print("clichés:", [p[:30] for p in CLICHES_FICCION
                       if re.search(p, muestra, re.IGNORECASE)])
