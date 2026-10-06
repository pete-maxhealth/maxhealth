// MaxedHealth Service Worker v2.2 - minimal, no caching, forces network-fresh fetch
// v2.2: tapping a notification now opens/focuses the app on the screen the reminder was about.
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

// Tapping a notification: bring the app forward and go to the screen it was sent for
// (notification.data.tab, e.g. 'supplements', 'chat', 'reports'). If the app is already
// open it is focused and told to switch; if not, it is opened with ?tab=<id> and the
// page switches itself once loaded.
self.addEventListener('notificationclick', e => {
  e.notification.close();
  const tab = (e.notification.data && e.notification.data.tab) || 'dash';
  e.waitUntil((async () => {
    const list = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
    const mine = list.find(c => c.url && c.url.startsWith(self.registration.scope));
    if (mine) {
      try { await mine.focus(); } catch (_) {}
      mine.postMessage({ action: 'switchTab', tab });
      return;
    }
    await self.clients.openWindow(self.registration.scope + '?tab=' + encodeURIComponent(tab));
  })());
});
