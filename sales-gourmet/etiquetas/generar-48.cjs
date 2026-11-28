// Hoja A4 de 48 etiquetas autoadhesivas (4 columnas × 12 filas), una variedad por columna:
// TM-01 | TM-02 | TM-03 | TM-04, 12 de cada una.
// Uso (desde la raíz del repositorio, requiere Playwright con Chromium):
//   node sales-gourmet/etiquetas/generar-48.cjs
// Las medidas se ajustan abajo según la hoja comprada (vienen impresas en la caja).
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const { SALES } = require("./generar.cjs");

const DIR = __dirname;
const url = (f) => `file://${path.join(DIR, f)}`;

// Medidas en mm. Por defecto: hoja de 48 etiquetas sin márgenes (52,5 × 24,75 mm, troquel a ras).
const COLS = 4, FILAS = 12;
const ANCHO = Number(process.env.ANCHO || 52.5);
const ALTO = Number(process.env.ALTO || 24.75);
const GAP_X = Number(process.env.GAP_X || 0);
const GAP_Y = Number(process.env.GAP_Y || 0);
const MARGEN_X = (210 - (COLS * ANCHO + (COLS - 1) * GAP_X)) / 2;
const MARGEN_Y = (297 - (FILAS * ALTO + (FILAS - 1) * GAP_Y)) / 2;
const GUIAS = process.env.GUIAS === "1"; // líneas de corte, solo para probar en papel común

function etiqueta(s) {
  return `<div class="celda"><div class="et" style="--fondo:${s.fondo}">
    <div class="marca">
      <img class="logo" src="${url(`arte/${s.codigo.toLowerCase()}-logo.png`)}" alt="">
      <div class="tm">Tierras Mágicas</div>
      <div class="lugar">Villa Pehuenia<br>Patagonia</div>
    </div>
    <div class="centro">
      <div class="nombre">${s.nombre}</div>
      <div class="linea"></div>
      <div class="sub">${s.subtitulo}</div>
      <div class="pie">Obsequio de la casa · 25 g</div>
    </div>
    <img class="ilus" src="${url(`arte/${s.codigo.toLowerCase()}-ilustracion.png`)}" alt="">
  </div></div>`;
}

function hoja() {
  const celdas = Array.from({ length: FILAS }, () => SALES.map(etiqueta)).flat();
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
  .celda { width: ${ANCHO}mm; height: ${ALTO}mm; padding: 1.2mm; ${GUIAS ? "outline: 0.1mm dashed #bbb;" : ""} }
  /* Margen interno de 1,2 mm: si el troquel corre un poco, no queda un filo blanco cortado */
  .et { position: relative; width: 100%; height: 100%; border-radius: 1.6mm; overflow: hidden; color: #f4e9d2;
    background: radial-gradient(ellipse at 50% 40%, color-mix(in srgb, var(--fondo) 80%, #fff 6%), var(--fondo) 75%);
    display: flex; align-items: stretch; gap: 1mm; padding: 1.3mm 1.4mm; font-family: Lato, sans-serif; }
  .et::after { content: ""; position: absolute; inset: 0.7mm; border: 0.2mm solid #c9a24a; border-radius: 1.1mm; pointer-events: none; }
  .marca { width: 12.5mm; flex: none; display: flex; flex-direction: column; align-items: center; justify-content: center;
    border-right: 0.2mm solid rgba(201,162,74,.8); padding-right: 0.8mm; }
  .logo { width: 11.5mm; height: 6.4mm; object-fit: contain; }
  .tm { font-family: "Great Vibes", cursive; color: #e6c06a; font-size: 5.6pt; line-height: 1; margin-top: 0.3mm; white-space: nowrap; }
  .lugar { font-weight: 700; color: #e6c06a; font-size: 2.6pt; letter-spacing: 0.06em; text-transform: uppercase; line-height: 1.25; text-align: center; margin-top: 0.4mm; }
  .centro { flex: 1; min-width: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
  .nombre { font-family: Cinzel, serif; font-size: 5.6pt; line-height: 1.1; text-transform: uppercase; letter-spacing: 0.01em; }
  .linea { width: 90%; border-top: 0.25mm dotted #e6c06a; margin: 0.7mm 0 0.6mm; }
  .sub { font-weight: 700; color: #e6c06a; font-size: 3.3pt; letter-spacing: 0.04em; text-transform: uppercase; line-height: 1.25; }
  .pie { font-size: 2.9pt; letter-spacing: 0.06em; text-transform: uppercase; color: #c9a24a; margin-top: 0.8mm; white-space: nowrap; }
  .ilus { width: 8.6mm; flex: none; height: 100%; object-fit: contain; }
  </style></head><body><div class="grilla">${celdas.join("")}</div></body></html>`;
}

(async () => {
  const b = await chromium.launch();
  const page = await b.newPage();
  const salida = process.env.SALIDA || "etiquetas_A4_48_surtidas";
  const html = path.join(DIR, `.${salida}.html`);
  fs.writeFileSync(html, hoja());
  await page.goto(`file://${html}`);
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: path.join(DIR, `${salida}.pdf`), format: "A4", printBackground: true, preferCSSPageSize: true });
  await page.setViewportSize({ width: 794, height: 1123 });
  const alta = await b.newPage({ deviceScaleFactor: 2, viewport: { width: 794, height: 1123 } });
  await alta.goto(`file://${html}`);
  await alta.evaluate(() => document.fonts.ready);
  await alta.screenshot({ path: path.join(DIR, `${salida}.png`), fullPage: true });
  fs.unlinkSync(html);
  await b.close();
  console.log(`Listo: ${salida}.pdf (${ANCHO} × ${ALTO} mm, márgenes ${MARGEN_X.toFixed(2)} / ${MARGEN_Y.toFixed(2)} mm)`);
})();
