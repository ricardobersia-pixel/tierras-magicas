import { db } from "./db.js";
import { config } from "./config.js";

// Tarifas y temporadas editables desde el panel. Lo guardado en la base reemplaza a config.json;
// "restablecer" vuelve a los valores de config.json. Se aplican sobre el mismo objeto config que usa reservas.js.

const CLAVE = "tarifas";
const esFecha = (s) => typeof s === "string" && /^\d{4}-\d{2}-\d{2}$/.test(s) && !isNaN(new Date(s + "T12:00:00Z"));
const entero = (v) => Number.isInteger(Number(v)) ? Number(v) : NaN;

function leerDeConfig() {
  const { _nota, ...temporadas } = config.temporadas;
  void _nota;
  return {
    precio_directo_descuento: config.negocio.precio_directo_descuento || 0,
    dormi: { plazas: config.negocio.dormi?.plazas || 0, precio_persona_noche: config.negocio.dormi?.precio_persona_noche || 0 },
    temporadas,
    calendario: config.calendario || [],
    tarifas: Object.fromEntries(config.cabanas.map((c) => [c.id, c.tarifas])),
  };
}

// Valores de config.json, antes de aplicar lo guardado en la base
const ORIGINAL = structuredClone(leerDeConfig());

function aplicar(t) {
  config.negocio.precio_directo_descuento = t.precio_directo_descuento;
  config.negocio.dormi = { ...config.negocio.dormi, ...t.dormi };
  config.temporadas = { _nota: config.temporadas._nota, ...t.temporadas };
  config.calendario = t.calendario;
  for (const c of config.cabanas) if (t.tarifas[c.id]) c.tarifas = t.tarifas[c.id];
}

export function obtenerTarifas() {
  const fila = db.prepare("SELECT actualizado FROM ajustes WHERE clave = ?").get(CLAVE);
  return { ...structuredClone(leerDeConfig()), personalizadas: Boolean(fila), actualizado: fila?.actualizado || null };
}

// Revisa todo y devuelve una copia limpia; ante el primer problema lanza un error que se entiende en el panel
export function validarTarifas(t) {
  const errores = [];
  const descuento = entero(t.precio_directo_descuento);
  if (!(descuento >= 0 && descuento <= 50)) errores.push("El descuento por venta directa debe estar entre 0 y 50%.");
  const plazas = entero(t.dormi?.plazas);
  const precioDormi = entero(t.dormi?.precio_persona_noche);
  if (!(plazas >= 0 && plazas <= 10)) errores.push("Las plazas del dormi deben estar entre 0 y 10.");
  if (!(precioDormi >= 0)) errores.push("El precio del dormi debe ser un número positivo.");

  const temporadas = {};
  for (const [id, x] of Object.entries(t.temporadas || {})) {
    const nombre = String(x.nombre || "").trim();
    const temp = {
      nombre, orden: entero(x.orden), minimo_noches: entero(x.minimo_noches), sena_porcentaje: entero(x.sena_porcentaje),
      politica: String(x.politica || "").trim(),
    };
    if (!/^[a-z0-9_-]+$/.test(id) || !nombre) errores.push(`Temporada "${id}": falta el nombre o el código no es válido.`);
    if (!(temp.minimo_noches >= 1)) errores.push(`${nombre || id}: el mínimo de noches debe ser 1 o más.`);
    if (!(temp.sena_porcentaje >= 1 && temp.sena_porcentaje <= 100)) errores.push(`${nombre || id}: la seña debe estar entre 1 y 100%.`);
    if (isNaN(temp.orden)) errores.push(`${nombre || id}: falta el orden.`);
    if (x.descuento && (x.descuento.porcentaje || x.descuento.desde_noches)) {
      temp.descuento = { desde_noches: entero(x.descuento.desde_noches), porcentaje: entero(x.descuento.porcentaje) };
      if (!(temp.descuento.desde_noches >= 1 && temp.descuento.porcentaje >= 1 && temp.descuento.porcentaje <= 90)) {
        errores.push(`${nombre || id}: el descuento por estadía larga necesita noches (1 o más) y porcentaje (1 a 90).`);
      }
    }
    temporadas[id] = temp;
  }
  if (!Object.keys(temporadas).length) errores.push("Tiene que haber al menos una temporada.");
  const sinCalendario = config.negocio.temporada_sin_calendario || "media";
  if (!temporadas[sinCalendario]) errores.push(`No se puede quitar la temporada "${sinCalendario}": se usa para las fechas fuera del calendario.`);

  const tarifas = {};
  for (const c of config.cabanas) {
    tarifas[c.id] = {};
    for (const id of Object.keys(temporadas)) {
      const r = t.tarifas?.[c.id]?.[id] || {};
      const min = entero(r.min);
      const max = entero(r.max);
      if (!(min > 0 && max > 0 && min <= max)) errores.push(`${c.nombre}, ${temporadas[id].nombre}: el precio mínimo y el máximo deben ser mayores a 0 y el mínimo no puede superar al máximo.`);
      tarifas[c.id][id] = { min, max };
    }
  }

  const calendario = (t.calendario || []).map((x) => {
    const tramo = { desde: x.desde, hasta: x.hasta, temporada: x.temporada, motivo: String(x.motivo || "").trim() };
    if (x.minimo_noches) tramo.minimo_noches = entero(x.minimo_noches);
    return tramo;
  }).sort((a, b) => (a.desde < b.desde ? -1 : 1));
  calendario.forEach((x, i) => {
    if (!esFecha(x.desde) || !esFecha(x.hasta) || x.hasta < x.desde) errores.push(`Tramo ${x.desde || "?"} a ${x.hasta || "?"}: fechas inválidas.`);
    if (!temporadas[x.temporada]) errores.push(`Tramo ${x.desde} a ${x.hasta}: la temporada "${x.temporada}" no existe.`);
    if (x.minimo_noches !== undefined && !(x.minimo_noches >= 1)) errores.push(`Tramo ${x.desde} a ${x.hasta}: el mínimo de noches debe ser 1 o más.`);
    if (i && x.desde <= calendario[i - 1].hasta) errores.push(`El tramo ${x.desde} a ${x.hasta} se superpone con ${calendario[i - 1].desde} a ${calendario[i - 1].hasta}.`);
  });

  if (errores.length) throw new Error(errores.slice(0, 5).join(" ") + (errores.length > 5 ? ` (y ${errores.length - 5} más)` : ""));
  return { precio_directo_descuento: descuento, dormi: { plazas, precio_persona_noche: precioDormi }, temporadas, calendario, tarifas };
}

export function guardarTarifas(t) {
  const limpio = validarTarifas(t);
  db.prepare(`INSERT INTO ajustes (clave, valor) VALUES (?, ?)
    ON CONFLICT (clave) DO UPDATE SET valor = excluded.valor, actualizado = datetime('now')`).run(CLAVE, JSON.stringify(limpio));
  aplicar(limpio);
  return obtenerTarifas();
}

// Ejecuta fn con tarifas propuestas (sin guardar) y vuelve a las vigentes: para la vista previa del panel
export function conTarifas(t, fn) {
  const vigentes = structuredClone(leerDeConfig());
  aplicar(validarTarifas(t));
  try {
    return fn();
  } finally {
    aplicar(vigentes);
  }
}

export function restablecerTarifas() {
  db.prepare("DELETE FROM ajustes WHERE clave = ?").run(CLAVE);
  aplicar(structuredClone(ORIGINAL));
  return obtenerTarifas();
}

// ---------- Otros ajustes del panel: recursos de turnos, respuestas para clientes y calendarios de Airbnb/Booking ----------

const ORIGINALES = {
  recursos: structuredClone(config.recursos || []),
  preguntas: structuredClone(config.negocio.preguntas_frecuentes || []),
  canales: Object.fromEntries(config.cabanas.map((c) => [c.id, { airbnb: "", booking: "", ...c.ical_importar }])),
};

const APLICAR = {
  recursos: (v) => (config.recursos = v),
  preguntas: (v) => (config.negocio.preguntas_frecuentes = v),
  canales: (v) => { for (const c of config.cabanas) if (v[c.id]) c.ical_importar = v[c.id]; },
};

const hora = (s) => typeof s === "string" && /^([01]\d|2[0-3]):[0-5]\d$/.test(s);
const enteroPos = (v, min = 1) => Number.isInteger(Number(v)) && Number(v) >= min;

const VALIDAR = {
  recursos(lista) {
    if (!Array.isArray(lista) || !lista.length) throw new Error("Tiene que haber al menos un recurso.");
    const ids = new Set();
    return lista.map((r) => {
      const nombre = String(r.nombre || "").trim();
      const id = String(r.id || "").trim() || nombre.toLowerCase().normalize("NFD").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
      if (!nombre || !id) throw new Error("Cada recurso necesita un nombre.");
      if (ids.has(id)) throw new Error(`Hay dos recursos con el mismo código (${id}).`);
      ids.add(id);
      if (!enteroPos(r.cantidad)) throw new Error(`${nombre}: la cantidad debe ser 1 o más.`);
      if (!enteroPos(r.duracion_min, 15)) throw new Error(`${nombre}: el turno debe durar al menos 15 minutos.`);
      if (!hora(r.desde) || !hora(r.hasta) || r.hasta <= r.desde) throw new Error(`${nombre}: el horario debe ser HH:MM y "hasta" posterior a "desde".`);
      return { id, nombre, cantidad: Number(r.cantidad), duracion_min: Number(r.duracion_min), desde: r.desde, hasta: r.hasta };
    });
  },
  preguntas(lista) {
    if (!Array.isArray(lista)) throw new Error("Lista inválida.");
    return lista.map((x) => ({ p: String(x.p || "").trim(), r: String(x.r || "").trim(), ...(x.tema ? { tema: String(x.tema).trim() } : {}) }))
      .filter((x) => x.p || x.r)
      .map((x) => {
        if (!x.p || !x.r) throw new Error("Cada pregunta necesita la pregunta y la respuesta.");
        return x;
      });
  },
  canales(v) {
    const limpio = {};
    for (const c of config.cabanas) {
      const x = v?.[c.id] || {};
      limpio[c.id] = {};
      for (const origen of ["airbnb", "booking"]) {
        const url = String(x[origen] || "").trim();
        if (url && !/^https:\/\/\S+$/.test(url)) throw new Error(`${c.nombre}, ${origen === "airbnb" ? "Airbnb" : "Booking"}: el enlace debe empezar con https://`);
        limpio[c.id][origen] = url;
      }
    }
    return limpio;
  },
};

export function obtenerAjuste(clave) {
  const fila = db.prepare("SELECT actualizado FROM ajustes WHERE clave = ?").get(clave);
  const actual = { recursos: config.recursos || [], preguntas: config.negocio.preguntas_frecuentes || [],
    canales: Object.fromEntries(config.cabanas.map((c) => [c.id, { airbnb: "", booking: "", ...c.ical_importar }])) }[clave];
  return { valor: structuredClone(actual), personalizado: Boolean(fila), actualizado: fila?.actualizado || null };
}

export function guardarAjuste(clave, valor) {
  if (!VALIDAR[clave]) throw new Error("Ajuste desconocido.");
  const limpio = VALIDAR[clave](valor);
  db.prepare(`INSERT INTO ajustes (clave, valor) VALUES (?, ?)
    ON CONFLICT (clave) DO UPDATE SET valor = excluded.valor, actualizado = datetime('now')`).run(clave, JSON.stringify(limpio));
  APLICAR[clave](limpio);
  return obtenerAjuste(clave);
}

export function restablecerAjuste(clave) {
  if (!VALIDAR[clave]) throw new Error("Ajuste desconocido.");
  db.prepare("DELETE FROM ajustes WHERE clave = ?").run(clave);
  APLICAR[clave](structuredClone(ORIGINALES[clave]));
  return obtenerAjuste(clave);
}

// Al arrancar: aplica lo guardado desde el panel
export function cargarAjustes() {
  const fila = db.prepare("SELECT valor FROM ajustes WHERE clave = ?").get(CLAVE);
  if (fila) aplicar(JSON.parse(fila.valor));
  for (const clave of Object.keys(APLICAR)) {
    const otra = db.prepare("SELECT valor FROM ajustes WHERE clave = ?").get(clave);
    if (otra) APLICAR[clave](JSON.parse(otra.valor));
  }
}
