import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

process.env.DATA_DIR = fs.mkdtempSync(path.join(os.tmpdir(), "tm-un-"));
const { config } = await import("../src/config.js");
const { cargarAjustes, guardarTarifas, obtenerTarifas, guardarAjuste } = await import("../src/ajustes.js");
const u = await import("../src/unidades.js");
const { crearReserva } = await import("../src/reservas.js");
const { crearTurno, horarios } = await import("../src/turnos.js");
const { atenderPanel } = await import("../src/rutas-panel.js");

cargarAjustes();
const PNG = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==";
const dueno = { id: 1, rol: "dueno", nombre: "Dueño" };
const recepcion = { id: 2, rol: "recepcion", nombre: "Recepción" };

test("la lista arranca con las cabañas, el dormi y los recursos de config.json", () => {
  const { unidades } = u.obtenerUnidades();
  assert.deepEqual(unidades.filter((x) => x.tipo === "cabana").map((x) => x.id), config.cabanas.map((c) => c.id));
  assert.ok(unidades.some((x) => x.tipo === "dormi"));
  assert.ok(unidades.some((x) => x.id === "kayak" && x.tipo === "kayak" && x.turnos));
});

test("una cabaña nueva entra en reservas, tarifas y calendarios", () => {
  const c = u.crearUnidad({ tipo: "cabana", nombre: "Cabaña 4", capacidad: 4, habitaciones: 1, banos: 1, tarifas_como: "cabana-3" });
  assert.equal(c.id, "cabana-4");
  const cab = config.cabanas.find((x) => x.id === "cabana-4");
  assert.deepEqual(cab.tarifas, config.cabanas.find((x) => x.id === "cabana-3").tarifas, "arranca con las tarifas de la cabaña elegida");
  const r = crearReserva({ cabanaId: "cabana-4", checkin: "2027-10-05", checkout: "2027-10-08", huespedes: 2, nombre: "Prueba", origen: "manual" });
  assert.equal(r.cabana_id, "cabana-4");
  // Las tarifas guardadas incluyen la cabaña nueva y sobreviven a un reinicio
  const t = obtenerTarifas();
  t.tarifas["cabana-4"].alta = { min: 1000, max: 2000 };
  guardarTarifas(t);
  guardarAjuste("canales", { "cabana-4": { booking: "https://ical.booking.com/v1/export?t=prueba" } });
  cargarAjustes();
  assert.deepEqual(config.cabanas.find((x) => x.id === "cabana-4").tarifas.alta, { min: 1000, max: 2000 });
  assert.equal(config.cabanas.find((x) => x.id === "cabana-4").ical_importar.booking, "https://ical.booking.com/v1/export?t=prueba");
  assert.throws(() => u.borrarUnidad("cabana-4"), /tiene reservas/);
});

test("equipos: bote a motor con precio y turnos; aparece en la agenda", () => {
  const b = u.crearUnidad({ tipo: "bote", nombre: "Bote a motor", cantidad: 1, incluido: false, precio: 60000, turnos: true, duracion_min: 240, desde: "07:00", hasta: "19:00" });
  const rec = config.recursos.find((r) => r.id === b.id);
  assert.equal(rec.precio, 60000);
  assert.deepEqual(horarios(rec), ["07:00", "11:00", "15:00"]);
  assert.throws(() => u.crearUnidad({ tipo: "bicicleta", nombre: "Bici", incluido: false, precio: 0 }), /precio/);
  const bici = u.crearUnidad({ tipo: "bicicleta", nombre: "Bicicletas", cantidad: 4, turnos: false });
  assert.ok(!config.recursos.some((r) => r.id === bici.id), "sin turnos no aparece en la agenda");
  assert.ok(config.equipos.some((e) => e.id === bici.id), "pero sí en la web");
  crearTurno({ fecha: "2099-01-10", hora: "07:00", recurso: b.id, nombre: "Pesca" });
  assert.throws(() => u.borrarUnidad(b.id), /turno/);
  u.borrarUnidad(bici.id);
  assert.ok(!config.equipos.some((e) => e.id === bici.id));
});

test("fotos: hasta 5, la principal es la de la web, y se validan", () => {
  for (let i = 0; i < 5; i++) u.agregarFoto("cabana-1", PNG);
  assert.throws(() => u.agregarFoto("cabana-1", PNG), /5 fotos/);
  assert.throws(() => u.agregarFoto("cabana-2", "data:text/html;base64,PGgxPg=="), /JPG, PNG o WebP/);
  const cab = config.cabanas.find((c) => c.id === "cabana-1");
  assert.equal(cab.fotos.length, 5);
  const ultima = u.obtenerUnidades().unidades.find((x) => x.id === "cabana-1").fotos.at(-1);
  u.fotoPrincipal("cabana-1", ultima.id);
  assert.equal(cab.foto, `/fotos/${ultima.id}`);
  u.borrarFoto("cabana-1", ultima.id);
  assert.equal(cab.fotos.length, 4);
  assert.notEqual(cab.foto, `/fotos/${ultima.id}`);
  assert.equal(u.fotoParaServir(cab.fotos[0].split("/").pop()).tipo, "image/png");
});

test("permisos: recepción ve las unidades, solo el dueño las cambia; el dormi no se borra", () => {
  assert.ok(atenderPanel("GET", "/unidades", recepcion).unidades.length);
  assert.throws(() => atenderPanel("POST", "/unidades", recepcion, { tipo: "kayak" }), /permiso/);
  assert.throws(() => atenderPanel("DELETE", "/unidades/dormi", dueno), /dormi no se borra/);
  const k = atenderPanel("POST", "/unidades/kayak", dueno, { cantidad: 3, nombre: "Kayaks dobles" });
  assert.equal(k.cantidad, 3);
  assert.equal(config.recursos.find((r) => r.id === "kayak").nombre, "Kayaks dobles");
  assert.equal(atenderPanel("POST", "/unidades/kayak/fotos", dueno, { datos: PNG }).unidades.find((x) => x.id === "kayak").fotos.length, 1);
});
