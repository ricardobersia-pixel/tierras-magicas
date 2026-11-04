// Gráficos de barras en SVG para las estadísticas del panel. Una sola serie por gráfico (un solo color),
// con el valor escrito en cada barra, el detalle al pasar el dedo o el mouse (<title>) y una tabla con los datos.

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

// Barras verticales: datos [{ etiqueta, valor, detalle }]
// Las medidas están en unidades del viewBox (640 de ancho): en un celular se ve a la mitad, por eso letras de 22-24.
export function barras(datos, { formato = String, alto = 260, titulo = "" } = {}) {
  const ancho = 640;
  const arriba = 34;
  const abajo = 40;
  const maximo = Math.max(1, ...datos.map((d) => d.valor));
  const lateral = 24; // margen para que las etiquetas de los extremos no se corten
  const paso = (ancho - 2 * lateral) / Math.max(1, datos.length);
  const claseValor = datos.length > 8 ? "grafico-valor chico" : "grafico-valor";
  const anchoBarra = Math.min(44, paso * 0.62);
  const zona = alto - arriba - abajo;
  const base = alto - abajo;
  const barrasSvg = datos.map((d, i) => {
    const h = (Math.max(0, d.valor) / maximo) * zona;
    const x = lateral + paso * i + (paso - anchoBarra) / 2;
    const cx = lateral + paso * i + paso / 2;
    const r = Math.min(4, h / 2, anchoBarra / 2);
    // Esquinas redondeadas solo arriba, la base queda apoyada en el eje
    const camino = h > 0
      ? `M${x},${base} V${base - h + r} Q${x},${base - h} ${x + r},${base - h} H${x + anchoBarra - r} Q${x + anchoBarra},${base - h} ${x + anchoBarra},${base - h + r} V${base} Z`
      : "";
    return `<g class="grafico-barra"><title>${esc(d.detalle || `${d.etiqueta}: ${formato(d.valor)}`)}</title>
      <rect x="${lateral + paso * i}" y="0" width="${paso}" height="${alto}" fill="transparent"/>
      ${camino ? `<path d="${camino}" class="grafico-marca"/>` : ""}
      ${d.valor ? `<text x="${cx}" y="${base - h - 8}" text-anchor="middle" class="${claseValor}">${esc(formato(d.valor))}</text>` : ""}
      <text x="${cx}" y="${alto - 10}" text-anchor="middle" class="grafico-eje">${esc(d.etiqueta)}</text></g>`;
  }).join("");
  return `<svg class="grafico" viewBox="0 0 ${ancho} ${alto}" role="img" aria-label="${esc(titulo)}">
    <line x1="0" y1="${base}" x2="${ancho}" y2="${base}" class="grafico-base"/>${barrasSvg}</svg>`;
}

// Barras horizontales para categorías (canales, cabañas, recursos): datos [{ etiqueta, valor, detalle }]
export function barrasH(datos, { formato = String, titulo = "" } = {}) {
  if (!datos.length) return `<p class="nota">Sin datos en el período.</p>`;
  const ancho = 640;
  const fila = 46;
  const izquierda = 200;
  const derecha = 150;
  const maximo = Math.max(1, ...datos.map((d) => d.valor));
  const zona = ancho - izquierda - derecha;
  const alto = datos.length * fila;
  const filas = datos.map((d, i) => {
    const w = (Math.max(0, d.valor) / maximo) * zona;
    const y = i * fila + 9;
    const r = Math.min(4, w / 2);
    const camino = w > 0
      ? `M${izquierda},${y} H${izquierda + w - r} Q${izquierda + w},${y} ${izquierda + w},${y + r} V${y + 28 - r} Q${izquierda + w},${y + 28} ${izquierda + w - r},${y + 28} H${izquierda} Z`
      : "";
    return `<g class="grafico-barra"><title>${esc(d.detalle || `${d.etiqueta}: ${formato(d.valor)}`)}</title>
      <rect x="0" y="${i * fila}" width="${ancho}" height="${fila}" fill="transparent"/>
      <text x="${izquierda - 10}" y="${y + 21}" text-anchor="end" class="grafico-eje">${esc(d.etiqueta)}</text>
      ${camino ? `<path d="${camino}" class="grafico-marca"/>` : ""}
      <text x="${izquierda + w + 8}" y="${y + 21}" class="grafico-valor">${esc(formato(d.valor))}</text></g>`;
  }).join("");
  return `<svg class="grafico" viewBox="0 0 ${ancho} ${alto}" role="img" aria-label="${esc(titulo)}">
    <line x1="${izquierda}" y1="0" x2="${izquierda}" y2="${alto}" class="grafico-base"/>${filas}</svg>`;
}

// Tabla con los mismos datos del gráfico (para leer los valores exactos o copiarlos)
export function tablaDatos(columnas, filas) {
  return `<details class="tabla-datos"><summary>Ver tabla</summary><div class="tabla-scroll"><table class="tabla">
    <thead><tr>${columnas.map((c, i) => `<th${i ? ' class="num"' : ""}>${esc(c)}</th>`).join("")}</tr></thead>
    <tbody>${filas.map((f) => `<tr>${f.map((v, i) => `<td${i ? ' class="num"' : ""}>${esc(v)}</td>`).join("")}</tr>`).join("")}</tbody></table></div></details>`;
}
