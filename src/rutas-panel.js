// Rutas del panel para finanzas y tarifas. Las usan el servidor (server.js) y la app de prueba del teléfono,
// así los permisos y la lógica son los mismos en los dos.
import { db } from "./db.js";
import { cabanaPorId } from "./config.js";
import { cotizar, hoyISO } from "./reservas.js";
import { registrar } from "./usuarios.js";
import { obtenerTarifas, guardarTarifas, restablecerTarifas, conTarifas, obtenerAjuste, guardarAjuste, restablecerAjuste } from "./ajustes.js";
import { calendarioMes } from "./panel.js";
import { agendaDelDia, crearTurno, borrarTurno } from "./turnos.js";
import {
  CATEGORIAS_GASTO, MEDIOS, CONCEPTOS, registrarPago, borrarPago, crearGasto, darDeBajaGasto, borrarGasto, actualizarOta,
  resumenMes, flujoDeCaja, porCobrar, reporteCsv, estadisticas,
} from "./finanzas.js";

export class ErrorPanel extends Error {
  constructor(estado, mensaje) {
    super(mensaje);
    this.estado = estado;
  }
}

const pesos = (n) => "$" + Number(n).toLocaleString("es-AR");

// Devuelve el cuerpo de la respuesta, o undefined si la ruta no es de este módulo
export function atenderPanel(metodo, ruta, usuario, cuerpo = {}, consulta = new URLSearchParams()) {
  const p = ruta.split("/").filter(Boolean);
  const modulos = ["finanzas", "pagos", "gastos", "ota", "tarifas", "calendario", "turnos", "respuestas", "ajustes", "estadisticas"];
  // /tareas/:id/hecha lo atiende el servidor; acá solo el alta de tareas (POST /tareas)
  const altaDeTarea = p[0] === "tareas" && p.length === 1 && metodo === "POST";
  if (!modulos.includes(p[0]) && !altaDeTarea) return undefined;
  const permitir = (...roles) => {
    if (!roles.includes(usuario.rol)) throw new ErrorPanel(403, "Tu usuario no tiene permiso para esta acción.");
  };
  const mes = consulta.get("mes") || hoyISO().slice(0, 7);
  const gestion = ["dueno", "recepcion"].includes(usuario.rol);

  // ---- Para todos los roles ----
  if (p[0] === "calendario" && metodo === "GET") return calendarioMes(usuario, mes);
  if (p[0] === "turnos" && metodo === "GET") return agendaDelDia(consulta.get("fecha") || hoyISO(), gestion);
  if (p[0] === "respuestas" && metodo === "GET") return obtenerAjuste("preguntas");
  // Cualquiera reporta un arreglo (tarea de mantenimiento); dueño y recepción pueden crear también tareas de limpieza
  if (altaDeTarea) {
    const tipo = gestion && ["limpieza", "mantenimiento", "otro"].includes(cuerpo.tipo) ? cuerpo.tipo : "mantenimiento";
    const fecha = cuerpo.fecha || hoyISO();
    if (!/^\d{4}-\d{2}-\d{2}$/.test(fecha)) throw new Error("Fecha inválida.");
    if (cuerpo.cabanaId && !cabanaPorId(cuerpo.cabanaId)) throw new Error("Cabaña inexistente.");
    const descripcion = String(cuerpo.descripcion || "").trim();
    if (!descripcion) throw new Error("Describí qué hay que hacer.");
    const { lastInsertRowid } = db.prepare("INSERT INTO tareas (cabana_id, fecha, tipo, descripcion) VALUES (?, ?, ?, ?)")
      .run(cuerpo.cabanaId || "general", fecha, tipo, `${descripcion} (reportó ${usuario.nombre})`);
    registrar(usuario.id, `tarea de ${tipo}`, `${cabanaPorId(cuerpo.cabanaId)?.nombre || "General"} · ${descripcion}`);
    return db.prepare("SELECT * FROM tareas WHERE id = ?").get(lastInsertRowid);
  }

  // ---- Dueño y recepción ----
  if (p[0] === "turnos" && metodo === "POST") {
    permitir("dueno", "recepcion");
    const t = crearTurno(cuerpo, usuario.id);
    registrar(usuario.id, "turno", `${t.recurso_nombre} · ${t.fecha} ${t.hora} · ${t.nombre || cabanaPorId(t.cabana_id)?.nombre || ""}`);
    return t;
  }
  if (p[0] === "turnos" && metodo === "DELETE") {
    permitir("dueno", "recepcion");
    const t = borrarTurno(Number(p[1]));
    registrar(usuario.id, "turno borrado", `${t.recurso_nombre} · ${t.fecha} ${t.hora}`);
    return { ok: true };
  }

  // Recepción registra los cobros (saldo al llegar, extras); el resto es solo del dueño
  if (p[0] === "pagos" && metodo === "POST") {
    permitir("dueno", "recepcion");
    const pago = registrarPago(cuerpo, usuario.id);
    registrar(usuario.id, "cobro", `${pesos(pago.monto)} · ${pago.concepto} · ${pago.medio}${pago.reserva_id ? ` · ${pago.reserva_id}` : ""}`);
    return pago;
  }
  permitir("dueno");

  if (p[0] === "finanzas" && metodo === "GET" && !p[1]) {
    return { resumen: resumenMes(mes), flujo: flujoDeCaja(mes), por_cobrar: porCobrar(), categorias: CATEGORIAS_GASTO, medios: MEDIOS, conceptos: CONCEPTOS };
  }
  if (p[0] === "finanzas" && p[1] === "reporte" && metodo === "GET") {
    return { nombre: `tierras-magicas-${mes}.csv`, csv: reporteCsv(mes) };
  }
  if (p[0] === "pagos" && metodo === "DELETE") {
    const pago = borrarPago(Number(p[1]));
    registrar(usuario.id, "cobro borrado", `${pesos(pago.monto)} · ${pago.fecha}`);
    return { ok: true };
  }
  if (p[0] === "gastos" && metodo === "POST" && !p[1]) {
    const g = crearGasto(cuerpo, usuario.id);
    registrar(usuario.id, "gasto", `${pesos(g.monto)} · ${g.categoria} · ${g.concepto}${g.mensual ? " (mensual)" : ""}`);
    return g;
  }
  if (p[0] === "gastos" && p[2] === "baja" && metodo === "POST") {
    const g = darDeBajaGasto(Number(p[1]), cuerpo.hasta);
    registrar(usuario.id, "gasto mensual dado de baja", `${g.concepto} · último mes ${g.hasta}`);
    return g;
  }
  if (p[0] === "gastos" && metodo === "DELETE") {
    const g = borrarGasto(Number(p[1]));
    registrar(usuario.id, "gasto borrado", `${pesos(g.monto)} · ${g.concepto}`);
    return { ok: true };
  }
  if (p[0] === "ota" && metodo === "POST") {
    const o = actualizarOta(Number(p[1]), cuerpo, usuario.id);
    registrar(usuario.id, "monto de plataforma", `${o.origen} · ${o.desde} a ${o.hasta} · ${o.cancelada === 2 ? "no es reserva" : o.monto_neto ? pesos(o.monto_neto) : "sin monto"}`);
    return o;
  }
  if (p[0] === "estadisticas" && metodo === "GET") return estadisticas(consulta.get("hasta") || mes);
  // Respuestas para clientes (también son las preguntas frecuentes de la web)
  if (p[0] === "respuestas" && metodo === "POST") {
    const r = p[1] === "restablecer" ? restablecerAjuste("preguntas") : guardarAjuste("preguntas", cuerpo.preguntas);
    registrar(usuario.id, "respuestas para clientes", p[1] === "restablecer" ? "restablecidas" : `${r.valor.length} preguntas`);
    return r;
  }
  // Recursos de turnos y calendarios de Airbnb/Booking
  if (p[0] === "ajustes" && ["recursos", "canales"].includes(p[1])) {
    if (metodo === "GET") return obtenerAjuste(p[1]);
    if (metodo === "POST") {
      const r = p[2] === "restablecer" ? restablecerAjuste(p[1]) : guardarAjuste(p[1], cuerpo.valor);
      registrar(usuario.id, p[1] === "recursos" ? "recursos de turnos" : "calendarios de Airbnb/Booking", p[2] === "restablecer" ? "restablecidos" : "actualizados");
      return r;
    }
  }
  if (p[0] === "tarifas" && metodo === "GET") return obtenerTarifas();
  if (p[0] === "tarifas" && metodo === "POST" && !p[1]) {
    const t = guardarTarifas(cuerpo);
    registrar(usuario.id, "tarifas y temporadas actualizadas", `${t.calendario.length} tramos de calendario`);
    return t;
  }
  if (p[0] === "tarifas" && p[1] === "restablecer" && metodo === "POST") {
    const t = restablecerTarifas();
    registrar(usuario.id, "tarifas restablecidas", "valores de config.json");
    return t;
  }
  // Vista previa: cotiza una estadía con las tarifas propuestas, sin guardarlas
  if (p[0] === "tarifas" && p[1] === "cotizar" && metodo === "POST") {
    const { cabanaId, checkin, checkout, huespedes, tarifas } = cuerpo;
    const cabana = cabanaPorId(cabanaId);
    if (!cabana) throw new Error("Cabaña inexistente.");
    if (!checkin || !checkout || checkout <= checkin) throw new Error("Elegí fechas de ingreso y salida.");
    const calcular = () => cotizar(cabana, checkin, checkout, Number(huespedes) || 2);
    return tarifas ? conTarifas(tarifas, calcular) : calcular();
  }
  throw new ErrorPanel(404, "Ruta inexistente");
}
