const CACHE_NAME = 'slither-io-v2';
const urlsToCache = [
'/',
'/assets/css/styles.css?v=2',
'/assets/js/main.js',
'/logo.png',
'/favicon.ico'
];
self.addEventListener('install', (event) => {
self.skipWaiting();
event.waitUntil(
caches.open(CACHE_NAME)
.then((cache) => {
return cache.addAll(urlsToCache);
})
);
});
self.addEventListener('activate', (event) => {
event.waitUntil(
caches.keys().then((cacheNames) => {
return Promise.all(
cacheNames.map((cacheName) => {
if (cacheName !== CACHE_NAME && cacheName.startsWith('slither-io-')) {
console.log('Deleting old cache:', cacheName);
return caches.delete(cacheName);
}
})
);
}).then(() => {
return self.clients.claim();
})
);
});
self.addEventListener('fetch', (event) => {
event.respondWith(
caches.match(event.request)
.then((response) => {
if (event.request.url.includes('.css')) {
return fetch(event.request).catch(() => response);
}
return response || fetch(event.request);
})
);
});