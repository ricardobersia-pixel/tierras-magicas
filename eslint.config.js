import js from "@eslint/js";
import globals from "globals";

export default [
  { ignores: ["node_modules/", "data/", "entrega/", "vistas_3d/"] },
  js.configs.recommended,
  {
    rules: {
      // Desestructurar para quitar campos ({ ical_importar, ...c }) es intencional
      "no-unused-vars": ["error", { ignoreRestSiblings: true }],
      // catch {} vacío para ignorar errores esperados (p. ej. ROLLBACK sin transacción abierta)
      "no-empty": ["error", { allowEmptyCatch: true }],
    },
  },
  { files: ["src/**/*.js", "test/**/*.js", "eslint.config.js"], languageOptions: { globals: globals.node } },
  { files: ["public/**/*.js"], languageOptions: { globals: globals.browser } },
  { files: ["public/sw.js"], languageOptions: { globals: globals.serviceworker } },
];
