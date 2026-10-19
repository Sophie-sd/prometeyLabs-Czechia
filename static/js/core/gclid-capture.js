/**
 * Google Ads GCLID & UTM capture + first-touch landing + outbound-click tracking.
 *
 * Values (`_prm_*`) are appended to the POST data of every lead form
 * (via `appendToFormData`) and end up in `FormSubmission.gclid/utm_*` and
 * `extra_data.source_page / landing_page / landing_referrer` (KeyCRM attribution).
 *
 * Consent (CookieYes, see /cookies/): `_prm_*` cookies are written ONLY after the
 * visitor accepts the "advertisement" or "analytics" category. Before that, values
 * live in sessionStorage / memory for the current session only (forms still get
 * them). When consent arrives (`cookieyes_consent_update` / `cookieyes_banner_load`
 * or an existing consent via `getCkyConsent()`), session values are persisted to
 * cookies; when consent is withdrawn, the cookies are expired again.
 *
 * Clicks on tel: / t.me / wa.me / m.me are pushed to dataLayer (GTM) as
 * `phone_click` / `messenger_click`. WhatsApp / m.me links get a `?text=` campaign tag.
 */
(function () {
    'use strict';

    const COOKIE_DAYS = 90;
    const TRACKING_PARAMS = ['gclid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];
    const LANDING_KEYS = ['landing_path', 'landing_referrer'];
    // Messenger prefill tag (cs default, en on /en/ pages).
    const IS_EN = (document.documentElement.getAttribute('lang') || 'cs').toLowerCase().indexOf('en') === 0;
    const TAG_ESHOPS = IS_EN ? 'E-shops' : 'E-shopy';
    const TAG_CORPORATE = IS_EN ? 'Corporate websites' : 'Firemní weby';
    const MESSAGE_PREFIX = IS_EN ? 'Google Ads enquiry: ' : 'Poptávka z Google Ads: ';
    const CAMPAIGN_TAGS = [
        { needle: 'shop', label: TAG_ESHOPS },
        { needle: 'ecom', label: TAG_ESHOPS },
        { needle: 'corp', label: TAG_CORPORATE },
        { needle: 'company', label: TAG_CORPORATE },
    ];

    const SESSION_PREFIX = 'prm_';
    const memoryStore = {};
    let consentGranted = false;

    function sessionGet(name) {
        try {
            const v = window.sessionStorage.getItem(SESSION_PREFIX + name);
            if (v !== null) return v;
        } catch (e) { /* storage blocked */ }
        return memoryStore[name] || '';
    }

    function sessionSet(name, value) {
        memoryStore[name] = value;
        try { window.sessionStorage.setItem(SESSION_PREFIX + name, value); } catch (e) { /* storage blocked */ }
    }

    function sessionRemove(name) {
        delete memoryStore[name];
        try { window.sessionStorage.removeItem(SESSION_PREFIX + name); } catch (e) { /* storage blocked */ }
    }

    function deleteCookie(name) {
        document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;SameSite=Lax`;
    }

    function allKeys() {
        return TRACKING_PARAMS.concat(LANDING_KEYS).map((k) => '_prm_' + k);
    }

    /** Read: cookie (consented, earlier visit) → session/memory. */
    function read(name) {
        return getCookie(name) || sessionGet(name);
    }

    /** Write: cookie only with consent, otherwise session/memory. */
    function store(name, value) {
        if (consentGranted) {
            setCookie(name, value, COOKIE_DAYS);
            sessionRemove(name);
        } else {
            sessionSet(name, value);
        }
    }

    function consentFromCategories(categories) {
        if (!categories) return false;
        return !!(categories.advertisement || categories.analytics);
    }

    function consentFromList(list) {
        return Array.isArray(list) && (list.indexOf('advertisement') !== -1 || list.indexOf('analytics') !== -1);
    }

    function applyConsent(granted) {
        consentGranted = !!granted;
        allKeys().forEach((name) => {
            if (consentGranted) {
                const v = sessionGet(name);
                if (v && !getCookie(name)) setCookie(name, v, COOKIE_DAYS);
                if (v) sessionRemove(name);
            } else {
                const c = getCookie(name);
                if (c) {
                    sessionSet(name, c); // keep for this session's forms only
                    deleteCookie(name);
                }
            }
        });
    }

    function checkExistingConsent() {
        try {
            if (typeof window.getCkyConsent === 'function') {
                const c = window.getCkyConsent();
                if (c && c.categories) applyConsent(consentFromCategories(c.categories));
            }
        } catch (e) { /* CookieYes not ready */ }
    }

    function listenConsent() {
        document.addEventListener('cookieyes_consent_update', (e) => {
            const d = (e && e.detail) || {};
            applyConsent(consentFromList(d.accepted));
        });
        document.addEventListener('cookieyes_banner_load', (e) => {
            const d = (e && e.detail) || {};
            if (d.categories) applyConsent(consentFromCategories(d.categories));
            else checkExistingConsent();
        });
    }

    function setCookie(name, value, days) {
        const date = new Date();
        date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
        const expires = 'expires=' + date.toUTCString();
        const secure = location.protocol === 'https:' ? ';Secure' : '';
        document.cookie = `${name}=${encodeURIComponent(value)};${expires};path=/${secure};SameSite=Lax`;
    }

    function getCookie(name) {
        const prefix = name + '=';
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const c = cookies[i].trim();
            if (c.indexOf(prefix) === 0) {
                return decodeURIComponent(c.substring(prefix.length));
            }
        }
        return '';
    }

    function captureFromURL() {
        const params = new URLSearchParams(window.location.search);
        TRACKING_PARAMS.forEach((p) => {
            const v = params.get(p);
            if (v) store('_prm_' + p, v);
        });
    }

    function captureFirstTouch() {
        if (!read('_prm_landing_path')) {
            store('_prm_landing_path', window.location.pathname);
        }
        if (!read('_prm_landing_referrer') && document.referrer) {
            try {
                const ref = new URL(document.referrer);
                if (ref.host !== window.location.host) {
                    store('_prm_landing_referrer', document.referrer);
                }
            } catch (e) {
                // ignore invalid referrer
            }
        }
    }

    function getTrackingData() {
        const data = {};
        TRACKING_PARAMS.forEach((p) => {
            const v = read('_prm_' + p);
            if (v) data[p] = v;
        });
        LANDING_KEYS.forEach((k) => {
            const v = read('_prm_' + k);
            if (v) data[k === 'landing_path' ? 'landing_page' : k] = v;
        });
        return data;
    }

    function hasNonEmpty(formData, key) {
        if (!formData.has(key)) return false;
        const v = formData.get(key);
        return v !== null && String(v).trim() !== '';
    }

    function setField(formData, key, value) {
        if (formData.has(key)) {
            formData.set(key, value);
        } else {
            formData.append(key, value);
        }
    }

    function appendToFormData(formData) {
        const tracking = getTrackingData();
        Object.keys(tracking).forEach((k) => {
            if (!hasNonEmpty(formData, k)) setField(formData, k, tracking[k]);
        });
        if (!hasNonEmpty(formData, 'source_page')) {
            setField(formData, 'source_page', window.location.pathname);
        }
        return formData;
    }

    function campaignTag() {
        const campaign = (read('_prm_utm_campaign') || '').toLowerCase();
        const landing = (read('_prm_landing_path') || window.location.pathname || '').toLowerCase();
        const hay = campaign + ' ' + landing;
        for (let i = 0; i < CAMPAIGN_TAGS.length; i++) {
            if (hay.indexOf(CAMPAIGN_TAGS[i].needle) !== -1) {
                return CAMPAIGN_TAGS[i].label;
            }
        }
        return '';
    }

    function pushEvent(name, link) {
        window.dataLayer = window.dataLayer || [];
        const tracking = getTrackingData();
        window.dataLayer.push(Object.assign({
            event: name,
            link_url: link.href,
            link_text: (link.textContent || '').trim().slice(0, 80),
            page_path: window.location.pathname,
        }, tracking));
    }

    function decorateMessengerLink(link) {
        if (link.dataset.prmDecorated === '1') return;
        link.dataset.prmDecorated = '1';
        const href = link.getAttribute('href') || '';
        const tag = campaignTag();
        if (!tag) return;
        const text = MESSAGE_PREFIX + tag;
        try {
            const url = new URL(href, window.location.origin);
            const host = url.host.toLowerCase();
            if (host === 'wa.me' || host === 'api.whatsapp.com' || host === 'm.me') {
                if (!url.searchParams.has('text')) {
                    url.searchParams.set('text', text);
                    link.setAttribute('href', url.toString());
                }
            } else if (host === 't.me') {
                // Telegram honours `?text=` only on its own `share/url` links.
                // For plain profile/bot links the tag is sent as an event only.
                if (url.pathname.endsWith('/share/url') && !url.searchParams.has('text')) {
                    url.searchParams.set('text', text);
                    link.setAttribute('href', url.toString());
                }
            }
        } catch (e) {
            // ignore
        }
    }

    function isPhone(link) {
        return (link.getAttribute('href') || '').toLowerCase().startsWith('tel:');
    }

    function isMessenger(link) {
        const h = (link.getAttribute('href') || '').toLowerCase();
        return h.includes('t.me/') || h.includes('wa.me/') ||
               h.includes('api.whatsapp.com') || h.includes('m.me/');
    }

    function trackOutboundClicks() {
        document.addEventListener('click', (e) => {
            const link = e.target.closest && e.target.closest('a[href]');
            if (!link) return;
            if (isPhone(link)) {
                pushEvent('phone_click', link);
            } else if (isMessenger(link)) {
                decorateMessengerLink(link);
                pushEvent('messenger_click', link);
            }
        }, { capture: true, passive: true });
    }

    listenConsent();
    checkExistingConsent();
    captureFromURL();
    captureFirstTouch();

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', trackOutboundClicks, { once: true });
    } else {
        trackOutboundClicks();
    }

    window.GCLIDCapture = {
        getTrackingData: getTrackingData,
        appendToFormData: appendToFormData,
    };
})();
