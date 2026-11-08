# Sitio de Festina Lente

Sitio estático publicado con GitHub Pages en <https://festinalente-cc.github.io> (y, cuando se conecte el dominio, en <https://festinalente.cc>).

- **Portada:** copia fiel del sitio original de festinalente.cc. El contenido está en `plantillas/portada.html`; los estilos originales en `plantillas/estilos.css` (los de los micrositios van al final, con prefijo `py-`). Datos comunes (correo, ciudad, fases) en `sitio.yml`.
- **Proyectos:** una carpeta por proyecto en `proyectos/`, publicada en `/p/<carpeta>/`. No se enlazan desde la portada ni se indexan: solo llega quien tenga el enlace.
- **Marca:** en `estaticos/brand/` están el isotipo (PNG 1200 px y `isotipo-vector.svg` extraído del manual), los wordmarks claro y oscuro y el fondo del encabezado. Las portadas de las publicaciones van en `estaticos/work/`.

## Crear un proyecto

1. Copiar `proyectos/ejemplo` con un nombre nuevo. El nombre de la carpeta es la dirección; para que no sea adivinable, agregar un código corto, p. ej. `consenso-eot-7k3q`.
2. Editar `proyecto.yml` (ficha, equipo, panel, cronograma, documentos, novedades) y `proyecto.md` (texto libre en Markdown).
3. Poner los archivos descargables en `documentos/` y declararlos en `proyecto.yml`.
4. Push a `main`. En 1–2 minutos está en línea.

Para ocultar un proyecto sin borrarlo: `publicar: false` en su `proyecto.yml`.

## Privacidad

En los micrositios solo van nombre, afiliación y ciudad de los panelistas. Nunca correos, teléfonos ni documentos de identidad. Las páginas de proyectos llevan `noindex` y `robots.txt` excluye `/p/`, pero son públicas para quien tenga el enlace: no publicar nada confidencial.

## Construir en local

```
pip install markdown pyyaml jinja2
python scripts/construir.py
python -m http.server -d sitio 8000
```
