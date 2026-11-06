import { db } from "./db.js";
import { cabanaPorId } from "./config.js";
import { hoyISO, sumarDias } from "./reservas.js";
import "./usuarios.js"; // crea la tabla usuarios (nombres de quién tomó o hizo la tarea)

// Tareas de limpieza, check-in, mantenimiento y otras: pendiente → en curso (alguien la toma) → hecha.
// Las urgentes van primero. Limpieza y Mantenimiento solo ven y mueven las de su tipo.

export const ESTADOS = ["pendiente", "en_curso", "hecha"];
const gestion = (u) => ["dueno", "recepcion"].includes(u.rol);
const SELECT = `SELECT t.*, a.nombre AS asignado, h.nombre AS hecha_por_nombre FROM tareas t
  LEFT JOIN usuarios a ON a.id = t.asignado_id LEFT JOIN usuarios h ON h.id = t.hecha_por`;

// Limpieza y mantenimiento no ven el nombre del huésped en las tareas generadas por una reserva
function paraRol(usuario, t) {
  if (gestion(usuario) || !t.reserva_id) return t;
  return { ...t, descripcion: "Limpieza tras la salida de los huéspedes" + (/\(incluye el dormi\)/.test(t.descripcion || "") ? " (incluye el dormi)" : "") };
}
const visibles = (usuario, lista) => (gestion(usuario) ? lista : lista.filter((t) => t.tipo === usuario.rol)).map((t) => paraRol(usuario, t));

// Pendientes y en curso hasta dentro de 7 días: urgentes primero, después por fecha
export function tareasAbiertas(usuario) {
  const lista = db.prepare(`${SELECT} WHERE t.hecha = 0 AND t.fecha <= ?
    ORDER BY (t.prioridad = 'urgente') DESC, t.fecha, t.id`).all(sumarDias(hoyISO(), 7));
  return visibles(usuario, lista);
}

// Hechas en los últimos días (quién y cuándo)
export function historialTareas(usuario, dias = 30) {
  const lista = db.prepare(`${SELECT} WHERE t.hecha = 1 AND COALESCE(t.hecha_en, t.fecha) >= ? ORDER BY COALESCE(t.hecha_en, t.fecha) DESC, t.id DESC LIMIT 200`)
    .all(sumarDias(hoyISO(), -dias));
  return visibles(usuario, lista);
}

export function crearTarea(usuario, cuerpo) {
  const tipo = gestion(usuario) && ["limpieza", "mantenimiento", "otro"].includes(cuerpo.tipo) ? cuerpo.tipo
    : usuario.rol === "limpieza" && cuerpo.tipo === "limpieza" ? "limpieza" : "mantenimiento";
  const fecha = cuerpo.fecha || hoyISO();
  if (!/^\d{4}-\d{2}-\d{2}$/.test(fecha)) throw new Error("Fecha inválida.");
  if (cuerpo.cabanaId && !cabanaPorId(cuerpo.cabanaId)) throw new Error("Cabaña inexistente.");
  const descripcion = String(cuerpo.descripcion || "").trim();
  if (!descripcion) throw new Error("Describí qué hay que hacer.");
  const prioridad = cuerpo.urgente ? "urgente" : "normal";
  const { lastInsertRowid } = db.prepare(`INSERT INTO tareas (cabana_id, fecha, tipo, descripcion, prioridad, estado, creada)
    VALUES (?, ?, ?, ?, ?, 'pendiente', datetime('now'))`).run(cuerpo.cabanaId || "general", fecha, tipo, `${descripcion} (reportó ${usuario.nombre})`, prioridad);
  return db.prepare(`${SELECT} WHERE t.id = ?`).get(lastInsertRowid);
}

function tareaPermitida(usuario, id) {
  const t = db.prepare(`${SELECT} WHERE t.id = ?`).get(Number(id));
  if (!t) throw Object.assign(new Error("Esa tarea no existe."), { estado: 404 });
  if (!gestion(usuario) && t.tipo !== usuario.rol) throw Object.assign(new Error("Tu usuario no tiene permiso para esta acción."), { estado: 403 });
  return t;
}

// accion: tomar | soltar | hecha | reabrir | urgente | normal
export function moverTarea(usuario, id, accion) {
  const t = tareaPermitida(usuario, id);
  const upd = (sql, ...params) => db.prepare(`UPDATE tareas SET ${sql} WHERE id = ?`).run(...params, t.id);
  if (accion === "tomar") {
    if (t.hecha) throw new Error("La tarea ya está hecha.");
    if (t.asignado_id && t.asignado_id !== usuario.id) throw new Error(`La tomó ${t.asignado}.`);
    upd("estado = 'en_curso', asignado_id = ?", usuario.id);
  } else if (accion === "soltar") {
    if (t.asignado_id !== usuario.id && !gestion(usuario)) throw new Error("Solo quien la tomó puede soltarla.");
    upd("estado = 'pendiente', asignado_id = NULL");
  } else if (accion === "hecha") {
    upd("estado = 'hecha', hecha = 1, hecha_por = ?, hecha_en = datetime('now')", usuario.id);
  } else if (accion === "reabrir") {
    upd("estado = CASE WHEN asignado_id IS NULL THEN 'pendiente' ELSE 'en_curso' END, hecha = 0, hecha_por = NULL, hecha_en = NULL");
  } else if (accion === "urgente" || accion === "normal") {
    if (!gestion(usuario)) throw Object.assign(new Error("Tu usuario no tiene permiso para esta acción."), { estado: 403 });
    upd("prioridad = ?", accion);
  } else {
    throw new Error("Acción inválida.");
  }
  return paraRol(usuario, db.prepare(`${SELECT} WHERE t.id = ?`).get(t.id));
}
