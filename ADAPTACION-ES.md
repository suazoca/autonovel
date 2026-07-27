# ADAPTACIÓN DE AUTONOVEL AL ESPAÑOL — Guía de instalación

Este paquete adapta [suazoca/autonovel] para escribir novelas en español.
Contiene archivos nuevos y archivos parchados que reemplazan a los del repo.

## Contenido del paquete

| Archivo | Tipo | Qué hace |
|---|---|---|
| `lang_es.py` | NUEVO | Todas las listas de detección de slop en español (Nivel 1/2/3, clichés de ficción, telling, tics estructurales, calcos del inglés, umbrales de -mente y gerundio, nota de idioma para los jueces LLM). |
| `evaluate.py` | REEMPLAZO | Importa las listas de `lang_es.py`. Corrige el conteo de rayas para NO penalizar el diálogo español. Añade 3 métricas nuevas: calcos del inglés, densidad de -mente, densidad de gerundios. Antepone la instrucción de idioma a todos los prompts de los jueces. Soporta frases prohibidas multipalabra. |
| `draft_chapter.py` | REEMPLAZO | System prompt y las 28 instrucciones de escritura en español, con reglas de raya, gerundio, -mente y calcos. Genérico (sin referencias a la novela "Bells"). |
| `gen_audiobook_script.py` | REEMPLAZO | Reglas de parseo para diálogo con raya e incisos del narrador. Diccionario de personajes con plantilla para tu novela. |
| `typeset/novel.tex` | REEMPLAZO | Añade polyglossia + spanish (partición silábica y tipografía españolas). |
| `typeset/epub_metadata.yaml` | REEMPLAZO | `lang: es`. |
| `ANTI-SLOP-ES.md` | NUEVO | Reemplaza a ANTI-SLOP.md como referencia de campo. |
| `voice_es.md` | NUEVO | Renombrar a `voice.md`: Parte 1 (barandillas) en español; Parte 2 con la decisión de variedad dialectal ya anotada. |

## Instalación

```bash
git clone https://github.com/suazoca/autonovel.git && cd autonovel
git checkout -b novela-es

# Copiar los archivos del paquete sobre el repo:
cp /ruta/al/paquete/lang_es.py .
cp /ruta/al/paquete/evaluate.py .
cp /ruta/al/paquete/draft_chapter.py .
cp /ruta/al/paquete/gen_audiobook_script.py .
cp /ruta/al/paquete/ANTI-SLOP-ES.md .
cp /ruta/al/paquete/voice_es.md voice.md
cp /ruta/al/paquete/typeset/novel.tex typeset/
cp /ruta/al/paquete/typeset/epub_metadata.yaml typeset/

cp .env.example .env   # y añade tu ANTHROPIC_API_KEY
uv sync
```

## Verificación rápida

```bash
python3 -c "
from evaluate import slop_score
r = slop_score('Cabe destacar que no pudo evitar sentir una ola de pánico que lo invadió. Eventualmente cerró sus ojos.')
print('penalización:', r['slop_penalty'], '(debe ser > 2)')
r2 = slop_score('—¿Adónde vas? —preguntó ella—. Es tarde.')
print('diálogo limpio:', r2['slop_penalty'], '(debe ser 0)')
"
```

## Cambios pendientes que haremos en el Paso 2 (fundación)

Estos archivos generan CONTENIDO y sus prompts conviene ajustarlos junto
con la fundación de tu novela, porque llevan contexto específico:

1. **`gen_world.py`, `gen_characters.py`, `gen_outline.py`, `gen_canon.py`,
   `seed.py`** — añadir a cada prompt este bloque (o pásalo como parte
   del seed):

   > "Escribe TODO el contenido en español. La novela es en español
   > neutro latinoamericano; los diálogos de ejemplo usan raya (—) y
   > respetan la variedad dialectal de cada personaje."

2. **`review.py`, `reader_panel.py`, `adversarial_edit.py`, `gen_brief.py`**
   — mismos jueces, pero como `evaluate.py` ya antepone `ES_JUDGE_NOTE`
   solo en sus propios prompts, hay que añadir la misma constante
   (importada de `lang_es`) al inicio de los prompts de estos cuatro
   scripts. Es un cambio de una línea por archivo:
   `prompt = ES_JUDGE_NOTE + prompt`.

3. **`run_pipeline.py`** — revisa los prompts embebidos del orquestador
   y aplica el mismo bloque de idioma.

4. **`audiobook_voices.json` + `gen_audiobook.py`** — al llegar a la fase
   de audio: usar el modelo `eleven_multilingual_v2` de ElevenLabs y
   elegir voces con buen español (puedes asignar acentos por personaje:
   hondureño, peninsular, acento eslavo, etc.).

5. **Calibración tras los primeros 3 capítulos** — revisa `eval_logs/`:
   si la densidad de -mente o gerundios penaliza prosa legítima, ajusta
   `UMBRAL_MENTE_X1000` / `UMBRAL_GERUNDIO_X1000` en `lang_es.py`.
   Los umbrales (4 y 12 por mil palabras) son conservadores.

## Decisiones editoriales ya tomadas (cámbialas si no estás de acuerdo)

- **Variedad:** narración en español neutro latinoamericano; dialectos
  solo en diálogo (voseo hondureño, castellano peninsular, español con
  interferencias para personajes no hispanohablantes).
- **Diálogo:** raya (—), convención literaria estándar del español.
- **Citas** (versículos como Miqueas 7:7, letreros): comillas angulares « ».
- **Meta por capítulo:** ~3,200 palabras se mantiene (el español rinde
  ~10% más palabras; 19-24 capítulos ≈ 80.000-95.000 palabras, ideal
  para thriller apocalíptico).
