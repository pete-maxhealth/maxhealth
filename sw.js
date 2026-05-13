// MaxedHealth Service Worker v1.6
const CACHE = 'maxhealth-v1.6';

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(['./', './maxhealth.html'])).catch(()=>{})
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  if (!e.request.url.startsWith(self.location.origin)) return;
  if (e.request.url.includes('workers.dev')||e.request.url.includes('anthropic.com')||e.request.url.includes('openai.com')) return;
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(res => {
        if (!res || res.status !== 200 || res.type !== 'basic') return res;
        const clone = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, clone));
        return res;
      }).catch(() => {
        if (e.request.mode === 'navigate') return caches.match('./maxhealth.html');
      });
    })
  );
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  const tab = e.notification.data?.tab || '';
  e.waitUntil(
    clients.matchAll({type:'window',includeUncontrolled:true}).then(list => {
      for (const c of list) {
        if (c.url.includes('maxhealth') && 'focus' in c) {
          c.focus();
          if (tab) c.postMessage({action:'switchTab', tab});
          return;
        }
      }
      return clients.openWindow('./maxhealth.html'+(tab?`#${tab}`:''));
    })
  );
});
