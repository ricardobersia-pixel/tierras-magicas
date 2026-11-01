import { test } from "node:test";
import assert from "node:assert/strict";
import { diagnosticar } from "../panel-app/www/motivo.js";

test("HTTP 404: dirección que no es de ningún servicio de Railway", () => {
  assert.match(diagnosticar({ tipo: "http", codigo: 404 }, true).motivo, /ningún servicio/);
});

test("HTTP 502/503: el servidor no arrancó o se cayó", () => {
  for (const codigo of [502, 503, 504]) assert.match(diagnosticar({ tipo: "http", codigo }, true).motivo, /no está respondiendo/);
});

test("Error de red sin internet: lo dice antes que cualquier otra cosa", () => {
  assert.match(diagnosticar({ tipo: "red", codigo: -2 }, false).motivo, /no tiene internet/);
});

test("Error de red con internet: DNS, conexión y certificado", () => {
  assert.match(diagnosticar({ tipo: "red", codigo: -2 }, true).motivo, /no existe/);
  assert.match(diagnosticar({ tipo: "red", codigo: -8 }, true).motivo, /no contesta/);
  assert.match(diagnosticar({ tipo: "red", codigo: -11 }, true).motivo, /https/);
});

test("Sin detalle (app anterior): mensaje genérico según haya internet", () => {
  assert.match(diagnosticar({ tipo: null, codigo: NaN }, true).motivo, /no respondió/);
  assert.match(diagnosticar({ tipo: null, codigo: NaN }, false).motivo, /no tiene internet/);
});
