/**
 * Enhanced Conversions phone bridge for Google Ads (via GTM).
 *
 * Saves a normalized E.164 phone to sessionStorage (`ec_phone`) before
 * redirect to /thank-you/, so GTM User-Provided Data can hash and send it.
 * No listeners on load — call saveFromRaw only after a successful lead redirect.
 * Default country code is +420 (Czech site, cs/en), e.g. "777 123 456" → "+420777123456".
 */
(function () {
    'use strict';

    var STORAGE_KEY = 'ec_phone';

    function normalizePhone(raw) {
        if (!raw) return null;
        var digits = String(raw).replace(/[^\d+]/g, '');
        if (!digits) return null;
        // Already international: keep as is (strip any extra '+').
        if (digits.indexOf('+') === 0) return '+' + digits.replace(/\+/g, '');
        // International "00" prefix (e.g. 00420…) → "+".
        if (digits.indexOf('00') === 0) return '+' + digits.slice(2);
        // Czech number already with country code but without "+" (420 + 9 digits).
        if (digits.indexOf('420') === 0 && digits.length === 12) return '+' + digits;
        // Default for the Czech site (cs/en): +420, same as phone-mask-intl.js.
        return '+420' + digits;
    }

    function saveFromRaw(raw) {
        var phone = normalizePhone(raw);
        if (!phone) return false;
        try {
            sessionStorage.setItem(STORAGE_KEY, phone);
            return true;
        } catch (err) {
            return false;
        }
    }

    window.ECPhone = {
        normalizePhone: normalizePhone,
        saveFromRaw: saveFromRaw,
        STORAGE_KEY: STORAGE_KEY
    };
})();

window.ec_stored_phone = (function () {
    try {
        return sessionStorage.getItem('ec_phone') || '';
    } catch (e) {
        return '';
    }
})();
