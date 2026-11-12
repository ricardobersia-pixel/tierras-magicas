import { db } from "./db.js";
import { config, env, cabanaPorId } from "./config.js";
import { hoyISO, sumarDias, obtenerReserva } from "./reservas.js";
import "./usuarios.js"; // crea la tabla usuarios (quién mandó cada mensaje)

// Mensajes para el huésped: plantillas con datos de la reserva ({nombre}, {ingreso}, {saldo}…) que recepción
// manda por WhatsApp con un toque. El panel avisa cuáles tocan hoy (confirmación, recordatorio antes de llegar,
// bienvenida el día de ingreso, despedida al salir) y registra cuáles ya se mandaron.

const CLAVE = "mensajes";
export const MOMENTOS = {
  confirmada: "Al confirmar la reserva",
  antes: "Días antes de llegar",
  ingreso: "El día de llegada",
  salida: "El día de salida",
  manual: "Cuando lo elijas",
};

export const VARIABLES = {
  nombre: "Nombre del huésped",
  nombre_completo: "Apellido y nombre",
  cabana: "Cabaña",
  ingreso: "Fecha de ingreso",
  salida: "Fecha de salida",
  noches: "Noches",
  huespedes: "Personas",
  total: "Total de la estadía",
  pagado: "Pagado hasta hoy",
  saldo: "Saldo a pagar",
  codigo: "Código de reserva",
  link_reserva: "Página de la reserva",
  check_in: "Hora de check-in",
  check_out: "Hora de check-out",
  como_llegar: "Cómo llegar",
  mapa: "Ubicación en Google Maps",
  resena: "Link para dejar una reseña en Google",
  pesca: "Pronóstico de pesca",
  web: "Sitio web",
  complejo: "Nombre del complejo",
};

const PREDETERMINADAS = [
  {
    id: "confirmacion", nombre: "Confirmación", cuando: "confirmada", dias: 0,
    texto: "¡Hola {nombre}! Tu reserva en {complejo} está confirmada ✅\n\n🏡 {cabana}\n📅 Ingreso: {ingreso} desde las {check_in} h\n📅 Salida: {salida} hasta las {check_out} h\n👥 {huespedes} personas · {noches} noches\n💰 Total {total} · Pagado {pagado} · Saldo {saldo}\n\nCódigo de reserva: {codigo}\nDetalle: {link_reserva}\n\nCualquier consulta, escribinos por acá. ¡Te esperamos!",
  },
  {
    id: "recordatorio", nombre: "Recordatorio antes de llegar", cuando: "antes", dias: 2,
    texto: "¡Hola {nombre}! Ya falta poco para tu llegada a {complejo} 🌲\n\nTe esperamos el {ingreso} desde las {check_in} h en {cabana}.\n📍 {como_llegar}\nMapa: {mapa}\n\nEl saldo a abonar al llegar es {saldo}.\n\nIncluido: ropa de cama, frazadas y toallas, amenities de baño, básicos de cocina y los pellets de la calefacción. La leña para el fogón, los asadores y el horno no está incluida.\nTina caliente, sauna, kayaks y stand up están incluidos; cuando hay mucha demanda se usan por turnos.\n\n¿A qué hora estiman llegar?",
  },
  {
    id: "bienvenida", nombre: "Bienvenida y guía de la zona", cuando: "ingreso", dias: 0,
    texto: "¡Bienvenidos a {complejo}, {nombre}! 🏔️\n\nPara la tina, el sauna, los kayaks o el stand up, pedinos turno por acá.\n🎣 Pronóstico de pesca de la zona: {pesca}\n\nEl check-out es el {salida} hasta las {check_out} h. ¡Que disfruten!",
  },
  {
    id: "despedida", nombre: "Despedida y reseña", cuando: "salida", dias: 0,
    texto: "¡Gracias por elegirnos, {nombre}! 🙌 Fue un gusto recibirlos en {complejo}.\n\nNos ayuda mucho saber cómo fue tu estadía: contanos qué te gustó y qué podemos mejorar en una reseña en Google: {resena}\n\nPara la próxima, reservando directo en {web} tenés mejor precio. ¡Hasta pronto!",
  },
];

// ---------- Plantillas ----------

export function plantillas() {
  const fila = db.prepare("SELECT valor FROM ajustes WHERE clave = ?").get(CLAVE);
  return fila ? JSON.parse(fila.valor) : structuredClone(PREDETERMINADAS);
}

export function obtenerMensajes() {
  const fila = db.prepare("SELECT actualizado FROM ajustes WHERE clave = ?").get(CLAVE);
  return { plantillas: plantillas(), momentos: MOMENTOS, variables: VARIABLES, personalizadas: Boolean(fila), actualizado: fila?.actualizado || null };
}

export function guardarPlantillas(lista) {
  if (!Array.isArray(lista) || !lista.length) throw new Error("Tiene que haber al menos un mensaje.");
  const ids = new Set();
  const limpia = lista.map((x, i) => {
    const nombre = String(x.nombre || "").trim().slice(0, 60);
    const texto = String(x.texto || "").trim();
    if (!nombre || !texto) throw new Error(`Mensaje ${i + 1}: falta el nombre o el texto.`);
    if (texto.length > 2000) throw new Error(`${nombre}: el texto es muy largo (máximo 2000 letras).`);
    if (!MOMENTOS[x.cuando]) throw new Error(`${nombre}: elegí cuándo se manda.`);
    const dias = Number(x.dias) || 0;
    if (!(Number.isInteger(dias) && dias >= 0 && dias <= 30)) throw new Error(`${nombre}: los días deben estar entre 0 y 30.`);
    const desconocida = [...texto.matchAll(/\{([a-z_]+)\}/g)].map((m) => m[1]).find((v) => !VARIABLES[v]);
    if (desconocida) throw new Error(`${nombre}: {${desconocida}} no es un dato que se pueda completar.`);
    let id = String(x.id || "").trim() || nombre.toLowerCase().normalize("NFD").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || `mensaje-${i + 1}`;
    while (ids.has(id)) id += "-2";
    ids.add(id);
    return { id, nombre, cuando: x.cuando, dias: x.cuando === "antes" ? Math.max(1, dias) : 0, texto };
  });
  db.prepare(`INSERT INTO ajustes (clave, valor) VALUES (?, ?)
    ON CONFLICT (clave) DO UPDATE SET valor = excluded.valor, actualizado = datetime('now')`).run(CLAVE, JSON.stringify(limpia));
  return obtenerMensajes();
}

export function restablecerPlantillas() {
  db.prepare("DELETE FROM ajustes WHERE clave = ?").run(CLAVE);
  return obtenerMensajes();
}

// ---------- Completar con los datos de una reserva ----------

const pesos = (n) => "$" + Number(n).toLocaleString("es-AR");
const fechaLarga = (iso) => new Date(iso + "T12:00:00Z").toLocaleDateString("es-AR", { weekday: "long", day: "numeric", month: "long", timeZone: "UTC" });
// "Pérez, Juan Carlos" → "Juan"; "Juan Pérez" → "Juan"
const primerNombre = (s) => {
  const t = String(s || "").trim();
  const parte = t.includes(",") ? t.split(",")[1] : t;
  return (parte.trim().split(/\s+/)[0] || t).replace(/^./, (c) => c.toUpperCase());
};

function datosReserva(r) {
  const n = config.negocio;
  const { pagado } = db.prepare("SELECT COALESCE(SUM(monto), 0) AS pagado FROM pagos WHERE reserva_id = ?").get(r.id);
  const noches = Math.round((new Date(r.checkout) - new Date(r.checkin)) / 864e5);
  return {
    nombre: primerNombre(r.nombre), nombre_completo: r.nombre, cabana: cabanaPorId(r.cabana_id)?.nombre || r.cabana_id,
    ingreso: fechaLarga(r.checkin), salida: fechaLarga(r.checkout), noches, huespedes: r.huespedes,
    total: pesos(r.total), pagado: pesos(pagado), saldo: pesos(Math.max(0, r.total - pagado)), codigo: r.id,
    link_reserva: `${env.baseUrl}/reserva/${r.id}`, check_in: n.check_in, check_out: n.check_out,
    como_llegar: String(n.como_llegar || "").replace(/\s*Ubicación en Google Maps:.*$/, ""), mapa: n.google_maps || "", resena: n.google_resena || n.google_maps || "",
    pesca: `${env.baseUrl}/pesca`, web: env.baseUrl, complejo: n.nombre,
  };
}

const completar = (texto, d) => texto.replace(/\{([a-z_]+)\}/g, (m, v) => (d[v] ?? m));

const enviadosDe = (reservaId) => Object.fromEntries(db.prepare(`SELECT e.plantilla, e.fecha, u.nombre AS usuario FROM mensajes_enviados e
  LEFT JOIN usuarios u ON u.id = e.usuario_id WHERE e.reserva_id = ?`).all(reservaId).map((e) => [e.plantilla, e]));

export function mensajesDeReserva(reservaId) {
  const r = obtenerReserva(reservaId);
  if (!r) throw Object.assign(new Error("Esa reserva no existe."), { estado: 404 });
  const d = datosReserva(r);
  const enviados = enviadosDe(r.id);
  return {
    reserva: { id: r.id, nombre: r.nombre, telefono: r.telefono, email: r.email, cabana: d.cabana, checkin: r.checkin, checkout: r.checkout },
    mensajes: plantillas().map((p) => ({ id: p.id, nombre: p.nombre, cuando: p.cuando, texto: completar(p.texto, d), enviado: enviados[p.id] || null })),
  };
}

// ¿Le toca hoy a esta reserva este mensaje?
function toca(p, r, hoy) {
  if (p.cuando === "confirmada") return r.checkout >= hoy;
  if (p.cuando === "antes") return hoy >= sumarDias(r.checkin, -p.dias) && hoy < r.checkin;
  if (p.cuando === "ingreso") return hoy >= r.checkin && hoy < r.checkout;
  if (p.cuando === "salida") return hoy >= r.checkout && hoy <= sumarDias(r.checkout, 2);
  return false;
}

// Mensajes que tocan hoy y todavía no se mandaron (reservas confirmadas, directas)
export function mensajesPendientes() {
  const hoy = hoyISO();
  const lista = plantillas().filter((p) => p.cuando !== "manual");
  const reservas = db.prepare("SELECT * FROM reservas WHERE estado = 'confirmada' AND checkout >= ? ORDER BY checkin").all(sumarDias(hoy, -2));
  const pendientes = [];
  for (const r of reservas) {
    const enviados = enviadosDe(r.id);
    const tocan = lista.filter((p) => !enviados[p.id] && toca(p, r, hoy));
    if (!tocan.length) continue;
    const d = datosReserva(r);
    for (const p of tocan) {
      pendientes.push({ reserva_id: r.id, nombre: r.nombre, telefono: r.telefono, cabana: d.cabana, checkin: r.checkin, checkout: r.checkout,
        plantilla: p.id, plantilla_nombre: p.nombre, texto: completar(p.texto, d) });
    }
  }
  return pendientes;
}

export function marcarEnviado(reservaId, plantillaId, usuarioId, enviado = true) {
  if (!obtenerReserva(reservaId)) throw Object.assign(new Error("Esa reserva no existe."), { estado: 404 });
  if (!plantillas().some((p) => p.id === plantillaId)) throw new Error("Ese mensaje no existe.");
  if (enviado) {
    db.prepare(`INSERT INTO mensajes_enviados (reserva_id, plantilla, usuario_id) VALUES (?, ?, ?)
      ON CONFLICT (reserva_id, plantilla) DO UPDATE SET fecha = datetime('now'), usuario_id = excluded.usuario_id`).run(reservaId, plantillaId, usuarioId);
  } else {
    db.prepare("DELETE FROM mensajes_enviados WHERE reserva_id = ? AND plantilla = ?").run(reservaId, plantillaId);
  }
  return mensajesDeReserva(reservaId);
}
