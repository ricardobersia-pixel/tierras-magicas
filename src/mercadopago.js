// Integración con Mercado Pago Checkout Pro vía API REST
// Docs: https://www.mercadopago.com.ar/developers/es/docs/checkout-pro/landing
import { env, cabanaPorId } from "./config.js";

const API = "https://api.mercadopago.com";

async function mp(ruta, opciones = {}) {
  const res = await fetch(API + ruta, {
    ...opciones,
    headers: {
      Authorization: `Bearer ${env.mpAccessToken}`,
      "Content-Type": "application/json",
      ...(opciones.headers || {}),
    },
    signal: AbortSignal.timeout(20000),
  });
  const cuerpo = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`Mercado Pago ${res.status}: ${cuerpo.message || JSON.stringify(cuerpo)}`);
  return cuerpo;
}

export const mpActivo = () => Boolean(env.mpAccessToken);

// Crea el link de pago de la seña
export async function crearPreferencia(reserva) {
  const cabana = cabanaPorId(reserva.cabana_id);
  const pref = await mp("/checkout/preferences", {
    method: "POST",
    headers: { "X-Idempotency-Key": `pref-${reserva.id}` },
    body: JSON.stringify({
      items: [
        {
          id: reserva.id,
          title: `Seña ${cabana.nombre} — ${reserva.checkin} a ${reserva.checkout}`,
          quantity: 1,
          currency_id: "ARS",
          unit_price: reserva.sena,
        },
      ],
      payer: { name: reserva.nombre, email: reserva.email || undefined },
      external_reference: reserva.id,
      back_urls: {
        success: `${env.baseUrl}/reserva/${reserva.id}`,
        pending: `${env.baseUrl}/reserva/${reserva.id}`,
        failure: `${env.baseUrl}/reserva/${reserva.id}`,
      },
      auto_return: env.baseUrl.startsWith("https://") ? "approved" : undefined,
      notification_url: env.baseUrl.startsWith("https://") ? `${env.baseUrl}/webhooks/mercadopago` : undefined,
      expires: true,
      expiration_date_to: new Date(Date.now() + 30 * 60000).toISOString(),
      statement_descriptor: "TIERRASMAGICAS",
    }),
  });
  return pref;
}

export async function obtenerPago(paymentId) {
  return mp(`/v1/payments/${encodeURIComponent(paymentId)}`);
}
