// MaxedHealth Service Worker v2.1 - minimal, no caching, forces network-fresh fetch
self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.map(k => caches.delete(k))))
  );
  self.clients.claim();
});
self.addEventListener('fetch', e => {
  // { cache: 'no-store' } forces a genuine network round-trip every time,
  // bypassing the browser's own HTTP cache (which otherwise can satisfy
  // the request before this fetch handler ever runs, serving a stale
  // maxhealth.html even though this service worker itself caches nothing).
  e.respondWith(
    fetch(e.request, { cache: 'no-store' }).catch(() => caches.match(e.request))
  );
});
