/**
 * Google Ads GCLID & UTM Capture + first-touch landing + outbound-click tracking.
 *
 * Все, що тут зберігається у cookies (`_prm_*`) — додається у POST-дані будь-якої форми
 * (через `appendToFormData`). На сервері це потрапляє в `FormSubmission.gclid/utm_*`
 * та `extra_data.source_page / landing_page / landing_referrer`. KeyCRM-резолвер
 * використовує ці підказки, щоб атрибутувати заявку до правильної рекламної кампанії
 * (Shops / Corporate / All), навіть якщо форма заповнена в footer/контактах,
 * а перший візит був на /internet-shop/ чи /corporate-website/.
 *
 * Кліки по tel: / t.me / wa.me / m.me відправляються у dataLayer (Google Tag Manager)
 * як події `phone_click` / `messenger_click` з gclid/utm/landing — для GA4/Google Ads.
 * Для WhatsApp та Telegram-ботів автоматично дописується `?text=` з тегом кампанії,
 * щоб менеджер у CRM одразу бачив джерело.
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
            if (v) setCookie('_prm_' + p, v, COOKIE_DAYS);
        });
    }

    function captureFirstTouch() {
        if (!getCookie('_prm_landing_path')) {
            setCookie('_prm_landing_path', window.location.pathname, COOKIE_DAYS);
        }
        if (!getCookie('_prm_landing_referrer') && document.referrer) {
            try {
                const ref = new URL(document.referrer);
                if (ref.host !== window.location.host) {
                    setCookie('_prm_landing_referrer', document.referrer, COOKIE_DAYS);
                }
            } catch (e) {
                // ігноруємо невалідний referrer
            }
        }
    }

    function getTrackingData() {
        const data = {};
        TRACKING_PARAMS.forEach((p) => {
            const v = getCookie('_prm_' + p);
            if (v) data[p] = v;
        });
        LANDING_KEYS.forEach((k) => {
            const v = getCookie('_prm_' + k);
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
        const campaign = (getCookie('_prm_utm_campaign') || '').toLowerCase();
        const landing = (getCookie('_prm_landing_path') || window.location.pathname || '').toLowerCase();
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
                // Telegram передає `?text=` лише у власних `share/url` посиланнях.
                // Для звичайних посилань на профіль/бот — додаємо tag лише як подію.
                if (url.pathname.endsWith('/share/url') && !url.searchParams.has('text')) {
                    url.searchParams.set('text', text);
                    link.setAttribute('href', url.toString());
                }
            }
        } catch (e) {
            // ігноруємо
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
