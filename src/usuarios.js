import crypto from "node:crypto";
import { db } from "./db.js";

export const ROLES = ["dueno", "recepcion", "limpieza"];
const DURACION_SESION_DIAS = 14;

db.exec(`
  CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    rol TEXT NOT NULL,              -- dueno | recepcion | limpieza
    clave_hash TEXT NOT NULL,       -- scrypt: sal:hash (hex)
    activo INTEGER NOT NULL DEFAULT 1,
    creado TEXT NOT NULL DEFAULT (datetime('now'))
  );

  -- Solo se guarda el hash del token: si alguien copia la base no puede usar las sesiones
  CREATE TABLE IF NOT EXISTS sesiones (
    token_hash TEXT PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    expira TEXT NOT NULL
  );

  -- Quién hizo qué en el panel
  CREATE TABLE IF NOT EXISTS auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL DEFAULT (datetime('now')),
    usuario_id INTEGER,
    accion TEXT NOT NULL,
    detalle TEXT
  );
`);

const normalizarEmail = (e) => String(e || "").trim().toLowerCase();
const sha256 = (s) => crypto.createHash("sha256").update(s).digest("hex");

function hashClave(clave) {
  const sal = crypto.randomBytes(16).toString("hex");
  return `${sal}:${crypto.scryptSync(clave, sal, 64).toString("hex")}`;
}

function claveCorrecta(clave, guardado) {
  const [sal, hash] = String(guardado).split(":");
  if (!sal || !hash) return false;
  return crypto.timingSafeEqual(crypto.scryptSync(clave, sal, 64), Buffer.from(hash, "hex"));
}

function validarClave(clave) {
  if (String(clave || "").length < 10) throw new Error("La contraseña debe tener al menos 10 caracteres.");
}

const publico = ({ clave_hash, ...u }) => ({ ...u, activo: Boolean(u.activo) });

export function listarUsuarios() {
  return db.prepare("SELECT * FROM usuarios ORDER BY activo DESC, rol, nombre").all().map(publico);
}

function duenosActivos(excluirId = 0) {
  return db.prepare("SELECT COUNT(*) AS n FROM usuarios WHERE rol = 'dueno' AND activo = 1 AND id != ?").get(excluirId).n;
}

export function crearUsuario({ email, nombre, rol, clave }) {
  email = normalizarEmail(email);
  if (!/^\S+@\S+\.\S+$/.test(email)) throw new Error("Ingresá un email válido.");
  if (!String(nombre || "").trim()) throw new Error("Ingresá el nombre.");
  if (!ROLES.includes(rol)) throw new Error("Rol inválido.");
  validarClave(clave);
  if (db.prepare("SELECT 1 FROM usuarios WHERE email = ?").get(email)) throw new Error("Ya existe un usuario con ese email.");
  const { lastInsertRowid } = db.prepare("INSERT INTO usuarios (email, nombre, rol, clave_hash) VALUES (?, ?, ?, ?)")
    .run(email, String(nombre).trim(), rol, hashClave(clave));
  return publico(db.prepare("SELECT * FROM usuarios WHERE id = ?").get(lastInsertRowid));
}

export function actualizarUsuario(id, { rol, activo, clave }) {
  const u = db.prepare("SELECT * FROM usuarios WHERE id = ?").get(id);
  if (!u) throw new Error("No existe el usuario.");
  const nuevoRol = rol ?? u.rol;
  const nuevoActivo = activo === undefined ? Boolean(u.activo) : Boolean(activo);
  if (!ROLES.includes(nuevoRol)) throw new Error("Rol inválido.");
  if ((nuevoRol !== "dueno" || !nuevoActivo) && u.rol === "dueno" && !duenosActivos(u.id)) {
    throw new Error("Tiene que quedar al menos un dueño activo.");
  }
  db.prepare("UPDATE usuarios SET rol = ?, activo = ? WHERE id = ?").run(nuevoRol, nuevoActivo ? 1 : 0, id);
  if (clave !== undefined && clave !== "") {
    validarClave(clave);
    db.prepare("UPDATE usuarios SET clave_hash = ? WHERE id = ?").run(hashClave(clave), id);
  }
  // Cambio de rol, baja o nueva contraseña: se cierran sus sesiones abiertas
  if (nuevoRol !== u.rol || !nuevoActivo || clave) db.prepare("DELETE FROM sesiones WHERE usuario_id = ?").run(id);
  return publico(db.prepare("SELECT * FROM usuarios WHERE id = ?").get(id));
}

export function cambiarClavePropia(id, actual, nueva) {
  const u = db.prepare("SELECT * FROM usuarios WHERE id = ?").get(id);
  if (!u || !claveCorrecta(String(actual || ""), u.clave_hash)) throw new Error("La contraseña actual no es correcta.");
  validarClave(nueva);
  db.prepare("UPDATE usuarios SET clave_hash = ? WHERE id = ?").run(hashClave(nueva), id);
}

// Devuelve un token de sesión nuevo, o null si el email/contraseña no coinciden
export function iniciarSesion(email, clave) {
  const u = db.prepare("SELECT * FROM usuarios WHERE email = ? AND activo = 1").get(normalizarEmail(email));
  if (!u || !claveCorrecta(String(clave || ""), u.clave_hash)) return null;
  const token = crypto.randomBytes(32).toString("base64url");
  const expira = new Date(Date.now() + DURACION_SESION_DIAS * 86400000).toISOString();
  db.prepare("DELETE FROM sesiones WHERE expira < ?").run(new Date().toISOString());
  db.prepare("INSERT INTO sesiones (token_hash, usuario_id, expira) VALUES (?, ?, ?)").run(sha256(token), u.id, expira);
  return { token, usuario: publico(u), maxAge: DURACION_SESION_DIAS * 86400000 };
}

export function usuarioDeSesion(token) {
  if (!token) return null;
  const u = db.prepare(`SELECT u.* FROM sesiones s JOIN usuarios u ON u.id = s.usuario_id
    WHERE s.token_hash = ? AND s.expira > ? AND u.activo = 1`).get(sha256(token), new Date().toISOString());
  return u ? publico(u) : null;
}

export function cerrarSesion(token) {
  if (token) db.prepare("DELETE FROM sesiones WHERE token_hash = ?").run(sha256(token));
}

export function registrar(usuarioId, accion, detalle = "") {
  db.prepare("INSERT INTO auditoria (usuario_id, accion, detalle) VALUES (?, ?, ?)").run(usuarioId ?? null, accion, String(detalle).slice(0, 500));
}

export function ultimaAuditoria(limite = 30) {
  return db.prepare(`SELECT a.fecha, a.accion, a.detalle, COALESCE(u.nombre, 'sistema') AS usuario
    FROM auditoria a LEFT JOIN usuarios u ON u.id = a.usuario_id ORDER BY a.id DESC LIMIT ?`).all(limite);
}

// Primer arranque: si no hay usuarios, crea al dueño con DUENO_EMAIL + ADMIN_PASSWORD
export function crearDuenoInicial(email, clave) {
  if (db.prepare("SELECT COUNT(*) AS n FROM usuarios").get().n) return false;
  if (!email || !clave) return false;
  crearUsuario({ email, nombre: "Dueño", rol: "dueno", clave });
  return true;
}
