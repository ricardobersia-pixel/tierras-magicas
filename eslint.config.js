import js from "@eslint/js";
import globals from "globals";

export default [
  { ignores: ["**/node_modules/", "data/", "entrega/", "vistas_3d/", "pesca-patagonia/android/", "sales-gourmet/android/", "panel-app/android/", "panel-app/www-prueba/"] },
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
  { files: ["public/**/*.js", "pesca-patagonia/www/**/*.js", "sales-gourmet/www/**/*.js", "panel-app/www/**/*.js", "panel-app/prueba/**/*.js"], languageOptions: { globals: globals.browser } },
  { files: ["public/sw.js", "pesca-patagonia/www/sw.js", "sales-gourmet/www/sw.js"], languageOptions: { globals: globals.serviceworker } },
];
