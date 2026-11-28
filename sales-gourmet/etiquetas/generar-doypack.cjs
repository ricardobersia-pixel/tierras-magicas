// Etiqueta única (frente + ingredientes) para el doypack kraft de 10 × 15 cm con ventana.
// Hoja A4 de 4 columnas (una por sal: TM-01 | TM-02 | TM-03 | TM-04) × 10 filas = 40 etiquetas, 10 de cada sal.
// Cada etiqueta mide 45,6 × 25,5 mm.
// Uso (desde la raíz del repositorio, requiere Playwright con Chromium):
//   node sales-gourmet/etiquetas/generar-doypack.cjs
//   GUIAS=1 SALIDA=etiquetas_A4_doypack_con_guias node sales-gourmet/etiquetas/generar-doypack.cjs
// Sin fechas, cantidades ni lote. Ingredientes en orden alfabético, tomados de la app de huéspedes.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const { SALES } = require("./generar.cjs");

const DIR = __dirname;
const url = (f) => `file://${path.join(DIR, f)}`;

const COLS = 4, FILAS = Number(process.env.FILAS || 10);
const MARGEN_X = Number(process.env.MARGEN_X ?? 10);
const MARGEN_Y = Number(process.env.MARGEN_Y ?? 10);
const GAP_X = Number(process.env.GAP_X ?? 2.5);
const GAP_Y = Number(process.env.GAP_Y ?? 2.5);
const ANCHO = (210 - 2 * MARGEN_X - (COLS - 1) * GAP_X) / COLS;
const ALTO = (297 - 2 * MARGEN_Y - (FILAS - 1) * GAP_Y) / FILAS;
const PAD = 0.8; // margen interno: si el troquel corre un poco, no queda un filo blanco
const GUIAS = process.env.GUIAS === "1";
let CONTIENE = {};

const LEYENDA = "Producto artesanal · Obsequio para nuestros huéspedes<br>Guardar cerrado, en lugar fresco y seco";

function etiqueta(s) {
  const txt = CONTIENE[s.codigo] || "";
  return `<div class="celda"><div class="et" style="--fondo:${s.fondo}">
    <div class="sup">
      <div class="marca">
        <img class="logo" src="${url(`arte/${s.codigo.toLowerCase()}-logo.png`)}" alt="">
        <div class="tm">Tierras Mágicas</div>
        <div class="lugar">Villa Pehuenia · Patagonia</div>
      </div>
      <div class="sep"></div>
      <div class="centro">
        <div class="nombre">${s.nombre}</div>
        <div class="linea"></div>
        <div class="sub">${s.subtitulo}</div>
        <div class="neto">Sal gourmet · 25 g</div>
      </div>
      <img class="ilus" src="${url(`arte/${s.codigo.toLowerCase()}-ilustracion.png`)}" alt="">
    </div>
    <div class="ing"><span><b>Ingredientes:</b> ${txt.charAt(0).toUpperCase() + txt.slice(1)}.</span></div>
    <div class="pie">${LEYENDA}</div>
  </div></div>`;
}

function hoja(celdas) {
  return `<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
  @font-face { font-family: Cinzel; src: url(${url("fuentes/cinzel-latin-600-normal.woff2")}); font-weight: 600; }
  @font-face { font-family: "Great Vibes"; src: url(${url("fuentes/great-vibes-latin-400-normal.woff2")}); }
  @font-face { font-family: Lato; src: url(${url("fuentes/lato-latin-400-normal.woff2")}); font-weight: 400; }
  @font-face { font-family: Lato; src: url(${url("fuentes/lato-latin-700-normal.woff2")}); font-weight: 700; }
  @page { size: A4; margin: 0; }
  * { box-sizing: border-box; }
  html, body { margin: 0; width: 210mm; height: 297mm; background: #fff; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .grilla { position: absolute; left: ${MARGEN_X}mm; top: ${MARGEN_Y}mm; display: grid;
    grid-template-columns: repeat(${COLS}, ${ANCHO}mm); grid-auto-rows: ${ALTO}mm; column-gap: ${GAP_X}mm; row-gap: ${GAP_Y}mm; }
  .celda { width: ${ANCHO}mm; height: ${ALTO}mm; padding: ${PAD}mm; ${GUIAS ? "outline: 0.1mm dashed #bbb;" : ""} }
  .celda > img { display: block; width: 100%; height: 100%; }
  .et { position: relative; width: 100%; height: 100%; border-radius: 1.4mm; overflow: hidden; color: #f4e9d2;
    background: radial-gradient(ellipse at 50% 30%, color-mix(in srgb, var(--fondo) 80%, #fff 6%), var(--fondo) 75%);
    display: flex; flex-direction: column; padding: 1.2mm 1.5mm 1.15mm; font-family: Lato, sans-serif; }
  .et::after { content: ""; position: absolute; inset: 0.6mm; border: 0.2mm solid #c9a24a; border-radius: 1mm; pointer-events: none; }
  .sup { display: flex; height: 10.2mm; gap: 0.9mm; flex: none; align-items: stretch; }
  .marca { width: 11mm; flex: none; display: flex; flex-direction: column; align-items: center; justify-content: center; }
  .logo { width: 10.5mm; height: 5.4mm; object-fit: contain; }
  .tm { font-family: "Great Vibes", cursive; color: #e6c06a; font-size: 5.2pt; line-height: 1; margin-top: 0.2mm; white-space: nowrap; }
  .lugar { font-weight: 700; color: #e6c06a; font-size: 2.1pt; letter-spacing: 0.05em; text-transform: uppercase; margin-top: 0.3mm; white-space: nowrap; }
  .sep { width: 0.2mm; background: #c9a24a; opacity: 0.8; flex: none; }
  .centro { flex: 1; min-width: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
  .nombre { font-family: Cinzel, serif; font-size: 5.1pt; line-height: 1.05; text-transform: uppercase; white-space: nowrap; }
  .linea { width: 92%; border-top: 0.25mm dotted #e6c06a; margin: 0.5mm 0 0.45mm; }
  .sub { font-weight: 700; color: #e6c06a; font-size: 3pt; letter-spacing: 0.03em; text-transform: uppercase; line-height: 1.2; }
  .neto { font-size: 2.6pt; letter-spacing: 0.06em; text-transform: uppercase; color: #c9a24a; margin-top: 0.4mm; white-space: nowrap; }
  .ilus { width: 7.2mm; flex: none; height: 100%; object-fit: contain; }
  /* Recuadro claro para leer bien los ingredientes */
  .ing { flex: 1; margin-top: 0.6mm; background: #fbf6ea; color: #2b1d14; border-radius: 0.7mm;
    display: flex; align-items: center; padding: 0.5mm 1mm; font-size: 4.1pt; line-height: 1.15; }
  .pie { font-size: 3.3pt; line-height: 1.15; letter-spacing: 0.02em; color: #c9a24a; margin-top: 0.5mm; text-align: center; white-space: nowrap; }
  </style></head><body><div class="grilla">${celdas.join("")}</div></body></html>`;
}

(async () => {
  const { SALES: DATOS } = await import(require("url").pathToFileURL(path.join(DIR, "..", "www", "js", "datos.js")).href);
  CONTIENE = Object.fromEntries(DATOS.map((d) => [d.codigo, d.contiene]));
  const b = await chromium.launch();
  const salida = process.env.SALIDA || "etiquetas_A4_doypack";
  const html = path.join(DIR, `.${salida}.html`);

  // 1) Cada sal se dibuja una vez como imagen de ~680 ppp: los visores de PDF de los teléfonos
  //    dibujan mal los degradados de CSS (etiquetas rosadas, recuadros blancos); con imágenes se ve igual en todos lados.
  fs.writeFileSync(html, hoja(SALES.map(etiqueta)));
  const raster = await b.newPage({ deviceScaleFactor: 7, viewport: { width: 794, height: 1123 } });
  await raster.goto(`file://${html}`);
  await raster.evaluate(() => document.fonts.ready);
  const ets = await raster.locator(".et").all();
  const imgs = [];
  for (const e of ets) imgs.push(`data:image/png;base64,${(await e.screenshot({ type: "png" })).toString("base64")}`);
  await raster.close();

  // 2) La hoja final coloca esas imágenes: una sal por columna
  const celdas = Array.from({ length: FILAS }, () => imgs.map((src) => `<div class="celda"><img src="${src}" alt=""></div>`)).flat();
  fs.writeFileSync(html, hoja(celdas));
  const page = await b.newPage();
  await page.goto(`file://${html}`);
  await page.pdf({ path: path.join(DIR, `${salida}.pdf`), format: "A4", printBackground: true, preferCSSPageSize: true });
  const alta = await b.newPage({ deviceScaleFactor: 2, viewport: { width: 794, height: 1123 } });
  await alta.goto(`file://${html}`);
  await alta.screenshot({ path: path.join(DIR, `${salida}.png`), fullPage: true });
  fs.unlinkSync(html);
  await b.close();
  console.log(`Listo: ${salida}.pdf (${FILAS * COLS} etiquetas de ${ANCHO.toFixed(1)} × ${ALTO.toFixed(1)} mm)`);
})();
