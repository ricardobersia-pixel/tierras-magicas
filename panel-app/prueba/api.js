// Las mismas rutas del panel que src/server.js, atendidas dentro del teléfono.
// La lógica de reservas, usuarios y permisos es la del servidor (src/); acá solo cambia el transporte.
import { db } from "../../src/db.js";
import { config, cabanaPorId } from "../../src/config.js";
import { crearReserva, obtenerReserva, cancelarReserva, validarRango, reprogramarReserva, hoyISO, sumarDias, cotizar } from "../../src/reservas.js";
import { confirmarConPago, registrarPago, crearGasto, actualizarOta } from "../../src/finanzas.js";
import { atenderPanel } from "../../src/rutas-panel.js";
import { cargarAjustes } from "../../src/ajustes.js";
import { crearTurno } from "../../src/turnos.js";
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
  { email: "mantenimiento@prueba.com", nombre: "Mantenimiento (prueba)", rol: "mantenimiento" },
];
export const CLAVE_PRUEBA = "tierras1234";

export function cargarDatosDePrueba() {
  cargarAjustes();
  if (listarUsuarios().length) return;
  for (const u of USUARIOS_PRUEBA) crearUsuario({ ...u, clave: CLAVE_PRUEBA });
  // Dos reservas confirmadas (una entra hoy) y una solicitud web pendiente de pago
  const hoy = hoyISO();
  const ejemplos = [
    { cabana: 0, desde: 0, noches: 3, nombre: "Fernández, Laura", huespedes: 2, origen: "manual", canal: "whatsapp" },
    { cabana: 1, desde: 2, noches: 4, nombre: "Sosa, Martín", huespedes: 2, origen: "manual", canal: "instagram" },
    { cabana: 2, desde: 1, noches: 3, nombre: "Gómez, José", huespedes: 6, origen: "manual", canal: "telefono" },
    { cabana: 0, desde: 9, noches: 4, nombre: "Torres, Ana", huespedes: 2, origen: "web" },
  ];
  for (const e of ejemplos) {
    const checkin = sumarDias(hoy, e.desde);
    try {
      crearReserva({
        cabanaId: config.cabanas[e.cabana % config.cabanas.length].id, checkin, checkout: sumarDias(checkin, e.noches),
        huespedes: e.huespedes, nombre: e.nombre, telefono: "5492942000000", email: "huesped@ejemplo.com",
        origen: e.origen, metodoPago: "transferencia", notas: "Reserva de ejemplo", canal: e.canal,
      });
    } catch {
      // Si la configuración no admite el ejemplo (capacidad, mínimo de noches), se omite
    }
  }
  cargarFinanzasDePrueba(hoy);
  cargarTurnosDePrueba(hoy);
}

// Turnos de hoy y mañana, y un arreglo reportado por limpieza
function cargarTurnosDePrueba(hoy) {
  const alojadas = db.prepare("SELECT * FROM reservas WHERE estado = 'confirmada' AND checkin <= ? AND checkout > ?").all(sumarDias(hoy, 1), hoy);
  const turnos = [
    { recurso: "jacuzzi", hora: "18:00", dia: 0 }, { recurso: "sauna", hora: "19:00", dia: 0 }, { recurso: "kayak-triple", hora: "11:00", dia: 1 },
    { recurso: "sup-rigido", hora: "09:00", dia: 1 }, { recurso: "jacuzzi", hora: "20:00", dia: 1 },
  ];
  turnos.forEach((t, i) => {
    const r = alojadas[i % Math.max(1, alojadas.length)];
    try {
      crearTurno({ fecha: sumarDias(hoy, t.dia), hora: t.hora, recurso: t.recurso, cantidad: t.cantidad || 1, reservaId: r?.id, nombre: r ? undefined : "Huésped" });
    } catch {
      // Si se editaron los recursos y el horario no existe, se omite
    }
  });
  db.prepare("INSERT INTO tareas (cabana_id, fecha, tipo, descripcion) VALUES (?, ?, 'mantenimiento', ?)")
    .run(config.cabanas[1 % config.cabanas.length].id, hoy, "Gotea la canilla de la cocina (reportó Limpieza (prueba))");
}

// Cobros, gastos y estadías de los dos meses anteriores para ver las finanzas con datos
function cargarFinanzasDePrueba(hoy) {
  const mes = (n) => desplazarMes(hoy.slice(0, 7), n);
  const cab = config.cabanas;
  // Estadías pasadas (se cargan directo: el sistema no deja crear reservas con fechas pasadas)
  const pasadas = [
    { id: "TM-EJ001", c: 0, desde: `${mes(-1)}-05`, n: 4, nombre: "Pérez, Familia", canal: "whatsapp" },
    { id: "TM-EJ002", c: 1, desde: `${mes(-1)}-12`, n: 3, nombre: "Ruiz, Carla", canal: "instagram" },
    { id: "TM-EJ003", c: 2, desde: `${mes(-2)}-20`, n: 5, nombre: "Molina, Diego", canal: "facebook" },
  ];
  for (const e of pasadas) {
    const cabana = cab[e.c % cab.length];
    const hasta = sumarDias(e.desde, e.n);
    const { total } = cotizar(cabana, e.desde, hasta, 2);
    db.prepare(`INSERT INTO reservas (id, cabana_id, checkin, checkout, huespedes, nombre, total, sena, estado, origen, notas, canal, creada)
      VALUES (?, ?, ?, ?, 2, ?, ?, ?, 'confirmada', 'manual', 'Estadía de ejemplo', ?, ?)`).run(e.id, cabana.id, e.desde, hasta, e.nombre, total, Math.round(total / 2), e.canal, sumarDias(e.desde, -25) + " 12:00:00");
    registrarPago({ fecha: sumarDias(e.desde, -20), reservaId: e.id, concepto: "sena", medio: "transferencia", monto: Math.round(total / 2) });
    registrarPago({ fecha: e.desde, reservaId: e.id, concepto: "saldo", medio: "efectivo", monto: total - Math.round(total / 2) });
  }
  registrarPago({ fecha: `${mes(-1)}-07`, reservaId: "TM-EJ001", concepto: "extra", medio: "efectivo", monto: 10000, nota: "Leña para el fogón" });
  // Señas de las reservas próximas
  for (const r of db.prepare("SELECT * FROM reservas WHERE origen = 'manual' AND notas = 'Reserva de ejemplo'").all()) {
    registrarPago({ fecha: sumarDias(hoy, -7), reservaId: r.id, concepto: "sena", medio: "transferencia", monto: r.sena });
  }
  // Airbnb: una estadía con monto cargado y una próxima sin cargar
  const ota = db.prepare("INSERT INTO reservas_ota (cabana_id, origen, uid, desde, hasta, resumen) VALUES (?, 'airbnb', ?, ?, ?, 'Reserved')");
  const { lastInsertRowid } = ota.run(cab[2 % cab.length].id, "ejemplo-airbnb-1", `${mes(-1)}-18`, `${mes(-1)}-22`);
  actualizarOta(Number(lastInsertRowid), { montoNeto: 420000, comision: 63000 });
  ota.run(cab[2 % cab.length].id, "ejemplo-airbnb-2", sumarDias(hoy, 12), sumarDias(hoy, 15));
  // Gastos fijos mensuales desde hace dos meses y variables de cada mes
  const fijos = [
    ["Personal (recepción, limpieza, mantenimiento)", "Sueldo limpieza y mantenimiento", 650000],
    ["Seguros", "Seguro de responsabilidad civil e incendio", 85000],
    ["Software y sistemas", "Internet Starlink y servidor del sitio", 95000],
  ];
  for (const [categoria, concepto, monto] of fijos) crearGasto({ fecha: `${mes(-2)}-01`, categoria, concepto, monto, tipo: "fijo", mensual: true });
  for (const m of [mes(-2), mes(-1), mes(0)]) {
    crearGasto({ fecha: `${m}-10`, categoria: "Servicios y energía (electricidad, gas, pellets, leña)", concepto: "Electricidad", monto: 140000, tipo: "variable" });
    crearGasto({ fecha: `${m}-15`, categoria: "Servicios y energía (electricidad, gas, pellets, leña)", concepto: "Pellets", monto: 110000, tipo: "variable" });
    crearGasto({ fecha: `${m}-20`, categoria: "Limpieza, lavandería e insumos", concepto: "Lavandería y amenities", monto: 60000, tipo: "variable" });
  }
}

function desplazarMes(mes, n) {
  let [a, m] = mes.split("-").map(Number);
  m += n;
  while (m < 1) { m += 12; a--; }
  while (m > 12) { m -= 12; a++; }
  return `${a}-${String(m).padStart(2, "0")}`;
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
    if (p[2] === "confirmar") {
      const r = obtenerReserva(p[1]);
      confirmarConPago(p[1], { medio: r.metodo_pago === "mercadopago" ? "mercadopago" : "transferencia", usuarioId: usuario.id });
    }
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
  if (metodo === "POST" && ruta === "/sincronizar") {
    gestion();
    return []; // Sin servidor no se pueden leer los calendarios de Airbnb/Booking
  }
  if (metodo === "POST" && ruta === "/borrador") {
    gestion();
    throw new Error("El asistente de WhatsApp necesita el servidor publicado; no está disponible en la app de prueba.");
  }
  const respuesta = atenderPanel(metodo, ruta, usuario, cuerpo || {}, consulta);
  if (respuesta !== undefined) return respuesta;
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
