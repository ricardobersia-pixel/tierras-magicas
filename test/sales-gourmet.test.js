import { test } from "node:test";
import assert from "node:assert/strict";
import { SALES } from "../sales-gourmet/www/js/datos.js";
import {
  buscarSal, controlFormula, escalar, planCompra, envasado, costos, rendimiento, codigoLote, siguienteNumero,
  sumarMeses, stock, faltantes, consumosDeLote, listaIngredientes, pctSal, csv,
} from "../sales-gourmet/www/js/calculos.js";

const PLAN_20KG = { "TM-01": 5000, "TM-02": 5000, "TM-03": 5000, "TM-04": 5000 };

test("las 4 fórmulas cierran en 100% (hoja 02_Control)", () => {
  assert.equal(SALES.length, 4);
  for (const s of SALES) assert.deepEqual(controlFormula(s), { suma: 100, cierra: true }, s.codigo);
});

test("el escalado reproduce la hoja 03_Escalado", () => {
  const tm01 = escalar(buscarSal("TM-01"), 250);
  assert.equal(tm01.find((f) => f.ingrediente === "Cebolla deshidratada").gramos, 12.5);
  const tm03 = escalar(buscarSal("TM-03"), 5000);
  assert.equal(tm03.find((f) => f.ingrediente === "Sal con Limón").gramos, 3250);
  assert.equal(tm03.reduce((t, f) => t + f.gramos, 0), 5000);
});

test("el plan de 20 kg reproduce la hoja Resumen Compra (+5%)", () => {
  const { filas, totales } = planCompra(PLAN_20KG, 0.05);
  assert.equal(filas.length, 20); // 20 ingredientes distintos
  const fila = (n) => filas.find((f) => f.ingrediente === n);
  assert.equal(fila("Hongos secos").total, 1000); // 500 + 100 + 400
  assert.equal(fila("Hongos secos").compra, 1050);
  assert.deepEqual(fila("Hongos secos").porSal, { "TM-01": 500, "TM-03": 100, "TM-04": 400 });
  assert.equal(fila("Ajo en escamas").compra, 525); // 500 × 1,05
  assert.equal(fila("Sal Marina").compra, 3885);
  assert.equal(totales.total, 20000);
  assert.equal(totales.compra, 21000);
  for (const c of Object.keys(PLAN_20KG)) assert.equal(totales.porSal[c], 5000);
});

test("planCompra ignora sales sin cantidad", () => {
  const { totales } = planCompra({ "TM-01": 1000, "TM-02": 0 });
  assert.deepEqual(Object.keys(totales.porSal), ["TM-01"]);
});

test("envasado: frascos enteros, sobrante y hojas de 24 etiquetas", () => {
  assert.deepEqual(envasado(5000, 100), { frascos: 50, sobrante: 0, hojas: 3 });
  assert.deepEqual(envasado(5000, 120), { frascos: 41, sobrante: 80, hojas: 2 });
  assert.equal(envasado(5000, 0).frascos, 0);
});

test("costos: por kg, por frasco y precio con ganancia sobre el precio", () => {
  const sal = buscarSal("TM-01");
  const precios = Object.fromEntries(sal.formula.map((f) => [f.ingrediente, 1000])); // $1.000/kg todo
  const c = costos(sal, precios, { margen: 0.05, neto: 100, envase: 500, ganancia: 0.5 });
  assert.equal(c.completo, true);
  assert.equal(c.porKg, 1050); // 1 kg × 1,05 × $1.000
  assert.equal(c.insumoFrasco, 105);
  assert.equal(c.porFrasco, 605);
  assert.equal(c.precioSugerido, 1210); // 605 / (1 − 0,5)
});

test("costos avisa qué precios faltan", () => {
  const c = costos(buscarSal("TM-02"), { "Sal con Hongos": 2000 });
  assert.equal(c.completo, false);
  assert.equal(c.faltan.length, 6);
  assert.ok(!c.faltan.includes("Sal con Hongos"));
});

test("rendimiento como la hoja Control Producción", () => {
  assert.equal(rendimiento(5000, 4900), 98);
  assert.equal(rendimiento(0, 10), 0);
});

test("código de lote, numeración del día y vencimiento", () => {
  assert.equal(codigoLote("TM-04", "2026-11-11", 1), "TM-04-261111-01");
  const lotes = [{ lote: "TM-04-261111-01" }, { lote: "TM-04-261111-02" }, { lote: "TM-01-261111-05" }];
  assert.equal(siguienteNumero(lotes, "TM-04", "2026-11-11"), 3);
  assert.equal(siguienteNumero(lotes, "TM-02", "2026-11-11"), 1);
  assert.equal(sumarMeses("2026-11-11", 12), "2027-11-11");
  assert.equal(sumarMeses("2027-01-31", 1), "2027-02-28");
});

test("stock y faltantes descuentan lo producido", () => {
  const movs = [
    { tipo: "compra", ingrediente: "Sal Marina", gramos: 4000 },
    ...consumosDeLote("TM-01", 1000, "TM-01-261111-01"), // usa 740 g de sal marina
  ];
  const s = stock(movs);
  assert.equal(s["Sal Marina"], 3260);
  assert.equal(s["Hongos secos"], -100); // se usó sin compra registrada
  const f = faltantes({ "TM-01": 5000 }, s);
  assert.equal(f.find((x) => x.ingrediente === "Sal Marina").comprar, 625); // 3885 − 3260
});

test("lista de ingredientes en orden decreciente y contenido de sal", () => {
  assert.match(listaIngredientes(buscarSal("TM-04")), /^Sal ahumada, Sal con vino tinto, Hongos secos/);
  assert.equal(pctSal(buscarSal("TM-01")), 74);
  assert.equal(pctSal(buscarSal("TM-03")), 80);
});

test("csv con punto y coma y comillas", () => {
  assert.equal(csv([["a", "b;c"], [1, 'x"y']]), 'a;"b;c"\r\n1;"x""y"');
});
