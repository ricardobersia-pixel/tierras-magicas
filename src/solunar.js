// El motor solunar vive en la app Caza&Pesca Patagonia; acá solo se agrega la ubicación del complejo.
import { config } from "./config.js";
import { pronostico as pronosticoLugar } from "../pesca-patagonia/www/js/solunar.js";

export { pronosticoDia } from "../pesca-patagonia/www/js/solunar.js";

export function lugarNegocio() {
  const n = config.negocio;
  return { lat: Number(n.coordenadas?.lat), lon: Number(n.coordenadas?.lon), zona: n.zona_horaria };
}

export function pronostico(desdeISO, dias, lugar = lugarNegocio()) {
  return pronosticoLugar(desdeISO, dias, lugar);
}
