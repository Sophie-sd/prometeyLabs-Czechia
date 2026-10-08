/* /web-development/: currency switch (EUR / CZK orientation), portfolio carousel, demo CMS tabs.
   Screen scroll-on-hover for case shots lives in js/portfolio-screen-scroll.js. */
(function () {
    'use strict';

    var root = document.getElementById('plWebRoot');
    if (!root) return;

    var CUR_KEY = 'pl-web-cur';

    /* EUR is the canonical price; CZK is an orientation at the calculator rate.
       Both strings are rendered server-side; the switch only toggles [hidden]. */
    function initCurrency() {
        var buttons = Array.prototype.slice.call(root.querySelectorAll('[data-pl-web-cur-btn]'));
        if (!buttons.length) return;

        function apply(cur) {
            if (cur !== 'czk') cur = 'eur';
            Array.prototype.forEach.call(root.querySelectorAll('[data-pl-web-cur]'), function (el) {
                el.hidden = el.getAttribute('data-pl-web-cur') !== cur;
            });
            buttons.forEach(function (btn) {
                var on = btn.getAttribute('data-pl-web-cur-btn') === cur;
                btn.classList.toggle('is-on', on);
                btn.setAttribute('aria-pressed', on ? 'true' : 'false');
            });
            root.setAttribute('data-pl-web-currency', cur);
        }

        buttons.forEach(function (btn) {
            btn.addEventListener('click', function () {
                var cur = btn.getAttribute('data-pl-web-cur-btn');
                apply(cur);
                try { window.localStorage.setItem(CUR_KEY, cur); } catch (e) { /* storage blocked */ }
            });
        });

        var saved = null;
        try { saved = window.localStorage.getItem(CUR_KEY); } catch (e) { saved = null; }
        if (saved === 'czk') apply('czk');
    }

    function initCarousel() {
        var section = root.querySelector('[data-pl-web-portfolio]');
        if (!section) return;
        var track = section.querySelector('[data-pl-web-track]');
        var prev = section.querySelector('[data-pl-web-prev]');
        var next = section.querySelector('[data-pl-web-next]');
        if (!track || !prev || !next) return;

        function cardStep() {
            var card = track.querySelector('.pl-web__work-card');
            if (!card) return 378;
            var styles = window.getComputedStyle(track);
            var gap = parseFloat(styles.columnGap || styles.gap || '20') || 20;
            return card.getBoundingClientRect().width + gap;
        }

        function scrollByDir(dir) {
            track.scrollBy({ left: dir * cardStep(), behavior: 'smooth' });
        }

        prev.addEventListener('click', function () { scrollByDir(-1); });
        next.addEventListener('click', function () { scrollByDir(1); });
    }

    /* Demo CMS window: WAI-ARIA tabs (roving tabindex, arrows/Home/End).
       No JS -> first pane visible via [hidden] on the rest. */
    function initCms(screen) {
        var tabs = Array.prototype.slice.call(screen.querySelectorAll('[data-pl-web-cms-tab]'));
        var panes = Array.prototype.slice.call(screen.querySelectorAll('[data-pl-web-cms-pane]'));
        var ind = screen.querySelector('[data-pl-web-cms-ind]');
        if (!tabs.length || tabs.length !== panes.length) return;

        var current = 0;
        tabs.forEach(function (tab, i) {
            if (tab.getAttribute('aria-selected') === 'true') current = i;
        });

        function placeIndicator() {
            if (!ind) return;
            var tab = tabs[current];
            ind.style.height = tab.offsetHeight + 'px';
            ind.style.transform = 'translate3d(0,' + tab.offsetTop + 'px,0)';
        }

        function select(index, focus) {
            if (index < 0) index = tabs.length - 1;
            if (index >= tabs.length) index = 0;
            current = index;
            tabs.forEach(function (tab, i) {
                var on = i === index;
                tab.classList.toggle('is-on', on);
                tab.setAttribute('aria-selected', on ? 'true' : 'false');
                tab.tabIndex = on ? 0 : -1;
                panes[i].classList.toggle('is-on', on);
                panes[i].setAttribute('aria-hidden', on ? 'false' : 'true');
            });
            if (focus) tabs[index].focus();
            placeIndicator();
        }

        // Enhance: keep all panes in layout (height lock), visibility handled by CSS.
        panes.forEach(function (pane) { pane.hidden = false; });
        screen.classList.add('is-js');

        tabs.forEach(function (tab, i) {
            tab.addEventListener('click', function () { select(i, false); });
            tab.addEventListener('keydown', function (e) {
                var key = e.key;
                if (key === 'ArrowDown' || key === 'ArrowRight') {
                    e.preventDefault();
                    select(current + 1, true);
                } else if (key === 'ArrowUp' || key === 'ArrowLeft') {
                    e.preventDefault();
                    select(current - 1, true);
                } else if (key === 'Home') {
                    e.preventDefault();
                    select(0, true);
                } else if (key === 'End') {
                    e.preventDefault();
                    select(tabs.length - 1, true);
                }
            });
        });

        // First placement without animation (no slide-in on load).
        if (ind) ind.style.transition = 'none';
        select(current, false);
        if (ind) {
            void ind.offsetHeight;
            ind.style.transition = '';
        }

        // Re-measure on resize / late webfont swap (tab height changes with font metrics).
        var t = 0;
        window.addEventListener('resize', function () {
            window.clearTimeout(t);
            t = window.setTimeout(placeIndicator, 150);
        }, { passive: true });
        if (document.fonts && document.fonts.ready) {
            document.fonts.ready.then(placeIndicator);
        }
    }

    initCurrency();
    initCarousel();
    Array.prototype.forEach.call(root.querySelectorAll('[data-pl-web-cms]'), initCms);
})();
