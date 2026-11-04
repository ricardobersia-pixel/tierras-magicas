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
  // Limpieza y mantenimiento: solo ven qué cabañas están ocupadas y sus tareas, sin datos de huéspedes ni montos
  if (rol === "limpieza" || rol === "mantenimiento") {
    return {
      hoy, desde, hasta, usuario,
      cabanas: config.cabanas.map((c) => ({ id: c.id, nombre: c.nombre })),
      ocupacion: config.cabanas.flatMap((c) => ocupaciones(c.id).filter((o) => o.hasta >= desde && o.desde <= hasta).map((o) => ({ cabana_id: c.id, desde: o.desde, hasta: o.hasta }))),
      // Las tareas generadas por una reserva llevan el nombre del huésped: se reemplaza por un texto genérico
      tareas: tareas.filter((t) => t.tipo === rol).map((t) => (!t.reserva_id ? t : {
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
    reservas: db.prepare(`SELECT r.*, COALESCE((SELECT SUM(monto) FROM pagos p WHERE p.reserva_id = r.id), 0) AS pagado
      FROM reservas r WHERE checkout >= ? ORDER BY checkin`).all(hoy),
    bloqueos: db.prepare("SELECT * FROM bloqueos WHERE hasta >= ? AND desde <= ? ORDER BY desde").all(desde, hasta),
    tareas,
    sync: db.prepare("SELECT * FROM sync_log ORDER BY id DESC LIMIT 12").all(),
    ingresosMes: rol !== "dueno" ? null : db.prepare("SELECT COALESCE(SUM(total),0) AS total, COUNT(*) AS n FROM reservas WHERE estado='confirmada' AND substr(checkin,1,7)=?").get(hoy.slice(0, 7)),
    pagoOnline,
    iaActiva,
  };
}

// ---------- Calendario mensual (vista tipo mapa de asientos) ----------

const esMes = (s) => typeof s === "string" && /^\d{4}-(0[1-9]|1[0-2])$/.test(s);
const mesSiguiente = (mes) => {
  const [a, m] = mes.split("-").map(Number);
  return m === 12 ? `${a + 1}-01-01` : `${a}-${String(m + 1).padStart(2, "0")}-01`;
};

// Ocupación del mes por cabaña y del dormi. Dueño y recepción ven los datos de cada reserva;
// limpieza y mantenimiento solo ven qué días están ocupados.
export function calendarioMes(usuario, mes) {
  if (!esMes(mes)) throw new Error("Mes inválido (AAAA-MM).");
  const ini = `${mes}-01`;
  const fin = mesSiguiente(mes);
  const conDatos = ["dueno", "recepcion"].includes(usuario.rol);
  const reservas = db.prepare(
    `SELECT r.*, COALESCE((SELECT SUM(monto) FROM pagos p WHERE p.reserva_id = r.id), 0) AS pagado
     FROM reservas r WHERE estado != 'cancelada' AND checkin < ? AND checkout > ? ORDER BY checkin`
  ).all(fin, ini);
  const otas = db.prepare("SELECT * FROM reservas_ota WHERE cancelada = 0 AND desde < ? AND hasta > ?").all(fin, ini);
  const uidsOta = new Set(otas.map((o) => o.uid));
  const bloqueos = db.prepare("SELECT * FROM bloqueos WHERE desde < ? AND hasta > ?").all(fin, ini);

  const reserva = (r) => conDatos
    ? { tipo: "reserva", id: r.id, desde: r.checkin, hasta: r.checkout, estado: r.estado, canal: r.canal || (r.origen === "web" ? "web" : "whatsapp"),
        nombre: r.nombre, huespedes: r.huespedes, adicionales: r.adicionales, telefono: r.telefono, email: r.email, notas: r.notas,
        total: r.total, pagado: r.pagado, origen: r.origen }
    : { tipo: "reserva", desde: r.checkin, hasta: r.checkout, estado: r.estado };
  const ota = (o) => conDatos
    ? { tipo: o.origen, id: o.id, desde: o.desde, hasta: o.hasta, resumen: o.resumen, monto_neto: o.monto_neto, comision: o.comision }
    : { tipo: o.origen, desde: o.desde, hasta: o.hasta };

  return {
    mes,
    hoy: hoyISO(),
    con_datos: conDatos,
    filas: [
      ...config.cabanas.map((c) => ({
        id: c.id,
        nombre: c.nombre,
        capacidad: c.capacidad,
        ocupaciones: [
          ...reservas.filter((r) => r.cabana_id === c.id).map(reserva),
          ...otas.filter((o) => o.cabana_id === c.id).map(ota),
          ...bloqueos.filter((b) => b.cabana_id === c.id && (b.origen === "manual" || !uidsOta.has(b.uid))).map((b) => ({
            tipo: "bloqueo", origen: b.origen, desde: b.desde, hasta: b.hasta, resumen: conDatos ? b.resumen : null,
          })),
        ],
      })),
      {
        id: "dormi",
        nombre: "Dormi",
        capacidad: config.negocio.dormi?.plazas || 0,
        ocupaciones: reservas.filter((r) => r.adicionales > 0 && r.estado !== "cancelada").map((r) => ({
          ...reserva(r), cabana: config.cabanas.find((c) => c.id === r.cabana_id)?.nombre,
        })),
      },
    ],
  };
}
