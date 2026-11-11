// Exporta el Welcome Book a PDF.
// Uso: WIFI_CLAVE=xxxx node docs/welcome-book/exportar-pdf.cjs
// La clave de Wi-Fi no se guarda en el repositorio: se inserta al exportar.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const dir = __dirname;
const salida = path.join(dir, "Welcome_Book_Tierras_Magicas.pdf");
const clave = process.env.WIFI_CLAVE;
if (!clave) { console.error("Falta WIFI_CLAVE"); process.exit(1); }

(async () => {
  const html = fs.readFileSync(path.join(dir, "welcome-book.html"), "utf8").replace("{{WIFI_CLAVE}}", clave);
  const temporal = path.join(dir, ".welcome-book-export.html");
  fs.writeFileSync(temporal, html);
  const navegador = await chromium.launch();
  try {
    const pagina = await navegador.newPage();
    await pagina.goto("file://" + temporal, { waitUntil: "load" });
    const desbordes = await pagina.$$eval("section.pag", (s) =>
      s.map((e, i) => [i + 1, e.scrollHeight - e.clientHeight]).filter(([, d]) => d > 0));
    if (desbordes.length) throw new Error("Páginas con texto cortado: " + JSON.stringify(desbordes));
    await pagina.pdf({ path: salida, preferCSSPageSize: true, printBackground: true });
    console.log("PDF:", salida);
  } finally {
    await navegador.close();
    fs.unlinkSync(temporal);
  }
})().catch((e) => { console.error(e.message); process.exit(1); });
