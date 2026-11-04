import { db } from "./db.js";
import { config, cabanaPorId } from "./config.js";
import { obtenerReserva } from "./reservas.js";

// Turnos de jacuzzi, sauna, kayaks y tablas de stand up. Cada recurso tiene una cantidad de unidades
// que se pueden usar a la vez, una duración de turno y un horario (config.recursos o editados en el panel).

const esFecha = (s) => typeof s === "string" && /^\d{4}-\d{2}-\d{2}$/.test(s) && !isNaN(new Date(s + "T12:00:00Z"));
const aMinutos = (h) => Number(h.slice(0, 2)) * 60 + Number(h.slice(3, 5));
const aHora = (m) => `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;

export const recursos = () => config.recursos || [];
const recursoPorId = (id) => recursos().find((r) => r.id === id);

// Horarios de inicio de turno de un recurso
export function horarios(recurso) {
  const lista = [];
  for (let m = aMinutos(recurso.desde); m + recurso.duracion_min <= aMinutos(recurso.hasta); m += recurso.duracion_min) lista.push(aHora(m));
  return lista;
}

const turnosDe = (fecha) =>
  db.prepare("SELECT * FROM turnos WHERE fecha = ? ORDER BY hora, recurso, id").all(fecha);

// Agenda del día: por recurso, cada horario con sus turnos y las unidades libres.
// conNombres = false (limpieza, mantenimiento): se muestra la cabaña pero no el nombre del huésped.
export function agendaDelDia(fecha, conNombres = true) {
  if (!esFecha(fecha)) throw new Error("Fecha inválida.");
  const turnos = turnosDe(fecha).map((t) => ({
    ...t,
    cabana: cabanaPorId(t.cabana_id)?.nombre || null,
    nombre: conNombres ? t.nombre : null,
    nota: conNombres ? t.nota : null,
  }));
  return {
    fecha,
    recursos: recursos().map((r) => ({
      ...r,
      horarios: horarios(r).map((hora) => {
        const enHorario = turnos.filter((t) => t.recurso === r.id && t.hora === hora);
        return { hora, turnos: enHorario, libres: r.cantidad - enHorario.reduce((s, t) => s + t.cantidad, 0) };
      }),
    })),
    total: turnos.length,
  };
}

export function crearTurno({ fecha, hora, recurso, cantidad = 1, cabanaId, reservaId, nombre, nota }, usuarioId = null) {
  if (!esFecha(fecha)) throw new Error("Fecha inválida.");
  const r = recursoPorId(recurso);
  if (!r) throw new Error("Elegí jacuzzi, sauna, kayaks o tablas.");
  if (!horarios(r).includes(hora)) throw new Error(`${r.nombre}: los turnos empiezan a las ${horarios(r).join(", ")}.`);
  cantidad = Number(cantidad);
  if (!(Number.isInteger(cantidad) && cantidad >= 1)) throw new Error("La cantidad debe ser 1 o más.");
  const reserva = reservaId ? obtenerReserva(reservaId) : null;
  if (reservaId && !reserva) throw new Error("La reserva no existe.");
  cabanaId = cabanaId || reserva?.cabana_id || null;
  if (cabanaId && !cabanaPorId(cabanaId)) throw new Error("Cabaña inexistente.");
  nombre = String(nombre || reserva?.nombre || "").trim();
  if (!nombre && !cabanaId) throw new Error("Indicá la cabaña o el nombre del huésped.");

  db.exec("BEGIN IMMEDIATE");
  try {
    const usadas = db.prepare("SELECT COALESCE(SUM(cantidad), 0) AS n FROM turnos WHERE fecha = ? AND hora = ? AND recurso = ?").get(fecha, hora, recurso).n;
    if (usadas + cantidad > r.cantidad) {
      const libres = r.cantidad - usadas;
      throw new Error(libres > 0 ? `${r.nombre} a las ${hora}: quedan ${libres} libre(s).` : `${r.nombre} a las ${hora} ya está ocupado.`);
    }
    const { lastInsertRowid } = db.prepare(
      "INSERT INTO turnos (fecha, hora, recurso, cantidad, cabana_id, reserva_id, nombre, nota, usuario_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    ).run(fecha, hora, recurso, cantidad, cabanaId, reservaId || null, nombre || null, nota || null, usuarioId);
    db.exec("COMMIT");
    return { ...db.prepare("SELECT * FROM turnos WHERE id = ?").get(lastInsertRowid), recurso_nombre: r.nombre };
  } catch (e) {
    db.exec("ROLLBACK");
    throw e;
  }
}

export function borrarTurno(id) {
  const t = db.prepare("SELECT * FROM turnos WHERE id = ?").get(id);
  if (!t) throw new Error("El turno no existe.");
  db.prepare("DELETE FROM turnos WHERE id = ?").run(id);
  return { ...t, recurso_nombre: recursoPorId(t.recurso)?.nombre || t.recurso };
}

// Uso de cada recurso entre dos fechas (para estadísticas)
export function usoDeRecursos(desde, hasta) {
  const filas = db.prepare("SELECT recurso, COUNT(*) AS turnos, SUM(cantidad) AS unidades FROM turnos WHERE fecha >= ? AND fecha < ? GROUP BY recurso").all(desde, hasta);
  return recursos().map((r) => {
    const f = filas.find((x) => x.recurso === r.id);
    return { recurso: r.nombre, turnos: f?.turnos || 0, unidades: f?.unidades || 0 };
  });
}
