// Rutas del panel para finanzas y tarifas. Las usan el servidor (server.js) y la app de prueba del teléfono,
// así los permisos y la lógica son los mismos en los dos.
import { cabanaPorId } from "./config.js";
import { cotizar, hoyISO } from "./reservas.js";
import { registrar } from "./usuarios.js";
import { obtenerTarifas, guardarTarifas, restablecerTarifas, conTarifas, obtenerAjuste, guardarAjuste, restablecerAjuste } from "./ajustes.js";
import { calendarioMes } from "./panel.js";
import { agendaDelDia, crearTurno, borrarTurno } from "./turnos.js";
import { tareasAbiertas, historialTareas, crearTarea, moverTarea } from "./tareas.js";
import { obtenerMensajes, guardarPlantillas, restablecerPlantillas, mensajesDeReserva, mensajesPendientes, marcarEnviado } from "./mensajes.js";
import { obtenerUnidades, crearUnidad, actualizarUnidad, borrarUnidad, agregarFoto, borrarFoto, fotoPrincipal } from "./unidades.js";
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
  const modulos = ["finanzas", "pagos", "gastos", "ota", "tarifas", "calendario", "turnos", "respuestas", "ajustes", "estadisticas", "unidades", "tareas", "mensajes"];
  if (!modulos.includes(p[0])) return undefined;
  const permitir = (...roles) => {
    if (!roles.includes(usuario.rol)) throw new ErrorPanel(403, "Tu usuario no tiene permiso para esta acción.");
  };
  const mes = consulta.get("mes") || hoyISO().slice(0, 7);
  const gestion = ["dueno", "recepcion"].includes(usuario.rol);

  // ---- Para todos los roles ----
  if (p[0] === "calendario" && metodo === "GET") return calendarioMes(usuario, mes);
  if (p[0] === "turnos" && metodo === "GET") return agendaDelDia(consulta.get("fecha") || hoyISO(), gestion);
  if (p[0] === "respuestas" && metodo === "GET") return obtenerAjuste("preguntas");
  // Tareas: cualquiera reporta un arreglo (tarea de mantenimiento; limpieza también de limpieza);
  // dueño y recepción crean de cualquier tipo. Cada uno toma, suelta y marca hechas las de su tipo.
  if (p[0] === "tareas") {
    if (metodo === "GET" && !p[1]) return tareasAbiertas(usuario);
    if (metodo === "GET" && p[1] === "historial") return historialTareas(usuario);
    if (metodo === "POST" && !p[1]) {
      const t = crearTarea(usuario, cuerpo);
      registrar(usuario.id, `tarea de ${t.tipo}${t.prioridad === "urgente" ? " (urgente)" : ""}`, `${cabanaPorId(t.cabana_id)?.nombre || "General"} · ${t.descripcion}`);
      return t;
    }
    if (metodo === "POST" && p[1] && p[2]) {
      const t = moverTarea(usuario, p[1], p[2]);
      registrar(usuario.id, `tarea: ${p[2]}`, `${t.tipo} · ${cabanaPorId(t.cabana_id)?.nombre || "General"} · ${t.fecha}`);
      return t;
    }
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

  // Unidades de alquiler: recepción las ve (con fotos, para mandar a clientes); el dueño las edita
  if (p[0] === "unidades" && metodo === "GET") {
    permitir("dueno", "recepcion");
    return obtenerUnidades();
  }

  // Mensajes al huésped: dueño y recepción los mandan; el dueño edita las plantillas (más abajo)
  if (p[0] === "mensajes" && !(metodo === "POST" && (!p[1] || p[1] === "restablecer"))) {
    permitir("dueno", "recepcion");
    if (metodo === "GET" && !p[1]) return obtenerMensajes();
    if (metodo === "GET" && p[1] === "pendientes") return mensajesPendientes();
    if (metodo === "GET" && p[1] === "reserva" && p[2]) return mensajesDeReserva(p[2]);
    if (["POST", "DELETE"].includes(metodo) && p[1] === "reserva" && p[2] && p[3]) {
      const m = marcarEnviado(p[2], p[3], usuario.id, metodo === "POST");
      registrar(usuario.id, metodo === "POST" ? "mensaje al huésped" : "mensaje desmarcado", `${p[2]} · ${p[3]}`);
      return m;
    }
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
  if (p[0] === "unidades" && metodo === "POST" && !p[1]) {
    const u = crearUnidad(cuerpo);
    registrar(usuario.id, "unidad nueva", `${u.nombre} (${u.tipo})`);
    return u;
  }
  if (p[0] === "unidades" && metodo === "POST" && p[1] && !p[2]) {
    const u = actualizarUnidad(p[1], cuerpo);
    registrar(usuario.id, "unidad actualizada", u.nombre);
    return u;
  }
  if (p[0] === "unidades" && metodo === "DELETE" && p[1] && !p[2]) {
    const u = borrarUnidad(p[1]);
    registrar(usuario.id, "unidad borrada", u.nombre);
    return { ok: true };
  }
  if (p[0] === "unidades" && p[2] === "fotos") {
    if (metodo === "POST" && !p[3]) {
      const f = agregarFoto(p[1], cuerpo.datos);
      registrar(usuario.id, "foto subida", f.unidad.nombre);
      return obtenerUnidades();
    }
    if (metodo === "POST" && p[4] === "principal") {
      fotoPrincipal(p[1], p[3]);
      return obtenerUnidades();
    }
    if (metodo === "DELETE" && p[3]) {
      borrarFoto(p[1], p[3]);
      registrar(usuario.id, "foto borrada", p[1]);
      return obtenerUnidades();
    }
  }
  if (p[0] === "mensajes" && metodo === "POST") {
    const m = p[1] === "restablecer" ? restablecerPlantillas() : guardarPlantillas(cuerpo.plantillas);
    registrar(usuario.id, "mensajes al huésped", p[1] === "restablecer" ? "restablecidos" : `${m.plantillas.length} plantillas`);
    return m;
  }
  if (p[0] === "estadisticas" && metodo === "GET") return estadisticas(consulta.get("hasta") || mes);
  // Respuestas para clientes (también son las preguntas frecuentes de la web)
  if (p[0] === "respuestas" && metodo === "POST") {
    const r = p[1] === "restablecer" ? restablecerAjuste("preguntas") : guardarAjuste("preguntas", cuerpo.preguntas);
    registrar(usuario.id, "respuestas para clientes", p[1] === "restablecer" ? "restablecidas" : `${r.valor.length} preguntas`);
    return r;
  }
  // Calendarios de Airbnb/Booking (los recursos de turnos se editan en Unidades)
  if (p[0] === "ajustes" && p[1] === "canales") {
    if (metodo === "GET") return obtenerAjuste(p[1]);
    if (metodo === "POST") {
      const r = p[2] === "restablecer" ? restablecerAjuste(p[1]) : guardarAjuste(p[1], cuerpo.valor);
      registrar(usuario.id, "calendarios de Airbnb/Booking", p[2] === "restablecer" ? "restablecidos" : "actualizados");
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
