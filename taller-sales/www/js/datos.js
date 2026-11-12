// TM Sales: datos públicos de las sales. Las FÓRMULAS NO ESTÁN EN EL CÓDIGO.
// Se cargan desde un archivo privado (Datos → Cargar fórmulas) y quedan guardadas solo en el teléfono.
// El repositorio es público: nunca agregar acá porcentajes ni gramos de las fórmulas.

export const VARIEDADES = [
  { codigo: "TM-01", nombre: "Caza Patagónica", descripcion: "Sal marina con hongos y especias del bosque" },
  { codigo: "TM-02", nombre: "Bosque Andino", descripcion: "Sal con hongos, hierbas aromáticas y especias" },
  { codigo: "TM-03", nombre: "Lago & Trucha", descripcion: "Sal con limón y mandarina, eneldo y especias suaves" },
  { codigo: "TM-04", nombre: "Reserva del Fogón", descripcion: "Sal ahumada con vino tinto y especias" },
];

// Hoja de etiquetas corregida: 4 columnas × 6 filas (sales-gourmet/etiquetas/)
export const ETIQUETAS_POR_HOJA = 24;
