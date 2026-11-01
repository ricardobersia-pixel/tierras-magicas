import { test, before } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

// Base de datos temporal: se configura antes de importar los módulos que la abren
process.env.DATA_DIR = fs.mkdtempSync(path.join(os.tmpdir(), "tm-test-"));
const { config } = await import("../src/config.js");
const { cotizar, noches, sumarDias, crearReserva, estaLibre, validarRango } = await import("../src/reservas.js");

const cabana = config.cabanas[0];
const precioBaja = (huespedes) => cabana.tarifas.baja.por_ocupacion.find((e) => huespedes <= e.hasta).precio;
// Fechas futuras en temporada baja (mayo)
const anio = new Date().getFullYear() + 1;
const MAYO = (d) => `${anio}-05-${String(d).padStart(2, "0")}`;

before(() => assert.ok(config.cabanas.length > 0));

test("sumarDias y noches cruzan fin de mes y de año", () => {
  assert.equal(sumarDias("2026-12-30", 3), "2027-01-02");
  assert.equal(noches("2026-12-30", "2027-01-02"), 3);
});

test("cotización en temporada baja con seña", () => {
  const c = cotizar(cabana, MAYO(10), MAYO(12), 2);
  assert.equal(c.noches, 2);
  assert.equal(c.total, 2 * precioBaja(2));
  assert.equal(c.sena, Math.round((c.total * config.negocio.sena_porcentaje) / 100));
  assert.equal(c.sena + c.saldo, c.total);
  assert.equal(c.noches_baja, 2);
});

test("temporada alta en USD se cobra en pesos al tipo de cambio", () => {
  const alta = cabana.tarifas.alta.por_ocupacion.at(-1).precio;
  const c = cotizar(cabana, `${anio}-01-10`, `${anio}-01-12`, 2);
  assert.equal(c.total_usd, 2 * alta);
  assert.equal(c.total, 2 * Math.round(alta * config.negocio.tipo_cambio_usd));
  assert.equal(c.noches_alta, 2);
});

test("validación de fechas", () => {
  assert.match(validarRango("2020-01-01", "2020-01-03"), /ya pasó/);
  assert.match(validarRango(MAYO(12), MAYO(10)), /posterior/);
  assert.match(validarRango("x", MAYO(10)), /inválidas/);
  assert.equal(validarRango(MAYO(10), MAYO(12)), null);
});

test("no permite doble reserva en fechas superpuestas", () => {
  const datos = { cabanaId: cabana.id, huespedes: 2, nombre: "Prueba", email: "p@ejemplo.com", telefono: "2990000000", metodoPago: "transferencia" };
  const r = crearReserva({ ...datos, checkin: MAYO(20), checkout: MAYO(23) });
  assert.equal(r.estado, "pendiente_pago");
  assert.equal(estaLibre(cabana.id, MAYO(21), MAYO(22)), false);
  assert.throws(() => crearReserva({ ...datos, checkin: MAYO(22), checkout: MAYO(25) }), /ya no están disponibles/);
  // El día de salida queda libre para otro ingreso
  assert.ok(crearReserva({ ...datos, checkin: MAYO(23), checkout: MAYO(25) }));
});

test("respeta la capacidad y el mínimo de noches", () => {
  const datos = { cabanaId: cabana.id, nombre: "Prueba", metodoPago: "transferencia" };
  assert.throws(() => crearReserva({ ...datos, huespedes: cabana.capacidad + 1, checkin: MAYO(1), checkout: MAYO(4) }), /Capacidad/);
  if (cabana.minimo_noches > 1) {
    assert.throws(() => crearReserva({ ...datos, huespedes: 2, checkin: MAYO(1), checkout: MAYO(2) }), /mínimo/);
  }
});
