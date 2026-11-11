// Service worker de Taller TM: guarda la app completa para usarla sin señal.
// Cambiar VERSION en cada publicación para que los teléfonos descarguen la nueva.
const VERSION = "taller-tm-v2";
const ARCHIVOS = [
  "./",
  "index.html",
  "css/estilos.css",
  "js/app.js",
  "js/datos.js",
  "js/calculos.js",
  "manifest.webmanifest",
  "img/icono.svg",
  "img/icono-192.png",
  "img/icono-512.png",
  "img/logo-tierras-magicas.jpg",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(ARCHIVOS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((claves) => Promise.all(claves.filter((k) => k !== VERSION).map((k) => caches.delete(k)))).then(() => self.clients.claim())
  );
});

// Primero lo guardado y se actualiza en segundo plano
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(
    caches.open(VERSION).then(async (cache) => {
      const guardada = await cache.match(e.request, { ignoreSearch: true });
      const red = fetch(e.request)
        .then((r) => {
          if (r.ok) cache.put(e.request, r.clone());
          return r;
        })
        .catch(() => guardada || Response.error());
      return guardada || red;
    })
  );
});
