/**
 * Receptor de la encuesta a socios de la ACE (hipoparatiroidismo).
 *
 * Instalación (una sola vez):
 *  1. Cree una hoja de Google nueva, p. ej. «Encuesta socios ACE – hipoparatiroidismo».
 *  2. Extensiones → Apps Script. Borre el contenido y pegue este archivo. Guarde.
 *  3. Ejecute una vez la función `preparar` (pide permisos) para crear las pestañas.
 *  4. (Opcional) Si en algún momento se tiene la lista de miembros del comité, pegue en la pestaña
 *     «Directorio», desde la fila 2: columna A correo, B capítulo, C categoría. Sin lista, déjela vacía:
 *     la columna verificado_socio quedará en «no» y no afecta el envío.
 *     La hoja NO debe compartirse: contiene datos personales.
 *  5. Implementar → Nueva implementación → Tipo: Aplicación web.
 *     Ejecutar como: Yo. Quién tiene acceso: Cualquier persona. Implementar.
 *  6. Copie la URL que termina en /exec y péguela en data-endpoint de paginas/01-encuesta.md.
 *  Al cambiar este código: Implementar → Gestionar implementaciones → Editar → Nueva versión
 *  (así la URL no cambia).
 *
 * Datos: «Identidad» (id, fecha, nombre, correo, verificado, duplicado, agradecimientos) y
 * «Respuestas» (id, fecha, versión y una columna por pregunta). El id es el único vínculo;
 * el análisis se hace solo con «Respuestas». Regla de duplicados: se analiza el último envío
 * de cada correo.
 */
var HOJAS = { identidad: "Identidad", respuestas: "Respuestas", directorio: "Directorio" };

function preparar() {
  var ss = SpreadsheetApp.getActive();
  hoja_(ss, HOJAS.identidad, ["id", "fecha", "nombre", "correo", "verificado_socio", "capitulo_directorio", "categoria_directorio", "envio_previo", "agradecimientos", "consentimiento"]);
  hoja_(ss, HOJAS.respuestas, ["id", "fecha", "version"]);
  hoja_(ss, HOJAS.directorio, ["correo", "capitulo", "categoria"]);
}

function doGet() {
  return salida_({ ok: true, servicio: "encuesta socios ACE hipoparatiroidismo" });
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
    var d = JSON.parse(e.postData.contents);
    if (d.trampa) return salida_({ ok: true });                       // envío de un robot: se descarta
    if (!d.id || !d.identidad || !d.respuestas) return salida_({ ok: false, error: "incompleto" });
    if (e.postData.contents.length > 60000) return salida_({ ok: false, error: "demasiado largo" });
    var idt = d.identidad, correo = String(idt.correo || "").trim().toLowerCase();
    if (idt.consentimiento !== "si" || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) {
      return salida_({ ok: false, error: "consentimiento o correo" });
    }
    var ss = SpreadsheetApp.getActive();
    preparar();
    var shI = ss.getSheetByName(HOJAS.identidad), shR = ss.getSheetByName(HOJAS.respuestas);
    var ahora = new Date();

    var shD = ss.getSheetByName(HOJAS.directorio);
    var dir = shD.getLastRow() > 1 ? shD.getRange(2, 1, shD.getLastRow() - 1, 3).getValues() : [];
    var socio = dir.filter(function (r) { return String(r[0]).trim().toLowerCase() === correo; })[0];
    var previos = shI.getLastRow() > 1 ? shI.getRange(2, 4, shI.getLastRow() - 1, 1).getValues()
      .filter(function (r) { return String(r[0]).toLowerCase() === correo; }).length : 0;

    shI.appendRow([d.id, ahora, limpiar_(idt.nombre), correo, socio ? "si" : "no",
                   socio ? limpiar_(socio[1]) : "", socio ? limpiar_(socio[2]) : "",
                   previos, idt.agradecimientos === "si" ? "si" : "no", "si"]);

    // Respuestas: una columna por campo; los campos nuevos se agregan al final del encabezado.
    var enc = shR.getRange(1, 1, 1, shR.getLastColumn()).getValues()[0];
    Object.keys(d.respuestas).forEach(function (k) {
      if (enc.indexOf(k) < 0) { enc.push(k); shR.getRange(1, enc.length).setValue(k); }
    });
    var fila = enc.map(function (k) {
      if (k === "id") return d.id;
      if (k === "fecha") return ahora;
      if (k === "version") return limpiar_(d.version);
      return k in d.respuestas ? limpiar_(d.respuestas[k]) : "";
    });
    shR.appendRow(fila);
    return salida_({ ok: true, id: d.id });
  } catch (err) {
    return salida_({ ok: false, error: String(err) });
  } finally {
    try { lock.releaseLock(); } catch (e) { }
  }
}

function hoja_(ss, nombre, encabezado) {
  var sh = ss.getSheetByName(nombre) || ss.insertSheet(nombre);
  if (sh.getLastRow() === 0) sh.appendRow(encabezado);
  return sh;
}
// Evita fórmulas inyectadas en la hoja y recorta textos largos.
function limpiar_(v) {
  var s = String(v == null ? "" : v).slice(0, 4000);
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}
function salida_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
