// Service worker de la app de pesca: guarda la página y el último pronóstico consultado
// para poder verlo sin señal (por ejemplo, en el lago).
// También sirve al panel instalable: sin señal muestra un aviso. Los datos del panel nunca se guardan.
const CACHE = "pesca-v2";
const BASE = ["/pesca", "/pesca.js", "/estilos.css", "/pesca.webmanifest", "/img/icono-pesca.svg", "/img/icono-pesca-192.png"];
const SIN_CONEXION = "/sin-conexion.html";
const PANEL = ["/admin", "/ingresar"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll([...BASE, SIN_CONEXION])).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((claves) => Promise.all(claves.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim())
  );
});

// Primero la red; si no hay conexión, lo último guardado
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;
  if (e.request.mode === "navigate" && PANEL.includes(url.pathname)) {
    e.respondWith(fetch(e.request).catch(() => caches.match(SIN_CONEXION)));
    return;
  }
  if (!(BASE.includes(url.pathname) || url.pathname === "/api/pesca")) return;
  e.respondWith(
    fetch(e.request)
      .then((r) => {
        if (r.ok) {
          const copia = r.clone();
          caches.open(CACHE).then((c) => c.put(e.request, copia));
        }
        return r;
      })
      .catch(() => caches.match(e.request).then((r) => r || Response.error()))
  );
});
