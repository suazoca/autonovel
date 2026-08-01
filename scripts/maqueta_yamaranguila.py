#!/usr/bin/env python3
"""Genera la maqueta PDF de Yamaranguila (texto + art/pages)."""
from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1] / "libros" / "01-piloto"
ART = ROOT / "art" / "pages"
OUT = ROOT / "maqueta" / "Yamaranguila-maqueta.pdf"


def parse_texts() -> dict[int, str]:
    md = (ROOT / "paginas.md").read_text(encoding="utf-8")
    body = md.split("# Texto corrido")[0]
    blocks = re.split(r"### Pág\. (\d+)\n", body)
    pages: dict[int, str] = {}
    for i in range(1, len(blocks), 2):
        num = int(blocks[i])
        m = re.search(
            r"\*\*texto:\*\*\s*(.*?)(?=\n- \*\*brief:)", blocks[i + 1], re.S
        )
        if m:
            lines = [ln.strip() for ln in m.group(1).strip().splitlines() if ln.strip()]
            pages[num] = "\n".join(lines)
    return pages


def art_map() -> dict[int, Path]:
    out: dict[int, Path] = {}
    for p in ART.glob("p*.jpg"):
        m = re.match(r"p(\d+)-", p.name)
        if m:
            out[int(m.group(1))] = p
    return out


def wrap_text(c, text, x, y, max_width, font="Helvetica", size=12, leading=16):
    c.setFont(font, size)
    c.setFillColorRGB(0.12, 0.12, 0.12)
    for para in text.split("\n"):
        if not para.strip():
            y -= leading * 0.5
            continue
        words = para.split()
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if c.stringWidth(test, font, size) <= max_width:
                line = test
            else:
                c.drawString(x, y, line)
                y -= leading
                line = w
        if line:
            c.drawString(x, y, line)
            y -= leading
        y -= leading * 0.15
    return y


def main() -> None:
    pages = parse_texts()
    arts = art_map()
    if len(pages) != 48 or len(arts) != 48:
        raise SystemExit(f"Need 48 texts and 48 arts; got {len(pages)} / {len(arts)}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    page_w, page_h = landscape(letter)
    margin = 0.45 * inch
    c = canvas.Canvas(str(OUT), pagesize=(page_w, page_h))
    c.setTitle("Yamaranguila — maqueta álbum medio")
    c.setAuthor("Chris Suazo")
    c.setSubject(
        "Maqueta de trabajo — texto v2.1 + arte Imagine — "
        "ebook + KDP Print 11x8.5 in landscape"
    )

    # cover
    c.setFillColorRGB(0.96, 0.94, 0.88)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    c.setFillColorRGB(0.15, 0.35, 0.28)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(page_w / 2, page_h / 2 + 40, "Yamaranguila")
    c.setFont("Helvetica-Oblique", 18)
    c.setFillColorRGB(0.3, 0.4, 0.35)
    c.drawCentredString(page_w / 2, page_h / 2 + 8, "El agua de la pirámide")
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.drawCentredString(
        page_w / 2, page_h / 2 - 40, "Maqueta de trabajo · álbum medio · ~48 páginas"
    )
    c.drawCentredString(
        page_w / 2,
        page_h / 2 - 58,
        "Chris Suazo · Serie Ciudades de Honduras · Noha, Ivana y el abuelo Dale",
    )
    c.setFont("Helvetica", 10)
    c.drawCentredString(
        page_w / 2,
        page_h / 2 - 78,
        "Ebook + Amazon KDP · trim 11\" × 8.5\" horizontal",
    )
    c.setFont("Helvetica", 9)
    c.drawCentredString(
        page_w / 2,
        0.55 * inch,
        "Texto v2.1 · Ilustraciones Imagine (borrador) · No es edición final de imprenta",
    )
    c.showPage()

    for n in range(1, 49):
        c.setFillColorRGB(0.99, 0.98, 0.96)
        c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
        c.setFillColorRGB(0.15, 0.35, 0.28)
        c.rect(0, page_h - 0.38 * inch, page_w, 0.38 * inch, fill=1, stroke=0)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, page_h - 0.26 * inch, "Yamaranguila")
        c.setFont("Helvetica", 10)
        c.drawRightString(page_w - margin, page_h - 0.26 * inch, f"Pág. {n} / 48")

        img_path = arts[n]
        img = ImageReader(str(img_path))
        iw, ih = img.getSize()
        max_w = page_w - 2 * margin
        max_h = page_h - 2.35 * inch
        scale = min(max_w / iw, max_h / ih)
        dw, dh = iw * scale, ih * scale
        ix = (page_w - dw) / 2
        iy = page_h - 0.5 * inch - dh
        c.drawImage(img, ix, iy, width=dw, height=dh, preserveAspectRatio=True, mask="auto")
        c.setStrokeColorRGB(0.75, 0.72, 0.65)
        c.setLineWidth(0.6)
        c.rect(ix, iy, dw, dh, fill=0, stroke=1)

        display = pages[n]
        size = 12 if len(display) < 120 else 11
        leading = 16 if len(display) < 120 else 14.5
        wrap_text(
            c,
            display,
            margin,
            iy - 0.22 * inch,
            page_w - 2 * margin,
            size=size,
            leading=leading,
        )
        c.setFont("Helvetica", 7)
        c.setFillColorRGB(0.55, 0.55, 0.55)
        c.drawString(margin, 0.28 * inch, img_path.name)
        c.drawRightString(page_w - margin, 0.28 * inch, "maqueta de trabajo")
        c.showPage()

    # coda
    c.setFillColorRGB(0.96, 0.94, 0.88)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    c.setFillColorRGB(0.15, 0.35, 0.28)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(page_w / 2, page_h / 2 + 50, "Nota para adultos")
    c.setFont("Helvetica", 11)
    c.setFillColorRGB(0.25, 0.25, 0.25)
    note = (
        "Yamaranguila (Intibucá, Honduras). En este cuento decimos que el nombre\n"
        "significa «agua de la pirámide», lectura poética del nombre antiguo\n"
        "Zabalanquíra / Zabalanquira. Hay otras teorías; esta es la de esta historia.\n\n"
        "Serie: Noha, Ivana y el abuelo Dale. Objetos: jarrito; mapa de Emilia.\n"
        "Formato: álbum medio (~48 páginas). Ilustraciones de borrador (IA)."
    )
    y = page_h / 2 + 20
    for line in note.split("\n"):
        c.drawCentredString(page_w / 2, y, line)
        y -= 16
    c.showPage()
    c.save()
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
