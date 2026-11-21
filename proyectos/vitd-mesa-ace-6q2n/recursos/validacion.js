/* Validación del borrador del informe, mesa de expertos de vitamina D.
 * Renderiza las preguntas dentro de #enc-raiz y envía las respuestas a un Google Apps Script
 * (data-endpoint; código en _fuentes/apps_script_validacion.gs). Sin endpoint, funciona en modo de prueba.
 * Los nombres de campo son estables para el análisis.
 */
(function () {
  "use strict";
  var raiz = document.getElementById("enc-raiz");
  if (!raiz) return;
  var ENDPOINT = (raiz.getAttribute("data-endpoint") || "").trim();
  var VERSION = raiz.getAttribute("data-version") || "sin-version";
  var CLAVE_BORRADOR = "val-vitd-" + VERSION;

  var PANEL = [
    "Geraldine Altamar Canales", "Andrés Felipe Coy Barrera", "David Monroy Duque", "Jorge Iván Palacio Uribe",
    "Pilar Cristina Ruiz Blanco", "José Luis Torres Grajales", "Esdras Martín Vásquez Mejía"
  ];
  var REFLEJA = [["refleja", "Refleja mi opinión"], ["cambios", "Refleja mi opinión con cambios"], ["no_refleja", "No refleja mi opinión"]];

  // ------------------------------------------------------------------ contenido
  var PREGUNTAS = [
    {
      id: "Q1", titulo: "Definiciones de dosis y bolos", ancla: "41-bloque-transversal-diagnostico-esquemas-y-adulto-mayor",
      html:
        "<p>Para la discusión usamos estas definiciones: mantenimiento diario, 800 a 2.000 UI; dosis diaria alta, hasta 4.000 UI; " +
        "esquema intermitente, intervalos de una semana o más; megadosis o bolo, 100.000 UI o más en una sola toma.</p>" +
        "<p>El informe recogería como punto de vista del panel que <strong>no hay adulto mayor en quien se justifique un bolo de 100.000 UI o más</strong>.</p>",
      extra: { id: "Q1_techo", txt: "Para prevenir caídas, en la sala se planteó no superar 50.000 a 60.000 UI por toma. ¿Lo comparte?",
               ops: [["comparte", "Lo comparto: que quede como opinión del panel"], ["un_panelista", "Que quede como opinión de un panelista"], ["sin_opinion", "No tengo opinión"]] }
    },
    {
      id: "Q2", titulo: "Medición de 25(OH)D", ancla: "41-bloque-transversal-diagnostico-esquemas-y-adulto-mayor",
      html:
        "<p>El informe diría: <strong>«El panel considera que no tiene sentido medir 25(OH)D de rutina en población general y que la medición " +
        "se justifica cuando el resultado vaya a cambiar una decisión diagnóstica o terapéutica»</strong>. La opinión de medir para tratar " +
        "hasta una meta quedaría registrada como posición minoritaria.</p>"
    },
    {
      id: "Q3", titulo: "Esquemas", ancla: "41-bloque-transversal-diagnostico-esquemas-y-adulto-mayor",
      html:
        "<p>El informe diría que, para el panel, <strong>la elección entre esquema diario y semanal depende de la indicación, la adherencia y la " +
        "polifarmacia, y que la prevención de la mortalidad por cáncer o de las infecciones no es una razón para formular vitamina D</strong>.</p>",
      extra: { id: "Q3_carga", txt: "En la sala se habló de una dosis de carga en la deficiencia franca o antes de un antirresortivo. En su opinión, esa carga…",
               ops: [["puede_bolo", "Puede ser de 100.000 UI o más"], ["por_debajo", "Debe quedar por debajo de 100.000 UI"], ["sin_opinion", "No tengo opinión"]] }
    },
    {
      id: "Q4", titulo: "Enfermedad autoinmune", ancla: "45-inmunidad-y-autoinmunidad",
      html:
        "<p>El tema quedó en ámbar: 5 de 7 estuvieron de acuerdo, uno lo ve en verde y otro en rojo. Proponemos <strong>reportarlo en ámbar " +
        "como punto abierto, con las dos posiciones</strong>.</p>"
    }
  ];
  var DRIVERS = [["a", "(a) En la práctica no impulsa la formulación"], ["b", "(b) La impulsa, pero no debería"], ["na", "Yo la validé como driver"]];

  // ------------------------------------------------------------------ utilidades
  function el(tag, attrs, html) {
    var e = document.createElement(tag);
    for (var k in (attrs || {})) e.setAttribute(k, attrs[k]);
    if (html != null) e.innerHTML = html;
    return e;
  }
  function radios(name, ops) {
    var f = el("div", { "class": "enc-ops enc-ops-lista", role: "radiogroup" });
    ops.forEach(function (o) {
      var id = name + "_" + o[0].replace(/[^a-z0-9]/gi, "x");
      var l = el("label", { "for": id });
      l.appendChild(el("input", { type: "radio", name: name, id: id, value: o[0] }));
      l.appendChild(el("span", null, o[1]));
      f.appendChild(l);
    });
    return f;
  }
  function grupo(id, legend, ops) {
    var g = el("fieldset", { "data-req": id });
    g.appendChild(el("legend", null, legend));
    g.appendChild(radios(id, ops));
    return g;
  }
  function comentario(name, txt) {
    var c = el("label", { "class": "enc-com", "data-com": name }, txt);
    c.appendChild(el("textarea", { name: name, rows: "3", maxlength: "3000" }));
    return c;
  }
  function valor(name) {
    var x = raiz.querySelector("input[type=radio][name='" + name + "']:checked");
    if (x) return x.value;
    var y = raiz.querySelector("[name='" + name + "']:not([type=radio])");
    if (!y) return "";
    return y.type === "checkbox" ? (y.checked ? "si" : "no") : y.value.trim();
  }
  function guardarBorrador() {
    try {
      var d = {};
      raiz.querySelectorAll("input,textarea,select").forEach(function (x) {
        if (x.name === "sitio_web") return;
        if (x.type === "radio") { if (x.checked) d[x.name] = x.value; }
        else d[x.name] = x.value;
      });
      localStorage.setItem(CLAVE_BORRADOR, JSON.stringify(d));
    } catch (e) { /* sin almacenamiento */ }
  }
  function cargarBorrador() {
    try {
      var d = JSON.parse(localStorage.getItem(CLAVE_BORRADOR) || "null");
      if (!d) return;
      Object.keys(d).forEach(function (k) {
        raiz.querySelectorAll("[name='" + k + "']").forEach(function (x) {
          if (x.type === "radio") x.checked = (x.value === d[k]); else x.value = d[k];
        });
      });
    } catch (e) { /* nada */ }
  }

  // ------------------------------------------------------------------ construcción
  if (!ENDPOINT) {
    raiz.appendChild(el("div", { "class": "enc-aviso" },
      "<strong>Modo de prueba.</strong> Este formulario todavía no está conectado: puede recorrerlo, pero sus respuestas no se enviarán."));
  }

  var reg = el("section", { "class": "enc-bloque" });
  reg.appendChild(el("h2", null, "Quién responde"));
  var sel = el("label", { "class": "enc-com", "data-req-sel": "1" }, "Su nombre");
  var s = el("select", { name: "panelista" });
  s.appendChild(el("option", { value: "" }, "Seleccione…"));
  PANEL.forEach(function (n) { s.appendChild(el("option", { value: n }, n)); });
  sel.appendChild(s);
  reg.appendChild(sel);
  reg.appendChild(el("label", { "class": "enc-trampa", "aria-hidden": "true" }, "Sitio web<input type='text' name='sitio_web' tabindex='-1' autocomplete='off'>"));
  raiz.appendChild(reg);

  PREGUNTAS.forEach(function (q, n) {
    var sec = el("section", { "class": "enc-ficha", id: "pregunta-" + (n + 1) });
    sec.appendChild(el("span", { "class": "enc-num" }, "Pregunta " + (n + 1) + " de 6"));
    sec.appendChild(el("h3", null, q.titulo));
    sec.appendChild(el("div", { "class": "enc-texto" }, q.html +
      "<p class='enc-nota'>Contexto en el <a href='../informe/'>borrador del informe</a>.</p>"));
    sec.appendChild(grupo(q.id, "¿Esto refleja su opinión?", REFLEJA));
    sec.appendChild(comentario("C_" + q.id, "Si propone cambios o no refleja su opinión, díganos cómo lo diría (obligatorio en esos casos)"));
    if (q.extra) sec.appendChild(grupo(q.extra.id, q.extra.txt, q.extra.ops));
    raiz.appendChild(sec);
  });

  var q5 = el("section", { "class": "enc-ficha", id: "pregunta-5" });
  q5.appendChild(el("span", { "class": "enc-num" }, "Pregunta 5 de 6"));
  q5.appendChild(el("h3", null, "Drivers de la formulación"));
  q5.appendChild(el("div", { "class": "enc-texto" },
    "<p>Sobre la medición rutinaria como driver de la formulación, el panel quedó dividido: 3 la validaron y 3 no.</p>" +
    "<p class='enc-nota'>Contexto en el <a href='../informe/'>borrador del informe</a>.</p>"));
  q5.appendChild(grupo("Q5", "Si usted no la validó, ¿qué quiso decir?", DRIVERS));
  raiz.appendChild(q5);

  var q6 = el("section", { "class": "enc-ficha", id: "pregunta-6" });
  q6.appendChild(el("span", { "class": "enc-num" }, "Pregunta 6 de 6"));
  q6.appendChild(el("h3", null, "Conflictos de interés"));
  q6.appendChild(el("div", { "class": "enc-texto" },
    "<p>Esta respuesta solo la ve el equipo coordinador y se incorporará a la sección de conflictos de interés del informe final.</p>"));
  q6.appendChild(grupo("Q6", "En los últimos 36 meses, ¿ha tenido alguna relación con empresas que fabrican o comercializan vitamina D u otros suplementos (honorarios como conferencista o asesor, juntas consultivas, financiación de investigación, apoyo para viajes o congresos, acciones o participación en la propiedad)?",
    [["ninguna", "Ninguna"], ["si", "Sí"]]));
  q6.appendChild(comentario("C_Q6", "Si respondió sí: empresa y tipo de relación (obligatorio en ese caso)"));
  raiz.appendChild(q6);

  var fin = el("section", { "class": "enc-bloque", id: "enc-envio" });
  fin.appendChild(el("h2", null, "Para terminar"));
  fin.appendChild(comentario("C_general", "Comentarios sobre cualquier otra parte del borrador (opcional)"));
  var est = el("p", { "class": "enc-estado", "aria-live": "polite" });
  var btn = el("button", { type: "button", "class": "hero-contact enc-enviar" }, "Enviar respuestas");
  fin.appendChild(btn);
  fin.appendChild(est);
  raiz.appendChild(fin);

  cargarBorrador();
  raiz.addEventListener("change", guardarBorrador);
  raiz.addEventListener("input", guardarBorrador);

  // ------------------------------------------------------------------ validación y envío
  var OBLIG = ["Q1", "Q1_techo", "Q2", "Q3", "Q3_carga", "Q4", "Q5", "Q6"];
  function validar() {
    raiz.querySelectorAll(".enc-falta").forEach(function (x) { x.classList.remove("enc-falta"); });
    var faltas = [];
    if (!valor("panelista")) faltas.push(raiz.querySelector("[data-req-sel]"));
    OBLIG.forEach(function (id) { if (!valor(id)) faltas.push(raiz.querySelector("[data-req='" + id + "']")); });
    ["Q1", "Q2", "Q3", "Q4"].forEach(function (id) {
      var v = valor(id);
      if ((v === "cambios" || v === "no_refleja") && !valor("C_" + id)) faltas.push(raiz.querySelector("[data-com='C_" + id + "']"));
    });
    if (valor("Q6") === "si" && !valor("C_Q6")) faltas.push(raiz.querySelector("[data-com='C_Q6']"));
    faltas.forEach(function (x) { x.classList.add("enc-falta"); });
    return faltas;
  }
  function uuid() {
    try { return crypto.randomUUID(); } catch (e) { return "id-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 10); }
  }

  btn.addEventListener("click", function () {
    var faltas = validar();
    if (faltas.length) {
      est.textContent = "Faltan " + faltas.length + " respuestas, marcadas en rojo.";
      faltas[0].scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    var resp = {};
    OBLIG.forEach(function (id) { resp[id] = valor(id); });
    ["C_Q1", "C_Q2", "C_Q3", "C_Q4", "C_Q6", "C_general"].forEach(function (id) { resp[id] = valor(id); });
    var datos = { version: VERSION, id: uuid(), trampa: valor("sitio_web"), panelista: valor("panelista"), respuestas: resp };
    if (!ENDPOINT) {
      est.textContent = "Modo de prueba: todo está completo, pero no se envió nada.";
      try { console.log("Validación (modo de prueba):", datos); } catch (e) { }
      return;
    }
    btn.disabled = true;
    est.textContent = "Enviando…";
    fetch(ENDPOINT, { method: "POST", headers: { "Content-Type": "text/plain;charset=utf-8" }, body: JSON.stringify(datos) })
      .then(function (r) { return r.json(); })
      .then(function (j) {
        if (!j || !j.ok) throw new Error((j && j.error) || "respuesta inesperada");
        try { localStorage.removeItem(CLAVE_BORRADOR); } catch (e) { }
        raiz.innerHTML = "<div class='enc-gracias'><h2>Gracias</h2><p>Recibimos sus respuestas. Con ellas cerramos el informe final que se entregará a la ACE y a su aliado estratégico.</p></div>";
        window.scrollTo({ top: raiz.offsetTop - 80, behavior: "smooth" });
      })
      .catch(function () {
        btn.disabled = false;
        est.innerHTML = "No pudimos enviar sus respuestas. Siguen guardadas en este navegador; intente de nuevo en un momento o escríbanos a <a href='mailto:cbuiles@festinalente.cc'>cbuiles@festinalente.cc</a>.";
      });
  });
})();
