/**
 * Portfolio filters — Figma 8ujBKCbHGm159yeTf0aObm (0:266 / 0:47).
 * Client-side filter by the real `PortfolioProject.category` field (data-category).
 * URL state: ?category=<key> (replaceState, no reload). Empty state + reset.
 * Card motion stays in portfolio-brand-snap.js: after a change we only fire
 * scroll/resize so it (and portfolio-screen-scroll.js) re-measure visible cards.
 */
(function () {
    'use strict';

    var ALL = 'all';
    var PARAM = 'category';

    var root = document.querySelector('[data-pf-filters]');
    var list = document.querySelector('[data-portfolio-snap]');
    if (!root || !list) {
        return;
    }

    var buttons = Array.prototype.slice.call(root.querySelectorAll('[data-pf-filter]'));
    var panels = Array.prototype.slice.call(list.querySelectorAll('[data-project-snap]'));
    var empty = list.querySelector('[data-pf-empty]');
    var keys = buttons.map(function (btn) { return btn.getAttribute('data-pf-filter'); });
    var prm = window.matchMedia('(prefers-reduced-motion: reduce)');
    var mobileMq = window.matchMedia('(max-width: 767px)');
    var current = ALL;

    function matches(panel, key) {
        return key === ALL || panel.getAttribute('data-category') === key;
    }

    /* Panels hidden by CSS alone (e.g. mobile-only hides in portfolio-screen.css). */
    function cssHiddenMap() {
        var saved = panels.map(function (panel) { return panel.hidden; });
        panels.forEach(function (panel) { panel.hidden = false; });
        var map = panels.map(function (panel) {
            return window.getComputedStyle(panel).display === 'none';
        });
        panels.forEach(function (panel, i) { panel.hidden = saved[i]; });
        return map;
    }

    var cssHidden = cssHiddenMap();

    function updateCounts() {
        keys.forEach(function (key) {
            var out = root.querySelector('[data-pf-count="' + key + '"]');
            if (!out) {
                return;
            }
            var n = 0;
            panels.forEach(function (panel, i) {
                if (!cssHidden[i] && matches(panel, key)) {
                    n += 1;
                }
            });
            out.textContent = String(n);
        });
    }

    function nudgeMotion() {
        window.dispatchEvent(new Event('resize'));
        window.dispatchEvent(new Event('scroll'));
    }

    function writeUrl(key) {
        if (!window.history || typeof window.history.replaceState !== 'function') {
            return;
        }
        var url = new URL(window.location.href);
        if (key === ALL) {
            url.searchParams.delete(PARAM);
        } else {
            url.searchParams.set(PARAM, key);
        }
        window.history.replaceState(window.history.state, '', url.pathname + url.search + url.hash);
    }

    function apply(key, opts) {
        if (keys.indexOf(key) === -1) {
            key = ALL;
        }
        current = key;
        buttons.forEach(function (btn) {
            var on = btn.getAttribute('data-pf-filter') === key;
            btn.classList.toggle('is-active', on);
            btn.setAttribute('aria-pressed', on ? 'true' : 'false');
        });

        var visible = 0;
        panels.forEach(function (panel, i) {
            var show = matches(panel, key);
            panel.hidden = !show;
            if (show && !cssHidden[i]) {
                /* Chessboard follows the visible order (same rule as get_layout_modifier). */
                panel.classList.toggle('pf-snap--flip', visible % 2 === 1);
                visible += 1;
            }
        });

        if (empty) {
            empty.hidden = visible !== 0;
        }
        list.classList.toggle('is-filtered', key !== ALL);
        if (!opts || opts.url !== false) {
            writeUrl(key);
        }
        nudgeMotion();
    }

    function scrollToFilters() {
        var top = root.getBoundingClientRect().top + window.pageYOffset;
        var nav = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nav-height')) || 60;
        window.scrollTo({ top: Math.max(0, top - nav - 16), behavior: prm.matches ? 'auto' : 'smooth' });
    }

    buttons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            apply(btn.getAttribute('data-pf-filter'));
        });
    });

    list.addEventListener('click', function (event) {
        var jump = event.target.closest('[data-pf-filter-jump]');
        if (jump) {
            apply(jump.getAttribute('data-pf-filter-jump'));
            scrollToFilters();
            return;
        }
        if (event.target.closest('[data-pf-filter-reset]')) {
            apply(ALL);
            scrollToFilters();
        }
    });

    var down = root.querySelector('[data-pf-scroll]');
    if (down) {
        down.addEventListener('click', function (event) {
            var first = panels.filter(function (panel, i) { return !panel.hidden && !cssHidden[i]; })[0] || empty || list;
            if (!first) {
                return;
            }
            event.preventDefault();
            var nav = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nav-height')) || 60;
            var top = first.getBoundingClientRect().top + window.pageYOffset - nav;
            window.scrollTo({ top: Math.max(0, top), behavior: prm.matches ? 'auto' : 'smooth' });
        });
    }

    function onBreakpoint() {
        cssHidden = cssHiddenMap();
        updateCounts();
        apply(current, { url: false });
    }

    if (typeof mobileMq.addEventListener === 'function') {
        mobileMq.addEventListener('change', onBreakpoint);
    } else {
        mobileMq.addListener(onBreakpoint);
    }

    updateCounts();
    var initial = new URL(window.location.href).searchParams.get(PARAM) || ALL;
    if (initial !== ALL) {
        apply(initial, { url: keys.indexOf(initial) === -1 });
    }
}());
