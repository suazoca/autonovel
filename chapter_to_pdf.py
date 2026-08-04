#!/usr/bin/env python3
"""Genera un PDF de lectura rápida para un capítulo ya aceptado.

No es el export final del libro (eso es typeset/build_tex.py + novel.tex,
con Garamond, drop caps y el formato de tapa/tapa dura). Este es el
formato liviano que se usa para leer un capítulo fuera del entorno
apenas se acepta: LaTeX clásico (Latin/Computer Modern), párrafo con
sangría, sin espacio entre párrafos, quiebre de escena (línea "---" en
el .md) como asterisco centrado.

Uso:
    uv run python chapter_to_pdf.py 9 "Maître Ansermet"

Escribe chapters/pdf/ch_09.pdf (crea el directorio si no existe) y
limpia los archivos auxiliares de xelatex. Requiere xelatex + polyglossia
instalados en el sistema (no es parte de las dependencias de uv).
"""
import re
import subprocess
import sys
from pathlib import Path

LATEX_SPECIAL = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def escape(text: str) -> str:
    return "".join(LATEX_SPECIAL.get(ch, ch) for ch in text)


def convert_inline(text: str) -> str:
    text = escape(text)
    text = re.sub(r"\*(.+?)\*", r"\\textit{\1}", text)  # cursiva: *texto*
    return text


def build_body(md_text: str) -> str:
    paragraphs = [p.strip() for p in md_text.strip().split("\n\n") if p.strip()]
    body = []
    for p in paragraphs:
        if p == "---":
            body.append(r"\begin{center}*\end{center}")
        else:
            body.append(convert_inline(p))
    return "\n\n".join(body)


def build_tex(md_text: str, titulo: str) -> str:
    body = build_body(md_text)
    titulo_tex = convert_inline(titulo)
    return r"""\documentclass[12pt]{article}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{spanish}
\usepackage[margin=1in]{geometry}
\usepackage{setspace}
\setstretch{1.35}
\raggedbottom
\begin{document}
\vspace*{34.0bp}
\begin{center}
{\Large %s}
\end{center}
\vspace{87.4bp}

%s

\end{document}
""" % (titulo_tex, body)


def main():
    if len(sys.argv) < 3:
        print('uso: chapter_to_pdf.py <numero> "<Título del capítulo>"', file=sys.stderr)
        sys.exit(1)

    num = int(sys.argv[1])
    titulo = sys.argv[2]
    root = Path(__file__).parent
    src = root / "chapters" / f"ch_{num:02d}.md"
    if not src.exists():
        print(f"No existe {src}", file=sys.stderr)
        sys.exit(1)

    out_dir = root / "chapters" / "pdf"
    out_dir.mkdir(exist_ok=True)
    stem = f"ch_{num:02d}"

    md_text = src.read_text(encoding="utf-8")
    tex = build_tex(md_text, f"Capítulo {num} — {titulo}")
    tex_path = out_dir / f"{stem}.tex"
    tex_path.write_text(tex, encoding="utf-8")

    subprocess.run(
        ["xelatex", "-interaction=nonstopmode", f"{stem}.tex"],
        cwd=out_dir,
        check=True,
        stdout=subprocess.DEVNULL,
    )

    for ext in ("aux", "log", "tex"):
        (out_dir / f"{stem}.{ext}").unlink(missing_ok=True)

    print(out_dir / f"{stem}.pdf")


if __name__ == "__main__":
    main()
