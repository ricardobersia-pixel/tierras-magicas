import { pronostico } from "./solunar.js";
import { LUGARES, ZONA_ARGENTINA, PATROCINADOR, REGULACION } from "./lugares.js";
import {
  obtenerPronostico, resumenDia, estadoCielo, cardinal, consejoViento, DIAS_MAX, horaMasCercana, horasDeCaza, vientoCaza, avisosCaza,
} from "./clima.js";

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
let modo = leer("modo") === "caza" ? "caza" : "pesca";
let diasActuales = [];
// Estado del pronóstico del tiempo: { cargando } | { dias, actualizado, desdeCopia, error? } | { error }
let clima = null;
let consulta = 0; // evita mostrar una respuesta vieja si se cambió de lugar mientras cargaba

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

// La flecha apunta hacia donde sopla el viento (la dirección informada es de dónde viene)
const flecha = (grados) => (Number.isFinite(grados) ? `<span class="flecha" style="transform:rotate(${grados}deg)" aria-hidden="true">↓</span>` : "");

function horasDestacadas(horas) {
  return `<div class="horario">${horas
    .filter((f) => Number(f.hora.slice(0, 2)) % 3 === 0)
    .map((f) => `<div><span>${f.hora.slice(0, 2)} h</span><span>${estadoCielo(f.codigo).emoji}</span><strong>${Math.round(f.temp)}°</strong>
      <span>${flecha(f.direccion)} ${Math.round(f.viento)}</span><small>ráf. ${Math.round(f.rafaga)}</small></div>`)
    .join("")}</div>`;
}

function bloqueClima(d, esHoy) {
  if (!clima || clima.cargando) return `<p class="clima-nota">Cargando el tiempo…</p>`;
  const horas = clima.dias?.[d.fecha];
  if (!horas) {
    if (!clima.dias) return `<p class="clima-nota">El tiempo no está disponible sin conexión.</p>`;
    return `<p class="clima-nota">Sin pronóstico del tiempo para esta fecha (hasta ${DIAS_MAX} días).</p>`;
  }
  const r = resumenDia(horas, d.sol);
  const tendencia = r.tendencia ? { sube: "↑ sube", baja: "↓ baja", estable: "→ estable" }[r.tendencia.sentido] : "";
  const kayak =
    modo === "pesca" && r.condiciones.nivel !== "aptas"
      ? `<p class="aviso ${r.condiciones.nivel}">🛶 Ráfagas de hasta ${r.rafaga} km/h: ${r.condiciones.nivel === "desaconsejado" ? "no conviene salir en kayak ni en bote chico" : "precaución en kayak y bote"}.</p>`
      : "";
  return `<div class="clima">
      <span>${r.cielo.emoji} ${esc(r.cielo.texto)}</span>
      <span>🌡 ${r.tempMin}° a ${r.tempMax}°</span>
      <span>💨 ${flecha(r.direccion)} ${r.direccion !== null ? cardinal(r.direccion) + " " : ""}${r.viento} km/h · ráf. ${r.rafaga}</span>
      <span>🌧 ${r.probLluvia}%${r.lluvia ? ` · ${r.lluvia} mm` : ""}</span>
      <span>⏱ ${r.presion} hPa ${tendencia}</span>
    </div>
    ${modo === "caza" ? climaCaza(d, horas) : `<p class="condiciones ${r.condiciones.nivel}">Condiciones en el lago: <strong>${esc(r.condiciones.texto)}</strong></p>${kayak}`}
    ${esHoy ? horasDestacadas(horas) : ""}`;
}

const NIVEL_VIENTO_CAZA = { estable: "aptas", calma: "precaucion", arrachado: "precaucion", cambiante: "precaucion", fuerte: "desaconsejado" };

// Tiempo para la caza: a la primera y la última luz, viento para el acecho en esas horas y avisos
function climaCaza(d, horas) {
  const civil = d.sol.crepusculos?.civil || {};
  const momento = (icono, nombre, hhmm) => {
    const f = horaMasCercana(horas, hhmm);
    if (!f) return "";
    return `<li>${icono} Tiempo a la <strong>${nombre}</strong>: ${estadoCielo(f.codigo).emoji} ${Math.round(f.temp)}° · ${flecha(f.direccion)} ${cardinal(f.direccion)} ${Math.round(f.viento)} km/h, ráf. ${Math.round(f.rafaga)}</li>`;
  };
  const filas = horasDeCaza(horas, civil);
  const v = vientoCaza(filas);
  const avisos = avisosCaza(horas, filas);
  return `<ul class="momentos">${momento("🌅", "primera luz", civil.inicio)}${momento("🌇", "última luz", civil.fin)}</ul>
    ${v ? `<p class="condiciones ${NIVEL_VIENTO_CAZA[v.nivel]}">Viento para el acecho: <strong>${esc(v.texto)}</strong> <small>(${v.direccion !== null ? cardinal(v.direccion) + " " : ""}${v.velocidad} km/h, ráf. ${v.rafaga})</small></p>` : ""}
    ${v && v.direccion !== null && v.nivel !== "cambiante" ? `<p class="consejo">🦌 ${esc(consejoViento(v.direccion))}</p>` : ""}
    ${avisos.map((a) => `<p class="aviso ${a.nivel}">${esc(a.texto)}</p>`).join("")}`;
}

function bloqueCaza(d) {
  const c = d.sol.crepusculos;
  if (!c) return "";
  return `<ul class="crepusculos">
      <li><strong>Primera luz ${c.civil.inicio ?? "–"}</strong> · última luz <strong>${c.civil.fin ?? "–"}</strong> <small>(crepúsculo civil)</small></li>
      <li>Crepúsculo náutico ${c.nautico.inicio ?? "–"} a ${c.nautico.fin ?? "–"} · astronómico ${c.astronomico.inicio ?? "–"} a ${c.astronomico.fin ?? "–"}</li>
    </ul>`;
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
    ${modo === "caza" ? bloqueCaza(d) : ""}
    ${bloqueClima(d, esHoy)}
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

const haceCuanto = (ms) => {
  const min = Math.round((Date.now() - ms) / 60000);
  return min < 1 ? "recién" : min < 60 ? `hace ${min} min` : `hace ${Math.round(min / 60)} h`;
};

function estadoClima() {
  const el = $("#clima-estado");
  if (!clima || clima.cargando) el.textContent = "Tiempo: consultando Open-Meteo…";
  else if (!clima.dias) el.textContent = `Tiempo no disponible: ${clima.error}`;
  else if (clima.error) el.textContent = `Sin conexión: pronóstico del tiempo guardado ${haceCuanto(clima.actualizado)}.`;
  else el.textContent = `Tiempo actualizado ${haceCuanto(clima.actualizado)}.`;
}

async function cargarClima(lugar) {
  const n = ++consulta;
  clima = { cargando: true };
  estadoClima();
  try {
    const r = await obtenerPronostico(lugar);
    if (n !== consulta) return;
    clima = r;
  } catch (e) {
    if (n !== consulta) return;
    // Un fallo de red llega como TypeError ("Failed to fetch"): se explica en castellano
    clima = { error: navigator.onLine === false || e instanceof TypeError ? "sin conexión o el servicio no responde" : e.message };
  }
  estadoClima();
  mostrar();
}

function calcular() {
  const lugar = lugarActual();
  $("#coords").textContent = `${lugar.lat.toFixed(2)}°, ${lugar.lon.toFixed(2)}° · ${lugar.zona === ZONA_ARGENTINA ? "hora de Argentina" : "hora del teléfono"}`;
  $("#error").textContent = "";
  try {
    diasActuales = pronostico($("#desde").value || hoyEn(lugar.zona), $("#dias").value, lugar);
  } catch (e) {
    $("#error").textContent = e.message;
    return;
  }
  mostrar();
  cargarClima(lugar);
}

function mostrar() {
  const dias = diasActuales;
  if (!dias.length) return;
  const lugar = lugarActual();
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

function cambiarModo(nuevo) {
  modo = nuevo;
  guardar("modo", modo);
  document.querySelectorAll("button[data-modo]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.modo === modo)));
  document.body.dataset.actividad = modo;
  regulacion();
  mostrar();
}

async function compartirUbicacion() {
  const error = await pedirUbicacion();
  if (error) {
    $("#error").textContent = error;
    return;
  }
  const { lat, lon } = miUbicacion;
  const texto = `Estoy ${modo === "caza" ? "cazando" : "pescando"} acá: https://maps.google.com/?q=${lat.toFixed(5)},${lon.toFixed(5)}`;
  try {
    if (navigator.share) return await navigator.share({ title: "Mi ubicación", text: texto });
  } catch (e) {
    if (e.name === "AbortError") return;
  }
  window.open(`https://wa.me/?text=${encodeURIComponent(texto)}`, "_blank", "noopener");
}

function regulacion() {
  const actividad = modo === "caza" ? "caza" : "pesca";
  const general =
    actividad === "pesca"
      ? "Para pescar necesitás el permiso de pesca deportiva de la provincia y respetar la temporada, los cupos y las zonas de devolución obligatoria. En Parques Nacionales rige además su propia reglamentación."
      : "Para cazar necesitás el permiso de caza de la provincia, la licencia de armas vigente y respetar las temporadas, las especies habilitadas, los cupos, las zonas y los horarios legales de tiro.";
  $("#regulacion").innerHTML = `<summary>Permisos y reglamentos de ${actividad}</summary>
    <p>${general}</p>
    <ul>${REGULACION.map((r) => `<li>${esc(r.provincia)}: ${r[actividad] ? `<a href="${esc(r[actividad])}" target="_blank" rel="noopener">reglamento oficial</a>` : "consultá el organismo de fauna y pesca de la provincia"}</li>`).join("")}</ul>
    <p>Las fechas y los cupos cambian cada temporada: verificalos siempre en la fuente oficial antes de salir.</p>`;
}

function patrocinador() {
  const p = PATROCINADOR;
  const wa = `https://wa.me/${p.whatsapp}?text=${encodeURIComponent("Hola! Vi Caza&Pesca Patagonia y quería consultar por las cabañas.")}`;
  $("#patrocinador").innerHTML = `<div class="patrocinador-cabecera">
      <img class="logo-tm" src="img/logo-tierras-magicas.jpg" width="96" height="98" alt="Logo de Tierras Mágicas, cabañas de montaña">
      <div><p class="sobre">Presentado por</p><h2>${esc(p.nombre)}</h2></div>
    </div>
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
  document.querySelectorAll("button[data-modo]").forEach((b) => b.addEventListener("click", () => cambiarModo(b.dataset.modo)));
  $("#btn-compartir").addEventListener("click", compartirUbicacion);
  // Al volver la conexión se actualiza el tiempo
  window.addEventListener("online", () => cargarClima(lugarActual()));
  patrocinador();
  cambiarModo(modo);
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
