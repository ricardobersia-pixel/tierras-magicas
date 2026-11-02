// Rutas del panel para finanzas y tarifas. Las usan el servidor (server.js) y la app de prueba del teléfono,
// así los permisos y la lógica son los mismos en los dos.
import { cabanaPorId } from "./config.js";
import { cotizar, hoyISO } from "./reservas.js";
import { registrar } from "./usuarios.js";
import { obtenerTarifas, guardarTarifas, restablecerTarifas, conTarifas } from "./ajustes.js";
import {
  CATEGORIAS_GASTO, MEDIOS, CONCEPTOS, registrarPago, borrarPago, crearGasto, darDeBajaGasto, borrarGasto, actualizarOta,
  resumenMes, flujoDeCaja, porCobrar, reporteCsv,
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
  if (!["finanzas", "pagos", "gastos", "ota", "tarifas"].includes(p[0])) return undefined;
  const permitir = (...roles) => {
    if (!roles.includes(usuario.rol)) throw new ErrorPanel(403, "Tu usuario no tiene permiso para esta acción.");
  };
  const mes = consulta.get("mes") || hoyISO().slice(0, 7);

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
