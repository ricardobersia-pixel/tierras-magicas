// Asistente IA (Claude) para responder consultas de huéspedes.
// - modo "web": chat del sitio, habla directo con el huésped.
// - modo "whatsapp": redacta un borrador que el dueño revisa y envía desde WhatsApp Business.
import Anthropic from "@anthropic-ai/sdk";
import { config, env } from "./config.js";
import { buscarDisponibilidad, hoyISO, noches } from "./reservas.js";
import { pronostico } from "./solunar.js";

const client = env.iaActiva ? new Anthropic() : null;
const MODELO = "claude-opus-5-5";

const herramientas = [
  {
    name: "consultar_disponibilidad",
    description:
      "Consulta qué cabañas están libres entre dos fechas para una cantidad de huéspedes, con el precio total, la seña y el saldo en pesos argentinos. Usar siempre antes de afirmar disponibilidad o precios.",
    strict: true,
    input_schema: {
      type: "object",
      properties: {
        checkin: { type: "string", description: "Fecha de ingreso AAAA-MM-DD" },
        checkout: { type: "string", description: "Fecha de salida AAAA-MM-DD" },
        huespedes: { type: "integer", description: "Cantidad de personas" },
      },
      required: ["checkin", "checkout", "huespedes"],
      additionalProperties: false,
    },
  },
  {
    name: "pronostico_pesca",
    description:
      "Pronóstico solunar de pesca en el complejo para un rango de fechas (máximo 62 días): puntaje 0-100 por día, fase lunar, salida y puesta del sol y horarios de los períodos mayores y menores. Usar cuando pregunten por pesca o por los mejores días para pescar.",
    strict: true,
    input_schema: {
      type: "object",
      properties: {
        desde: { type: "string", description: "Primer día AAAA-MM-DD" },
        hasta: { type: "string", description: "Último día AAAA-MM-DD" },
      },
      required: ["desde", "hasta"],
      additionalProperties: false,
    },
  },
];

function sistema(modo) {
  const n = config.negocio;
  const datos = {
    negocio: n.nombre,
    ubicacion: n.ubicacion,
    check_in: n.check_in,
    check_out: n.check_out,
    pago: `Seña del ${n.sena_porcentaje}% del total para asegurar la fecha y el resto al llegar${n.permite_pago_total ? "; también se puede pagar el total" : ""}. Medios: transferencia bancaria o Mercado Pago.`,
    temporada_alta: config.temporadas.map((t) => `${t.nombre}: ${t.desde} a ${t.hasta} (MM-DD)`),
    tarifas_temporada_alta: "En temporada alta el precio es en dólares y se cobra en pesos al tipo de cambio vigente.",
    politicas: n.politicas,
    servicios: n.servicios,
    como_llegar: n.como_llegar,
    preguntas_frecuentes: n.preguntas_frecuentes,
    cabanas: config.cabanas.map((c) => ({
      nombre: c.nombre, capacidad: c.capacidad, descripcion: c.descripcion, minimo_noches: c.minimo_noches, tarifas_por_noche: c.tarifas,
    })),
  };
  const canal =
    modo === "whatsapp"
      ? `Redactás un borrador de respuesta por WhatsApp que el dueño va a revisar antes de enviar. Devolvé solo el texto del mensaje, listo para copiar, sin comillas ni comentarios para el dueño.`
      : `Estás en el chat del sitio web. Cuando el huésped quiera reservar, dale el enlace ${env.baseUrl}/?checkin=AAAA-MM-DD&checkout=AAAA-MM-DD&huespedes=N#reservar con sus datos. Para pedidos especiales, ofrecé seguir por WhatsApp: https://wa.me/${n.whatsapp}`;
  return `Sos el asistente de reservas de ${n.nombre}, un complejo de cabañas en Argentina. Respondés en español rioplatense, cálido y breve (2 a 5 oraciones), como lo haría el anfitrión.

${canal}

Reglas:
- Para disponibilidad y precios usá siempre la herramienta consultar_disponibilidad; nunca inventes precios ni fechas libres.
- Si falta un dato (fechas o cantidad de personas), preguntalo.
- Si algo no está en la información del negocio o un dato figura como [COMPLETAR], decí que lo confirma el anfitrión; no lo inventes.
- Los totales que devuelve la herramienta están en pesos argentinos; escribilos con formato $145.000. Si la estadía incluye temporada alta, aclará que esas noches se cotizan en dólares.
- No confirmes reservas: la reserva se confirma solo al pagar la seña.
- Para preguntas de pesca usá pronostico_pesca. Aclará que la tabla solunar es orientativa (tradición de pescadores, sin validación científica) y que la pesca requiere el permiso provincial vigente. Si sugerís fechas, consultá también la disponibilidad. El pronóstico completo está en ${env.baseUrl}/pesca.

Información del negocio:
${JSON.stringify(datos, null, 2)}`;
}

function ejecutarHerramienta(nombre, entrada) {
  if (nombre === "consultar_disponibilidad") {
    return buscarDisponibilidad(entrada.checkin, entrada.checkout, Number(entrada.huespedes));
  }
  if (nombre === "pronostico_pesca") {
    return pronostico(entrada.desde, noches(entrada.desde, entrada.hasta) + 1).map(({ periodos, ...d }) => ({
      ...d,
      periodos: periodos.map(({ desde, hasta, ...p }) => p),
    }));
  }
  return { error: `Herramienta desconocida: ${nombre}` };
}

const SIN_IA = `En este momento el asistente automático no está activo. Escribinos por WhatsApp y te respondemos enseguida: https://wa.me/${config.negocio.whatsapp}`;

/**
 * @param {Anthropic.Beta.BetaMessageParam[]} historial  mensajes previos (role user/assistant, content texto)
 * @param {"web"|"whatsapp"} modo
 */
export async function responder(historial, modo = "web") {
  if (!client) return SIN_IA;

  const messages = historial.slice(-20).map((m) => ({ role: m.role, content: String(m.content).slice(0, 4000) }));
  // La fecha va en el último turno para no invalidar la caché del prompt de sistema
  messages.push({ role: "system", content: `Hoy es ${hoyISO()} (zona horaria de Argentina).` });

  for (let vuelta = 0; vuelta < 6; vuelta++) {
    const respuesta = await client.beta.messages.create({
      model: MODELO,
      max_tokens: 16000,
      system: [{ type: "text", text: sistema(modo), cache_control: { type: "ephemeral" } }],
      tools: herramientas,
      messages,
      output_config: { effort: "low" },
      betas: ["server-side-fallback-2026-07-01"],
      fallbacks: "default",
    });

    if (respuesta.stop_reason === "refusal") return SIN_IA;

    if (respuesta.stop_reason !== "tool_use") {
      const texto = respuesta.content.filter((b) => b.type === "text").map((b) => b.text).join("\n").trim();
      return texto || SIN_IA;
    }

    messages.push({ role: "assistant", content: respuesta.content });
    const resultados = respuesta.content
      .filter((b) => b.type === "tool_use")
      .map((b) => {
        let contenido;
        let esError = false;
        try {
          contenido = JSON.stringify(ejecutarHerramienta(b.name, b.input));
        } catch (e) {
          contenido = String(e.message);
          esError = true;
        }
        return { type: "tool_result", tool_use_id: b.id, content: contenido, is_error: esError };
      });
    messages.push({ role: "user", content: resultados });
  }
  return SIN_IA;
}
