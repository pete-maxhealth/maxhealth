// MaxHealth Service Worker
// Network-first for HTML — always loads latest version
// Cache-first for static assets (icons, manifest)

const CACHE = 'maxhealth-v1.2';
const STATIC = [
  '/maxhealth/manifest.json',
  '/maxhealth/docs/icon-192.png',
  '/maxhealth/docs/icon-512.png',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(STATIC))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const url = e.request.url;

  // Never intercept external API calls
  if (url.includes('api.anthropic.com') ||
      url.includes('api.openai.com') ||
      url.includes('workers.dev') ||
      url.includes('fonts.googleapis.com') ||
      url.includes('cdnjs.cloudflare.com')) {
    return;
  }

  // Network-first for HTML — always get latest version
  if (url.includes('.html')) {
    e.respondWith(
      fetch(e.request)
        .then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE).then(cache => cache.put(e.request, clone));
          }
          return response;
        })
        .catch(() => caches.match(e.request)) // fallback to cache if offline
    );
    return;
  }

  // Cache-first for static assets
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(response => {
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE).then(cache => cache.put(e.request, clone));
        }
        return response;
      });
    })
  );
});
