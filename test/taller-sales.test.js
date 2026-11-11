import { test } from "node:test";
import assert from "node:assert/strict";
import {
  validarFormulas, buscarSal, controlFormula, escalar, ingredientes, planCompra, envasado, costos, rendimiento, codigoLote,
  siguienteNumero, stock, faltantes, consumosDeLote, listaIngredientes, csv,
} from "../taller-sales/www/js/calculos.js";

// Fórmulas FICTICIAS: las reales no se publican (el repositorio es público).
const ARCHIVO = {
  app: "taller-tm",
  tipo: "formulas",
  sales: [
    { codigo: "TM-91", nombre: "Prueba A", formula: [{ ingrediente: "Sal X", pct: 70 }, { ingrediente: "Hierba Y", pct: 20 }, { ingrediente: "Especia Z", pct: 10 }] },
    { codigo: "TM-92", nombre: "Prueba B", formula: [{ ingrediente: "Sal X", pct: 60 }, { ingrediente: "Hierba Y", pct: 25 }, { ingrediente: "Ajo W", pct: 15 }] },
  ],
};
const SALES = ARCHIVO.sales;
const PLAN = { "TM-91": 5000, "TM-92": 5000 };

test("validarFormulas acepta el archivo y rechaza fórmulas que no cierran", () => {
  assert.equal(validarFormulas(ARCHIVO).ok, true);
  assert.equal(validarFormulas({ app: "otra" }).ok, false);
  const malo = structuredClone(ARCHIVO);
  malo.sales[0].formula[0].pct = 69;
  const v = validarFormulas(malo);
  assert.equal(v.ok, false);
  assert.match(v.errores[0], /suma 99%/);
});

test("controlFormula y escalado", () => {
  assert.deepEqual(controlFormula(SALES[0]), { suma: 100, cierra: true });
  const e = escalar(SALES[0], 250);
  assert.deepEqual(e.map((f) => f.gramos), [175, 50, 25]);
  assert.deepEqual(ingredientes(SALES), ["Ajo W", "Especia Z", "Hierba Y", "Sal X"]);
});

test("plan de compra consolidado con margen del 5%", () => {
  const { filas, totales } = planCompra(PLAN, 0.05, SALES);
  const sal = filas.find((f) => f.ingrediente === "Sal X");
  assert.equal(sal.total, 6500); // 3500 + 3000
  assert.equal(sal.compra, 6825);
  assert.deepEqual(sal.porSal, { "TM-91": 3500, "TM-92": 3000 });
  assert.equal(totales.total, 10000);
  assert.equal(totales.compra, 10500);
  assert.deepEqual(Object.keys(planCompra({ "TM-91": 1000, "TM-99": 1000 }, 0, SALES).totales.porSal), ["TM-91"]);
});

test("envasado en sobres doypack de 25 g: sobres, sobrante y hojas de 24 etiquetas", () => {
  assert.deepEqual(envasado(5000, 25), { unidades: 200, sobrante: 0, hojas: 9 });
  assert.deepEqual(envasado(4930, 25), { unidades: 197, sobrante: 5, hojas: 9 });
  assert.equal(envasado(5000, 0).unidades, 0);
});

test("costo de cada obsequio y precios faltantes", () => {
  const precios = { "Sal X": 1000, "Hierba Y": 1000, "Especia Z": 1000 };
  const c = costos(SALES[0], precios, { margen: 0.05, neto: 25, envase: 300 });
  assert.equal(c.completo, true);
  assert.equal(c.porKg, 1050);
  assert.equal(c.insumoSobre, 26); // 26,25
  assert.equal(c.porSobre, 326);
  assert.deepEqual(costos(SALES[1], precios).faltan, ["Ajo W"]);
});

test("lotes: rendimiento, código y numeración", () => {
  assert.equal(rendimiento(5000, 4900), 98);
  assert.equal(rendimiento(0, 10), 0);
  assert.equal(codigoLote("TM-04", "2026-11-11", 1), "TM-04-261111-01");
  const lotes = [{ lote: "TM-04-261111-01" }, { lote: "TM-04-261111-02" }, { lote: "TM-01-261111-05" }];
  assert.equal(siguienteNumero(lotes, "TM-04", "2026-11-11"), 3);
  assert.equal(siguienteNumero(lotes, "TM-02", "2026-11-11"), 1);
});

test("stock y faltantes descuentan lo producido", () => {
  const s = stock([{ tipo: "compra", ingrediente: "Sal X", gramos: 4000 }, ...consumosDeLote(buscarSal(SALES, "TM-91"), 1000, "L1")]);
  assert.equal(s["Sal X"], 3300);
  assert.equal(s["Hierba Y"], -200);
  const f = faltantes({ "TM-91": 5000 }, s, 0.05, SALES);
  assert.equal(f.find((x) => x.ingrediente === "Sal X").comprar, 375); // 3675 − 3300
});

test("rótulo: ingredientes en orden alfabético y sin cantidades", () => {
  assert.equal(listaIngredientes(SALES[0]), "Especia z, Hierba y, Sal x");
});

test("csv con punto y coma y comillas", () => {
  assert.equal(csv([["a", "b;c"], [1, 'x"y']]), 'a;"b;c"\r\n1;"x""y"');
});
