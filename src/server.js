import express from "express";
import crypto from "node:crypto";
import { config, env, cabanaPorId } from "./config.js";
import { db } from "./db.js";
import {
  buscarDisponibilidad, crearReserva, obtenerReserva, confirmarReserva, cancelarReserva, ocupaciones, hoyISO, sumarDias, validarRango, preciosReferencia, reprogramarReserva,
} from "./reservas.js";
import { sincronizarTodo, exportarICal } from "./ical.js";
import { mpActivo, crearPreferencia, obtenerPago } from "./mercadopago.js";
import { responder } from "./asistente.js";
import { pronostico } from "./solunar.js";

const app = express();
app.set("trust proxy", 1); // detrás del proxy de Railway: IP real del visitante para el límite de solicitudes
app.use(express.json({ limit: "100kb" }));

app.get("/salud", (req, res) => res.json({ ok: true }));
app.use(express.static("public"));

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const pesos = (n) => "$" + Number(n).toLocaleString("es-AR");
const icalToken = crypto.createHash("sha256").update("ical:" + (env.adminPassword || "sin-clave")).digest("hex").slice(0, 16);

// Límite simple por IP para endpoints públicos costosos
const visitas = new Map();
function limitar(maxPorMinuto) {
  return (req, res, next) => {
    const clave = req.ip + req.path;
    const ahora = Date.now();
    const lista = (visitas.get(clave) || []).filter((t) => ahora - t < 60000);
    if (lista.length >= maxPorMinuto) return res.status(429).json({ error: "Demasiadas solicitudes, esperá un minuto." });
    lista.push(ahora);
    visitas.set(clave, lista);
    next();
  };
}

// ---------- API pública ----------

app.get("/api/info", (req, res) => {
  const { negocio } = config;
  res.json({
    negocio: { nombre: negocio.nombre, eslogan: negocio.eslogan, ubicacion: negocio.ubicacion, whatsapp: negocio.whatsapp,
      instagram: negocio.instagram, facebook: negocio.facebook, google_maps: negocio.google_maps, check_in: negocio.check_in,
      check_out: negocio.check_out, sena_porcentaje: negocio.sena_porcentaje, permite_pago_total: negocio.permite_pago_total,
      tipo_cambio_usd: negocio.tipo_cambio_usd, politicas: negocio.politicas, servicios: negocio.servicios, como_llegar: negocio.como_llegar,
      preguntas_frecuentes: negocio.preguntas_frecuentes },
    temporadas: config.temporadas,
    cabanas: config.cabanas.map(({ ical_importar, tarifas, ...c }) => ({ ...c, precios: preciosReferencia({ tarifas }) })),
    hoy: hoyISO(),
    pagoOnline: mpActivo(),
  });
});

app.get("/api/disponibilidad", (req, res) => {
  const { checkin, checkout } = req.query;
  res.json(buscarDisponibilidad(checkin, checkout, Math.max(1, Number(req.query.huespedes) || 1)));
});

// Pronóstico solunar de pesca para la ubicación del complejo
app.get("/api/pesca", (req, res) => {
  try {
    res.json({ ubicacion: config.negocio.ubicacion, dias: pronostico(req.query.desde || hoyISO(), req.query.dias || 14) });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

app.get("/pesca", (req, res) => res.sendFile("pesca.html", { root: "public" }));

// Días ocupados por cabaña (para pintar el calendario público, sin datos personales)
app.get("/api/ocupacion/:cabanaId", (req, res) => {
  if (!cabanaPorId(req.params.cabanaId)) return res.status(404).json({ error: "Cabaña inexistente" });
  res.json(ocupaciones(req.params.cabanaId).map((o) => ({ desde: o.desde, hasta: o.hasta })));
});

app.post("/api/reservas", limitar(5), async (req, res) => {
  try {
    const { cabanaId, checkin, checkout, huespedes, nombre, email, telefono, notas, metodoPago, modalidad } = req.body || {};
    if (!email || !/^\S+@\S+\.\S+$/.test(email)) throw new Error("Ingresá un email válido.");
    if (!telefono || String(telefono).replace(/\D/g, "").length < 8) throw new Error("Ingresá un teléfono / WhatsApp válido.");
    const reserva = crearReserva({ cabanaId, checkin, checkout, huespedes, nombre, email, telefono, notas, metodoPago, modalidad });
    if (reserva.metodo_pago === "mercadopago" && mpActivo()) {
      const pref = await crearPreferencia(reserva);
      db.prepare("UPDATE reservas SET mp_preference_id = ? WHERE id = ?").run(pref.id, reserva.id);
      return res.json({ reserva: reserva.id, pagarEn: pref.init_point });
    }
    res.json({ reserva: reserva.id, pagarEn: `/reserva/${reserva.id}` });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

async function verificarPago(paymentId) {
  const pago = await obtenerPago(paymentId);
  const reserva = pago.external_reference && obtenerReserva(pago.external_reference);
  if (reserva && pago.status === "approved" && Math.round(pago.transaction_amount) >= reserva.sena) {
    confirmarReserva(reserva.id, String(pago.id));
  }
  return pago;
}

// Página de estado a la que vuelve el huésped después de pagar
app.get("/reserva/:id", async (req, res) => {
  let r = obtenerReserva(req.params.id);
  if (!r) return res.status(404).send("Reserva no encontrada");
  if (r.estado === "pendiente_pago" && req.query.payment_id && mpActivo()) {
    try { await verificarPago(req.query.payment_id); r = obtenerReserva(r.id); } catch (e) { console.error(e.message); }
  }
  const c = cabanaPorId(r.cabana_id);
  const n = config.negocio;
  const t = n.transferencia || {};
  const porTransferencia = r.metodo_pago === "transferencia" || (r.metodo_pago === "mercadopago" && !mpActivo());
  const concepto = r.modalidad === "total" ? "el total" : `la seña (${n.sena_porcentaje}%)`;
  const estado = {
    confirmada: ["✅ Reserva confirmada", "¡Te esperamos! Te escribimos por WhatsApp unos días antes con las indicaciones de llegada."],
    pendiente_pago: porTransferencia
      ? ["📝 Reserva pendiente de pago", `Para confirmarla, transferí ${concepto} y envianos el comprobante por WhatsApp. Guardamos las fechas durante ${n.retencion_transferencia_horas || 48} horas.`]
      : ["⏳ Pago pendiente", "Todavía no recibimos la confirmación del pago. Si ya pagaste, puede tardar unos minutos."],
    cancelada: ["❌ Reserva cancelada", "Si creés que es un error, escribinos."],
  }[r.estado];
  const msj = encodeURIComponent(`Hola! Tengo la reserva ${r.id} en ${c.nombre} del ${r.checkin} al ${r.checkout}.${r.estado === "pendiente_pago" && porTransferencia ? " Te envío el comprobante de la transferencia." : ""}`);
  const datosTransferencia = r.estado === "pendiente_pago" && porTransferencia
    ? `<div class="transferencia"><h2>Datos para transferir ${pesos(r.sena)}</h2><dl>
<dt>Alias</dt><dd>${esc(t.alias)}</dd><dt>CBU</dt><dd>${esc(t.cbu)}</dd><dt>Titular</dt><dd>${esc(t.titular)}</dd><dt>Banco</dt><dd>${esc(t.banco)}</dd>
<dt>Concepto</dt><dd>Reserva ${esc(r.id)}</dd></dl></div>`
    : "";
  res.send(`<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reserva ${esc(r.id)} · ${esc(n.nombre)}</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet"><link rel="stylesheet" href="/estilos.css"></head>
<body class="pagina-reserva"><main class="tarjeta">
<a href="/" class="marca">${esc(n.nombre)}</a>
<h1>${estado[0]}</h1><p>${estado[1]}</p>
${datosTransferencia}
<dl><dt>Código</dt><dd>${esc(r.id)}</dd><dt>Cabaña</dt><dd>${esc(c.nombre)}</dd>
<dt>Ingreso</dt><dd>${esc(r.checkin)} desde las ${esc(n.check_in)}</dd><dt>Salida</dt><dd>${esc(r.checkout)} hasta las ${esc(n.check_out)}</dd>
<dt>Huéspedes</dt><dd>${r.huespedes}</dd><dt>Total</dt><dd>${pesos(r.total)}</dd>
<dt>${r.modalidad === "total" ? "Pago total" : "Seña"}</dt><dd>${pesos(r.sena)}</dd><dt>Saldo al ingresar</dt><dd>${pesos(r.total - r.sena)}</dd></dl>
<a class="boton" href="https://wa.me/${esc(n.whatsapp)}?text=${msj}">${r.estado === "pendiente_pago" && porTransferencia ? "Enviar comprobante por WhatsApp" : "Escribinos por WhatsApp"}</a>
</main></body></html>`);
});

// Notificaciones de Mercado Pago (IPN / Webhooks). Se verifica consultando el pago a la API.
app.post("/webhooks/mercadopago", async (req, res) => {
  res.sendStatus(200);
  const tipo = req.body?.type || req.query.type || req.query.topic;
  const id = req.body?.data?.id || req.query["data.id"] || req.query.id;
  if (tipo === "payment" && id && mpActivo()) {
    try { await verificarPago(id); } catch (e) { console.error("Webhook MP:", e.message); }
  }
});

app.post("/api/chat", limitar(15), async (req, res) => {
  try {
    const mensajes = Array.isArray(req.body?.mensajes) ? req.body.mensajes.filter((m) => ["user", "assistant"].includes(m.role)) : [];
    if (!mensajes.length || mensajes.at(-1).role !== "user") return res.status(400).json({ error: "Mensaje vacío" });
    res.json({ respuesta: await responder(mensajes, "web") });
  } catch (e) {
    console.error("Chat:", e.message);
    res.json({ respuesta: `Tuve un problema para responder. Escribinos por WhatsApp: https://wa.me/${config.negocio.whatsapp}` });
  }
});

// Calendario para pegar en Airbnb / Booking
app.get("/ical/:archivo", (req, res) => {
  const cabanaId = req.params.archivo.replace(/\.ics$/, "");
  if (req.query.t !== icalToken || !cabanaPorId(cabanaId)) return res.sendStatus(404);
  res.type("text/calendar; charset=utf-8").send(exportarICal(cabanaId));
});

// ---------- Panel de administración ----------

function soloAdmin(req, res, next) {
  const [tipo, cred] = (req.headers.authorization || "").split(" ");
  const [, clave] = Buffer.from(cred || "", "base64").toString().split(":");
  const ok = env.adminPassword && tipo === "Basic" && clave &&
    crypto.timingSafeEqual(crypto.createHash("sha256").update(clave).digest(), crypto.createHash("sha256").update(env.adminPassword).digest());
  if (ok) return next();
  res.set("WWW-Authenticate", 'Basic realm="Tierras Magicas"').status(401).send(env.adminPassword ? "Acceso restringido" : "Configurá ADMIN_PASSWORD en .env");
}

app.use(["/admin", "/api/admin"], soloAdmin);
app.get("/admin", (req, res) => res.sendFile("admin.html", { root: "public" }));

app.get("/api/admin/resumen", (req, res) => {
  const hoy = hoyISO();
  const desde = req.query.desde || hoy;
  const hasta = sumarDias(desde, 42);
  res.json({
    hoy,
    desde,
    hasta,
    cabanas: config.cabanas.map((c) => ({
      id: c.id, nombre: c.nombre,
      ical_exportar: `${env.baseUrl}/ical/${c.id}.ics?t=${icalToken}`,
      ical_configurado: Object.fromEntries(Object.entries(c.ical_importar || {}).map(([k, v]) => [k, Boolean(v)])),
    })),
    reservas: db.prepare("SELECT * FROM reservas WHERE checkout >= ? ORDER BY checkin").all(hoy),
    bloqueos: db.prepare("SELECT * FROM bloqueos WHERE hasta >= ? AND desde <= ? ORDER BY desde").all(desde, hasta),
    tareas: db.prepare("SELECT * FROM tareas WHERE hecha = 0 AND fecha <= ? ORDER BY fecha").all(sumarDias(hoy, 7)),
    sync: db.prepare("SELECT * FROM sync_log ORDER BY id DESC LIMIT 12").all(),
    ingresosMes: db.prepare("SELECT COALESCE(SUM(total),0) AS total, COUNT(*) AS n FROM reservas WHERE estado='confirmada' AND substr(checkin,1,7)=?").get(hoy.slice(0, 7)),
    pagoOnline: mpActivo(),
    iaActiva: env.iaActiva,
  });
});

app.post("/api/admin/reservas", (req, res) => {
  try {
    res.json(crearReserva({ ...req.body, origen: "manual" }));
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

app.post("/api/admin/reservas/:id/reprogramar", (req, res) => {
  try {
    res.json(reprogramarReserva(req.params.id, req.body || {}));
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

app.post("/api/admin/reservas/:id/:accion", (req, res) => {
  const { id, accion } = req.params;
  if (!obtenerReserva(id)) return res.status(404).json({ error: "No existe" });
  if (accion === "confirmar") confirmarReserva(id);
  else if (accion === "cancelar") cancelarReserva(id);
  else return res.status(400).json({ error: "Acción inválida" });
  res.json(obtenerReserva(id));
});

app.post("/api/admin/bloqueos", (req, res) => {
  const { cabanaId, desde, hasta, resumen } = req.body || {};
  const error = !cabanaPorId(cabanaId) ? "Cabaña inexistente" : validarRango(desde, hasta);
  if (error) return res.status(400).json({ error });
  db.prepare("INSERT INTO bloqueos (cabana_id, desde, hasta, origen, resumen) VALUES (?, ?, ?, 'manual', ?)").run(cabanaId, desde, hasta, resumen || "Bloqueo manual");
  res.json({ ok: true });
});

app.delete("/api/admin/bloqueos/:id", (req, res) => {
  db.prepare("DELETE FROM bloqueos WHERE id = ? AND origen = 'manual'").run(req.params.id);
  res.json({ ok: true });
});

app.post("/api/admin/tareas/:id/hecha", (req, res) => {
  db.prepare("UPDATE tareas SET hecha = 1 WHERE id = ?").run(req.params.id);
  res.json({ ok: true });
});

app.post("/api/admin/sincronizar", async (req, res) => {
  res.json(await sincronizarTodo());
});

// Borrador de respuesta para WhatsApp Business (sin API): el dueño pega el mensaje del huésped
app.post("/api/admin/borrador", async (req, res) => {
  try {
    const mensajes = Array.isArray(req.body?.mensajes) ? req.body.mensajes : [];
    if (!mensajes.length) return res.status(400).json({ error: "Pegá el mensaje del huésped" });
    res.json({ respuesta: await responder(mensajes, "whatsapp") });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ---------- Arranque ----------

app.listen(env.port, () => {
  console.log(`Tierras Mágicas en ${env.baseUrl}  ·  panel: ${env.baseUrl}/admin`);
  console.log(`Pago online: ${mpActivo() ? "Mercado Pago" : "modo demo"}  ·  IA: ${env.iaActiva ? "activa" : "inactiva"}`);
  if (!env.adminPassword) console.warn("ATENCIÓN: falta ADMIN_PASSWORD; el panel /admin queda bloqueado.");
});

sincronizarTodo().catch(() => {});
setInterval(() => sincronizarTodo().catch(() => {}), env.icalSyncMinutes * 60000);
