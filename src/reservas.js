import crypto from "node:crypto";
import { db } from "./db.js";
import { config, env, cabanaPorId } from "./config.js";

// Con Mercado Pago, una reserva web sin pagar retiene las fechas durante este tiempo.
// Sin Mercado Pago (modo demo) la solicitud retiene las fechas hasta que el dueño la confirma o cancela.
// Por transferencia, retiene las fechas durante negocio.retencion_transferencia_horas.
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

function temporada(fechaISO) {
  const md = fechaISO.slice(5); // MM-DD
  for (const t of config.temporadas || []) {
    const dentro = t.desde <= t.hasta ? md >= t.desde && md <= t.hasta : md >= t.desde || md <= t.hasta;
    if (dentro) return t.id;
  }
  return "baja";
}

// Precio de una noche según temporada y cantidad de huéspedes, en la moneda de la tarifa
function tarifaNoche(cabana, fechaISO, huespedes) {
  const tarifas = cabana.tarifas[temporada(fechaISO)] || cabana.tarifas.baja;
  const escala = tarifas.por_ocupacion.find((e) => huespedes <= e.hasta) || tarifas.por_ocupacion.at(-1);
  return { moneda: tarifas.moneda, precio: escala.precio };
}

export function aPesos({ moneda, precio }) {
  return moneda === "USD" ? Math.round(precio * config.negocio.tipo_cambio_usd) : precio;
}

// Precio de referencia por noche para mostrar ("desde")
export function preciosReferencia(cabana) {
  return Object.fromEntries(
    Object.entries(cabana.tarifas).map(([t, v]) => [t, { moneda: v.moneda, desde: v.por_ocupacion[0].precio, hasta: v.por_ocupacion.at(-1).precio }])
  );
}

export function cotizar(cabana, checkin, checkout, huespedes) {
  let total = 0;
  let totalUsd = 0;
  const nochesPor = { alta: 0, baja: 0 };
  for (let f = checkin; f < checkout; f = sumarDias(f, 1)) {
    const t = tarifaNoche(cabana, f, huespedes);
    total += aPesos(t);
    if (t.moneda === "USD") totalUsd += t.precio;
    nochesPor[temporada(f) === "baja" ? "baja" : "alta"]++;
  }
  const sena = Math.round((total * config.negocio.sena_porcentaje) / 100);
  return { noches: noches(checkin, checkout), total, sena, saldo: total - sena, total_usd: totalUsd || null, noches_alta: nochesPor.alta, noches_baja: nochesPor.baja };
}

// Devuelve los rangos ocupados de una cabaña (reservas activas + bloqueos importados/manuales)
export function ocupaciones(cabanaId, excluirReservaId = null) {
  const reservas = db
    .prepare(
      `SELECT id, checkin AS desde, checkout AS hasta, estado, nombre, 'web' AS origen FROM reservas
       WHERE cabana_id = ? AND (estado = 'confirmada'
         OR (estado = 'pendiente_pago' AND (origen = 'manual'
           OR (metodo_pago = 'transferencia' AND creada > datetime('now', ?))
           OR (metodo_pago = 'mercadopago' AND (? OR creada > datetime('now', ?))))))`
    )
    .all(cabanaId, `-${config.negocio.retencion_transferencia_horas || 48} hours`, env.mpAccessToken ? 0 : 1, `-${RETENCION_PENDIENTE_MIN} minutes`)
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

export function crearReserva({ cabanaId, checkin, checkout, huespedes, nombre, email, telefono, notas, origen = "web", metodoPago = "mercadopago", modalidad = "sena" }) {
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
  if (!["mercadopago", "transferencia"].includes(metodoPago)) throw new Error("Medio de pago inválido.");
  if (modalidad === "total" && !config.negocio.permite_pago_total) modalidad = "sena";
  const cot = cotizar(cabana, checkin, checkout, huespedes);
  const total = cot.total;
  const sena = modalidad === "total" ? cot.total : cot.sena; // monto a pagar ahora

  // Verificación + inserción atómica para evitar doble reserva
  db.exec("BEGIN IMMEDIATE");
  try {
    if (!estaLibre(cabanaId, checkin, checkout)) throw new Error("Las fechas elegidas ya no están disponibles.");
    db.prepare(
      `INSERT INTO reservas (id, cabana_id, checkin, checkout, huespedes, nombre, email, telefono, total, sena, estado, origen, notas, metodo_pago, modalidad)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).run(id, cabanaId, checkin, checkout, huespedes, nombre.trim(), email || null, telefono || null, total, sena,
      origen === "manual" ? "confirmada" : "pendiente_pago", origen, notas || null, origen === "manual" ? null : metodoPago, modalidad);
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

// Mueve una reserva a otras fechas/cabaña conservando lo abonado.
// Si el nuevo período cuesta más (p. ej. de temporada baja a alta) se suma la diferencia al saldo;
// si cuesta menos, el total queda igual a lo pactado (no hay devolución).
export function reprogramarReserva(id, { cabanaId, checkin, checkout }) {
  const r = obtenerReserva(id);
  if (!r || r.estado === "cancelada") throw new Error("Reserva inexistente o cancelada.");
  cabanaId = cabanaId || r.cabana_id;
  const cabana = cabanaPorId(cabanaId);
  if (!cabana) throw new Error("Cabaña inexistente.");
  const error = validarRango(checkin, checkout);
  if (error) throw new Error(error);
  if (r.huespedes > cabana.capacidad) throw new Error(`Capacidad máxima de ${cabana.nombre}: ${cabana.capacidad} personas.`);
  db.exec("BEGIN IMMEDIATE");
  try {
    if (!estaLibre(cabanaId, checkin, checkout, id)) throw new Error("Las nuevas fechas no están disponibles.");
    const nuevoPrecio = cotizar(cabana, checkin, checkout, r.huespedes).total;
    const diferencia = Math.max(0, nuevoPrecio - r.total);
    const nota = `Reprogramada desde ${r.checkin}→${r.checkout} (${r.cabana_id}) el ${hoyISO()}` +
      (diferencia ? `; diferencia a cobrar $${diferencia.toLocaleString("es-AR")}.` : "; sin diferencia.");
    db.prepare("UPDATE reservas SET cabana_id = ?, checkin = ?, checkout = ?, total = ?, notas = TRIM(COALESCE(notas, '') || ' ' || ?) WHERE id = ?")
      .run(cabanaId, checkin, checkout, r.total + diferencia, nota, id);
    db.prepare("DELETE FROM tareas WHERE reserva_id = ? AND hecha = 0").run(id);
    db.exec("COMMIT");
  } catch (e) {
    db.exec("ROLLBACK");
    throw e;
  }
  if (obtenerReserva(id).estado === "confirmada") generarTareas(id, true);
  return { ...obtenerReserva(id), diferencia: obtenerReserva(id).total - r.total };
}

export function cancelarReserva(id) {
  db.prepare("UPDATE reservas SET estado = 'cancelada' WHERE id = ?").run(id);
  db.prepare("DELETE FROM tareas WHERE reserva_id = ? AND hecha = 0").run(id);
}

function generarTareas(reservaId, forzar = false) {
  const r = obtenerReserva(reservaId);
  const yaExisten = db.prepare("SELECT COUNT(*) AS n FROM tareas WHERE reserva_id = ? AND hecha = 0").get(reservaId).n;
  if (yaExisten && !forzar) return;
  const ins = db.prepare("INSERT INTO tareas (cabana_id, fecha, tipo, descripcion, reserva_id) VALUES (?, ?, ?, ?, ?)");
  const saldo = r.total - r.sena;
  ins.run(r.cabana_id, r.checkin, "check-in", `Recibir a ${r.nombre} (${r.huespedes} pers.) — ${saldo > 0 ? `cobrar saldo $${saldo.toLocaleString("es-AR")}` : "pagado en su totalidad"}`, r.id);
  ins.run(r.cabana_id, r.checkout, "limpieza", `Limpieza tras salida de ${r.nombre}`, r.id);
}
