import { test } from "node:test";
import assert from "node:assert/strict";
import { pronostico, pronosticoDia } from "../src/solunar.js";

// Valores de referencia verificados contra la biblioteca SunCalc (±1 min)
const lugar = { lat: -38.92, lon: -71.28, zona: "America/Argentina/Buenos_Aires" };
const minutos = (hhmm) => { const [h, m] = hhmm.split(":").map(Number); return h * 60 + m; };

test("salida y puesta del sol del 26/10/2026 en Moquehue", () => {
  const d = pronosticoDia("2026-10-26", lugar);
  assert.ok(Math.abs(minutos(d.sol.salida) - minutos("06:44")) <= 2, d.sol.salida);
  assert.ok(Math.abs(minutos(d.sol.puesta) - minutos("20:15")) <= 2, d.sol.puesta);
});

test("fase lunar: llena el 26/10/2026 y nueva el 8/11/2026", () => {
  const llena = pronosticoDia("2026-10-26", lugar);
  const nueva = pronosticoDia("2026-11-08", lugar);
  assert.equal(llena.luna.nombre, "Luna llena");
  assert.ok(llena.luna.iluminacion >= 99);
  assert.equal(nueva.luna.nombre, "Luna nueva");
  assert.ok(nueva.luna.iluminacion <= 1);
});

test("los días cerca de luna llena o nueva puntúan más que los cuartos", () => {
  const llena = pronosticoDia("2026-10-26", lugar);
  const cuarto = pronosticoDia("2026-11-01", lugar);
  assert.ok(llena.puntaje > cuarto.puntaje);
  assert.equal(llena.calificacion, "Excelente");
});

test("cada día tiene períodos mayores de 2 h y menores de 1 h ordenados", () => {
  for (const d of pronostico("2026-10-24", 10, lugar)) {
    const mayores = d.periodos.filter((p) => p.tipo === "mayor");
    assert.ok(mayores.length >= 1 && mayores.length <= 2, `${d.fecha}: ${mayores.length} mayores`);
    for (const p of d.periodos) {
      const dur = (minutos(p.fin) - minutos(p.inicio) + 1440) % 1440;
      assert.equal(dur, p.tipo === "mayor" ? 120 : 60, `${d.fecha} ${p.motivo}`);
    }
    const desdes = d.periodos.map((p) => p.desde);
    assert.deepEqual(desdes, [...desdes].sort((a, b) => a - b));
  }
});

test("rango de días y validación de la fecha", () => {
  assert.equal(pronostico("2026-11-01", 500, lugar).length, 62);
  assert.equal(pronostico("2026-11-01", 3, lugar)[2].fecha, "2026-11-03");
  assert.throws(() => pronostico("01/11/2026", 3, lugar), /Fecha inválida/);
  assert.throws(() => pronostico("2026-11-01", 3, { ...lugar, lat: NaN }), /coordenadas/);
});

test("crepúsculos civil, náutico y astronómico (referencia SunCalc ±2 min)", () => {
  const c = pronosticoDia("2026-11-10", lugar).sol.crepusculos;
  const cerca = (a, b) => assert.ok(Math.abs(minutos(a) - minutos(b)) <= 2, `${a} vs ${b}`);
  cerca(c.civil.inicio, "05:58");
  cerca(c.civil.fin, "21:02");
  cerca(c.nautico.inicio, "05:22");
  cerca(c.astronomico.fin, "22:17");
  // Ushuaia en el solsticio de verano: no llega a haber noche náutica
  const ushuaia = pronosticoDia("2026-12-21", { lat: -54.8, lon: -68.3, zona: lugar.zona }).sol.crepusculos;
  assert.ok(ushuaia.civil.inicio);
  assert.equal(ushuaia.nautico.inicio, undefined);
});
