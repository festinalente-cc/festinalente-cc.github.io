/**
 * Receptor de la validación del borrador del informe, mesa de expertos de vitamina D.
 *
 * Instalación (una sola vez):
 *  1. Cree una hoja de Google nueva, p. ej. «Validación informe – mesa vitamina D». No la comparta.
 *  2. Extensiones → Apps Script. Borre el contenido, pegue este archivo y guarde.
 *  3. Ejecute una vez la función `preparar` (pide permisos) para crear la pestaña «Respuestas».
 *  4. Implementar → Nueva implementación → Tipo: Aplicación web.
 *     Ejecutar como: Yo. Quién tiene acceso: Cualquier persona. Implementar.
 *  5. Copie la URL que termina en /exec y péguela en data-endpoint de paginas/validacion.md.
 *  Al cambiar este código: Implementar → Gestionar implementaciones → Editar → Nueva versión
 *  (así la URL no cambia).
 *
 * Datos: una fila por envío, identificada con el nombre del panelista (el panel aceptó responder
 * con nombre). Regla de duplicados: se analiza el último envío de cada panelista.
 */
var HOJA = "Respuestas";

function preparar() {
  var ss = SpreadsheetApp.getActive();
  var sh = ss.getSheetByName(HOJA) || ss.insertSheet(HOJA);
  if (sh.getLastRow() === 0) sh.appendRow(["id", "fecha", "version", "panelista"]);
  return sh;
}

function doGet() {
  return salida_({ ok: true, servicio: "validación informe mesa vitamina D" });
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
    if (e.postData.contents.length > 60000) return salida_({ ok: false, error: "demasiado largo" });
    var d = JSON.parse(e.postData.contents);
    if (d.trampa) return salida_({ ok: true });                       // envío de un robot: se descarta
    if (!d.id || !d.panelista || !d.respuestas) return salida_({ ok: false, error: "incompleto" });
    var sh = preparar();
    var enc = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0];
    Object.keys(d.respuestas).forEach(function (k) {
      if (enc.indexOf(k) < 0) { enc.push(k); sh.getRange(1, enc.length).setValue(k); }
    });
    var fila = enc.map(function (k) {
      if (k === "id") return d.id;
      if (k === "fecha") return new Date();
      if (k === "version") return limpiar_(d.version);
      if (k === "panelista") return limpiar_(d.panelista);
      return k in d.respuestas ? limpiar_(d.respuestas[k]) : "";
    });
    sh.appendRow(fila);
    return salida_({ ok: true, id: d.id });
  } catch (err) {
    return salida_({ ok: false, error: String(err) });
  } finally {
    try { lock.releaseLock(); } catch (e) { }
  }
}

// Evita fórmulas inyectadas en la hoja y recorta textos largos.
function limpiar_(v) {
  var s = String(v == null ? "" : v).slice(0, 4000);
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}
function salida_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
