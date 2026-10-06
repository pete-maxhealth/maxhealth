// MaxedHealth Service Worker v2.3
// v2.2: tapping a notification opens/focuses the app on the screen the reminder was about.
// v2.3: works with NO connection at all. Android Chrome will not even try the local server
// (localhost:5757) when the phone has no network of any kind (airplane mode with WiFi and
// mobile data off) and falls back to something stale it stored months ago. A service worker
// answers before that happens, so it keeps the LAST GOOD copy of the app page and hands it
// back only when the server cannot be reached. Whenever the server answers, the page always
// comes fresh from it (network first, cache: 'no-store'); the saved copy is a fallback only.
const SHELL_CACHE = 'mh-shell-v1';

function shellKey(url) {
  const u = new URL(url);
  return u.origin + u.pathname; // ignore ?tab= and other query strings
}
function isAppPage(req) {
  if (req.mode !== 'navigate') return false;
  const p = new URL(req.url).pathname;
  return p === '/' || p === '/maxhealth' || p === '/maxhealth.html' || p === '/maxhealth/maxhealth.html';
}

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    // Save a copy straight away so the very first offline open already works.
    try {
      const r = await fetch(self.registration.scope, { cache: 'no-store' });
      if (r && r.status === 200) (await caches.open(SHELL_CACHE)).put(shellKey(self.registration.scope), r.clone());
    } catch (_) { /* offline at install time: nothing to save yet, not an error */ }
    self.skipWaiting();
  })());
});
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== SHELL_CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  if (isAppPage(e.request)) {
    e.respondWith((async () => {
      try {
        // { cache: 'no-store' } forces a genuine network round-trip every time, bypassing the
        // browser's own HTTP cache, so a reachable server always wins over any saved copy.
        const r = await fetch(e.request, { cache: 'no-store' });
        if (r && r.status === 200 && !r.redirected) {
          try { (await caches.open(SHELL_CACHE)).put(shellKey(e.request.url), r.clone()); } catch (_) {}
        }
        return r;
      } catch (err) {
        const c = await caches.open(SHELL_CACHE);
        return (await c.match(shellKey(e.request.url))) ||
               (await c.match(shellKey(self.registration.scope))) ||
               Response.error();
      }
    })());
    return;
  }
  e.respondWith(fetch(e.request, { cache: 'no-store' }));
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
