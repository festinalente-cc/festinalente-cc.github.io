#!/usr/bin/env python3
"""Genera los documentos descargables de la mesa de vitamina D a partir de las páginas ya generadas
(scripts/vitd_paginas.py) y de la extracción (_fuentes/extraccion.json):

  documentos/Fichas_evidencia_vitD.pdf                    todas las páginas en un PDF (A4)
  documentos/Anexo_tecnico_evidencia_por_tema_vitD.xlsx   una hoja por tema, con la cita textual de cada cifra
  documentos/Referencias_incluidas_vitD.xlsx              los 74 estudios

Requiere markdown, openpyxl y playwright (Chromium). Uso: python scripts/vitd_documentos.py vitd-mesa-ace-6q2n
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import markdown
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parent.parent
slug = sys.argv[1] if len(sys.argv) > 1 else "vitd-mesa-ace-6q2n"
PROY = RAIZ / "proyectos" / slug
DOCS = PROY / "documentos"
PAG = PROY / "paginas"

datos = json.loads((PROY / "_fuentes" / "extraccion.json").read_text(encoding="utf-8"))
EST = {e["id"]: e for e in datos["estudios"]}


def leer_pagina(f: Path) -> tuple[dict, str]:
    t = f.read_text(encoding="utf-8")
    _, cab, cuerpo = t.split("---", 2)
    meta = {}
    for linea in cab.strip().splitlines():
        k, v = linea.split(":", 1)
        v = v.strip()
        meta[k] = json.loads(v) if v.startswith('"') else (int(v) if v.isdigit() else v)
    return meta, cuerpo.strip()


paginas = sorted((leer_pagina(f) + (f.stem,) for f in PAG.glob("*.md")), key=lambda x: x[0]["orden"])
temas = [(nombre, meta) for meta, _, nombre in paginas if re.fullmatch(r"t\d+[ab]?", nombre)]
citas_por_tema = {nombre: sorted(set(re.findall(r"\b(VD\d{3})\b", cuerpo.split("## Estudios citados")[0])))
                  for meta, cuerpo, nombre in paginas if re.fullmatch(r"t\d+[ab]?", nombre)}

# ---------------------------------------------------------------- Excel ----------
CAB = Font(bold=True, color="FFFFFF")
FONDO = PatternFill("solid", fgColor="2F3133")
ENVOLVER = Alignment(wrap_text=True, vertical="top")


def hoja(wb: Workbook, nombre: str, columnas: list[str], filas: list[list], anchos: list[int]) -> None:
    ws = wb.create_sheet(nombre[:31])
    ws.append(columnas)
    for c in ws[1]:
        c.font, c.fill, c.alignment = CAB, FONDO, Alignment(wrap_text=True, vertical="center")
    for f in filas:
        ws.append(f)
    for i, a in enumerate(anchos, 1):
        ws.column_dimensions[get_column_letter(i)].width = a
    for fila in ws.iter_rows(min_row=2):
        for c in fila:
            c.alignment = ENVOLVER
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions


def calidad(e: dict) -> str:
    return f"{e['calidad']['herramienta']}: {e['calidad']['juicio_global']}"


def ic(o: dict) -> str:
    if o.get("ic_inf") is None:
        return ""
    return f"{o['ic_inf']} a {o['ic_sup']}"


wb = Workbook()
wb.remove(wb.active)
ws = wb.create_sheet("Léeme")
for linea, negrita in [
    ("Anexo técnico – Mesa de expertos sobre la formulación de vitamina D (ACE 2026)", True),
    ("Una hoja por tema (T1 a T12) con los estudios citados en su ficha. Cada fila es un resultado del estudio, "
     "o una recomendación cuando se trata de una guía o un consenso.", False),
    ("La columna «Cita textual» reproduce el fragmento del artículo de donde sale la cifra; se verificó de forma "
     "automática contra el PDF.", False),
    ("Calidad: AMSTAR 2 (revisiones sistemáticas), RoB 2 (ensayos clínicos), AGREE II (guías) y lista JBI de texto y "
     "opinión (consensos y revisiones críticas). Un segundo revisor confirmó la evaluación.", False),
    ("Hoja «Calidad»: dominios o ítems de cada herramienta y justificación del juicio, para los 74 estudios.", False),
]:
    ws.append([linea])
    ws.cell(ws.max_row, 1).font = Font(bold=negrita, size=13 if negrita else 11)
    ws.cell(ws.max_row, 1).alignment = Alignment(wrap_text=True)
ws.column_dimensions["A"].width = 130

for nombre, meta in temas:
    filas = []
    for c in citas_por_tema[nombre]:
        e = EST[c]
        base = [c, e["cita_corta"], e["tipo_publicacion"], calidad(e)]
        for o in e.get("desenlaces", []):
            filas.append(base + [o["nombre"], o["rol"], o["medida"], o.get("estimado"), ic(o), o.get("p", ""),
                                 o.get("k_estudios"), o.get("n"), o.get("i2_pct"), o.get("certeza_grade", ""),
                                 o.get("subgrupo", ""), o["cita"] + (" … " + o["cita_2"] if o.get("cita_2") else "")])
        for o in e.get("hallazgos_modificadores", []):
            filas.append(base + [o["modificador"], "modificador", "", None, "", "", None, None, None, "",
                                 o["hallazgo"], o.get("cita", "")])
        for r in e.get("recomendaciones", []):
            filas.append(base + [r["texto"], "recomendación", "", None, "", "", None, None, None,
                                 r.get("certeza", ""), r.get("fuerza", ""), ""])
    hoja(wb, meta["titulo"].split(".")[0], ["Código", "Estudio", "Tipo", "Calidad", "Resultado o recomendación", "Rol",
                                           "Medida", "Estimado", "IC 95 %", "p", "k", "n", "I² %", "GRADE",
                                           "Subgrupo, unidad o fuerza", "Cita textual"],
         filas, [8, 24, 16, 24, 40, 12, 9, 9, 14, 9, 5, 8, 6, 9, 28, 60])

hoja(wb, "Calidad", ["Código", "Estudio", "Herramienta", "Juicio global", "Dominios o ítems", "Justificación"],
     [[e["id"], e["cita_corta"], e["calidad"]["herramienta"], e["calidad"]["juicio_global"],
       "; ".join(f"{k}: {v}" for k, v in e["calidad"]["dominios"].items()), e["calidad"]["justificacion"]]
      for e in datos["estudios"]], [8, 26, 16, 22, 60, 70])
wb.save(DOCS / "Anexo_tecnico_evidencia_por_tema_vitD.xlsx")

temas_de = {}
for t, cods in citas_por_tema.items():
    for c in cods:
        temas_de.setdefault(c, []).append(t.upper())
wb = Workbook()
wb.remove(wb.active)
hoja(wb, "Referencias", ["Código", "Primer autor y revista", "Título", "PMID", "DOI", "Tipo", "Calidad", "Fichas"],
     [[e["id"], e["cita_corta"], e["titulo"], e["pmid"], f"https://doi.org/{e['doi']}", e["tipo_publicacion"],
       calidad(e), ", ".join(temas_de.get(e["id"], []))] for e in datos["estudios"]],
     [8, 30, 70, 11, 36, 18, 26, 14])
wb.save(DOCS / "Referencias_incluidas_vitD.xlsx")

# ---------------------------------------------------------------- PDF ------------
md = markdown.Markdown(extensions=["extra", "sane_lists", "smarty"])


def a_html(cuerpo: str) -> str:
    cuerpo = re.sub(r"\]\(\.\./referencias/#(vd\d{3})\)", r"](#\1)", cuerpo)
    cuerpo = re.sub(r"\]\(\.\./(t\d+[ab]?|panel|resumen|preguntas|referencias)/\)", r"](#\1)", cuerpo)
    cuerpo = cuerpo.replace("](preguntas/)", "](#preguntas)")
    cuerpo = cuerpo.replace("../documentos/figuras/", (DOCS / "figuras").as_uri() + "/")
    md.reset()
    return md.convert(cuerpo)


partes = []
for meta, cuerpo, nombre in paginas:
    grupo = f'<p class="grupo">{meta.get("grupo", "")}</p>' if meta.get("grupo") else ""
    resumen = f'<p class="pregunta">{meta["resumen"]}</p>' if meta.get("resumen") else ""
    partes.append(f'<section id="{nombre}">{grupo}<h1>{meta["titulo"]}</h1>{resumen}{a_html(cuerpo)}</section>')

indice = "".join(f'<li><a href="#{n}">{m["titulo"]}</a></li>' for m, _, n in paginas)
html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
@page {{ size: A4; margin: 18mm 16mm 18mm 16mm; }}
body {{ font-family: "Helvetica Neue", Arial, sans-serif; font-size: 10pt; line-height: 1.5; color: #2f3133; }}
h1 {{ font-weight: 300; font-size: 21pt; line-height: 1.15; margin: 0 0 6pt; color: #1d1e20; }}
h2 {{ font-size: 12.5pt; font-weight: 600; margin: 16pt 0 6pt; color: #1d1e20; }}
section {{ page-break-before: always; }}
.portada {{ page-break-before: avoid; padding-top: 50mm; }}
.portada h1 {{ font-size: 30pt; }}
.grupo {{ text-transform: uppercase; letter-spacing: .14em; font-size: 7.5pt; font-weight: 700; color: #6b6f73; margin: 0 0 4pt; }}
.pregunta {{ font-size: 11pt; color: #3c3f42; border-left: 3px solid #2f3133; padding-left: 9pt; margin: 4pt 0 12pt; }}
table {{ border-collapse: collapse; width: 100%; font-size: 8.4pt; margin: 4pt 0 10pt; page-break-inside: auto; }}
tr {{ page-break-inside: avoid; }}
th, td {{ border-bottom: 1px solid #d9d9d6; padding: 4pt 5pt; text-align: left; vertical-align: top; }}
th {{ border-bottom: 1px solid #2f3133; }}
a {{ color: #2f3133; text-decoration: none; border-bottom: 1px solid #b8b8b4; }}
img {{ max-width: 100%; max-height: 105mm; display: block; margin: 6pt auto 10pt; }}
li {{ margin-bottom: 3pt; }}
.py-sem {{ display: inline-block; padding: 1pt 6pt; font-size: 7.5pt; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; border-left: 2.5pt solid currentColor; }}
.py-sem.verde {{ background: #e3efe4; color: #1f5a2b; }} .py-sem.ambar {{ background: #f8ecd0; color: #7a5200; }} .py-sem.rojo {{ background: #f6dcd8; color: #8a2419; }}
.py-sem-nota {{ color: #6b6f73; font-size: 9pt; margin-left: 6pt; }}
.py-aviso {{ background: #f4f4f2; border-left: 3px solid #5f8f8b; padding: 6pt 9pt; margin: 0 0 10pt; }}
.indice li {{ margin-bottom: 2pt; }}
</style></head><body>
<div class="portada"><p class="grupo">Asociación Colombiana de Endocrinología, Diabetes y Metabolismo · Festina Lente</p>
<h1>Mesa de expertos sobre la formulación de vitamina D</h1>
<p class="pregunta">Fichas de evidencia y resultados del formulario del panel. Prelectura para la sesión presencial del 13 de noviembre de 2026. Versión 1.0, 8 de noviembre de 2026.</p>
<h2>Contenido</h2><ol class="indice">{indice}</ol>
<p style="margin-top:30mm;color:#6b6f73;font-size:8.5pt">Documento de trabajo para el panel. Por favor no lo distribuya fuera del grupo de trabajo.</p></div>
{''.join(partes)}
</body></html>"""

tmp = PROY / "_fuentes" / "_fichas_pdf.html"
tmp.write_text(html, encoding="utf-8")
from playwright.sync_api import sync_playwright  # noqa: E402

with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_page()
    pg.goto(tmp.as_uri(), wait_until="networkidle")
    pg.pdf(path=str(DOCS / "Fichas_evidencia_vitD.pdf"), format="A4", print_background=True,
           display_header_footer=True, header_template="<span></span>",
           footer_template='<div style="font-size:7pt;color:#888;width:100%;text-align:center">'
                           'Mesa de expertos vitamina D · <span class="pageNumber"></span>/<span class="totalPages"></span></div>',
           margin={"top": "16mm", "bottom": "18mm", "left": "16mm", "right": "16mm"})
    nav.close()
tmp.unlink()
print("Documentos escritos en", DOCS.relative_to(RAIZ))
