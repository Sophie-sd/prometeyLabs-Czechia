/**
 * Portfolio filters — Figma 8ujBKCbHGm159yeTf0aObm (0:266 / 0:47).
 * - Client-side filter by the real `PortfolioProject.category` (data-category),
 *   URL state ?category=<key> (replaceState), empty state + reset.
 * - Sticky bar: the pills stick under the fixed header (live height in
 *   --pfg-header-h, bar height in --pfg-bar-h); the slot keeps its height so the
 *   page never jumps. Released after the project list ends.
 * - Every filter change replays the card entrance (portfolio-brand-snap.js owns
 *   the motion; we send 'pf:snap-reset' and nudge scroll so it re-measures).
 */
(function () {
    'use strict';

    var ALL = 'all';
    var PARAM = 'category';
    var GAP = 16;

    var root = document.querySelector('[data-pf-filters]');
    var list = document.querySelector('[data-portfolio-snap]');
    if (!root || !list) {
        return;
    }

    var html = document.documentElement;
    var buttons = Array.prototype.slice.call(root.querySelectorAll('[data-pf-filter]'));
    var panels = Array.prototype.slice.call(list.querySelectorAll('[data-project-snap]'));
    var empty = list.querySelector('[data-pf-empty]');
    var slot = root.querySelector('[data-pf-bar-slot]');
    var bar = root.querySelector('[data-pf-bar]');
    var barList = root.querySelector('[data-pf-bar-list]');
    var endMark = list.querySelector('[data-pf-bar-end]');
    var header = document.querySelector('header') || document.querySelector('.header');
    var keys = buttons.map(function (btn) { return btn.getAttribute('data-pf-filter'); });
    var prm = window.matchMedia('(prefers-reduced-motion: reduce)');
    var mobileMq = window.matchMedia('(max-width: 767px)');
    var current = ALL;
    var stuck = false;
    var stuckBarH = 64;
    var headerH = 0;
    var raf = 0;
    var autoTimer = 0;

    /* ---------- header + sticky bar ---------- */
    function measureHeader() {
        var h = 0;
        if (header) {
            var pos = getComputedStyle(header).position;
            if (pos === 'fixed' || pos === 'sticky') {
                h = Math.max(0, Math.round(header.getBoundingClientRect().bottom));
            }
        }
        if (h !== headerH) {
            headerH = h;
            html.style.setProperty('--pfg-header-h', h + 'px');
        }
        return h;
    }

    function setStuck(on) {
        if (!slot || !bar || on === stuck) {
            return;
        }
        stuck = on;
        if (on) {
            slot.style.setProperty('--pfg-slot-h', slot.offsetHeight + 'px');
        }
        slot.classList.toggle('is-stuck', on);
        bar.classList.toggle('is-stuck', on);
        if (on) {
            stuckBarH = bar.offsetHeight || stuckBarH;
            html.style.setProperty('--pfg-bar-h', stuckBarH + 'px');
            revealActiveChip();
        } else {
            html.style.setProperty('--pfg-bar-h', '0px');
        }
        /* brand-snap caches its inset on resize; screen-scroll re-measures too. */
        window.dispatchEvent(new Event('resize'));
    }

    function updateSticky() {
        raf = 0;
        if (!slot || !bar) {
            return;
        }
        var top = measureHeader();
        var slotTop = slot.getBoundingClientRect().top;
        var endTop = endMark ? endMark.getBoundingClientRect().top : Infinity;
        setStuck(slotTop < top && endTop > top + stuckBarH);
    }

    function onScroll() {
        if (!raf) {
            raf = window.requestAnimationFrame(updateSticky);
        }
    }

    function revealActiveChip() {
        if (!barList || barList.scrollWidth <= barList.clientWidth) {
            return;
        }
        var active = barList.querySelector('.pfg-filter.is-active');
        if (active) {
            var left = active.offsetLeft - (barList.clientWidth - active.offsetWidth) / 2;
            barList.scrollTo({ left: Math.max(0, left), behavior: prm.matches ? 'auto' : 'smooth' });
        }
    }

    /* ---------- filtering ---------- */
    function matches(panel, key) {
        return key === ALL || panel.getAttribute('data-category') === key;
    }

    /* Panels hidden by CSS alone (mobile-only hides in portfolio-screen.css). */
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

    function nudgeMotion() {
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

    function firstResult() {
        for (var i = 0; i < panels.length; i += 1) {
            if (!panels[i].hidden && !cssHidden[i]) {
                return panels[i];
            }
        }
        return empty && !empty.hidden ? empty : null;
    }

    function endAutoScroll() {
        window.clearTimeout(autoTimer);
        if (html.hasAttribute('data-pf-autoscroll')) {
            html.removeAttribute('data-pf-autoscroll');
            nudgeMotion();
        }
    }

    /* Smoothly bring the first result just below header + stuck bar. */
    function scrollToResults() {
        var target = firstResult();
        if (!target) {
            return;
        }
        var y = target.getBoundingClientRect().top + window.pageYOffset - measureHeader() - stuckBarH - GAP;
        y = Math.max(0, Math.round(y));
        if (Math.abs(y - window.pageYOffset) < 2) {
            return;
        }
        if (prm.matches) {
            window.scrollTo(0, y);
            return;
        }
        html.setAttribute('data-pf-autoscroll', '');
        window.clearTimeout(autoTimer);
        autoTimer = window.setTimeout(endAutoScroll, 1400);
        if ('onscrollend' in window) {
            window.addEventListener('scrollend', endAutoScroll, { once: true });
        }
        window.scrollTo({ top: y, behavior: 'smooth' });
    }

    function apply(key, opts) {
        opts = opts || {};
        if (keys.indexOf(key) === -1) {
            key = ALL;
        }
        current = key;
        buttons.forEach(function (btn) {
            var on = btn.getAttribute('data-pf-filter') === key;
            btn.classList.toggle('is-active', on);
            btn.setAttribute('aria-pressed', on ? 'true' : 'false');
        });

        var shown = [];
        var visible = 0;
        panels.forEach(function (panel, i) {
            var show = matches(panel, key);
            panel.hidden = !show;
            if (show) {
                shown.push(panel);
                if (!cssHidden[i]) {
                    /* Chessboard follows the visible order (same rule as get_layout_modifier). */
                    panel.classList.toggle('pf-snap--flip', visible % 2 === 1);
                    visible += 1;
                }
            }
        });

        if (empty) {
            empty.hidden = visible !== 0;
        }
        list.classList.toggle('is-filtered', key !== ALL);
        if (opts.url !== false) {
            writeUrl(key);
        }

        /* Replay the entrance for every card shown under this filter. */
        if (opts.replay !== false) {
            document.dispatchEvent(new CustomEvent('pf:snap-reset', { detail: { panels: shown } }));
        }
        revealActiveChip();
        if (opts.scroll) {
            scrollToResults();
        }
        nudgeMotion();
        onScroll();
    }

    buttons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            var wasStuck = stuck;
            apply(btn.getAttribute('data-pf-filter'), { scroll: wasStuck });
        });
    });

    list.addEventListener('click', function (event) {
        var jump = event.target.closest('[data-pf-filter-jump]');
        if (jump) {
            apply(jump.getAttribute('data-pf-filter-jump'), { scroll: true });
            return;
        }
        if (event.target.closest('[data-pf-filter-reset]')) {
            apply(ALL, { scroll: true });
        }
    });

    var down = root.querySelector('[data-pf-scroll]');
    if (down) {
        down.addEventListener('click', function (event) {
            event.preventDefault();
            scrollToResults();
        });
    }

    function onBreakpoint() {
        cssHidden = cssHiddenMap();
        apply(current, { url: false, replay: false });
    }

    if (typeof mobileMq.addEventListener === 'function') {
        mobileMq.addEventListener('change', onBreakpoint);
    } else {
        mobileMq.addListener(onBreakpoint);
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    if (typeof window.ResizeObserver === 'function') {
        var ro = new ResizeObserver(function () {
            if (stuck && bar) {
                stuckBarH = bar.offsetHeight || stuckBarH;
                html.style.setProperty('--pfg-bar-h', stuckBarH + 'px');
            }
            onScroll();
        });
        if (header) {
            ro.observe(header);
        }
        if (bar) {
            ro.observe(bar);
        }
    }
    if (header && typeof window.MutationObserver === 'function') {
        /* Header that hides/shows via class or inline transform. */
        new MutationObserver(onScroll).observe(header, { attributes: true, attributeFilter: ['class', 'style'] });
    }

    measureHeader();
    var initial = new URL(window.location.href).searchParams.get(PARAM) || ALL;
    if (initial !== ALL) {
        apply(initial, { url: keys.indexOf(initial) === -1 });
    }
    updateSticky();
}());
