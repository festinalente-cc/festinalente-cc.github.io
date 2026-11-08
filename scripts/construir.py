#!/usr/bin/env python3
"""Construye el sitio estático de Festina Lente en la carpeta sitio/.

Portada: sitio.yml + plantillas/portada.html
Proyectos: cada carpeta en proyectos/ con proyecto.yml (+ proyecto.md y documentos/)
           se publica en sitio/p/<carpeta>/ sin enlazarse desde la portada.
"""
from __future__ import annotations

import base64
import datetime as dt
import json
import os
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


def separar_frontmatter(texto: str):
    """Devuelve (meta, cuerpo) si el archivo empieza con un bloque YAML entre '---'."""
    if texto.startswith("---"):
        partes = texto.split("---", 2)
        if len(partes) == 3:
            return (yaml.safe_load(partes[1]) or {}), partes[2].lstrip("\n")
    return {}, texto


FICHAS: list = []


def cifrar(texto: str, clave: str) -> str:
    """AES-256-GCM con clave derivada por PBKDF2; se descifra con WebCrypto en el navegador."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    salt, iv, iteraciones = os.urandom(16), os.urandom(12), 600_000
    k = PBKDF2HMAC(hashes.SHA256(), 32, salt, iteraciones).derive(clave.encode())
    datos = AESGCM(k).encrypt(iv, texto.encode("utf-8"), None)
    b = lambda x: base64.b64encode(x).decode()
    return json.dumps({"salt": b(salt), "iv": b(iv), "iter": iteraciones, "datos": b(datos)})


def construir_indice(env, sitio, comun):
    clave = os.environ.get("INDICE_CLAVE")
    if not clave:
        print("AVISO: sin INDICE_CLAVE; no se genera el índice interno.", file=sys.stderr)
        return
    base = sitio.get("url_proyectos") or "https://festinalente-cc.github.io"
    filas = []
    for slug, p in FICHAS:
        url = f"{base}/p/{slug}/"
        ahora = (p.get("ahora") or {})
        plazo = ahora.get("plazo")
        plantilla = p.get("mensaje") or sitio.get("mensaje") or "{url}"
        mensaje = plantilla.format(
            titulo=p.get("titulo", slug), url=url,
            ahora=(ahora.get("titulo") + ". ") if ahora.get("titulo") else "",
            plazo=f"Plazo para comentarios: {filtro_fecha(plazo)}." if plazo else "")
        filas.append(dict(slug=slug, url=url, titulo=p.get("titulo", slug), cliente=p.get("cliente"),
                          fase=p.get("fase"), plazo=plazo, ahora_titulo=ahora.get("titulo"),
                          publicado=p.get("publicar", True) is not False,
                          asunto=f"Proyecto: {p.get('titulo', slug)}", mensaje=mensaje))
    interior = env.get_template("indice_contenido.html").render(proyectos=filas, **comun)
    (SALIDA / "indice").mkdir(exist_ok=True)
    (SALIDA / "indice" / "index.html").write_text(
        env.get_template("indice.html").render(raiz="/", cifrado=cifrar(interior, clave), **comun),
        encoding="utf-8")
    print("Índice interno cifrado: /indice/")


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
        slug = carpeta.name
        FICHAS.append((slug, p))
        if p.get("publicar", True) is False:
            continue
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

        # Subpáginas: proyectos/<slug>/paginas/<nombre>.md con encabezado YAML
        # (titulo, orden, grupo, resumen, formulario). Se publican en /p/<slug>/<nombre>/.
        paginas = []
        carpeta_pag = carpeta / "paginas"
        if carpeta_pag.exists():
            for archivo in sorted(carpeta_pag.glob("*.md")):
                meta, texto = separar_frontmatter(archivo.read_text(encoding="utf-8"))
                md.reset()
                paginas.append(dict(
                    nombre=archivo.stem, titulo=meta.get("titulo", archivo.stem),
                    orden=meta.get("orden", 999), grupo=meta.get("grupo", ""),
                    resumen=meta.get("resumen", ""), formulario=meta.get("formulario"),
                    html=md.convert(texto)))
            paginas.sort(key=lambda x: (x["orden"], x["nombre"]))
            grupos = []
            for pg in paginas:
                if not grupos or grupos[-1]["nombre"] != pg["grupo"]:
                    grupos.append(dict(nombre=pg["grupo"], paginas=[]))
                grupos[-1]["paginas"].append(pg)
            p["paginas"] = paginas
            p["grupos_paginas"] = grupos
            plantilla_pag = env.get_template("pagina.html")
            for i, pg in enumerate(paginas):
                d = destino / pg["nombre"]
                d.mkdir(parents=True)
                (d / "index.html").write_text(
                    plantilla_pag.render(raiz="/", p=p, pg=pg, slug=slug,
                                         anterior=paginas[i - 1] if i > 0 else None,
                                         siguiente=paginas[i + 1] if i + 1 < len(paginas) else None,
                                         **comun), encoding="utf-8")

        (destino / "index.html").write_text(
            plantilla.render(raiz="/", p=p, cuerpo=cuerpo, fase_idx=fase_idx, **comun),
            encoding="utf-8")
        publicados.append(slug + (f" (+{len(paginas)} páginas)" if paginas else ""))

    construir_indice(env, sitio, comun)
    print(f"Portada y {len(publicados)} proyecto(s): {', '.join(publicados)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
