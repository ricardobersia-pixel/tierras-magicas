import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { SALES, RECETAS } from "../sales-gourmet/www/js/datos.js";

test("el recetario tiene 5 recetas por sal, con ids únicos y datos completos", () => {
  assert.equal(SALES.length, 4);
  for (const s of SALES) assert.equal(RECETAS.filter((r) => r.sal === s.codigo).length, 5, s.codigo);
  assert.equal(new Set(RECETAS.map((r) => r.id)).size, RECETAS.length);
  for (const r of RECETAS) {
    assert.ok(r.titulo && r.bajada && r.porciones > 0 && r.tiempo, r.id);
    assert.ok(r.ingredientes.length >= 2 && r.pasos.length >= 3 || r.pasos.length >= 2, r.id);
    assert.match(r.foto, /^[a-z0-9-]+\.jpg$/, r.id);
  }
});

test("la app del huésped no incluye fórmulas ni proporciones", () => {
  for (const s of SALES) {
    assert.equal(s.formula, undefined);
    assert.doesNotMatch(s.contiene, /\d/);
  }
  const archivos = fs.readdirSync("sales-gourmet/www/js").map((f) => fs.readFileSync(`sales-gourmet/www/js/${f}`, "utf8"));
  for (const t of archivos) assert.doesNotMatch(t, /\bpct\b|g\/kg|granulometr/i);
});

test("la app del taller no trae fórmulas en el código", () => {
  for (const f of fs.readdirSync("taller-sales/www/js")) {
    assert.doesNotMatch(fs.readFileSync(`taller-sales/www/js/${f}`, "utf8"), /pct:\s*\d/, f);
  }
});
