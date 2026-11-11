import js from "@eslint/js";
import globals from "globals";

export default [
  { ignores: ["**/node_modules/", "data/", "entrega/", "vistas_3d/", "pesca-patagonia/android/", "sales-gourmet/android/", "taller-sales/android/", "panel-app/android/", "panel-app/www-prueba/"] },
  js.configs.recommended,
  {
    rules: {
      // Desestructurar para quitar campos ({ ical_importar, ...c }) es intencional
      "no-unused-vars": ["error", { ignoreRestSiblings: true }],
      // catch {} vacío para ignorar errores esperados (p. ej. ROLLBACK sin transacción abierta)
      "no-empty": ["error", { allowEmptyCatch: true }],
    },
  },
  { files: ["src/**/*.js", "test/**/*.js", "eslint.config.js", "panel-app/configurar.mjs", "panel-app/prueba/construir.mjs"], languageOptions: { globals: globals.node } },
  { files: ["public/**/*.js", "pesca-patagonia/www/**/*.js", "sales-gourmet/www/**/*.js", "taller-sales/www/**/*.js", "panel-app/www/**/*.js", "panel-app/prueba/**/*.js"], languageOptions: { globals: globals.browser } },
  // Generador de etiquetas: Node (CommonJS) con código que corre en la página de Playwright
  { files: ["sales-gourmet/etiquetas/*.cjs"], languageOptions: { sourceType: "commonjs", globals: { ...globals.node, document: "readonly" } } },
  { files: ["public/sw.js", "pesca-patagonia/www/sw.js", "sales-gourmet/www/sw.js", "taller-sales/www/sw.js"], languageOptions: { globals: globals.serviceworker } },
];
