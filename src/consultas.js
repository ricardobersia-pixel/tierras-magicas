import { config, cabanaPorId } from "./config.js";
import { buscarDisponibilidad, cotizar, estaLibre, dormiLibre, validarRango, noches } from "./reservas.js";

// Respuestas a consultas de reserva por WhatsApp, armadas con el cuadro tarifario del panel (Tarifas):
// el mismo cálculo que la web y las reservas (temporada de cada noche, día de semana o fin de semana,
// descuento directo, mínimo de noches, seña y dormi). Reemplaza a los mensajes con precio fijo.
// Tres pasos: bienvenida (pide datos) → cotización (precio para esas fechas) → cómo reservar (seña y políticas).

const pesos = (n) => "$" + Number(n).toLocaleString("es-AR");
const fechaCorta = (iso) => new Date(iso + "T12:00:00Z").toLocaleDateString("es-AR", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" });
// Las descripciones internas pueden tener marcas para el dueño ([CONFIRMAR], [COMPLETAR]): no van al huésped
const sinMarcas = (s) => String(s || "").replace(/\s*\[[^\]]*\]/g, "").trim();

export function bienvenida() {
  const n = config.negocio;
  return `¡Hola! 👋 Gracias por escribir a *${n.nombre}*, casas de montaña en ${n.ubicacion}.\n\n` +
    "Para pasarte disponibilidad y precio exacto, contanos:\n" +
    "1️⃣ Fecha de llegada y de salida\n2️⃣ Cuántas personas son\n3️⃣ Si viajan con mascota\n\n" +
    "Te respondemos enseguida 🌲";
}

function incluido() {
  return "✅ *Incluido sin costo extra:*\n" +
    "• Tina caliente (jacuzzi) y sauna\n" +
    "• Kayaks, stand up, airtrack e isla flotante\n" +
    "• Wifi mesh en todo el complejo con Starlink de alta velocidad\n" +
    "• Calefacción a pellets y Smart TV\n" +
    "• Sábanas, toallas, frazadas, amenities y básicos de cocina";
}

function validarConsulta({ checkin, checkout, huespedes }) {
  const error = validarRango(checkin, checkout);
  if (error) throw new Error(error);
  const h = Number(huespedes);
  if (!(Number.isInteger(h) && h >= 1 && h <= 30)) throw new Error("Indicá cuántas personas son.");
  return h;
}

// Cotización de todas las cabañas para esas fechas y el mensaje con las disponibles
export function cotizarConsulta({ checkin, checkout, huespedes, mascota = false }) {
  const h = validarConsulta({ checkin, checkout, huespedes });
  const r = buscarDisponibilidad(checkin, checkout, h);
  const n = r.noches;
  const cabanas = r.cabanas.map((c) => ({
    id: c.id, nombre: c.nombre, capacidad: c.capacidad, disponible: c.disponible, motivo: c.motivo,
    total: c.total, sena: c.sena, sena_porcentaje: c.sena_porcentaje, temporada_nombre: c.temporada_nombre,
    minimo_noches: c.minimo_noches, adicionales: c.adicionales, total_adicionales: c.total_adicionales,
  }));
  const libres = r.cabanas.filter((c) => c.disponible);
  const encabezado = `Para el ${fechaCorta(checkin)} al ${fechaCorta(checkout)} (${n} ${n === 1 ? "noche" : "noches"}, ${h} ${h === 1 ? "persona" : "personas"})`;
  let mensaje;
  if (!libres.length) {
    const minimo = Math.max(...r.cabanas.map((c) => c.minimo_noches), 0);
    const porMinimo = r.cabanas.length && r.cabanas.every((c) => c.motivo?.startsWith("mínimo"));
    mensaje = `¡Gracias por escribirnos! ${encabezado} no tenemos disponibilidad` +
      (porMinimo ? `: en esas fechas la estadía mínima es de ${minimo} noches.` : ".") +
      "\n\n¿Te sirve otra fecha? Decinos y te pasamos opciones 🙌";
  } else {
    // Cabañas iguales (misma capacidad, descripción y precio) van en una sola opción: "Cabaña 1 o Cabaña 2"
    const grupos = [];
    for (const c of libres) {
      const desc = sinMarcas(cabanaPorId(c.id)?.descripcion);
      const g = grupos.find((x) => x.capacidad === c.capacidad && x.total === c.total && x.desc === desc && x.adicionales === c.adicionales);
      if (g) g.nombres.push(c.nombre);
      else grupos.push({ ...c, desc, nombres: [c.nombre] });
    }
    const opciones = grupos.map((c) => {
      const dormi = c.adicionales ? `\n   Incluye dormi para ${c.adicionales} ${c.adicionales === 1 ? "persona" : "personas"} más (${pesos(c.total_adicionales)}).` : "";
      return `🏡 *${c.nombres.join(" o ")}* (hasta ${c.capacidad} personas)\n   💰 *${pesos(c.total)}* en total${c.desc ? `\n   ${c.desc}` : ""}${dormi}`;
    }).join("\n\n");
    const descuento = config.negocio.precio_directo_descuento;
    mensaje = `¡Gracias por escribirnos! ${encabezado} tenemos disponible:\n\n${opciones}\n\n` +
      (descuento ? `Es precio directo: ${descuento}% menos que en Booking y Airbnb.\n\n` : "") +
      `${incluido()}\n\n` +
      (mascota ? "🐕 Aceptamos mascotas de tamaño mediano.\n" : "") +
      "📍 A unos 50 m del lago por un sendero entre ñires, con vista a la cordillera.\n\n¿Te mando fotos y cómo reservar?";
  }
  return { checkin, checkout, noches: n, huespedes: h, cabanas, mensaje };
}

const oraciones = (s) => String(s || "").split(/(?<=\.)\s+/).filter(Boolean);

// Cancelación general (de las políticas del negocio) más lo propio de la temporada (p. ej. cambio de fechas en Media)
function politicas(c, anticipado) {
  if (anticipado) return "• El pago no es reembolsable\n";
  const general = (config.negocio.politicas || []).find((p) => /^cancelaci/i.test(p));
  const cancelacion = oraciones(general).filter((o) => !/premium/i.test(o)).join(" ");
  const extra = oraciones(String(c.politica || "").replace(/^[^:]+:\s*/, "")).filter((o) => !/seña|anticipad|días o más/i.test(o)).join(" ");
  return (cancelacion ? `• ${cancelacion}\n` : "") + (extra ? `• ${extra}\n` : "");
}

// Mensaje con la seña, los datos de pago y las políticas de la temporada, para la cabaña elegida
export function mensajeReservar({ cabanaId, checkin, checkout, huespedes, mascota = false }) {
  const h = validarConsulta({ checkin, checkout, huespedes });
  const cabana = cabanaPorId(cabanaId);
  if (!cabana) throw new Error("Elegí una cabaña.");
  const c = cotizar(cabana, checkin, checkout, h);
  if (noches(checkin, checkout) < c.minimo_noches) throw new Error(`En esas fechas la estadía mínima es de ${c.minimo_noches} noches.`);
  if (!estaLibre(cabana.id, checkin, checkout) || (c.adicionales && !dormiLibre(checkin, checkout))) throw new Error(`${cabana.nombre} no está disponible en esas fechas.`);
  const n = config.negocio;
  const t = n.transferencia || {};
  const anticipado = c.sena_porcentaje >= 100;
  return {
    cabana: cabana.nombre, ...c,
    mensaje: `¡Genial! Para reservar *${cabana.nombre}* del ${fechaCorta(checkin)} al ${fechaCorta(checkout)}:\n\n` +
      `💰 Total: *${pesos(c.total)}*\n` +
      (anticipado
        ? `💳 Se abona el *100% por adelantado: ${pesos(c.total)}* (temporada ${c.temporada_nombre}).\n`
        : `💳 *Seña del ${c.sena_porcentaje}%: ${pesos(c.sena)}*. El resto (${pesos(c.saldo)}), al llegar.\n`) +
      "Con el pago el precio queda congelado.\n\n" +
      "Podés pagar por:\n" +
      (t.alias ? `• Transferencia: alias *${t.alias}*${t.titular ? ` · titular ${t.titular}` : ""}\n` : "") +
      "• Mercado Pago: te pasamos el link\n" +
      (anticipado ? "\n" : "El saldo al llegar también se puede pagar en efectivo. Cobramos en pesos argentinos; si venís del exterior, aceptamos dólares o pesos chilenos a la cotización del día del BCRA.\n\n") +
      "📋 *Antes de pagar, tené en cuenta:*\n" +
      `• Check-in desde las ${n.check_in} h · check-out hasta las ${n.check_out} h\n` +
      politicas(c, anticipado) +
      (mascota ? "• Mascotas de tamaño mediano, avisándonos antes 🐕\n" : "") +
      "• No se fuma dentro de la cabaña\n" +
      "• La leña para el fogón, los asadores y el horno no está incluida; se pide aparte\n\n" +
      "Mandanos el comprobante con tu nombre completo y DNI, y te confirmamos al momento ✅",
  };
}
