#!/usr/bin/env python3
"""
One-shot voice.md/voz.md Parte 2 generator for foundation phase.

Solo depende de la semilla y de CRAFT.md -- nunca de mundo.md ni de
personajes.md. Si dependiera de esos dos, habría una dependencia circular
con gen_world.py/gen_characters.py, que a su vez leen la voz como insumo
(ver docs/HALLAZGOS.md, "restricción de orden"). Por eso corre PRIMERO en
el loop de fundación, antes que gen_world.py.

La voz se genera UNA SOLA VEZ: si la Parte 2 ya tiene contenido real (no
la plantilla vacía), este script no llama a la API -- informa que ya
existe y sale. La semilla no cambia entre iteraciones de fundación, así
que regenerar la voz en cada vuelta sería ruido, no exploración. Es
coherente con la regla de la Clase B para series: la voz no se
redescubre entre libros, se congela y se copia idéntica.
"""
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv

from fundacion_comun import (
    ruta_bilingue, load_file, load_file_bilingue, extraer_voz_parte2,
    voz_parte2_tiene_contenido, exigir_semilla,
)

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

WRITER_MODEL = os.environ.get("AUTONOVEL_WRITER_MODEL", "claude-sonnet-4-6")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_BASE = os.environ.get("AUTONOVEL_API_BASE_URL", "https://api.anthropic.com")

def call_writer(prompt, max_tokens=8000):
    import httpx
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": WRITER_MODEL,
        "max_tokens": max_tokens,
        "system": (
            "Sos un descubridor de voz narrativa. A partir de una semilla de "
            "novela, proponés una identidad de voz específica -- tono, ritmo, "
            "registro léxico, punto de vista -- y escribís pasajes de ejemplo "
            "que SON esa voz, no que la describen. Nunca usás relleno de IA. "
            "Escribís en español. No inventás nombres, lugares ni personajes "
            "de ninguna novela existente -- lo que necesites para los pasajes "
            "de ejemplo, lo derivás de la semilla o lo inventás de cero."
        ),
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = httpx.post(f"{API_BASE}/v1/messages", headers=headers, json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


# ---------------------------------------------------------------------------
# Las 7 secciones que este script llena. "Reglas específicas de capítulo"
# (Chapter-Specific Rules) queda afuera a propósito: es opcional, la
# plantilla dice explícitamente que puede quedar vacía, y no es parte del
# descubrimiento de voz -- son reglas por capítulo que se agregan más
# tarde, si hacen falta.
# ---------------------------------------------------------------------------

SECCIONES = [
    # (marcador interno, patrón bilingüe del encabezado real en el archivo)
    ("TONO", r"Tone|Tono"),
    ("RITMO", r"Sentence Rhythm|Ritmo de oraci[oó]n"),
    ("VOCABULARIO", r"Vocabulary Register|Registro l[ée]xico"),
    ("POV_TIEMPO", r"POV and Tense|POV y [Tt]iempo(?: verbal)?"),
    ("DIALOGO", r"Dialogue Conventions|Convenciones de di[aá]logo"),
    ("EJEMPLARES", r"Exemplar Passages|Pasajes ejemplares"),
    ("ANTIEJEMPLARES", r"Anti-Exemplars|Anti-ejemplares"),
]


def build_prompt(seed, craft):
    marcadores = "\n".join(f"###{marcador}###" for marcador, _ in SECCIONES)
    return f"""Descubrí la identidad de voz para esta novela. No estás describiendo
una voz en abstracto -- estás decidiendo cómo suena ESTA historia y
demostrándolo con prosa real.

CONCEPTO SEMILLA:
{seed}

REFERENCIA DE OFICIO (de CRAFT.md):
{craft}

Pensá varias direcciones posibles de tono y registro antes de decidirte
-- pero tu respuesta final debe ser UNA sola voz, coherente, no un menú
de opciones. Una vez que decidas, todo lo que sigue debe sonar a la
misma persona escribiendo.

No inventes nombres, lugares ni personajes de ninguna otra novela. Para
los pasajes de ejemplo, usá lo que la semilla ya sugiere, o inventá algo
mínimo y genérico si la semilla no alcanza -- lo importante es CÓMO está
escrito, no la trama.

Respondé con exactamente estas 7 secciones, en este orden, cada una
empezando con su marcador en una línea propia (tal cual, con los símbolos
### de cada lado), seguido del contenido:

{marcadores}

Contenido esperado de cada sección:

###TONO###
Una o dos oraciones. Ejemplos de la forma esperada (no copiar, inventar
la propia): "Mítico y pesado, como tablillas de piedra leídas en voz
alta." "Cálido, casi sin aliento, como alguien contando historias junto
al fuego." "Seco y frío. Oraciones como cortes de cuchillo."

###RITMO###
Tendencias, no reglas. Ej.: "Oraciones largas para la ambientación,
cortas para la violencia." "El diálogo es cortante. La narración fluye."

###VOCABULARIO###
El pozo léxico de este mundo. ¿A qué suena? ¿Vocabulario concreto y
anglosajón? ¿Latinizado y barroco? ¿Coloquial moderno? ¿Una mezcla?

###POV_TIEMPO###
¿Tercera persona limitada? ¿Primera? ¿Rotativo? ¿Pretérito? ¿Presente?
¿Cambia por efecto?

###DIALOGO###
¿Acotaciones solo con "dijo"? ¿Con acción? ¿Sin acotaciones? ¿Cómo suena
distinto cada personaje? ¿Dicen lo que piensan o hay subtexto?

###EJEMPLARES###
3-5 párrafos que SEAN la voz, no que la describan. Esto es el diapasón
contra el que se va a calibrar cada capítulo.

###ANTIEJEMPLARES###
3-5 párrafos mostrando qué NO es esta voz. No la lista genérica de
anti-slop (esa ya está en la Parte 1) -- específico a esta novela.
Ej.: "Esto es demasiado florido para nuestro tono." "Esto es demasiado
moderno."
"""


def parsear_secciones(texto_modelo):
    """Devuelve {{marcador: contenido}} a partir de la respuesta del modelo,
    dividida por los marcadores ###MARCADOR### que pedimos en el prompt."""
    resultado = {}
    patron = r'###(' + '|'.join(m for m, _ in SECCIONES) + r')###'
    partes = re.split(patron, texto_modelo)
    # re.split con grupo de captura devuelve [antes, marcador, cuerpo, marcador, cuerpo, ...]
    for i in range(1, len(partes), 2):
        marcador = partes[i]
        cuerpo = partes[i + 1].strip() if i + 1 < len(partes) else ""
        resultado[marcador] = cuerpo
    return resultado


def _rango_subseccion(texto, patron_nombre):
    """(inicio, fin) del CUERPO de un '### <nombre>' -- desde el final del
    encabezado hasta el próximo '###'/'##'/'#' o fin de archivo. None si
    el encabezado no existe en este archivo."""
    m = re.search(rf'^###\s*(?:{patron_nombre}).*$', texto, re.IGNORECASE | re.MULTILINE)
    if not m:
        return None
    inicio = m.end()
    nxt = re.search(r'^#{1,3}\s', texto[inicio:], re.MULTILINE)
    fin = inicio + nxt.start() if nxt else len(texto)
    return inicio, fin


def llenar_parte2(texto_completo, secciones):
    """Reemplaza el cuerpo de cada subsección vacía de la Parte 2 por el
    contenido generado, sin tocar la Parte 1 ni ninguna subsección que ya
    tenga contenido real. Si una subsección del archivo no coincide con
    ninguna de SECCIONES (p.ej. "Reglas específicas de capítulo"), se deja
    tal cual estaba."""
    resultado = texto_completo
    # de atrás para adelante, para que los índices de las secciones
    # anteriores no se corran al reemplazar
    rangos = []
    for marcador, patron in SECCIONES:
        rango = _rango_subseccion(resultado, patron)
        if rango is None:
            continue
        rangos.append((rango, marcador))
    rangos.sort(key=lambda r: r[0][0], reverse=True)

    for (inicio, fin), marcador in rangos:
        cuerpo_actual = resultado[inicio:fin]
        sin_comentarios = re.sub(r'<!--.*?-->', '', cuerpo_actual, flags=re.DOTALL).strip()
        if sin_comentarios:
            continue  # ya tiene contenido real, no tocar
        nuevo = secciones.get(marcador)
        if not nuevo:
            continue  # el modelo no devolvió esta sección, dejar como estaba
        resultado = resultado[:inicio] + "\n" + nuevo + "\n\n" + resultado[fin:]

    return resultado


def main():
    seed = load_file_bilingue(BASE_DIR, "semilla.txt", "seed.txt")
    exigir_semilla(seed, "descubrir una voz")

    ruta_voz = ruta_bilingue(BASE_DIR, "voz.md", "voice.md")
    voz_actual = load_file(ruta_voz)

    if voz_parte2_tiene_contenido(voz_actual):
        print(f"La Parte 2 de {ruta_voz.name} ya tiene contenido -- no se "
              f"regenera. La voz se decide una sola vez.", file=sys.stderr)
        print(extraer_voz_parte2(voz_actual))
        return

    craft = load_file(BASE_DIR / "CRAFT.md")

    prompt = build_prompt(seed, craft)

    print("Calling writer model...", file=sys.stderr)
    resultado_modelo = call_writer(prompt)
    secciones = parsear_secciones(resultado_modelo)

    texto_final = llenar_parte2(voz_actual, secciones)

    ruta_voz.write_text(texto_final, encoding="utf-8")
    print(f"Saved to {ruta_voz}", file=sys.stderr)
    print(extraer_voz_parte2(texto_final))


if __name__ == "__main__":
    main()
