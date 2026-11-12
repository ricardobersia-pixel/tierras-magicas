import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

process.env.DATA_DIR = fs.mkdtempSync(path.join(os.tmpdir(), "tm-consultas-"));
const { config } = await import("../src/config.js");
const { cotizar, crearReserva, confirmarReserva } = await import("../src/reservas.js");
const { crearUsuario } = await import("../src/usuarios.js");
const { atenderPanel } = await import("../src/rutas-panel.js");

const recepcion = { ...crearUsuario({ nombre: "Recepción", email: "r@x.com", rol: "recepcion", clave: "clave-larga-1" }), rol: "recepcion" };
const limpieza = { ...crearUsuario({ nombre: "Limpieza", email: "l@x.com", rol: "limpieza", clave: "clave-larga-2" }), rol: "limpieza" };
const [c1, , c3] = config.cabanas;
const pesos = (n) => "$" + Number(n).toLocaleString("es-AR");

// Fechas del calendario 2027 (temporada Media del 1 al 24 de marzo): lunes 8 a jueves 11
const media = { checkin: "2027-03-08", checkout: "2027-03-11", huespedes: 4 };

test("cotiza con el cuadro tarifario del panel, sin precio fijo", () => {
  const r = atenderPanel("POST", "/consultas/cotizar", recepcion, media);
  const esperado = cotizar(c3, media.checkin, media.checkout, 4);
  const cab3 = r.cabanas.find((c) => c.id === c3.id);
  assert.equal(cab3.total, esperado.total, "mismo cálculo que la web y las reservas");
  assert.equal(cab3.temporada_nombre, "Media");
  assert.ok(r.mensaje.includes(pesos(esperado.total)));
  assert.ok(r.mensaje.includes("Cabaña 3"));
  assert.ok(!r.mensaje.includes("["), "sin marcas internas para el dueño");
  assert.ok(!/booking\.com|exclusivo/i.test(r.mensaje));
});

test("si se cambian las tarifas en el panel, la cotización cambia", () => {
  const t = atenderPanel("GET", "/tarifas", { ...recepcion, rol: "dueno" });
  t.tarifas[c3.id].media = { min: 200000, max: 200000 };
  atenderPanel("POST", "/tarifas", { ...recepcion, rol: "dueno" }, t);
  const cab3 = atenderPanel("POST", "/consultas/cotizar", recepcion, media).cabanas.find((c) => c.id === c3.id);
  assert.equal(cab3.total, 3 * 200000 * (1 - config.negocio.precio_directo_descuento / 100));
  atenderPanel("POST", "/tarifas/restablecer", { ...recepcion, rol: "dueno" });
});

test("respeta el mínimo de noches de Fin de Año y la seña del 100% en Alta Premium", () => {
  const corta = atenderPanel("POST", "/consultas/cotizar", recepcion, { checkin: "2026-12-28", checkout: "2026-12-30", huespedes: 2 });
  assert.ok(corta.cabanas.every((c) => !c.disponible));
  assert.match(corta.mensaje, /mínima es de 5 noches/);
  assert.throws(() => atenderPanel("POST", "/consultas/reservar", recepcion, { cabanaId: c1.id, checkin: "2026-12-28", checkout: "2026-12-30", huespedes: 2 }), /mínima es de 5/);
  const fin = atenderPanel("POST", "/consultas/reservar", recepcion, { cabanaId: c1.id, checkin: "2026-12-26", checkout: "2026-12-31", huespedes: 2 });
  assert.equal(fin.sena_porcentaje, 100);
  assert.match(fin.mensaje, /100% por adelantado/);
  assert.match(fin.mensaje, /no es reembolsable/);
});

test("cómo reservar: seña, alias, políticas de la temporada y mascota", () => {
  const r = atenderPanel("POST", "/consultas/reservar", recepcion, { ...media, cabanaId: c3.id, mascota: true });
  assert.equal(r.sena_porcentaje, 50);
  assert.ok(r.mensaje.includes(pesos(r.sena)));
  assert.ok(r.mensaje.includes(config.negocio.transferencia.alias));
  assert.match(r.mensaje, /15 días o más/);
  assert.match(r.mensaje, /Cambio de fechas sin cargo/, "regla propia de temporada Media");
  assert.match(r.mensaje, /mascotas de tamaño mediano/i);
  assert.match(r.mensaje, /leña/);
});

test("no ofrece una cabaña ocupada y suma el dormi a grupos grandes", () => {
  const res = crearReserva({ cabanaId: c1.id, ...media, nombre: "Pérez, Ana", telefono: "2994000000", origen: "manual", metodoPago: "transferencia" });
  confirmarReserva(res.id);
  const r = atenderPanel("POST", "/consultas/cotizar", recepcion, media);
  assert.equal(r.cabanas.find((c) => c.id === c1.id).disponible, false);
  assert.ok(!r.mensaje.includes("Cabaña 1"));
  assert.throws(() => atenderPanel("POST", "/consultas/reservar", recepcion, { ...media, cabanaId: c1.id }), /no está disponible/);
  const grupo = atenderPanel("POST", "/consultas/cotizar", recepcion, { ...media, huespedes: 8 });
  assert.match(grupo.mensaje, /dormi para 2 personas más/);
});

test("bienvenida y permisos", () => {
  assert.match(atenderPanel("GET", "/consultas/bienvenida", recepcion).mensaje, /Fecha de llegada/);
  assert.throws(() => atenderPanel("GET", "/consultas/bienvenida", limpieza), /permiso/);
});
