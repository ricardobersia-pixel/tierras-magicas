// Service worker de Sales de la Cordillera: guarda la app completa para usarla sin señal.
// Cambiar VERSION en cada publicación para que los teléfonos descarguen la nueva.
const VERSION = "sales-tm-v7";
const ARCHIVOS = [
  "./",
  "index.html",
  "css/estilos.css",
  "js/app.js",
  "js/datos.js",
  "manifest.webmanifest",
  "img/icono.jpg",
  "img/icono-192.png",
  "img/icono-512.png",
  "img/portada.jpg",
  "img/logo-tierras-magicas.jpg",
  "img/etiqueta-tm-01.jpg",
  "img/etiqueta-tm-02.jpg",
  "img/etiqueta-tm-03.jpg",
  "img/etiqueta-tm-04.jpg",
  "img/recetas/asado-tira.jpg",
  "img/recetas/bife-chorizo-fogon.jpg",
  "img/recetas/bondiola-horno.jpg",
  "img/recetas/ceviche-trucha.jpg",
  "img/recetas/ciervo-papas.jpg",
  "img/recetas/cordero-cruz.jpg",
  "img/recetas/focaccia-hierbas.jpg",
  "img/recetas/hongos-salteados.jpg",
  "img/recetas/huevos-ciboulette.jpg",
  "img/recetas/jabali-hongos.jpg",
  "img/recetas/langostinos-plancha.jpg",
  "img/recetas/noquis-hierbas.jpg",
  "img/recetas/papas-horno-romero.jpg",
  "img/recetas/papas-rescoldo.jpg",
  "img/recetas/pollo-limon.jpg",
  "img/recetas/risotto-hongos.jpg",
  "img/recetas/trucha-parrilla.jpg",
  "img/recetas/vegetales-asados.jpg",
  "img/recetas/vegetales-parrilla-eneldo.jpg",
  "img/recetas/vegetales-rescoldo.jpg",
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
