// Service worker mínimo: faz cache do "casco" da interface para a PWA abrir
// offline. A conversão em si continua dependendo do backend (rede local).
const CACHE = "tomarkdown-v1";
const SHELL = [
  ".",
  "index.html",
  "style.css",
  "app.js",
  "manifest.webmanifest",
  "icon.svg",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  // Nunca faz cache das chamadas de API.
  if (url.pathname.startsWith("/api/")) return;
  e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request)));
});
