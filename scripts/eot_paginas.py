#!/usr/bin/env python3
"""Genera las páginas del micrositio del panel EOT a partir de las fichas de evidencia.

Lee, en proyectos/<slug>/_fuentes/:
  fichas.md            fichas de evidencia (una sección '## Pxx ...' por pregunta)
  parametros.csv       parámetros numéricos de la ronda 1 (codigo, titulo, unidad, escenario, preguntas, nota)
  formularios_kobo.csv (opcional) salida de kobo_desplegar.R; se usa url_iframe por código (F0, P01..P19, F4)
y escribe proyectos/<slug>/paginas/*.md. Volver a correrlo sobrescribe las páginas generadas.

Uso:  python scripts/eot_paginas.py eot-estandares-4h7p
"""
from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
slug = sys.argv[1] if len(sys.argv) > 1 else "eot-estandares-4h7p"
PROY = RAIZ / "proyectos" / slug
FUENTES = PROY / "_fuentes"
SALIDA = PROY / "paginas"
SALIDA.mkdir(exist_ok=True)

# ---------- insumos --------------------------------------------------------------
texto = (FUENTES / "fichas.md").read_text(encoding="utf-8")

params = list(csv.DictReader((FUENTES / "parametros.csv").open(encoding="utf-8")))
par_por_pregunta: dict[str, list[dict]] = defaultdict(list)
for p in params:
    for q in [x.strip() for x in p["preguntas"].split(",")]:
        par_por_pregunta[q].append(p)

enlaces: dict[str, str] = {}
f_kobo = FUENTES / "formularios_kobo.csv"
if f_kobo.exists():
    for r in csv.DictReader(f_kobo.open(encoding="utf-8")):
        if r.get("url_iframe"):
            enlaces[r["codigo"]] = r["url_iframe"]

# Afirmaciones añadidas por el equipo (no están en las fichas originales)
NUEVAS_P12 = [
    "En adultos tratados con metilprednisolona intravenosa por EOT, el tratante debe medir enzimas hepáticas, glucemia y presión arterial antes de cada infusión o al menos mensualmente, y suspender el ciclo ante elevación significativa de transaminasas \\[0169, 0221, 0229, 0005\\].",
    "En adultos tratados con micofenolato por EOT, el tratante debe controlar hemograma y enzimas hepáticas al inicio, a las 4 semanas y luego al menos cada 3 meses mientras dure el tratamiento \\[0169, 0016\\].",
    "Antes de rituximab o tocilizumab por EOT, debe tamizarse hepatitis B y tuberculosis latente; durante tocilizumab deben vigilarse neutrófilos, enzimas hepáticas y lípidos, y durante rituximab las reacciones infusionales y las infecciones \\[0151, 0169, 0202, 0168\\].",
    "Todo servicio que prescriba inmunomoduladores para EOT debe contar con un protocolo escrito de vigilancia de seguridad por fármaco, con responsable definido y registro de los controles en la historia clínica *(afirmación de práctica, sin fuente directa en las fichas)*.",
]

# ---------- utilidades -----------------------------------------------------------
def frontmatter(**kw) -> str:
    lineas = ["---"]
    for k, v in kw.items():
        if v is None or v == "":
            continue
        v = str(v).replace('"', "'")
        lineas.append(f'{k}: "{v}"' if k in ("titulo", "resumen", "grupo", "formulario") else f"{k}: {v}")
    lineas.append("---\n")
    return "\n".join(lineas)


def bloque_elicitacion(codigo: str, original: str) -> str:
    original = original.strip()
    original = re.sub(r"^Elicitación numérica:\s*", "", original)
    mios = par_por_pregunta.get(codigo, [])
    out = ["**Parámetros numéricos.** La ficha identificó la necesidad de elicitación: " + original]
    if mios:
        out.append("")
        out.append("En esta ronda se piden para esta pregunta, en la página *Parámetros numéricos*:")
        out.append("")
        for p in mios:
            out.append(f"- **{p['titulo']}** ({p['unidad']}). Escenario: {p['escenario']}.")
        out.append("")
        out.append("Los demás plazos o umbrales que señala la ficha se tratarán en la reunión del panel y, si procede, se calificarán como afirmaciones en la ronda 2.")
    else:
        out.append("")
        out.append("En esta ronda no se pide ningún parámetro numérico para esta pregunta. Los plazos o umbrales que señala la ficha se tratarán en la reunión del panel y, si procede, se calificarán como afirmaciones en la ronda 2.")
    return "\n".join(out)


def lista_dos_digitos(s: str) -> str:
    return s


# ---------- partir las fichas -----------------------------------------------------
secciones = re.split(r"^## ", texto, flags=re.M)
cabecera = secciones[0]
fichas = {}
referencias = None
for sec in secciones[1:]:
    titulo, _, cuerpo = sec.partition("\n")
    m = re.match(r"(P\d\d) (.+)", titulo.strip())
    if m:
        fichas[m.group(1)] = (m.group(2).strip(), cuerpo.strip())
    elif titulo.strip().startswith("Referencias"):
        referencias = cuerpo.strip()

assert len(fichas) == 19, f"se esperaban 19 fichas, hay {len(fichas)}"

# ---------- página 00 · registro ----------------------------------------------------
registro = frontmatter(titulo="Paso 1 · Registro y conflictos de interés", orden=0, grupo="Antes de calificar",
                       resumen="Complete este formulario una sola vez, antes de las preguntas. Sus datos los conoce solo la secretaría técnica.",
                       formulario=enlaces.get("F0")) + """
## Qué pide el registro

Nombre, correo, especialidad, institución, ciudad, ámbito de práctica, años de experiencia y volumen de pacientes con EOT; la declaración de conflictos de interés de los últimos tres años; y la confirmación de que leyó la guía y acepta las condiciones de participación.

## Por qué el correo

El **correo electrónico** es la llave que une sus respuestas de los 21 formularios de la ronda (registro, 19 preguntas y parámetros). Escríbalo igual en todos. Solo la secretaría técnica lo conoce; al grupo las calificaciones llegan de forma anónima.

## Conflictos de interés

Declare los vínculos de los últimos tres años por tipo (honorarios, investigación financiada, participación económica, autoría de guías o estudios sobre EOT, cargos institucionales) y los productos o empresas relacionados con la EOT con los que los haya tenido. La secretaría técnica define, por pregunta, cuándo un vínculo es relevante; en ese caso se le pedirá marcar «No califico» en los ítems correspondientes. Declarar un vínculo no excluye del panel.

<div class="py-aviso">Después de enviar el registro, continúe con las preguntas P01 a P19 en el orden que prefiera y termine con los parámetros numéricos. Puede hacerlo en varias sesiones.</div>
"""
(SALIDA / "00-registro.md").write_text(registro, encoding="utf-8")

# ---------- páginas P01–P19 ----------------------------------------------------------
for i, (codigo, (nombre, cuerpo)) in enumerate(sorted(fichas.items()), start=1):
    # resumen = primer párrafo antes de '### Identificación'
    pre, _, resto = cuerpo.partition("### Identificación")
    resumen = " ".join(pre.strip().split())
    resumen = re.sub(r"\\\[", "[", resumen); resumen = re.sub(r"\\\]", "]", resumen)
    mq = re.search(r'Pregunta marco:\s*[«"“]?\s*(¿[^?]+\?)', resto)
    resumen_corto = mq.group(1).strip() if mq else (resumen if len(resumen) <= 220 else resumen[:217].rsplit(" ", 1)[0] + "…")
    cuerpo_md = "### Identificación" + resto

    # elicitación → bloque reescrito
    cuerpo_md = re.sub(r"^Elicitación numérica:.*?$(?=\n\n|\n###)",
                       lambda m: bloque_elicitacion(codigo, m.group(0)), cuerpo_md, count=1, flags=re.M | re.S)

    # P12: añadir afirmaciones 7–10 al final de la lista de deliberación
    if codigo == "P12":
        def agregar(m):
            lista = m.group(0).rstrip("\n")
            n = len(re.findall(r"^\d+\. ", lista, flags=re.M))
            extra = "\n".join(f"{n + k}. {t}" for k, t in enumerate(NUEVAS_P12, start=1))
            return lista + "\n" + extra + "\n\nLas afirmaciones 7 a 10 fueron añadidas por el equipo técnico tras revisar la cobertura de la vigilancia de seguridad por fármaco; sus frecuencias provienen de la práctica y de las fichas técnicas, no de las fichas de evidencia, salvo donde se cita una fuente.\n"
        cuerpo_md = re.sub(r"(?<=### Deliberación\n\n)(?:^\d+\. .*\n?)+", agregar, cuerpo_md, count=1, flags=re.M)

    # el '###' de la ficha pasa a '##' dentro de la página
    cuerpo_md = re.sub(r"^### ", "## ", cuerpo_md, flags=re.M)

    n_items = len(re.findall(r"^\d+\. ", cuerpo_md.split("## Deliberación")[1].split("##")[0], flags=re.M)) if "## Deliberación" in cuerpo_md else ""
    intro = (f"> {resumen}\n\n" if resumen else "")
    pagina = frontmatter(titulo=f"{codigo} {nombre}", orden=i, grupo="Preguntas",
                         resumen=resumen_corto, formulario=enlaces.get(codigo)) + intro + cuerpo_md.strip() + "\n"
    (SALIDA / f"{i:02d}-{codigo.lower()}.md").write_text(pagina, encoding="utf-8")

# ---------- página 20 · parámetros ------------------------------------------------------
filas = ["| N.º | Parámetro | Unidad | Escenario | Preguntas |", "| --- | --- | --- | --- | --- |"]
for p in params:
    nota = f" *{p['nota']}*" if p["nota"] else ""
    filas.append(f"| {p['codigo'][3:]} | **{p['titulo']}**{nota} | {p['unidad']} | {p['escenario']} | {p['preguntas']} |")
parametros = frontmatter(titulo="Paso 3 · Parámetros numéricos", orden=20, grupo="Para terminar",
                         resumen=f"{len(params)} plazos, intervalos y umbrales que la evidencia no fija y que el panel propone como juicio experto.",
                         formulario=enlaces.get("F4")) + f"""
## Qué se le pide

Cuando la evidencia no fija un plazo o una frecuencia, el panel aporta su juicio como valor numérico. Cada parámetro llega definido: escenario clínico, unidad, momento de inicio y de fin. Usted indica el **valor central** que propondría como estándar, el **intervalo defendible** (mínimo y máximo que considera aceptables), su **confianza** (baja, media, alta) y una frase de **fundamento**. Son juicios, no intervalos de confianza estadísticos. Puede dejar en blanco los parámetros que estén fuera de su competencia.

El panel recibirá la mediana de las propuestas y su dispersión. Tras la reunión, el valor discutido se convierte en una afirmación completa que se califica en la ronda 2 con la escala de apropiación. La mediana numérica, por sí sola, no aprueba un estándar.

## Los {len(params)} parámetros de esta ronda

{chr(10).join(filas)}

Las fichas señalan otros plazos y umbrales que la evidencia no fija. No se piden en esta ronda: se tratarán en la reunión del panel y, si procede, se calificarán como afirmaciones en la ronda 2.
"""
(SALIDA / "20-parametros.md").write_text(parametros, encoding="utf-8")

# ---------- página 21 · referencias -------------------------------------------------------
if referencias:
    refs = frontmatter(titulo="Referencias citadas en las fichas", orden=21, grupo="Materiales",
                       resumen="Las fuentes citadas en las fichas, por código. La lista completa de las 234 publicaciones incluidas está en Documentos.")
    refs += "\n" + re.sub(r"^### ", "## ", referencias, flags=re.M) + "\n"
    (SALIDA / "21-referencias.md").write_text(refs, encoding="utf-8")

print(f"{len(list(SALIDA.glob('*.md')))} páginas en {SALIDA.relative_to(RAIZ)}; "
      f"enlaces de formulario: {len(enlaces)} de 21")
