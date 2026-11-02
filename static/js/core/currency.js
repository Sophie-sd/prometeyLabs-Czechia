(function () {
    'use strict';

    document.addEventListener('submit', function (event) {
        var form = event.target;
        if (!form || !form.classList || !form.classList.contains('fx-switch')) {
            return;
        }
        try {
            sessionStorage.setItem('pl_fx_switched', '1');
        } catch (err) {
            /* iOS private mode */
        }
    });

    // Safari restores the pre-switch page from bfcache; reload so prices match the cookie.
    window.addEventListener('pageshow', function (event) {
        if (!event.persisted || !document.querySelector('.fx-switch')) {
            return;
        }
        var flag = '';
        try {
            flag = sessionStorage.getItem('pl_fx_switched') || '';
        } catch (err) {
            return;
        }
        if (!flag) {
            return;
        }
        try {
            sessionStorage.removeItem('pl_fx_switched');
        } catch (err) {
            /* ignore */
        }
        window.location.reload();
    });
}());
