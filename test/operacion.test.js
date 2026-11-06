import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

process.env.DATA_DIR = fs.mkdtempSync(path.join(os.tmpdir(), "tm-op-"));
const { config } = await import("../src/config.js");
const { crearReserva } = await import("../src/reservas.js");
const { calendarioMes } = await import("../src/panel.js");
const turnos = await import("../src/turnos.js");
const ajustes = await import("../src/ajustes.js");
const { estadisticas } = await import("../src/finanzas.js");
const { atenderPanel } = await import("../src/rutas-panel.js");

const [c1, c2, c3] = config.cabanas;
const dueno = { id: 1, rol: "dueno", nombre: "Dueño" };
const limpieza = { id: 2, rol: "limpieza", nombre: "Limpieza" };
const mantenimiento = { id: 3, rol: "mantenimiento", nombre: "Mantenimiento" };

const r1 = crearReserva({ cabanaId: c1.id, checkin: "2027-09-02", checkout: "2027-09-05", huespedes: 2, nombre: "Pérez, Juan", origen: "manual", canal: "instagram", telefono: "2990000000" });
const r3 = crearReserva({ cabanaId: c3.id, checkin: "2027-09-03", checkout: "2027-09-06", huespedes: c3.capacidad + 2, nombre: "Gómez, Ana", origen: "manual" });

test("canal de la reserva: el elegido en reservas manuales, web en la web", () => {
  assert.equal(r1.canal, "instagram");
  assert.equal(r3.canal, "whatsapp", "sin canal elegido, una reserva manual queda como WhatsApp");
  const web = crearReserva({ cabanaId: c2.id, checkin: "2027-09-20", checkout: "2027-09-23", huespedes: 2, nombre: "Web", email: "w@x.com", telefono: "2990000000", metodoPago: "transferencia", canal: "instagram" });
  assert.equal(web.canal, "web");
});

test("calendario mensual: datos completos para el dueño, sin datos del huésped para limpieza y mantenimiento", () => {
  const cal = calendarioMes(dueno, "2027-09");
  const fila = cal.filas.find((f) => f.id === c1.id);
  const o = fila.ocupaciones.find((x) => x.id === r1.id);
  assert.equal(o.nombre, "Pérez, Juan");
  assert.equal(o.canal, "instagram");
  assert.equal(o.telefono, "2990000000");
  const dormi = cal.filas.find((f) => f.id === "dormi");
  assert.ok(dormi.ocupaciones.some((x) => x.id === r3.id && x.cabana === c3.nombre), "la reserva con adicionales aparece en el dormi");
  for (const usuario of [limpieza, mantenimiento]) {
    const visto = calendarioMes(usuario, "2027-09").filas.find((f) => f.id === c1.id).ocupaciones[0];
    assert.deepEqual(Object.keys(visto).sort(), ["desde", "estado", "hasta", "tipo"]);
  }
  assert.throws(() => calendarioMes(dueno, "2027-13"), /Mes inválido/);
});

test("turnos: horarios por recurso, cupo y validaciones", () => {
  const jacuzzi = config.recursos.find((r) => r.id === "jacuzzi");
  const horas = turnos.horarios(jacuzzi);
  assert.equal(horas[0], jacuzzi.desde);
  const t = turnos.crearTurno({ fecha: "2027-09-03", hora: horas[0], recurso: "jacuzzi", reservaId: r1.id });
  assert.equal(t.cabana_id, c1.id);
  assert.equal(t.nombre, "Pérez, Juan");
  assert.throws(() => turnos.crearTurno({ fecha: "2027-09-03", hora: horas[0], recurso: "jacuzzi", nombre: "Otro" }), /ocupado/);
  assert.throws(() => turnos.crearTurno({ fecha: "2027-09-03", hora: "10:17", recurso: "jacuzzi", nombre: "Otro" }), /empiezan/);
  const kayak = config.recursos.find((r) => r.id === "kayak-triple");
  assert.deepEqual(turnos.horarios(kayak), ["09:00", "11:00", "13:00", "15:00", "17:00"], "turnos de 2 horas de 9 a 20");
  // Cupo parcial: un equipo con varias unidades a la vez
  config.recursos.push({ id: "bicis", nombre: "Bicis", cantidad: 3, duracion_min: 60, desde: "09:00", hasta: "12:00" });
  turnos.crearTurno({ fecha: "2027-09-03", hora: "09:00", recurso: "bicis", cantidad: 2, nombre: "Grupo" });
  assert.throws(() => turnos.crearTurno({ fecha: "2027-09-03", hora: "09:00", recurso: "bicis", cantidad: 2, nombre: "Otro" }), /quedan 1 libre/);
  config.recursos.pop();
  const agenda = turnos.agendaDelDia("2027-09-03", false);
  const slot = agenda.recursos.find((r) => r.id === "jacuzzi").horarios[0];
  assert.equal(slot.libres, 0);
  assert.equal(slot.turnos[0].nombre, null, "limpieza y mantenimiento no ven el nombre del huésped");
  turnos.borrarTurno(t.id);
  assert.equal(turnos.agendaDelDia("2027-09-03").recursos.find((r) => r.id === "jacuzzi").horarios[0].libres, 1);
});

test("rutas: permisos de mantenimiento y alta de tareas", () => {
  const tarea = atenderPanel("POST", "/tareas", mantenimiento, { cabanaId: c2.id, descripcion: "Cambiar foco", tipo: "limpieza" });
  assert.equal(tarea.tipo, "mantenimiento", "mantenimiento solo crea tareas de mantenimiento");
  assert.match(tarea.descripcion, /reportó Mantenimiento/);
  assert.ok(atenderPanel("GET", "/calendario", mantenimiento, {}, new URLSearchParams("mes=2027-09")));
  assert.throws(() => atenderPanel("POST", "/turnos", mantenimiento, {}), /permiso/);
  assert.throws(() => atenderPanel("GET", "/estadisticas", mantenimiento), /permiso/);
  assert.throws(() => atenderPanel("POST", "/respuestas", limpieza, { preguntas: [] }), /permiso/);
  assert.ok(atenderPanel("GET", "/tareas", dueno).some((t) => t.id === tarea.id), "el dueño ve todas las tareas");
  assert.equal(atenderPanel("GET", "/reservas", dueno), undefined, "otras rutas las atiende el servidor");
});

test("ajustes: respuestas, recursos y calendarios de Airbnb/Booking", () => {
  const antes = config.negocio.preguntas_frecuentes.length;
  ajustes.guardarAjuste("preguntas", [{ p: "¿Hay wifi?", r: "Sí, Starlink." }]);
  assert.equal(config.negocio.preguntas_frecuentes.length, 1, "la web usa las mismas preguntas");
  assert.throws(() => ajustes.guardarAjuste("preguntas", [{ p: "Sin respuesta", r: "" }]), /respuesta/);
  ajustes.restablecerAjuste("preguntas");
  assert.equal(config.negocio.preguntas_frecuentes.length, antes);

  assert.throws(() => ajustes.guardarAjuste("recursos", [{ nombre: "Sauna", cantidad: 1, duracion_min: 60, desde: "20:00", hasta: "10:00" }]), /horario/);
  ajustes.guardarAjuste("recursos", [{ id: "kayak", nombre: "Kayaks", cantidad: 4, duracion_min: 90, desde: "09:00", hasta: "18:00" }]);
  assert.equal(turnos.horarios(config.recursos[0]).length, 6);
  ajustes.restablecerAjuste("recursos");

  assert.throws(() => ajustes.guardarAjuste("canales", { [c1.id]: { airbnb: "http://inseguro" } }), /https/);
  ajustes.guardarAjuste("canales", { [c1.id]: { airbnb: "https://www.airbnb.com/calendar/ical/1.ics", booking: "" } });
  assert.equal(c1.ical_importar.airbnb, "https://www.airbnb.com/calendar/ical/1.ics", "la sincronización usa el enlace guardado");
  ajustes.restablecerAjuste("canales");
  assert.equal(c1.ical_importar.airbnb, "");
});

test("estadísticas de 12 meses: serie, canales y reservas directas", () => {
  const e = estadisticas("2027-09");
  assert.equal(e.serie.length, 12);
  assert.equal(e.serie.at(-1).mes, "2027-09");
  assert.ok(e.serie.at(-1).noches >= 6);
  assert.ok(e.canales.some((c) => c.canal === "Instagram"), "las reservas directas se abren por canal");
  assert.equal(e.reservas.con_dormi, 1);
  assert.ok(e.reservas.por_canal.some((c) => c.canal === "Instagram" && c.reservas === 1));
});
