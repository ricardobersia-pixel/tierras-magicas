// Las mismas rutas del panel que src/server.js, atendidas dentro del teléfono.
// La lógica de reservas, usuarios y permisos es la del servidor (src/); acá solo cambia el transporte.
import { db } from "../../src/db.js";
import { config, cabanaPorId } from "../../src/config.js";
import { crearReserva, obtenerReserva, confirmarReserva, cancelarReserva, validarRango, reprogramarReserva, hoyISO, sumarDias } from "../../src/reservas.js";
import {
  ROLES, listarUsuarios, crearUsuario, actualizarUsuario, cambiarClavePropia, iniciarSesion, usuarioDeSesion, cerrarSesion, registrar, ultimaAuditoria,
} from "../../src/usuarios.js";
import { resumenPanel } from "../../src/panel.js";

const SESION = "tm-prueba-sesion";
const leerSesion = () => localStorage.getItem(SESION);

class ErrorHttp extends Error {
  constructor(estado, mensaje) {
    super(mensaje);
    this.estado = estado;
  }
}
const sinPermiso = () => new ErrorHttp(403, "Tu usuario no tiene permiso para esta acción.");

// Usuarios de prueba y algunas reservas para ver el calendario y las tareas con datos
export const USUARIOS_PRUEBA = [
  { email: "dueno@prueba.com", nombre: "Dueño (prueba)", rol: "dueno" },
  { email: "recepcion@prueba.com", nombre: "Recepción (prueba)", rol: "recepcion" },
  { email: "limpieza@prueba.com", nombre: "Limpieza (prueba)", rol: "limpieza" },
];
export const CLAVE_PRUEBA = "tierras1234";

export function cargarDatosDePrueba() {
  if (listarUsuarios().length) return;
  for (const u of USUARIOS_PRUEBA) crearUsuario({ ...u, clave: CLAVE_PRUEBA });
  // Dos reservas confirmadas (una entra hoy) y una solicitud web pendiente de pago
  const hoy = hoyISO();
  const ejemplos = [
    { cabana: 0, desde: 0, noches: 3, nombre: "Laura Fernández", huespedes: 2, origen: "manual" },
    { cabana: 1, desde: 2, noches: 4, nombre: "Martín Sosa", huespedes: 2, origen: "manual" },
    { cabana: 0, desde: 9, noches: 4, nombre: "Ana Torres", huespedes: 2, origen: "web" },
  ];
  for (const e of ejemplos) {
    const checkin = sumarDias(hoy, e.desde);
    try {
      crearReserva({
        cabanaId: config.cabanas[e.cabana % config.cabanas.length].id, checkin, checkout: sumarDias(checkin, e.noches),
        huespedes: e.huespedes, nombre: e.nombre, telefono: "5492942000000", email: "huesped@ejemplo.com",
        origen: e.origen, metodoPago: "transferencia", notas: "Reserva de ejemplo",
      });
    } catch {
      // Si la configuración no admite el ejemplo (capacidad, mínimo de noches), se omite
    }
  }
}

function ingresar(cuerpo) {
  const sesion = iniciarSesion(cuerpo?.email, cuerpo?.clave);
  if (!sesion) throw new ErrorHttp(401, "Email o contraseña incorrectos.");
  localStorage.setItem(SESION, sesion.token);
  registrar(sesion.usuario.id, "ingreso");
  return { usuario: sesion.usuario };
}

function panel(metodo, ruta, cuerpo, consulta) {
  const usuario = usuarioDeSesion(leerSesion());
  if (!usuario) throw new ErrorHttp(401, "Tu sesión terminó. Volvé a ingresar.");
  const gestion = () => { if (!["dueno", "recepcion"].includes(usuario.rol)) throw sinPermiso(); };
  const soloDueno = () => { if (usuario.rol !== "dueno") throw sinPermiso(); };
  const p = ruta.split("/").filter(Boolean); // ["usuarios", "3"], ["reservas", "TM-1", "cancelar"]…

  if (metodo === "GET" && ruta === "/yo") return usuario;
  if (metodo === "GET" && ruta === "/resumen") {
    return resumenPanel(usuario, consulta.get("desde"), { icalExportar: () => null, pagoOnline: false, iaActiva: false });
  }
  if (metodo === "POST" && ruta === "/clave") {
    cambiarClavePropia(usuario.id, cuerpo?.actual, cuerpo?.nueva);
    registrar(usuario.id, "cambio de contraseña propia");
    return { ok: true };
  }
  if (p[0] === "usuarios") {
    soloDueno();
    if (metodo === "GET") return { roles: ROLES, usuarios: listarUsuarios(), auditoria: ultimaAuditoria() };
    if (metodo === "POST" && !p[1]) {
      const u = crearUsuario(cuerpo || {});
      registrar(usuario.id, "alta de usuario", `${u.email} (${u.rol})`);
      return u;
    }
    if (metodo === "POST") {
      const { rol, activo, clave } = cuerpo || {};
      const u = actualizarUsuario(Number(p[1]), { rol, activo, clave });
      const cambios = [rol && `rol ${u.rol}`, activo !== undefined && (u.activo ? "activado" : "desactivado"), clave && "nueva contraseña"].filter(Boolean).join(", ");
      registrar(usuario.id, "cambio de usuario", `${u.email}: ${cambios}`);
      return u;
    }
  }
  if (p[0] === "reservas" && metodo === "POST") {
    gestion();
    if (!p[1]) {
      const r = crearReserva({ ...cuerpo, origen: "manual" });
      registrar(usuario.id, "reserva manual", `${r.id} · ${r.cabana_id} · ${r.checkin} a ${r.checkout} · ${r.nombre}`);
      return r;
    }
    if (p[2] === "reprogramar") {
      const r = reprogramarReserva(p[1], cuerpo || {});
      registrar(usuario.id, "reprogramación", `${r.id} · ${r.cabana_id} · ${r.checkin} a ${r.checkout}`);
      return r;
    }
    if (!obtenerReserva(p[1])) throw new ErrorHttp(404, "No existe");
    if (p[2] === "confirmar") confirmarReserva(p[1]);
    else if (p[2] === "cancelar") cancelarReserva(p[1]);
    else throw new Error("Acción inválida");
    registrar(usuario.id, p[2] === "confirmar" ? "confirmación" : "cancelación", p[1]);
    return obtenerReserva(p[1]);
  }
  if (p[0] === "bloqueos") {
    gestion();
    if (metodo === "POST") {
      const { cabanaId, desde, hasta, resumen } = cuerpo || {};
      const error = !cabanaPorId(cabanaId) ? "Cabaña inexistente" : validarRango(desde, hasta);
      if (error) throw new Error(error);
      db.prepare("INSERT INTO bloqueos (cabana_id, desde, hasta, origen, resumen) VALUES (?, ?, ?, 'manual', ?)").run(cabanaId, desde, hasta, resumen || "Bloqueo manual");
      registrar(usuario.id, "bloqueo", `${cabanaId} · ${desde} a ${hasta}`);
      return { ok: true };
    }
    if (metodo === "DELETE") {
      const { changes } = db.prepare("DELETE FROM bloqueos WHERE id = ? AND origen = 'manual'").run(p[1]);
      if (changes) registrar(usuario.id, "bloqueo eliminado", p[1]);
      return { ok: true };
    }
  }
  if (p[0] === "tareas" && p[2] === "hecha" && metodo === "POST") {
    const t = db.prepare("SELECT * FROM tareas WHERE id = ?").get(p[1]);
    if (!t) throw new ErrorHttp(404, "No existe");
    if (usuario.rol === "limpieza" && t.tipo !== "limpieza") throw sinPermiso();
    db.prepare("UPDATE tareas SET hecha = 1 WHERE id = ?").run(t.id);
    registrar(usuario.id, "tarea hecha", `${t.tipo} · ${t.cabana_id} · ${t.fecha}`);
    return { ok: true };
  }
  if (metodo === "POST" && ruta === "/sincronizar") {
    gestion();
    return []; // Sin servidor no se pueden leer los calendarios de Airbnb/Booking
  }
  if (metodo === "POST" && ruta === "/borrador") {
    gestion();
    throw new Error("El asistente de WhatsApp necesita el servidor publicado; no está disponible en la app de prueba.");
  }
  throw new ErrorHttp(404, "Ruta inexistente");
}

// Atiende un pedido a /api/… como lo haría el servidor. Devuelve { estado, cuerpo }.
export function atender(metodo, url, cuerpo) {
  try {
    if (metodo === "POST" && url.pathname === "/api/ingresar") return { estado: 200, cuerpo: ingresar(cuerpo) };
    if (metodo === "POST" && url.pathname === "/api/salir") {
      cerrarSesion(leerSesion());
      localStorage.removeItem(SESION);
      return { estado: 200, cuerpo: { ok: true } };
    }
    if (url.pathname.startsWith("/api/admin/")) {
      return { estado: 200, cuerpo: panel(metodo, url.pathname.slice("/api/admin".length), cuerpo, url.searchParams) };
    }
    return { estado: 404, cuerpo: { error: "Ruta inexistente" } };
  } catch (e) {
    return { estado: e.estado || 400, cuerpo: { error: e.message } };
  }
}

export function haySesion() {
  return Boolean(usuarioDeSesion(leerSesion()));
}
