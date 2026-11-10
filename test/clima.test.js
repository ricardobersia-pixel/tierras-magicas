import { test } from "node:test";
import assert from "node:assert/strict";
import {
  urlPronostico, porDia, cardinal, direccionMedia, estadoCielo, tendenciaPresion, condiciones, resumenDia, consejoViento, obtenerPronostico,
} from "../pesca-patagonia/www/js/clima.js";

// Respuesta con el formato de Open-Meteo (hourly con timezone): 2 días de 24 horas
function respuesta({ viento = 10, rafaga = 18, direccion = 225 } = {}) {
  const time = [];
  for (const d of ["2026-11-10", "2026-11-11"]) for (let h = 0; h < 24; h++) time.push(`${d}T${String(h).padStart(2, "0")}:00`);
  const n = time.length;
  const serie = (f) => Array.from({ length: n }, (_, i) => f(i % 24, i));
  return {
    latitude: -38.92, longitude: -71.28, timezone: "America/Argentina/Buenos_Aires",
    hourly: {
      time,
      temperature_2m: serie((h) => 5 + h / 2),
      apparent_temperature: serie((h) => 3 + h / 2),
      precipitation_probability: serie((h) => (h === 15 ? 40 : 10)),
      precipitation: serie((h) => (h === 15 ? 1.2 : 0)),
      weather_code: serie((h) => (h === 15 ? 61 : 2)),
      cloud_cover: serie(() => 50),
      pressure_msl: serie((h) => 1015 - (h >= 9 ? (h - 9) * 1 : 0)),
      wind_speed_10m: serie((h) => (h === 14 ? viento : 5)),
      wind_gusts_10m: serie((h) => (h === 14 ? rafaga : 9)),
      wind_direction_10m: serie(() => direccion),
    },
  };
}

test("la consulta pide las variables, la zona y redondea la ubicación a ~1 km", () => {
  const u = new URL(urlPronostico({ lat: -38.923456, lon: -71.281234, zona: "America/Argentina/Buenos_Aires" }));
  assert.equal(u.hostname, "api.open-meteo.com");
  assert.equal(u.searchParams.get("latitude"), "-38.92");
  assert.equal(u.searchParams.get("longitude"), "-71.28");
  assert.equal(u.searchParams.get("timezone"), "America/Argentina/Buenos_Aires");
  assert.equal(u.searchParams.get("wind_speed_unit"), "kmh");
  for (const v of ["wind_gusts_10m", "wind_direction_10m", "pressure_msl", "precipitation_probability"]) assert.ok(u.searchParams.get("hourly").includes(v));
});

test("agrupa las horas por día local", () => {
  const dias = porDia(respuesta());
  assert.deepEqual(Object.keys(dias), ["2026-11-10", "2026-11-11"]);
  assert.equal(dias["2026-11-10"].length, 24);
  assert.equal(dias["2026-11-10"][15].hora, "15:00");
  assert.equal(dias["2026-11-10"][15].lluvia, 1.2);
  assert.throws(() => porDia({}), /sin datos/);
});

test("rumbos y dirección promedio del viento", () => {
  assert.equal(cardinal(0), "N");
  assert.equal(cardinal(225), "SO");
  assert.equal(cardinal(359), "N");
  assert.equal(cardinal(-90), "O");
  assert.equal(direccionMedia([350, 10]), 0);
  assert.equal(direccionMedia([]), null);
});

test("estado del cielo según el código WMO", () => {
  assert.equal(estadoCielo(0).texto, "Despejado");
  assert.equal(estadoCielo(63).texto, "Lluvia");
  assert.equal(estadoCielo(95).texto, "Tormenta");
});

test("tendencia de la presión en 3 horas", () => {
  assert.equal(tendenciaPresion(1015, 1012).sentido, "baja");
  assert.equal(tendenciaPresion(1012, 1014).sentido, "sube");
  assert.equal(tendenciaPresion(1012, 1013).sentido, "estable");
  assert.equal(tendenciaPresion(undefined, 1013), null);
});

test("condiciones en el lago por viento y ráfagas", () => {
  assert.equal(condiciones(10, 20).nivel, "aptas");
  assert.equal(condiciones(10, 25).nivel, "precaucion");
  assert.equal(condiciones(16, 20).nivel, "precaucion");
  assert.equal(condiciones(10, 35).nivel, "desaconsejado");
  assert.equal(condiciones(25, 10).nivel, "desaconsejado");
});

test("resumen del día usa las horas de luz para el viento", () => {
  const horas = porDia(respuesta({ viento: 22, rafaga: 38 }))["2026-11-10"];
  const r = resumenDia(horas, { salida: "06:30", puesta: "20:20" });
  assert.equal(r.viento, 22);
  assert.equal(r.rafaga, 38);
  assert.equal(r.condiciones.nivel, "desaconsejado");
  assert.equal(r.tempMin, 5);
  assert.equal(r.tempMax, 17);
  assert.equal(r.probLluvia, 40);
  assert.equal(r.lluvia, 1.2);
  assert.equal(r.cielo.texto, "Lluvia");
  assert.equal(r.tendencia.sentido, "baja"); // 1015 a las 9 h → 1012 a las 12 h
  assert.equal(cardinal(r.direccion), "SO");
  // Un pico de viento de noche no cuenta para las condiciones del día
  const nocturno = porDia(respuesta())["2026-11-10"].map((f) => (f.hora === "02:00" ? { ...f, viento: 60, rafaga: 80 } : f));
  assert.equal(resumenDia(nocturno, { salida: "06:30", puesta: "20:20" }).condiciones.nivel, "aptas");
  assert.equal(resumenDia([], {}), null);
});

test("consejo de caza: acercarse con el viento en la cara", () => {
  assert.match(consejoViento(225), /Viento del SO: acercate desde el NE/);
  assert.equal(consejoViento(null), null);
});

test("obtenerPronostico consulta el servicio y avisa si falla sin copia guardada", async () => {
  const lugar = { lat: -38.92, lon: -71.28, zona: "America/Argentina/Buenos_Aires" };
  const ok = await obtenerPronostico(lugar, { fetchFn: async () => ({ ok: true, json: async () => respuesta() }) });
  assert.equal(ok.desdeCopia, false);
  assert.equal(ok.dias["2026-11-11"].length, 24);
  await assert.rejects(obtenerPronostico(lugar, { fetchFn: async () => ({ ok: false, status: 429 }) }), /429/);
  await assert.rejects(obtenerPronostico(lugar, { fetchFn: async () => { throw new TypeError("Failed to fetch"); } }), /Failed to fetch/);
});
