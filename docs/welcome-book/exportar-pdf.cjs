/* global __dirname, process, console */
// Exporta el Welcome Book a PDF.
// Uso: WIFI_CLAVE=xxxx node docs/welcome-book/exportar-pdf.cjs
// La clave de Wi-Fi no se guarda en el repositorio: se inserta al exportar.
const { chromium } = require("playwright");
const { PDFDocument, PDFName, PDFDict, PDFArray } = require("pdf-lib");
const fs = require("fs");
const path = require("path");

const dir = __dirname;
const salida = path.join(dir, "Welcome_Book_Tierras_Magicas.pdf");
const clave = process.env.WIFI_CLAVE;
if (!clave) { console.error("Falta WIFI_CLAVE"); process.exit(1); }

// Chrome arma los links internos con destinos con nombre (/Dest /bienvenida), que muchos visores
// de celular (WhatsApp, Drive, Android) no siguen. Se reemplazan por una acción "ir a la página N",
// como hace Canva, que funciona en todos los visores.
async function linksDirectos(bytes) {
  const doc = await PDFDocument.load(bytes);
  const destinos = doc.catalog.lookup(PDFName.of("Dests"), PDFDict);
  let cambiados = 0;
  for (const pagina of doc.getPages()) {
    const anotaciones = pagina.node.Annots();
    if (!anotaciones) continue;
    for (let i = 0; i < anotaciones.size(); i++) {
      const link = anotaciones.lookup(i, PDFDict);
      const nombre = link.get(PDFName.of("Dest"));
      if (!(nombre instanceof PDFName) || !destinos) continue;
      const destino = destinos.lookup(nombre, PDFArray);
      if (!destino) throw new Error("Link a una sección que no existe: " + nombre.asString());
      const ir = doc.context.obj({ S: "GoTo", D: [destino.get(0), PDFName.of("Fit")] });
      link.delete(PDFName.of("Dest"));
      link.set(PDFName.of("A"), ir);
      cambiados++;
    }
  }
  if (!cambiados) throw new Error("No se encontraron links internos para convertir.");
  return doc.save();
}

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
    const pdf = await pagina.pdf({ preferCSSPageSize: true, printBackground: true });
    fs.writeFileSync(salida, await linksDirectos(pdf));
    console.log("PDF:", salida);
  } finally {
    await navegador.close();
    fs.unlinkSync(temporal);
  }
})().catch((e) => { console.error(e.message); process.exit(1); });
