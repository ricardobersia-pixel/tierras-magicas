// Renderiza las vistas de escena.html con el Chromium de Playwright (WebGL por SwiftShader).
// Uso: node docs/acceso/render/render.cjs
const { chromium } = require('playwright');
const path = require('path');
const dir = __dirname;
const VISTAS = [
  ['ruta', 3200, 1000, 'R1_frente_completo_desde_la_ruta.jpg'],
  ['interior', 3200, 1000, 'R2_frente_completo_desde_el_interior.jpg'],
  ['portal', 2400, 1500, 'R3_portal_peatonal.jpg'],
  ['vehicular', 2400, 1500, 'R4_acceso_vehicular.jpg'],
];
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  for (const [v, w, h, out] of VISTAS) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    await p.goto('file://' + path.join(dir, 'escena.html'));
    await p.waitForFunction(() => window.listo === true, null, { timeout: 120000 });
    await p.evaluate((n) => window.vista(n), v);
    await p.waitForTimeout(300);
    await p.screenshot({ path: path.join(dir, out), type: 'jpeg', quality: 88 });
    console.log('ok', out, errs.length ? errs : '');
    await p.close();
  }
  await b.close();
})();
