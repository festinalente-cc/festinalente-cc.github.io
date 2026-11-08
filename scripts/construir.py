#!/usr/bin/env python3
"""Construye el sitio estático de Festina Lente en la carpeta sitio/.

Portada: sitio.yml + plantillas/portada.html
Proyectos: cada carpeta en proyectos/ con proyecto.yml (+ proyecto.md y documentos/)
           se publica en sitio/p/<carpeta>/ sin enlazarse desde la portada.
"""
from __future__ import annotations

import datetime as dt
import shutil
import subprocess
import sys
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

RAIZ = Path(__file__).resolve().parent.parent
PLANTILLAS = RAIZ / "plantillas"
PROYECTOS = RAIZ / "proyectos"
ESTATICOS = RAIZ / "estaticos"
SALIDA = RAIZ / "sitio"

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def a_fecha(v):
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    s = str(v).strip()
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def filtro_fecha(v):
    d = a_fecha(v)
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}" if d else str(v)


def filtro_mes(v):
    d = a_fecha(v)
    if not d:
        return str(v)
    s = str(v).strip()
    if len(s) <= 7:  # solo año o año-mes
        return f"{MESES[d.month - 1]} de {d.year}" if len(s) == 7 else str(d.year)
    return filtro_fecha(d)


def fecha_git(ruta: Path) -> dt.date:
    """Fecha del último commit que tocó la carpeta; si no hay git, hoy."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(ruta)],
            cwd=RAIZ, capture_output=True, text=True, check=True).stdout.strip()
        if out:
            return dt.date.fromisoformat(out)
    except Exception:
        pass
    return dt.date.today()


def main() -> int:
    sitio = yaml.safe_load((RAIZ / "sitio.yml").read_text(encoding="utf-8"))
    env = Environment(loader=FileSystemLoader(PLANTILLAS),
                      autoescape=select_autoescape(["html"]))
    env.filters["fecha"] = filtro_fecha
    env.filters["mes"] = filtro_mes

    # Logo: si existe estaticos/brand/wordmark.svg o .png se usa en la cabecera.
    marca_img = None
    for nombre in ("wordmark-dark.png",):
        if (ESTATICOS / "brand" / nombre).exists():
            marca_img = nombre
            break

    comun = dict(sitio=sitio, anio=dt.date.today().year, marca_img=marca_img)

    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir()

    # Estáticos
    if ESTATICOS.exists():
        shutil.copytree(ESTATICOS, SALIDA, dirs_exist_ok=True)
    shutil.copy(PLANTILLAS / "estilos.css", SALIDA / "estilos.css")

    # Portada y 404
    (SALIDA / "index.html").write_text(
        env.get_template("portada.html").render(raiz="/", **comun), encoding="utf-8")
    (SALIDA / "404.html").write_text(
        env.get_template("404.html").render(raiz="/", **comun), encoding="utf-8")

    # Buscadores: nada de este sitio se indexa (el sitio público es festinalente.cc).
    (SALIDA / "robots.txt").write_text(
        "User-agent: *\nDisallow: /\n", encoding="utf-8")
    (SALIDA / "p" / ".keep").parent.mkdir(exist_ok=True)
    # Un index vacío en /p/ evita que GitHub liste algo si alguien entra ahí.
    (SALIDA / "p" / "index.html").write_text(
        env.get_template("404.html").render(raiz="/", **comun), encoding="utf-8")

    # Proyectos
    md = markdown.Markdown(extensions=["extra", "sane_lists", "smarty"])
    plantilla = env.get_template("proyecto.html")
    publicados = []
    for carpeta in sorted(p for p in PROYECTOS.iterdir() if p.is_dir()):
        ficha = carpeta / "proyecto.yml"
        if not ficha.exists():
            continue
        p = yaml.safe_load(ficha.read_text(encoding="utf-8")) or {}
        if p.get("publicar", True) is False:
            continue
        slug = carpeta.name
        destino = SALIDA / "p" / slug
        destino.mkdir(parents=True)

        cuerpo = ""
        if (carpeta / "proyecto.md").exists():
            md.reset()
            cuerpo = md.convert((carpeta / "proyecto.md").read_text(encoding="utf-8"))

        docs = carpeta / "documentos"
        if docs.exists():
            shutil.copytree(docs, destino / "documentos")
            faltan = [d["archivo"] for d in p.get("documentos", [])
                      if not (docs / d["archivo"]).exists()]
            if faltan:
                print(f"AVISO {slug}: documentos declarados que no existen: {faltan}",
                      file=sys.stderr)

        fases = sitio.get("fases", [])
        fase_idx = fases.index(p["fase"]) if p.get("fase") in fases else -1
        p.setdefault("actualizado", fecha_git(carpeta))

        (destino / "index.html").write_text(
            plantilla.render(raiz="/", p=p, cuerpo=cuerpo, fase_idx=fase_idx, **comun),
            encoding="utf-8")
        publicados.append(slug)

    print(f"Portada y {len(publicados)} proyecto(s): {', '.join(publicados)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
