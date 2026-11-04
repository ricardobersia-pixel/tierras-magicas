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

// Tramo del calendario de una noche (fecha de ingreso de esa noche). Fuera del calendario: temporada_sin_calendario.
export function tramoCalendario(fechaISO) {
  return (config.calendario || []).find((t) => fechaISO >= t.desde && fechaISO <= t.hasta) ||
    { temporada: config.negocio.temporada_sin_calendario || "media", motivo: "Fuera del calendario cargado" };
}

export function temporada(fechaISO) {
  return tramoCalendario(fechaISO).temporada;
}

const datosTemporada = (id) => config.temporadas[id];
const redondearMil = (n) => Math.round(n / 1000) * 1000;

// Precio directo de una noche: mínimo del rango de domingo a jueves, máximo viernes y sábado,
// menos el descuento por venta directa (las tarifas cargadas son las de Booking/Airbnb).
function tarifaNoche(cabana, fechaISO) {
  const rango = cabana.tarifas[temporada(fechaISO)];
  const dia = new Date(fechaISO + "T12:00:00Z").getUTCDay(); // 5 = viernes, 6 = sábado
  const ota = dia === 5 || dia === 6 ? rango.max : rango.min;
  return redondearMil(ota * (1 - (config.negocio.precio_directo_descuento || 0) / 100));
}

// Mínimo de noches de una estadía: el mayor entre la cabaña y cada noche (temporada o tramo especial, p. ej. Fin de Año)
export function minimoNoches(cabana, checkin, checkout) {
  let minimo = cabana.minimo_noches || 1;
  for (let f = checkin; f < checkout; f = sumarDias(f, 1)) {
    const tramo = tramoCalendario(f);
    minimo = Math.max(minimo, tramo.minimo_noches || datosTemporada(tramo.temporada).minimo_noches || 1);
  }
  return minimo;
}

// Precio de referencia por noche y temporada para mostrar (directo, de domingo a jueves y fin de semana)
export function preciosReferencia(cabana) {
  const directo = (n) => redondearMil(n * (1 - (config.negocio.precio_directo_descuento || 0) / 100));
  return Object.entries(cabana.tarifas)
    .sort(([a], [b]) => datosTemporada(a).orden - datosTemporada(b).orden)
    .map(([id, r]) => ({ temporada: id, nombre: datosTemporada(id).nombre, semana: directo(r.min), finde: directo(r.max) }));
}

// La temporada más alta de la estadía define la seña y la política (p. ej. una noche en Alta Premium: 100% anticipado)
export function cotizar(cabana, checkin, checkout, huespedes = 1) {
  const n = noches(checkin, checkout);
  let total = 0;
  const nochesPor = {};
  let principal = null;
  for (let f = checkin; f < checkout; f = sumarDias(f, 1)) {
    const t = temporada(f);
    const descuento = datosTemporada(t).descuento;
    const precio = tarifaNoche(cabana, f);
    total += descuento && n >= descuento.desde_noches ? redondearMil(precio * (1 - descuento.porcentaje / 100)) : precio;
    nochesPor[t] = (nochesPor[t] || 0) + 1;
    if (!principal || datosTemporada(t).orden > datosTemporada(principal).orden) principal = t;
  }
  // Dormi: precio fijo por persona y por noche, sin descuentos de temporada
  const adicionales = adicionalesDe(cabana, huespedes);
  const totalAdicionales = adicionales * n * (config.negocio.dormi?.precio_persona_noche || 0);
  total += totalAdicionales;
  const senaPorcentaje = datosTemporada(principal).sena_porcentaje;
  const sena = Math.round((total * senaPorcentaje) / 100);
  return {
    noches: n, total, sena, saldo: total - sena, sena_porcentaje: senaPorcentaje,
    temporada: principal, temporada_nombre: datosTemporada(principal).nombre, politica: datosTemporada(principal).politica,
    noches_por_temporada: nochesPor, minimo_noches: minimoNoches(cabana, checkin, checkout),
    adicionales, total_adicionales: totalAdicionales,
  };
}

// Devuelve los rangos ocupados de una cabaña (reservas activas + bloqueos importados/manuales)
// Reservas que retienen fechas: confirmadas, o pendientes dentro del plazo de pago
function reservasActivas(condicion, valor, excluirReservaId) {
  return db
    .prepare(
      `SELECT id, checkin AS desde, checkout AS hasta, estado, nombre, adicionales, 'web' AS origen FROM reservas
       WHERE ${condicion} AND (estado = 'confirmada'
         OR (estado = 'pendiente_pago' AND (origen = 'manual'
           OR (metodo_pago = 'transferencia' AND creada > datetime('now', ?))
           OR (metodo_pago = 'mercadopago' AND (? OR creada > datetime('now', ?))))))`
    )
    .all(valor, `-${config.negocio.retencion_transferencia_horas || 48} hours`, env.mpAccessToken ? 0 : 1, `-${RETENCION_PENDIENTE_MIN} minutes`)
    .filter((r) => r.id !== excluirReservaId);
}

export function ocupaciones(cabanaId, excluirReservaId = null) {
  const bloqueos = db.prepare(`SELECT desde, hasta, origen, resumen FROM bloqueos WHERE cabana_id = ?`).all(cabanaId);
  return [...reservasActivas("cabana_id = ?", cabanaId, excluirReservaId), ...bloqueos];
}

// El dormi es uno solo y lo usa una reserva a la vez
export function ocupacionesDormi(excluirReservaId = null) {
  return reservasActivas("adicionales > ?", 0, excluirReservaId);
}

export function dormiLibre(checkin, checkout, excluirReservaId = null) {
  return !ocupacionesDormi(excluirReservaId).some((o) => checkin < o.hasta && o.desde < checkout);
}

// Personas que van al dormi: las que exceden la capacidad de la cabaña
export const adicionalesDe = (cabana, huespedes) => Math.max(0, Number(huespedes) - cabana.capacidad);
const capacidadMaxima = (cabana) => cabana.capacidad + (config.negocio.dormi?.plazas || 0);

export function estaLibre(cabanaId, checkin, checkout, excluirReservaId = null) {
  return !ocupaciones(cabanaId, excluirReservaId).some((o) => checkin < o.hasta && o.desde < checkout);
}

// Para el panel: con qué choca una reserva (fechas y de quién). Al público no se le muestran nombres.
function detalleOcupada(cabana, checkin, checkout, excluirReservaId) {
  const o = ocupaciones(cabana.id, excluirReservaId).find((x) => checkin < x.hasta && x.desde < checkout);
  const quien = o.nombre ? `reserva de ${o.nombre}` : o.origen === "manual" ? `bloqueo: ${o.resumen || "manual"}` : `reserva de ${o.origen === "airbnb" ? "Airbnb" : "Booking"}`;
  const corta = (f) => new Date(f + "T12:00:00Z").toLocaleDateString("es-AR", { day: "numeric", month: "short", timeZone: "UTC" });
  return `${cabana.nombre} ya está ocupada del ${corta(o.desde)} al ${corta(o.hasta)} (${quien}).`;
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
      .filter((c) => capacidadMaxima(c) >= huespedes)
      .map((c) => {
        const libre = estaLibre(c.id, checkin, checkout);
        const cotizacion = cotizar(c, checkin, checkout, huespedes);
        const dormiOk = !cotizacion.adicionales || dormiLibre(checkin, checkout);
        const cumpleMinimo = n >= cotizacion.minimo_noches;
        return {
          id: c.id,
          nombre: c.nombre,
          capacidad: c.capacidad,
          disponible: libre && dormiOk && cumpleMinimo,
          motivo: !libre ? "ocupada" : !dormiOk ? "el dormi para las personas adicionales está ocupado" : !cumpleMinimo ? `mínimo ${cotizacion.minimo_noches} noches` : null,
          ...cotizacion,
        };
      }),
  };
}

// De dónde llegan las reservas directas. Booking y Airbnb entran por su calendario (no se cargan a mano: chocarían con su bloqueo).
export const CANALES = { web: "Web", whatsapp: "WhatsApp", instagram: "Instagram", facebook: "Facebook", telefono: "Teléfono", email: "Email", presencial: "Presencial", otro: "Otro" };

export function crearReserva({ cabanaId, checkin, checkout, huespedes, nombre, email, telefono, notas, origen = "web", metodoPago = "mercadopago", modalidad = "sena", canal }) {
  canal = origen === "web" ? "web" : CANALES[canal] ? canal : "whatsapp";
  const cabana = cabanaPorId(cabanaId);
  if (!cabana) throw new Error("Cabaña inexistente.");
  const error = validarRango(checkin, checkout);
  if (error) throw new Error(error);
  huespedes = Number(huespedes);
  if (!(huespedes >= 1 && huespedes <= capacidadMaxima(cabana))) {
    throw new Error(`Capacidad máxima: ${cabana.capacidad} personas${config.negocio.dormi ? ` más ${config.negocio.dormi.plazas} en el dormi` : ""}.`);
  }
  const adicionales = adicionalesDe(cabana, huespedes);
  const minimo = minimoNoches(cabana, checkin, checkout);
  if (origen === "web" && noches(checkin, checkout) < minimo)
    throw new Error(`Para esas fechas el mínimo es de ${minimo} noches.`);
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
    if (!estaLibre(cabanaId, checkin, checkout)) {
      throw new Error(origen === "manual" ? detalleOcupada(cabana, checkin, checkout) : "Las fechas elegidas ya no están disponibles.");
    }
    if (adicionales && !dormiLibre(checkin, checkout)) throw new Error("El dormi para las personas adicionales ya está ocupado en esas fechas.");
    db.prepare(
      `INSERT INTO reservas (id, cabana_id, checkin, checkout, huespedes, nombre, email, telefono, total, sena, estado, origen, notas, metodo_pago, modalidad, adicionales, canal)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).run(id, cabanaId, checkin, checkout, huespedes, nombre.trim(), email || null, telefono || null, total, sena,
      origen === "manual" ? "confirmada" : "pendiente_pago", origen, notas || null, origen === "manual" ? null : metodoPago, modalidad, adicionales, canal);
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
  if (r.huespedes > capacidadMaxima(cabana)) throw new Error(`Capacidad máxima de ${cabana.nombre}: ${capacidadMaxima(cabana)} personas con el dormi.`);
  const adicionales = adicionalesDe(cabana, r.huespedes);
  db.exec("BEGIN IMMEDIATE");
  try {
    if (!estaLibre(cabanaId, checkin, checkout, id)) throw new Error(detalleOcupada(cabana, checkin, checkout, id));
    if (adicionales && !dormiLibre(checkin, checkout, id)) throw new Error("El dormi para las personas adicionales está ocupado en las nuevas fechas.");
    const nuevoPrecio = cotizar(cabana, checkin, checkout, r.huespedes).total;
    const diferencia = Math.max(0, nuevoPrecio - r.total);
    const nota = `Reprogramada desde ${r.checkin}→${r.checkout} (${r.cabana_id}) el ${hoyISO()}` +
      (diferencia ? `; diferencia a cobrar $${diferencia.toLocaleString("es-AR")}.` : "; sin diferencia.");
    db.prepare("UPDATE reservas SET cabana_id = ?, checkin = ?, checkout = ?, total = ?, adicionales = ?, notas = TRIM(COALESCE(notas, '') || ' ' || ?) WHERE id = ?")
      .run(cabanaId, checkin, checkout, r.total + diferencia, adicionales, nota, id);
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
  const dormi = r.adicionales ? `, ${r.adicionales} en el dormi` : "";
  ins.run(r.cabana_id, r.checkin, "check-in", `Recibir a ${r.nombre} (${r.huespedes} pers.${dormi}) — ${saldo > 0 ? `cobrar saldo $${saldo.toLocaleString("es-AR")}` : "pagado en su totalidad"}`, r.id);
  ins.run(r.cabana_id, r.checkout, "limpieza", `Limpieza tras salida de ${r.nombre}${r.adicionales ? " (incluye el dormi)" : ""}`, r.id);
}
