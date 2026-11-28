// Hoja A4 de 48 etiquetas autoadhesivas (4 columnas × 12 filas), una variedad por columna:
// TM-01 | TM-02 | TM-03 | TM-04.
// Por defecto alterna filas de FRENTE y DORSO: 6 sobres completos de cada sal por hoja.
// Uso (desde la raíz del repositorio, requiere Playwright con Chromium):
//   node sales-gourmet/etiquetas/generar-48.cjs                 → frente y dorso
//   SOLO_FRENTE=1 node sales-gourmet/etiquetas/generar-48.cjs   → 12 frentes de cada sal
// El dorso no lleva fechas ni cantidades: ingredientes en orden alfabético (de la app de huéspedes), contenido y lote.
// Las medidas se ajustan abajo según la hoja comprada (vienen impresas en la caja).
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const { SALES } = require("./generar.cjs");

const DIR = __dirname;
const url = (f) => `file://${path.join(DIR, f)}`;

const COLS = 4, FILAS = 12;
// Márgenes de la hoja (bordes que la impresora no imprime) y separación entre etiquetas.
// Por defecto: 10 mm a los costados, 10 mm arriba y abajo, 2,5 mm entre columnas y 2 mm entre filas.
// El tamaño de cada etiqueta se calcula solo; si la hoja comprada indica medidas, se pasan con ANCHO y ALTO.
const MARGEN_X = Number(process.env.MARGEN_X ?? 10);
const MARGEN_Y = Number(process.env.MARGEN_Y ?? 10);
const GAP_X = Number(process.env.GAP_X ?? 2.5);
const GAP_Y = Number(process.env.GAP_Y ?? 2);
const ANCHO = Number(process.env.ANCHO || (210 - 2 * MARGEN_X - (COLS - 1) * GAP_X) / COLS);
const ALTO = Number(process.env.ALTO || (297 - 2 * MARGEN_Y - (FILAS - 1) * GAP_Y) / FILAS);
// El diseño está dibujado para 52,5 × 24,75 mm y se escala para entrar en la etiqueta
const PAD = 0.8;
const BASE_W = 52.5 - 2.4, BASE_H = 24.75 - 2.4;
const ESCALA = Math.min((ANCHO - 2 * PAD) / BASE_W, (ALTO - 2 * PAD) / BASE_H);
const GUIAS = process.env.GUIAS === "1"; // líneas de corte, solo para probar en papel común
const SOLO_FRENTE = process.env.SOLO_FRENTE === "1";
const ELABORADOR = "Cabañas Tierras Mágicas · Villa Pehuenia – Moquehue, Neuquén";
const LEYENDA = "Producción artesanal · Obsequio para nuestros huéspedes · Guardar cerrado, en lugar fresco y seco";
let CONTIENE = {};

function dorso(s) {
  const txt = CONTIENE[s.codigo] || "";
  return `<div class="celda"><div class="et dorso" style="--fondo:${s.fondo}">
    <div class="banda"><span class="nombre">${s.nombre}</span><span class="neto">Sal gourmet · 25 g</span></div>
    <div class="ing"><b>Ingredientes:</b> ${txt.charAt(0).toUpperCase() + txt.slice(1)}.</div>
    <div class="lote"><b>Lote:</b><span></span></div>
    <div class="leg">${ELABORADOR}<br>${LEYENDA}</div>
  </div></div>`;
}

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

// Disposición de la hoja: qué etiqueta va en cada celda (fila por fila)
const disposicion = () => Array.from({ length: FILAS }, (_, i) => SALES.map((s) => ({ s, cara: !SOLO_FRENTE && i % 2 ? "dorso" : "frente" }))).flat();

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
  .celda { width: ${ANCHO}mm; height: ${ALTO}mm; padding: ${PAD}mm; display: grid; place-items: center; ${GUIAS ? "outline: 0.1mm dashed #bbb;" : ""} }
  /* Margen interno: si el troquel corre un poco, no queda un filo blanco cortado */
  .et { position: relative; width: ${(ANCHO - 2 * PAD) / ESCALA}mm; height: ${(ALTO - 2 * PAD) / ESCALA}mm; zoom: ${ESCALA}; border-radius: 1.6mm; overflow: hidden; color: #f4e9d2;
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
  .celda > img { display: block; width: ${ANCHO - 2 * PAD}mm; height: ${ALTO - 2 * PAD}mm; }
  .ilus { width: 8.6mm; flex: none; height: 100%; object-fit: contain; }
  /* Dorso: fondo claro para leer bien los ingredientes y escribir el lote a mano */
  .et.dorso { background: #fbf6ea; color: #2b1d14; flex-direction: column; gap: 0.6mm; padding: 0; }
  .et.dorso::after { border-color: var(--fondo); }
  .banda { background: var(--fondo); color: #f4e9d2; display: flex; justify-content: space-between; align-items: baseline; gap: 1mm; padding: 1.2mm 2mm 0.9mm; }
  .banda .nombre { font-size: 4.6pt; white-space: nowrap; }
  .neto { font-size: 3pt; font-weight: 700; color: #e6c06a; letter-spacing: 0.05em; text-transform: uppercase; white-space: nowrap; }
  .ing { font-size: 4.1pt; line-height: 1.22; padding: 0 2mm; }
  .lote { display: flex; align-items: flex-end; gap: 1mm; font-size: 4.1pt; padding: 0 2mm; }
  .lote span { flex: 1; border-bottom: 0.2mm solid #8a7a6a; height: 2.6mm; max-width: 24mm; }
  .leg { margin-top: auto; font-size: 2.8pt; line-height: 1.25; color: #6f6258; padding: 0 2mm 1.3mm; }
  </style></head><body><div class="grilla">${celdas.join("")}</div></body></html>`;
}

(async () => {
  const { SALES: DATOS } = await import(require("url").pathToFileURL(path.join(DIR, "..", "www", "js", "datos.js")).href);
  CONTIENE = Object.fromEntries(DATOS.map((d) => [d.codigo, d.contiene]));
  const b = await chromium.launch();
  const salida = process.env.SALIDA || (SOLO_FRENTE ? "etiquetas_A4_48_surtidas" : "etiquetas_A4_48_frente_dorso");
  const html = path.join(DIR, `.${salida}.html`);

  // 1) Cada etiqueta distinta se dibuja una vez como imagen de ~670 ppp.
  //    Los visores de PDF de los teléfonos dibujan mal los degradados y transparencias de CSS
  //    (aparecían etiquetas rosadas y recuadros blancos); con imágenes planas el PDF se ve igual en todos lados.
  const unicas = [...SALES.map((s) => ({ s, cara: "frente" })), ...SALES.map((s) => ({ s, cara: "dorso" }))];
  fs.writeFileSync(html, hoja(unicas.map((u) => (u.cara === "dorso" ? dorso : etiqueta)(u.s))));
  const raster = await b.newPage({ deviceScaleFactor: 7, viewport: { width: 794, height: 1123 } });
  await raster.goto(`file://${html}`);
  await raster.evaluate(() => document.fonts.ready);
  const imgs = {};
  const ets = await raster.locator(".et").all();
  for (let i = 0; i < unicas.length; i++) {
    const png = await ets[i].screenshot({ type: "png" });
    imgs[`${unicas[i].s.codigo}-${unicas[i].cara}`] = `data:image/png;base64,${png.toString("base64")}`;
  }
  await raster.close();

  // 2) La hoja final solo coloca esas imágenes en la grilla
  const celdas = disposicion().map((d) => `<div class="celda"><img src="${imgs[`${d.s.codigo}-${d.cara}`]}" alt=""></div>`);
  fs.writeFileSync(html, hoja(celdas));
  const page = await b.newPage();
  await page.goto(`file://${html}`);
  await page.pdf({ path: path.join(DIR, `${salida}.pdf`), format: "A4", printBackground: true, preferCSSPageSize: true });
  const alta = await b.newPage({ deviceScaleFactor: 2, viewport: { width: 794, height: 1123 } });
  await alta.goto(`file://${html}`);
  await alta.screenshot({ path: path.join(DIR, `${salida}.png`), fullPage: true });
  fs.unlinkSync(html);
  await b.close();
  console.log(`Listo: ${salida}.pdf (${ANCHO.toFixed(2)} × ${ALTO.toFixed(2)} mm, márgenes ${MARGEN_X.toFixed(2)} / ${MARGEN_Y.toFixed(2)} mm)`);
})();
