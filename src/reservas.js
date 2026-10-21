import crypto from "node:crypto";
import { db } from "./db.js";
import { config, env, cabanaPorId } from "./config.js";

// Con Mercado Pago, una reserva web sin pagar retiene las fechas durante este tiempo.
// Sin Mercado Pago (modo demo) la solicitud retiene las fechas hasta que el dueño la confirma o cancela.
const RETENCION_PENDIENTE_MIN = 30;

export function hoyISO() {
  return new Date().toLocaleDateString("en-CA", { timeZone: config.negocio.zona_horaria });
}

export function sumarDias(fechaISO, dias) {
  const d = new Date(fechaISO + "T12:00:00Z");
  d.setUTCDate(d.getUTCDate() + dias);
  return d.toISOString().slice(0, 10);
}

export function noches(checkin, checkout) {
  return Math.round((new Date(checkout + "T12:00:00Z") - new Date(checkin + "T12:00:00Z")) / 86400000);
}

function esFecha(s) {
  return typeof s === "string" && /^\d{4}-\d{2}-\d{2}$/.test(s) && !isNaN(new Date(s + "T12:00:00Z"));
}

function multiplicadorTemporada(fechaISO) {
  const md = fechaISO.slice(5); // MM-DD
  for (const t of config.temporadas || []) {
    const dentro = t.desde <= t.hasta ? md >= t.desde && md <= t.hasta : md >= t.desde || md <= t.hasta;
    if (dentro) return t.multiplicador;
  }
  return 1;
}

export function cotizar(cabana, checkin, checkout, huespedes) {
  let total = 0;
  for (let f = checkin; f < checkout; f = sumarDias(f, 1)) {
    total += cabana.precio_noche * multiplicadorTemporada(f);
  }
  const extra = Math.max(0, huespedes - 2) * (cabana.precio_huesped_extra || 0) * noches(checkin, checkout);
  total = Math.round(total + extra);
  const sena = Math.round((total * config.negocio.sena_porcentaje) / 100);
  return { noches: noches(checkin, checkout), total, sena, saldo: total - sena };
}

// Devuelve los rangos ocupados de una cabaña (reservas activas + bloqueos importados/manuales)
export function ocupaciones(cabanaId, excluirReservaId = null) {
  const reservas = db
    .prepare(
      `SELECT id, checkin AS desde, checkout AS hasta, estado, nombre, 'web' AS origen FROM reservas
       WHERE cabana_id = ? AND (estado = 'confirmada'
         OR (estado = 'pendiente_pago' AND (origen = 'manual' OR ? OR creada > datetime('now', ?))))`
    )
    .all(cabanaId, env.mpAccessToken ? 0 : 1, `-${RETENCION_PENDIENTE_MIN} minutes`)
    .filter((r) => r.id !== excluirReservaId);
  const bloqueos = db.prepare(`SELECT desde, hasta, origen, resumen FROM bloqueos WHERE cabana_id = ?`).all(cabanaId);
  return [...reservas, ...bloqueos];
}

export function estaLibre(cabanaId, checkin, checkout, excluirReservaId = null) {
  return !ocupaciones(cabanaId, excluirReservaId).some((o) => checkin < o.hasta && o.desde < checkout);
}

export function validarRango(checkin, checkout) {
  if (!esFecha(checkin) || !esFecha(checkout)) return "Fechas inválidas (formato AAAA-MM-DD).";
  if (checkout <= checkin) return "La fecha de salida debe ser posterior a la de ingreso.";
  if (checkin < hoyISO()) return "La fecha de ingreso ya pasó.";
  if (noches(checkin, checkout) > 60) return "Para estadías de más de 60 noches, consultanos por WhatsApp.";
  return null;
}

export function buscarDisponibilidad(checkin, checkout, huespedes) {
  const error = validarRango(checkin, checkout);
  if (error) return { error };
  const n = noches(checkin, checkout);
  return {
    checkin,
    checkout,
    noches: n,
    huespedes,
    cabanas: config.cabanas
      .filter((c) => c.capacidad >= huespedes)
      .map((c) => {
        const libre = estaLibre(c.id, checkin, checkout);
        const cumpleMinimo = n >= c.minimo_noches;
        return {
          id: c.id,
          nombre: c.nombre,
          capacidad: c.capacidad,
          disponible: libre && cumpleMinimo,
          motivo: !libre ? "ocupada" : !cumpleMinimo ? `mínimo ${c.minimo_noches} noches` : null,
          ...cotizar(c, checkin, checkout, huespedes),
        };
      }),
  };
}

export function crearReserva({ cabanaId, checkin, checkout, huespedes, nombre, email, telefono, notas, origen = "web" }) {
  const cabana = cabanaPorId(cabanaId);
  if (!cabana) throw new Error("Cabaña inexistente.");
  const error = validarRango(checkin, checkout);
  if (error) throw new Error(error);
  huespedes = Number(huespedes);
  if (!(huespedes >= 1 && huespedes <= cabana.capacidad)) throw new Error(`Capacidad máxima: ${cabana.capacidad} personas.`);
  if (origen === "web" && noches(checkin, checkout) < cabana.minimo_noches)
    throw new Error(`Esta cabaña requiere un mínimo de ${cabana.minimo_noches} noches.`);
  if (!nombre?.trim()) throw new Error("Falta el nombre.");

  const id = "TM-" + crypto.randomBytes(3).toString("hex").toUpperCase();
  const { total, sena } = cotizar(cabana, checkin, checkout, huespedes);

  // Verificación + inserción atómica para evitar doble reserva
  db.exec("BEGIN IMMEDIATE");
  try {
    if (!estaLibre(cabanaId, checkin, checkout)) throw new Error("Las fechas elegidas ya no están disponibles.");
    db.prepare(
      `INSERT INTO reservas (id, cabana_id, checkin, checkout, huespedes, nombre, email, telefono, total, sena, estado, origen, notas)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).run(id, cabanaId, checkin, checkout, huespedes, nombre.trim(), email || null, telefono || null, total, sena,
      origen === "manual" ? "confirmada" : "pendiente_pago", origen, notas || null);
    db.exec("COMMIT");
  } catch (e) {
    db.exec("ROLLBACK");
    throw e;
  }
  if (origen === "manual") generarTareas(id);
  return obtenerReserva(id);
}

export function obtenerReserva(id) {
  return db.prepare("SELECT * FROM reservas WHERE id = ?").get(id);
}

export function confirmarReserva(id, mpPaymentId = null) {
  const r = obtenerReserva(id);
  if (!r || r.estado === "confirmada") return r;
  db.prepare("UPDATE reservas SET estado = 'confirmada', mp_payment_id = COALESCE(?, mp_payment_id) WHERE id = ?").run(mpPaymentId, id);
  generarTareas(id);
  return obtenerReserva(id);
}

export function cancelarReserva(id) {
  db.prepare("UPDATE reservas SET estado = 'cancelada' WHERE id = ?").run(id);
  db.prepare("DELETE FROM tareas WHERE reserva_id = ? AND hecha = 0").run(id);
}

function generarTareas(reservaId) {
  const r = obtenerReserva(reservaId);
  const yaExisten = db.prepare("SELECT COUNT(*) AS n FROM tareas WHERE reserva_id = ?").get(reservaId).n;
  if (yaExisten) return;
  const ins = db.prepare("INSERT INTO tareas (cabana_id, fecha, tipo, descripcion, reserva_id) VALUES (?, ?, ?, ?, ?)");
  ins.run(r.cabana_id, r.checkin, "check-in", `Recibir a ${r.nombre} (${r.huespedes} pers.) — cobrar saldo $${(r.total - r.sena).toLocaleString("es-AR")}`, r.id);
  ins.run(r.cabana_id, r.checkout, "limpieza", `Limpieza tras salida de ${r.nombre}`, r.id);
}
