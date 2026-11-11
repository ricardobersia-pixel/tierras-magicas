// Sales de la Cordillera: catálogo, recetas, guía y taller de producción. Todo funciona sin conexión.
import { SALES, COMPUESTOS, GUIA, ETIQUETAS_POR_HOJA } from "./datos.js";
import {
  buscarSal, controlFormula, planCompra, envasado, costos, rendimiento, codigoLote, siguienteNumero, sumarMeses,
  stock, faltantes, consumosDeLote, listaIngredientes, pctSal, csv, formatoGramos, r1,
} from "./calculos.js";

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const pesos = (n) => `$ ${Math.round(n).toLocaleString("es-AR")}`;
const fechaAR = (iso) => (iso ? iso.split("-").reverse().join("/") : "—");
const hoyISO = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};
const INGREDIENTES = [...new Set(SALES.flatMap((s) => s.formula.map((f) => f.ingrediente)))].sort((a, b) => a.localeCompare(b, "es"));

// ---------- Estado guardado en el teléfono ----------
const CLAVE = "sales-tm-v1";
const INICIAL = {
  plan: { "TM-01": 5000, "TM-02": 5000, "TM-03": 5000, "TM-04": 5000 }, // planilla "Compra y Producción 20 kg"
  margen: 5,
  neto: null, // gramos por frasco: a definir por el dueño
  envase: null,
  ganancia: null,
  precios: {},
  lotes: [],
  movs: [],
  rotulo: { razon: "", domicilio: "", rne: "", rnpa: "" },
  vistaTaller: "plan",
};
let estado = cargar();
function cargar() {
  try {
    const g = JSON.parse(localStorage.getItem(CLAVE));
    return g ? { ...structuredClone(INICIAL), ...g, rotulo: { ...INICIAL.rotulo, ...(g.rotulo || {}) } } : structuredClone(INICIAL);
  } catch {
    return structuredClone(INICIAL);
  }
}
function guardar() {
  try {
    localStorage.setItem(CLAVE, JSON.stringify(estado));
  } catch {
    avisar("No se pudo guardar en el teléfono");
  }
}
let timerAviso;
function avisar(t) {
  const a = $("#aviso");
  a.textContent = t;
  a.hidden = false;
  clearTimeout(timerAviso);
  timerAviso = setTimeout(() => (a.hidden = true), 2600);
}

// ---------- Navegación ----------
function ir(ruta) {
  const [vista, param] = ruta.split("/");
  const v = ["sales", "recetas", "guia", "taller", "sal"].includes(vista) ? vista : "sales";
  $$(".vista").forEach((s) => (s.hidden = true));
  if (v === "sal") {
    renderFicha(param);
    $("#vista-ficha").hidden = false;
  } else {
    $(`#vista-${v}`).hidden = false;
  }
  $$(".pestanas button").forEach((b) => b.toggleAttribute("aria-current", b.dataset.ir === (v === "sal" ? "sales" : v)));
  if (v === "taller") renderTaller();
  window.scrollTo(0, 0);
}
$$(".pestanas button").forEach((b) => b.addEventListener("click", () => (location.hash = b.dataset.ir)));
window.addEventListener("hashchange", () => ir(location.hash.slice(1)));

// ---------- Sales ----------
function renderSales() {
  $("#lista-sales").innerHTML = SALES.map(
    (s) => `<button class="tarjeta-sal" style="--sal:${s.color}" data-sal="${s.codigo}">
      <img src="${s.imagen}" alt="Etiqueta ${esc(s.nombre)}" loading="lazy"><span>${esc(s.descripcion)}</span></button>`
  ).join("");
  $$("#lista-sales .tarjeta-sal").forEach((b) => b.addEventListener("click", () => (location.hash = `sal/${b.dataset.sal}`)));
}

function renderFicha(codigo) {
  const s = SALES.find((x) => x.codigo === codigo) || SALES[0];
  $("#vista-ficha").innerHTML = `
    <button class="boton secundario chico volver" type="button" onclick="location.hash='sales'">← Volver</button>
    <div class="ficha-cab">
      <img src="${s.imagen}" alt="">
      <div><h2>${esc(s.nombre)}</h2><p>${esc(s.descripcion)}</p><p>${esc(s.ideal)}</p></div>
    </div>
    <h3>Ingredientes</h3>
    <p class="nota">${esc(listaIngredientes(s))}.</p>
    <h3>Fórmula (${s.codigo})</h3>
    <div class="tabla-cont"><table>
      <thead><tr><th>Ingrediente</th><th>Granulometría</th><th class="num">%</th><th class="num">g/kg</th></tr></thead>
      <tbody>${s.formula
        .map((f) => `<tr><td>${esc(f.ingrediente)}${COMPUESTOS.includes(f.ingrediente) ? " *" : ""}</td><td>${esc(f.granulometria)}</td><td class="num">${f.pct}</td><td class="num">${f.pct * 10}</td></tr>`)
        .join("")}</tbody>
    </table></div>
    <p class="nota">* Ingrediente compuesto: falta su ficha para la trazabilidad completa.</p>
    <h3>Recetas con ${esc(s.nombre)}</h3>
    ${s.recetas.map((r) => tarjetaReceta(s, r, false)).join("")}`;
}

// ---------- Recetas ----------
let filtroSal = "";
function tarjetaReceta(s, r, conSal = true) {
  return `<article class="panel receta" style="--sal:${s.color}">
    ${conSal ? `<p class="de-sal">${esc(s.nombre)}</p>` : ""}
    <h3>${esc(r.titulo)}</h3>
    <p class="bajada">${esc(r.bajada)}</p>
    <ol>${r.pasos.map((p) => `<li>${esc(p)}</li>`).join("")}</ol>
    ${r.seguridad ? `<p class="seguridad">⚠️ ${esc(r.seguridad)}</p>` : ""}
  </article>`;
}
const sinTildes = (t) => t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
function renderRecetas() {
  const q = sinTildes($("#buscar-receta").value.trim());
  const html = SALES.filter((s) => !filtroSal || s.codigo === filtroSal)
    .flatMap((s) => s.recetas.filter((r) => !q || sinTildes([r.titulo, r.bajada, ...r.pasos].join(" ")).includes(q)).map((r) => tarjetaReceta(s, r)))
    .join("");
  $("#lista-recetas").innerHTML = html || `<p class="vacio">No hay recetas con esa búsqueda.</p>`;
}
function iniciarRecetas() {
  $("#chips-sal").innerHTML = [`<button type="button" data-f="" aria-pressed="true">Todas</button>`, ...SALES.map((s) => `<button type="button" data-f="${s.codigo}" aria-pressed="false">${esc(s.nombre)}</button>`)].join("");
  $$("#chips-sal button").forEach((b) =>
    b.addEventListener("click", () => {
      filtroSal = b.dataset.f;
      $$("#chips-sal button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      renderRecetas();
    })
  );
  $("#buscar-receta").addEventListener("input", renderRecetas);
  renderRecetas();
}

// ---------- Guía ----------
function renderGuia() {
  $("#guia").innerHTML = GUIA.map((g) => `<div class="guia-item"><strong>${esc(g.titulo)}</strong>${esc(g.texto)}</div>`).join("");
  $("#sodio").innerHTML = `
    ${SALES.map((s) => `<div class="guia-item"><strong>${esc(s.nombre)}</strong>${pctSal(s)}% de base salina</div>`).join("")}
    <p class="nota">La Organización Mundial de la Salud recomienda consumir menos de 5 g de sal por día. Usalas como toque final y con medida.</p>`;
}

// ---------- Taller ----------
function renderTaller() {
  $$("[data-taller]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.taller === estado.vistaTaller)));
  $$("[data-panel]").forEach((p) => (p.hidden = p.dataset.panel !== estado.vistaTaller));
  ({ plan: renderPlan, lotes: renderLotes, stock: renderStock, costos: renderCostos, datos: renderDatos })[estado.vistaTaller]();
}
$$("[data-taller]").forEach((b) =>
  b.addEventListener("click", () => {
    estado.vistaTaller = b.dataset.taller;
    guardar();
    renderTaller();
  })
);

const stockActual = () => stock(estado.movs);
const margen = () => (Number(estado.margen) || 0) / 100;

// Plan
function renderPlan() {
  const e = $("#plan-entradas");
  if (!e.dataset.listo) {
    e.innerHTML = `${SALES.map((s) => `<label>${esc(s.nombre)} (kg)<input type="number" min="0" step="0.1" inputmode="decimal" data-plan="${s.codigo}"></label>`).join("")}
      <label>Margen de compra (%)<input type="number" min="0" max="50" step="0.5" id="plan-margen"></label>
      <label>Neto por frasco (g)<input type="number" min="1" step="1" id="plan-neto" placeholder="a definir"></label>`;
    $$("[data-plan]", e).forEach((i) =>
      i.addEventListener("input", () => {
        estado.plan[i.dataset.plan] = Math.max(0, Number(i.value) || 0) * 1000;
        guardar();
        renderPlanResultado();
      })
    );
    $("#plan-margen").addEventListener("input", (ev) => {
      estado.margen = Number(ev.target.value) || 0;
      guardar();
      renderPlanResultado();
    });
    $("#plan-neto").addEventListener("input", (ev) => {
      estado.neto = Number(ev.target.value) || null;
      guardar();
      renderPlanResultado();
    });
    e.dataset.listo = "1";
  }
  $$("[data-plan]", e).forEach((i) => (i.value = (estado.plan[i.dataset.plan] || 0) / 1000));
  $("#plan-margen").value = estado.margen;
  $("#plan-neto").value = estado.neto || "";
  renderPlanResultado();
}

function renderPlanResultado() {
  const { filas, totales } = planCompra(estado.plan, margen());
  const cods = Object.keys(totales.porSal);
  if (!cods.length) {
    $("#plan-resultado").innerHTML = `<p class="vacio">Cargá los kilos a producir de al menos una sal.</p>`;
    return;
  }
  const st = stockActual();
  const hayStock = estado.movs.length > 0;
  const env = cods.map((c) => ({ c, ...envasado(totales.porSal[c], estado.neto, ETIQUETAS_POR_HOJA) }));
  $("#plan-resultado").innerHTML = `
    <div class="tabla-cont"><table>
      <thead><tr><th>Ingrediente</th>${cods.map((c) => `<th class="num">${c}</th>`).join("")}<th class="num">Total</th><th class="num">Comprar +${estado.margen}%</th>${hayStock ? '<th class="num">Stock</th><th class="num">Falta</th>' : ""}</tr></thead>
      <tbody>${filas
        .map((f) => {
          const falta = Math.max(0, r1(f.compra - (st[f.ingrediente] || 0)));
          return `<tr><td>${esc(f.ingrediente)}</td>${cods.map((c) => `<td class="num">${f.porSal[c] ? formatoGramos(f.porSal[c]) : "—"}</td>`).join("")}
            <td class="num">${formatoGramos(f.total)}</td><td class="num"><strong>${formatoGramos(f.compra)}</strong></td>
            ${hayStock ? `<td class="num">${formatoGramos(st[f.ingrediente] || 0)}</td><td class="num ${falta ? "negativo" : ""}">${falta ? formatoGramos(falta) : "✓"}</td>` : ""}</tr>`;
        })
        .join("")}</tbody>
      <tfoot><tr><td>Total</td>${cods.map((c) => `<td class="num">${formatoGramos(totales.porSal[c])}</td>`).join("")}<td class="num">${formatoGramos(totales.total)}</td><td class="num">${formatoGramos(totales.compra)}</td>${hayStock ? "<td></td><td></td>" : ""}</tr></tfoot>
    </table></div>
    <p class="nota">El margen cubre pérdidas de compra y proceso; no cambia la fórmula. ${hayStock ? "" : "Registrá compras en Stock para ver qué falta comprar."}</p>
    ${
      estado.neto
        ? `<h3>Envasado (${estado.neto} g por frasco)</h3><div class="tabla-cont"><table>
        <thead><tr><th>Sal</th><th class="num">Frascos</th><th class="num">Sobrante</th><th class="num">Hojas de etiquetas</th></tr></thead>
        <tbody>${env.map((x) => `<tr><td>${esc(buscarSal(x.c).nombre)}</td><td class="num">${x.frascos}</td><td class="num">${formatoGramos(x.sobrante)}</td><td class="num">${x.hojas}</td></tr>`).join("")}</tbody>
      </table></div><p class="nota">Hoja A4 de ${ETIQUETAS_POR_HOJA} etiquetas (4 × 6), una variedad por columna: ${ETIQUETAS_POR_HOJA / 4} de cada sal por hoja.</p>`
        : `<p class="nota">Cargá el neto por frasco para calcular frascos y etiquetas.</p>`
    }`;
}

// Lotes
function renderLotes() {
  const f = $("#form-lote");
  if (!f.dataset.listo) {
    $("#lote-sal").innerHTML = SALES.map((s) => `<option value="${s.codigo}">${s.codigo} ${esc(s.nombre)}</option>`).join("");
    f.addEventListener("submit", guardarLote);
    f.dataset.listo = "1";
  }
  f.fecha.value ||= hoyISO();
  f.objetivo.value ||= 5000;
  if (!f.neto.value && estado.neto) f.neto.value = estado.neto;
  const lotes = [...estado.lotes].sort((a, b) => b.fecha.localeCompare(a.fecha) || b.lote.localeCompare(a.lote));
  $("#lista-lotes").innerHTML = lotes.length
    ? lotes
        .map((l) => {
          const rend = rendimiento(l.objetivo, l.real);
          const env = l.neto ? envasado(l.real, l.neto) : null;
          return `<div class="panel item"><div>
            <strong>${esc(l.lote)}</strong> · ${esc(buscarSal(l.codigo).nombre)}
            <p>Elaborado ${fechaAR(l.fecha)} · Vence ${l.vence ? fechaAR(l.vence) : "a definir"}${l.responsable ? ` · ${esc(l.responsable)}` : ""}</p>
            <p>${formatoGramos(l.real)} de ${formatoGramos(l.objetivo)} <span class="etiqueta ${rend >= 95 ? "ok" : "alerta"}">${rend}%</span>${env ? ` · ${env.frascos} frascos de ${l.neto} g` : ""}</p>
            ${l.obs ? `<p>${esc(l.obs)}</p>` : ""}
          </div><div class="botones">
            <button class="boton chico secundario" type="button" data-imprimir="${esc(l.lote)}">Rótulo</button>
            <button class="boton chico peligro" type="button" data-borrar-lote="${esc(l.lote)}" aria-label="Borrar lote ${esc(l.lote)}">✕</button>
          </div></div>`;
        })
        .join("")
    : `<p class="vacio">Todavía no hay lotes.</p>`;
  $$("[data-borrar-lote]").forEach((b) => b.addEventListener("click", () => borrarLote(b.dataset.borrarLote)));
  $$("[data-imprimir]").forEach((b) => b.addEventListener("click", () => imprimirRotulos(b.dataset.imprimir)));
}

function guardarLote(ev) {
  ev.preventDefault();
  const f = ev.target;
  const codigo = f.codigo.value;
  const fecha = f.fecha.value;
  const lote = codigoLote(codigo, fecha, siguienteNumero(estado.lotes, codigo, fecha));
  const vida = Number(f.vida.value) || null;
  const real = Number(f.real.value);
  const l = {
    lote, codigo, fecha, vida,
    vence: vida ? sumarMeses(fecha, vida) : null,
    objetivo: Number(f.objetivo.value),
    real,
    neto: Number(f.neto.value) || null,
    responsable: f.responsable.value.trim(),
    obs: f.obs.value.trim(),
  };
  estado.lotes.push(l);
  // Se descuenta lo que pide la fórmula para el peso objetivo (lo que se pesó y se mezcló)
  if (f.descontar.checked) estado.movs.push(...consumosDeLote(codigo, l.objetivo, lote).map((m) => ({ ...m, fecha })));
  guardar();
  f.real.value = "";
  f.obs.value = "";
  avisar(`Lote ${lote} guardado`);
  renderLotes();
}

function borrarLote(lote) {
  if (!confirm(`¿Borrar el lote ${lote}? También se devuelven al stock sus ingredientes.`)) return;
  estado.lotes = estado.lotes.filter((l) => l.lote !== lote);
  estado.movs = estado.movs.filter((m) => m.ref !== lote);
  guardar();
  renderLotes();
}

// Rótulos de lote para imprimir (complementan la etiqueta artística con los datos que exige el rotulado)
function imprimirRotulos(lote) {
  const l = estado.lotes.find((x) => x.lote === lote);
  const s = buscarSal(l.codigo);
  const r = estado.rotulo;
  const completar = (v, t) => (v ? esc(v) : `<mark>[${t}]</mark>`);
  const cantidad = l.neto ? Math.min(envasado(l.real, l.neto).frascos, 40) || 1 : 20;
  const rotulo = `<div class="rot">
    <b>${esc(s.nombre)}</b> — ${esc(s.descripcion)}<br>
    <small>Ingredientes: ${esc(listaIngredientes(s))}.</small><br>
    Cont. neto: ${l.neto ? `${l.neto} g` : "<mark>[NETO]</mark>"} · Lote: ${esc(l.lote)}<br>
    Elab.: ${fechaAR(l.fecha)} · Venc.: ${l.vence ? fechaAR(l.vence) : "<mark>[VENCIMIENTO]</mark>"}<br>
    <small>Elab. por: ${completar(r.razon, "RAZÓN SOCIAL")}, ${completar(r.domicilio, "DOMICILIO")} · RNE ${completar(r.rne, "RNE")} · RNPA ${completar(r.rnpa, "RNPA")} · Industria Argentina</small>
  </div>`;
  const html = `<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Rótulos ${esc(l.lote)}</title><style>
    @page { size: A4; margin: 8mm; }
    body { font: 7pt/1.25 system-ui, sans-serif; margin: 0; }
    .hoja { display: grid; grid-template-columns: repeat(4, 1fr); gap: 2mm; }
    .rot { border: 0.2mm dashed #999; padding: 1.5mm; height: 26mm; overflow: hidden; }
    mark { background: #ffe08a; }
  </style></head><body><div class="hoja">${rotulo.repeat(cantidad)}</div></body></html>`;
  if (window.Capacitor?.isNativePlatform?.()) {
    descargar(`rotulos-${l.lote}.html`, html, "text/html");
    avisar("Abrí el archivo en Chrome para imprimirlo");
    return;
  }
  const w = window.open("", "_blank");
  if (!w) return avisar("Permití las ventanas emergentes para imprimir");
  w.document.write(html);
  w.document.close();
  w.focus();
  w.print();
}

// Stock
function renderStock() {
  const f = $("#form-mov");
  if (!f.dataset.listo) {
    $("#mov-ing").innerHTML = INGREDIENTES.map((i) => `<option>${esc(i)}</option>`).join("");
    f.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const gramos = Number(f.gramos.value);
      if (!gramos) return;
      estado.movs.push({
        tipo: f.tipo.value, ingrediente: f.ingrediente.value, gramos, fecha: f.fecha.value,
        proveedor: f.proveedor.value.trim(), loteProv: f.loteProv.value.trim(),
      });
      guardar();
      f.gramos.value = "";
      avisar("Movimiento guardado");
      renderStock();
    });
    f.dataset.listo = "1";
  }
  f.fecha.value ||= hoyISO();
  const st = stockActual();
  const falt = Object.fromEntries(faltantes(estado.plan, st, margen()).map((x) => [x.ingrediente, x.comprar]));
  $("#tabla-stock").innerHTML = `<div class="tabla-cont"><table>
    <thead><tr><th>Ingrediente</th><th class="num">Stock</th><th class="num">Falta para el plan</th></tr></thead>
    <tbody>${INGREDIENTES.map((i) => `<tr><td>${esc(i)}</td><td class="num ${(st[i] || 0) < 0 ? "negativo" : ""}">${formatoGramos(st[i] || 0)}</td><td class="num ${falt[i] ? "negativo" : ""}">${falt[i] ? formatoGramos(falt[i]) : "✓"}</td></tr>`).join("")}</tbody>
  </table></div><p class="nota">Stock negativo: se usó más de lo que se registró como compra.</p>`;
  const movs = estado.movs.map((m, i) => ({ ...m, i })).reverse().slice(0, 60);
  $("#lista-movs").innerHTML = movs.length
    ? `<div class="tabla-cont"><table><thead><tr><th>Fecha</th><th>Tipo</th><th>Ingrediente</th><th class="num">g</th><th>Detalle</th><th></th></tr></thead><tbody>${movs
        .map(
          (m) => `<tr><td>${fechaAR(m.fecha)}</td><td>${m.tipo}</td><td>${esc(m.ingrediente)}</td><td class="num">${m.tipo === "consumo" ? "−" : ""}${formatoGramos(m.gramos)}</td>
          <td>${esc(m.ref || [m.proveedor, m.loteProv].filter(Boolean).join(" · "))}</td>
          <td>${m.ref ? "" : `<button class="boton chico peligro" type="button" data-borrar-mov="${m.i}" aria-label="Borrar">✕</button>`}</td></tr>`
        )
        .join("")}</tbody></table></div>`
    : `<p class="vacio">Sin movimientos.</p>`;
  $$("[data-borrar-mov]").forEach((b) =>
    b.addEventListener("click", () => {
      if (!confirm("¿Borrar este movimiento?")) return;
      estado.movs.splice(Number(b.dataset.borrarMov), 1);
      guardar();
      renderStock();
    })
  );
}

// Costos
function renderCostos() {
  const p = $("#precios");
  if (!p.dataset.listo) {
    p.innerHTML = `<div class="controles">${INGREDIENTES.map((i) => `<label>${esc(i)} ($/kg)<input type="number" min="0" step="1" inputmode="decimal" data-precio="${esc(i)}"></label>`).join("")}</div>`;
    $$("[data-precio]", p).forEach((inp) =>
      inp.addEventListener("input", () => {
        if (inp.value === "") delete estado.precios[inp.dataset.precio];
        else estado.precios[inp.dataset.precio] = Number(inp.value);
        guardar();
        renderTablaCostos();
      })
    );
    $("#param-costos").innerHTML = `
      <label>Neto por frasco (g)<input type="number" min="1" step="1" id="c-neto" placeholder="a definir"></label>
      <label>Envase por frasco ($)<input type="number" min="0" step="1" id="c-envase" placeholder="frasco + tapa + etiqueta"></label>
      <label>Ganancia sobre el precio (%)<input type="number" min="0" max="90" step="1" id="c-ganancia"></label>
      <label>Margen de compra (%)<input type="number" min="0" step="0.5" id="c-margen"></label>`;
    const enlazar = (id, campo) =>
      $(id).addEventListener("input", (ev) => {
        estado[campo] = ev.target.value === "" ? null : Number(ev.target.value);
        guardar();
        renderTablaCostos();
      });
    enlazar("#c-neto", "neto");
    enlazar("#c-envase", "envase");
    enlazar("#c-ganancia", "ganancia");
    enlazar("#c-margen", "margen");
    p.dataset.listo = "1";
  }
  $$("[data-precio]", p).forEach((inp) => (inp.value = estado.precios[inp.dataset.precio] ?? ""));
  $("#c-neto").value = estado.neto ?? "";
  $("#c-envase").value = estado.envase ?? "";
  $("#c-ganancia").value = estado.ganancia ?? "";
  $("#c-margen").value = estado.margen ?? "";
  renderTablaCostos();
}
function renderTablaCostos() {
  const filas = SALES.map((s) => ({
    s,
    c: costos(s, estado.precios, { margen: margen(), neto: estado.neto || 0, envase: estado.envase || 0, ganancia: (estado.ganancia || 0) / 100 }),
  }));
  $("#tabla-costos").innerHTML = `<div class="tabla-cont"><table>
    <thead><tr><th>Sal</th><th class="num">Insumos por kg</th>${estado.neto ? '<th class="num">Insumos frasco</th><th class="num">Costo frasco</th><th class="num">Precio sugerido</th>' : ""}<th>Estado</th></tr></thead>
    <tbody>${filas
      .map(
        ({ s, c }) => `<tr><td>${esc(s.nombre)}</td><td class="num">${pesos(c.porKg)}</td>
        ${estado.neto ? `<td class="num">${pesos(c.insumoFrasco)}</td><td class="num">${pesos(c.porFrasco)}</td><td class="num"><strong>${pesos(c.precioSugerido)}</strong></td>` : ""}
        <td>${c.completo ? '<span class="etiqueta ok">completo</span>' : `<span class="etiqueta alerta" title="${esc(c.faltan.join(", "))}">faltan ${c.faltan.length} precios</span>`}</td></tr>`
      )
      .join("")}</tbody></table></div>
    <p class="nota">Costo de insumos con el margen de compra. No incluye mano de obra, energía, habilitación ni impuestos. ${estado.neto ? "" : "Cargá el neto por frasco para ver el costo y el precio por frasco."}</p>`;
}

// Datos
function renderDatos() {
  $("#control-formulas").innerHTML = `<div class="tabla-cont"><table><thead><tr><th>Código</th><th>Producto</th><th class="num">Suma %</th><th>Estado</th></tr></thead><tbody>${SALES.map((s) => {
    const c = controlFormula(s);
    return `<tr><td>${s.codigo}</td><td>${esc(s.nombre)}</td><td class="num">${c.suma}</td><td><span class="etiqueta ${c.cierra ? "ok" : "alerta"}">${c.cierra ? "CIERRA" : "NO CIERRA"}</span></td></tr>`;
  }).join("")}</tbody></table></div>
  <h2>Datos del rótulo</h2>
  <p class="nota">Se imprimen en los rótulos de lote. Mientras estén vacíos, el rótulo los marca para completar.</p>
  <div class="panel controles" id="rotulo">
    <label class="ancho">Razón social<input data-rot="razon"></label>
    <label class="ancho">Domicilio del elaborador<input data-rot="domicilio"></label>
    <label>N° RNE<input data-rot="rne"></label>
    <label>N° RNPA<input data-rot="rnpa"></label>
  </div>`;
  $$("[data-rot]").forEach((i) => {
    i.value = estado.rotulo[i.dataset.rot] || "";
    i.addEventListener("input", () => {
      estado.rotulo[i.dataset.rot] = i.value.trim();
      guardar();
    });
  });
}

async function descargar(nombre, contenido, tipo) {
  const blob = new Blob([contenido], { type: tipo });
  const archivo = new File([blob], nombre, { type: tipo });
  if (navigator.canShare?.({ files: [archivo] })) {
    try {
      await navigator.share({ files: [archivo], title: nombre });
      return;
    } catch (e) {
      if (e.name === "AbortError") return;
    }
  }
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = nombre;
  document.body.append(a);
  a.click();
  setTimeout(() => {
    URL.revokeObjectURL(a.href);
    a.remove();
  }, 1000);
}
const BOM = "﻿"; // para que Excel lea las tildes

$("#csv-plan").addEventListener("click", () => {
  const { filas, totales } = planCompra(estado.plan, margen());
  const cods = Object.keys(totales.porSal);
  const st = stockActual();
  const t = csv([
    ["Ingrediente", ...cods.map((c) => `${c} (g)`), "Total (g)", `Compra +${estado.margen}% (g)`, "Stock (g)", "Falta (g)"],
    ...filas.map((f) => [f.ingrediente, ...cods.map((c) => f.porSal[c] || 0), f.total, f.compra, st[f.ingrediente] || 0, Math.max(0, r1(f.compra - (st[f.ingrediente] || 0)))]),
    ["TOTAL", ...cods.map((c) => totales.porSal[c]), totales.total, totales.compra],
  ]);
  descargar(`plan-compra-${hoyISO()}.csv`, BOM + t, "text/csv");
});
$("#csv-lotes").addEventListener("click", () => {
  const t = csv([
    ["Lote", "Variedad", "Fecha elaboración", "Vencimiento", "Peso objetivo (g)", "Peso real (g)", "Rendimiento %", "Neto frasco (g)", "Responsable", "Observaciones"],
    ...estado.lotes.map((l) => [l.lote, `${l.codigo} ${buscarSal(l.codigo).nombre}`, l.fecha, l.vence || "", l.objetivo, l.real, rendimiento(l.objetivo, l.real), l.neto || "", l.responsable, l.obs]),
  ]);
  descargar(`lotes-${hoyISO()}.csv`, BOM + t, "text/csv");
});
$("#csv-stock").addEventListener("click", () => {
  const st = stockActual();
  const t = csv([
    ["STOCK"], ["Ingrediente", "Stock (g)"], ...INGREDIENTES.map((i) => [i, st[i] || 0]), [],
    ["MOVIMIENTOS"], ["Fecha", "Tipo", "Ingrediente", "Gramos", "Lote producido", "Proveedor", "Lote/venc. proveedor"],
    ...estado.movs.map((m) => [m.fecha, m.tipo, m.ingrediente, m.tipo === "consumo" ? -m.gramos : m.gramos, m.ref || "", m.proveedor || "", m.loteProv || ""]),
  ]);
  descargar(`stock-${hoyISO()}.csv`, BOM + t, "text/csv");
});
$("#respaldo").addEventListener("click", () => descargar(`sales-tm-copia-${hoyISO()}.json`, JSON.stringify({ app: "sales-tm", version: 1, estado }, null, 1), "application/json"));
$("#restaurar").addEventListener("change", async (ev) => {
  const f = ev.target.files[0];
  if (!f) return;
  try {
    const d = JSON.parse(await f.text());
    if (d.app !== "sales-tm" || !d.estado) throw new Error();
    if (!confirm("Esto reemplaza los datos del taller de este teléfono. ¿Seguir?")) return;
    estado = { ...structuredClone(INICIAL), ...d.estado };
    guardar();
    avisar("Copia restaurada");
    renderTaller();
  } catch {
    avisar("El archivo no es una copia válida");
  } finally {
    ev.target.value = "";
  }
});

// ---------- Inicio ----------
renderSales();
iniciarRecetas();
renderGuia();
// Enlace desde el QR de la etiqueta: ?sal=TM-01 abre la ficha de esa sal
const salQR = new URLSearchParams(location.search).get("sal");
if (salQR && SALES.some((s) => s.codigo === salQR.toUpperCase()) && !location.hash) location.hash = `sal/${salQR.toUpperCase()}`;
ir(location.hash.slice(1));

if ("serviceWorker" in navigator && location.protocol === "https:") navigator.serviceWorker.register("sw.js").catch(() => {});
let pedidoInstalar;
window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  pedidoInstalar = e;
  $("#btn-instalar").hidden = false;
});
$("#btn-instalar").addEventListener("click", async () => {
  if (!pedidoInstalar) return;
  pedidoInstalar.prompt();
  await pedidoInstalar.userChoice;
  pedidoInstalar = null;
  $("#btn-instalar").hidden = true;
});
