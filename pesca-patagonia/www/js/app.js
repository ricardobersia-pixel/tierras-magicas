import { pronostico } from "./solunar.js";
import { LUGARES, ZONA_ARGENTINA, PATROCINADOR } from "./lugares.js";

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const mayuscula = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const fechaLarga = (iso) => new Date(iso + "T12:00:00").toLocaleDateString("es-AR", { weekday: "long", day: "numeric", month: "long" });
const fechaCorta = (iso) => mayuscula(new Date(iso + "T12:00:00").toLocaleDateString("es-AR", { weekday: "short", day: "numeric", month: "short" }));
const zonaTelefono = () => Intl.DateTimeFormat().resolvedOptions().timeZone || ZONA_ARGENTINA;
const hoyEn = (zona) => new Date().toLocaleDateString("en-CA", { timeZone: zona });

// Preferencias del usuario en el teléfono (puede no haber almacenamiento disponible)
const guardar = (clave, valor) => { try { localStorage.setItem(clave, JSON.stringify(valor)); } catch { /* sin almacenamiento */ } };
const leer = (clave) => { try { return JSON.parse(localStorage.getItem(clave)); } catch { return null; } };

const GPS = "gps";
let miUbicacion = leer("mi-ubicacion"); // { lat, lon }

function lugarActual() {
  const id = $("#lugar").value;
  if (id === GPS && miUbicacion) return { nombre: "Mi ubicación", lat: miUbicacion.lat, lon: miUbicacion.lon, zona: zonaTelefono() };
  const l = LUGARES.find((x) => x.id === id) || LUGARES[0];
  return { ...l, zona: ZONA_ARGENTINA };
}

const fraccion = (hhmm) => {
  const [h, m] = hhmm.split(":").map(Number);
  return (h * 60 + m) / 1440;
};

const nivel = (p) => (p >= 80 ? "n4" : p >= 60 ? "n3" : p >= 40 ? "n2" : "n1");

function lineaTiempo(d) {
  const bloques = d.periodos
    .map((p) => `<span class="bloque ${p.tipo}" style="left:${(p.desde * 100).toFixed(2)}%;width:${((p.hasta - p.desde) * 100).toFixed(2)}%"></span>`)
    .join("");
  const soles = [d.sol.salida, d.sol.puesta].filter(Boolean).map((h) => `<span class="marca-sol" style="left:${(fraccion(h) * 100).toFixed(2)}%"></span>`).join("");
  // Franja clara entre la salida y la puesta del sol
  const dia = d.sol.salida && d.sol.puesta ? [fraccion(d.sol.salida) * 100, fraccion(d.sol.puesta) * 100].map((x) => x.toFixed(2)) : null;
  const fondo = dia ? ` style="--amanece:${dia[0]}%;--anochece:${dia[1]}%"` : "";
  return `<div class="linea${dia ? " con-sol" : ""}" aria-hidden="true"${fondo}>${bloques}${soles}</div>
    <div class="horas" aria-hidden="true"><span>0</span><span>6</span><span>12</span><span>18</span><span>24</span></div>`;
}

function tarjetaDia(d, esHoy = false) {
  return `<article class="dia ${esHoy ? "destacado" : ""}">
    <header>
      <div>
        <h3>${esHoy ? "Hoy · " + esc(fechaLarga(d.fecha)) : esc(fechaCorta(d.fecha))}</h3>
        <p class="meta">${d.luna.emoji} ${esc(d.luna.nombre)} (${d.luna.iluminacion}%) · ☀ ${d.sol.salida ?? "–"} a ${d.sol.puesta ?? "–"}</p>
      </div>
      <div class="puntaje ${nivel(d.puntaje)}"><strong>${d.puntaje}</strong><span>${esc(d.calificacion)}</span></div>
    </header>
    ${lineaTiempo(d)}
    <ul class="periodos">${d.periodos
      .map((p) => `<li class="${p.tipo}"><strong>${p.inicio}–${p.fin}</strong> ${p.tipo === "mayor" ? "Mayor" : "Menor"} · ${esc(p.motivo)}${p.coincide_sol ? " ☀" : ""}</li>`)
      .join("")}</ul>
  </article>`;
}

// Los 3 mejores días del período, separados entre sí
function mejoresDias(dias) {
  const elegidos = [];
  for (const d of [...dias].sort((a, b) => b.puntaje - a.puntaje)) {
    if (elegidos.every((e) => Math.abs(new Date(e.fecha) - new Date(d.fecha)) >= 2 * 86400000)) elegidos.push(d);
    if (elegidos.length === 3) break;
  }
  return elegidos.sort((a, b) => a.fecha.localeCompare(b.fecha));
}

function calcular() {
  const lugar = lugarActual();
  $("#coords").textContent = `${lugar.lat.toFixed(2)}°, ${lugar.lon.toFixed(2)}° · ${lugar.zona === ZONA_ARGENTINA ? "hora de Argentina" : "hora del teléfono"}`;
  $("#error").textContent = "";
  let dias;
  try {
    dias = pronostico($("#desde").value || hoyEn(lugar.zona), $("#dias").value, lugar);
  } catch (e) {
    $("#error").textContent = e.message;
    return;
  }
  const [primero, ...resto] = dias;
  const esHoy = primero.fecha === hoyEn(lugar.zona);
  $("#hoy").innerHTML = tarjetaDia(primero, esHoy);
  $("#dias-lista").innerHTML = (esHoy ? resto : dias).map((d) => tarjetaDia(d)).join("");
  const mejores = dias.length >= 4 ? mejoresDias(dias) : [];
  $("#mejores-sec").hidden = !mejores.length;
  $("#mejores").innerHTML = mejores
    .map((d) => `<div class="mejor"><span class="puntaje ${nivel(d.puntaje)}"><strong>${d.puntaje}</strong></span>
      <span><strong>${esc(fechaCorta(d.fecha))}</strong><br><small>${d.luna.emoji} ${esc(d.luna.nombre)}</small></span></div>`)
    .join("");
}

function opcionesLugar() {
  const porProvincia = Object.groupBy ? Object.groupBy(LUGARES, (l) => l.provincia) : LUGARES.reduce((a, l) => ((a[l.provincia] ||= []).push(l), a), {});
  $("#lugar").innerHTML =
    `<option value="${GPS}">📍 Mi ubicación${miUbicacion ? "" : " (GPS)"}</option>` +
    Object.entries(porProvincia)
      .map(([prov, ls]) => `<optgroup label="${esc(prov)}">${ls.map((l) => `<option value="${l.id}">${esc(l.nombre)}</option>`).join("")}</optgroup>`)
      .join("");
}

// Devuelve null si obtuvo la ubicación, o el mensaje de error
function pedirUbicacion() {
  if (!navigator.geolocation) return Promise.resolve("Este teléfono no permite obtener la ubicación.");
  $("#coords").textContent = "Buscando tu ubicación…";
  return new Promise((listo) =>
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        miUbicacion = { lat: pos.coords.latitude, lon: pos.coords.longitude };
        guardar("mi-ubicacion", miUbicacion);
        listo(null);
      },
      () => listo("No se pudo obtener la ubicación. Revisá que el GPS y el permiso de ubicación estén activados, o elegí un lugar de la lista."),
      { enableHighAccuracy: false, timeout: 15000, maximumAge: 10 * 60000 }
    )
  );
}

const ultimoLugar = () => (LUGARES.some((l) => l.id === leer("lugar")) ? leer("lugar") : LUGARES[0].id);

async function cambiarLugar() {
  let id = $("#lugar").value;
  let error = null;
  if (id === GPS) {
    // Se intenta actualizar la ubicación; si falla, se usa la última guardada o el último lugar elegido
    error = await pedirUbicacion();
    if (error && !miUbicacion) id = ultimoLugar();
    opcionesLugar();
    $("#lugar").value = id;
  }
  guardar("lugar", id);
  calcular();
  if (error) $("#error").textContent = error;
}

function patrocinador() {
  const p = PATROCINADOR;
  const wa = `https://wa.me/${p.whatsapp}?text=${encodeURIComponent("Hola! Vi Pesca Patagonia y quería consultar por las cabañas.")}`;
  $("#patrocinador").innerHTML = `<p class="sobre">Presentado por</p>
    <h2>${esc(p.nombre)}</h2>
    <p>${esc(p.lugar)} · ${esc(p.texto)}</p>
    <p class="acciones"><a class="boton" href="${wa}" target="_blank" rel="noopener">Consultar por WhatsApp</a>
    <a class="boton sec" href="https://instagram.com/${esc(p.instagram)}" target="_blank" rel="noopener">Instagram</a></p>`;
}

function iniciar() {
  opcionesLugar();
  const guardado = leer("lugar");
  $("#lugar").value = guardado === GPS && miUbicacion ? GPS : ultimoLugar();
  $("#desde").value = hoyEn(lugarActual().zona);
  $("#lugar").addEventListener("change", cambiarLugar);
  $("#desde").addEventListener("change", calcular);
  $("#dias").addEventListener("change", calcular);
  patrocinador();
  calcular();
}

iniciar();

// Instalación como app (navegadores compatibles) y funcionamiento sin señal
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
