/* global __dirname, process, console */
// Exporta el Welcome Book a PDF.
// Uso: WIFI_CLAVE=xxxx node docs/welcome-book/exportar-pdf.cjs [idioma]
//   sin idioma (o "es"): welcome-book.html    → Welcome_Book_Tierras_Magicas.pdf
//   fr:                  welcome-book-fr.html → Welcome_Book_Tierras_Magicas_FR.pdf
//   en:                  welcome-book-en.html → Welcome_Book_Tierras_Magicas_EN.pdf
// La clave de Wi-Fi no se guarda en el repositorio: se inserta al exportar.
const { chromium } = require("playwright");
const { PDFDocument, PDFName, PDFDict, PDFArray, PDFString } = require("pdf-lib");
const fs = require("fs");
const path = require("path");

const dir = __dirname;
const idioma = (process.argv[2] || "es").toLowerCase();
const fuentes = { es: ["welcome-book.html", "Welcome_Book_Tierras_Magicas.pdf"], fr: ["welcome-book-fr.html", "Welcome_Book_Tierras_Magicas_FR.pdf"],
  en: ["welcome-book-en.html", "Welcome_Book_Tierras_Magicas_EN.pdf"] };
if (!fuentes[idioma]) { console.error("Idioma no disponible: " + idioma + ". Opciones: " + Object.keys(fuentes).join(", ")); process.exit(1); }
const salida = path.join(dir, fuentes[idioma][1]);
const clave = process.env.WIFI_CLAVE;
if (!clave) { console.error("Falta WIFI_CLAVE"); process.exit(1); }

// Chrome arma los links internos con destinos con nombre (/Dest /bienvenida), que muchos visores
// de celular (Android, WhatsApp, Drive) no siguen. Se reemplazan por una acción "ir a la página N"
// con el mismo formato que usa Canva (/XYZ al tope de la página, /F 4, sin borde), que sí funciona
// en Android, y el archivo se guarda con tabla de referencias clásica (sin flujos de objetos).
async function linksDirectos(bytes) {
  const doc = await PDFDocument.load(bytes);
  const destinos = doc.catalog.lookup(PDFName.of("Dests"), PDFDict);
  const paginas = doc.getPages();
  const numeroDe = new Map(paginas.map((p, i) => [p.ref.toString(), i + 1]));
  let cambiados = 0;
  for (const pagina of paginas) {
    const anotaciones = pagina.node.Annots();
    if (!anotaciones) continue;
    for (let i = 0; i < anotaciones.size(); i++) {
      const link = anotaciones.lookup(i, PDFDict);
      const nombre = link.get(PDFName.of("Dest"));
      if (!(nombre instanceof PDFName) || !destinos) continue;
      const destino = destinos.lookup(nombre, PDFArray);
      if (!destino) throw new Error("Link a una sección que no existe: " + nombre.asString());
      const ref = destino.get(0);
      const alto = doc.getPage(numeroDe.get(ref.toString()) - 1).getHeight();
      const ir = doc.context.obj({ Type: "Action", S: "GoTo", D: [ref, PDFName.of("XYZ"), null, alto, null] });
      link.delete(PDFName.of("Dest"));
      link.set(PDFName.of("A"), doc.context.register(ir));
      link.set(PDFName.of("F"), doc.context.obj(4));
      link.set(PDFName.of("Border"), doc.context.obj([0, 0, 0]));
      link.set(PDFName.of("Contents"), PDFString.of("Ir a la página " + numeroDe.get(ref.toString())));
      cambiados++;
    }
  }
  if (!cambiados) throw new Error("No se encontraron links internos para convertir.");
  doc.catalog.delete(PDFName.of("Dests"));
  return doc.save({ useObjectStreams: false });
}

(async () => {
  const html = fs.readFileSync(path.join(dir, fuentes[idioma][0]), "utf8").replace("{{WIFI_CLAVE}}", clave);
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
