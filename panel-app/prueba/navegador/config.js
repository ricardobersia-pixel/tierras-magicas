// Reemplaza src/config.js en la app de prueba: misma configuración del negocio, sin pagos ni IA.
import config from "../../../config.json";

export { config };

export const env = {
  baseUrl: location.origin,
  adminPassword: "",
  duenoEmail: "",
  mpAccessToken: "",
  icalSyncMinutes: 15,
  iaActiva: false,
};

export function cabanaPorId(id) {
  return config.cabanas.find((c) => c.id === id);
}
