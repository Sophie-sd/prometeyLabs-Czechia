/**
 * Google Ads GCLID & UTM capture + first-touch landing + outbound-click tracking.
 *
 * Values (`_prm_*`) are appended to the POST data of every lead form
 * (via `appendToFormData`) and end up in `FormSubmission.gclid/utm_*` and
 * `extra_data.source_page / landing_page / landing_referrer` (KeyCRM attribution).
 *
 * Consent (first-party banner #pl-consent, cookie `pl_consent` = JSON {v,a,m,t,id},
 * see templates/partials/consent_banner.html + partials/gtm_head.html, /cookies/ čl. 7):
 *  - before Marketing consent (m=1) values live ONLY in page memory (`memoryStore`);
 *    nothing is written to sessionStorage or cookies;
 *  - after Marketing consent they are copied to sessionStorage (`prm_*`, until the tab closes);
 *  - on withdrawal sessionStorage is cleared again (memory keeps the current page's values).
 * Forms always get the in-memory/session values via `appendToFormData`, so gclid/utm reach
 * KeyCRM with the lead even without consent (same as before). Consent changes arrive via the
 * `pl_consent_update` DOM event dispatched by the banner (detail = the pl_consent object).
 * Legacy `_prm_*` cookies (older versions) are moved to memory/session and expired.
 *
 * Clicks on tel: / t.me / wa.me / m.me are pushed to dataLayer (GTM) as
 * `phone_click` / `messenger_click`; wa.me / t.me / mailto: clicks also push
 * `contact_click` with channel whatsapp|telegram|email. WhatsApp / m.me links get a `?text=` campaign tag.
 */
(function () {
    'use strict';

    const TRACKING_PARAMS = ['gclid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];
    const LANDING_KEYS = ['landing_path', 'landing_referrer'];
    // Messenger prefill tag (cs default, en on /en/ pages).
    const IS_EN = (document.documentElement.getAttribute('lang') || 'cs').toLowerCase().indexOf('en') === 0;
    const TAG_ESHOPS = IS_EN ? 'E-shops' : 'E-shopy';
    const TAG_CORPORATE = IS_EN ? 'Corporate websites' : 'Firemní weby';
    const MESSAGE_PREFIX = IS_EN ? 'Google Ads enquiry: ' : 'Poptávka z Google Ads: ';
    // gclid є, але тег кампанії не розпізнано → загальний текст без тегу.
    const MESSAGE_GENERIC = IS_EN ? 'Google Ads enquiry' : 'Poptávka z Google Ads';
    const CAMPAIGN_TAGS = [
        { needle: 'shop', label: TAG_ESHOPS },
        { needle: 'ecom', label: TAG_ESHOPS },
        { needle: 'corp', label: TAG_CORPORATE },
        { needle: 'company', label: TAG_CORPORATE },
    ];

    const SESSION_PREFIX = 'prm_';
    const memoryStore = {};
    let marketingGranted = false;

    function allKeys() {
        return TRACKING_PARAMS.concat(LANDING_KEYS).map((k) => '_prm_' + k);
    }

    function sessionRead(name) {
        try { return window.sessionStorage.getItem(SESSION_PREFIX + name) || ''; } catch (e) { return ''; }
    }

    function sessionWrite(name, value) {
        try { window.sessionStorage.setItem(SESSION_PREFIX + name, value); } catch (e) { /* storage blocked */ }
    }

    function sessionRemove(name) {
        try { window.sessionStorage.removeItem(SESSION_PREFIX + name); } catch (e) { /* storage blocked */ }
    }

    function getCookie(name) {
        const prefix = name + '=';
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const c = cookies[i].trim();
            if (c.indexOf(prefix) === 0) {
                try { return decodeURIComponent(c.substring(prefix.length)); } catch (e) { return ''; }
            }
        }
        return '';
    }

    function deleteCookie(name) {
        document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;SameSite=Lax`;
    }

    /** Read: page memory → sessionStorage (filled only after Marketing consent). */
    function read(name) {
        return memoryStore[name] || (marketingGranted ? sessionRead(name) : '');
    }

    /** Write: always page memory; sessionStorage only with Marketing consent. */
    function store(name, value) {
        memoryStore[name] = value;
        if (marketingGranted) sessionWrite(name, value);
    }

    /** pl_consent cookie -> {a,m,...} or null (format owned by partials/gtm_head.html). */
    function readConsent() {
        try {
            if (window.plConsent && typeof window.plConsent.read === 'function') {
                return window.plConsent.read();
            }
        } catch (e) { /* fall through */ }
        const raw = getCookie('pl_consent');
        if (!raw) return null;
        try { return JSON.parse(raw); } catch (e) { return null; }
    }

    function applyConsent(state) {
        marketingGranted = !!(state && state.m);
        allKeys().forEach((name) => {
            const legacy = getCookie(name);
            if (legacy) {
                if (!memoryStore[name]) memoryStore[name] = legacy;
                deleteCookie(name);
            }
            if (marketingGranted) {
                const v = memoryStore[name] || sessionRead(name);
                if (v) {
                    memoryStore[name] = v;
                    sessionWrite(name, v);
                }
            } else {
                sessionRemove(name);
            }
        });
    }

    function listenConsent() {
        document.addEventListener('pl_consent_update', (e) => {
            applyConsent((e && e.detail) || readConsent());
        });
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
        // Мова сторінки (cs|en) явно — сервер віддає їй пріоритет (CZ/EN у KeyCRM, /thank-you/ vs /en/thank-you/).
        if (!hasNonEmpty(formData, 'lang')) {
            setField(formData, 'lang', IS_EN ? 'en' : 'cs');
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

    /**
     * Prefill text only for Google Ads visitors (gclid present):
     * tagged campaign → 'Poptávka z Google Ads: <tag>'; gclid without tag → generic.
     * No gclid (organic/direct, even on /internet-shop/ or /corporate-website/) → nothing.
     */
    function messengerText() {
        if (!read('_prm_gclid')) return '';
        const tag = campaignTag();
        if (tag) return MESSAGE_PREFIX + tag;
        return MESSAGE_GENERIC;
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
        const text = messengerText();
        if (!text) return;
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

    /**
     * contact_click: WhatsApp / Telegram / e-mail links. One delegated listener on
     * `document`, attached as soon as this script runs (not behind the consent
     * banner), so clicks are queued in dataLayer even before GTM loads.
     */
    function contactChannel(link) {
        const h = (link.getAttribute('href') || '').trim().toLowerCase();
        if (h.startsWith('mailto:')) return 'email';
        if (/^(https?:)?\/\/(www\.)?(wa\.me|api\.whatsapp\.com)\//.test(h)) return 'whatsapp';
        if (/^(https?:)?\/\/(www\.)?t\.me\//.test(h)) return 'telegram';
        return '';
    }

    function trackContactClicks() {
        document.addEventListener('click', (e) => {
            const link = e.target && e.target.closest && e.target.closest('a[href]');
            if (!link) return;
            const channel = contactChannel(link);
            if (!channel) return;
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({ event: 'contact_click', channel: channel });
        }, { capture: true, passive: true });
    }

    trackContactClicks();
    listenConsent();
    applyConsent(readConsent());
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
        messengerText: messengerText,
    };
})();
