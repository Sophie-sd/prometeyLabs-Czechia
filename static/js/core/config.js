/**
 * CONFIG.JS - Центральний конфігураційний файл
 * Всі константи, endpoints, event names
 * Версія: 2.0 (2025)
 */

export const CONFIG = {
    // ===== API ENDPOINTS =====
    endpoints: {
        formSubmit: '/forms/submit/',
        formTest: '/forms/test/',
        languageSet: '/i18n/set_language/',
        blogSearch: '/blog/search/',
    },

    // ===== EVENT NAMES =====
    events: {
        // System
        initialized: 'app:initialized',
        ready: 'app:ready',
        
        // MobileCore
        mobileCoreInit: 'mobilecore:initialized',
        viewportChange: 'mobilecore:viewportchange',
        
        // VideoSystem
        videoLoaded: 'videosystem:video:loaded',
        videoPlaying: 'videosystem:video:playing',
        videoError: 'videosystem:video:error',
        videoAutoplayFailed: 'videosystem:video:autoplay-failed',
        
        // Navigation
        menuOpen: 'menu:opened',
        menuClose: 'menu:closed',
        
        // Modals
        modalOpen: 'modal:opened',
        modalClose: 'modal:closed',
        
        // Forms
        formSubmit: 'form:submit',
        formSuccess: 'form:success',
        formError: 'form:error',
    },

    // ===== TIMEOUTS & DELAYS =====
    timing: {
        scrollThreshold: 50,
        menuTransition: 400,
        notificationDuration: 5000,
        debounceDelay: 100,
        videoLoadTimeout: 10000,
        autoAdvanceDelay: 500,
        touchFeedbackMin: 100,
    },

    // ===== ANIMATION SETTINGS =====
    animation: {
        intersectionThreshold: 0.1,
        intersectionMargin: '0px 0px -50px 0px',
        scrollBehavior: 'smooth',
        scrollOffset: 80,
    },

    // ===== STORAGE KEYS =====
    storage: {
        userData: 'prometey_user_data',
        calculatorAnswers: 'calculator_answers',
        language: 'prometey_language',
        theme: 'prometey_theme',
    },

    // ===== FORM TYPES =====
    formTypes: {
        test: 'test',
        contact: 'contact',
        siteRequest: 'site_request',
        callRequest: 'call_request',
    },

    // ===== MODAL IDS =====
    modals: {
        siteRequest: 'site-request-modal',
        callRequest: 'call-request-modal',
    },

    // ===== SELECTORS (часто використовувані) =====
    selectors: {
        nav: '.main-navigation',
        burgerBtn: '.burger-menu',
        mobileMenu: '.mobile-menu',
        modal: '.modal',
        form: 'form[data-form-type]',
        card: '.card, .blog-card, .service-card',
        video: 'video',
        lazyVideo: '.lazy-video',
    },

    // ===== BREAKPOINTS (синхронізовані з CSS) =====
    breakpoints: {
        mobile: 767,
        tablet: 1024,
        desktop: 1200,
    },

    // ===== FEATURE FLAGS =====
    features: {
        enableAnalytics: true,
        enableAnimations: true,
        enableHaptic: true,
        enableNotifications: true,
        enableDebugLog: false,
    },

    // ===== ANALYTICS =====
    analytics: {
        trackPageView: true,
        trackClicks: true,
        trackScroll: true,
        trackForms: true,
        engagementTime: 30, // seconds
    },
};

// ===== HELPER: Get CSS Variable =====
export function getCSSVar(varName) {
    return getComputedStyle(document.documentElement)
        .getPropertyValue(varName)
        .trim();
}

// ===== HELPER: Is Mobile =====
export function isMobile() {
    return window.innerWidth <= CONFIG.breakpoints.mobile;
}

// ===== HELPER: Is Tablet =====
export function isTablet() {
    return window.innerWidth > CONFIG.breakpoints.mobile && 
           window.innerWidth <= CONFIG.breakpoints.tablet;
}

// ===== HELPER: Is Desktop =====
export function isDesktop() {
    return window.innerWidth > CONFIG.breakpoints.tablet;
}

// ===== EXPORT (HYBRID - працює як module і як script) =====
window.AppConfig = CONFIG;

// ES Module export (якщо завантажується як module)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}

// Для import в інших modules
export default CONFIG;
