// Service Worker for {{ site_name }}
// Progressive Web App caching strategy with automatic cache management

const CACHE_NAME = '{{ cache_name }}-v1';
const urlsToCache = [
  '/',
  '/templates/styles.css',
  '/assets/js/main.js',
  '/logo.png',
  '/favicon.ico'
];

// Install event - cache initial assets
self.addEventListener('install', (event) => {
  // Skip waiting to activate immediately
  self.skipWaiting();
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(urlsToCache);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          // Delete all old caches that don't match current version
          if (cacheName !== CACHE_NAME && cacheName.startsWith('{{ cache_name }}-')) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      // Take control of all pages immediately
      return self.clients.claim();
    })
  );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // For CSS files, always fetch fresh to ensure updates are reflected
        if (event.request.url.includes('.css')) {
          return fetch(event.request).catch(() => response);
        }
        // Return cached version or fetch from network
        return response || fetch(event.request);
      })
  );
});