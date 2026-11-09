#!/usr/bin/env python3
"""Genera las páginas del micrositio de la mesa de expertos de vitamina D.

Lee, en proyectos/<slug>/_fuentes/:
  fichas.md   fichas de evidencia exportadas del documento de trabajo (Markdown):
              '## Cómo leer las fichas', '## Resumen', '## Eje N. ...' con '### Tn. Título – Semáforo',
              '## Preguntas para la sesión ...' y '## Método y referencias' (tabla Código | Referencia | Calidad)
  panel.md    texto de la página «Lo que respondió el panel» (figuras en documentos/figuras/)
y escribe proyectos/<slug>/paginas/*.md. Volver a correrlo sobrescribe las páginas generadas.

Uso:  python scripts/vitd_paginas.py vitd-mesa-ace-6q2n
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
slug = sys.argv[1] if len(sys.argv) > 1 else "vitd-mesa-ace-6q2n"
PROY = RAIZ / "proyectos" / slug
FUENTES = PROY / "_fuentes"
SALIDA = PROY / "paginas"
SALIDA.mkdir(exist_ok=True)
for viejo in SALIDA.glob("*.md"):
    viejo.unlink()

texto = (FUENTES / "fichas.md").read_text(encoding="utf-8")
texto = texto.replace("\\[", "[").replace("\\]", "]")

SEM = {"verde": ("verde", "Verde · respaldada"),
       "ámbar": ("ambar", "Ámbar · emergente o condicional"),
       "rojo": ("rojo", "Rojo · sin respaldo")}


def insignia(palabra: str, corta: bool = False) -> str:
    clave, largo = SEM[palabra.lower()]
    return f'<span class="py-sem {clave}">{palabra.capitalize() if corta else largo}</span>'


def secciones(md: str, nivel: str) -> list[tuple[str, str]]:
    """Divide por encabezados de un nivel ('## ' o '### '): [(título, cuerpo)]."""
    partes = re.split(rf"^{re.escape(nivel)}(.+)$", md, flags=re.M)
    return [(partes[i].strip(), partes[i + 1].strip()) for i in range(1, len(partes), 2)]


def yaml_texto(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def escribir(nombre: str, titulo: str, orden: int, grupo: str, resumen: str, cuerpo: str) -> None:
    cab = (f"---\ntitulo: {yaml_texto(titulo)}\norden: {orden}\ngrupo: {yaml_texto(grupo)}\n"
           f"resumen: {yaml_texto(resumen)}\n---\n")
    (SALIDA / f"{nombre}.md").write_text(cab + cuerpo.strip() + "\n", encoding="utf-8")


secs = dict(secciones(texto, "## "))
orden_secs = [t for t, _ in secciones(texto, "## ")]

# ---------- referencias ----------------------------------------------------------
metodo = secs["Método y referencias"]
refs: dict[str, tuple[str, str]] = {}
for fila in re.findall(r"^\| (VD\d{3}) \| (.+?) \| ([^|]+?) \|$", metodo, flags=re.M):
    refs[fila[0]] = (fila[1], fila[2])

def enlazar_codigos(md: str) -> str:
    return re.sub(r"\b(VD\d{3})\b", lambda m: f"[{m.group(1)}](../referencias/#{m.group(1).lower()})", md)

# ---------- página de resumen ----------------------------------------------------
def tabla_resumen(md: str) -> str:
    def fila(m: re.Match) -> str:
        celdas = [c.strip() for c in m.group(0).strip("|").split("|")]
        if len(celdas) == 4 and celdas[2].lower() in SEM:
            codigo = celdas[0].split()[0].lower()
            celdas[0] = f"[{celdas[0]}](../{codigo}/)"
            celdas[2] = insignia(celdas[2], corta=True)
            return "| " + " | ".join(celdas) + " |"
        return m.group(0)
    return re.sub(r"^\|.+\|$", fila, md, flags=re.M)

leer = secs["Cómo leer las fichas"]
leer = re.sub(r"^\| (Verde|Ámbar|Rojo) – ", lambda m: f"| {insignia(m.group(1), corta=True)} ", leer, flags=re.M)
leer = leer.replace("Los códigos VD001 a VD074 remiten al corpus de 74 estudios y aparecen en la sección final.",
                    "Los códigos VD001 a VD074 remiten al corpus de 74 estudios y llevan a la página de [referencias](../referencias/).")
cuerpo = ("## Los 14 temas de un vistazo\n\n" + tabla_resumen(secs["Resumen"]) +
          "\n\n## Cómo leer las fichas\n\n" + leer)
escribir("resumen", "Resumen y cómo leer las fichas", 0, "Para empezar",
         "Los 14 temas con su semáforo y la guía para leer cada ficha.", cuerpo)

# ---------- página del panel -----------------------------------------------------
escribir("panel", "Lo que respondió el panel", 1, "Para empezar",
         "Práctica actual, factores que impulsan la formulación, familiaridad y expectativas por eje, según el formulario.",
         (FUENTES / "panel.md").read_text(encoding="utf-8"))

# ---------- fichas por tema ------------------------------------------------------
orden = 2
for titulo_eje in [t for t in orden_secs if t.startswith("Eje ")]:
    for titulo, cuerpo in secciones(secs[titulo_eje], "### "):
        m = re.match(r"(T\d+[ab]?)\. (.+?) – (Verde|Ámbar|Rojo)(.*)$", titulo)
        codigo, nombre, sem, matiz = m.group(1), m.group(2), m.group(3), m.group(4).strip()
        pregunta = re.search(r"^\*\*Pregunta\.\*\* (.+)$", cuerpo, flags=re.M).group(1)
        cuerpo = re.sub(r"^\*\*Pregunta\.\*\* .+\n*", "", cuerpo, flags=re.M)
        cuerpo = re.sub(r"^\*\*(Lo que dijo el panel|Lo que muestra la evidencia|Para discutir)\.\*\*\s*",
                        lambda x: f"## {x.group(1)}\n\n", cuerpo, flags=re.M)
        citados = sorted(set(re.findall(r"\bVD\d{3}\b", cuerpo)))
        cuerpo = enlazar_codigos(cuerpo)
        cab = f'<p class="py-semaforo">{insignia(sem)}'
        if matiz:
            cab += f' <span class="py-sem-nota">{matiz.strip("() ")}</span>'
        cab += "</p>\n\n"
        tabla = ["| Código | Referencia | Calidad |", "| --- | --- | --- |"]
        for c in citados:
            ref, cal = refs[c]
            tabla.append(f"| [{c}](../referencias/#{c.lower()}) | {ref} | {cal} |")
        cuerpo = cab + cuerpo + "\n\n## Estudios citados en esta ficha\n\n" + "\n".join(tabla)
        escribir(codigo.lower(), f"{codigo}. {nombre}", orden, titulo_eje, pregunta, cuerpo)
        orden += 1

# ---------- preguntas para la sesión ---------------------------------------------
t_preg = next(t for t in orden_secs if t.startswith("Preguntas para la sesión"))
preg = re.sub(r"\(((?:T\d+[ab]?(?:, )?)+)\)",
              lambda m: "(" + ", ".join(f"[{c}](../{c.lower()}/)" for c in m.group(1).split(", ")) + ")",
              secs[t_preg])
escribir("preguntas", "Preguntas para la sesión", orden, "Para la sesión",
         "Cinco preguntas transversales para ordenar la discusión presencial del 13 de noviembre.", preg)
orden += 1

# ---------- referencias ----------------------------------------------------------
intro = metodo.split("| Código |")[0].strip()
tabla = ["| Código | Referencia | Calidad |", "| --- | --- | --- |"]
for c, (ref, cal) in refs.items():
    tabla.append(f'| <span id="{c.lower()}">{c}</span> | {ref} | {cal} |')
escribir("referencias", "Método y referencias", orden, "Para la sesión",
         "Cómo se armaron las fichas y los 74 estudios del corpus, con su calidad.",
         "## Método\n\n" + intro + "\n\n## Los 74 estudios\n\n" + "\n".join(tabla))

print(f"{len(list(SALIDA.glob('*.md')))} páginas escritas en {SALIDA.relative_to(RAIZ)}")
