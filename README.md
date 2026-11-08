# Sitio de Festina Lente

Sitio estático publicado con GitHub Pages en <https://festinalente-cc.github.io> (y, cuando se conecte el dominio, en <https://festinalente.cc>).

- **Portada:** textos en `sitio.yml`; diseño en `plantillas/portada.html` y `plantillas/estilos.css`.
- **Proyectos:** una carpeta por proyecto en `proyectos/`, publicada en `/p/<carpeta>/`. No se enlazan desde la portada ni se indexan: solo llega quien tenga el enlace.
- **Logo:** poner `wordmark.svg` (o `.png`) en `estaticos/brand/` y aparecerá en la cabecera.

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
