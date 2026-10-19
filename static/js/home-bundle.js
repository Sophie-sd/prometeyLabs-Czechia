/**
 * HOME-BUNDLE.JS - Оптимізований bundle для головної сторінки
 * Включає: Utils, MobileCore, VideoSystem, PrometeyApp, Home
 * Версія: 1.0 - Performance Optimized
 *
 * УВАГА: цей файл — копія окремих модулів (static/js/core/utils.js,
 * static/js/mobile-core.js, static/js/video-system.js, static/js/base.js,
 * static/js/home.js). Будь-які правки в оригіналах мають бути продубльовані тут,
 * інакше фіча працюватиме всюди, крім головної сторінки.
 */

// ========================================
// UTILS.JS - Утилітарні функції
// ========================================

const Utils = {
    debounce(func, wait = 100) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    throttle(func, limit = 100) {
        let inThrottle;
        return function (...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    getCSRFToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            const token = metaTag.getAttribute('content');
            if (token) return token;
        }

        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        if (input?.value) return input.value;

        const match = document.cookie.match(/csrftoken=([^;]+)/);
        if (match) return match[1];

        return '';
    },

    storage: {
        set(key, value) {
            try {
                sessionStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (error) {
                console.error('Storage set error:', error);
                return false;
            }
        },

        get(key, defaultValue = null) {
            try {
                const item = sessionStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (error) {
                console.error('Storage get error:', error);
                return defaultValue;
            }
        },

        remove(key) {
            try {
                sessionStorage.removeItem(key);
                return true;
            } catch (error) {
                console.error('Storage remove error:', error);
                return false;
            }
        },

        clear() {
            try {
                sessionStorage.clear();
                return true;
            } catch (error) {
                console.error('Storage clear error:', error);
                return false;
            }
        }
    },

    element: {
        cache: new Map(),

        get(selector, bustCache = false) {
            if (bustCache || !this.cache.has(selector)) {
                const element = document.querySelector(selector);
                this.cache.set(selector, element);
            }
            return this.cache.get(selector);
        },

        getAll(selector) {
            return Array.from(document.querySelectorAll(selector));
        },

        create(tag, options = {}) {
            const element = document.createElement(tag);

            if (options.className) {
                element.className = options.className;
            }

            if (options.id) {
                element.id = options.id;
            }

            if (options.attributes) {
                Object.entries(options.attributes).forEach(([key, value]) => {
                    element.setAttribute(key, value);
                });
            }

            if (options.innerHTML) {
                element.innerHTML = options.innerHTML;
            }

            if (options.textContent) {
                element.textContent = options.textContent;
            }

            return element;
        }
    },

    scrollTo(selector, offset = 80) {
        const element = typeof selector === 'string'
            ? document.querySelector(selector)
            : selector;

        if (!element) return;

        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - offset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    },

    events: {
        listeners: new Map(),

        on(eventName, callback) {
            if (!this.listeners.has(eventName)) {
                this.listeners.set(eventName, []);
            }
            this.listeners.get(eventName).push(callback);
        },

        off(eventName, callback) {
            if (!this.listeners.has(eventName)) return;

            const callbacks = this.listeners.get(eventName);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        },

        emit(eventName, data = null) {
            const event = new CustomEvent(eventName, { detail: data });
            document.dispatchEvent(event);

            if (this.listeners.has(eventName)) {
                this.listeners.get(eventName).forEach(callback => {
                    callback(data);
                });
            }
        }
    },

    animation: {
        raf(callback) {
            return window.requestAnimationFrame
                ? window.requestAnimationFrame(callback)
                : setTimeout(callback, 16);
        },

        caf(id) {
            return window.cancelAnimationFrame
                ? window.cancelAnimationFrame(id)
                : clearTimeout(id);
        }
    },

    device: {
        isMobile() {
            return window.innerWidth <= 767 ||
                'ontouchstart' in window ||
                navigator.maxTouchPoints > 0;
        },

        isTablet() {
            const width = window.innerWidth;
            return width > 767 && width <= 1024;
        },

        isDesktop() {
            return window.innerWidth > 1024;
        },

        isTouch() {
            return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        }
    }
};

window.PrometeyUtils = Utils;

// ========================================
// MOBILE-CORE.JS - Мобільні оптимізації
// ========================================

class MobileCore {
    constructor() {
        this.device = this.detectDevice();
        this.capabilities = this.detectCapabilities();
        this.initialized = false;
        this.viewportUpdateCallbacks = [];
        this._touchBound = false;

        this.init();
    }

    detectDevice() {
        const ua = navigator.userAgent.toLowerCase();
        const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

        return {
            iOS: /ipad|iphone|ipod/.test(ua) && !window.MSStream,
            android: /android/.test(ua),
            safari: /^((?!chrome|android).)*safari/i.test(navigator.userAgent),

            iOSVersion: this.getIOSVersion(ua),
            androidVersion: this.getAndroidVersion(ua),

            isTouch: isTouchDevice,
            isMobile: window.innerWidth <= 767 || isTouchDevice,
            isTablet: window.innerWidth > 767 && window.innerWidth <= 1024 && isTouchDevice,
            hasNotch: CSS.supports && (CSS.supports('padding-top: env(safe-area-inset-top)') || CSS.supports('padding-top: constant(safe-area-inset-top)')),

            isLowEnd: this.detectLowEndDevice(),
            prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches
        };
    }

    detectCapabilities() {
        return {
            supportsIntersectionObserver: 'IntersectionObserver' in window,
            supportsResizeObserver: 'ResizeObserver' in window,
            supportsCustomProperties: CSS.supports && CSS.supports('color', 'var(--test)'),

            supportsServiceWorker: 'serviceWorker' in navigator,
            supportsWebShare: 'share' in navigator,
            supportsVibration: 'vibrate' in navigator,

            supportsDisplayCutout: CSS.supports && CSS.supports('padding-top: env(safe-area-inset-top)'),
            supportsDynamicViewport: CSS.supports && CSS.supports('height: 100dvh')
        };
    }

    init() {
        if (this.initialized) return;

        this.setupPerformanceOptimizations();
        this.applyPlatformClasses();

        this.initialized = true;
        this.dispatchInitEvent();

        const runHeavy = () => {
            this.setupViewportSystem();
            this.setupTouchOptimizations();
            if (this.device.iOS) {
                this.optimizeIOSSafariPerformance();
            }
        };

        if (typeof requestAnimationFrame === 'function') {
            requestAnimationFrame(() => {
                requestAnimationFrame(runHeavy);
            });
        } else {
            setTimeout(runHeavy, 0);
        }
    }

    applyPlatformClasses() {
        if (this.device.iOS) {
            document.documentElement.classList.add('ios', 'safari');
            if (this.device.iOSVersion >= 17) {
                document.documentElement.classList.add('ios-17');
            }
        }
        if (this.device.android) {
            document.documentElement.classList.add('android');
        }
    }

    setupViewportSystem() {
        const setVH = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };

        setVH();

        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                setVH();
                this.notifyViewportChange();
            }, 250);
        });

        this.notifyViewportChange();
    }


    setupIOSSafariOptimizations() {
        this.applyPlatformClasses();
        this.optimizeIOSSafariPerformance();
    }


    setupTouchOptimizations() {
        if (!this.device.isTouch) return;
        this.setupTouchFeedback();
    }

    setupTouchFeedback() {
        if (this._touchBound) return;
        this._touchBound = true;

        const selector = 'button, [role="button"], .btn, .nav-link, .card-link, [data-modal]';
        let activeEl = null;
        let touchTimeout;

        const clearActive = () => {
            if (activeEl) {
                activeEl.classList.remove('touch-active');
                activeEl = null;
            }
            clearTimeout(touchTimeout);
        };

        document.addEventListener('touchstart', (e) => {
            const el = e.target.closest && e.target.closest(selector);
            if (!el) return;
            clearActive();
            activeEl = el;
            el.classList.add('touch-active');
            if (this.capabilities.supportsVibration && this.device.iOS) {
                navigator.vibrate(10);
            }
        }, { passive: true });

        document.addEventListener('touchend', () => {
            if (!activeEl) return;
            const el = activeEl;
            touchTimeout = setTimeout(() => {
                el.classList.remove('touch-active');
                if (activeEl === el) activeEl = null;
            }, 100);
        }, { passive: true });

        document.addEventListener('touchcancel', clearActive, { passive: true });
    }

    setupPerformanceOptimizations() {
        if (this.device.isLowEnd || this.device.prefersReducedMotion) {
            document.documentElement.classList.add('reduce-motion');
        }
    }

    getIOSVersion(ua) {
        const match = ua.match(/os (\d+)_(\d+)_?(\d+)?/);
        return match ? parseInt(match[1], 10) : 0;
    }

    getAndroidVersion(ua) {
        const match = ua.match(/android\s([\d\.]+)/);
        return match ? parseFloat(match[1]) : 0;
    }

    hasDisplayCutout() {
        return this.capabilities.supportsDisplayCutout &&
            (CSS.supports('padding-top: env(safe-area-inset-top)') ||
                CSS.supports('padding-top: constant(safe-area-inset-top)'));
    }

    detectLowEndDevice() {
        const memory = navigator.deviceMemory || 4;
        const cores = navigator.hardwareConcurrency || 4;
        const connection = navigator.connection;

        return memory < 3 || cores < 4 ||
            (connection && (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g'));
    }

    isRootScrollableElement(element) {
        return element === document.documentElement ||
            element === document.body ||
            element.closest('[data-prevent-overscroll]');
    }

    dispatchInitEvent() {
        const event = new CustomEvent('mobilecore:initialized', {
            detail: {
                device: this.device,
                capabilities: this.capabilities
            }
        });
        document.dispatchEvent(event);
    }

    dispatchViewportChangeEvent() {
        const event = new CustomEvent('mobilecore:viewportchange', {
            detail: {
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                device: this.device
            }
        });
        document.dispatchEvent(event);
    }

    getDevice() {
        return this.device;
    }

    getCapabilities() {
        return this.capabilities;
    }

    isInitialized() {
        return this.initialized;
    }

    onViewportChange(callback) {
        this.viewportUpdateCallbacks.push(callback);
    }

    notifyViewportChange() {
        this.viewportUpdateCallbacks.forEach(callback => {
            try {
                callback({
                    width: window.innerWidth,
                    height: window.innerHeight,
                    device: this.device
                });
            } catch (error) {
                console.error('Viewport callback error:', error);
            }
        });
    }

    /** Anti-zoom via CSS font-size: 16px (base-bundle). No-op for API compat. */
    preventAccidentalZoom() {}

    setupAndroidOptimizations() {
        document.documentElement.classList.add('android');
    }

    /** overscroll via html.ios in CSS. No-op for API compat. */
    fixIOSSafariScrollBounce() {}

    optimizeIOSSafariPerformance() {
        const videos = document.querySelectorAll('video');
        videos.forEach(video => {
            video.setAttribute('playsinline', '');
            video.setAttribute('webkit-playsinline', '');
        });
    }

    preventIOSZoomOnInputs() {
        this.preventAccidentalZoom();
    }

    handleOrientationChange() {
        // Placeholder для майбутньої логіки
    }
}

window.MobileCore = new MobileCore();

// ========================================
// VIDEO-SYSTEM.JS - Відео система
// ========================================

class VideoSystem {
    constructor() {
        this.videos = new Map();
        this.autoplaySupported = null;
        this.loadingStrategy = null;
        this.observers = {
            intersection: null,
            visibility: null
        };

        this.config = {
            lazyLoadMargin: '200px',
            lazyLoadThreshold: 0,
            loadTimeout: 10000
        };

        this.sharedKeepaliveTimer = null;
    }

    async init() {
        this.loadingStrategy = this.determineLoadingStrategy();
        this.setupObservers();
        this.autoplaySupported = true;
        await this.processPageVideos();
        this.setupSharedVideoGroups();
        this.setupEventListeners();
        this.testAutoplaySupport().then((ok) => {
            this.autoplaySupported = ok;
        });
    }

    getSharedVideoLeader(element) {
        const key = element.getAttribute('data-shared-video');
        if (!key) {
            return null;
        }

        const siblings = document.querySelectorAll(`video[data-shared-video="${key}"]`);
        for (const sibling of siblings) {
            const siblingData = this.videos.get(sibling);
            if (siblingData?.loaded && sibling.readyState >= 2) {
                return sibling;
            }
        }

        return null;
    }

    setupSharedVideoGroups() {
        const sharedVideos = document.querySelectorAll('video[data-shared-video]');
        if (!sharedVideos.length) {
            return;
        }

        const groups = new Map();
        sharedVideos.forEach((video) => {
            if (!this.isVideoForCurrentViewport(video)) {
                return;
            }
            const key = video.getAttribute('data-shared-video');
            if (!key) {
                return;
            }
            if (!groups.has(key)) {
                groups.set(key, []);
            }
            groups.get(key).push(video);
        });

        const keepGroupPlaying = (videos) => {
            if (document.hidden) {
                return;
            }

            videos.forEach((video) => {
                if (video.paused && video.readyState >= 2) {
                    video.play().catch(() => { });
                }
            });
        };

        groups.forEach((videos) => {
            if (videos.length < 2) {
                return;
            }

            const leader = videos[0];

            leader.addEventListener('timeupdate', () => {
                const time = leader.currentTime;
                videos.forEach((video) => {
                    if (video === leader) {
                        return;
                    }
                    if (Math.abs(video.currentTime - time) > 0.35) {
                        try {
                            video.currentTime = time;
                        } catch (error) {
                            /* ignore seek errors on iOS */
                        }
                    }
                });
            });

            videos.forEach((video) => {
                video.addEventListener('pause', () => {
                    if (!document.hidden) {
                        window.setTimeout(() => keepGroupPlaying(videos), 50);
                    }
                });
                video.addEventListener('stalled', () => keepGroupPlaying(videos));
                video.addEventListener('waiting', () => keepGroupPlaying(videos));
            });

            keepGroupPlaying(videos);
        });

        if (this.sharedKeepaliveTimer) {
            window.clearInterval(this.sharedKeepaliveTimer);
        }

        this.sharedKeepaliveTimer = window.setInterval(() => {
            groups.forEach((videos) => keepGroupPlaying(videos));
        }, 2500);
    }

    async testAutoplaySupport() {
        const video = document.createElement('video');
        video.muted = true;
        video.playsInline = true;
        video.hidden = true;
        video.width = 1;
        video.height = 1;
        video.setAttribute('aria-hidden', 'true');

        try {
            const testVideoSrc = 'data:video/mp4;base64,AAAAIGZ0eXBpc29tAAACAGlzb21pc28yYXZjMW1wNDEAAAAIZnJlZQAAAu1tZGF0';
            video.src = testVideoSrc;
            document.body.appendChild(video);

            const playPromise = video.play();

            if (playPromise instanceof Promise) {
                await playPromise;
                return true;
            }

            return false;
        } catch (error) {
            return false;
        } finally {
            video.remove();
        }
    }

    determineLoadingStrategy() {
        const device = window.MobileCore?.getDevice() || {};
        const connection = navigator.connection;

        if (device.isLowEnd || connection?.effectiveType === 'slow-2g') {
            return 'minimal';
        } else if (device.isMobile || connection?.effectiveType === '2g') {
            return 'lazy';
        } else if (connection?.effectiveType === '3g') {
            return 'progressive';
        }
        return 'eager';
    }

    setupObservers() {
        if (!('IntersectionObserver' in window)) return;

        this.observers.intersection = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadVideoForElement(entry.target);
                }
            });
        }, {
            rootMargin: this.config.lazyLoadMargin,
            threshold: this.config.lazyLoadThreshold
        });
    }

    isMobileViewport() {
        return window.matchMedia('(max-width: 767px)').matches;
    }

    isVideoForCurrentViewport(video) {
        const isMobile = this.isMobileViewport();
        if (video.classList.contains('desktop-video') && isMobile) {
            return false;
        }
        if (video.classList.contains('mobile-video') && !isMobile) {
            return false;
        }
        if (!isMobile && video.closest('#svc-piano, .home-cta-section')) {
            return false;
        }
        return true;
    }

    lazyObserveRoot(video) {
        return video.closest('section, .hero-section, .cta-section, .project-section')
            || video.parentElement
            || video;
    }

    applyDataSrc(element) {
        const source = element.querySelector('source');
        const url = element.getAttribute('data-src')
            || (source && (source.getAttribute('data-src') || source.getAttribute('src')));
        if (!url) {
            return Boolean(element.currentSrc || element.src || (source && source.getAttribute('src')));
        }
        if (source && source.getAttribute('src') !== url) {
            source.src = url;
        }
        if (source) {
            source.removeAttribute('data-src');
        }
        element.removeAttribute('data-src');
        return true;
    }

    async processPageVideos() {
        const standardVideos = document.querySelectorAll(
            '.video-background:not(.lazy-video), .hero-video:not(.lazy-video)'
        );

        for (const video of standardVideos) {
            if (!this.isVideoForCurrentViewport(video)) {
                continue;
            }
            await this.processVideo(video, 'standard');
        }

        const lazyVideos = document.querySelectorAll('.lazy-video');

        lazyVideos.forEach((video) => {
            if (!this.isVideoForCurrentViewport(video)) {
                return;
            }

            const videoData = {
                element: video,
                mode: 'lazy',
                loaded: false,
                playing: false,
                container: video.closest('[data-video-container]') || video.parentElement
            };

            this.videos.set(video, videoData);
            this.optimizeVideoAttributes(video);

            if (this.observers.intersection) {
                this.observers.intersection.observe(this.lazyObserveRoot(video));
            } else {
                this.loadVideo(videoData);
            }
        });
    }

    async processVideo(videoElement, mode = 'standard') {
        if (!videoElement) return;

        const videoData = {
            element: videoElement,
            mode,
            loaded: false,
            playing: false,
            container: videoElement.closest('[data-video-container]') || videoElement.parentElement
        };

        this.videos.set(videoElement, videoData);
        this.optimizeVideoAttributes(videoElement);

        if (mode === 'lazy' || videoElement.classList.contains('lazy-video')) {
            await this.setupLazyVideo(videoData);
        } else {
            await this.loadVideo(videoData);
        }
    }

    async setupLazyVideo(videoData) {
        // Observer вже налаштований
    }

    async loadVideoForElement(element) {
        let video = null;

        if (element.tagName === 'VIDEO') {
            video = element;
        } else {
            const isMobile = this.isMobileViewport();
            const selector = isMobile
                ? 'video.lazy-video.mobile-video, video.lazy-video:not(.desktop-video)'
                : 'video.lazy-video.desktop-video, video.lazy-video:not(.mobile-video)';
            video = element.querySelector(selector);

            if (!video) {
                video = element.querySelector('video.lazy-video');
            }
        }

        if (video && !this.isVideoForCurrentViewport(video)) {
            return;
        }

        if (!video) {
            return;
        }

        const videoData = this.videos.get(video);
        if (!videoData) {
            await this.processVideo(video, 'lazy');
            return;
        }

        if (videoData.loaded) {
            return;
        }

        await this.loadVideo(videoData);
    }

    isHeroBackgroundVideo(element) {
        return element.classList.contains('video-background') && !element.classList.contains('lazy-video');
    }

    async loadVideo(videoData) {
        const { element, container } = videoData;
        if (!this.isVideoForCurrentViewport(element)) {
            return;
        }
        const isHeroBackground = this.isHeroBackgroundVideo(element);

        try {
            this.applyDataSrc(element);
            element.classList.remove('lazy-video');

            const sharedLeader = this.getSharedVideoLeader(element);

            if (sharedLeader && sharedLeader !== element) {
                if (element.readyState < 2) {
                    element.load();
                    await this.waitForVideoReady(element);
                }

                try {
                    element.currentTime = sharedLeader.currentTime;
                } catch (error) {
                    /* ignore seek errors */
                }

                videoData.loaded = true;
                await this.attemptAutoplay(videoData);
                this.emit('video:loaded', { element, container });
                return;
            }

            const alreadyReady = element.readyState >= 2;
            const alreadyFetching = element.networkState === 2 || element.readyState >= 1;

            if (!alreadyReady && !alreadyFetching) {
                element.load();
            }

            await this.waitForVideoReady(element);

            videoData.loaded = true;

            if (isHeroBackground || this.autoplaySupported) {
                await this.attemptAutoplay(videoData);
            }

            this.emit('video:loaded', { element, container });

        } catch (error) {
            this.handleVideoError(videoData, error);
        }
    }

    optimizeVideoAttributes(video) {
        video.muted = true;
        video.playsInline = true;
        video.loop = true;
        video.controls = false;

        video.setAttribute('playsinline', '');
        video.setAttribute('webkit-playsinline', '');

        if (video.classList.contains('lazy-video')) {
            video.preload = 'none';
            return;
        }

        video.preload = this.loadingStrategy === 'minimal' ? 'none' : 'metadata';
    }

    async waitForVideoReady(video) {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Video loading timeout'));
            }, this.config.loadTimeout);

            const onReady = () => {
                clearTimeout(timeout);
                cleanup();
                resolve();
            };

            const onError = (error) => {
                clearTimeout(timeout);
                cleanup();
                reject(error);
            };

            const cleanup = () => {
                video.removeEventListener('loadeddata', onReady);
                video.removeEventListener('error', onError);
            };

            if (video.readyState >= 2) {
                resolve();
            } else {
                video.addEventListener('loadeddata', onReady);
                video.addEventListener('error', onError);
            }
        });
    }

    async attemptAutoplay(videoData) {
        const { element } = videoData;

        try {
            await element.play();
            videoData.playing = true;
            this.emit('video:playing', { element });
        } catch (error) {
            this.emit('video:autoplay-failed', { element });
        }
    }

    handleVideoError(videoData, error) {
        const { element, container } = videoData;
        element.style.display = 'none';
        this.emit('video:error', { element, container, error });
    }

    setupEventListeners() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAll();
            } else {
                this.resumeAll();
            }
        });

        if (navigator.connection) {
            navigator.connection.addEventListener('change', () => {
                this.handleConnectionChange();
            });
        }
    }

    handleConnectionChange() {
        const connection = navigator.connection;
        if (connection?.effectiveType === 'slow-2g' || connection?.effectiveType === '2g') {
            this.pauseAll();
        }
    }

    pauseAll() {
        this.videos.forEach((videoData) => {
            const { element } = videoData;
            if (!element.paused) {
                element.pause();
            }
            videoData.playing = false;
        });
    }

    resumeAll() {
        this.videos.forEach((videoData) => {
            const { element } = videoData;
            if (videoData.loaded && element.paused) {
                element.play().then(() => {
                    videoData.playing = true;
                }).catch(() => { });
            }
        });
    }

    pauseVideo(videoElement) {
        const videoData = this.videos.get(videoElement);
        if (videoData && !videoElement.paused) {
            videoElement.pause();
            videoData.playing = false;
        }
    }

    playVideo(videoElement) {
        const videoData = this.videos.get(videoElement);
        if (videoData && videoElement.paused && videoData.loaded) {
            videoElement.play().catch(() => { });
            videoData.playing = true;
        }
    }

    async addVideo(videoElement, mode = 'standard') {
        await this.processVideo(videoElement, mode);
    }

    removeVideo(videoElement) {
        this.videos.delete(videoElement);
    }

    getVideoData(videoElement) {
        return this.videos.get(videoElement);
    }

    isAutoplaySupported() {
        return this.autoplaySupported;
    }

    observeLazy(element) {
        if (this.observers.intersection) {
            this.observers.intersection.observe(element);
        }
    }

    unobserveLazy(element) {
        if (this.observers.intersection) {
            this.observers.intersection.unobserve(element);
        }
    }

    emit(eventName, data) {
        const event = new CustomEvent(`videosystem:${eventName}`, { detail: data });
        document.dispatchEvent(event);
    }

    on(eventName, callback) {
        document.addEventListener(`videosystem:${eventName}`, callback);
    }

    off(eventName, callback) {
        document.removeEventListener(`videosystem:${eventName}`, callback);
    }
}

window.VideoSystem = new VideoSystem();

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.VideoSystem.init();
    });
} else {
    window.VideoSystem.init();
}

// ========================================
// BASE.JS - Базова логіка PrometeyApp
// ========================================

class PrometeyApp {
    /**
     * Fallback text when window.I18N is missing: cs (default) / en.
     */
    fallbackText(cs, en) {
        const lang = (document.documentElement.getAttribute('lang') || 'cs').toLowerCase();
        return lang.indexOf('en') === 0 ? en : cs;
    }

    constructor() {
        this.config = {
            scrollThreshold: 50,
            menuTransitionDuration: 400,
            notificationDuration: 5000
        };

        this.state = {
            menuOpen: false,
            activeModal: null
        };

        this.elements = {};
        this.phoneMasks = new Map(); // Зберігаємо інстанси PhoneMask

        this.init();
    }

    init() {
        if (window.MobileCore?.isInitialized()) {
            this.initWithMobileCore();
        } else {
            document.addEventListener('mobilecore:initialized', () => {
                this.initWithMobileCore();
            });
        }
    }

    initWithMobileCore() {
        this.cacheElements();
        this.setupNavigation();
        this.setupMobileMenu();
        this.setupModals();
        this.setupBackGesture();
        this.setupPhoneMasks();
        this.setupForms();
        this.setupLanguageSwitcher();
        this.setupAccessibility();
        this.setupFooterAccordion();
        this.setupContactWidget();
        this.setupScrollStateDetection();

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.onDOMReady());
        } else {
            this.onDOMReady();
        }
    }

    cacheElements() {
        this.elements = {
            nav: document.querySelector('.main-navigation'),
            burgerBtn: document.querySelector('.burger-menu'),
            mobileMenu: document.querySelector('.mobile-menu'),
            mobileMenuClose: document.querySelector('.mobile-menu-close'),
            mobileNavLinks: document.querySelectorAll('.mobile-nav-link'),
            langDropdown: document.querySelector('.lang-dropdown'),
            langDropdownBtn: document.querySelector('.lang-dropdown-btn'),
            langSwitchers: document.querySelectorAll('.lang-switcher-link')
        };
    }

    onDOMReady() {
        // Ініціалізуємо PhoneMask для полів, які могли з'явитися після початкової ініціалізації
        this.initPhoneMasksForElement(document);
    }

    setupNavigation() {
        if (!this.elements.nav) return;

        let ticking = false;
        let lastScrollTop = 0;
        let isScrolled = false;

        const handleScroll = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                    const shouldBeScrolled = scrollTop > this.config.scrollThreshold;

                    if (shouldBeScrolled !== isScrolled) {
                        this.elements.nav.classList.toggle('scrolled', shouldBeScrolled);
                        isScrolled = shouldBeScrolled;
                    }

                    lastScrollTop = scrollTop;
                    ticking = false;
                });
                ticking = true;
            }
        };

        window.addEventListener('scroll', handleScroll, { passive: true });

        this.setupSmoothScroll();
    }

    setupSmoothScroll() {
        const links = document.querySelectorAll('a[href^="#"]');

        links.forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                if (href === '#') return;

                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    const offsetTop = target.offsetTop - 80;
                    window.scrollTo({ top: offsetTop, behavior: 'smooth' });
                }
            }, { passive: false });
        });
    }

    setupScrollStateDetection() {
        let scrollTimeout;
        let isScrolling = false;
        
        const handleScroll = () => {
            if (!isScrolling) {
                document.body.classList.add('is-scrolling');
                isScrolling = true;
            }
            
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                document.body.classList.remove('is-scrolling');
                isScrolling = false;
            }, 100);
        };
        
        let lastScrollTime = 0;
        const throttleDelay = 16;
        
        const throttledScroll = () => {
            const now = Date.now();
            if (now - lastScrollTime >= throttleDelay) {
                handleScroll();
                lastScrollTime = now;
            }
        };
        
        window.addEventListener('scroll', throttledScroll, { passive: true, capture: true });
    }

    // Back gesture closes the open overlay (modal / mobile menu): one history entry per overlay
    pushBackState() {
        if (this._overlayPushed) return;
        try {
            history.pushState({ plOverlay: 1 }, '');
            this._overlayPushed = true;
        } catch (e) { /* ignore */ }
    }

    popBackState() {
        if (!this._overlayPushed) return;
        if (document.querySelector('.modal.active') || this.state.menuOpen) return;
        this._overlayPushed = false;
        const y = this.scrollPosition || 0;
        try {
            if (history.state && history.state.plOverlay) {
                window.addEventListener('popstate', () => window.scrollTo(0, y), { once: true });
                history.back();
            }
        } catch (e) { /* ignore */ }
    }

    setupBackGesture() {
        window.addEventListener('popstate', () => {
            if (!this._overlayPushed) return;
            this._overlayPushed = false;
            document.querySelectorAll('.modal.active').forEach((m) => {
                const btn = m.querySelector('.modal-close');
                if (btn) btn.click(); else this.closeModal(m.id);
            });
            if (this.state.menuOpen) this.closeMobileMenu();
        });
    }


    setupMobileMenu() {
        const { burgerBtn, mobileMenu, mobileMenuClose, mobileNavLinks } = this.elements;

        if (!burgerBtn || !mobileMenu) return;

        burgerBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleMobileMenu();
        });

        mobileMenuClose?.addEventListener('click', (e) => {
            e.preventDefault();
            this.closeMobileMenu();
        });

        mobileNavLinks.forEach(link => {
            link.addEventListener('click', () => this.closeMobileMenu());
        });

        mobileMenu.addEventListener('click', (e) => {
            if (e.target === mobileMenu) this.closeMobileMenu();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.state.menuOpen) {
                this.closeMobileMenu();
            }
        });

        if ('ontouchstart' in window) {
            this.setupMenuTouchOptimizations();
        }
    }

    setupMenuTouchOptimizations() {
        const { mobileMenu, mobileNavLinks } = this.elements;

        mobileMenu?.addEventListener('touchstart', (e) => {
            e.stopPropagation();
        }, { passive: true });

        mobileNavLinks.forEach(link => {
            link.addEventListener('touchstart', (e) => {
                e.stopPropagation();
            }, { passive: true });
        });
    }

    toggleMobileMenu() {
        if (this.state.menuOpen) {
            this.closeMobileMenu();
        } else {
            this.openMobileMenu();
        }
    }

    openMobileMenu() {
        const { burgerBtn, mobileMenu } = this.elements;

        this.saveScrollPosition();
        burgerBtn.classList.add('active');
        mobileMenu.classList.add('active');
        document.body.style.top = `-${this.scrollPosition}px`;
        document.body.style.overflow = 'hidden';
        document.body.classList.add('menu-open');

        this.state.menuOpen = true;

        this.emit('menu:opened');
        this.pushBackState();
    }

    closeMobileMenu() {
        const { burgerBtn, mobileMenu } = this.elements;

        burgerBtn.classList.remove('active');
        mobileMenu.classList.remove('active');
        document.body.style.overflow = '';
        document.body.style.top = '';
        document.body.classList.remove('menu-open');

        this.state.menuOpen = false;
        this.restoreScrollPosition();

        this.emit('menu:closed');
        this.popBackState();
    }

    setupModals() {

        const modalTriggers = document.querySelectorAll('[data-modal]');
        const closeButtons = document.querySelectorAll('.modal-close, .modal-close-specific');

        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.getAttribute('data-modal');
                this.openModal(modalId);
            });
        });

        closeButtons.forEach(button => {

            button.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = button.getAttribute('data-modal-id');
                this.closeModal(modalId);
            });
        });

        document.querySelectorAll('.modal').forEach(modal => {

            modal.addEventListener('click', (e) => {
                if (e.target === modal || e.target.classList.contains('modal-backdrop')) {
                    this.closeModal(modal.id);
                }
            });
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.state.activeModal) {
                this.closeModal();
            }
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        this.saveScrollPosition();
        
        // Ініціалізуємо PhoneMask для полів телефону в модальному вікні ПЕРЕД prefill
        this.initPhoneMasksForElement(modal);
        
        this.prefillModalForm(modal);

        if (modalId === 'call-request-modal') {
            const pageSrc = document.body.getAttribute('data-modal-source-page') || '';
            const sourceInput = document.getElementById('call-modal-source-page');
            if (sourceInput) {
                sourceInput.value = pageSrc;
            }
        }

        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.top = `-${this.scrollPosition}px`;
        document.body.style.overflow = 'hidden';

        this.state.activeModal = modalId;

        const firstInput = modal.querySelector('input:not([type="hidden"]), textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 300);
        }

        this.emit('modal:opened', { modalId });
        this.pushBackState();
    }

    closeModal(modalId = null) {
        const modal = modalId
            ? document.getElementById(modalId)
            : document.querySelector('.modal.active');

        if (!modal) return;

        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        document.body.style.top = '';

        this.state.activeModal = null;
        this.restoreScrollPosition();

        this.emit('modal:closed', { modalId: modal.id });
        this.popBackState();
    }

    prefillModalForm(modal) {
        const userData = this.getStoredUserData();
        if (!userData) return;

        const nameField = modal.querySelector('input[name="name"]');
        const phoneField = modal.querySelector('input[name="phone"]');

        if (nameField && userData.name) nameField.value = userData.name;
        
        // Для телефону використовуємо PhoneMask якщо він ініціалізований
        if (phoneField && userData.phone) {
            // Переконуємось що PhoneMask ініціалізований
            if (!this.phoneMasks.has(phoneField)) {
                // Якщо PhoneMask не ініціалізований, ініціалізуємо його
                this.initPhoneMasksForElement(modal);
            }
            
            if (this.phoneMasks.has(phoneField)) {
                // Якщо PhoneMask ініціалізований, встановлюємо значення через нього
                const mask = this.phoneMasks.get(phoneField);
                // Використовуємо formatValue для правильного форматування
                mask.formatValue(userData.phone);
            } else {
                // Якщо PhoneMask все ще не доступний, встановлюємо значення і форматуємо вручну
                phoneField.value = userData.phone;
                // Спробуємо ініціалізувати PhoneMask ще раз
                setTimeout(() => {
                    this._attachPhoneMask(phoneField);
                    const mask = this.phoneMasks.get(phoneField);
                    if (mask && typeof mask.formatValue === 'function') {
                        mask.formatValue(userData.phone);
                    }
                }, 0);
            }
        } else if (phoneField) {
            // Якщо немає збереженого телефону, переконуємось що +38 відображається
            if (!this.phoneMasks.has(phoneField)) {
                this.initPhoneMasksForElement(modal);
            }
            if (this.phoneMasks.has(phoneField)) {
                const mask = this.phoneMasks.get(phoneField);
                mask.ensurePrefix();
            }
        }
    }

    // ===== PHONE MASK SYSTEM =====
    setupPhoneMasks() {
        // Ініціалізуємо маску для всіх полів телефону
        this.initPhoneMasksForElement(document);
    }
    
    _useIntlPhoneMask(input) {
        // Маска обирається лише за мовою інтерфейсу, не за контейнером поля:
        // cs/en → вільний міжнародний формат, uk/ru → жорсткий український +38.
        // (синхронізовано з static/js/base.js::_useIntlPhoneMask)
        const lang = (document.documentElement.getAttribute('lang') || 'cs').toLowerCase();
        const isIntlLang = lang.indexOf('cs') === 0 || lang.indexOf('en') === 0;
        return isIntlLang && typeof IntlPhoneMask !== 'undefined';
    }

    _attachPhoneMask(input) {
        if (this.phoneMasks.has(input)) return;
        if (this._useIntlPhoneMask(input)) {
            this.phoneMasks.set(input, new IntlPhoneMask(input));
        } else if (typeof PhoneMask !== 'undefined') {
            this.phoneMasks.set(input, new PhoneMask(input));
        }
    }

    initPhoneMasksForElement(container) {
        const phoneInputs = container.querySelectorAll('input[type="tel"]');
        phoneInputs.forEach((input) => this._attachPhoneMask(input));
    }
    
    /**
     * Відновлює префікс +38 для всіх полів телефону в формі після reset
     */
    restorePhonePrefixes(form) {
        const phoneInputs = form.querySelectorAll('input[type="tel"]');
        
        phoneInputs.forEach(input => {
            if (this.phoneMasks.has(input)) {
                const mask = this.phoneMasks.get(input);
                mask.ensurePrefix();
            } else {
                this._attachPhoneMask(input);
            }
        });
    }

    setupForms() {
        const forms = document.querySelectorAll('form[data-form-type]');

        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmit(form);
            });

            // Додаємо обробники для очищення помилок при редагуванні
            const inputs = form.querySelectorAll('[required], [name="name"], [name="phone"]');
            inputs.forEach(input => {
                input.addEventListener('input', () => {
                    if (input.classList.contains('error')) {
                        input.classList.remove('error');
                        this.clearFieldError(input);
                    }
                });
            });
        });
    }

    async handleFormSubmit(form) {
        const plfRule = form.matches('.plf-form') && form.querySelector('[data-lead-contact-rule]');
        if (plfRule) { plfRule.hidden = true; plfRule.textContent = ''; delete plfRule.dataset.plfShown; }
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn?.textContent;

        // При помилці валідації на клієнті - форма НЕ очищається, відповіді залишаються
        if (!this.validateForm(form)) return;

        if (submitBtn) {
            submitBtn.classList.add('btn-loading');
            submitBtn.disabled = true;
        }

        try {
            const formData = new FormData(form);
            const formType = form.getAttribute('data-form-type');

            // Оновлюємо значення телефону з PhoneMask якщо доступний
            const phoneField = form.querySelector('[name="phone"]');
            if (phoneField && this.phoneMasks.has(phoneField)) {
                const mask = this.phoneMasks.get(phoneField);
                const cleanedValue = mask.getCleanedValue();
                formData.set('phone', cleanedValue);
            }
            // Prefix-only phone (e.g. "+420") counts as empty, so e-mail/Telegram-only leads pass server validation
            if (phoneField && String(formData.get('phone') || '').replace(/\D/g, '').length <= 3) {
                formData.set('phone', '');
            }

            this.saveUserData(formData);

            const response = await this.submitForm(formData, formType);
            const data = await response.json();

            if (response.ok && data.success) {
                // Enhanced Conversions: phone for GTM before thank-you redirect
                if (data.redirect && window.ECPhone) {
                    window.ECPhone.saveFromRaw(formData.get('phone'));
                }

                // ТІЛЬКИ при успішній відправці - очищаємо форму
                // Для тесту - виклик спеціального очищення
                if (formType === 'test' && window.calculatorInstance) {
                    window.calculatorInstance.clearForm();
                } else {
                    form.reset();
                    // Після reset відновлюємо префікс +38 для всіх полів телефону
                    this.restorePhonePrefixes(form);
                }

                this.handleFormSuccess(data);
                this.closeModal();
            } else {
                // При помилці від сервера - форма НЕ очищається, відповіді залишаються
                // Обробляємо помилку від сервера
                const errorMessage = data.message || (window.I18N?.errorSending || this.fallbackText('Odeslání se nezdařilo. Zkuste to prosím znovu.', 'Sending failed. Please try again.'));
                
                // Перевіримо чи це помилка валідації конкретного поля
                if (errorMessage.includes('jméno') || errorMessage.includes('name')) {
                    const nameField = form.querySelector('[name="name"]');
                    if (nameField) {
                        nameField.classList.add('error');
                        this.showFieldError(nameField, errorMessage);
                    }
                } else if (errorMessage.includes('telefon') || errorMessage.includes('phone') || errorMessage.includes('číslo') || errorMessage.includes('number')) {
                    const phoneField = form.querySelector('[name="phone"]');
                    if (phoneField) {
                        phoneField.classList.add('error');
                        this.showFieldError(phoneField, errorMessage);
                    }
                } else {
                    this.showNotification(errorMessage, 'error');
                }
            }

        } catch (error) {
            // При помилці мережі/винятку - форма НЕ очищається, відповіді залишаються
            console.error('Form error:', error);
            this.showNotification(window.I18N?.errorSubmittingForm || this.fallbackText('Odeslání se nezdařilo. Zkuste to prosím znovu.', 'Sending failed. Please try again.'), 'error');
        } finally {
            if (submitBtn) {
                submitBtn.classList.remove('btn-loading');
                submitBtn.disabled = false;
                if (originalText) submitBtn.textContent = originalText;
            }
        }
    }

    validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('error');
                this.showFieldError(field, window.I18N?.fieldRequired || this.fallbackText('Toto pole je povinné.', 'This field is required.'));
                isValid = false;
            } else {
                field.classList.remove('error');
                this.clearFieldError(field);
            }
        });

        // Додаткова валідація для імені та телефону (як на сервері)
        const nameField = form.querySelector('[name="name"]');
        const phoneField = form.querySelector('[name="phone"]');

        if (nameField && nameField.value) {
            const name = nameField.value.trim();
            let nameError = null;

            if (name.length < 2) {
                nameError = window.I18N?.nameMinLength || this.fallbackText('Zadejte platné jméno (alespoň 2 znaky).', 'Enter a valid name (at least 2 characters).');
            } else if (/^\d+$/.test(name)) {
                nameError = window.I18N?.nameDigitsOnly || this.fallbackText('Jméno nemůže obsahovat pouze číslice.', 'Name cannot contain digits only.');
            } else if (!/\p{L}/u.test(name)) {
                nameError = window.I18N?.nameNeedsLetter || this.fallbackText('Zadejte platné jméno (alespoň jedno písmeno).', 'Enter a valid name (at least one letter).');
            }

            if (nameError) {
                nameField.classList.add('error');
                this.showFieldError(nameField, nameError);
                isValid = false;
            } else {
                nameField.classList.remove('error');
                this.clearFieldError(nameField);
            }
        }

        if (phoneField && phoneField.value) {
            let phoneError = null;
            
            // Використовуємо PhoneMask валідацію якщо доступна
            if (this.phoneMasks.has(phoneField)) {
                const mask = this.phoneMasks.get(phoneField);
                const validation = mask.validate();
                
                if (!validation.valid) {
                    phoneError = validation.message;
                }
            } else {
                const digits = phoneField.value.replace(/\D/g, '');
                if (digits.length < 7) {
                    phoneError = window.I18N?.phoneInvalid || this.fallbackText('Zadejte platné telefonní číslo.', 'Enter a valid phone number.');
                }
            }

            if (phoneError) {
                phoneField.classList.add('error');
                this.showFieldError(phoneField, phoneError);
                isValid = false;
            } else {
                phoneField.classList.remove('error');
                this.clearFieldError(phoneField);
            }
        }

        return isValid;
    }

    showFieldError(field, message) {
        const plf = field.closest('.plf-form');
        if (plf) {
            const rule = plf.querySelector('[data-lead-contact-rule]');
            if (rule && rule.dataset.plfShown !== '1') {
                rule.dataset.plfShown = '1';
                rule.hidden = false;
                rule.textContent = message;
                rule.classList.add('lead-form-contact-rule--error');
            }
            return;
        }
        const errorEl = field.parentElement?.querySelector('.calc-field__error');
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.add('show');
        }
    }

    clearFieldError(field) {
        const errorEl = field.parentElement?.querySelector('.calc-field__error');
        if (errorEl) {
            errorEl.textContent = '';
            errorEl.classList.remove('show');
        }
    }

    localizedFormUrl(path) {
        const lang = (document.documentElement.lang || 'cs').split('-')[0].toLowerCase();
        // cs = LANGUAGE_CODE with prefix_default_language=False -> no prefix
        // (synced with static/js/base.js::localizedFormUrl)
        if (!lang || lang === 'cs') return path;
        return `/${lang}${path}`;
    }

    async submitForm(formData, formType) {
        const raw = formType === 'test' ? '/forms/test/' : '/forms/submit/';
        const url = this.localizedFormUrl(raw);

        if (formType !== 'test') {
            formData.append('form_type', formType);
        }

        if (window.GCLIDCapture) {
            window.GCLIDCapture.appendToFormData(formData);
        }

        return fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            }
        });
    }

    handleFormSuccess(data) {
        if (data.redirect) {
            window.location.href = data.redirect;
        }
    }

    setupLanguageSwitcher() {
        const { langDropdown, langDropdownBtn, langSwitchers } = this.elements;

        langDropdownBtn?.addEventListener('click', (e) => {
            e.preventDefault();
            langDropdown?.classList.toggle('active');
        });

        document.addEventListener('click', (e) => {
            if (langDropdown && !langDropdown.contains(e.target)) {
                langDropdown.classList.remove('active');
            }
        });

        langSwitchers.forEach(switcher => {
            switcher.addEventListener('click', (e) => {
                // Plain links (real href to /<path>/ or /en/<path>/) navigate natively.
                const href = switcher.getAttribute('href');
                if (href && href !== '#') return;
                e.preventDefault();
                const langCode = switcher.getAttribute('data-language-code');
                if (langCode) this.setLanguage(langCode);
            });
        });
    }

    setLanguage(langCode) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/i18n/set_language/';

        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = this.getCSRFToken();
        form.appendChild(csrfInput);

        const langInput = document.createElement('input');
        langInput.type = 'hidden';
        langInput.name = 'language';
        langInput.value = langCode;
        form.appendChild(langInput);

        let nextUrl = window.location.pathname + window.location.search;
        const originalUrl = nextUrl;
        // Remove language prefix (/en/, /cs/); cs (default) has no prefix
        // (синхронізовано з static/js/base.js::setLanguage)
        nextUrl = nextUrl.replace(/^\/(en|cs)\//, '/');

        const nextInput = document.createElement('input');
        nextInput.type = 'hidden';
        nextInput.name = 'next';
        nextInput.value = nextUrl;
        form.appendChild(nextInput);

        document.body.appendChild(form);
        form.submit();
    }

    setupAccessibility() {
        const animatedElements = document.querySelectorAll('.animate-on-scroll');

        if (animatedElements.length === 0) return;
        if (!('IntersectionObserver' in window)) {
            animatedElements.forEach(el => el.classList.add('visible'));
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    
                    setTimeout(() => {
                        entry.target.classList.add('animated');
                    }, 600);
                    
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.05,
            rootMargin: '0px 0px -20px 0px'
        });

        animatedElements.forEach(el => observer.observe(el));
    }

    setupFooterAccordion() {
        const footerSections = document.querySelectorAll('.footer-section:not(.footer-form-section)');
        
        if (footerSections.length === 0) return;

        footerSections.forEach(section => {
            const heading = section.querySelector('h3');
            if (!heading) return;

            heading.addEventListener('click', () => {
                if (window.innerWidth >= 768) return;

                section.classList.toggle('footer-accordion-active');

                this.emit('footer:accordion-toggle', {
                    section: heading.textContent,
                    isOpen: section.classList.contains('footer-accordion-active')
                });
            });
        });

        window.addEventListener('resize', () => {
            if (window.innerWidth >= 768) {
                footerSections.forEach(section => {
                    section.classList.remove('footer-accordion-active');
                });
            }
        });
    }

    setupContactWidget() {
        const widget = document.getElementById('contact-widget');
        const toggle = document.getElementById('contact-widget-toggle');
        const panel  = document.getElementById('contact-widget-panel');

        if (!widget || !toggle || !panel) return;

        const openWidget = () => {
            widget.classList.add('contact-widget--open');
            toggle.setAttribute('aria-expanded', 'true');
            panel.setAttribute('aria-hidden', 'false');
        };

        const closeWidget = () => {
            widget.classList.remove('contact-widget--open');
            toggle.setAttribute('aria-expanded', 'false');
            panel.setAttribute('aria-hidden', 'true');
        };

        const isWidgetOpen = () => widget.classList.contains('contact-widget--open');

        toggle.addEventListener('click', () => {
            isWidgetOpen() ? closeWidget() : openWidget();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && isWidgetOpen()) closeWidget();
        });

        document.addEventListener('click', (e) => {
            if (isWidgetOpen() && !widget.contains(e.target)) closeWidget();
        });
    }

    saveScrollPosition() {
        this.scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
    }

    restoreScrollPosition() {
        if (this.scrollPosition !== undefined) {
            window.scrollTo({
                top: this.scrollPosition,
                behavior: 'auto'
            });
        }
    }

    getCSRFToken() {
        if (window.PrometeyUtils?.getCSRFToken) {
            return window.PrometeyUtils.getCSRFToken();
        }

        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            const token = metaTag.getAttribute('content');
            if (token) return token;
        }

        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        if (input) return input.value;

        const match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }

    saveUserData(formData) {
        const userData = {
            name: formData.get('name'),
            phone: formData.get('phone'),
            timestamp: Date.now()
        };

        try {
            sessionStorage.setItem('prometey_user_data', JSON.stringify(userData));
        } catch (error) {
            console.error('Failed to save user data:', error);
        }
    }

    getStoredUserData() {
        try {
            const data = sessionStorage.getItem('prometey_user_data');
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Failed to get user data:', error);
            return null;
        }
    }

    emit(eventName, data = null) {
        const event = new CustomEvent(eventName, { detail: data });
        document.dispatchEvent(event);
        window.dispatchEvent(event);
    }

    on(eventName, callback) {
        document.addEventListener(eventName, callback);
    }

    off(eventName, callback) {
        document.removeEventListener(eventName, callback);
    }

    static getInstance() {
        if (!window.prometeyApp) {
            window.prometeyApp = new PrometeyApp();
        }
        return window.prometeyApp;
    }
}

const notificationStyles = document.createElement('style');
notificationStyles.id = 'prometey-notification-styles';
notificationStyles.textContent = `
.prometey-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10000;
    padding: 15px 20px;
    background: var(--color-white);
    border: 2px solid var(--color-brand-orange);
    font-weight: 600;
    font-size: var(--font-base);
    transform: translateX(400px);
    transition: transform var(--transition-normal) var(--easing-default);
    display: flex;
    align-items: center;
    gap: 10px;
    box-shadow: var(--shadow-lg);
}

.prometey-notification--show {
    transform: translateX(0);
}

.prometey-notification--error {
    border-color: var(--color-brand-orange);
    color: var(--color-brand-orange);
    background: #ffebee;
}

.prometey-notification__close {
    background: none;
    border: none;
    font-size: 20px;
    line-height: 1;
    cursor: pointer;
    color: inherit;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform var(--transition-fast) var(--easing-default);
}

.prometey-notification__close:hover {
    transform: rotate(90deg);
}

@media (max-width: 767px) {
    .prometey-notification {
        top: 20px;
        right: var(--space-xs);
        left: var(--space-xs);
        width: calc(100% - var(--space-xs) * 2);
        max-width: none;
        font-size: var(--font-small);
        padding: 12px 16px;
    }
}
`;

if (!document.getElementById('prometey-notification-styles')) {
    document.head.appendChild(notificationStyles);
}

const app = PrometeyApp.getInstance();

if (typeof module !== 'undefined' && module.exports) {
    module.exports = PrometeyApp;
}

// ========================================
// HOME.JS - Логіка головної сторінки
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    initServiceModals();
    initProjectStories();
    initAnalytics();
    initWhyChooseAnimations();
});

function initServiceCardsOptimized() {
    const serviceCards = document.querySelectorAll('.service-card');
    if (serviceCards.length === 0) return;
    
    if (!('IntersectionObserver' in window)) {
        serviceCards.forEach(card => {
            card.classList.add('visible');
            loadBackground(card);
        });
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const card = entry.target;
                card.classList.add('visible');
                
                if (card.classList.contains('lazy-bg')) {
                    loadBackground(card);
                }
                
                setTimeout(() => {
                    card.style.willChange = 'auto';
                }, 600);
                
                observer.unobserve(card);
            }
        });
    }, {
        threshold: 0.01,
        rootMargin: '200px'
    });

    serviceCards.forEach(card => {
        const rect = card.getBoundingClientRect();
        const isInViewport = rect.top < window.innerHeight && rect.bottom > 0;
        
        if (isInViewport) {
            card.classList.add('visible');
            loadBackground(card);
            setTimeout(() => {
                card.style.willChange = 'auto';
            }, 600);
        } else {
            observer.observe(card);
        }
    });
}

function initServiceModals() {
    let savedScrollPosition = 0;

    const lockScroll = () => {
        savedScrollPosition = window.pageYOffset || document.documentElement.scrollTop;
        document.body.style.top = `-${savedScrollPosition}px`;
        document.body.classList.add('modal-open', 'service-modal-open');
        document.documentElement.style.backgroundColor = '#000';
    };

    const unlockScroll = () => {
        document.body.style.top = '';
        document.body.classList.remove('modal-open', 'service-modal-open');
        document.documentElement.style.backgroundColor = '';
        window.scrollTo({
            top: savedScrollPosition,
            behavior: 'auto'
        });
    };

    const openModal = (serviceType) => {
        const modalId = `service-${serviceType}-modal`;
        const modal = document.getElementById(modalId);

        if (!modal) return;

        lockScroll();
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');

        const closeModal = () => {
            modal.classList.remove('active');
            modal.setAttribute('aria-hidden', 'true');
            unlockScroll();
        };

        const closeBtn = modal.querySelector('.modal-close');
        const backdrop = modal.querySelector('.modal-backdrop');

        closeBtn.removeEventListener('click', closeModal);
        backdrop.removeEventListener('click', closeModal);

        closeBtn.addEventListener('click', closeModal);
        backdrop.addEventListener('click', closeModal);

        document.addEventListener('keydown', function escHandler(e) {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', escHandler);
            }
        });
    };

    document.querySelectorAll('.service-card').forEach(card => {
        card.addEventListener('click', (e) => {
            if (e.target.closest('.service-detail-btn')) return;
            openModal(card.dataset.service);
        });
    });

    document.querySelectorAll('.service-detail-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            openModal(btn.closest('.service-card').dataset.service);
        });
    });
}

function initProjectStories() {
    const container = document.querySelector('.projects-stories-container');
    if (!container) return;
    
    waitForImages(container).then(() => {
        initMarqueeAnimation(container);
    }).catch(() => {
        setTimeout(() => initMarqueeAnimation(container), 500);
    });
}

function waitForImages(container) {
    return new Promise((resolve, reject) => {
        const images = container.querySelectorAll('img');
        if (images.length === 0) {
            resolve();
            return;
        }
        
        let loadedCount = 0;
        const totalImages = images.length;
        const timeout = setTimeout(() => reject('timeout'), 3000);
        
        images.forEach(img => {
            if (img.complete) {
                loadedCount++;
                if (loadedCount === totalImages) {
                    clearTimeout(timeout);
                    resolve();
                }
            } else {
                img.addEventListener('load', () => {
                    loadedCount++;
                    if (loadedCount === totalImages) {
                        clearTimeout(timeout);
                        resolve();
                    }
                }, { once: true });
                
                img.addEventListener('error', () => {
                    loadedCount++;
                    if (loadedCount === totalImages) {
                        clearTimeout(timeout);
                        resolve();
                    }
                }, { once: true });
            }
        });
    });
}

function initMarqueeAnimation(container) {
    const stories = container.querySelectorAll('.project-story:not(.story-clone)');
    if (stories.length === 0) return;
    
    const containerStyles = window.getComputedStyle(container);
    const gap = parseFloat(containerStyles.gap) || 24;
    
    const firstStory = stories[0];
    const lastStory = stories[stories.length - 1];
    const setWidth = (lastStory.offsetLeft + lastStory.offsetWidth + gap) - firstStory.offsetLeft;
    
    container.style.setProperty('--marquee-distance', `${setWidth}px`);
    container.setAttribute('aria-label', (((document.documentElement.getAttribute('lang') || 'cs').toLowerCase().indexOf('en') === 0) ? 'Our projects — automatic showcase' : 'Naše projekty — automatická ukázka'));
    container.setAttribute('role', 'marquee');
    
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    requestAnimationFrame(() => {
                        container.classList.add('marquee-active');
                    });
                    observer.unobserve(container);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });
        
        observer.observe(container);
    } else {
        requestAnimationFrame(() => {
            container.classList.add('marquee-active');
        });
    }
}

function initAnalytics() {
    document.addEventListener('click', (e) => {
        const button = e.target.closest('.btn');
        if (button && typeof gtag !== 'undefined') {
            gtag('event', 'button_click', {
                button_text: button.textContent.trim(),
                page_location: window.location.href
            });
        }
    }, { passive: true });

    let timeOnPage = 0;
    let trackedEngagement = false;

    const timeTracker = setInterval(() => {
        timeOnPage += 1;
        if (timeOnPage === 30 && !trackedEngagement && typeof gtag !== 'undefined') {
            gtag('event', 'engaged_session', {
                time_on_page: timeOnPage
            });
            trackedEngagement = true;
            clearInterval(timeTracker);
        }
    }, 1000);
}

function initWhyChooseAnimations() {
    const whyGrid = document.querySelector('.v2-why-grid');
    const whyCards = document.querySelectorAll('.v2-why-grid .v2-why-card');
    if (whyCards.length === 0) return;

    const reduceMotion = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (!whyGrid || reduceMotion) return;
    if (whyGrid.dataset.whyReady === '1') return;
    whyGrid.dataset.whyReady = '1';

    const canHover = () =>
        window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;

    function setActiveCard(target) {
        whyCards.forEach(card => {
            card.classList.toggle('v2-why-card--active', card === target);
        });
    }

    whyCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            if (!canHover()) return;
            setActiveCard(card);
        });

        card.addEventListener('click', () => {
            setActiveCard(card);
        });
    });

    whyGrid.addEventListener('mouseleave', () => {
        if (!canHover()) return;
        setActiveCard(null);
    });
}

// Helper функція для завантаження background images
function loadBackground(element) {
    const isMobile = window.innerWidth <= 767;
    const bgUrl = isMobile 
        ? element.getAttribute('data-bg-mobile') 
        : element.getAttribute('data-bg-desktop');
    
    if (bgUrl) {
        const img = new Image();
        img.onload = () => {
            element.style.backgroundImage = `url('${bgUrl}')`;
            element.classList.add('lazy-bg-loaded');
            element.classList.remove('lazy-bg');
        };
        img.src = bgUrl;
    }
}

