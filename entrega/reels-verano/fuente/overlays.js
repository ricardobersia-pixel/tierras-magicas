// Renderiza los textos de cada toma como PNG transparente 1080x1920.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outDir = process.argv[3];

const css = `
html,body{margin:0;width:1080px;height:1920px;background:transparent;}
body{font-family:'Inter','Noto Color Emoji',sans-serif;color:#fff;position:relative;}
.main{position:absolute;left:60px;right:60px;top:820px;text-align:center;font-weight:600;
  font-size:58px;line-height:1.22;letter-spacing:-0.5px;
  text-shadow:0 2px 6px rgba(0,0,0,.75),0 0 22px rgba(0,0,0,.45);}
.label{position:absolute;left:0;right:0;top:1040px;text-align:center;}
.label span{display:inline-block;font-weight:700;font-size:46px;padding:10px 28px;border-radius:40px;
  background:rgba(255,255,255,.92);color:#1d2b22;text-shadow:none;}
.handle{position:absolute;left:0;right:0;bottom:170px;text-align:center;font-weight:500;font-size:36px;
  opacity:.95;text-shadow:0 2px 6px rgba(0,0,0,.8);}
`;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const reel of spec) {
    for (let i = 0; i < reel.shots.length; i++) {
      const s = reel.shots[i];
      const esc = t => t.replace(/&/g, '&amp;').replace(/</g, '&lt;');
      const html = `<html><head><style>${css}</style></head><body>
        <div class="main">${reel.text.map(esc).join('<br>')}</div>
        ${s.label ? `<div class="label"><span>${esc(s.label)}</span></div>` : ''}
        ${s.handle ? `<div class="handle">@tierrasmagicasneuquen · Moquehue, Neuquén</div>` : ''}
      </body></html>`;
      await page.setContent(html);
      await page.evaluate(() => document.fonts.ready);
      await page.screenshot({ path: path.join(outDir, `${reel.id}_${i}.png`), omitBackground: true });
    }
  }
  await browser.close();
})();
