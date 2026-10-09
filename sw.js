// MaxedHealth Service Worker v2.4
// v2.4: a connection that is ON but silent (airplane mode with a VPN still showing, a dead hotspot) used to make the
// page wait for the browser's own long timeout before the saved copy was used. If this page is already saved and the
// server has not even started to answer within NET_WAIT_MS, the saved copy is shown at once and the fetch carries on in
// the background to refresh it. The landing page (/maxhealth/ and index.html) is covered too, not just the app page,
// and so are the bundled /lib/ scripts, which block the page while loading.
// v2.2: tapping a notification opens/focuses the app on the screen the reminder was about.
// v2.3: works with NO connection at all. Android Chrome will not even try the local server
// (localhost:5757) when the phone has no network of any kind (airplane mode with WiFi and
// mobile data off) and falls back to something stale it stored months ago. A service worker
// answers before that happens, so it keeps the LAST GOOD copy of the app page and hands it
// back only when the server cannot be reached. Whenever the server answers, the page always
// comes fresh from it (network first, cache: 'no-store'); the saved copy is a fallback only.
const SHELL_CACHE = 'mh-shell-v1';
const NET_WAIT_MS = 3000; // time to first response only (headers); a slow download is never cut off

function shellKey(url) {
  const u = new URL(url);
  return u.origin + u.pathname; // ignore ?tab= and other query strings
}
function isAppPage(req) {
  if (req.mode !== 'navigate') return false;
  const p = new URL(req.url).pathname;
  return p === '/' || p === '/index.html' || p === '/maxhealth' || p === '/maxhealth/' || p === '/maxhealth/index.html' ||
         p === '/maxhealth.html' || p === '/maxhealth/maxhealth.html';
}

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    // Save a copy straight away so the very first offline open already works.
    try {
      const r = await fetch(self.registration.scope, { cache: 'no-store' });
      if (r && r.status === 200) (await caches.open(SHELL_CACHE)).put(shellKey(self.registration.scope), r.clone());
    } catch (_) { /* offline at install time: nothing to save yet, not an error */ }
    // Save the bundled scripts too, so the very first offline open does not wait on them.
    try {
      const c = await caches.open(SHELL_CACHE);
      for (const n of ['chart.umd.js', 'jspdf.umd.min.js', 'jspdf.plugin.autotable.min.js', 'jszip.min.js']) {
        try { const u = new URL('lib/' + n, self.registration.scope).href; const r = await fetch(u, { cache: 'no-store' }); if (r && r.status === 200) await c.put(u, r); } catch (_) {}
      }
    } catch (_) {}
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
      const c = await caches.open(SHELL_CACHE);
      const key = shellKey(e.request.url);
      const fallback = async () => (await c.match(key)) || (await c.match(shellKey(self.registration.scope))) || Response.error();
      // { cache: 'no-store' } forces a genuine network round-trip every time, bypassing the
      // browser's own HTTP cache, so a reachable server always wins over any saved copy.
      const net = fetch(e.request, { cache: 'no-store' }).then(r => {
        if (r && r.status === 200 && !r.redirected) { try { c.put(key, r.clone()); } catch (_) {} }
        return r;
      });
      const have = await c.match(key);
      if (!have) { try { return await net; } catch (err) { return fallback(); } }
      let timer;
      const silent = new Promise(res => { timer = setTimeout(() => res(null), NET_WAIT_MS); });
      try {
        const r = await Promise.race([net, silent]);
        clearTimeout(timer);
        if (r) return r;
        e.waitUntil(net.catch(() => {}));
        return have;
      } catch (err) { clearTimeout(timer); return fallback(); }
    })());
    return;
  }
  // The bundled libraries (Chart.js, jsPDF, JSZip) are plain <script> tags that block the page while they load, so a silent
  // connection would hold the whole app up on them. Serve the saved copy at once and refresh it in the background.
  if (new URL(e.request.url).pathname.includes('/lib/')) {
    e.respondWith((async () => {
      const c = await caches.open(SHELL_CACHE);
      const have = await c.match(e.request.url);
      const net = fetch(e.request, { cache: 'no-store' }).then(r => { if (r && r.status === 200) { try { c.put(e.request.url, r.clone()); } catch (_) {} } return r; });
      if (have) { e.waitUntil(net.catch(() => {})); return have; }
      return net;
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
