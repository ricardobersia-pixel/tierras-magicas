import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

process.env.DATA_DIR = fs.mkdtempSync(path.join(os.tmpdir(), "tm-fin-"));
const { config } = await import("../src/config.js");
const { db } = await import("../src/db.js");
const { crearReserva, cotizar } = await import("../src/reservas.js");
const fin = await import("../src/finanzas.js");
const { registrarReservasOta } = await import("../src/ical.js");
const ajustes = await import("../src/ajustes.js");

const [c1, c2] = config.cabanas;
const MES = "2027-09"; // septiembre 2027: 30 días, temporada Baja casi todo el mes
const dias = 30;

test("ingresos devengados, ocupación, ADR y RevPAR prorratean las noches del mes", () => {
  // 28/09 al 02/10: 3 noches en septiembre y 1 en octubre
  const r = crearReserva({ cabanaId: c1.id, checkin: "2027-09-28", checkout: "2027-10-02", huespedes: 2, nombre: "Cruce de mes", origen: "manual" });
  const m = fin.resumenMes(MES).metricas;
  assert.equal(m.noches_vendidas, 3);
  assert.equal(m.noches_disponibles, config.cabanas.length * dias);
  assert.equal(m.ingresos_devengados, Math.round((r.total * 3) / 4));
  assert.equal(m.adr, Math.round(m.ingresos_devengados / 3));
  assert.equal(m.revpar, Math.round(m.ingresos_devengados / m.noches_disponibles));
});

test("cobros: caja del mes, saldo pendiente y validaciones", () => {
  const r = crearReserva({ cabanaId: c2.id, checkin: "2027-09-05", checkout: "2027-09-08", huespedes: 2, nombre: "Cobro", origen: "manual" });
  fin.registrarPago({ fecha: "2027-09-01", reservaId: r.id, concepto: "sena", medio: "transferencia", monto: r.sena });
  assert.equal(fin.pagadoDe(r.id), r.sena);
  assert.ok(fin.porCobrar().some((x) => x.id === r.id && x.saldo === r.total - r.sena));
  fin.registrarPago({ fecha: "2027-09-05", reservaId: r.id, concepto: "saldo", medio: "efectivo", monto: r.total - r.sena });
  assert.ok(!fin.porCobrar().some((x) => x.id === r.id));
  assert.equal(fin.resumenMes(MES).caja.cobros, r.total);
  assert.throws(() => fin.registrarPago({ reservaId: r.id, concepto: "saldo", medio: "cheque", monto: 10 }), /Medio/);
  assert.throws(() => fin.registrarPago({ reservaId: r.id, concepto: "saldo", medio: "efectivo", monto: -5 }), /monto/);
});

test("gastos mensuales se repiten hasta darlos de baja; equilibrio con la fórmula del plan", () => {
  const g = fin.crearGasto({ fecha: "2027-08-01", categoria: fin.CATEGORIAS_GASTO[3], concepto: "Sueldos", monto: 600000, tipo: "fijo", mensual: true });
  fin.crearGasto({ fecha: "2027-09-10", categoria: fin.CATEGORIAS_GASTO[2], concepto: "Luz", monto: 90000, tipo: "variable" });
  const sept = fin.resumenMes(MES);
  assert.equal(sept.metricas.gastos_fijos, 600000);
  assert.equal(sept.metricas.gastos_variables, 90000);
  const vendidas = sept.metricas.noches_vendidas;
  assert.equal(sept.metricas.costo_noche, Math.round(600000 / sept.metricas.noches_disponibles) + Math.round(90000 / vendidas));
  fin.darDeBajaGasto(g.id, "2027-09");
  assert.equal(fin.resumenMes("2027-10").metricas.gastos_fijos, 0);
  assert.equal(fin.resumenMes("2027-08").metricas.gastos_fijos, 600000);
  const flujo = fin.flujoDeCaja(MES, 3);
  assert.deepEqual(flujo.map((f) => f.mes), ["2027-07", "2027-08", "2027-09"]);
  assert.equal(flujo.at(-1).acumulado, flujo.reduce((s, f) => s + f.neto, 0));
});

test("Airbnb/Booking: registro permanente, monto como cobro, cancelaciones y bloqueos", () => {
  registrarReservasOta(c1.id, "airbnb", [
    { uid: "a1", desde: "2027-09-15", hasta: "2027-09-18", resumen: "Reserved" },
    { uid: "a2", desde: "2027-09-20", hasta: "2027-09-21", resumen: "Airbnb (Not available)" },
  ]);
  const ota = db.prepare("SELECT * FROM reservas_ota WHERE uid = 'a1'").get();
  assert.ok(ota);
  assert.equal(db.prepare("SELECT COUNT(*) AS n FROM reservas_ota WHERE uid = 'a2'").get().n, 0, "los bloqueos de Airbnb no son reservas");
  let m = fin.resumenMes(MES);
  assert.equal(m.metricas.otas_sin_monto, 1);
  fin.actualizarOta(ota.id, { montoNeto: 300000, comision: 45000 });
  m = fin.resumenMes(MES);
  const airbnb = m.por_canal.find((c) => c.canal === "Airbnb");
  assert.equal(airbnb.ingresos, 300000);
  assert.equal(airbnb.comisiones, 45000);
  assert.ok(m.cobros.some((p) => p.ota_id === ota.id && p.monto === 300000 && p.fecha === "2027-09-15"));
  // Si deja de aparecer en el calendario antes de empezar y tenía monto: queda cancelada, no se borra
  registrarReservasOta(c1.id, "airbnb", []);
  assert.equal(db.prepare("SELECT cancelada FROM reservas_ota WHERE id = ?").get(ota.id).cancelada, 1);
  // "No es reserva" sobrevive a la sincronización
  registrarReservasOta(c2.id, "booking", [{ uid: "b1", desde: "2027-09-22", hasta: "2027-09-24", resumen: "CLOSED - Not available" }]);
  const b = db.prepare("SELECT id FROM reservas_ota WHERE uid = 'b1'").get();
  fin.actualizarOta(b.id, { noEsReserva: true });
  registrarReservasOta(c2.id, "booking", [{ uid: "b1", desde: "2027-09-22", hasta: "2027-09-24", resumen: "CLOSED - Not available" }]);
  assert.equal(db.prepare("SELECT cancelada FROM reservas_ota WHERE id = ?").get(b.id).cancelada, 2);
});

test("reporte CSV con resumen, cobros y gastos", () => {
  const csv = fin.reporteCsv(MES);
  assert.ok(csv.startsWith("﻿"));
  assert.match(csv, /Cobros del mes \(caja\)/);
  assert.match(csv, /"Sueldos"/);
});

test("tarifas editables: validación, guardado, vista previa y restablecer", () => {
  const original = ajustes.obtenerTarifas();
  const base = (t) => ({ precio_directo_descuento: t.precio_directo_descuento, dormi: t.dormi, temporadas: t.temporadas, calendario: t.calendario, tarifas: t.tarifas });
  const t = base(structuredClone(original));
  // Superposición de tramos
  const malo = structuredClone(t);
  malo.calendario.push({ desde: "2027-09-10", hasta: "2027-09-12", temporada: "alta", motivo: "choca" });
  assert.throws(() => ajustes.guardarTarifas(malo), /se superpone/);
  // Mínimo mayor que máximo
  const malo2 = structuredClone(t);
  malo2.tarifas[c1.id].baja = { min: 200000, max: 100000 };
  assert.throws(() => ajustes.guardarTarifas(malo2), /mínimo no puede superar/);
  // Vista previa sin guardar
  const nuevo = structuredClone(t);
  nuevo.tarifas[c1.id].baja = { min: 200000, max: 200000 };
  const antes = cotizar(c1, "2027-09-07", "2027-09-08").total;
  const previa = ajustes.conTarifas(nuevo, () => cotizar(c1, "2027-09-07", "2027-09-08").total);
  assert.equal(previa, 180000);
  assert.equal(cotizar(c1, "2027-09-07", "2027-09-08").total, antes, "la vista previa no cambia las tarifas vigentes");
  // Guardar y restablecer
  ajustes.guardarTarifas(nuevo);
  assert.equal(cotizar(c1, "2027-09-07", "2027-09-08").total, 180000);
  assert.equal(ajustes.obtenerTarifas().personalizadas, true);
  ajustes.restablecerTarifas();
  assert.equal(cotizar(c1, "2027-09-07", "2027-09-08").total, antes);
  assert.equal(ajustes.obtenerTarifas().personalizadas, false);
});
