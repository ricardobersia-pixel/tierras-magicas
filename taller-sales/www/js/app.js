// TM Sales: producción artesanal de las Sales Tierras Mágicas. Uso interno; funciona sin conexión.
// Las fórmulas no vienen en el código: se cargan desde un archivo privado y quedan solo en el teléfono.
import { VARIEDADES, ETIQUETAS_POR_HOJA } from "./datos.js";
import {
  validarFormulas, buscarSal, controlFormula, ingredientes, planCompra, envasado, costos, rendimiento, codigoLote, siguienteNumero,
  stock, faltantes, consumosDeLote, listaIngredientes, csv, formatoGramos, r1,
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
const nombre = (codigo) => VARIEDADES.find((v) => v.codigo === codigo)?.nombre || codigo;

// ---------- Estado guardado en el teléfono ----------
const CLAVE = "taller-tm-v1";
const INICIAL = {
  formulas: [], // se cargan desde el archivo privado
  plan: { "TM-01": 5000, "TM-02": 5000, "TM-03": 5000, "TM-04": 5000 },
  margen: 5,
  neto: 25, // presentación: sobre doypack de 25 g
  envase: null,
  precios: {},
  lotes: [],
  movs: [],
  rotulo: {
    elaborador: "Cabañas Tierras Mágicas · Villa Pehuenia – Moquehue, Neuquén",
    leyenda: "Producción artesanal · Obsequio para nuestros huéspedes · Cerrar bien el sobre y guardar en lugar fresco y seco",
  },
  vista: "plan",
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
  timerAviso = setTimeout(() => (a.hidden = true), 2800);
}
const hayFormulas = () => estado.formulas.length > 0;
const sales = () => estado.formulas;
const ings = () => ingredientes(sales());
const stockActual = () => stock(estado.movs);
const margen = () => (Number(estado.margen) || 0) / 100;

// ---------- Navegación ----------
const VISTAS = { plan: renderPlan, lotes: renderLotes, stock: renderStock, costos: renderCostos, datos: renderDatos };
function ir(v) {
  if (!VISTAS[v]) v = estado.vista in VISTAS ? estado.vista : "plan";
  estado.vista = v;
  guardar();
  $$(".vista").forEach((s) => (s.hidden = s.dataset.vista !== v));
  $$(".pestanas button").forEach((b) => b.toggleAttribute("aria-current", b.dataset.ir === v));
  $("#sin-formulas").hidden = hayFormulas() || v === "datos";
  VISTAS[v]();
  window.scrollTo(0, 0);
}
$$(".pestanas button").forEach((b) => b.addEventListener("click", () => (location.hash = b.dataset.ir)));
window.addEventListener("hashchange", () => ir(location.hash.slice(1)));
const vacio = (t) => `<p class="vacio">${t}</p>`;

// ---------- Plan ----------
function renderPlan() {
  const e = $("#plan-entradas");
  if (!e.dataset.listo) {
    e.innerHTML = `${VARIEDADES.map((s) => `<label>${esc(s.nombre)} (kg)<input type="number" min="0" step="0.1" inputmode="decimal" data-plan="${s.codigo}"></label>`).join("")}
      <label>Margen de compra (%)<input type="number" min="0" max="50" step="0.5" id="plan-margen"></label>
      <label>Neto por sobre (g)<input type="number" min="1" step="1" id="plan-neto" placeholder="25"></label>`;
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
  const r = $("#plan-resultado");
  if (!hayFormulas()) return (r.innerHTML = vacio("Sin fórmulas no se puede calcular la compra."));
  const { filas, totales } = planCompra(estado.plan, margen(), sales());
  const cods = Object.keys(totales.porSal);
  if (!cods.length) return (r.innerHTML = vacio("Cargá los kilos a producir de al menos una sal."));
  const st = stockActual();
  const hayStock = estado.movs.length > 0;
  const env = cods.map((c) => ({ c, ...envasado(totales.porSal[c], estado.neto, ETIQUETAS_POR_HOJA) }));
  r.innerHTML = `
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
        ? `<h3>Envasado (sobres doypack de ${estado.neto} g)</h3><div class="tabla-cont"><table>
        <thead><tr><th>Sal</th><th class="num">Sobres</th><th class="num">Sobrante</th><th class="num">Hojas de etiquetas</th></tr></thead>
        <tbody>${env.map((x) => `<tr><td>${esc(nombre(x.c))}</td><td class="num">${x.unidades}</td><td class="num">${formatoGramos(x.sobrante)}</td><td class="num">${x.hojas}</td></tr>`).join("")}</tbody>
      </table></div><p class="nota">Hojas de una sola variedad (${ETIQUETAS_POR_HOJA} etiquetas). Los PDF están en sales-gourmet/etiquetas/.</p>`
        : `<p class="nota">Cargá el neto por sobre para calcular sobres y etiquetas.</p>`
    }`;
}

// ---------- Lotes ----------
function renderLotes() {
  const f = $("#form-lote");
  if (!f.dataset.listo) {
    $("#lote-sal").innerHTML = VARIEDADES.map((s) => `<option value="${s.codigo}">${s.codigo} ${esc(s.nombre)}</option>`).join("");
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
            <strong>${esc(l.lote)}</strong> · ${esc(nombre(l.codigo))}
            <p>Elaborado ${fechaAR(l.fecha)}${l.responsable ? ` · ${esc(l.responsable)}` : ""}</p>
            <p>${formatoGramos(l.real)} de ${formatoGramos(l.objetivo)} <span class="etiqueta ${rend >= 95 ? "ok" : "alerta"}">${rend}%</span>${env ? ` · ${env.unidades} sobres de ${l.neto} g` : ""}</p>
            ${l.obs ? `<p>${esc(l.obs)}</p>` : ""}
          </div><div class="botones">
            <button class="boton chico secundario" type="button" data-imprimir="${esc(l.lote)}">Rótulo</button>
            <button class="boton chico peligro" type="button" data-borrar-lote="${esc(l.lote)}" aria-label="Borrar lote ${esc(l.lote)}">✕</button>
          </div></div>`;
        })
        .join("")
    : vacio("Todavía no hay lotes.");
  $$("[data-borrar-lote]").forEach((b) => b.addEventListener("click", () => borrarLote(b.dataset.borrarLote)));
  $$("[data-imprimir]").forEach((b) => b.addEventListener("click", () => imprimirRotulos(b.dataset.imprimir)));
}

function guardarLote(ev) {
  ev.preventDefault();
  const f = ev.target;
  const codigo = f.codigo.value;
  if (f.descontar.checked && !sales().some((s) => s.codigo === codigo)) return avisar("Para descontar el stock hay que cargar las fórmulas");
  const fecha = f.fecha.value;
  const lote = codigoLote(codigo, fecha, siguienteNumero(estado.lotes, codigo, fecha));
  const l = {
    lote, codigo, fecha,
    objetivo: Number(f.objetivo.value),
    real: Number(f.real.value),
    neto: Number(f.neto.value) || null,
    responsable: f.responsable.value.trim(),
    obs: f.obs.value.trim(),
  };
  estado.lotes.push(l);
  // Se descuenta lo que pide la fórmula para el peso objetivo (lo que se pesó y se mezcló)
  if (f.descontar.checked) estado.movs.push(...consumosDeLote(buscarSal(sales(), codigo), l.objetivo, lote).map((m) => ({ ...m, fecha })));
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

// Rótulo del obsequio (dorso del sobre): ingredientes en orden alfabético, sin cantidades. Sin fechas.
function imprimirRotulos(lote) {
  const l = estado.lotes.find((x) => x.lote === lote);
  const v = VARIEDADES.find((x) => x.codigo === l.codigo);
  const sal = sales().find((s) => s.codigo === l.codigo);
  const r = estado.rotulo;
  const cantidad = l.neto ? envasado(l.real, l.neto).unidades || 1 : 40; // un rótulo por sobre (varias hojas si hace falta)
  const rotulo = `<div class="rot">
    <b>${esc(v.nombre)}</b> — ${esc(v.descripcion)}<br>
    ${sal ? `<small>Contiene: ${esc(listaIngredientes(sal))}.</small><br>` : ""}
    ${l.neto ? `Contenido: ${l.neto} g · ` : ""}Lote ${esc(l.lote)}<br>
    <small>${esc(r.elaborador)}<br>${esc(r.leyenda)}</small>
  </div>`;
  const html = `<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Rótulos ${esc(l.lote)}</title><style>
    @page { size: A4; margin: 8mm; }
    body { font: 7pt/1.25 system-ui, sans-serif; margin: 0; }
    .hoja { display: grid; grid-template-columns: repeat(4, 1fr); gap: 2mm; }
    .rot { border: 0.2mm dashed #999; padding: 1.5mm; height: 26mm; overflow: hidden; }
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

// ---------- Stock ----------
function renderStock() {
  const f = $("#form-mov");
  if (!f.dataset.listo) {
    f.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const gramos = Number(f.gramos.value);
      if (!gramos || !f.ingrediente.value) return;
      estado.movs.push({
        tipo: f.tipo.value, ingrediente: f.ingrediente.value, gramos, fecha: f.fecha.value,
        proveedor: f.proveedor.value.trim(), loteProv: f.loteProv.value.trim(), ubicacion: f.ubicacion.value.trim(),
      });
      guardar();
      f.gramos.value = "";
      avisar("Movimiento guardado");
      renderStock();
    });
    f.dataset.listo = "1";
  }
  const lista = ings();
  const elegido = f.ingrediente.value;
  $("#mov-ing").innerHTML = lista.map((i) => `<option${i === elegido ? " selected" : ""}>${esc(i)}</option>`).join("");
  f.fecha.value ||= hoyISO();
  const st = stockActual();
  const todos = [...new Set([...lista, ...Object.keys(st)])].sort((a, b) => a.localeCompare(b, "es"));
  const falt = hayFormulas() ? Object.fromEntries(faltantes(estado.plan, st, margen(), sales()).map((x) => [x.ingrediente, x.comprar])) : {};
  $("#tabla-stock").innerHTML = todos.length
    ? `<div class="tabla-cont"><table>
    <thead><tr><th>Ingrediente</th><th class="num">Stock</th><th class="num">Falta para el plan</th></tr></thead>
    <tbody>${todos.map((i) => `<tr><td>${esc(i)}</td><td class="num ${(st[i] || 0) < 0 ? "negativo" : ""}">${formatoGramos(st[i] || 0)}</td><td class="num ${falt[i] ? "negativo" : ""}">${falt[i] ? formatoGramos(falt[i]) : "✓"}</td></tr>`).join("")}</tbody>
  </table></div><p class="nota">Stock negativo: se usó más de lo que se registró como compra.</p>`
    : vacio("Sin ingredientes: cargá las fórmulas.");
  const movs = estado.movs.map((m, i) => ({ ...m, i })).reverse().slice(0, 60);
  $("#lista-movs").innerHTML = movs.length
    ? `<div class="tabla-cont"><table><thead><tr><th>Fecha</th><th>Tipo</th><th>Ingrediente</th><th class="num">g</th><th>Detalle</th><th></th></tr></thead><tbody>${movs
        .map(
          (m) => `<tr><td>${fechaAR(m.fecha)}</td><td>${m.tipo}</td><td>${esc(m.ingrediente)}</td><td class="num">${m.tipo === "consumo" ? "−" : ""}${formatoGramos(m.gramos)}</td>
          <td>${esc(m.ref || [m.proveedor, m.loteProv, m.ubicacion].filter(Boolean).join(" · "))}</td>
          <td>${m.ref ? "" : `<button class="boton chico peligro" type="button" data-borrar-mov="${m.i}" aria-label="Borrar">✕</button>`}</td></tr>`
        )
        .join("")}</tbody></table></div>`
    : vacio("Sin movimientos.");
  $$("[data-borrar-mov]").forEach((b) =>
    b.addEventListener("click", () => {
      if (!confirm("¿Borrar este movimiento?")) return;
      estado.movs.splice(Number(b.dataset.borrarMov), 1);
      guardar();
      renderStock();
    })
  );
}

// ---------- Costos ----------
function renderCostos() {
  const p = $("#precios");
  p.innerHTML = hayFormulas()
    ? `<div class="controles">${ings().map((i) => `<label>${esc(i)} ($/kg)<input type="number" min="0" step="1" inputmode="decimal" data-precio="${esc(i)}"></label>`).join("")}</div>`
    : vacio("Cargá las fórmulas para ver los ingredientes.");
  $$("[data-precio]", p).forEach((inp) => {
    inp.value = estado.precios[inp.dataset.precio] ?? "";
    inp.addEventListener("input", () => {
      if (inp.value === "") delete estado.precios[inp.dataset.precio];
      else estado.precios[inp.dataset.precio] = Number(inp.value);
      guardar();
      renderTablaCostos();
    });
  });
  const pc = $("#param-costos");
  if (!pc.dataset.listo) {
    pc.innerHTML = `
      <label>Neto por sobre (g)<input type="number" min="1" step="1" id="c-neto" placeholder="25"></label>
      <label>Sobre doypack + etiquetas ($)<input type="number" min="0" step="1" id="c-envase" placeholder="por sobre"></label>
      <label>Margen de compra (%)<input type="number" min="0" step="0.5" id="c-margen"></label>`;
    const enlazar = (id, campo) =>
      $(id).addEventListener("input", (ev) => {
        estado[campo] = ev.target.value === "" ? null : Number(ev.target.value);
        guardar();
        renderTablaCostos();
      });
    enlazar("#c-neto", "neto");
    enlazar("#c-envase", "envase");
    enlazar("#c-margen", "margen");
    pc.dataset.listo = "1";
  }
  $("#c-neto").value = estado.neto ?? "";
  $("#c-envase").value = estado.envase ?? "";
  $("#c-margen").value = estado.margen ?? "";
  renderTablaCostos();
}
function renderTablaCostos() {
  if (!hayFormulas()) return ($("#tabla-costos").innerHTML = "");
  const filas = sales().map((s) => ({ s, c: costos(s, estado.precios, { margen: margen(), neto: estado.neto || 0, envase: estado.envase || 0 }) }));
  $("#tabla-costos").innerHTML = `<div class="tabla-cont"><table>
    <thead><tr><th>Sal</th><th class="num">Insumos por kg</th>${estado.neto ? '<th class="num">Insumos sobre</th><th class="num">Costo por sobre</th>' : ""}<th>Estado</th></tr></thead>
    <tbody>${filas
      .map(
        ({ s, c }) => `<tr><td>${esc(nombre(s.codigo))}</td><td class="num">${pesos(c.porKg)}</td>
        ${estado.neto ? `<td class="num">${pesos(c.insumoSobre)}</td><td class="num"><strong>${pesos(c.porSobre)}</strong></td>` : ""}
        <td>${c.completo ? '<span class="etiqueta ok">completo</span>' : `<span class="etiqueta alerta" title="${esc(c.faltan.join(", "))}">faltan ${c.faltan.length} precios</span>`}</td></tr>`
      )
      .join("")}</tbody></table></div>
    <p class="nota">Costo de cada sobre obsequiado: insumos con el margen de compra más el sobre y las etiquetas. No incluye mano de obra ni energía. ${estado.neto ? "" : "Cargá el neto por sobre para ver el costo por sobre."}</p>`;
}

// ---------- Datos ----------
// Escalado como la hoja 03_Escalado de las formulaciones, más el sobre de 25 g
const ESCALAS = [{ t: "Sobre 25 g", g: 25 }, { t: "100 g", g: 100 }, { t: "250 g", g: 250 }, { t: "500 g", g: 500 }, { t: "1 kg", g: 1000 }, { t: "5 kg", g: 5000 }];
function renderDatos() {
  $("#control-formulas").innerHTML = hayFormulas()
    ? `<div class="tabla-cont"><table><thead><tr><th>Código</th><th>Producto</th><th class="num">Ingredientes</th><th class="num">Suma %</th><th>Estado</th></tr></thead><tbody>${sales()
        .map((s) => {
          const c = controlFormula(s);
          return `<tr><td>${esc(s.codigo)}</td><td>${esc(s.nombre)}</td><td class="num">${s.formula.length}</td><td class="num">${c.suma}</td><td><span class="etiqueta ${c.cierra ? "ok" : "alerta"}">${c.cierra ? "CIERRA" : "NO CIERRA"}</span></td></tr>`;
        })
        .join("")}</tbody></table></div>
      ${sales()
        .map(
          (s) => `<details class="panel"><summary>${esc(s.codigo)} ${esc(s.nombre)}</summary><div class="tabla-cont"><table>
        <thead><tr><th>Ingrediente</th><th>Tipo</th><th>Granulometría</th><th class="num">%</th>${ESCALAS.map((e) => `<th class="num">${e.t}</th>`).join("")}</tr></thead>
        <tbody>${s.formula.map((f) => `<tr><td>${esc(f.ingrediente)}</td><td>${esc(f.tipo || "")}</td><td>${esc(f.granulometria || "")}</td><td class="num">${f.pct}</td>${ESCALAS.map((e) => `<td class="num">${formatoGramos(r1((e.g * f.pct) / 100))}</td>`).join("")}</tr>`).join("")}</tbody></table></div></details>`
        )
        .join("")}`
    : vacio("No hay fórmulas cargadas en este teléfono.");
  const el = $("#rot-elaborador");
  const le = $("#rot-leyenda");
  el.value = estado.rotulo.elaborador;
  le.value = estado.rotulo.leyenda;
  el.oninput = () => ((estado.rotulo.elaborador = el.value), guardar());
  le.oninput = () => ((estado.rotulo.leyenda = le.value), guardar());
}

async function leerJSON(input) {
  const f = input.files[0];
  input.value = "";
  if (!f) return null;
  try {
    return JSON.parse(await f.text());
  } catch {
    avisar("El archivo no es un JSON válido");
    return null;
  }
}
$("#cargar-formulas").addEventListener("change", async (ev) => {
  const d = await leerJSON(ev.target);
  if (!d) return;
  const v = validarFormulas(d);
  if (!v.ok) return alert(`No se cargaron las fórmulas:\n\n${v.errores.join("\n")}`);
  estado.formulas = v.sales;
  guardar();
  avisar(`Fórmulas cargadas: ${v.sales.length} sales`);
  ir("datos");
});
$("#borrar-formulas").addEventListener("click", () => {
  if (!confirm("¿Quitar las fórmulas de este teléfono? Lotes, stock y precios se conservan.")) return;
  estado.formulas = [];
  guardar();
  ir("datos");
});

async function descargar(nombreArchivo, contenido, tipo) {
  const blob = new Blob([contenido], { type: tipo });
  const archivo = new File([blob], nombreArchivo, { type: tipo });
  if (navigator.canShare?.({ files: [archivo] })) {
    try {
      await navigator.share({ files: [archivo], title: nombreArchivo });
      return;
    } catch (e) {
      if (e.name === "AbortError") return;
    }
  }
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = nombreArchivo;
  document.body.append(a);
  a.click();
  setTimeout(() => {
    URL.revokeObjectURL(a.href);
    a.remove();
  }, 1000);
}
const BOM = "﻿"; // para que Excel lea las tildes

$("#csv-plan").addEventListener("click", () => {
  if (!hayFormulas()) return avisar("Cargá las fórmulas primero");
  const { filas, totales } = planCompra(estado.plan, margen(), sales());
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
    ["Lote", "Variedad", "Fecha elaboración", "Peso objetivo (g)", "Peso real (g)", "Rendimiento %", "Neto sobre (g)", "Sobres", "Responsable", "Observaciones"],
    ...estado.lotes.map((l) => [l.lote, `${l.codigo} ${nombre(l.codigo)}`, l.fecha, l.objetivo, l.real, rendimiento(l.objetivo, l.real), l.neto || "", l.neto ? envasado(l.real, l.neto).unidades : "", l.responsable, l.obs]),
  ]);
  descargar(`lotes-${hoyISO()}.csv`, BOM + t, "text/csv");
});
$("#csv-stock").addEventListener("click", () => {
  const st = stockActual();
  const t = csv([
    ["STOCK"], ["Ingrediente", "Stock (g)"], ...Object.keys(st).sort().map((i) => [i, st[i]]), [],
    ["MOVIMIENTOS"], ["Fecha", "Tipo", "Ingrediente", "Gramos", "Lote producido", "Proveedor", "Lote/venc. proveedor", "Ubicación"],
    ...estado.movs.map((m) => [m.fecha, m.tipo, m.ingrediente, m.tipo === "consumo" ? -m.gramos : m.gramos, m.ref || "", m.proveedor || "", m.loteProv || "", m.ubicacion || ""]),
  ]);
  descargar(`stock-${hoyISO()}.csv`, BOM + t, "text/csv");
});
$("#respaldo").addEventListener("click", () => descargar(`taller-tm-copia-${hoyISO()}.json`, JSON.stringify({ app: "taller-tm", tipo: "copia", version: 1, estado }, null, 1), "application/json"));
$("#restaurar").addEventListener("change", async (ev) => {
  const d = await leerJSON(ev.target);
  if (!d) return;
  if (d.app !== "taller-tm" || d.tipo !== "copia" || !d.estado) return avisar("El archivo no es una copia del TM Sales");
  if (!confirm("Esto reemplaza los datos del taller de este teléfono. ¿Seguir?")) return;
  estado = { ...structuredClone(INICIAL), ...d.estado };
  guardar();
  avisar("Copia restaurada");
  ir(estado.vista);
});

// ---------- Inicio ----------
ir(location.hash.slice(1) || estado.vista);
if ("serviceWorker" in navigator && location.protocol === "https:") navigator.serviceWorker.register("sw.js").catch(() => {});
