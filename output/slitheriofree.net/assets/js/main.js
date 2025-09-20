(function() {
'use strict';
const CONFIG = {
SCROLL_THRESHOLD: 100,
ANIMATION_DURATION: 300,
DEBOUNCE_DELAY: 250,
LAZY_LOADING_MARGIN: '50px',
TOAST_DURATION: 3000
};
let isScrolling = false;
let scrollTimeout;
function debounce(func, wait, immediate) {
let timeout;
return function executedFunction() {
const context = this;
const args = arguments;
const later = function() {
timeout = null;
if (!immediate) func.apply(context, args);
};
const callNow = immediate && !timeout;
clearTimeout(timeout);
timeout = setTimeout(later, wait);
if (callNow) func.apply(context, args);
};
}
function throttle(func, limit) {
let inThrottle;
return function() {
const args = arguments;
const context = this;
if (!inThrottle) {
func.apply(context, args);
inThrottle = true;
setTimeout(() => inThrottle = false, limit);
}
}
}
function isElementInViewport(el) {
const rect = el.getBoundingClientRect();
return (
rect.top >= 0 &&
rect.left >= 0 &&
rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
rect.right <= (window.innerWidth || document.documentElement.clientWidth)
);
}
function smoothScrollTo(target, offset = 0) {
const element = typeof target === 'string' ? document.querySelector(target) : target;
if (!element) return;
const targetPosition = element.offsetTop - offset;
const startPosition = window.pageYOffset;
const distance = targetPosition - startPosition;
const duration = Math.min(Math.abs(distance) * 0.5, 1000);
let start = null;
function animation(currentTime) {
if (start === null) start = currentTime;
const timeElapsed = currentTime - start;
const run = ease(timeElapsed, startPosition, distance, duration);
window.scrollTo(0, run);
if (timeElapsed < duration) requestAnimationFrame(animation);
}
function ease(t, b, c, d) {
t /= d / 2;
if (t < 1) return c / 2 * t * t + b;
t--;
return -c / 2 * (t * (t - 2) - 1) + b;
}
requestAnimationFrame(animation);
}
function initializeNavigation() {
const navbar = document.querySelector('.navbar');
const navLinks = document.querySelectorAll('.nav-link');
const mobileToggle = document.querySelector('.navbar-toggler');
const navbarCollapse = document.querySelector('.navbar-collapse');
if (navbar) {
const handleScroll = throttle(() => {
const scrolled = window.scrollY > CONFIG.SCROLL_THRESHOLD;
navbar.classList.toggle('navbar-scrolled', scrolled);
if (scrolled) {
navbar.style.backgroundColor = 'rgba(255, 255, 255, 0.98)';
} else {
navbar.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
}
}, 16);
window.addEventListener('scroll', handleScroll);
}
if (mobileToggle && navbarCollapse) {
mobileToggle.addEventListener('click', (e) => {
e.preventDefault();
const isExpanded = mobileToggle.getAttribute('aria-expanded') === 'true';
mobileToggle.setAttribute('aria-expanded', !isExpanded);
navbarCollapse.classList.toggle('show');
navbarCollapse.classList.add('collapsing');
setTimeout(() => {
navbarCollapse.classList.remove('collapsing');
}, CONFIG.ANIMATION_DURATION);
});
document.addEventListener('click', (e) => {
if (!navbar.contains(e.target) && navbarCollapse.classList.contains('show')) {
mobileToggle.click();
}
});
}
navLinks.forEach(link => {
if (link.getAttribute('href').startsWith('#')) {
link.addEventListener('click', (e) => {
e.preventDefault();
const targetId = link.getAttribute('href').substring(1);
const targetElement = document.getElementById(targetId);
if (targetElement) {
smoothScrollTo(targetElement, 80);
}
});
}
});
updateActiveNavigation();
}
function updateActiveNavigation() {
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
if (sections.length === 0) return;
const handleScroll = throttle(() => {
let current = '';
sections.forEach(section => {
const sectionTop = section.offsetTop - 100;
const sectionHeight = section.offsetHeight;
if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
current = section.getAttribute('id');
}
});
navLinks.forEach(link => {
link.classList.remove('active');
if (link.getAttribute('href') === `#${current}`) {
link.classList.add('active');
}
});
}, 16);
window.addEventListener('scroll', handleScroll);
}
function enterFullscreen(element) {
const elem = element || document.querySelector('.frame-wrap');
if (!elem) return;
if (elem.requestFullscreen) {
elem.requestFullscreen();
} else if (elem.webkitRequestFullscreen) {
elem.webkitRequestFullscreen();
} else if (elem.mozRequestFullScreen) {
elem.mozRequestFullScreen();
} else if (elem.msRequestFullscreen) {
elem.msRequestFullscreen();
}
}
function exitFullscreen() {
const isFullscreen = !!(
document.fullscreenElement ||
document.webkitFullscreenElement ||
document.mozFullScreenElement ||
document.msFullscreenElement
);
if (!isFullscreen) {
return;
}
try {
if (document.exitFullscreen) {
document.exitFullscreen();
} else if (document.webkitExitFullscreen) {
document.webkitExitFullscreen();
} else if (document.mozCancelFullScreen) {
document.mozCancelFullScreen();
} else if (document.msExitFullscreen) {
document.msExitFullscreen();
}
} catch (error) {
}
}
function reloadGame() {
const gameFrame = document.getElementById('game-frame');
const playBtn = document.getElementById('play-btn');
if (gameFrame && playBtn) {
gameFrame.src = 'about:blank';
const overlay = document.getElementById('overlay');
if (overlay) {
overlay.style.display = 'grid';
overlay.innerHTML = `
<div class="play-button-container">
<button id="play-btn" class="btn primary-play-btn" aria-controls="game-frame">
<span class="play-icon">▶</span>
<span class="play-text">Play Now</span>
</button>
</div>
`;
initializeGameFeatures();
}
}
}
window.enterFullscreen = enterFullscreen;
window.exitFullscreen = exitFullscreen;
window.reloadGame = reloadGame;
function initializeGameFeatures() {
const gameFrame = document.getElementById('game-frame');
const playBtn = document.getElementById('play-btn');
const overlay = document.getElementById('overlay');
const exitBtn = document.getElementById('exit-full');
const frameWrap = document.querySelector('.frame-wrap');
if (!gameFrame) return;
if (playBtn && overlay) {
playBtn.addEventListener('click', function() {
let gameUrl = this.dataset.gameUrl || gameFrame.dataset.gameUrl;
if (!gameUrl || gameUrl === 'undefined' || gameUrl.includes('{{')) {
const currentPath = window.location.pathname;
if (currentPath.includes('/games/')) {
gameUrl = currentPath;
} else {
gameUrl = '/games/golf-hit.html';
}
}
if (gameUrl) {
gameFrame.src = gameUrl;
overlay.style.display = 'none';
if (typeof gtag !== 'undefined') {
gtag('event', 'game_started', {
'game_url': gameUrl
});
}
}
});
}
if (exitBtn) {
exitBtn.addEventListener('click', function() {
exitFullscreen();
document.body.classList.remove('playing');
});
}
gameFrame.onload = function() {
if (typeof gtag !== 'undefined') {
gtag('event', 'game_loaded', {
'game_url': gameFrame.src,
'load_time': Date.now()
});
}
};
gameFrame.onerror = function() {
if (overlay) {
overlay.innerHTML = `
<div class="play-button-container">
<div class="text-center text-white">
<i class="bi bi-exclamation-triangle fs-1 mb-3"></i>
<h5>Failed to Load Game</h5>
<p class="mb-3">There was an error loading the game. Please try again.</p>
<button class="btn btn-light" onclick="location.reload()">
<i class="bi bi-arrow-clockwise me-1"></i> Reload Page
</button>
</div>
</div>
`;
overlay.style.display = 'grid';
}
};
document.addEventListener('fullscreenchange', handleFullscreenChange);
document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
document.addEventListener('mozfullscreenchange', handleFullscreenChange);
document.addEventListener('MSFullscreenChange', handleFullscreenChange);
function handleFullscreenChange() {
const isFullscreen = !!(
document.fullscreenElement ||
document.webkitFullscreenElement ||
document.mozFullScreenElement ||
document.msFullscreenElement
);
if (frameWrap) {
frameWrap.classList.toggle('fullscreen', isFullscreen);
}
if (!isFullscreen) {
document.body.classList.remove('playing');
}
}
if ('PerformanceObserver' in window) {
try {
const observer = new PerformanceObserver((list) => {
for (const entry of list.getEntries()) {
if (entry.name.includes('game') || entry.name === gameFrame.src) {
}
}
});
observer.observe({ entryTypes: ['navigation', 'resource'] });
} catch (e) {
}
}
}
function initializeImageEnhancements() {
if ('loading' in HTMLImageElement.prototype) {
const lazyImages = document.querySelectorAll('img[loading="lazy"]');
lazyImages.forEach(img => {
if (!img.src && img.dataset.src) {
img.src = img.dataset.src;
}
});
} else {
implementLazyLoading();
}
enhanceImageLoading();
handleImageErrors();
}
function implementLazyLoading() {
if (!('IntersectionObserver' in window)) return;
const imageObserver = new IntersectionObserver((entries, observer) => {
entries.forEach(entry => {
if (entry.isIntersecting) {
const img = entry.target;
if (img.dataset.src) {
img.src = img.dataset.src;
img.removeAttribute('data-src');
}
if (img.dataset.srcset) {
img.srcset = img.dataset.srcset;
img.removeAttribute('data-srcset');
}
img.classList.remove('lazy');
observer.unobserve(img);
}
});
}, {
rootMargin: CONFIG.LAZY_LOADING_MARGIN,
threshold: 0.01
});
document.querySelectorAll('img[data-src]').forEach(img => {
imageObserver.observe(img);
});
}
function enhanceImageLoading() {
const images = document.querySelectorAll('img');
images.forEach(img => {
if (img.complete && img.naturalHeight !== 0) {
img.classList.add('loaded');
} else {
img.addEventListener('load', () => {
img.classList.add('loaded');
});
}
});
}
function handleImageErrors() {
document.addEventListener('error', (e) => {
if (e.target.tagName === 'IMG') {
const img = e.target;
if (img.src.includes('.webp')) {
const fallbackSrc = img.src.replace('.webp', '.jpg');
if (fallbackSrc !== img.src) {
img.src = fallbackSrc;
return;
}
}
img.classList.add('img-error');
const placeholder = document.createElement('div');
placeholder.className = 'img-placeholder d-flex align-items-center justify-content-center bg-light text-muted';
placeholder.style.cssText = `
width: ${img.width || 300}px;
height: ${img.height || 200}px;
border-radius: 0.5rem;
`;
placeholder.innerHTML = '<i class="bi bi-image fs-1"></i>';
img.parentNode.replaceChild(placeholder, img);
}
}, true);
}
function initializeSearchFeatures() {
const searchInputs = document.querySelectorAll('input[type="search"], input[placeholder*="search" i]');
searchInputs.forEach(input => {
const debouncedSearch = debounce((e) => {
performSearch(e.target.value, e.target);
}, CONFIG.DEBOUNCE_DELAY);
input.addEventListener('input', debouncedSearch);
input.addEventListener('keydown', (e) => {
if (e.key === 'Escape') {
input.value = '';
performSearch('', input);
}
});
});
}
function performSearch(query, inputElement) {
const searchableElements = document.querySelectorAll('[data-searchable], .game-card, .card');
const normalizedQuery = query.toLowerCase().trim();
let visibleCount = 0;
searchableElements.forEach(element => {
const searchText = (
element.textContent ||
element.querySelector('.card-title, .game-title, h1, h2, h3')?.textContent ||
''
).toLowerCase();
const isMatch = !normalizedQuery || searchText.includes(normalizedQuery);
if (isMatch) {
element.style.display = '';
element.classList.add('search-match');
visibleCount++;
} else {
element.style.display = 'none';
element.classList.remove('search-match');
}
});
updateSearchResults(visibleCount, query);
if (query && typeof gtag !== 'undefined') {
gtag('event', 'search', {
'search_term': query,
'results_count': visibleCount
});
}
}
function updateSearchResults(count, query) {
let indicator = document.querySelector('.search-results-indicator');
if (query && query.length > 0) {
if (!indicator) {
indicator = document.createElement('div');
indicator.className = 'search-results-indicator alert alert-info mt-2';
const searchContainer = document.querySelector('.search-container') ||
document.querySelector('input[type="search"]')?.parentNode;
if (searchContainer) {
searchContainer.appendChild(indicator);
}
}
if (indicator) {
indicator.innerHTML = count > 0
? `<i class="bi bi-search me-2"></i>Found ${count} result${count !== 1 ? 's' : ''} for "${query}"`
: `<i class="bi bi-exclamation-triangle me-2"></i>No results found for "${query}"`;
}
} else if (indicator) {
indicator.remove();
}
}
function initializeFormEnhancements() {
const forms = document.querySelectorAll('form');
forms.forEach(form => {
form.addEventListener('submit', (e) => {
const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
if (submitBtn) {
submitBtn.disabled = true;
submitBtn.innerHTML = '<i class="bi bi-arrow-clockwise spin me-2"></i>Sending...';
}
});
const inputs = form.querySelectorAll('input, textarea, select');
inputs.forEach(input => {
input.addEventListener('blur', () => validateField(input));
input.addEventListener('input', debounce(() => validateField(input), 300));
});
});
}
function validateField(field) {
const value = field.value.trim();
const type = field.type;
let isValid = true;
let message = '';
if (field.required && !value) {
isValid = false;
message = 'This field is required';
}
else if (type === 'email' && value) {
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(value)) {
isValid = false;
message = 'Please enter a valid email address';
}
}
field.classList.toggle('is-invalid', !isValid);
field.classList.toggle('is-valid', isValid && value);
let feedback = field.parentNode.querySelector('.invalid-feedback');
if (!isValid && message) {
if (!feedback) {
feedback = document.createElement('div');
feedback.className = 'invalid-feedback';
field.parentNode.appendChild(feedback);
}
feedback.textContent = message;
} else if (feedback) {
feedback.remove();
}
return isValid;
}
function initializePerformanceFeatures() {
if ('web-vitals' in window) {
monitorWebVitals();
}
optimizeResourceLoading();
monitorMemoryUsage();
trackUserInteractions();
}
function monitorWebVitals() {
if ('PerformanceObserver' in window) {
try {
new PerformanceObserver((entryList) => {
for (const entry of entryList.getEntries()) {
if (typeof gtag !== 'undefined') {
gtag('event', 'web_vitals', {
'metric_name': 'LCP',
'value': Math.round(entry.startTime),
'metric_id': 'lcp'
});
}
}
}).observe({ type: 'largest-contentful-paint', buffered: true });
} catch (e) {
}
try {
new PerformanceObserver((entryList) => {
let cumulativeScore = 0;
for (const entry of entryList.getEntries()) {
if (!entry.hadRecentInput) {
cumulativeScore += entry.value;
}
}
if (typeof gtag !== 'undefined') {
gtag('event', 'web_vitals', {
'metric_name': 'CLS',
'value': Math.round(cumulativeScore * 1000),
'metric_id': 'cls'
});
}
}).observe({ type: 'layout-shift', buffered: true });
} catch (e) {
}
}
}
function optimizeResourceLoading() {
const criticalImages = document.querySelectorAll('img[data-critical]');
criticalImages.forEach(img => {
const link = document.createElement('link');
link.rel = 'preload';
link.as = 'image';
link.href = img.src || img.dataset.src;
document.head.appendChild(link);
});
const internalLinks = document.querySelectorAll('a[href^="/"], a[href^="./"]');
const prefetchedUrls = new Set();
internalLinks.forEach(link => {
link.addEventListener('mouseenter', () => {
const url = link.href;
if (!prefetchedUrls.has(url)) {
const prefetchLink = document.createElement('link');
prefetchLink.rel = 'prefetch';
prefetchLink.href = url;
document.head.appendChild(prefetchLink);
prefetchedUrls.add(url);
}
});
});
}
function monitorMemoryUsage() {
if ('memory' in performance) {
setInterval(() => {
const memory = performance.memory;
if (memory.usedJSHeapSize > memory.jsHeapSizeLimit * 0.9) {
cleanupMemory();
}
}, 30000);
}
}
function cleanupMemory() {
if (window.gc) {
window.gc();
}
}
function trackUserInteractions() {
let maxScrollDepth = 0;
const trackScrollDepth = throttle(() => {
const scrollPercent = Math.round(
(window.scrollY + window.innerHeight) / document.documentElement.scrollHeight * 100
);
if (scrollPercent > maxScrollDepth) {
maxScrollDepth = scrollPercent;
if (typeof gtag !== 'undefined' && scrollPercent >= 75) {
gtag('event', 'scroll_depth', {
'page_location': window.location.pathname,
'scroll_percent': scrollPercent
});
}
}
}, 1000);
window.addEventListener('scroll', trackScrollDepth);
const startTime = Date.now();
window.addEventListener('beforeunload', () => {
const timeSpent = Math.round((Date.now() - startTime) / 1000);
if (typeof gtag !== 'undefined' && timeSpent > 10) {
gtag('event', 'time_on_page', {
'page_location': window.location.pathname,
'time_spent': timeSpent
});
}
});
}
function createToast(message, type = 'info', duration = CONFIG.TOAST_DURATION) {
const toastContainer = getOrCreateToastContainer();
const toast = document.createElement('div');
toast.className = `toast align-items-center text-bg-${type} border-0`;
toast.setAttribute('role', 'alert');
toast.setAttribute('aria-live', 'assertive');
toast.setAttribute('aria-atomic', 'true');
toast.innerHTML = `
<div class="d-flex">
<div class="toast-body">
${message}
</div>
<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
</div>
`;
toastContainer.appendChild(toast);
const bsToast = new bootstrap.Toast(toast, {
autohide: duration > 0,
delay: duration
});
bsToast.show();
toast.addEventListener('hidden.bs.toast', () => {
toast.remove();
});
return toast;
}
function getOrCreateToastContainer() {
let container = document.querySelector('.toast-container');
if (!container) {
container = document.createElement('div');
container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
container.style.zIndex = '9999';
document.body.appendChild(container);
}
return container;
}
function initializeAccessibilityFeatures() {
const skipLink = document.querySelector('.visually-hidden-focusable');
if (skipLink) {
skipLink.addEventListener('click', (e) => {
e.preventDefault();
const target = document.querySelector(skipLink.getAttribute('href'));
if (target) {
target.focus();
target.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
});
}
enhanceKeyboardNavigation();
createLiveRegions();
manageFocus();
}
function enhanceKeyboardNavigation() {
document.addEventListener('keydown', (e) => {
if (e.key === 'Escape') {
const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
openDropdowns.forEach(dropdown => {
const toggle = dropdown.previousElementSibling;
if (toggle) {
bootstrap.Dropdown.getInstance(toggle)?.hide();
}
});
const openModals = document.querySelectorAll('.modal.show');
openModals.forEach(modal => {
bootstrap.Modal.getInstance(modal)?.hide();
});
}
});
}
function createLiveRegions() {
if (!document.querySelector('#aria-live-polite')) {
const politeRegion = document.createElement('div');
politeRegion.id = 'aria-live-polite';
politeRegion.setAttribute('aria-live', 'polite');
politeRegion.setAttribute('aria-atomic', 'true');
politeRegion.className = 'visually-hidden';
document.body.appendChild(politeRegion);
}
if (!document.querySelector('#aria-live-assertive')) {
const assertiveRegion = document.createElement('div');
assertiveRegion.id = 'aria-live-assertive';
assertiveRegion.setAttribute('aria-live', 'assertive');
assertiveRegion.setAttribute('aria-atomic', 'true');
assertiveRegion.className = 'visually-hidden';
document.body.appendChild(assertiveRegion);
}
}
function announceToScreenReader(message, priority = 'polite') {
const liveRegion = document.querySelector(`#aria-live-${priority}`);
if (liveRegion) {
liveRegion.textContent = message;
setTimeout(() => {
liveRegion.textContent = '';
}, 1000);
}
}
function manageFocus() {
document.addEventListener('keydown', (e) => {
if (e.key === 'Tab') {
const modal = document.querySelector('.modal.show');
if (modal) {
const focusableElements = modal.querySelectorAll(
'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
);
if (focusableElements.length > 0) {
const firstElement = focusableElements[0];
const lastElement = focusableElements[focusableElements.length - 1];
if (e.shiftKey && document.activeElement === firstElement) {
e.preventDefault();
lastElement.focus();
} else if (!e.shiftKey && document.activeElement === lastElement) {
e.preventDefault();
firstElement.focus();
}
}
}
}
});
}
window.reloadGame = function() {
const gameFrame = document.getElementById('gameFrame');
const gameLoading = document.getElementById('gameLoading');
if (gameFrame) {
if (gameLoading) {
gameLoading.style.display = 'flex';
gameLoading.style.opacity = '1';
}
gameFrame.src = gameFrame.src;
if (typeof gtag !== 'undefined') {
gtag('event', 'game_reload', {
'game_url': gameFrame.src
});
}
}
};
window.toggleFullscreen = function() {
const gameContainer = document.querySelector('.game-container');
if (!gameContainer) return;
const isFullscreen = !!(
document.fullscreenElement ||
document.webkitFullscreenElement ||
document.mozFullScreenElement ||
document.msFullscreenElement
);
if (!isFullscreen) {
if (gameContainer.requestFullscreen) {
gameContainer.requestFullscreen();
} else if (gameContainer.webkitRequestFullscreen) {
gameContainer.webkitRequestFullscreen();
} else if (gameContainer.mozRequestFullScreen) {
gameContainer.mozRequestFullScreen();
} else if (gameContainer.msRequestFullscreen) {
gameContainer.msRequestFullscreen();
}
} else {
if (document.exitFullscreen) {
document.exitFullscreen();
} else if (document.webkitExitFullscreen) {
document.webkitExitFullscreen();
} else if (document.mozCancelFullScreen) {
document.mozCancelFullScreen();
} else if (document.msExitFullscreen) {
document.msExitFullscreen();
}
}
if (typeof gtag !== 'undefined') {
gtag('event', 'game_fullscreen', {
'action': isFullscreen ? 'exit' : 'enter'
});
}
};
window.openGameFullscreen = function() {
const gameEmbed = document.querySelector('meta[name="game-url"]');
const gameUrl = gameEmbed ? gameEmbed.content :
document.getElementById('gameFrame')?.src;
if (gameUrl) {
window.open(
gameUrl,
'_blank',
'fullscreen=yes,scrollbars=no,menubar=no,toolbar=no,location=no,status=no'
);
if (typeof gtag !== 'undefined') {
gtag('event', 'game_open_new_window', {
'game_url': gameUrl
});
}
}
};
window.copyToClipboard = function(text) {
if (navigator.clipboard) {
navigator.clipboard.writeText(text).then(() => {
createToast('Link copied to clipboard!', 'success');
announceToScreenReader('Link copied to clipboard');
}).catch(err => {
createToast('Failed to copy link', 'danger');
});
} else {
const textArea = document.createElement('textarea');
textArea.value = text;
textArea.style.position = 'fixed';
textArea.style.left = '-999999px';
textArea.style.top = '-999999px';
document.body.appendChild(textArea);
textArea.focus();
textArea.select();
try {
document.execCommand('copy');
createToast('Link copied to clipboard!', 'success');
announceToScreenReader('Link copied to clipboard');
} catch (err) {
createToast('Failed to copy link', 'danger');
}
document.body.removeChild(textArea);
}
};
window.showToast = function(message, type = 'info') {
createToast(message, type);
};
function initialize() {
try {
initializeNavigation();
initializeGameFeatures();
initializeImageEnhancements();
initializeSearchFeatures();
initializeFormEnhancements();
initializePerformanceFeatures();
initializeAccessibilityFeatures();
document.body.classList.add('js-loaded');
} catch (error) {
}
}
if (document.readyState === 'loading') {
document.addEventListener('DOMContentLoaded', initialize);
} else {
initialize();
}
document.addEventListener('visibilitychange', () => {
if (document.hidden) {
} else {
}
});
})();
if ('serviceWorker' in navigator) {
window.addEventListener('load', () => {
navigator.serviceWorker.register('/sw.js')
.then(registration => {
})
.catch(error => {
});
});
}
if (!document.querySelector('#dynamic-animations-css')) {
const animationCSS = document.createElement('style');
animationCSS.id = 'dynamic-animations-css';
animationCSS.textContent = `
@keyframes spin {
from { transform: rotate(0deg); }
to { transform: rotate(360deg); }
}
.spin {
animation: spin 1s linear infinite;
}
.js-loaded img {
opacity: 0;
transition: opacity 0.3s ease-in-out;
}
.js-loaded img.loaded {
opacity: 1;
}
.fullscreen-active {
position: fixed;
top: 0;
left: 0;
width: 100vw;
height: 100vh;
z-index: 9999;
background: #000;
}
.fullscreen-active .game-iframe {
border-radius: 0;
}
.search-match {
animation: highlight 0.5s ease-in-out;
}
@keyframes highlight {
0% { background-color: transparent; }
50% { background-color: rgba(255, 193, 7, 0.2); }
100% { background-color: transparent; }
}
.img-placeholder {
background: linear-gradient(45deg, #f8f9fa 25%, transparent 25%),
linear-gradient(-45deg, #f8f9fa 25%, transparent 25%),
linear-gradient(45deg, transparent 75%, #f8f9fa 75%),
linear-gradient(-45deg, transparent 75%, #f8f9fa 75%);
background-size: 20px 20px;
background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
}
`;
document.head.appendChild(animationCSS);
}