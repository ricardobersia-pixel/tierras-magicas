const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const mayuscula = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const fechaLarga = (iso) => mayuscula(new Date(iso + "T12:00:00").toLocaleDateString("es-AR", { weekday: "long", day: "numeric", month: "long" }));
const fechaCorta = (iso) => mayuscula(new Date(iso + "T12:00:00").toLocaleDateString("es-AR", { weekday: "short", day: "numeric", month: "short" }));
const hoyLocal = () => new Date().toLocaleDateString("en-CA", { timeZone: "America/Argentina/Buenos_Aires" });

function sumar(iso, dias) {
  const d = new Date(iso + "T12:00:00Z");
  d.setUTCDate(d.getUTCDate() + dias);
  return d.toISOString().slice(0, 10);
}

// Minutos desde medianoche → fracción del día, para ubicar el sol en la línea de tiempo
const fraccion = (hhmm) => {
  const [h, m] = hhmm.split(":").map(Number);
  return (h * 60 + m) / 1440;
};

function nivel(puntaje) {
  return puntaje >= 80 ? "n4" : puntaje >= 60 ? "n3" : puntaje >= 40 ? "n2" : "n1";
}

function lineaTiempo(d) {
  const bloques = d.periodos
    .map((p) => `<span class="bloque ${p.tipo}" style="left:${(p.desde * 100).toFixed(2)}%;width:${((p.hasta - p.desde) * 100).toFixed(2)}%" title="${esc(p.motivo)} ${p.inicio}–${p.fin}"></span>`)
    .join("");
  const soles = [d.sol.salida, d.sol.puesta].filter(Boolean).map((h) => `<span class="marca-sol" style="left:${(fraccion(h) * 100).toFixed(2)}%"></span>`).join("");
  // Franja clara entre la salida y la puesta del sol
  const dia = d.sol.salida && d.sol.puesta ? [fraccion(d.sol.salida) * 100, fraccion(d.sol.puesta) * 100].map((x) => x.toFixed(2)) : null;
  const fondo = dia ? ` style="background:linear-gradient(90deg,#dfe4e9 0 ${dia[0]}%,#f3ead2 ${dia[0]}% ${dia[1]}%,#dfe4e9 ${dia[1]}%)"` : "";
  return `<div class="linea" aria-hidden="true"${fondo}>${bloques}${soles}</div>
    <div class="horas" aria-hidden="true"><span>0</span><span>6</span><span>12</span><span>18</span><span>24</span></div>`;
}

function listaPeriodos(d) {
  return `<ul class="periodos">${d.periodos
    .map((p) => `<li class="${p.tipo}"><strong>${p.inicio}–${p.fin}</strong> ${p.tipo === "mayor" ? "Mayor" : "Menor"} · ${esc(p.motivo)}${p.coincide_sol ? " ☀" : ""}</li>`)
    .join("")}</ul>`;
}

function tarjetaDia(d, destacada = false) {
  return `<article class="dia ${destacada ? "destacado" : ""}">
    <header>
      <div>
        <h3>${destacada ? "Hoy · " + esc(fechaLarga(d.fecha).toLowerCase()) : esc(fechaCorta(d.fecha))}</h3>
        <p class="meta">${d.luna.emoji} ${esc(d.luna.nombre)} (${d.luna.iluminacion}%) · ☀ ${d.sol.salida ?? "–"} a ${d.sol.puesta ?? "–"}</p>
      </div>
      <div class="puntaje ${nivel(d.puntaje)}"><strong>${d.puntaje}</strong><span>${esc(d.calificacion)}</span></div>
    </header>
    ${lineaTiempo(d)}
    ${listaPeriodos(d)}
  </article>`;
}

// Bloques de días consecutivos con mejor puntaje, para sugerir una escapada (mínimo 2 noches)
function mejoresEscapadas(dias) {
  const candidatos = [];
  for (let i = 0; i + 1 < dias.length; i++) {
    const tramo = dias.slice(i, i + 2);
    candidatos.push({ desde: tramo[0].fecha, promedio: tramo.reduce((s, d) => s + d.puntaje, 0) / tramo.length });
  }
  const elegidos = [];
  for (const c of candidatos.sort((a, b) => b.promedio - a.promedio)) {
    if (elegidos.every((e) => Math.abs(new Date(e.desde) - new Date(c.desde)) >= 3 * 86400000)) elegidos.push(c);
    if (elegidos.length === 3) break;
  }
  return elegidos.sort((a, b) => a.desde.localeCompare(b.desde));
}

async function cargar() {
  const desde = $("#desde").value || hoyLocal();
  const dias = $("#dias").value;
  $("#error").textContent = "";
  let datos;
  try {
    const r = await fetch(`/api/pesca?desde=${desde}&dias=${dias}`);
    datos = await r.json();
    if (!r.ok) throw new Error(datos.error || "No se pudo calcular el pronóstico.");
  } catch (e) {
    $("#error").textContent = e.message === "Failed to fetch" ? "Sin conexión y sin un pronóstico guardado para estas fechas." : e.message;
    return;
  }
  if (datos.ubicacion) $("#ubicacion").textContent = datos.ubicacion;

  const [primero, ...resto] = datos.dias;
  const esHoy = primero.fecha === hoyLocal();
  $("#hoy").innerHTML = tarjetaDia(primero, esHoy);
  $("#dias-lista").innerHTML = (esHoy ? resto : datos.dias).map((d) => tarjetaDia(d)).join("");

  const escapadas = datos.dias.length >= 4 ? mejoresEscapadas(datos.dias) : [];
  $("#mejores-sec").hidden = !escapadas.length;
  $("#mejores").innerHTML = escapadas
    .map((e) => {
      const checkout = sumar(e.desde, 2);
      return `<a class="mejor" href="/?checkin=${e.desde}&checkout=${checkout}&huespedes=2#reservar">
        <span class="puntaje ${nivel(e.promedio)}"><strong>${Math.round(e.promedio)}</strong></span>
        <span><strong>${esc(fechaCorta(e.desde))} → ${esc(fechaCorta(checkout))}</strong><br><small>Ver disponibilidad para 2 noches</small></span>
      </a>`;
    })
    .join("");
}

$("#desde").value = hoyLocal();
$("#desde").addEventListener("change", cargar);
$("#dias").addEventListener("change", cargar);
cargar();

// Instalación como app (PWA)
if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
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
