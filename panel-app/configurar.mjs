// Opcional: fija de antemano la dirección del panel en el APK (la app ya no la pide al abrirse).
// Uso: node configurar.mjs https://tu-panel.up.railway.app   (o variable TM_PANEL_URL)
// Sin dirección, el APK la pide la primera vez que se abre.
import fs from "node:fs";
import { normalizar } from "./www/panel.js";

const entrada = (process.argv[2] || process.env.TM_PANEL_URL || "").trim();
if (!entrada) {
  console.log("Sin TM_PANEL_URL: la app pedirá la dirección del panel al abrirse.");
  process.exit(0);
}
let origen;
try {
  origen = normalizar(entrada);
} catch (e) {
  console.error(e.message);
  process.exit(1);
}
const archivo = "www/panel.js";
fs.writeFileSync(archivo, fs.readFileSync(archivo, "utf8").replace(/const PREDETERMINADA = ".*?";/, `const PREDETERMINADA = ${JSON.stringify(origen)};`));
console.log(`La app abre ${origen}/admin`);
