const CACHE_NAME = 'asistencia-shell-v1';
const APP_SHELL = [
  '/',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/asistencia/scan-offline/',       // tu HTML
  'https://unpkg.com/html5-qrcode@2.4.1/minified/html5-qrcode.min.js'
];

self.addEventListener('install', evt => {
  evt.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', evt => {
  evt.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys
        .filter(key => key !== CACHE_NAME)
        .map(key => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', evt => {
  const url = new URL(evt.request.url);
  // 1) Si es tu API de registrar QR, intenta red runtime (y luego guardar offline si falla)
  if (url.pathname.startsWith('/api/registrar-qr/')) {
    return evt.respondWith(
      fetch(evt.request).catch(() => caches.match(evt.request))
    );
  }
  // 2) Para todo lo demás, usa cache-first
  evt.respondWith(
    caches.match(evt.request)
      .then(res => res || fetch(evt.request))
  );
});
