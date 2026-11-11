// Genera las hojas A4 de etiquetas de las Sales Gourmet Tierras Mágicas (PDF listo para imprimir y vista previa PNG).
// Uso (desde la raíz del repositorio, requiere Playwright con Chromium):
//   node sales-gourmet/etiquetas/generar.cjs
// Textos corregidos respecto de etiquetas_tierras_magicas_A4.pdf:
// - "Villa Pehuenia – Moquehue" y "Patagonia Argentina" con tipografía real (antes, texto deformado por la IA).
// - Sin el ícono de trigo tachado ("sin TACC"), que no corresponde sin certificación.
// - Medidas reales en el pie: 24 etiquetas (4 × 6) de 4,8 × 4,4 cm.
// - Leyenda de obsequio: son de producción artesanal y no se venden.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const DIR = __dirname;
const url = (f) => `file://${path.join(DIR, f)}`;

const SALES = [
  {
    codigo: "TM-01", nombre: "Caza Patagónica", subtitulo: "Sal marina con hongos<br>y especias del bosque",
    ideal: "Ideal para carnes rojas, caza mayor y papas al horno.", fondo: "#0b2a10", iconos: ["tm-01-icono-2", "tm-01-icono-3", "tm-01-icono-4"],
  },
  {
    codigo: "TM-02", nombre: "Bosque Andino", subtitulo: "Sal con hongos, hierbas<br>aromáticas y especias",
    ideal: "Ideal para huevos, pastas, vegetales y comidas frescas.", fondo: "#3a3006", iconos: ["tm-02-icono-2", "tm-02-icono-3", "tm-02-icono-4"],
  },
  {
    codigo: "TM-03", nombre: "Lago &amp; Trucha", subtitulo: "Sal con limón y mandarina,<br>eneldo y especias suaves",
    ideal: "Ideal para pescados, mariscos, aves y vegetales a la parrilla.", fondo: "#061a2c", iconos: ["tm-03-icono-1", "tm-03-icono-2", "tm-03-icono-3"],
  },
  {
    codigo: "TM-04", nombre: "Reserva del Fogón", subtitulo: "Sal ahumada con<br>vino tinto y especias",
    ideal: "Ideal para asados, carnes a la parrilla, cerdo y vegetales al rescoldo.", fondo: "#420a05", iconos: ["tm-04-icono-1", "tm-04-icono-2", "tm-04-icono-3"],
  },
];

// Medidas en mm
const ANCHO = 48, ALTO = 44, GAP = 2, COLS = 4, FILAS = 6;
const MARGEN_X = (210 - (COLS * ANCHO + (COLS - 1) * GAP)) / 2;
const MARGEN_Y = 6;

function etiqueta(s) {
  return `<div class="et" style="--fondo:${s.fondo}">
    <div class="sup">
      <div class="marca">
        <img class="logo" src="${url(`arte/${s.codigo.toLowerCase()}-logo.png`)}" alt="">
        <div class="tm">Tierras Mágicas</div>
        <div class="cab">— Cabañas de Montaña —</div>
        <div class="lugar">Villa Pehuenia – Moquehue</div>
        <div class="lugar">Patagonia Argentina</div>
      </div>
      <div class="sep"></div>
      <img class="ilus" src="${url(`arte/${s.codigo.toLowerCase()}-ilustracion.png`)}" alt="">
    </div>
    <div class="nombre">${s.nombre}</div>
    <div class="linea"></div>
    <div class="sub">${s.subtitulo}</div>
    <div class="inf">
      <div class="iconos">${s.iconos.map((i) => `<img src="${url(`arte/${i}.png`)}" alt="">`).join("")}</div>
      <div class="sep"></div>
      <div class="ideal">${s.ideal}</div>
    </div>
    <div class="pie">Producción artesanal · Obsequio de la casa</div>
  </div>`;
}

function hoja(celdas, pie) {
  return `<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
  @font-face { font-family: Cinzel; src: url(${url("fuentes/cinzel-latin-600-normal.woff2")}); font-weight: 600; }
  @font-face { font-family: "Great Vibes"; src: url(${url("fuentes/great-vibes-latin-400-normal.woff2")}); }
  @font-face { font-family: Lato; src: url(${url("fuentes/lato-latin-400-normal.woff2")}); font-weight: 400; }
  @font-face { font-family: Lato; src: url(${url("fuentes/lato-latin-700-normal.woff2")}); font-weight: 700; }
  @page { size: A4; margin: 0; }
  * { box-sizing: border-box; }
  html, body { margin: 0; width: 210mm; height: 297mm; background: #fff; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .grilla { position: absolute; left: ${MARGEN_X}mm; top: ${MARGEN_Y}mm; display: grid;
    grid-template-columns: repeat(${COLS}, ${ANCHO}mm); grid-auto-rows: ${ALTO}mm; gap: ${GAP}mm; }
  .et { position: relative; width: ${ANCHO}mm; height: ${ALTO}mm; border-radius: 2mm; overflow: hidden; color: #f4e9d2;
    background: radial-gradient(ellipse at 50% 40%, color-mix(in srgb, var(--fondo) 80%, #fff 6%), var(--fondo) 75%);
    padding: 2.2mm 2.4mm 1.4mm; display: flex; flex-direction: column; align-items: center;
    font-family: Lato, sans-serif; outline: 0.1mm dashed #bbb; outline-offset: 0.9mm; }
  .et::after { content: ""; position: absolute; inset: 1mm; border: 0.25mm solid #c9a24a; border-radius: 1.4mm; pointer-events: none; }
  .sup { display: flex; width: 100%; height: 17.6mm; align-items: stretch; gap: 1.2mm; }
  .marca { flex: 1.45; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; }
  .logo { width: 23mm; height: 9.4mm; object-fit: contain; }
  .tm { font-family: "Great Vibes", cursive; color: #e6c06a; font-size: 9.6pt; line-height: 1; margin-top: 0.2mm; }
  .cab { font-family: Cinzel, serif; color: #e6c06a; font-size: 3.5pt; letter-spacing: 0.06em; margin-top: 0.35mm; white-space: nowrap; }
  .lugar { font-weight: 700; color: #e6c06a; font-size: 3.4pt; letter-spacing: 0.09em; text-transform: uppercase; line-height: 1.3; white-space: nowrap; }
  .sep { width: 0.2mm; background: #c9a24a; opacity: 0.8; }
  .ilus { flex: 1; min-width: 0; height: 100%; object-fit: contain; }
  .nombre { font-family: Cinzel, serif; font-size: 8.4pt; letter-spacing: 0.02em; margin-top: 1.1mm; white-space: nowrap; text-transform: uppercase; }
  .linea { width: 86%; border-top: 0.3mm dotted #e6c06a; margin: 0.8mm 0 0.7mm; }
  .sub { font-weight: 700; color: #e6c06a; font-size: 4.7pt; letter-spacing: 0.06em; text-transform: uppercase; text-align: center; line-height: 1.25; }
  .inf { display: flex; width: 100%; align-items: center; gap: 1.2mm; margin-top: auto; height: 7.2mm; }
  .iconos { display: flex; gap: 0.9mm; align-items: center; }
  .iconos img { height: 5.4mm; }
  .inf .sep { align-self: stretch; }
  .ideal { flex: 1; font-size: 4pt; line-height: 1.2; color: #f4e9d2; }
  .pie { font-size: 3.1pt; letter-spacing: 0.08em; text-transform: uppercase; color: #c9a24a; margin-top: 0.5mm; }
  .leyenda { position: absolute; left: ${MARGEN_X}mm; right: ${MARGEN_X}mm; bottom: 5mm; display: flex; justify-content: space-between;
    font: 7pt/1.3 Lato, sans-serif; color: #555; text-align: center; }
  .leyenda div { flex: 1; border-left: 0.2mm solid #ccc; }
  .leyenda div:first-child { border-left: 0; }
  </style></head><body><div class="grilla">${celdas.join("")}</div>
  <div class="leyenda">${pie.map((p) => `<div>${p}</div>`).join("")}</div></body></html>`;
}

const PIE_COMUN = ["Hoja A4<br>(21 × 29,7 cm)", "Etiqueta<br>4,8 × 4,4 cm", "Imprimir al 100%<br>(sin ajustar a página)", "Recortar por la<br>línea punteada exterior"];

(async () => {
  const b = await chromium.launch();
  const page = await b.newPage();
  const salidas = [
    // Surtida: una variedad por columna, 6 de cada una
    { archivo: "etiquetas_A4_surtidas", celdas: Array.from({ length: FILAS }, () => SALES.map(etiqueta)).flat(), pie: ["24 etiquetas<br>6 de cada sal", ...PIE_COMUN] },
    // Una hoja por variedad, para producir un lote completo
    ...SALES.map((s) => ({ archivo: `etiquetas_A4_${s.codigo}`, celdas: Array(COLS * FILAS).fill(etiqueta(s)), pie: [`24 etiquetas<br>${s.nombre}`, ...PIE_COMUN] })),
  ];
  for (const o of salidas) {
    const html = path.join(DIR, `.${o.archivo}.html`);
    fs.writeFileSync(html, hoja(o.celdas, o.pie));
    await page.goto(`file://${html}`);
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({ path: path.join(DIR, `${o.archivo}.pdf`), format: "A4", printBackground: true, preferCSSPageSize: true });
    if (o.archivo === "etiquetas_A4_surtidas") {
      await page.setViewportSize({ width: 794, height: 1123 });
      await page.screenshot({ path: path.join(DIR, "vista-previa.png"), fullPage: true });
      // Imagen de cada etiqueta para la app de huéspedes (www/img/etiqueta-tm-0N.jpg)
      const alta = await b.newPage({ deviceScaleFactor: 3 });
      await alta.goto(`file://${html}`);
      await alta.evaluate(() => document.fonts.ready);
      await alta.addStyleTag({ content: ".et { outline: 0 !important; }" });
      const ets = await alta.locator(".et").all();
      for (let i = 0; i < SALES.length; i++) {
        await ets[i].screenshot({ path: path.join(DIR, "..", "www", "img", `etiqueta-${SALES[i].codigo.toLowerCase()}.jpg`), type: "jpeg", quality: 85 });
      }
      await alta.close();
    }
    fs.unlinkSync(html);
  }
  await b.close();
  console.log("Listo:", salidas.map((o) => `${o.archivo}.pdf`).join(", "));
})();
