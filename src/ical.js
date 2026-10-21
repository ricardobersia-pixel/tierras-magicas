import { db } from "./db.js";
import { config } from "./config.js";
import { sumarDias, hoyISO, ocupaciones } from "./reservas.js";

// --- Importación: Airbnb y Booking publican un calendario .ics por anuncio ---

function desplegar(texto) {
  // RFC 5545: líneas que empiezan con espacio/tab continúan la anterior
  return texto.replace(/\r?\n[ \t]/g, "");
}

function fechaICal(valor) {
  const m = valor.match(/(\d{4})(\d{2})(\d{2})/);
  return m ? `${m[1]}-${m[2]}-${m[3]}` : null;
}

export function parsearICal(texto) {
  const eventos = [];
  for (const bloque of desplegar(texto).split("BEGIN:VEVENT").slice(1)) {
    const cuerpo = bloque.split("END:VEVENT")[0];
    const campo = (nombre) => {
      const m = cuerpo.match(new RegExp(`^${nombre}(?:;[^:\\r\\n]*)?:(.*)$`, "m"));
      return m ? m[1].trim() : null;
    };
    const desde = fechaICal(campo("DTSTART") || "");
    let hasta = fechaICal(campo("DTEND") || "");
    if (!desde) continue;
    if (!hasta || hasta <= desde) hasta = sumarDias(desde, 1);
    eventos.push({ uid: campo("UID"), desde, hasta, resumen: campo("SUMMARY") });
  }
  return eventos;
}

export async function sincronizarCabana(cabana) {
  const resultados = [];
  for (const [origen, url] of Object.entries(cabana.ical_importar || {})) {
    if (!url) continue;
    try {
      const res = await fetch(url, { signal: AbortSignal.timeout(20000), headers: { "User-Agent": "TierrasMagicas/1.0" } });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const texto = await res.text();
      if (!texto.includes("BEGIN:VCALENDAR")) throw new Error("La respuesta no es un calendario iCal");
      const eventos = parsearICal(texto).filter((e) => e.hasta >= hoyISO());

      db.exec("BEGIN");
      db.prepare("DELETE FROM bloqueos WHERE cabana_id = ? AND origen = ?").run(cabana.id, origen);
      const ins = db.prepare("INSERT INTO bloqueos (cabana_id, desde, hasta, origen, uid, resumen) VALUES (?, ?, ?, ?, ?, ?)");
      for (const e of eventos) ins.run(cabana.id, e.desde, e.hasta, origen, e.uid, e.resumen);
      db.exec("COMMIT");

      db.prepare("INSERT INTO sync_log (cabana_id, origen, ok, mensaje) VALUES (?, ?, 1, ?)").run(cabana.id, origen, `${eventos.length} ocupaciones`);
      resultados.push({ cabana: cabana.id, origen, ok: true, ocupaciones: eventos.length });
    } catch (e) {
      try { db.exec("ROLLBACK"); } catch {}
      db.prepare("INSERT INTO sync_log (cabana_id, origen, ok, mensaje) VALUES (?, ?, 0, ?)").run(cabana.id, origen, String(e.message));
      resultados.push({ cabana: cabana.id, origen, ok: false, error: e.message });
    }
  }
  return resultados;
}

export async function sincronizarTodo() {
  const todos = [];
  for (const c of config.cabanas) todos.push(...(await sincronizarCabana(c)));
  return todos;
}

// --- Exportación: este calendario se pega en Airbnb y Booking ("Importar calendario") ---
// Incluye reservas web/manuales y bloqueos manuales. NO reexporta lo importado
// de Airbnb/Booking, para evitar bucles entre plataformas.

function formatoFecha(iso) {
  return iso.replace(/-/g, "");
}

export function exportarICal(cabanaId) {
  const propias = ocupaciones(cabanaId).filter((o) => o.id && o.hasta >= hoyISO());
  const reservas = propias.filter((o) => o.origen === "web");
  const manuales = db.prepare("SELECT id, desde, hasta FROM bloqueos WHERE cabana_id = ? AND origen = 'manual' AND hasta >= ?").all(cabanaId, hoyISO());
  const sello = new Date().toISOString().replace(/[-:]/g, "").slice(0, 15) + "Z";
  const lineas = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Tierras Magicas//Reservas//ES",
    "CALSCALE:GREGORIAN",
    ...[...reservas.map((r) => ({ ...r, uid: `${r.id}@tierrasmagicas` })), ...manuales.map((b) => ({ ...b, uid: `bloqueo-${b.id}@tierrasmagicas` }))].flatMap((e) => [
      "BEGIN:VEVENT",
      `UID:${e.uid}`,
      `DTSTAMP:${sello}`,
      `DTSTART;VALUE=DATE:${formatoFecha(e.desde)}`,
      `DTEND;VALUE=DATE:${formatoFecha(e.hasta)}`,
      "SUMMARY:No disponible",
      "END:VEVENT",
    ]),
    "END:VCALENDAR",
  ];
  return lineas.join("\r\n") + "\r\n";
}
