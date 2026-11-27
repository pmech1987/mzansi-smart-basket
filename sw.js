const CACHE_NAME = 'mzansi-basket-personal-v3';
const APP_SHELL = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png'];
const FEED_KEY = new Request('./deals.json');

self.addEventListener('install', e => e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(APP_SHELL)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))).then(() => self.clients.claim())));

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  // Feed: network-first. Always stored under ONE stable key (the app adds ?t=timestamp, which used to fill the phone with copies of a multi-MB file).
  if (req.url.includes('deals.json')) {
    e.respondWith(fetch(req).then(res => { if (res.ok) { const c = res.clone(); caches.open(CACHE_NAME).then(x => x.put(FEED_KEY, c)).catch(err => console.warn('Full feed could not be saved to Cache Storage:', err)); } return res; })
      .catch(() => caches.match(FEED_KEY).then(r => r || new Response('{}', { status: 503 }))));
    return;
  }
  // App shell: stale-while-revalidate so new versions of the app reach users on the next open.
  e.respondWith(caches.match(req, { ignoreSearch: true }).then(hit => {
    const net = fetch(req).then(res => { if (res.ok) { const c = res.clone(); caches.open(CACHE_NAME).then(x => x.put(req, c)); } return res; }).catch(() => hit);
    return hit || net;
  }));
});
