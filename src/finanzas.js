import { db } from "./db.js";
import { config, cabanaPorId } from "./config.js";
import { hoyISO, sumarDias, noches, obtenerReserva, confirmarReserva } from "./reservas.js";

// Cobros, gastos, reservas de Airbnb/Booking con monto y métricas del complejo por mes.
// Ingresos "devengados": lo que corresponde a las noches del mes (prorrateado por noche).
// Caja: el dinero que efectivamente entró (cobros) y salió (gastos) en el mes.

export const CATEGORIAS_GASTO = [
  "Comercialización (Booking, Airbnb)",
  "Comercialización directa (publicidad, pasarelas)",
  "Servicios y energía (electricidad, gas, pellets, leña)",
  "Personal (recepción, limpieza, mantenimiento)",
  "Software y sistemas",
  "Seguros",
  "Limpieza, lavandería e insumos",
  "Mantenimiento y reparaciones",
  "Impuestos y tasas",
  "Otros",
];
export const MEDIOS = ["efectivo", "transferencia", "mercadopago", "plataforma"];
export const CONCEPTOS = ["sena", "saldo", "total", "extra", "ota", "otro"];

const esFecha = (s) => typeof s === "string" && /^\d{4}-\d{2}-\d{2}$/.test(s) && !isNaN(new Date(s + "T12:00:00Z"));
const esMes = (s) => typeof s === "string" && /^\d{4}-(0[1-9]|1[0-2])$/.test(s);
const montoValido = (m) => Number.isInteger(Number(m)) && Number(m) > 0;
const inicioMes = (mes) => `${mes}-01`;
const mesSiguiente = (mes) => {
  const [a, m] = mes.split("-").map(Number);
  return m === 12 ? `${a + 1}-01` : `${a}-${String(m + 1).padStart(2, "0")}`;
};
const mesAnterior = (mes) => {
  const [a, m] = mes.split("-").map(Number);
  return m === 1 ? `${a - 1}-12` : `${a}-${String(m - 1).padStart(2, "0")}`;
};
// Noches de [desde, hasta) que caen dentro del mes
function nochesEnMes(desde, hasta, mes) {
  const ini = inicioMes(mes);
  const fin = inicioMes(mesSiguiente(mes));
  const a = desde > ini ? desde : ini;
  const b = hasta < fin ? hasta : fin;
  return b > a ? noches(a, b) : 0;
}

// ---------- Cobros ----------

export function pagadoDe(reservaId) {
  return db.prepare("SELECT COALESCE(SUM(monto), 0) AS total FROM pagos WHERE reserva_id = ?").get(reservaId).total;
}

export function registrarPago({ fecha, reservaId, otaId, concepto, medio, monto, nota }, usuarioId = null) {
  fecha = fecha || hoyISO();
  if (!esFecha(fecha)) throw new Error("Fecha inválida.");
  if (!CONCEPTOS.includes(concepto)) throw new Error("Concepto inválido.");
  if (!MEDIOS.includes(medio)) throw new Error("Medio de pago inválido.");
  if (!montoValido(monto)) throw new Error("El monto debe ser un número entero mayor a 0.");
  if (reservaId && !obtenerReserva(reservaId)) throw new Error("La reserva no existe.");
  const { lastInsertRowid } = db.prepare(
    "INSERT INTO pagos (fecha, reserva_id, ota_id, concepto, medio, monto, nota, usuario_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
  ).run(fecha, reservaId || null, otaId || null, concepto, medio, Number(monto), nota || null, usuarioId);
  return db.prepare("SELECT * FROM pagos WHERE id = ?").get(lastInsertRowid);
}

export function borrarPago(id) {
  const p = db.prepare("SELECT * FROM pagos WHERE id = ?").get(id);
  if (!p) throw new Error("El cobro no existe.");
  if (p.ota_id) throw new Error("Este cobro sale del monto de la reserva de Airbnb/Booking: cambialo ahí.");
  db.prepare("DELETE FROM pagos WHERE id = ?").run(id);
  return p;
}

// Confirma una reserva y, si se pagó online o por transferencia, registra la seña (o el total) como cobro
export function confirmarConPago(id, { medio, mpPaymentId = null, usuarioId = null } = {}) {
  const antes = obtenerReserva(id);
  const r = confirmarReserva(id, mpPaymentId);
  if (antes && antes.estado === "pendiente_pago" && antes.origen === "web" && medio && !pagadoDe(id)) {
    registrarPago({ reservaId: id, concepto: antes.sena >= antes.total ? "total" : "sena", medio, monto: antes.sena,
      nota: mpPaymentId ? `Mercado Pago ${mpPaymentId}` : "Registrado al confirmar la reserva" }, usuarioId);
  }
  return r;
}

// ---------- Gastos ----------

export function crearGasto({ fecha, categoria, concepto, monto, tipo, mensual, nota }, usuarioId = null) {
  if (!esFecha(fecha)) throw new Error("Fecha inválida.");
  if (!CATEGORIAS_GASTO.includes(categoria)) throw new Error("Elegí una categoría.");
  if (!String(concepto || "").trim()) throw new Error("Escribí el concepto del gasto.");
  if (!montoValido(monto)) throw new Error("El monto debe ser un número entero mayor a 0.");
  if (!["fijo", "variable"].includes(tipo)) throw new Error("El tipo debe ser fijo o variable.");
  const { lastInsertRowid } = db.prepare(
    "INSERT INTO gastos (fecha, categoria, concepto, monto, tipo, mensual, nota, usuario_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
  ).run(fecha, categoria, String(concepto).trim(), Number(monto), tipo, mensual ? 1 : 0, nota || null, usuarioId);
  return db.prepare("SELECT * FROM gastos WHERE id = ?").get(lastInsertRowid);
}

// Un gasto mensual deja de repetirse desde el mes siguiente a "hasta"
export function darDeBajaGasto(id, hasta) {
  const g = db.prepare("SELECT * FROM gastos WHERE id = ?").get(id);
  if (!g || !g.mensual) throw new Error("Solo se dan de baja los gastos mensuales.");
  if (!esMes(hasta) || hasta < g.fecha.slice(0, 7)) throw new Error("Mes de baja inválido.");
  db.prepare("UPDATE gastos SET hasta = ? WHERE id = ?").run(hasta, id);
  return db.prepare("SELECT * FROM gastos WHERE id = ?").get(id);
}

export function borrarGasto(id) {
  const g = db.prepare("SELECT * FROM gastos WHERE id = ?").get(id);
  if (!g) throw new Error("El gasto no existe.");
  db.prepare("DELETE FROM gastos WHERE id = ?").run(id);
  return g;
}

function gastosDelMes(mes) {
  return db.prepare(
    `SELECT * FROM gastos WHERE (mensual = 0 AND substr(fecha, 1, 7) = ?)
       OR (mensual = 1 AND substr(fecha, 1, 7) <= ? AND (hasta IS NULL OR hasta >= ?)) ORDER BY fecha, id`
  ).all(mes, mes, mes);
}

// ---------- Airbnb / Booking ----------

// El monto neto se registra como cobro de la plataforma en la fecha de ingreso (cuando suelen depositar)
export function actualizarOta(id, { montoNeto, comision, noEsReserva }, usuarioId = null) {
  const o = db.prepare("SELECT * FROM reservas_ota WHERE id = ?").get(id);
  if (!o) throw new Error("La reserva de la plataforma no existe.");
  if (noEsReserva) {
    db.prepare("UPDATE reservas_ota SET cancelada = 2 WHERE id = ?").run(id);
    db.prepare("DELETE FROM pagos WHERE ota_id = ?").run(id);
    return db.prepare("SELECT * FROM reservas_ota WHERE id = ?").get(id);
  }
  const neto = montoNeto === "" || montoNeto == null ? null : Number(montoNeto);
  const com = comision === "" || comision == null ? null : Number(comision);
  if (neto !== null && !montoValido(neto)) throw new Error("El monto neto debe ser un número entero mayor a 0.");
  if (com !== null && !(Number.isInteger(com) && com >= 0)) throw new Error("La comisión debe ser un número entero.");
  db.prepare("UPDATE reservas_ota SET monto_neto = ?, comision = ?, cancelada = CASE WHEN cancelada = 2 THEN 0 ELSE cancelada END WHERE id = ?").run(neto, com, id);
  db.prepare("DELETE FROM pagos WHERE ota_id = ?").run(id);
  if (neto) {
    registrarPago({ fecha: o.desde, otaId: id, concepto: "ota", medio: "plataforma", monto: neto,
      nota: `${o.origen === "airbnb" ? "Airbnb" : "Booking"} · ${cabanaPorId(o.cabana_id)?.nombre || o.cabana_id}` }, usuarioId);
  }
  return db.prepare("SELECT * FROM reservas_ota WHERE id = ?").get(id);
}

// ---------- Métricas ----------

const diasDelMes = (mes) => noches(inicioMes(mes), inicioMes(mesSiguiente(mes)));
const canalDe = (origen) => (origen === "airbnb" ? "Airbnb" : origen === "booking" ? "Booking" : "Directo");

function resumenCaja(mes) {
  const cobros = db.prepare("SELECT COALESCE(SUM(monto), 0) AS t FROM pagos WHERE substr(fecha, 1, 7) = ?").get(mes).t;
  const gastos = gastosDelMes(mes).reduce((s, g) => s + g.monto, 0);
  return { cobros, gastos, neto: cobros - gastos };
}

export function resumenMes(mes) {
  if (!esMes(mes)) throw new Error("Mes inválido (AAAA-MM).");
  const ini = inicioMes(mes);
  const fin = inicioMes(mesSiguiente(mes));
  const dias = diasDelMes(mes);
  const disponibles = config.cabanas.length * dias;

  const porCabana = Object.fromEntries(config.cabanas.map((c) => [c.id, { cabana: c.nombre, noches: 0, ingresos: 0 }]));
  const porCanal = {};
  const sumar = (cabanaId, canal, n, ingreso) => {
    if (porCabana[cabanaId]) {
      porCabana[cabanaId].noches += n;
      porCabana[cabanaId].ingresos += ingreso;
    }
    porCanal[canal] = porCanal[canal] || { canal, noches: 0, ingresos: 0, comisiones: 0, reservas: 0 };
    porCanal[canal].noches += n;
    porCanal[canal].ingresos += ingreso;
    porCanal[canal].reservas += 1;
  };

  const reservas = db.prepare("SELECT * FROM reservas WHERE estado = 'confirmada' AND checkin < ? AND checkout > ?").all(fin, ini);
  for (const r of reservas) {
    const n = nochesEnMes(r.checkin, r.checkout, mes);
    sumar(r.cabana_id, "Directo", n, Math.round((r.total * n) / noches(r.checkin, r.checkout)));
  }
  const otas = db.prepare("SELECT * FROM reservas_ota WHERE cancelada = 0 AND desde < ? AND hasta > ?").all(fin, ini);
  let otasSinMonto = 0;
  for (const o of otas) {
    const n = nochesEnMes(o.desde, o.hasta, mes);
    const total = noches(o.desde, o.hasta);
    sumar(o.cabana_id, canalDe(o.origen), n, o.monto_neto ? Math.round((o.monto_neto * n) / total) : 0);
    if (o.comision) porCanal[canalDe(o.origen)].comisiones += Math.round((o.comision * n) / total);
    if (o.monto_neto == null) otasSinMonto++;
  }

  const vendidas = Object.values(porCabana).reduce((s, c) => s + c.noches, 0);
  const ingresos = Object.values(porCabana).reduce((s, c) => s + c.ingresos, 0);
  const listaGastos = gastosDelMes(mes);
  const fijos = listaGastos.filter((g) => g.tipo === "fijo").reduce((s, g) => s + g.monto, 0);
  const variables = listaGastos.filter((g) => g.tipo === "variable").reduce((s, g) => s + g.monto, 0);
  const adr = vendidas ? Math.round(ingresos / vendidas) : 0;
  const variablePorNoche = vendidas ? Math.round(variables / vendidas) : 0;
  const margenPorNoche = adr - variablePorNoche;

  const cobros = db.prepare(
    `SELECT p.*, r.nombre AS huesped, r.cabana_id FROM pagos p LEFT JOIN reservas r ON r.id = p.reserva_id
     WHERE substr(p.fecha, 1, 7) = ? ORDER BY p.fecha, p.id`
  ).all(mes);

  return {
    mes,
    dias,
    caja: resumenCaja(mes),
    metricas: {
      noches_disponibles: disponibles,
      noches_vendidas: vendidas,
      ocupacion: disponibles ? Math.round((vendidas * 1000) / disponibles) / 10 : 0,
      ingresos_devengados: ingresos,
      adr,
      revpar: disponibles ? Math.round(ingresos / disponibles) : 0,
      gastos_fijos: fijos,
      gastos_variables: variables,
      resultado_devengado: ingresos - fijos - variables,
      // Fórmula del plan: costo por noche = fijos / (cabañas × días) + variables por noche ocupada
      costo_noche: Math.round(fijos / disponibles) + variablePorNoche,
      ocupacion_equilibrio: margenPorNoche > 0 ? Math.round((fijos * 1000) / (margenPorNoche * disponibles)) / 10 : null,
      otas_sin_monto: otasSinMonto,
    },
    por_cabana: Object.values(porCabana).map((c) => ({ ...c, ocupacion: dias ? Math.round((c.noches * 1000) / dias) / 10 : 0 })),
    por_canal: Object.values(porCanal).sort((a, b) => b.ingresos - a.ingresos),
    cobros,
    cobros_por_medio: Object.fromEntries(MEDIOS.map((m) => [m, cobros.filter((p) => p.medio === m).reduce((s, p) => s + p.monto, 0)])),
    gastos: listaGastos,
    gastos_por_categoria: CATEGORIAS_GASTO.map((c) => ({ categoria: c, monto: listaGastos.filter((g) => g.categoria === c).reduce((s, g) => s + g.monto, 0) })).filter((g) => g.monto),
    otas: db.prepare("SELECT * FROM reservas_ota WHERE cancelada != 1 AND desde < ? AND hasta > ? ORDER BY desde").all(fin, ini)
      .map((o) => ({ ...o, cabana: cabanaPorId(o.cabana_id)?.nombre || o.cabana_id })),
  };
}

// Flujo de caja de los últimos meses (hasta el mes indicado, incluido)
export function flujoDeCaja(hastaMes, meses = 12) {
  let mes = hastaMes;
  const filas = [];
  for (let i = 0; i < meses; i++) {
    filas.unshift({ mes, ...resumenCaja(mes) });
    mes = mesAnterior(mes);
  }
  let acumulado = 0;
  return filas.map((f) => ({ ...f, acumulado: (acumulado += f.neto) }));
}

// Reservas confirmadas que todavía deben saldo
export function porCobrar() {
  return db.prepare(
    `SELECT r.id, r.cabana_id, r.nombre, r.checkin, r.checkout, r.total,
       COALESCE((SELECT SUM(monto) FROM pagos p WHERE p.reserva_id = r.id), 0) AS pagado
     FROM reservas r WHERE r.estado = 'confirmada' AND r.checkout >= ? ORDER BY r.checkin`
  ).all(sumarDias(hoyISO(), -60)).filter((r) => r.total > r.pagado).map((r) => ({ ...r, saldo: r.total - r.pagado, cabana: cabanaPorId(r.cabana_id)?.nombre || r.cabana_id }));
}

// Reporte mensual para el contador (CSV separado por punto y coma, abre directo en Excel)
export function reporteCsv(mes) {
  const r = resumenMes(mes);
  const celda = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const fila = (...v) => v.map(celda).join(";");
  const lineas = [
    fila(`Tierras Mágicas · Reporte ${mes}`),
    "",
    fila("Resumen", "Monto"),
    fila("Cobros del mes (caja)", r.caja.cobros),
    fila("Gastos del mes", r.caja.gastos),
    fila("Resultado de caja", r.caja.neto),
    fila("Ingresos devengados (noches del mes)", r.metricas.ingresos_devengados),
    fila("Ocupación %", r.metricas.ocupacion),
    fila("Tarifa promedio por noche (ADR)", r.metricas.adr),
    fila("RevPAR", r.metricas.revpar),
    "",
    fila("Cobros"),
    fila("Fecha", "Concepto", "Medio", "Reserva", "Huésped", "Monto", "Nota"),
    ...r.cobros.map((p) => fila(p.fecha, p.concepto, p.medio, p.reserva_id || "", p.huesped || "", p.monto, p.nota || "")),
    "",
    fila("Gastos"),
    fila("Fecha", "Categoría", "Concepto", "Tipo", "Mensual", "Monto"),
    ...r.gastos.map((g) => fila(g.mensual ? `${mes} (mensual)` : g.fecha, g.categoria, g.concepto, g.tipo, g.mensual ? "sí" : "no", g.monto)),
    "",
    fila("Por canal"),
    fila("Canal", "Reservas", "Noches", "Ingresos", "Comisiones"),
    ...r.por_canal.map((c) => fila(c.canal, c.reservas, c.noches, c.ingresos, c.comisiones)),
  ];
  return "\uFEFF" + lineas.join("\r\n");
}
