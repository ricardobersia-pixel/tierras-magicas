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
  // Las fotos quedan en la base del teléfono: más chicas y dentro de la página (no hay servidor que las sirva)
  fotoMaxLado: 800,
  fotosEnLinea: true,
};

export function cabanaPorId(id) {
  return config.cabanas.find((c) => c.id === id);
}
