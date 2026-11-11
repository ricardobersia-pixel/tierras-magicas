// Cálculos de producción de las Sales Gourmet. Sin dependencias del navegador: se prueban con node --test.
import { SALES, BASES_SALINAS } from "./datos.js";

/** Redondeo a 1 decimal (gramos) o al entero (pesos) */
export const r1 = (x) => Math.round(x * 10) / 10;

export function buscarSal(codigo) {
  const sal = SALES.find((s) => s.codigo === codigo);
  if (!sal) throw new Error(`Sal desconocida: ${codigo}`);
  return sal;
}

/** Control de la fórmula: tiene que sumar 100% (equivale a 1.000 g/kg) */
export function controlFormula(sal) {
  const suma = r1(sal.formula.reduce((t, f) => t + f.pct, 0));
  return { suma, cierra: Math.abs(suma - 100) < 0.001 };
}

/** Gramos de cada ingrediente para un lote de `gramos` de producto terminado */
export function escalar(sal, gramos) {
  return sal.formula.map((f) => ({ ...f, gramos: r1((gramos * f.pct) / 100) }));
}

/** Porcentaje de base salina del producto (para el aviso de sodio) */
export function pctSal(sal) {
  return sal.formula.filter((f) => BASES_SALINAS.includes(f.ingrediente)).reduce((t, f) => t + f.pct, 0);
}

/**
 * Plan de compra consolidado.
 * @param {Record<string, number>} plan gramos de producto terminado por código, p. ej. { "TM-01": 5000 }
 * @param {number} margen margen de compra/proceso (0.05 = 5%, como la planilla de 20 kg). No cambia la fórmula.
 * @returns {{ filas: {ingrediente, porSal: Record<string, number>, total, compra}[], totales: {porSal, total, compra} }}
 */
export function planCompra(plan, margen = 0.05) {
  const mapa = new Map();
  const totalesPorSal = {};
  for (const [codigo, gramos] of Object.entries(plan)) {
    if (!(gramos > 0)) continue;
    const sal = buscarSal(codigo);
    totalesPorSal[codigo] = 0;
    for (const f of escalar(sal, gramos)) {
      const fila = mapa.get(f.ingrediente) || { ingrediente: f.ingrediente, porSal: {}, total: 0 };
      fila.porSal[codigo] = r1((fila.porSal[codigo] || 0) + f.gramos);
      fila.total = r1(fila.total + f.gramos);
      totalesPorSal[codigo] = r1(totalesPorSal[codigo] + f.gramos);
      mapa.set(f.ingrediente, fila);
    }
  }
  const filas = [...mapa.values()]
    .map((f) => ({ ...f, compra: r1(f.total * (1 + margen)) }))
    .sort((a, b) => a.ingrediente.localeCompare(b.ingrediente, "es"));
  const total = r1(filas.reduce((t, f) => t + f.total, 0));
  return { filas, totales: { porSal: totalesPorSal, total, compra: r1(total * (1 + margen)) } };
}

/** Frascos y hojas de etiquetas para un lote */
export function envasado(gramos, netoPorFrasco, etiquetasPorHoja = 24) {
  if (!(netoPorFrasco > 0)) return { frascos: 0, sobrante: gramos, hojas: 0 };
  const frascos = Math.floor((gramos + 1e-9) / netoPorFrasco);
  return { frascos, sobrante: r1(gramos - frascos * netoPorFrasco), hojas: Math.ceil(frascos / etiquetasPorHoja) };
}

/**
 * Costo de un producto con los precios cargados por el usuario.
 * @param {object} sal
 * @param {Record<string, number>} precios pesos por kg de cada ingrediente
 * @param {object} o { margen: margen de compra (0.05), neto: g por frasco, envase: $ por frasco (frasco+tapa+etiqueta), ganancia: 0.4 = 40% sobre el precio }
 */
export function costos(sal, precios, { margen = 0.05, neto = 0, envase = 0, ganancia = 0 } = {}) {
  const faltan = sal.formula.filter((f) => typeof precios[f.ingrediente] !== "number" || !(precios[f.ingrediente] >= 0)).map((f) => f.ingrediente);
  // Costo de 1 kg terminado: g/kg × (1 + margen) × $/kg ÷ 1000
  const porKg = sal.formula.reduce((t, f) => t + ((f.pct * 10 * (1 + margen)) / 1000) * (precios[f.ingrediente] || 0), 0);
  const insumoFrasco = (porKg * neto) / 1000;
  const porFrasco = insumoFrasco + (envase || 0);
  // Precio para que la ganancia sea ese % del precio (margen sobre venta, no recargo sobre costo)
  const precio = ganancia > 0 && ganancia < 1 ? porFrasco / (1 - ganancia) : porFrasco;
  return {
    completo: faltan.length === 0,
    faltan,
    porKg: Math.round(porKg),
    insumoFrasco: Math.round(insumoFrasco),
    porFrasco: Math.round(porFrasco),
    precioSugerido: Math.round(precio),
  };
}

/** Rendimiento del lote (peso real ÷ objetivo), como la hoja "Control Producción" */
export function rendimiento(objetivo, real) {
  if (!(objetivo > 0) || !(real >= 0)) return 0;
  return r1((real / objetivo) * 100);
}

/** Código de lote: TM-01-AAMMDD-NN */
export function codigoLote(codigo, fechaISO, numero = 1) {
  const [a, m, d] = fechaISO.split("-");
  return `${codigo}-${a.slice(2)}${m}${d}-${String(numero).padStart(2, "0")}`;
}

/** Siguiente número de lote del día para esa sal */
export function siguienteNumero(lotes, codigo, fechaISO) {
  const prefijo = codigoLote(codigo, fechaISO, 0).slice(0, -2);
  const usados = lotes.filter((l) => l.lote.startsWith(prefijo)).map((l) => Number(l.lote.slice(-2)));
  return usados.length ? Math.max(...usados) + 1 : 1;
}

/** Fecha + meses (vencimiento), en ISO. Si el día no existe en el mes destino, usa el último día. */
export function sumarMeses(fechaISO, meses) {
  const [a, m, d] = fechaISO.split("-").map(Number);
  const total = a * 12 + (m - 1) + meses;
  const anio = Math.floor(total / 12);
  const mes = (total % 12) + 1;
  const ultimo = new Date(Date.UTC(anio, mes, 0)).getUTCDate();
  return `${anio}-${String(mes).padStart(2, "0")}-${String(Math.min(d, ultimo)).padStart(2, "0")}`;
}

/**
 * Stock por ingrediente.
 * @param {{tipo: "compra"|"consumo"|"ajuste", ingrediente, gramos}[]} movimientos (consumo en positivo)
 */
export function stock(movimientos) {
  const s = {};
  for (const m of movimientos) {
    const signo = m.tipo === "consumo" ? -1 : 1;
    s[m.ingrediente] = r1((s[m.ingrediente] || 0) + signo * m.gramos);
  }
  return s;
}

/** Lo que falta comprar para un plan, según el stock actual (compra con margen − stock) */
export function faltantes(plan, stockActual, margen = 0.05) {
  return planCompra(plan, margen)
    .filas.map((f) => ({ ingrediente: f.ingrediente, necesario: f.compra, stock: stockActual[f.ingrediente] || 0 }))
    .map((f) => ({ ...f, comprar: r1(Math.max(0, f.necesario - f.stock)) }))
    .filter((f) => f.comprar > 0);
}

/** Movimientos de consumo de un lote producido */
export function consumosDeLote(codigo, gramos, lote) {
  return escalar(buscarSal(codigo), gramos).map((f) => ({ tipo: "consumo", ingrediente: f.ingrediente, gramos: f.gramos, ref: lote }));
}

/** Lista de ingredientes para el rótulo: en orden decreciente de peso, como pide el Código Alimentario Argentino */
export function listaIngredientes(sal) {
  return [...sal.formula]
    .sort((a, b) => b.pct - a.pct)
    .map((f) => f.ingrediente.charAt(0) + f.ingrediente.slice(1).toLowerCase())
    .join(", ");
}

/** CSV con ; (Excel en español) */
export function csv(filas) {
  const celda = (v) => {
    const t = v === null || v === undefined ? "" : String(v);
    return /[;"\n]/.test(t) ? `"${t.replace(/"/g, '""')}"` : t;
  };
  return filas.map((f) => f.map(celda).join(";")).join("\r\n");
}

/** Formato de gramos para mostrar: 3.885 g o 3,9 kg */
export function formatoGramos(g) {
  if (Math.abs(g) >= 10000) return `${(g / 1000).toLocaleString("es-AR", { maximumFractionDigits: 2 })} kg`;
  return `${g.toLocaleString("es-AR", { maximumFractionDigits: 1 })} g`;
}
