// Generador de PDF mínimo (sin dependencias) para los informes del panel: títulos, párrafos, tablas
// y gráficos de barras, en A4 con Helvetica. Funciona en el navegador y en la app sin servidor.

const A4 = { ancho: 595.28, alto: 841.89 };
const MARGEN = 40;

// Anchos de Helvetica (1/1000 em) para los caracteres más usados; el resto se estima
const ANCHOS = {
  " ": 278, "!": 278, "$": 556, "%": 889, "(": 333, ")": 333, ",": 278, "-": 333, ".": 278, "/": 278, ":": 278, "·": 278,
  "0": 556, "1": 556, "2": 556, "3": 556, "4": 556, "5": 556, "6": 556, "7": 556, "8": 556, "9": 556,
  i: 222, j: 222, l: 222, f: 278, t: 278, r: 333, I: 278, m: 833, w: 722, M: 833, W: 944,
};
const anchoTexto = (texto, tamano, negrita = false) =>
  [...String(texto)].reduce((s, c) => s + (ANCHOS[c] ?? (c === c.toUpperCase() && c !== c.toLowerCase() ? 667 : 556)), 0) * (tamano / 1000) * (negrita ? 1.05 : 1);

// Texto a WinAnsi: los caracteres que no existen en Latin-1 se reemplazan por equivalentes
function codificar(texto) {
  return String(texto ?? "")
    .replace(/[→⟶]/g, "->").replace(/[–—]/g, "-").replace(/[“”]/g, '"').replace(/[‘’]/g, "'").replace(/…/g, "...")
    .replace(/[^\x20-\xff]/g, "?")
    .replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)");
}

export class Pdf {
  constructor({ titulo = "Informe", pie = "" } = {}) {
    this.titulo = titulo;
    this.pie = pie;
    this.paginas = [];
    this.nuevaPagina();
  }

  nuevaPagina() {
    this.ops = [];
    this.paginas.push(this.ops);
    this.y = A4.alto - MARGEN;
  }

  // Asegura espacio vertical; si no alcanza, pasa a la página siguiente
  espacio(alto) {
    if (this.y - alto < MARGEN + 20) this.nuevaPagina();
  }

  texto(x, y, texto, { tamano = 10, negrita = false, color = [0.16, 0.16, 0.15] } = {}) {
    this.ops.push(`BT ${color.join(" ")} rg /${negrita ? "F2" : "F1"} ${tamano} Tf ${x.toFixed(2)} ${y.toFixed(2)} Td (${codificar(texto)}) Tj ET`);
  }

  rect(x, y, ancho, alto, color) {
    this.ops.push(`${color.join(" ")} rg ${x.toFixed(2)} ${y.toFixed(2)} ${ancho.toFixed(2)} ${alto.toFixed(2)} re f`);
  }

  linea(x1, y1, x2, y2, color = [0.85, 0.83, 0.78], grosor = 0.6) {
    this.ops.push(`${color.join(" ")} RG ${grosor} w ${x1.toFixed(2)} ${y1.toFixed(2)} m ${x2.toFixed(2)} ${y2.toFixed(2)} l S`);
  }

  titulo1(texto, subtitulo = "") {
    this.espacio(50);
    this.texto(MARGEN, this.y - 18, texto, { tamano: 18, negrita: true, color: [0.18, 0.29, 0.23] });
    this.y -= 26;
    if (subtitulo) {
      this.texto(MARGEN, this.y - 10, subtitulo, { tamano: 10, color: [0.42, 0.42, 0.38] });
      this.y -= 16;
    }
    this.linea(MARGEN, this.y - 4, A4.ancho - MARGEN, this.y - 4, [0.76, 0.39, 0.24], 1.2);
    this.y -= 14;
  }

  titulo2(texto) {
    this.espacio(40);
    this.y -= 8;
    this.texto(MARGEN, this.y - 12, texto, { tamano: 13, negrita: true, color: [0.18, 0.29, 0.23] });
    this.y -= 20;
  }

  parrafo(texto, { tamano = 9.5, color } = {}) {
    const ancho = A4.ancho - 2 * MARGEN;
    const lineas = [];
    let actual = "";
    for (const palabra of String(texto).split(/\s+/)) {
      const prueba = actual ? `${actual} ${palabra}` : palabra;
      if (anchoTexto(prueba, tamano) > ancho && actual) {
        lineas.push(actual);
        actual = palabra;
      } else actual = prueba;
    }
    if (actual) lineas.push(actual);
    for (const l of lineas) {
      this.espacio(tamano + 4);
      this.texto(MARGEN, this.y - tamano, l, { tamano, color });
      this.y -= tamano + 4;
    }
    this.y -= 4;
  }

  // Tabla: columnas [{ titulo, ancho (fracción), derecha }], filas de textos. La última fila puede ir en negrita (total).
  tabla(columnas, filas, { totalEnNegrita = false, tamano = 8.5 } = {}) {
    const anchoTotal = A4.ancho - 2 * MARGEN;
    const anchos = columnas.map((c) => c.ancho * anchoTotal);
    const alto = tamano + 7;
    const recortar = (t, ancho, negrita) => {
      let s = String(t ?? "");
      while (s.length > 1 && anchoTexto(s, tamano, negrita) > ancho - 6) s = s.slice(0, -2) + "…";
      return s;
    };
    const fila = (valores, { cabecera = false, negrita = false } = {}) => {
      this.espacio(alto);
      if (cabecera) this.rect(MARGEN, this.y - alto, anchoTotal, alto, [0.96, 0.95, 0.91]);
      let x = MARGEN;
      valores.forEach((v, i) => {
        const txt = recortar(v, anchos[i], cabecera || negrita);
        const tx = columnas[i].derecha ? x + anchos[i] - 3 - anchoTexto(txt, tamano, cabecera || negrita) : x + 3;
        this.texto(tx, this.y - tamano - 2, txt, { tamano, negrita: cabecera || negrita, color: cabecera ? [0.42, 0.42, 0.38] : undefined });
        x += anchos[i];
      });
      this.y -= alto;
      this.linea(MARGEN, this.y, MARGEN + anchoTotal, this.y);
    };
    fila(columnas.map((c) => c.titulo), { cabecera: true });
    filas.forEach((f, i) => fila(f, { negrita: totalEnNegrita && i === filas.length - 1 }));
    this.y -= 8;
  }

  // Indicadores en dos columnas: [[etiqueta, valor], ...]
  indicadores(pares) {
    const anchoCol = (A4.ancho - 2 * MARGEN) / 2;
    for (let i = 0; i < pares.length; i += 2) {
      this.espacio(32);
      pares.slice(i, i + 2).forEach(([etiqueta, valor], j) => {
        const x = MARGEN + j * anchoCol;
        this.texto(x, this.y - 9, etiqueta, { tamano: 8.5, color: [0.42, 0.42, 0.38] });
        this.texto(x, this.y - 24, valor, { tamano: 13, negrita: true, color: [0.18, 0.29, 0.23] });
      });
      this.y -= 32;
    }
    this.y -= 4;
  }

  // Barras verticales de un solo color con el valor encima de cada barra
  barras(datos, { alto = 120, formato = (v) => String(v) } = {}) {
    this.espacio(alto + 34);
    const anchoTotal = A4.ancho - 2 * MARGEN;
    const base = this.y - alto - 4;
    const maximo = Math.max(1, ...datos.map((d) => d.valor));
    const paso = anchoTotal / datos.length;
    const anchoBarra = Math.min(34, paso * 0.62);
    this.linea(MARGEN, base, MARGEN + anchoTotal, base, [0.6, 0.58, 0.54], 0.8);
    datos.forEach((d, i) => {
      const h = (Math.max(0, d.valor) / maximo) * (alto - 16);
      const cx = MARGEN + paso * i + paso / 2;
      if (h > 0) this.rect(cx - anchoBarra / 2, base, anchoBarra, h, [0.31, 0.54, 0.39]);
      const valor = formato(d.valor);
      this.texto(cx - anchoTexto(valor, 7) / 2, base + h + 3, valor, { tamano: 7, color: [0.32, 0.32, 0.3] });
      this.texto(cx - anchoTexto(d.etiqueta, 7) / 2, base - 10, d.etiqueta, { tamano: 7, color: [0.42, 0.42, 0.38] });
    });
    this.y = base - 22;
  }

  // Devuelve el PDF como Uint8Array
  bytes() {
    const objetos = [];
    const agregar = (contenido) => objetos.push(contenido) && objetos.length;
    const catalogo = agregar(null);
    const paginasId = agregar(null);
    const f1 = agregar("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>");
    const f2 = agregar("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>");
    const kids = [];
    this.paginas.forEach((ops, i) => {
      const pie = `${this.pie}${this.pie ? " · " : ""}Página ${i + 1} de ${this.paginas.length}`;
      const contenido = [...ops,
        `0.85 0.83 0.78 RG 0.6 w ${MARGEN} ${MARGEN - 6} m ${A4.ancho - MARGEN} ${MARGEN - 6} l S`,
        `BT 0.42 0.42 0.38 rg /F1 7.5 Tf ${MARGEN} ${MARGEN - 18} Td (${codificar(pie)}) Tj ET`].join("\n");
      const stream = agregar(`<< /Length ${latin1(contenido).length} >>\nstream\n${contenido}\nendstream`);
      kids.push(agregar(`<< /Type /Page /Parent ${paginasId} 0 R /MediaBox [0 0 ${A4.ancho} ${A4.alto}] /Resources << /Font << /F1 ${f1} 0 R /F2 ${f2} 0 R >> >> /Contents ${stream} 0 R >>`));
    });
    objetos[catalogo - 1] = `<< /Type /Catalog /Pages ${paginasId} 0 R >>`;
    objetos[paginasId - 1] = `<< /Type /Pages /Kids [${kids.map((k) => `${k} 0 R`).join(" ")}] /Count ${kids.length} >>`;
    const info = agregar(`<< /Title (${codificar(this.titulo)}) /Producer (Tierras Magicas) >>`);

    let salida = "%PDF-1.4\n%\xe2\xe3\xcf\xd3\n";
    const offsets = [];
    objetos.forEach((o, i) => {
      offsets.push(latin1(salida).length);
      salida += `${i + 1} 0 obj\n${o}\nendobj\n`;
    });
    const xref = latin1(salida).length;
    salida += `xref\n0 ${objetos.length + 1}\n0000000000 65535 f \n` + offsets.map((o) => `${String(o).padStart(10, "0")} 00000 n \n`).join("");
    salida += `trailer\n<< /Size ${objetos.length + 1} /Root ${catalogo} 0 R /Info ${info} 0 R >>\nstartxref\n${xref}\n%%EOF`;
    return latin1(salida);
  }
}

// Cadena (ya en el rango 0-255) a bytes Latin-1 / WinAnsi
function latin1(texto) {
  const bytes = new Uint8Array(texto.length);
  for (let i = 0; i < texto.length; i++) bytes[i] = texto.charCodeAt(i) & 0xff;
  return bytes;
}
