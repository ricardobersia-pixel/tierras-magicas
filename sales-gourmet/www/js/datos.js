// Datos de las Sales Gourmet Tierras Mágicas.
// Fuentes:
// - Fórmulas: Tierras_Magicas_Formulaciones_Consolidadas_2_0.xlsx (hoja 01_Formulaciones), sin correcciones.
// - Textos de etiqueta: etiquetas_tierras_magicas_A4.pdf.
// - Recetas y guía de uso: Tierras_Magicas_Libro_de_Cocina_COMPLETO_FINAL.pdf.
// Los avisos de seguridad (campo "seguridad") se agregaron en la app; no están en el libro.

export const SALES = [
  {
    codigo: "TM-01",
    nombre: "Caza Patagónica",
    descripcion: "Sal marina con hongos y especias del bosque",
    ideal: "Ideal para carnes rojas, caza mayor y papas al horno.",
    color: "#1f3a24",
    imagen: "img/etiqueta-tm-01.jpg",
    formula: [
      { ingrediente: "Sal Marina", tipo: "Base", granulometria: "Grano fino", pct: 74 },
      { ingrediente: "Hongos secos", tipo: "Bosque", granulometria: "Molido medio", pct: 10 },
      { ingrediente: "Cebolla deshidratada", tipo: "Vegetal", granulometria: "Granulada", pct: 5 },
      { ingrediente: "Ajo en escamas", tipo: "Especia", granulometria: "Triturado", pct: 4 },
      { ingrediente: "Pimienta negra", tipo: "Especia", granulometria: "Molido medio", pct: 3 },
      { ingrediente: "Romero", tipo: "Hierba", granulometria: "Molido fino", pct: 2 },
      { ingrediente: "Tomillo", tipo: "Hierba", granulometria: "Molido fino", pct: 1 },
      { ingrediente: "Merkén ahumado", tipo: "Especia", granulometria: "Molido fino", pct: 1 },
    ],
    recetas: [
      {
        titulo: "Bife de chorizo al fogón",
        bajada: "Realzá el sabor natural de la carne con un toque de bosque y especias.",
        pasos: ["Espolvorear generosamente antes de cocinar.", "Cocinar a las brasas o plancha.", "Dejar reposar 5 minutos y servir."],
      },
      {
        titulo: "Ciervo al horno con papas",
        bajada: "Aporta profundidad y un aroma silvestre.",
        pasos: ["Frotar la carne con la sal.", "Hornear a 180 °C por 90 minutos.", "Acompañar con papas rústicas."],
        seguridad: "Carne de caza: cocinar hasta 63 °C en el centro en cortes enteros (71 °C si es picada).",
      },
      {
        titulo: "Hongos salteados",
        bajada: "Potenciá el sabor terroso de los hongos.",
        pasos: ["Saltear hongos frescos en aceite de oliva.", "Agregar la sal al final de la cocción.", "Ideal como guarnición o entrada."],
        seguridad: "Usar solo hongos comprados o identificados con certeza: varios hongos silvestres de la Patagonia son tóxicos.",
      },
      {
        titulo: "Papas al disco",
        bajada: "Crujientes por fuera, tiernas por dentro.",
        pasos: ["Cocinar las papas en disco con aceite.", "Condimentar con la sal durante la cocción.", "Terminar con romero fresco."],
      },
      {
        titulo: "Vegetales a la parrilla",
        bajada: "Un toque de bosque para tus verduras.",
        pasos: ["Cortar vegetales en bastones o rodajas.", "Rociar con aceite de oliva y la sal.", "Asar a la parrilla hasta dorar."],
      },
    ],
  },
  {
    codigo: "TM-02",
    nombre: "Bosque Andino",
    descripcion: "Sal con hongos, hierbas aromáticas y especias",
    ideal: "Ideal para huevos, pastas, vegetales y comidas frescas.",
    color: "#4a4416",
    imagen: "img/etiqueta-tm-02.jpg",
    formula: [
      { ingrediente: "Sal con Hongos", tipo: "Base", granulometria: "Grano fino", pct: 80 },
      { ingrediente: "Mix de Hierbas", tipo: "Hierbas", granulometria: "Molido medio", pct: 6 },
      { ingrediente: "Ciboulette", tipo: "Hierba", granulometria: "Cortado fino", pct: 4 },
      { ingrediente: "Cebolla deshidratada", tipo: "Vegetal", granulometria: "Granulada", pct: 4 },
      { ingrediente: "Ajo en escamas", tipo: "Especia", granulometria: "Triturado", pct: 3 },
      { ingrediente: "Orégano", tipo: "Hierba", granulometria: "Molido fino", pct: 2 },
      { ingrediente: "Pimienta verde", tipo: "Especia", granulometria: "Molido medio", pct: 1 },
    ],
    recetas: [
      {
        titulo: "Risotto de hongos",
        bajada: "Cremoso, aromático y lleno de sabor.",
        pasos: ["Preparar el risotto de la forma clásica.", "Agregar la sal al final de la cocción.", "Servir con queso parmesano."],
      },
      {
        titulo: "Pollo al horno",
        bajada: "Hierbas y especias que realzan cada bocado.",
        pasos: ["Frotar el pollo con la sal y aceite de oliva.", "Hornear a 190 °C por 75 minutos.", "Dejar reposar y cortar."],
        seguridad: "El pollo está listo con 74 °C en la parte más gruesa del muslo.",
      },
      {
        titulo: "Salmón a la plancha",
        bajada: "Perfecto para pescados y mariscos.",
        pasos: ["Cocinar el salmón por la parte de la piel.", "Añadir la sal en los últimos minutos.", "Acompañar con limón."],
      },
      {
        titulo: "Verduras asadas",
        bajada: "Aromáticas, simples y deliciosas.",
        pasos: ["Cortar verduras en trozos.", "Mezclar con aceite de oliva y la sal.", "Hornear a 200 °C hasta dorar."],
      },
      {
        titulo: "Focaccia casera",
        bajada: "Pan especiado con aroma de hierbas.",
        pasos: ["Preparar la masa de focaccia.", "Espolvorear la sal antes del horneado.", "Añadir aceite de oliva y romero fresco."],
      },
    ],
  },
  {
    codigo: "TM-03",
    nombre: "Lago & Trucha",
    descripcion: "Sal con limón y mandarina, eneldo y especias suaves",
    ideal: "Ideal para pescados, mariscos, aves y vegetales a la parrilla.",
    color: "#14284a",
    imagen: "img/etiqueta-tm-03.jpg",
    formula: [
      { ingrediente: "Sal con Limón", tipo: "Base", granulometria: "Grano fino", pct: 65 },
      { ingrediente: "Sal con Mandarina", tipo: "Base", granulometria: "Grano fino", pct: 15 },
      { ingrediente: "Eneldo", tipo: "Hierba", granulometria: "Molido fino", pct: 5 },
      { ingrediente: "Ciboulette", tipo: "Hierba", granulometria: "Cortado fino", pct: 4 },
      { ingrediente: "Pimienta verde", tipo: "Especia", granulometria: "Molido medio", pct: 3 },
      { ingrediente: "Mix de Hierbas", tipo: "Hierbas", granulometria: "Molido medio", pct: 3 },
      { ingrediente: "Jengibre", tipo: "Especia", granulometria: "Molido fino", pct: 2 },
      { ingrediente: "Hongos secos", tipo: "Bosque", granulometria: "Molido medio", pct: 2 },
      { ingrediente: "Cúrcuma", tipo: "Especia", granulometria: "Molido fino", pct: 1 },
    ],
    recetas: [
      {
        titulo: "Trucha a la parrilla",
        bajada: "Fresca, cítrica y delicada.",
        pasos: ["Frotar la trucha con la sal.", "Asar a la parrilla por ambos lados.", "Servir con eneldo fresco."],
      },
      {
        titulo: "Ceviche de pescado",
        bajada: "Ligero, cítrico y aromático.",
        pasos: ["Cortar el pescado en cubos.", "Marinar con jugo de limón y naranja.", "Añadir la sal y dejar reposar 20 minutos."],
        seguridad:
          "El limón no cocina ni elimina parásitos. Usar pescado apto para consumo crudo o congelado antes a −20 °C durante 7 días. No usar trucha de pesca sin congelar.",
      },
      {
        titulo: "Camarones a la plancha",
        bajada: "Un toque cítrico que los hace irresistibles.",
        pasos: ["Marinar los camarones con la sal y aceite.", "Cocinar en plancha bien caliente.", "Servir con limón."],
      },
      {
        titulo: "Ensalada fresca",
        bajada: "Realza vegetales y aderezos.",
        pasos: ["Preparar la ensalada de tu elección.", "Aliñar con aceite de oliva y la sal.", "Agregar al final para máxima frescura."],
      },
      {
        titulo: "Verduras al horno",
        bajada: "Cítricos y especias para un plato perfecto.",
        pasos: ["Cortar verduras en trozos.", "Mezclar con aceite y la sal.", "Hornear a 200 °C hasta dorar."],
      },
    ],
  },
  {
    codigo: "TM-04",
    nombre: "Reserva del Fogón",
    descripcion: "Sal ahumada con vino tinto y especias",
    ideal: "Ideal para asados, carnes a la parrilla, cerdo y vegetales al rescoldo.",
    color: "#4a1414",
    imagen: "img/etiqueta-tm-04.jpg",
    formula: [
      { ingrediente: "Sal Ahumada", tipo: "Base", granulometria: "Grano fino", pct: 65 },
      { ingrediente: "Sal con Vino Tinto", tipo: "Base", granulometria: "Grano fino", pct: 15 },
      { ingrediente: "Hongos secos", tipo: "Bosque", granulometria: "Molido medio", pct: 8 },
      { ingrediente: "Cebolla deshidratada", tipo: "Vegetal", granulometria: "Granulada", pct: 4 },
      { ingrediente: "Ajo en escamas", tipo: "Especia", granulometria: "Triturado", pct: 3 },
      { ingrediente: "Romero", tipo: "Hierba", granulometria: "Molido fino", pct: 2 },
      { ingrediente: "Pimienta negra", tipo: "Especia", granulometria: "Molido medio", pct: 2 },
      { ingrediente: "Merkén ahumado", tipo: "Especia", granulometria: "Molido fino", pct: 1 },
    ],
    recetas: [
      {
        titulo: "Costillar a la parrilla",
        bajada: "Ahumado, intenso y memorable.",
        pasos: ["Frotar el costillar con la sal.", "Cocinar a fuego bajo en el asador.", "Pintar con vino tinto durante la cocción."],
      },
      {
        titulo: "Lomo de cerdo al horno",
        bajada: "Aromático y jugoso.",
        pasos: ["Condimentar el lomo con la sal.", "Hornear a 180 °C por 60 minutos.", "Dejar reposar y cortar."],
        seguridad: "El cerdo está listo con 63 °C en el centro y 3 minutos de reposo.",
      },
      {
        titulo: "Cebollas y pimientos asados",
        bajada: "Sabor ahumado y profundo.",
        pasos: ["Asar las verduras enteras o en mitades.", "Espolvorear la sal al final.", "Ideal para acompañar carnes."],
      },
      {
        titulo: "Papas al horno con queso",
        bajada: "Simples y llenas de sabor.",
        pasos: ["Cocinar las papas al horno.", "Abrir, agregar manteca, queso y la sal.", "Gratinar unos minutos."],
      },
      {
        titulo: "Tabla de quesos y fiambres",
        bajada: "Ideal para sorprender.",
        pasos: ["Usar la sal para realzar quesos duros y semiduros.", "Una combinación simple para compartir."],
      },
    ],
  },
];

// Ingredientes que son a su vez mezclas. Sin ficha propia no hay trazabilidad completa
// ni lista de ingredientes completa para el rótulo (hoja 04_Notas de las formulaciones).
export const COMPUESTOS = ["Sal con Hongos", "Sal con Limón", "Sal con Mandarina", "Sal Ahumada", "Sal con Vino Tinto", "Mix de Hierbas"];

// Ingredientes de base salina: se usan para calcular el contenido de sal de cada producto.
// SUPUESTO: las sales saborizadas se toman como 100% sal hasta tener su ficha.
export const BASES_SALINAS = ["Sal Marina", "Sal con Hongos", "Sal con Limón", "Sal con Mandarina", "Sal Ahumada", "Sal con Vino Tinto"];

// Guía de uso (página 6 del libro)
export const GUIA = [
  { titulo: "¿Cómo usarlas?", texto: "Espolvorear la sal al final de la cocción o durante el proceso según la receta." },
  { titulo: "Cantidad recomendada", texto: "1/2 a 1 cucharadita por porción, ajustar a gusto." },
  { titulo: "Conservación", texto: "Guardar en un recipiente hermético, en lugar fresco y seco." },
  { titulo: "El toque final", texto: "Un poco de sal gourmet transforma cualquier plato en una experiencia." },
];

// Hoja de etiquetas: 4 columnas × 6 filas (lo que muestra etiquetas_tierras_magicas_A4.pdf)
export const ETIQUETAS_POR_HOJA = 24;
