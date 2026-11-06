import { db } from "./db.js";
import { config, env } from "./config.js";
import { hoyISO } from "./reservas.js";

// Unidades de alquiler: cabañas, el dormi y los equipos o espacios que se usan por turno
// (kayaks, tablas de stand up, sauna, jacuzzi, bicicletas, bote a motor u otros), cada una con hasta 5 fotos.
// La lista editada en el panel se guarda en ajustes ("unidades") y se aplica sobre el mismo objeto config
// que usan reservas, calendario, turnos y la web: config.cabanas, config.recursos y config.negocio.dormi.

export const MAX_FOTOS = 5;
const MAX_BYTES_FOTO = 3 * 1024 * 1024;
const CLAVE = "unidades";

export const TIPOS = {
  cabana: { nombre: "Cabaña", clase: "alojamiento" },
  dormi: { nombre: "Dormi", clase: "alojamiento" },
  kayak: { nombre: "Kayak", clase: "equipo" },
  sup: { nombre: "Tabla de stand up", clase: "equipo" },
  sauna: { nombre: "Sauna", clase: "equipo" },
  jacuzzi: { nombre: "Jacuzzi / tina caliente", clase: "equipo" },
  bicicleta: { nombre: "Bicicleta", clase: "equipo" },
  bote: { nombre: "Bote a motor", clase: "equipo" },
  otro: { nombre: "Otro", clase: "equipo" },
};
const esEquipo = (tipo) => TIPOS[tipo]?.clase === "equipo";

// Foto de dibujo que muestra la web mientras una cabaña no tiene fotos cargadas
const FOTO_ORIGINAL = Object.fromEntries(config.cabanas.map((c) => [c.id, c.foto]));
const FOTO_GENERICA = config.cabanas[0]?.foto || "/img/hero.svg";

const entero = (v) => (v === "" || v === null || v === undefined ? null : Number.isInteger(Number(v)) ? Number(v) : NaN);
const hora = (s) => typeof s === "string" && /^([01]\d|2[0-3]):[0-5]\d$/.test(s);
const slug = (s) => String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

// ---------- Lista vigente ----------

// La lista tal como está en config (config.json más lo guardado antes de existir esta pestaña)
function desdeConfig() {
  const lista = config.cabanas.map((c) => ({
    id: c.id, tipo: "cabana", nombre: c.nombre, descripcion: c.descripcion || "",
    capacidad: c.capacidad, habitaciones: c.habitaciones ?? null, banos: c.banos ?? null,
  }));
  const d = config.negocio.dormi;
  if (d) lista.push({ id: "dormi", tipo: "dormi", nombre: d.nombre || "Dormi", descripcion: d.descripcion || "" });
  for (const r of config.recursos || []) {
    lista.push({
      id: r.id, tipo: r.tipo || (TIPOS[r.id] && esEquipo(r.id) ? r.id : "otro"), nombre: r.nombre, descripcion: r.descripcion || "",
      cantidad: r.cantidad, turnos: true, duracion_min: r.duracion_min, desde: r.desde, hasta: r.hasta,
      incluido: r.incluido ?? true, precio: r.precio || 0,
    });
  }
  return lista;
}

function listaGuardada() {
  const fila = db.prepare("SELECT valor FROM ajustes WHERE clave = ?").get(CLAVE);
  return fila ? JSON.parse(fila.valor) : null;
}
const listaActual = () => listaGuardada() || desdeConfig();

// ---------- Fotos ----------

const fotosDe = (unidadId, conDatos = false) =>
  db.prepare(`SELECT id, tipo${conDatos ? ", datos" : ""} FROM fotos WHERE unidad = ? ORDER BY orden, id`).all(unidadId);

// En el servidor la foto se sirve en /fotos/:id; en la app de prueba (sin servidor) va dentro de la página
const urlFoto = (f) => (env.fotosEnLinea ? `data:${f.tipo};base64,${f.datos}` : `/fotos/${f.id}`);
const fotosConUrl = (unidadId) => fotosDe(unidadId, env.fotosEnLinea).map((f) => ({ id: f.id, url: urlFoto(f) }));

export function fotoParaServir(id) {
  const f = db.prepare("SELECT tipo, datos FROM fotos WHERE id = ?").get(Number(id));
  return f ? { tipo: f.tipo, bytes: Buffer.from(f.datos, "base64") } : null;
}

// ---------- Aplicar sobre config ----------

function aplicar(lista) {
  const anteriores = Object.fromEntries(config.cabanas.map((c) => [c.id, c]));
  const molde = config.cabanas[0];
  config.cabanas = lista.filter((u) => u.tipo === "cabana").map((u) => {
    const c = anteriores[u.id] || {
      id: u.id, minimo_noches: molde?.minimo_noches || 2,
      tarifas: structuredClone(u.tarifas_inicial || molde?.tarifas || {}), ical_importar: { airbnb: "", booking: "" },
    };
    const fotos = fotosConUrl(u.id).map((f) => f.url);
    return Object.assign(c, {
      nombre: u.nombre, descripcion: u.descripcion, capacidad: u.capacidad, habitaciones: u.habitaciones, banos: u.banos,
      fotos, foto: fotos[0] || FOTO_ORIGINAL[u.id] || FOTO_GENERICA,
    });
  });
  const dormi = lista.find((u) => u.tipo === "dormi");
  if (dormi && config.negocio.dormi) {
    Object.assign(config.negocio.dormi, { nombre: dormi.nombre, descripcion: dormi.descripcion, fotos: fotosConUrl("dormi").map((f) => f.url) });
  }
  const equipos = lista.filter((u) => esEquipo(u.tipo));
  config.recursos = equipos.filter((u) => u.turnos).map(({ id, tipo, nombre, cantidad, duracion_min, desde, hasta, incluido, precio }) =>
    ({ id, tipo, nombre, cantidad, duracion_min, desde, hasta, incluido, precio }));
  // Para la web: lo que se puede usar o alquilar en el complejo, con sus fotos
  config.equipos = equipos.map(({ id, tipo, nombre, descripcion, cantidad, incluido, precio, turnos }) =>
    ({ id, tipo, nombre, descripcion, cantidad, incluido, precio, turnos, fotos: fotosConUrl(id).map((f) => f.url) }));
}

// ---------- Validación ----------

function validar(lista) {
  const ids = new Set();
  const limpia = lista.map((u) => {
    const tipo = u.tipo;
    if (!TIPOS[tipo]) throw new Error("Tipo de unidad desconocido.");
    const nombre = String(u.nombre || "").trim().slice(0, 60);
    if (!nombre) throw new Error("Cada unidad necesita un nombre.");
    if (!/^[a-z0-9-]+$/.test(u.id || "")) throw new Error(`${nombre}: código inválido.`);
    if (ids.has(u.id)) throw new Error(`Hay dos unidades con el mismo código (${u.id}).`);
    ids.add(u.id);
    const descripcion = String(u.descripcion || "").trim();
    if (descripcion.length > 800) throw new Error(`${nombre}: la descripción es muy larga (máximo 800 letras).`);
    const base = { id: u.id, tipo, nombre, descripcion };

    if (tipo === "cabana") {
      const capacidad = entero(u.capacidad);
      const habitaciones = entero(u.habitaciones);
      const banos = entero(u.banos);
      if (!(capacidad >= 1 && capacidad <= 20)) throw new Error(`${nombre}: la capacidad debe estar entre 1 y 20 personas.`);
      if (habitaciones !== null && !(habitaciones >= 0 && habitaciones <= 10)) throw new Error(`${nombre}: habitaciones entre 0 y 10.`);
      if (banos !== null && !(banos >= 0 && banos <= 10)) throw new Error(`${nombre}: baños entre 0 y 10.`);
      return { ...base, capacidad, habitaciones, banos, ...(u.tarifas_inicial ? { tarifas_inicial: u.tarifas_inicial } : {}) };
    }
    if (tipo === "dormi") return base;

    const cantidad = entero(u.cantidad);
    if (!(cantidad >= 1 && cantidad <= 50)) throw new Error(`${nombre}: la cantidad debe estar entre 1 y 50.`);
    const incluido = u.incluido !== false;
    const precio = incluido ? 0 : entero(u.precio);
    if (!incluido && !(precio > 0)) throw new Error(`${nombre}: si no está incluido en la tarifa, poné el precio por turno.`);
    const equipo = { ...base, cantidad, incluido, precio, turnos: Boolean(u.turnos) };
    if (equipo.turnos) {
      const duracion_min = entero(u.duracion_min);
      if (!(duracion_min >= 15 && duracion_min <= 1440)) throw new Error(`${nombre}: el turno debe durar entre 15 minutos y 24 horas.`);
      if (!hora(u.desde) || !hora(u.hasta) || u.hasta <= u.desde) throw new Error(`${nombre}: el horario debe ser HH:MM y "hasta" posterior a "desde".`);
      Object.assign(equipo, { duracion_min, desde: u.desde, hasta: u.hasta });
    }
    return equipo;
  });
  if (!limpia.some((u) => u.tipo === "cabana")) throw new Error("Tiene que haber al menos una cabaña.");
  if (limpia.filter((u) => u.tipo === "dormi").length > 1) throw new Error("Hay un solo dormi.");
  return limpia;
}

function guardar(lista) {
  const limpia = validar(lista);
  db.prepare(`INSERT INTO ajustes (clave, valor) VALUES (?, ?)
    ON CONFLICT (clave) DO UPDATE SET valor = excluded.valor, actualizado = datetime('now')`).run(CLAVE, JSON.stringify(limpia));
  // Los recursos de turnos ahora salen de las unidades
  db.prepare("DELETE FROM ajustes WHERE clave = 'recursos'").run();
  aplicar(limpia);
  return limpia;
}

// ---------- Operaciones del panel ----------

export function obtenerUnidades() {
  const fila = db.prepare("SELECT actualizado FROM ajustes WHERE clave = ?").get(CLAVE);
  return {
    tipos: TIPOS,
    max_fotos: MAX_FOTOS,
    foto_max_lado: env.fotoMaxLado || 1600,
    dormi: config.negocio.dormi ? { plazas: config.negocio.dormi.plazas, precio_persona_noche: config.negocio.dormi.precio_persona_noche } : null,
    actualizado: fila?.actualizado || null,
    unidades: listaActual().map(({ tarifas_inicial, ...u }) => ({ ...u, fotos: fotosConUrl(u.id) })),
  };
}

const buscar = (lista, id) => {
  const u = lista.find((x) => x.id === id);
  if (!u) throw new Error("Esa unidad no existe.");
  return u;
};

// Campos que se pueden editar según el tipo (el tipo y el código no cambian)
const CAMPOS = {
  cabana: ["nombre", "descripcion", "capacidad", "habitaciones", "banos"],
  dormi: ["nombre", "descripcion"],
  equipo: ["nombre", "descripcion", "cantidad", "turnos", "duracion_min", "desde", "hasta", "incluido", "precio"],
};
const camposDe = (tipo) => CAMPOS[esEquipo(tipo) ? "equipo" : tipo];
const elegir = (datos, tipo) => Object.fromEntries(camposDe(tipo).filter((k) => datos[k] !== undefined).map((k) => [k, datos[k]]));

export function crearUnidad(datos) {
  const lista = listaActual();
  const tipo = datos.tipo;
  if (!TIPOS[tipo]) throw new Error("Elegí el tipo de unidad.");
  if (tipo === "dormi" && lista.some((u) => u.tipo === "dormi")) throw new Error("Ya hay un dormi cargado.");
  if (tipo === "dormi" && !config.negocio.dormi) throw new Error("El dormi se habilita poniendo plazas en Tarifas.");
  const raiz = slug(datos.nombre || TIPOS[tipo].nombre) || tipo;
  let id = raiz;
  for (let n = 2; lista.some((u) => u.id === id); n++) id = `${raiz}-${n}`;
  const nueva = {
    id, tipo,
    ...(esEquipo(tipo) ? { cantidad: 1, turnos: true, duracion_min: 60, desde: "10:00", hasta: "20:00", incluido: true, precio: 0 } : {}),
    ...elegir(datos, tipo),
  };
  if (tipo === "cabana") {
    // Las tarifas de una cabaña nueva arrancan como las de otra (después se ajustan en Tarifas)
    const molde = config.cabanas.find((c) => c.id === datos.tarifas_como)
      || [...config.cabanas].sort((a, b) => Math.abs(a.capacidad - nueva.capacidad) - Math.abs(b.capacidad - nueva.capacidad))[0];
    if (molde) nueva.tarifas_inicial = structuredClone(molde.tarifas);
  }
  guardar([...lista, nueva]);
  return obtenerUnidades().unidades.find((u) => u.id === id);
}

export function actualizarUnidad(id, datos) {
  const lista = listaActual();
  const u = buscar(lista, id);
  Object.assign(u, elegir(datos, u.tipo));
  guardar(lista);
  return obtenerUnidades().unidades.find((x) => x.id === id);
}

export function borrarUnidad(id) {
  const lista = listaActual();
  const u = buscar(lista, id);
  if (u.tipo === "dormi") throw new Error("El dormi no se borra: para dejar de ofrecerlo poné 0 plazas en Tarifas.");
  if (u.tipo === "cabana") {
    const { n } = db.prepare("SELECT COUNT(*) AS n FROM reservas WHERE cabana_id = ?").get(id);
    const { m } = db.prepare("SELECT COUNT(*) AS m FROM reservas_ota WHERE cabana_id = ?").get(id);
    if (n || m) throw new Error(`${u.nombre} tiene reservas cargadas (${n + m}) y no se puede borrar: los informes y las finanzas las usan.`);
  } else {
    const { n } = db.prepare("SELECT COUNT(*) AS n FROM turnos WHERE recurso = ? AND fecha >= ?").get(id, hoyISO());
    if (n) throw new Error(`${u.nombre} tiene ${n} turno(s) desde hoy. Borralos primero en Turnos.`);
  }
  guardar(lista.filter((x) => x.id !== id));
  db.prepare("DELETE FROM fotos WHERE unidad = ?").run(id);
  return u;
}

export function agregarFoto(unidadId, dataUrl) {
  const lista = listaActual();
  const u = buscar(lista, unidadId);
  if (fotosDe(unidadId).length >= MAX_FOTOS) throw new Error(`${u.nombre} ya tiene ${MAX_FOTOS} fotos. Borrá una para subir otra.`);
  const m = /^data:(image\/(?:jpeg|png|webp));base64,([A-Za-z0-9+/]+=*)$/.exec(String(dataUrl || ""));
  if (!m) throw new Error("La foto debe ser JPG, PNG o WebP.");
  if (m[2].length * 0.75 > MAX_BYTES_FOTO) throw new Error("La foto es muy pesada (máximo 3 MB).");
  const { orden } = db.prepare("SELECT COALESCE(MAX(orden), 0) AS orden FROM fotos WHERE unidad = ?").get(unidadId);
  const { lastInsertRowid } = db.prepare("INSERT INTO fotos (unidad, orden, tipo, datos) VALUES (?, ?, ?, ?)").run(unidadId, orden + 1, m[1], m[2]);
  aplicar(lista);
  return { id: Number(lastInsertRowid), unidad: u };
}

const fotoDe = (unidadId, fotoId) => {
  const f = db.prepare("SELECT id FROM fotos WHERE id = ? AND unidad = ?").get(Number(fotoId), unidadId);
  if (!f) throw new Error("Esa foto no existe.");
  return f;
};

export function borrarFoto(unidadId, fotoId) {
  fotoDe(unidadId, fotoId);
  db.prepare("DELETE FROM fotos WHERE id = ?").run(Number(fotoId));
  aplicar(listaActual());
}

// La foto principal es la primera: la que muestra la web en la tarjeta de la cabaña
export function fotoPrincipal(unidadId, fotoId) {
  fotoDe(unidadId, fotoId);
  const { orden } = db.prepare("SELECT COALESCE(MIN(orden), 0) AS orden FROM fotos WHERE unidad = ?").get(unidadId);
  db.prepare("UPDATE fotos SET orden = ? WHERE id = ?").run(orden - 1, Number(fotoId));
  aplicar(listaActual());
}

// Al arrancar (antes que tarifas y calendarios): aplica la lista guardada y las fotos
export function cargarUnidades() {
  aplicar(listaActual());
  return Boolean(listaGuardada());
}
