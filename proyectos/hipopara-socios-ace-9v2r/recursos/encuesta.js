/* Encuesta a los socios de la ACE: declaración de posición sobre hipoparatiroidismo crónico.
 * Renderiza las fichas y las preguntas dentro de #enc-raiz y envía las respuestas a un
 * Google Apps Script (data-endpoint). Sin endpoint, funciona en modo de prueba.
 * El contenido de las fichas está en FICHAS; los nombres de campo son estables para el análisis.
 */
(function () {
  "use strict";
  var raiz = document.getElementById("enc-raiz");
  if (!raiz) return;
  var ENDPOINT = (raiz.getAttribute("data-endpoint") || "").trim();
  var VERSION = raiz.getAttribute("data-version") || "sin-version";
  var CLAVE_BORRADOR = "enc-hipopara-ace-" + VERSION;

  var ESCALA = [
    ["1", "Totalmente en desacuerdo"], ["2", "En desacuerdo"], ["3", "Ni de acuerdo ni en desacuerdo"],
    ["4", "De acuerdo"], ["5", "Totalmente de acuerdo"], ["NO", "No puedo opinar"]
  ];
  var PREGUNTA = "¿Está de acuerdo con este enunciado para la atención de adultos con hipoparatiroidismo crónico en Colombia?";

  // ------------------------------------------------------------------ contenido
  var FICHAS = [
    {
      id: "F1", titulo: "Quién debe evaluarse para reemplazo con PTH",
      html:
        "<p>Debe evaluarse para reemplazo con PTH el adulto con hipoparatiroidismo crónico que cumple <strong>las tres condiciones</strong>:</p>" +
        "<ol><li>El tratamiento convencional se revisó y, cuando hizo falta, se optimizó (ficha 5), y se atendieron las causas potencialmente corregibles.</li>" +
        "<li>Cada alteración usada para decidir se confirmó en al menos dos evaluaciones, salvo un hallazgo estructural como una nefrocalcinosis nueva.</li>" +
        "<li>Persiste control inadecuado en <strong>dos o más dominios</strong> (ficha 3), aun con el calcio sérico en la meta, <strong>o en un dominio</strong> cuando el tratamiento convencional está limitado por intolerancia persistente a dosis altas de calcio y calcitriol o por malabsorción comprobada (ficha 4).</li></ol>" +
        "<p>Cumplir estas condiciones significa que el paciente debe evaluarse para reemplazo con PTH. La decisión de tratar se comparte con el paciente y tiene en cuenta la formulación, la capacidad de seguimiento y el acceso.</p>" +
        "<p class='enc-nota'>Hipoparatiroidismo crónico: después de una cirugía de cuello, el que persiste más de 12 meses. Los criterios aplican a las formulaciones de PTH con evidencia de ensayos clínicos en hipoparatiroidismo crónico y describen lo clínicamente apropiado, con independencia del costo o la disponibilidad.</p>",
      items: [{ id: "F1", texto: null }]
    },
    {
      id: "F2", titulo: "Control inadecuado y limitaciones del tratamiento son conceptos distintos",
      html:
        "<ul><li>El <strong>control inadecuado</strong> se define solo por los dominios de la ficha 3: lo que ocurre con el calcio, el fósforo, la calciuria, los riñones y la necesidad de atención urgente pese al tratamiento optimizado.</li>" +
        "<li>Las <strong>limitaciones del tratamiento</strong> explican por qué el tratamiento convencional no puede darse como se necesita: intolerancia persistente a dosis altas de calcio y calcitriol, y malabsorción comprobada (ficha 4). No cuentan como dominios, pero bajan el umbral para evaluar cuando hay control inadecuado.</li>" +
        "<li>Una limitación sola, en un paciente bien controlado y sin complicaciones, <strong>no</strong> es indicación de reemplazo con PTH.</li>" +
        "<li>Un requerimiento de dosis alta no es un dominio ni una limitación: es una señal para revisar el tratamiento (ficha 6).</li></ul>",
      items: [{ id: "F2", texto: null }]
    },
    {
      id: "F3", titulo: "Dominios de control inadecuado y cómo medirlos",
      html:
        "<p>Califique cada dominio por separado. Los dominios que comparten un proceso (por ejemplo, hipercalciuria y nefrocalcinosis) cuentan por separado; su coexistencia suele reflejar una enfermedad más grave.</p>",
      items: [
        { id: "F3_hipocalcemia", texto: "<strong>Hipocalcemia.</strong> Calcio total corregido por albúmina menor de 8,0 mg/dL, o calcio iónico por debajo del límite inferior del laboratorio, con o sin síntomas. Se prefiere el calcio iónico con albúmina baja, TFGe menor de 60 mL/min/1,73 m², trastornos ácido-base o embarazo." },
        { id: "F3_fluctuacion", texto: "<strong>Calcemia fluctuante.</strong> Tres o más intensificaciones del tratamiento (aumentos de dosis por hipocalcemia) en 12 meses, después de verificar la adherencia y otras condiciones modificables." },
        { id: "F3_hiperfosfatemia", texto: "<strong>Hiperfosfatemia.</strong> Fósforo sérico por encima del límite superior del laboratorio, confirmado en una muestra adecuada (en ayunas, no hemolizada, sin torniquete prolongado), con un producto calcio × fósforo mayor de 55 mg²/dL²." },
        { id: "F3_hipercalciuria", texto: "<strong>Hipercalciuria.</strong> Más de 300 mg/24 h en hombres o de 250 mg/24 h en mujeres, después de descartar exceso de calcio o sodio en la dieta y sobretratamiento." },
        { id: "F3_renal", texto: "<strong>Deterioro de la función renal.</strong> Descenso de la TFGe mayor de 5 mL/min/1,73 m² por año, no explicado por otras causas, estimado con al menos tres valores en al menos 12 meses. La diabetes, la hipertensión o la edad no lo excluyen si el descenso es más rápido de lo que explican o se acompaña de hipercalciuria o de un producto calcio × fósforo alto." },
        { id: "F3_litiasis", texto: "<strong>Nefrolitiasis o nefrocalcinosis</strong> nueva o en progresión después del diagnóstico de hipoparatiroidismo. Se recomienda una ecografía renal basal cuando el hipoparatiroidismo se vuelve crónico." },
        { id: "F3_urgencias", texto: "<strong>Atención urgente u hospitalización.</strong> Dos o más episodios relacionados con el hipoparatiroidismo en 12 meses, ya establecido como crónico, sin un desencadenante identificable o corregible, como una enfermedad intercurrente o una interrupción en la dispensación de los medicamentos." }
      ]
    },
    {
      id: "F4", titulo: "Limitaciones del tratamiento convencional",
      html: "<p>Una limitación apoya la evaluación para reemplazo con PTH <strong>solo cuando persiste al menos un dominio</strong> de control inadecuado. Califique cada definición.</p>",
      items: [
        { id: "F4_intolerancia", texto: "<strong>Intolerancia persistente.</strong> Efectos adversos no metabólicos, sobre todo gastrointestinales, atribuibles a las dosis altas de calcio y calcitriol necesarias para el control, que impiden alcanzarlas o mantenerlas. Solo después de optimizar: cambio de sal de calcio (carbonato a citrato), dosis fraccionadas, toma con las comidas y ajuste del calcio de la dieta. La hipercalcemia y la hipercalciuria son dominios, no intolerancia." },
        { id: "F4_malabsorcion", texto: "<strong>Malabsorción comprobada.</strong> Una causa estructural o enteropática demostrada (bypass gástrico o derivación biliopancreática, pancreatoduodenectomía, resección intestinal, enfermedad celíaca confirmada, insuficiencia pancreática exocrina o enfermedad inflamatoria intestinal activa) con evidencia funcional concordante: calcio sérico y urinario persistentemente bajos pese a dosis altas con adherencia verificada, o necesidad recurrente de calcio intravenoso. La cirugía digestiva sola no basta." }
      ]
    },
    {
      id: "F5", titulo: "Optimizar antes de decidir",
      html:
        "<p>Lista de verificación del tratamiento convencional optimizado (punto de buena práctica):</p><ol>" +
        "<li>Calcio corregido por albúmina en una meta de 8,0 a 8,5 mg/dL, o calcio iónico en la parte baja del rango de referencia, medido siempre con el mismo método.</li>" +
        "<li>Magnesio sérico en el rango de referencia.</li>" +
        "<li>25-hidroxivitamina D de 30 ng/mL o más.</li>" +
        "<li>Calcio de la dieta de 1000 a 1200 mg/día, para no usar suplementos para reemplazar una ingesta baja.</li>" +
        "<li>Fósforo sérico en el rango de referencia y producto calcio × fósforo de 55 mg²/dL² o menos, con el calcio tomado con las comidas como quelante y moderación del fósforo de la dieta, sobre todo el inorgánico de los aditivos.</li>" +
        "<li>Calciuria por debajo de los umbrales de la ficha 3, con restricción de sodio (sal menor de 6 g/día) y tiazida cuando haga falta (por ejemplo, hidroclorotiazida 25 mg cada 12 horas), vigilando hiponatremia, hipopotasemia, hipomagnesemia e hipotensión, y con cautela en insuficiencia suprarrenal e hipocalcemia autosómica dominante.</li>" +
        "<li>Sal de calcio y horario adecuados: citrato con inhibidores de bomba de protones o aclorhidria; 500 mg o menos de calcio elemental por toma, porque la absorción es saturable; calcitriol en dosis fraccionadas.</li>" +
        "<li>Adherencia verificada y revisión de medicamentos y condiciones que interfieren, incluidos los niveles elevados de hormonas tiroideas por sobretratamiento con levotiroxina, que reducen la absorción intestinal de calcio; la dosis de levotiroxina debe ajustarse a la meta de cada paciente.</li>" +
        "<li>Calcio, fósforo, magnesio y creatinina séricos, y calciuria de 24 horas, después de cada cambio de dosis y en cada evaluación.</li></ol>",
      items: [{ id: "F5", texto: null }]
    },
    {
      id: "F6", titulo: "Requerimiento de dosis alta",
      html:
        "<p>Un requerimiento de <strong>calcio elemental mayor de 3 g/día</strong> con cualquier dosis de calcitriol, o de <strong>calcitriol mayor de 2 µg/día</strong> con cualquier dosis de calcio, debe llevar a una revisión completa del tratamiento convencional (ficha 5) y a buscar malabsorción. Por sí solo, en un paciente sin ningún dominio de control inadecuado, no es indicación de reemplazo con PTH.</p>" +
        "<p class='enc-nota'>Estos umbrales son más estrictos que los de las guías internacionales (calcio elemental mayor de 2 a 2,5 g/día; vitamina D activa mayor de 1,5 a 2 µg/día). No se exige una dosis mínima de calcitriol para el umbral de calcio, aunque mantener calcio sin vitamina D activa no es apropiado en el hipoparatiroidismo crónico.</p>",
      items: [{ id: "F6", texto: null }]
    },
    {
      id: "F7", titulo: "Lo que no basta por sí solo",
      html:
        "<p>No son suficientes por sí solos para evaluar el reemplazo con PTH:</p><ul>" +
        "<li>Un solo dominio de control inadecuado sin una limitación del tratamiento.</li>" +
        "<li>Un evento grave único, como una convulsión o un laringoespasmo, que requiere manejo urgente y reoptimización del tratamiento.</li>" +
        "<li>Una limitación del tratamiento, o un requerimiento de dosis alta, en un paciente sin ningún dominio de control inadecuado.</li>" +
        "<li>Los síntomas persistentes, la afectación de la calidad de vida o las dificultades de adherencia, en los que el panel no alcanzó acuerdo. Deben motivar una revisión cuidadosa del plan de tratamiento.</li></ul>",
      items: [{ id: "F7", texto: null }]
    },
    {
      id: "F8", titulo: "La ruta clínica en seis pasos",
      html:
        "<ol><li><strong>Confirmar el diagnóstico y la cronicidad</strong> (más de 12 meses tras la cirugía en los casos posquirúrgicos) y que el paciente recibe calcio oral y vitamina D activa.</li>" +
        "<li><strong>Optimizar el tratamiento y buscar causas corregibles</strong> (ficha 5), en ambas direcciones: corregir el subtratamiento (hipocalcemia sintomática o recurrente) y el sobretratamiento (calcio por encima de la meta, hipercalciuria, hiperfosfatemia).</li>" +
        "<li><strong>Evaluar los dominios</strong> de control inadecuado con las definiciones de la ficha 3, con el mismo método de laboratorio durante el seguimiento.</li>" +
        "<li><strong>Confirmar la persistencia</strong> en al menos dos evaluaciones con tratamiento optimizado.</li>" +
        "<li><strong>Buscar limitaciones del tratamiento</strong>: intolerancia persistente o malabsorción comprobada (ficha 4).</li>" +
        "<li><strong>Decidir</strong>: evaluar para reemplazo con PTH con dos o más dominios persistentes, o con uno más una limitación. Si no, continuar el tratamiento optimizado y reevaluar en cada visita.</li></ol>",
      items: [{ id: "F8", texto: null }]
    }
  ];

  var PRUEBAS = [
    ["X_ionico", "Calcio iónico"], ["X_magnesio", "Magnesio sérico"], ["X_25ohd", "25-hidroxivitamina D"],
    ["X_calciuria", "Calciuria de 24 horas"], ["X_tfge", "Creatinina con TFGe seriada"], ["X_eco", "Ecografía renal"]
  ];
  var FACTIBLE = [["si", "Sí, habitualmente"], ["dificil", "Con dificultad o demora"], ["no", "No"]];

  var PERFIL = [
    { id: "P_especialidad", txt: "Especialidad", ops: [["endo_adultos", "Endocrinología de adultos"], ["endo_pediatrica", "Endocrinología pediátrica"], ["residente", "Residente de endocrinología"]] },
    { id: "P_anios", txt: "Años de ejercicio como especialista", ops: [["residente", "No aplica: soy residente"], ["<5", "Menos de 5"], ["5-9", "5 a 9"], ["10-19", "10 a 19"], [">=20", "20 o más"]] },
    { id: "P_ambito", txt: "Ámbito principal de práctica", ops: [["publico", "Público"], ["privado", "Privado"], ["mixto", "Mixto"], ["academico", "Principalmente académico"]] },
    { id: "P_capitulo", txt: "Capítulo de la ACE al que pertenece", ops: [["bolivar_grande", "Bolívar Grande"], ["caribe", "Caribe"], ["central", "Central"], ["eje_cafetero", "Eje Cafetero"], ["noroccidente", "Noroccidente"], ["nororiente", "Nororiente"], ["suroccidente", "Suroccidente"]] },
    { id: "P_pacientes", txt: "Adultos con hipoparatiroidismo crónico que atendió en el último año", ops: [["0", "Ninguno"], ["1-5", "1 a 5"], ["6-20", "6 a 20"], [">20", "Más de 20"]] },
    { id: "P_coi", txt: "En los últimos 36 meses, ¿ha tenido relaciones financieras (asesorías, conferencias, investigación) con alguna compañía que comercialice terapias con PTH?", ops: [["no", "No"], ["si", "Sí"], ["nr", "Prefiero no responder"]] }
  ];

  // ------------------------------------------------------------------ utilidades
  function el(tag, attrs, html) {
    var e = document.createElement(tag);
    for (var k in (attrs || {})) e.setAttribute(k, attrs[k]);
    if (html != null) e.innerHTML = html;
    return e;
  }
  function radios(name, ops, clase) {
    var f = el("div", { "class": "enc-ops " + (clase || ""), role: "radiogroup" });
    ops.forEach(function (o) {
      var id = name + "_" + o[0].replace(/[^a-z0-9]/gi, "x");
      var l = el("label", { "for": id });
      var i = el("input", { type: "radio", name: name, id: id, value: o[0] });
      l.appendChild(i);
      l.appendChild(el("span", null, o[1]));
      f.appendChild(l);
    });
    return f;
  }
  function guardarBorrador() {
    try {
      var d = {};
      raiz.querySelectorAll("input,textarea,select").forEach(function (x) {
        if (x.name === "sitio_web") return;
        if (x.type === "radio") { if (x.checked) d[x.name] = x.value; }
        else if (x.type === "checkbox") d[x.name] = x.checked;
        else d[x.name] = x.value;
      });
      localStorage.setItem(CLAVE_BORRADOR, JSON.stringify(d));
    } catch (e) { /* sin almacenamiento: se ignora */ }
  }
  function cargarBorrador() {
    try {
      var d = JSON.parse(localStorage.getItem(CLAVE_BORRADOR) || "null");
      if (!d) return;
      Object.keys(d).forEach(function (k) {
        raiz.querySelectorAll("[name='" + k + "']").forEach(function (x) {
          if (x.type === "radio") x.checked = (x.value === d[k]);
          else if (x.type === "checkbox") x.checked = !!d[k];
          else x.value = d[k];
        });
      });
    } catch (e) { /* nada */ }
  }
  function valor(name) {
    var x = raiz.querySelector("input[type=radio][name='" + name + "']:checked");
    if (x) return x.value;
    var y = raiz.querySelector("[name='" + name + "']:not([type=radio])");
    if (!y) return "";
    return y.type === "checkbox" ? (y.checked ? "si" : "no") : y.value.trim();
  }

  // ------------------------------------------------------------------ construcción
  var itemsVoto = [];
  FICHAS.forEach(function (f) { f.items.forEach(function (i) { itemsVoto.push(i.id); }); });

  if (!ENDPOINT) {
    raiz.appendChild(el("div", { "class": "enc-aviso" },
      "<strong>Modo de prueba.</strong> Esta encuesta todavía no está conectada: puede recorrerla, pero sus respuestas no se enviarán."));
  }

  // Registro
  var reg = el("section", { "class": "enc-bloque", id: "enc-registro" });
  reg.appendChild(el("h2", null, "1. Sus datos"));
  reg.appendChild(el("p", null, "Su nombre y su correo se usan solo para verificar que es socio de la ACE y evitar respuestas duplicadas. Se guardan aparte de sus respuestas, que se analizan con un código y se informan solo de forma agregada."));
  var campos = el("div", { "class": "enc-campos" });
  campos.innerHTML =
    "<label>Nombre completo<input type='text' name='I_nombre' autocomplete='name' required></label>" +
    "<label>Correo electrónico registrado en la ACE<input type='email' name='I_correo' autocomplete='email' required></label>" +
    "<label class='enc-trampa' aria-hidden='true'>Sitio web<input type='text' name='sitio_web' tabindex='-1' autocomplete='off'></label>";
  reg.appendChild(campos);
  PERFIL.forEach(function (p) {
    var g = el("fieldset", { "class": "enc-perfil", "data-req": p.id });
    g.appendChild(el("legend", null, p.txt));
    g.appendChild(radios(p.id, p.ops, "enc-ops-lista"));
    reg.appendChild(g);
  });
  raiz.appendChild(reg);

  // Fichas
  var intro = el("section", { "class": "enc-bloque" });
  intro.appendChild(el("h2", null, "2. Las fichas"));
  intro.appendChild(el("p", null, "Lea cada ficha y responda la pregunta: <em>" + PREGUNTA + "</em> Marque «No puedo opinar» si el tema está fuera de su práctica. El comentario es opcional; si está en desacuerdo, nos ayuda saber por qué."));
  raiz.appendChild(intro);

  FICHAS.forEach(function (f, n) {
    var s = el("section", { "class": "enc-ficha", id: "ficha-" + f.id });
    s.appendChild(el("span", { "class": "enc-num" }, "Ficha " + (n + 1) + " de " + FICHAS.length));
    s.appendChild(el("h3", null, f.titulo));
    s.appendChild(el("div", { "class": "enc-texto" }, f.html));
    f.items.forEach(function (it) {
      var q = el("fieldset", { "class": "enc-voto", "data-req": it.id });
      q.appendChild(el("legend", null, it.texto ? it.texto : PREGUNTA));
      q.appendChild(radios(it.id, ESCALA, "enc-escala"));
      s.appendChild(q);
    });
    if (f.items.length > 1) s.appendChild(el("p", { "class": "enc-nota" }, "En cada definición: " + PREGUNTA.toLowerCase()));
    var c = el("label", { "class": "enc-com" }, "Comentario sobre esta ficha (opcional)");
    c.appendChild(el("textarea", { name: "C_" + f.id, rows: "3", maxlength: "2000" }));
    s.appendChild(c);
    raiz.appendChild(s);
  });

  // Factibilidad
  var fx = el("section", { "class": "enc-bloque" });
  fx.appendChild(el("h2", null, "3. Factibilidad en su entorno"));
  fx.appendChild(el("p", null, "En su práctica, ¿puede obtener estas pruebas cuando las necesita?"));
  PRUEBAS.forEach(function (p) {
    var g = el("fieldset", { "class": "enc-perfil", "data-req": p[0] });
    g.appendChild(el("legend", null, p[1]));
    g.appendChild(radios(p[0], FACTIBLE, "enc-ops-lista"));
    fx.appendChild(g);
  });
  raiz.appendChild(fx);

  // Cierre
  var fin = el("section", { "class": "enc-bloque", id: "enc-envio" });
  fin.appendChild(el("h2", null, "4. Para terminar"));
  var cg = el("label", { "class": "enc-com" }, "¿Falta algo en la declaración, o hay algo que impediría aplicarla en su práctica? (opcional)");
  cg.appendChild(el("textarea", { name: "C_general", rows: "4", maxlength: "4000" }));
  fin.appendChild(cg);
  fin.appendChild(el("label", { "class": "enc-check" },
    "<input type='checkbox' name='I_agradecimientos'> Acepto que mi nombre aparezca en los agradecimientos del artículo como participante de la consulta. Entiendo que esto no implica que respalde la versión final."));
  fin.appendChild(el("label", { "class": "enc-check" },
    "<input type='checkbox' name='I_consentimiento' required> Autorizo el tratamiento de mis datos personales para esta consulta, conforme a la Ley 1581 de 2012. Responsable: Festina Lente, por encargo de la ACE. Finalidad: verificar la condición de socio, evitar duplicados y, si lo autorizo, incluir mi nombre en los agradecimientos. Mis respuestas se analizarán con un código y se informarán solo de forma agregada. Puedo consultar, corregir o pedir la supresión de mis datos escribiendo a cbuiles@festinalente.cc."));
  var est = el("p", { "class": "enc-estado", "aria-live": "polite" });
  var btn = el("button", { type: "button", "class": "hero-contact enc-enviar" }, "Enviar respuestas");
  fin.appendChild(btn);
  fin.appendChild(est);
  raiz.appendChild(fin);

  // Progreso
  var prog = el("div", { "class": "enc-progreso", "aria-live": "polite" });
  document.body.appendChild(prog);
  function actualizarProgreso() {
    var hechas = itemsVoto.filter(function (id) { return !!valor(id); }).length;
    prog.textContent = hechas + " de " + itemsVoto.length + " calificaciones";
    prog.classList.toggle("completo", hechas === itemsVoto.length);
  }

  cargarBorrador();
  actualizarProgreso();
  raiz.addEventListener("change", function () { guardarBorrador(); actualizarProgreso(); });
  raiz.addEventListener("input", guardarBorrador);

  // ------------------------------------------------------------------ validación y envío
  function validar() {
    raiz.querySelectorAll(".enc-falta").forEach(function (x) { x.classList.remove("enc-falta"); });
    var faltas = [];
    var nombre = valor("I_nombre"), correo = valor("I_correo");
    if (nombre.length < 5) faltas.push(raiz.querySelector("[name=I_nombre]").parentNode);
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) faltas.push(raiz.querySelector("[name=I_correo]").parentNode);
    raiz.querySelectorAll("[data-req]").forEach(function (g) {
      if (!valor(g.getAttribute("data-req"))) faltas.push(g);
    });
    if (valor("I_consentimiento") !== "si") faltas.push(raiz.querySelector("[name=I_consentimiento]").parentNode);
    faltas.forEach(function (x) { x.classList.add("enc-falta"); });
    return faltas;
  }

  function uuid() {
    try { return crypto.randomUUID(); } catch (e) {
      return "id-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 10);
    }
  }

  btn.addEventListener("click", function () {
    var faltas = validar();
    if (faltas.length) {
      est.textContent = "Faltan " + faltas.length + " respuestas o datos obligatorios, marcados en rojo.";
      faltas[0].scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    var resp = {};
    itemsVoto.forEach(function (id) { resp[id] = valor(id); });
    FICHAS.forEach(function (f) { resp["C_" + f.id] = valor("C_" + f.id); });
    PERFIL.forEach(function (p) { resp[p.id] = valor(p.id); });
    PRUEBAS.forEach(function (p) { resp[p[0]] = valor(p[0]); });
    resp.C_general = valor("C_general");
    var datos = {
      version: VERSION, id: uuid(), trampa: valor("sitio_web"),
      identidad: { nombre: valor("I_nombre"), correo: valor("I_correo").toLowerCase(),
                   agradecimientos: valor("I_agradecimientos"), consentimiento: valor("I_consentimiento") },
      respuestas: resp
    };
    if (!ENDPOINT) {
      est.textContent = "Modo de prueba: todo está completo, pero no se envió nada.";
      try { console.log("Encuesta (modo de prueba):", datos); } catch (e) { }
      return;
    }
    btn.disabled = true;
    est.textContent = "Enviando…";
    fetch(ENDPOINT, { method: "POST", headers: { "Content-Type": "text/plain;charset=utf-8" }, body: JSON.stringify(datos) })
      .then(function (r) { return r.json(); })
      .then(function (j) {
        if (!j || !j.ok) throw new Error((j && j.error) || "respuesta inesperada");
        try { localStorage.removeItem(CLAVE_BORRADOR); } catch (e) { }
        raiz.innerHTML = "<div class='enc-gracias'><h2>Gracias</h2><p>Recibimos sus respuestas. Los resultados agregados se informarán en la versión final de la declaración.</p></div>";
        prog.remove();
        window.scrollTo({ top: raiz.offsetTop - 80, behavior: "smooth" });
      })
      .catch(function () {
        btn.disabled = false;
        est.innerHTML = "No pudimos enviar sus respuestas. Sus datos siguen guardados en este navegador; intente de nuevo en un momento o escríbanos a <a href='mailto:cbuiles@festinalente.cc'>cbuiles@festinalente.cc</a>.";
      });
  });
})();
