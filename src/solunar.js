// Pronóstico solunar para pesca: posición del Sol y la Luna con fórmulas astronómicas de baja precisión
// (efemérides simplificadas, error de pocos minutos) y la teoría solunar clásica:
// - Períodos mayores (~2 h): tránsito superior e inferior de la Luna (Luna en lo alto y "bajo los pies").
// - Períodos menores (~1 h): salida y puesta de la Luna.
// - Mejores días: cerca de luna nueva y luna llena, y cuando un período coincide con la salida o la puesta del Sol.
// La teoría solunar es tradicional y no está validada científicamente: es orientativa.
import { config } from "./config.js";

const RAD = Math.PI / 180;
const DIA_MS = 86400000;
const J2000 = Date.UTC(2000, 0, 1, 12);
const OBLICUIDAD = 23.4397 * RAD;
const PASO_MS = 10 * 60000; // muestreo cada 10 minutos y refinamiento por bisección
const MAYOR_MIN = 60; // ± minutos alrededor del tránsito
const MENOR_MIN = 30; // ± minutos alrededor de la salida/puesta
const COINCIDENCIA_MIN = 60; // ventana alrededor de la salida/puesta del Sol

const diasJ2000 = (ms) => (ms - J2000) / DIA_MS;
const normalizar = (a) => ((a % (2 * Math.PI)) + 3 * Math.PI) % (2 * Math.PI) - Math.PI; // a (-π, π]

function ecuatorial(lon, lat) {
  return {
    ra: Math.atan2(Math.sin(lon) * Math.cos(OBLICUIDAD) - Math.tan(lat) * Math.sin(OBLICUIDAD), Math.cos(lon)),
    dec: Math.asin(Math.sin(lat) * Math.cos(OBLICUIDAD) + Math.cos(lat) * Math.sin(OBLICUIDAD) * Math.sin(lon)),
  };
}

function sol(d) {
  const M = RAD * (357.5291 + 0.98560028 * d);
  const C = RAD * (1.9148 * Math.sin(M) + 0.02 * Math.sin(2 * M) + 0.0003 * Math.sin(3 * M));
  const lon = M + C + RAD * 102.9372 + Math.PI;
  return { ...ecuatorial(lon, 0), dist: 149598000 };
}

function luna(d) {
  const L = RAD * (218.316 + 13.176396 * d);
  const M = RAD * (134.963 + 13.064993 * d);
  const F = RAD * (93.272 + 13.22935 * d);
  return { ...ecuatorial(L + RAD * 6.289 * Math.sin(M), RAD * 5.128 * Math.sin(F)), dist: 385001 - 20905 * Math.cos(M) };
}

function angHorario(d, ra, lat, lon) {
  return normalizar(RAD * (280.16 + 360.9856235 * d) + lon * RAD - ra);
}

function altura(cuerpo, ms, lat, lon) {
  const d = diasJ2000(ms);
  const { ra, dec } = cuerpo(d);
  const H = angHorario(d, ra, lat, lon);
  const phi = lat * RAD;
  return Math.asin(Math.sin(phi) * Math.sin(dec) + Math.cos(phi) * Math.cos(dec) * Math.cos(H)) / RAD;
}

// Altura aparente de la Luna corregida por refracción; la salida/puesta se toma a +0,133°
// (paralaje − refracción − semidiámetro), como es habitual.
function alturaLuna(ms, lat, lon) {
  const h = altura(luna, ms, lat, lon);
  const hr = Math.max(h, 0) * RAD;
  return h + 0.0002967 / Math.tan(hr + 0.00312536 / (hr + 0.08901179)) / RAD;
}

// Raíces de f en [desde, hasta): muestreo y bisección. Devuelve { ms, sube } por cada cruce de 0.
function cruces(f, desde, hasta) {
  const res = [];
  let t0 = desde;
  let v0 = f(t0);
  for (let t1 = desde + PASO_MS; t1 <= hasta; t1 += PASO_MS) {
    const v1 = f(t1);
    if (v0 === 0 || v0 * v1 < 0) {
      let a = t0, b = t1, fa = v0;
      for (let i = 0; i < 20; i++) {
        const m = (a + b) / 2;
        const fm = f(m);
        if (fa * fm <= 0) b = m;
        else { a = m; fa = fm; }
      }
      res.push({ ms: (a + b) / 2, sube: v1 > v0 });
    }
    t0 = t1;
    v0 = v1;
  }
  return res;
}

// Tránsitos de la Luna: cuando el ángulo horario pasa por 0 (superior) o por ±180° (inferior).
function transitos(desde, hasta, lat, lon) {
  const H = (ms) => { const d = diasJ2000(ms); return angHorario(d, luna(d).ra, lat, lon); };
  const todos = cruces((ms) => Math.sin(H(ms)), desde, hasta);
  return {
    superior: todos.filter((c) => c.sube && Math.cos(H(c.ms)) > 0).map((c) => c.ms),
    inferior: todos.filter((c) => !c.sube && Math.cos(H(c.ms)) < 0).map((c) => c.ms),
  };
}

export function faseLunar(ms) {
  const d = diasJ2000(ms);
  const s = sol(d);
  const m = luna(d);
  const phi = Math.acos(Math.sin(s.dec) * Math.sin(m.dec) + Math.cos(s.dec) * Math.cos(m.dec) * Math.cos(s.ra - m.ra));
  const inc = Math.atan2(s.dist * Math.sin(phi), m.dist - s.dist * Math.cos(phi));
  const angulo = Math.atan2(Math.cos(s.dec) * Math.sin(s.ra - m.ra), Math.sin(s.dec) * Math.cos(m.dec) - Math.cos(s.dec) * Math.sin(m.dec) * Math.cos(s.ra - m.ra));
  const fase = 0.5 + (0.5 * inc * (angulo < 0 ? -1 : 1)) / Math.PI; // 0 nueva · 0,25 creciente · 0,5 llena · 0,75 menguante
  return { fase, iluminacion: (1 + Math.cos(inc)) / 2 };
}

function nombreFase(fase) {
  const nombres = ["Luna nueva", "Luna creciente", "Cuarto creciente", "Gibosa creciente", "Luna llena", "Gibosa menguante", "Cuarto menguante", "Luna menguante"];
  const emojis = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"];
  const i = Math.round(fase * 8) % 8;
  return { nombre: nombres[i], emoji: emojis[i] };
}

// Desfase de la zona horaria (minutos a sumar a UTC) en un instante dado
function desfaseMin(ms, zona) {
  const p = Object.fromEntries(new Intl.DateTimeFormat("en-US", { timeZone: zona, hourCycle: "h23", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" })
    .formatToParts(new Date(ms)).map((x) => [x.type, x.value]));
  return (Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour, +p.minute) - Math.floor(ms / 60000) * 60000) / 60000;
}

function inicioDiaLocal(fechaISO, zona) {
  const medianocheUTC = Date.parse(fechaISO + "T00:00:00Z");
  return medianocheUTC - desfaseMin(medianocheUTC, zona) * 60000;
}

const horaLocal = (ms, zona) => new Date(ms).toLocaleTimeString("es-AR", { timeZone: zona, hour: "2-digit", minute: "2-digit", hourCycle: "h23" });

/**
 * Pronóstico de un día local.
 * @param {string} fechaISO AAAA-MM-DD
 * @param {{lat:number, lon:number, zona:string}} lugar
 */
export function pronosticoDia(fechaISO, { lat, lon, zona }) {
  const ini = inicioDiaLocal(fechaISO, zona);
  const fin = ini + DIA_MS;
  const hora = (ms) => horaLocal(ms, zona);

  const sl = cruces((ms) => altura(sol, ms, lat, lon) + 0.833, ini, fin);
  const ll = cruces((ms) => alturaLuna(ms, lat, lon) - 0.133, ini, fin);
  const tr = transitos(ini, fin, lat, lon);
  const salidaSol = sl.find((c) => c.sube)?.ms;
  const puestaSol = sl.find((c) => !c.sube)?.ms;

  const periodos = [
    ...tr.superior.map((ms) => ({ tipo: "mayor", motivo: "Luna en lo alto", centro: ms, min: MAYOR_MIN })),
    ...tr.inferior.map((ms) => ({ tipo: "mayor", motivo: "Luna bajo los pies", centro: ms, min: MAYOR_MIN })),
    ...ll.map((c) => ({ tipo: "menor", motivo: c.sube ? "Salida de la Luna" : "Puesta de la Luna", centro: c.ms, min: MENOR_MIN })),
  ]
    .sort((a, b) => a.centro - b.centro)
    .map((p) => {
      const coincide = [salidaSol, puestaSol].some((s) => s !== undefined && Math.abs(s - p.centro) <= (p.min + COINCIDENCIA_MIN) * 60000);
      return {
        tipo: p.tipo,
        motivo: p.motivo,
        inicio: hora(p.centro - p.min * 60000),
        fin: hora(p.centro + p.min * 60000),
        // posición en el día (0 a 1) para dibujar la línea de tiempo
        desde: Math.max(0, (p.centro - p.min * 60000 - ini) / DIA_MS),
        hasta: Math.min(1, (p.centro + p.min * 60000 - ini) / DIA_MS),
        coincide_sol: coincide,
      };
    });

  const { fase, iluminacion } = faseLunar(ini + DIA_MS / 2);
  // 1 en luna nueva o llena, 0 en los cuartos
  const cercaniaSicigia = Math.abs(Math.cos(2 * Math.PI * fase));
  const coincidencias = periodos.filter((p) => p.coincide_sol).length;
  const puntaje = Math.min(100, Math.round(25 + 55 * cercaniaSicigia ** 2 + 10 * Math.min(coincidencias, 2)));
  const calificacion = puntaje >= 80 ? "Excelente" : puntaje >= 60 ? "Muy bueno" : puntaje >= 40 ? "Bueno" : "Regular";

  return {
    fecha: fechaISO,
    puntaje,
    calificacion,
    luna: { ...nombreFase(fase), iluminacion: Math.round(iluminacion * 100) },
    sol: { salida: salidaSol && hora(salidaSol), puesta: puestaSol && hora(puestaSol) },
    periodos,
  };
}

export function lugarNegocio() {
  const n = config.negocio;
  return { lat: Number(n.coordenadas?.lat), lon: Number(n.coordenadas?.lon), zona: n.zona_horaria };
}

const MAX_DIAS = 62;

export function pronostico(desdeISO, dias, lugar = lugarNegocio()) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(desdeISO || "") || isNaN(Date.parse(desdeISO))) throw new Error("Fecha inválida (AAAA-MM-DD).");
  if (!Number.isFinite(lugar.lat) || !Number.isFinite(lugar.lon)) throw new Error("Faltan las coordenadas del negocio en config.json.");
  const n = Math.min(MAX_DIAS, Math.max(1, Math.floor(Number(dias)) || 7));
  return Array.from({ length: n }, (_, i) => {
    const d = new Date(desdeISO + "T12:00:00Z");
    d.setUTCDate(d.getUTCDate() + i);
    return pronosticoDia(d.toISOString().slice(0, 10), lugar);
  });
}
