import { db } from "./db.js";
import { config } from "./config.js";
import { hoyISO, sumarDias, ocupaciones, ocupacionesDormi } from "./reservas.js";

// Datos del panel según el rol. Lo usan el servidor y la app de prueba del teléfono.
// icalExportar(cabana): enlace del calendario para pegar en Airbnb/Booking (solo lo ve el dueño).
export function resumenPanel(usuario, desdePedido, { icalExportar, pagoOnline, iaActiva }) {
  const hoy = hoyISO();
  const desde = desdePedido || hoy;
  const hasta = sumarDias(desde, 42);
  const rol = usuario.rol;
  const tareas = db.prepare("SELECT * FROM tareas WHERE hecha = 0 AND fecha <= ? ORDER BY fecha").all(sumarDias(hoy, 7));
  // Limpieza: solo ve qué cabañas están ocupadas y sus tareas de limpieza, sin datos de huéspedes ni montos
  if (rol === "limpieza") {
    return {
      hoy, desde, hasta, usuario,
      cabanas: config.cabanas.map((c) => ({ id: c.id, nombre: c.nombre })),
      ocupacion: config.cabanas.flatMap((c) => ocupaciones(c.id).filter((o) => o.hasta >= desde && o.desde <= hasta).map((o) => ({ cabana_id: c.id, desde: o.desde, hasta: o.hasta }))),
      tareas: tareas.filter((t) => t.tipo === "limpieza").map((t) => ({
        ...t, descripcion: "Limpieza tras la salida de los huéspedes" + (/\(incluye el dormi\)/.test(t.descripcion) ? " (incluye el dormi)" : ""),
      })),
      dormi: ocupacionesDormi().filter((o) => o.hasta >= desde && o.desde <= hasta).map((o) => ({ desde: o.desde, hasta: o.hasta })),
    };
  }
  return {
    hoy,
    desde,
    hasta,
    usuario,
    cabanas: config.cabanas.map((c) => ({
      id: c.id, nombre: c.nombre,
      ical_exportar: rol === "dueno" ? icalExportar(c) : null,
      ical_configurado: Object.fromEntries(Object.entries(c.ical_importar || {}).map(([k, v]) => [k, Boolean(v)])),
    })),
    reservas: db.prepare("SELECT * FROM reservas WHERE checkout >= ? ORDER BY checkin").all(hoy),
    bloqueos: db.prepare("SELECT * FROM bloqueos WHERE hasta >= ? AND desde <= ? ORDER BY desde").all(desde, hasta),
    tareas,
    sync: db.prepare("SELECT * FROM sync_log ORDER BY id DESC LIMIT 12").all(),
    ingresosMes: rol !== "dueno" ? null : db.prepare("SELECT COALESCE(SUM(total),0) AS total, COUNT(*) AS n FROM reservas WHERE estado='confirmada' AND substr(checkin,1,7)=?").get(hoy.slice(0, 7)),
    pagoOnline,
    iaActiva,
  };
}
