/**
 * Enhanced Conversions phone bridge for Google Ads (via GTM).
 *
 * Saves a normalized E.164 phone to sessionStorage (`ec_phone`) before
 * redirect to /thank-you/, so GTM User-Provided Data can hash and send it.
 * No listeners on load — call saveFromRaw only after a successful lead redirect.
 */
(function () {
    'use strict';

    var STORAGE_KEY = 'ec_phone';

    function normalizePhone(raw) {
        if (!raw) return null;
        var digits = String(raw).replace(/[^\d+]/g, '');
        if (!digits) return null;
        if (digits.indexOf('+') === 0) return digits;
        if (digits.indexOf('00') === 0) return '+' + digits.slice(2);
        // CZ site: national 9-digit numbers default to +420; longer digit strings already carry a code
        if (digits.length <= 9) return '+420' + digits;
        return '+' + digits;
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
