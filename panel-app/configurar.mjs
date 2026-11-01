// Fija la dirección del panel publicado en la app antes de compilar el APK.
// Uso: node configurar.mjs https://tu-panel.up.railway.app   (o variable TM_PANEL_URL)
import fs from "node:fs";

const entrada = (process.argv[2] || process.env.TM_PANEL_URL || "").trim();
let url;
try {
  url = new URL(entrada);
} catch {
  console.error("Falta la dirección del panel. Ejemplo: node configurar.mjs https://tierras-magicas-production.up.railway.app");
  process.exit(1);
}
if (url.protocol !== "https:") {
  console.error("La dirección del panel tiene que empezar con https://");
  process.exit(1);
}
const panel = `${url.origin}/admin`;

const config = JSON.parse(fs.readFileSync("capacitor.config.json", "utf8"));
config.server.url = panel;
fs.writeFileSync("capacitor.config.json", JSON.stringify(config, null, 2) + "\n");

const pagina = "www/sin-conexion.html";
fs.writeFileSync(pagina, fs.readFileSync(pagina, "utf8").replace(/const PANEL = ".*?";/, `const PANEL = ${JSON.stringify(panel)};`));

console.log(`La app abre ${panel}`);
