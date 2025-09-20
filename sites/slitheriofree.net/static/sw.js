// Service Worker for Slither Io
// Enhanced caching strategy with cache busting

const CACHE_NAME = 'slither-io-v2'; // Updated version to force cache clear
const urlsToCache = [
  '/',
  '/assets/css/styles.css?v=2', // Added version parameter
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
          if (cacheName !== CACHE_NAME && cacheName.startsWith('slither-io-')) {
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