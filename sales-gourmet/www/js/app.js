// Sales de la Cordillera (app para huéspedes): sales, recetas y guía de uso. Funciona sin conexión.
import { SALES, RECETAS, GUIA } from "./datos.js";

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const salDe = (codigo) => SALES.find((s) => s.codigo === codigo);
const sinTildes = (t) => t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

// ---------- Navegación: #sales, #recetas, #guia, #sal/TM-01, #receta/id ----------
function ir(ruta) {
  const [vista, param] = ruta.split("/");
  $$(".vista").forEach((s) => (s.hidden = true));
  let pestana = vista;
  if (vista === "sal" && salDe(param)) {
    renderSal(param);
    $("#vista-sal").hidden = false;
    pestana = "sales";
  } else if (vista === "receta" && RECETAS.some((r) => r.id === param)) {
    renderReceta(param);
    $("#vista-receta").hidden = false;
    pestana = "recetas";
  } else if (["recetas", "guia"].includes(vista)) {
    $(`#vista-${vista}`).hidden = false;
  } else {
    $("#vista-sales").hidden = false;
    pestana = "sales";
  }
  $$(".pestanas button").forEach((b) => b.toggleAttribute("aria-current", b.dataset.ir === pestana));
  window.scrollTo(0, 0);
}
$$(".pestanas button").forEach((b) => b.addEventListener("click", () => (location.hash = b.dataset.ir)));
window.addEventListener("hashchange", () => ir(location.hash.slice(1)));

// ---------- Fotos: si falta el archivo, queda el bloque con el color de la sal ----------
function foto(r, clase = "") {
  const s = salDe(r.sal);
  return `<div class="foto ${clase}" style="--sal:${s.color}"><span>${esc(s.nombre)}</span>
    <img src="img/recetas/${esc(r.foto)}" alt="${esc(r.titulo)}" loading="lazy" onerror="this.remove()"></div>`;
}

function tarjetaReceta(r) {
  return `<a class="tarjeta-receta" href="#receta/${r.id}">
    ${foto(r)}
    <div class="cuerpo"><p class="de-sal">${esc(salDe(r.sal).nombre)}</p><h3>${esc(r.titulo)}</h3>
    <p class="datos">${r.porciones} porciones · ${esc(r.tiempo)}</p></div></a>`;
}

// ---------- Sales ----------
function renderSales() {
  $("#lista-sales").innerHTML = SALES.map(
    (s) => `<a class="tarjeta-sal" style="--sal:${s.color}" href="#sal/${s.codigo}">
      <img src="${s.imagen}" alt="Etiqueta ${esc(s.nombre)}" loading="lazy"><span>${esc(s.descripcion)}</span></a>`
  ).join("");
}

function renderSal(codigo) {
  const s = salDe(codigo);
  const recetas = RECETAS.filter((r) => r.sal === codigo);
  $("#vista-sal").innerHTML = `
    <a class="boton secundario chico volver" href="#sales">← Sales</a>
    <div class="ficha-cab">
      <img src="${s.imagen}" alt="">
      <div><h2>${esc(s.nombre)}</h2><p>${esc(s.descripcion)}</p><p>${esc(s.ideal)}</p></div>
    </div>
    <p class="nota"><strong>Contiene:</strong> ${esc(s.contiene)}.</p>
    <h3>Recetas con ${esc(s.nombre)}</h3>
    <div class="grilla-recetas">${recetas.map(tarjetaReceta).join("")}</div>`;
}

// ---------- Recetas ----------
let filtroSal = "";
function renderRecetas() {
  const q = sinTildes($("#buscar-receta").value.trim());
  const lista = RECETAS.filter((r) => !filtroSal || r.sal === filtroSal).filter(
    (r) => !q || sinTildes([r.titulo, r.bajada, ...r.ingredientes, ...r.pasos].join(" ")).includes(q)
  );
  $("#lista-recetas").innerHTML = lista.map(tarjetaReceta).join("") || `<p class="vacio">No hay recetas con esa búsqueda.</p>`;
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

function renderReceta(id) {
  const r = RECETAS.find((x) => x.id === id);
  const s = salDe(r.sal);
  $("#vista-receta").innerHTML = `
    <a class="boton secundario chico volver" href="#recetas">← Recetas</a>
    <article class="receta" style="--sal:${s.color}">
      ${foto(r, "grande")}
      <p class="de-sal"><a href="#sal/${s.codigo}">${esc(s.nombre)}</a></p>
      <h2>${esc(r.titulo)}</h2>
      <p class="bajada">${esc(r.bajada)}</p>
      <p class="datos">🍽 ${r.porciones} porciones · ⏱ ${esc(r.tiempo)}</p>
      <h3>Ingredientes</h3>
      <ul>${r.ingredientes.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>
      <h3>Preparación</h3>
      <ol>${r.pasos.map((p) => `<li>${esc(p)}</li>`).join("")}</ol>
      ${r.consejo ? `<p class="consejo">💡 ${esc(r.consejo)}</p>` : ""}
      ${r.seguridad ? `<p class="seguridad">⚠️ ${esc(r.seguridad)}</p>` : ""}
    </article>`;
}

// ---------- Guía ----------
function renderGuia() {
  $("#guia").innerHTML = GUIA.map((g) => `<div class="guia-item"><strong>${esc(g.titulo)}</strong>${esc(g.texto)}</div>`).join("");
}

// ---------- Inicio ----------
renderSales();
iniciarRecetas();
renderGuia();
// Enlace del QR de la etiqueta: ?sal=TM-01 abre la ficha de esa sal
const salQR = (new URLSearchParams(location.search).get("sal") || "").toUpperCase();
if (salDe(salQR) && !location.hash) location.hash = `sal/${salQR}`;
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
