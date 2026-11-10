// Pronóstico del tiempo de Open-Meteo (https://open-meteo.com): viento, ráfagas, presión, lluvia y temperatura por hora.
// La última consulta se guarda en el teléfono para verla sin señal.
// Las funciones de resumen y de condiciones son puras: no dependen del navegador.

const API = "https://api.open-meteo.com/v1/forecast";
export const DIAS_MAX = 16; // máximo que ofrece Open-Meteo
const VIGENCIA_MS = 60 * 60000; // se vuelve a consultar después de 1 hora
const VARIABLES = [
  "temperature_2m",
  "apparent_temperature",
  "precipitation_probability",
  "precipitation",
  "weather_code",
  "cloud_cover",
  "pressure_msl",
  "wind_speed_10m",
  "wind_gusts_10m",
  "wind_direction_10m",
];

// Umbrales de condiciones para estar en el lago (km/h). SUPUESTO a validar con quien conozca el lago Moquehue.
export const UMBRALES = { precaucion: { viento: 15, rafaga: 25 }, desaconsejado: { viento: 25, rafaga: 35 } };

// Se redondea a 2 decimales (~1 km): alcanza para el pronóstico y no envía la ubicación exacta
const redondear = (x) => Math.round(x * 100) / 100;

export function urlPronostico({ lat, lon, zona }) {
  const q = new URLSearchParams({
    latitude: redondear(lat),
    longitude: redondear(lon),
    hourly: VARIABLES.join(","),
    timezone: zona,
    forecast_days: DIAS_MAX,
    wind_speed_unit: "kmh",
  });
  return `${API}?${q}`;
}

// Respuesta de Open-Meteo → { "AAAA-MM-DD": [ { hora, temp, ... }, ... ] }
export function porDia(respuesta) {
  const h = respuesta?.hourly;
  if (!h?.time?.length) throw new Error("Respuesta del pronóstico sin datos por hora.");
  const dias = {};
  h.time.forEach((t, i) => {
    const fila = {
      hora: t.slice(11, 16),
      temp: h.temperature_2m?.[i],
      sensacion: h.apparent_temperature?.[i],
      probLluvia: h.precipitation_probability?.[i],
      lluvia: h.precipitation?.[i],
      codigo: h.weather_code?.[i],
      nubes: h.cloud_cover?.[i],
      presion: h.pressure_msl?.[i],
      viento: h.wind_speed_10m?.[i],
      rafaga: h.wind_gusts_10m?.[i],
      direccion: h.wind_direction_10m?.[i],
    };
    (dias[t.slice(0, 10)] ||= []).push(fila);
  });
  return dias;
}

const PUNTOS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"];
export const cardinal = (grados) => PUNTOS[Math.round((((grados % 360) + 360) % 360) / 22.5) % 16];

// Dirección promedio (vectorial: el promedio de 350° y 10° es 0°, no 180°)
export function direccionMedia(grados) {
  const v = grados.filter((g) => Number.isFinite(g));
  if (!v.length) return null;
  const x = v.reduce((s, g) => s + Math.cos((g * Math.PI) / 180), 0);
  const y = v.reduce((s, g) => s + Math.sin((g * Math.PI) / 180), 0);
  return Math.round(((Math.atan2(y, x) * 180) / Math.PI + 360) % 360);
}

// Códigos WMO que usa Open-Meteo
export function estadoCielo(codigo) {
  if (codigo === 0) return { texto: "Despejado", emoji: "☀️" };
  if (codigo === 1 || codigo === 2) return { texto: "Parcialmente nublado", emoji: "⛅" };
  if (codigo === 3) return { texto: "Nublado", emoji: "☁️" };
  if (codigo === 45 || codigo === 48) return { texto: "Niebla", emoji: "🌫️" };
  if (codigo >= 51 && codigo <= 57) return { texto: "Llovizna", emoji: "🌦️" };
  if (codigo >= 61 && codigo <= 67) return { texto: "Lluvia", emoji: "🌧️" };
  if (codigo >= 71 && codigo <= 77) return { texto: "Nieve", emoji: "🌨️" };
  if (codigo >= 80 && codigo <= 82) return { texto: "Chaparrones", emoji: "🌦️" };
  if (codigo === 85 || codigo === 86) return { texto: "Nevadas", emoji: "🌨️" };
  if (codigo >= 95) return { texto: "Tormenta", emoji: "⛈️" };
  return { texto: "Sin dato", emoji: "·" };
}

// Tendencia de la presión en 3 horas (convención meteorológica)
export function tendenciaPresion(antes, despues) {
  if (!Number.isFinite(antes) || !Number.isFinite(despues)) return null;
  const d = despues - antes;
  return { cambio: Math.round(d * 10) / 10, sentido: d >= 1.5 ? "sube" : d <= -1.5 ? "baja" : "estable" };
}

export function condiciones(viento, rafaga) {
  const u = UMBRALES;
  if (viento >= u.desaconsejado.viento || rafaga >= u.desaconsejado.rafaga) return { nivel: "desaconsejado", texto: "No recomendadas en el lago" };
  if (viento >= u.precaucion.viento || rafaga >= u.precaucion.rafaga) return { nivel: "precaucion", texto: "Con precaución" };
  return { nivel: "aptas", texto: "Aptas" };
}

const max = (filas, k) => Math.max(...filas.map((f) => f[k]).filter(Number.isFinite));
const min = (filas, k) => Math.min(...filas.map((f) => f[k]).filter(Number.isFinite));

/**
 * Resumen de un día. Viento, ráfagas y cielo se calculan en las horas de luz (cuando se sale a pescar o cazar).
 * @param {Array} horas filas de porDia para la fecha
 * @param {{salida?:string, puesta?:string}} sol horarios del sol para limitar a las horas de luz
 */
export function resumenDia(horas, sol = {}) {
  if (!horas?.length) return null;
  const deDia = horas.filter((f) => (!sol.salida || f.hora >= sol.salida.slice(0, 2) + ":00") && (!sol.puesta || f.hora <= sol.puesta));
  const base = deDia.length ? deDia : horas;
  const viento = max(base, "viento");
  const rafaga = max(base, "rafaga");
  const codigos = base.map((f) => f.codigo).filter(Number.isFinite);
  // El código más "severo" del día representa mejor lo que puede pasar
  const codigo = codigos.length ? Math.max(...codigos) : null;
  const iniPresion = horas.find((f) => f.hora === "09:00") || horas[0];
  const finPresion = horas.find((f) => f.hora === "12:00") || horas[Math.min(3, horas.length - 1)];
  return {
    tempMin: Math.round(min(horas, "temp")),
    tempMax: Math.round(max(horas, "temp")),
    viento: Math.round(viento),
    rafaga: Math.round(rafaga),
    direccion: direccionMedia(base.map((f) => f.direccion)),
    probLluvia: Math.round(max(horas, "probLluvia")),
    lluvia: Math.round(horas.reduce((s, f) => s + (f.lluvia || 0), 0) * 10) / 10,
    cielo: estadoCielo(codigo),
    presion: Math.round(iniPresion.presion),
    tendencia: tendenciaPresion(iniPresion.presion, finPresion.presion),
    condiciones: condiciones(viento, rafaga),
  };
}

// Caza: hay que acercarse con el viento en la cara, desde el lado hacia donde sopla
export function consejoViento(direccion) {
  if (!Number.isFinite(direccion)) return null;
  const de = cardinal(direccion);
  const hacia = cardinal(direccion + 180);
  return `Viento del ${de}: acercate desde el ${hacia}, caminando hacia el ${de} con el viento en la cara.`;
}

// ---------- Consulta con copia guardada (navegador) ----------

const clave = ({ lat, lon }) => `clima:${redondear(lat)},${redondear(lon)}`;

function leerCopia(lugar) {
  try {
    return JSON.parse(localStorage.getItem(clave(lugar)));
  } catch {
    return null;
  }
}

function guardarCopia(lugar, datos) {
  try {
    localStorage.setItem(clave(lugar), JSON.stringify(datos));
  } catch {
    /* sin almacenamiento: se usa solo en memoria */
  }
}

/**
 * Pronóstico por día para un lugar: usa la copia guardada si tiene menos de 1 hora; si no, consulta Open-Meteo.
 * Sin conexión devuelve la última copia, indicando su antigüedad.
 * @returns {Promise<{dias:Object, actualizado:number, desdeCopia:boolean, error?:string}>}
 */
export async function obtenerPronostico(lugar, { ahora = Date.now(), fetchFn = globalThis.fetch } = {}) {
  const copia = leerCopia(lugar);
  if (copia && ahora - copia.actualizado < VIGENCIA_MS) return { ...copia, desdeCopia: true };
  try {
    const r = await fetchFn(urlPronostico(lugar));
    if (!r.ok) throw new Error(`El servicio del tiempo respondió ${r.status}.`);
    const datos = { dias: porDia(await r.json()), actualizado: ahora };
    guardarCopia(lugar, datos);
    return { ...datos, desdeCopia: false };
  } catch (e) {
    if (copia) return { ...copia, desdeCopia: true, error: e.message };
    throw e;
  }
}

// ---------- Caza ----------

const aMin = (hhmm) => Number(hhmm.slice(0, 2)) * 60 + Number(hhmm.slice(3, 5));

// Fila de la hora más cercana a un horario "HH:MM"
export function horaMasCercana(horas, hhmm) {
  if (!horas?.length || !hhmm) return null;
  return horas.reduce((mejor, f) => (Math.abs(aMin(f.hora) - aMin(hhmm)) < Math.abs(aMin(mejor.hora) - aMin(hhmm)) ? f : mejor));
}

// Horas de las salidas de caza: desde la primera luz hasta 3 h después, y desde 3 h antes hasta la última luz.
// Entra cada hora (de HH:00 a HH:59) que se superpone con alguna de esas ventanas.
export function horasDeCaza(horas, civil = {}) {
  if (!horas?.length || !civil.inicio || !civil.fin) return [];
  const ini = aMin(civil.inicio);
  const fin = aMin(civil.fin);
  const toca = (m, desde, hasta) => m + 60 > desde && m < hasta;
  return horas.filter((f) => toca(aMin(f.hora), ini, ini + 180) || toca(aMin(f.hora), fin - 180, fin));
}

// Qué tan constante es la dirección: 1 = siempre la misma, 0 = cambia en todas las direcciones
function constancia(grados) {
  const v = grados.filter(Number.isFinite);
  if (v.length < 2) return 1;
  const x = v.reduce((s, g) => s + Math.cos((g * Math.PI) / 180), 0) / v.length;
  const y = v.reduce((s, g) => s + Math.sin((g * Math.PI) / 180), 0) / v.length;
  return Math.hypot(x, y);
}

/**
 * Viento para el acecho en las horas de caza. Criterios de práctica de caza (orientativos):
 * calma = el olor queda alrededor; arrachado o cambiante = no se puede controlar de dónde llega el olor.
 */
export function vientoCaza(filas) {
  const v = filas.filter((f) => Number.isFinite(f.viento));
  if (!v.length) return null;
  const medio = v.reduce((s, f) => s + f.viento, 0) / v.length;
  const rafaga = Math.max(...v.map((f) => f.rafaga).filter(Number.isFinite), 0);
  const direccion = direccionMedia(v.map((f) => f.direccion));
  const base = { velocidad: Math.round(medio), rafaga: Math.round(rafaga), direccion };
  if (medio >= 25) return { ...base, nivel: "fuerte", texto: "Fuerte: los animales se esconden y cuesta oír y apuntar" };
  if (constancia(v.map((f) => f.direccion)) < 0.7) return { ...base, nivel: "cambiante", texto: "Cambiante: rota de dirección y es difícil controlar el olor" };
  if (rafaga >= 25 && rafaga >= medio * 1.8) return { ...base, nivel: "arrachado", texto: "Arrachado: ráfagas que desparraman el olor" };
  if (medio < 5) return { ...base, nivel: "calma", texto: "Calma: el olor queda alrededor tuyo; moverse despacio" };
  return { ...base, nivel: "estable", texto: "Estable: bueno para el acecho con el viento en la cara" };
}

// Calor para conservar la carne (SUPUESTO de práctica: por encima de esta máxima, enfriar la pieza enseguida)
export const MAXIMA_CARNE = 15;

export function avisosCaza(horas, filasCaza) {
  const avisos = [];
  const codigos = horas.map((f) => f.codigo);
  if (codigos.some((c) => c >= 95)) avisos.push({ nivel: "desaconsejado", texto: "⛈ Tormenta eléctrica: evitá filos, cumbres y zonas abiertas." });
  if (filasCaza.some((f) => f.codigo === 45 || f.codigo === 48)) avisos.push({ nivel: "precaucion", texto: "🌫 Niebla en las horas de caza: identificá bien el blanco y lo que hay detrás antes de tirar." });
  const rafaga = Math.max(...horas.map((f) => f.rafaga).filter(Number.isFinite), 0);
  if (rafaga >= 50) avisos.push({ nivel: "precaucion", texto: `🌲 Ráfagas de hasta ${Math.round(rafaga)} km/h: riesgo de caída de ramas y árboles en el bosque.` });
  if (codigos.some((c) => (c >= 71 && c <= 77) || c === 85 || c === 86)) avisos.push({ nivel: "info", texto: "🌨 Nieve: buenas huellas para rastrear; abrigate y planificá el regreso." });
  const maxima = Math.max(...horas.map((f) => f.temp).filter(Number.isFinite));
  if (maxima >= MAXIMA_CARNE) avisos.push({ nivel: "info", texto: `🌡 Máxima de ${Math.round(maxima)}°: enfriá la carne cuanto antes después de la caza.` });
  return avisos;
}
