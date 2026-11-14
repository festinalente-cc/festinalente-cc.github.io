#!/usr/bin/env python3
"""Regenera documentos/Fichas_evidencia_EOT.pdf desde las páginas del micrositio del panel EOT.

Toma la presentación y la tabla de cobertura de _fuentes/fichas.md, las páginas P01–P19 ya
generadas por eot_paginas.py y la página de referencias, y las imprime a PDF con Chromium.
Así el PDF y el sitio tienen siempre el mismo contenido.

Requiere: pip install markdown playwright  y  python -m playwright install chromium
Uso:      python scripts/eot_pdf_fichas.py eot-estandares-4h7p "1.2" "14 de noviembre de 2026" "nota de cambios"
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
slug = sys.argv[1] if len(sys.argv) > 1 else "eot-estandares-4h7p"
version = sys.argv[2] if len(sys.argv) > 2 else "1.1"
fecha = sys.argv[3] if len(sys.argv) > 3 else ""
cambios = sys.argv[4] if len(sys.argv) > 4 else ""
P = RAIZ / "proyectos" / slug

src = (P / "_fuentes/fichas.md").read_text(encoding="utf-8")
head = re.split(r"^## P01 ", src, flags=re.M)[0]
head = head.replace("Ningún dato fue verificado por una persona; ante una cifra que vaya a sustentar una afirmación, "
                    "consultar la cita en el anexo técnico.",
                    "Ante una cifra que vaya a sustentar una afirmación, consultar la cita en el anexo técnico.")
head = re.sub(r"^# .*\n", "", head, count=1)
head = re.sub(r"^Nov \d+, 2026.*\n", "", head, flags=re.M)
linea_version = f"*Versión {version}" + (f" · {fecha}" if fecha else "") + ". " + (cambios + " " if cambios else "") + \
    "El contenido es el mismo que el de las páginas del micrositio del panel.*"
head = head.replace("## Presentación", "## Presentación\n\n" + linea_version, 1)

cuerpo = []
for f in sorted(P.glob("paginas/[0-9][0-9]-p[0-9][0-9].md")):
    _, meta, txt = f.read_text(encoding="utf-8").split("---", 2)
    titulo = re.search(r'titulo: "(.+)"', meta).group(1)
    txt = re.sub(r"\A\s*> ", "", txt)
    txt = re.sub(r"^## ", "### ", txt, flags=re.M)
    cuerpo.append(f"## {titulo}\n\n{txt.strip()}\n")
refs = (P / "paginas/21-referencias.md").read_text(encoding="utf-8").split("---", 2)[2]
refs = re.sub(r"^## ", "### ", refs, flags=re.M)

md_all = ("# Fichas de evidencia para el panel — EOT en adultos, Colombia\n\n" + head.strip() + "\n\n"
          + "\n".join(cuerpo) + "\n## Referencias citadas\n" + refs)
html = markdown.markdown(md_all, extensions=["extra", "sane_lists", "smarty"])
html = html.replace("<h2>Presentación</h2>", "<h2 class='first'>Presentación</h2>", 1)

CSS = """
body { font-family: "Inter", "Helvetica Neue", Arial, sans-serif; font-size: 10.2pt; line-height: 1.45; color: #2b2d30; }
h1 { font-weight: 300; font-size: 24pt; letter-spacing: -0.02em; margin: 0 0 18pt; color: #141416; }
h2 { font-weight: 300; font-size: 19pt; letter-spacing: -0.02em; color: #141416; margin: 0 0 12pt;
     page-break-before: always; border-bottom: 1px solid #141416; padding-bottom: 6pt; }
h2.first { page-break-before: avoid; }
h3 { font-size: 11.5pt; font-weight: 600; margin: 16pt 0 6pt; color: #141416; }
p { margin: 0 0 8pt; } li { margin-bottom: 4pt; }
table { border-collapse: collapse; width: 100%; font-size: 8.8pt; margin: 6pt 0 12pt; }
th, td { border-bottom: 1px solid #d9d9d6; padding: 4pt 6pt; text-align: left; vertical-align: top; }
th { border-bottom: 1px solid #141416; font-weight: 600; }
tr { page-break-inside: avoid; }
em { color: #555; }
"""
pie = ("<div style='font-size:7.5pt;color:#777;width:100%;padding:0 18mm;font-family:Arial;display:flex;"
       "justify-content:space-between'><span>Festina Lente · uso exclusivo del panel</span>"
       "<span>Página <span class='pageNumber'></span> de <span class='totalPages'></span></span></div>")
cabecera = ("<div style='font-size:7.5pt;color:#777;width:100%;padding:0 18mm;font-family:Arial'>"
            f"Fichas de evidencia para el panel — EOT en adultos, Colombia · Versión {version}</div>")

with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
    tmp.write(f"<!doctype html><html lang='es'><head><meta charset='utf-8'><style>{CSS}</style></head>"
              f"<body>{html}</body></html>")
salida = P / "documentos/Fichas_evidencia_EOT.pdf"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.goto(Path(tmp.name).as_uri())
    pg.wait_for_timeout(500)
    pg.pdf(path=str(salida), format="A4", print_background=True, display_header_footer=True,
           margin={"top": "22mm", "bottom": "20mm", "left": "18mm", "right": "18mm"},
           header_template=cabecera, footer_template=pie)
    b.close()
print(f"PDF versión {version} escrito en {salida.relative_to(RAIZ)}")
