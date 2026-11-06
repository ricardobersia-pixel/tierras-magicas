import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

process.env.DATA_DIR = fs.mkdtempSync(path.join(os.tmpdir(), "tm-tm-"));
const { config } = await import("../src/config.js");
const { crearReserva, hoyISO, sumarDias } = await import("../src/reservas.js");
const { confirmarConPago, registrarPago } = await import("../src/finanzas.js");
const { crearUsuario } = await import("../src/usuarios.js");
const { atenderPanel } = await import("../src/rutas-panel.js");
const { resumenPanel } = await import("../src/panel.js");
const mensajes = await import("../src/mensajes.js");

const dueno = { ...crearUsuario({ nombre: "Dueño", email: "d@x.com", rol: "dueno", clave: "clave-larga-1" }), rol: "dueno" };
const limpieza = { ...crearUsuario({ nombre: "Camila", email: "c@x.com", rol: "limpieza", clave: "clave-larga-2" }), rol: "limpieza" };
const mant = { ...crearUsuario({ nombre: "Jorge", email: "j@x.com", rol: "mantenimiento", clave: "clave-larga-3" }), rol: "mantenimiento" };
const [c1, c2] = config.cabanas;
const hoy = hoyISO();
const opciones = { icalExportar: () => null, pagoOnline: false, iaActiva: false };

test("tareas: urgentes primero, tomar, hecha con quién y cuándo, historial y permisos por tipo", () => {
  const normal = atenderPanel("POST", "/tareas", dueno, { cabanaId: c1.id, tipo: "limpieza", descripcion: "Repasar vidrios" });
  const urgente = atenderPanel("POST", "/tareas", mant, { cabanaId: c2.id, descripcion: "No sale agua caliente", urgente: true });
  assert.equal(urgente.prioridad, "urgente");
  assert.equal(atenderPanel("GET", "/tareas", dueno)[0].id, urgente.id, "la urgente va primero");
  assert.deepEqual(atenderPanel("GET", "/tareas", limpieza).map((t) => t.id), [normal.id], "limpieza ve solo las suyas");
  const tomada = atenderPanel("POST", `/tareas/${normal.id}/tomar`, limpieza);
  assert.equal(tomada.estado, "en_curso");
  assert.equal(tomada.asignado, "Camila");
  assert.throws(() => atenderPanel("POST", `/tareas/${normal.id}/tomar`, dueno), /La tomó Camila/);
  assert.throws(() => atenderPanel("POST", `/tareas/${urgente.id}/hecha`, limpieza), /permiso/);
  assert.throws(() => atenderPanel("POST", `/tareas/${normal.id}/urgente`, limpieza), /permiso/);
  const hecha = atenderPanel("POST", `/tareas/${normal.id}/hecha`, limpieza);
  assert.equal(hecha.estado, "hecha");
  assert.equal(hecha.hecha_por_nombre, "Camila");
  assert.ok(!resumenPanel(limpieza, null, opciones).tareas.some((t) => t.id === normal.id));
  assert.equal(atenderPanel("GET", "/tareas/historial", limpieza)[0].id, normal.id);
  assert.equal(atenderPanel("POST", `/tareas/${normal.id}/reabrir`, dueno).estado, "en_curso");
});

test("tareas de una reserva: limpieza no ve el nombre del huésped", () => {
  const r = crearReserva({ cabanaId: c1.id, checkin: sumarDias(hoy, 1), checkout: sumarDias(hoy, 4), huespedes: 2, nombre: "Pérez, Juan", origen: "manual", telefono: "2942000000" });
  confirmarConPago(r.id, { medio: "transferencia" });
  const deLimpieza = resumenPanel(limpieza, null, opciones).tareas.find((t) => t.reserva_id === r.id);
  assert.ok(!deLimpieza || !/Pérez/.test(deLimpieza.descripcion));
});

test("mensajes: datos de la reserva, cuáles tocan hoy y registro de enviados", () => {
  const r = crearReserva({ cabanaId: c2.id, checkin: sumarDias(hoy, 2), checkout: sumarDias(hoy, 5), huespedes: 3, nombre: "Gómez, Ana María", origen: "manual", telefono: "2942111111" });
  confirmarConPago(r.id, { medio: "transferencia" });
  registrarPago({ fecha: hoy, reservaId: r.id, concepto: "extra", medio: "efectivo", monto: 1000 });
  const { mensajes: lista } = mensajes.mensajesDeReserva(r.id);
  const conf = lista.find((m) => m.id === "confirmacion").texto;
  assert.match(conf, /¡Hola Ana!/);
  assert.match(conf, new RegExp(r.id));
  assert.doesNotMatch(conf, /\{[a-z_]+\}/, "no quedan datos sin completar");
  const tocan = atenderPanel("GET", "/mensajes/pendientes", dueno).filter((m) => m.reserva_id === r.id).map((m) => m.plantilla);
  assert.deepEqual(tocan.sort(), ["confirmacion", "recordatorio"], "a 2 días de llegar: confirmación y recordatorio");
  atenderPanel("POST", `/mensajes/reserva/${r.id}/recordatorio`, dueno);
  assert.ok(!atenderPanel("GET", "/mensajes/pendientes", dueno).some((m) => m.reserva_id === r.id && m.plantilla === "recordatorio"));
  assert.equal(mensajes.mensajesDeReserva(r.id).mensajes.find((m) => m.id === "recordatorio").enviado.usuario, "Dueño");
  assert.throws(() => atenderPanel("GET", "/mensajes/pendientes", limpieza), /permiso/);
});

test("plantillas editables: validan los datos y se restablecen", () => {
  assert.throws(() => mensajes.guardarPlantillas([{ nombre: "X", cuando: "manual", texto: "Hola {apodo}" }]), /\{apodo\}/);
  assert.throws(() => atenderPanel("POST", "/mensajes", { ...dueno, rol: "recepcion" }, { plantillas: [] }), /permiso/);
  const m = atenderPanel("POST", "/mensajes", dueno, { plantillas: [{ nombre: "Wifi", cuando: "manual", texto: "Hola {nombre}, la clave es..." }] });
  assert.equal(m.plantillas[0].id, "wifi");
  assert.equal(atenderPanel("POST", "/mensajes/restablecer", dueno).plantillas.length, 4);
});
