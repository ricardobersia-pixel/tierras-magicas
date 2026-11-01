// Dirección del panel: la elige el usuario la primera vez (o viene fijada al compilar con TM_PANEL_URL).
// Solo se aceptan direcciones https de Railway (*.up.railway.app), las únicas que la app deja abrir.
const PREDETERMINADA = "";
const CLAVE = "tm-panel-url";

export function normalizar(texto) {
  let t = String(texto || "").trim();
  if (!t) throw new Error("Escribí la dirección del panel.");
  if (!/^https?:\/\//i.test(t)) t = "https://" + t;
  const url = new URL(t);
  if (url.protocol !== "https:") throw new Error("La dirección tiene que empezar con https://");
  if (!url.hostname.endsWith(".up.railway.app") || url.hostname.split(".").length !== 4) {
    throw new Error("Tiene que ser la dirección de Railway, por ejemplo tierras-magicas-production.up.railway.app");
  }
  return url.origin;
}

export function guardada() {
  try {
    return localStorage.getItem(CLAVE) || PREDETERMINADA;
  } catch {
    return PREDETERMINADA;
  }
}

export function guardar(origen) {
  try {
    localStorage.setItem(CLAVE, origen);
  } catch {}
}

export function olvidar() {
  try {
    localStorage.removeItem(CLAVE);
  } catch {}
}

export const abrir = (origen) => location.replace(origen + "/admin");
