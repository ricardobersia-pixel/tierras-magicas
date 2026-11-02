import { test, before } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

// Base de datos temporal: se configura antes de importar los módulos que la abren
process.env.DATA_DIR = fs.mkdtempSync(path.join(os.tmpdir(), "tm-test-"));
const { config } = await import("../src/config.js");
const { cotizar, noches, sumarDias, crearReserva, estaLibre, validarRango } = await import("../src/reservas.js");

const { tramoCalendario, minimoNoches, dormiLibre, reprogramarReserva } = await import("../src/reservas.js");

const cabana = config.cabanas[0];
// Precio directo de una noche: tarifa de Booking/Airbnb (mín. dom–jue, máx. vie–sáb) menos el descuento directo
const directo = (n) => Math.round((n * (1 - config.negocio.precio_directo_descuento / 100)) / 1000) * 1000;
// Fechas de prueba en temporada Baja de 2027 (calendario cargado): 12/05 es miércoles
const MAYO = (d) => `2027-05-${String(d).padStart(2, "0")}`;
const SEPT = (d) => `2027-09-${String(d).padStart(2, "0")}`;

before(() => assert.ok(config.cabanas.length > 0));

test("sumarDias y noches cruzan fin de mes y de año", () => {
  assert.equal(sumarDias("2026-12-30", 3), "2027-01-02");
  assert.equal(noches("2026-12-30", "2027-01-02"), 3);
});

test("el calendario cubre cada día de 2026 y 2027 una sola vez, con temporadas existentes", () => {
  for (let f = "2026-01-01"; f <= "2027-12-31"; f = sumarDias(f, 1)) {
    const tramos = config.calendario.filter((t) => f >= t.desde && f <= t.hasta);
    assert.equal(tramos.length, 1, `${f}: ${tramos.length} tramos`);
    assert.ok(config.temporadas[tramos[0].temporada], `${f}: temporada ${tramos[0].temporada}`);
  }
  assert.equal(tramoCalendario("2028-03-01").temporada, config.negocio.temporada_sin_calendario);
});

test("días de semana al mínimo del rango y viernes/sábado al máximo, con descuento directo", () => {
  const t = cabana.tarifas.baja;
  const semana = cotizar(cabana, MAYO(12), MAYO(14)); // mié y jue
  assert.equal(semana.total, 2 * directo(t.min));
  assert.equal(semana.temporada, "baja");
  const finde = cotizar(cabana, MAYO(14), MAYO(16)); // vie y sáb
  assert.equal(finde.total, 2 * directo(t.max));
  assert.equal(finde.sena, Math.round((finde.total * config.temporadas.baja.sena_porcentaje) / 100));
  assert.equal(finde.sena + finde.saldo, finde.total);
});

test("temporada Baja: 15% de descuento desde 4 noches", () => {
  const t = cabana.tarifas.baja;
  const c = cotizar(cabana, MAYO(12), MAYO(16)); // mié a sáb
  const conDescuento = (n) => Math.round((n * 0.85) / 1000) * 1000;
  assert.equal(c.total, 2 * conDescuento(directo(t.min)) + 2 * conDescuento(directo(t.max)));
});

test("Alta Premium: pago anticipado del 100% y la temporada más alta define la estadía", () => {
  const premium = cotizar(cabana, "2027-07-12", "2027-07-15");
  assert.equal(premium.temporada, "premium");
  assert.equal(premium.sena, premium.total);
  assert.equal(premium.saldo, 0);
  // Del 20/05 (Baja) al 23/05 (Alta desde el 22): manda Alta, con mínimo de 3 noches
  const mixta = cotizar(cabana, MAYO(20), MAYO(23));
  assert.equal(mixta.temporada, "alta");
  assert.deepEqual(mixta.noches_por_temporada, { baja: 2, alta: 1 });
  assert.equal(mixta.minimo_noches, 3);
});

test("mínimo de noches: 2 en Baja, 3 en Alta y 5 en Fin de Año", () => {
  assert.equal(minimoNoches(cabana, MAYO(12), MAYO(13)), 2);
  assert.equal(minimoNoches(cabana, "2027-01-10", "2027-01-11"), 3);
  assert.equal(minimoNoches(cabana, "2027-12-26", "2027-12-29"), 5);
  const datos = { cabanaId: cabana.id, huespedes: 2, nombre: "Prueba", metodoPago: "transferencia" };
  assert.throws(() => crearReserva({ ...datos, checkin: "2027-12-26", checkout: "2027-12-29" }), /mínimo es de 5 noches/);
});

test("validación de fechas", () => {
  assert.match(validarRango("2020-01-01", "2020-01-03"), /ya pasó/);
  assert.match(validarRango(MAYO(12), MAYO(10)), /posterior/);
  assert.match(validarRango("x", MAYO(10)), /inválidas/);
  assert.equal(validarRango(SEPT(10), SEPT(12)), null);
});

test("no permite doble reserva en fechas superpuestas", () => {
  const datos = { cabanaId: cabana.id, huespedes: 2, nombre: "Prueba", email: "p@ejemplo.com", telefono: "2990000000", metodoPago: "transferencia" };
  const r = crearReserva({ ...datos, checkin: SEPT(1), checkout: SEPT(4) });
  assert.equal(r.estado, "pendiente_pago");
  assert.equal(estaLibre(cabana.id, SEPT(2), SEPT(3)), false);
  assert.throws(() => crearReserva({ ...datos, checkin: SEPT(3), checkout: SEPT(6) }), /ya no están disponibles/);
  // El día de salida queda libre para otro ingreso
  assert.ok(crearReserva({ ...datos, checkin: SEPT(4), checkout: SEPT(6) }));
});

test("respeta la capacidad y el mínimo de noches", () => {
  const datos = { cabanaId: cabana.id, nombre: "Prueba", metodoPago: "transferencia" };
  assert.throws(() => crearReserva({ ...datos, huespedes: cabana.capacidad + config.negocio.dormi.plazas + 1, checkin: SEPT(20), checkout: SEPT(23) }), /Capacidad/);
  assert.throws(() => crearReserva({ ...datos, huespedes: 2, checkin: SEPT(20), checkout: SEPT(21) }), /mínimo/);
});

test("dormi: $ por persona adicional y por noche, sin descuentos de temporada", () => {
  const { plazas, precio_persona_noche: precio } = config.negocio.dormi;
  const base = cotizar(cabana, MAYO(12), MAYO(16), cabana.capacidad);
  const conDormi = cotizar(cabana, MAYO(12), MAYO(16), cabana.capacidad + 2);
  assert.equal(base.adicionales, 0);
  assert.equal(conDormi.adicionales, 2);
  assert.equal(conDormi.total_adicionales, 2 * 4 * precio);
  assert.equal(conDormi.total, base.total + 2 * 4 * precio);
  assert.equal(cotizar(cabana, MAYO(12), MAYO(16), cabana.capacidad + plazas).adicionales, plazas);
});

test("dormi: uno solo, una reserva a la vez, y capacidad máxima de cabaña + dormi", () => {
  const [c1, c2] = config.cabanas;
  const datos = { nombre: "Grupo", metodoPago: "transferencia", origen: "manual" };
  assert.throws(() => crearReserva({ ...datos, cabanaId: c1.id, huespedes: c1.capacidad + config.negocio.dormi.plazas + 1, checkin: SEPT(8), checkout: SEPT(11) }), /Capacidad máxima/);
  const r = crearReserva({ ...datos, cabanaId: c1.id, huespedes: c1.capacidad + 3, checkin: SEPT(8), checkout: SEPT(11) });
  assert.equal(r.adicionales, 3);
  assert.equal(dormiLibre(SEPT(10), SEPT(12)), false);
  // Otra cabaña libre en esas fechas no puede usar el dormi, pero sí reservar sin adicionales
  assert.throws(() => crearReserva({ ...datos, cabanaId: c2.id, huespedes: c2.capacidad + 1, checkin: SEPT(9), checkout: SEPT(12) }), /dormi/);
  assert.ok(crearReserva({ ...datos, cabanaId: c2.id, huespedes: 2, checkin: SEPT(9), checkout: SEPT(12) }));
  // En el panel, el error dice con qué choca
  assert.throws(() => crearReserva({ ...datos, cabanaId: c2.id, huespedes: 2, checkin: SEPT(10), checkout: SEPT(11) }), new RegExp(`${c2.nombre} ya está ocupada del 9 \\S+ al 12 \\S+ \\(reserva de Grupo\\)`));
  // Al reprogramar, el dormi se libera en las fechas viejas
  reprogramarReserva(r.id, { checkin: SEPT(13), checkout: SEPT(16) });
  assert.equal(dormiLibre(SEPT(8), SEPT(11)), true);
  assert.equal(dormiLibre(SEPT(14), SEPT(15)), false);
});
