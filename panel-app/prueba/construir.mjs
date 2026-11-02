// Arma www-prueba/: el panel de public/ más prueba.js, que lo hace funcionar sin servidor.
// Uso (desde panel-app/): node prueba/construir.mjs [--app]
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as esbuild from "esbuild";

const aqui = path.dirname(fileURLToPath(import.meta.url));
const raiz = path.resolve(aqui, "../..");
const salida = path.resolve(aqui, "../www-prueba");
const navegador = path.join(aqui, "navegador");

fs.rmSync(salida, { recursive: true, force: true });
fs.mkdirSync(path.join(salida, "img"), { recursive: true });

// src/db.js, src/config.js y node:crypto se reemplazan por sus versiones para el navegador
const reemplazos = {
  name: "reemplazos-navegador",
  setup(build) {
    build.onResolve({ filter: /^\.\/(db|config)\.js$/ }, (args) =>
      path.dirname(args.importer) === path.join(raiz, "src") ? { path: path.join(navegador, path.basename(args.path)) } : undefined
    );
    build.onResolve({ filter: /\/src\/(db|config)\.js$/ }, (args) => ({ path: path.join(navegador, path.basename(args.path)) }));
    build.onResolve({ filter: /^node:crypto$/ }, () => ({ path: path.join(navegador, "crypto.js") }));
    // sql.js menciona módulos de Node que en el navegador no usa
    build.onResolve({ filter: /^(fs|path|crypto)$/ }, () => ({ path: "vacio", namespace: "vacio" }));
    build.onLoad({ filter: /.*/, namespace: "vacio" }, () => ({ contents: "export default {}" }));
  },
};

await esbuild.build({
  entryPoints: [path.join(aqui, "entrada.js")],
  bundle: true,
  format: "iife",
  target: "chrome90",
  outfile: path.join(salida, "prueba.js"),
  loader: { ".wasm": "binary" },
  inject: [path.join(navegador, "bytes.js")],
  plugins: [reemplazos],
  minify: true,
  logLevel: "warning",
});

const publico = (f) => path.join(raiz, "public", f);
// Sin service worker: la app ya tiene todo adentro
const sinServiceWorker = (texto) => {
  const linea = 'if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});';
  if (!texto.includes(linea)) throw new Error("No se encontró el registro del service worker en public/");
  return texto.replace(linea, "");
};
fs.writeFileSync(path.join(salida, "admin.js"), sinServiceWorker(fs.readFileSync(publico("admin.js"), "utf8")));
for (const f of ["admin.css", "estilos.css"]) fs.copyFileSync(publico(f), path.join(salida, f));
for (const f of fs.readdirSync(publico("img")).filter((f) => f.startsWith("icono-panel"))) fs.copyFileSync(publico(`img/${f}`), path.join(salida, "img", f));

// Las páginas cargan prueba.js antes que todo y llevan el estilo del aviso de prueba
const estiloPrueba = `<style>
.aviso-prueba { display: flex; justify-content: space-between; align-items: center; gap: .6rem; flex-wrap: wrap; padding: .5rem 1rem; background: #f8ebc8; color: #7a5a10; font-size: .85rem; }
.aviso-prueba button { background: none; border: 1px solid #7a5a10; color: #7a5a10; border-radius: 999px; padding: .2rem .8rem; font: 600 .8rem Inter, sans-serif; }
.pagina-reserva { padding-top: 5.5rem; }
.pagina-reserva .aviso-prueba { position: fixed; top: 0; left: 0; right: 0; }
.usuarios-prueba { display: grid; gap: .5rem; margin-top: 1rem; }
</style>`;
for (const f of ["admin.html", "ingresar.html"]) {
  let html = fs.readFileSync(publico(f), "utf8");
  if (f === "ingresar.html") html = sinServiceWorker(html);
  html = html
    .replace("<head>", `<head>\n  <script src="/prueba.js"></script>`)
    .replace("</head>", `${estiloPrueba}\n</head>`)
    .replace(/<link rel="manifest"[^>]*>\n?/, "");
  fs.writeFileSync(path.join(salida, f), html);
}

// Capacitor responde index.html a /admin, /ingresar o /: se redirige a la página real
fs.writeFileSync(path.join(salida, "index.html"), `<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>TM Panel Prueba</title></head>
<body><script>
  const destino = { "/admin": "/admin.html", "/ingresar": "/ingresar.html" }[location.pathname.replace(/\\/$/, "")];
  location.replace(destino || (localStorage.getItem("tm-prueba-sesion") ? "/admin.html" : "/ingresar.html"));
</script></body></html>
`);

// --app: deja capacitor.config.json listo para compilar la app de prueba (sin servidor)
if (process.argv.includes("--app")) {
  const archivo = path.resolve(aqui, "../capacitor.config.json");
  const config = JSON.parse(fs.readFileSync(archivo, "utf8"));
  config.appId = "ar.tierrasmagicas.panel.prueba";
  config.appName = "TM Panel Prueba";
  config.webDir = "www-prueba";
  delete config.server;
  fs.writeFileSync(archivo, JSON.stringify(config, null, 2) + "\n");
}

console.log(`App de prueba lista en ${path.relative(process.cwd(), salida)}/`);
