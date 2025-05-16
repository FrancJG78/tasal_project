// service-worker.js

const CACHE_NAME = 'tasal-cache-v1';
const urlsToCache = [
  '/',
  '/static/manifest.json',
  '/static/js/offline.js',
  // Agrega aquí otras rutas esenciales que quieras cachear, como CSS, imágenes, etc.
];

// Instalar el Service Worker y cachear archivos esenciales
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Abriendo cache y agregando archivos esenciales');
        return cache.addAll(urlsToCache);
      })
  );
});

// Recuperar recursos desde la caché cuando sea posible
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Si se encuentra en la caché, se devuelve.
        if (response) {
          return response;
        }
        // Si no está en la caché, se realiza la solicitud a la red.
        return fetch(event.request).then(
          networkResponse => {
            // Opcional: guardar la respuesta en caché para futuras solicitudes.
            if (!networkResponse || networkResponse.status !== 200) {
              return networkResponse;
            }
            let responseClone = networkResponse.clone();
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseClone);
              });
            return networkResponse;
          }
        );
      })
  );
});

// Actualizar el cache cuando se instala una nueva versión del Service Worker
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (!cacheWhitelist.includes(cacheName)) {
            console.log('Borrando cache antiguo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});


// Opcional: Lógica de background sync para enviar registros pendientes.
