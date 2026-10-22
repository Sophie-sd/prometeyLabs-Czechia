/* Payment page enhancements: countdown timer that disables the pay-button
   when expired. No inline JS in templates — all behavior is wired via
   data-* attributes. */
(function () {
    'use strict';

    function pad(n) {
        return String(n).padStart(2, '0');
    }

    function formatRemaining(ms) {
        if (ms <= 0) return '00:00:00';
        var totalSeconds = Math.floor(ms / 1000);
        var hours = Math.floor(totalSeconds / 3600);
        var minutes = Math.floor((totalSeconds % 3600) / 60);
        var seconds = totalSeconds % 60;
        return pad(hours) + ':' + pad(minutes) + ':' + pad(seconds);
    }

    function initCountdown(el) {
        var iso = el.getAttribute('data-expires-at');
        if (!iso) return;
        var expiresAt = new Date(iso).getTime();
        if (isNaN(expiresAt)) return;

        var disableSel = el.getAttribute('data-disable');
        var expiredText = el.getAttribute('data-expired-text') || 'TIME IS UP';
        var disableTarget = disableSel ? document.querySelector(disableSel) : null;
        var timerId = null;

        function tick() {
            var dist = expiresAt - Date.now();
            if (dist <= 0) {
                if (timerId) window.clearInterval(timerId);
                el.textContent = expiredText;
                el.classList.add('expired');
                if (disableTarget) {
                    disableTarget.disabled = true;
                    disableTarget.setAttribute('aria-disabled', 'true');
                }
                return;
            }
            el.textContent = formatRemaining(dist);
        }

        tick();
        timerId = window.setInterval(tick, 1000);
    }

    function init() {
        var nodes = document.querySelectorAll('[data-countdown]');
        for (var i = 0; i < nodes.length; i++) {
            initCountdown(nodes[i]);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
