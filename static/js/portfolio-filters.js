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
    var desktopMq = window.matchMedia('(min-width: 1024px)');
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
    }

    /* Height the bar will have once stuck (measured off-screen-free: class toggled within one frame). */
    function measureStuckH() {
        if (!bar || stuck) {
            return stuckBarH;
        }
        bar.classList.add('is-stuck');
        stuckBarH = bar.offsetHeight || stuckBarH;
        bar.classList.remove('is-stuck');
        return stuckBarH;
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

    /* Rare full re-evaluation (init, resize, header change, filter) — NOT on scroll. */
    function onScroll() {
        if (!raf) {
            raf = window.requestAnimationFrame(function () {
                updateSticky();
                bindStickyIo();
            });
        }
    }

    /*
     * Scroll-time sticky state comes from IntersectionObserver only (no per-frame layout reads):
     * - slot crosses the header line  -> slotAbove
     * - end sentinel crosses header+bar line -> endBelow
     */
    var slotAbove = false;
    var endBelow = true;
    var stickyIo = [];
    var boundFor = '';

    function bindStickyIo() {
        if (!slot || !bar || typeof window.IntersectionObserver !== 'function') {
            return;
        }
        var key = headerH + ':' + stuckBarH;
        if (key === boundFor) {
            return;
        }
        boundFor = key;
        stickyIo.forEach(function (o) { o.disconnect(); });
        stickyIo = [];
        var a = new IntersectionObserver(function (entries) {
            var e = entries[entries.length - 1];
            slotAbove = e.boundingClientRect.top < e.rootBounds.top;
            setStuck(slotAbove && endBelow);
        }, { rootMargin: '-' + headerH + 'px 0px 0px 0px', threshold: [0, 1] });
        a.observe(slot);
        stickyIo.push(a);
        if (endMark) {
            var b = new IntersectionObserver(function (entries) {
                var e = entries[entries.length - 1];
                endBelow = e.boundingClientRect.top > e.rootBounds.top;
                setStuck(slotAbove && endBelow);
            }, { rootMargin: '-' + (headerH + stuckBarH) + 'px 0px 0px 0px', threshold: [0, 1] });
            b.observe(endMark);
            stickyIo.push(b);
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

    /* Programmatic glide finished: let brand-snap play what is on screen (no fake scroll event). */
    function nudgeMotion() {
        document.dispatchEvent(new CustomEvent('pf:autoscroll-end'));
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

    /* The user took over (wheel/touch/keys) during the glide: stop owning the scroll — never pull back. */
    var userTookOver = false;

    function onUserScrollInput() {
        if (html.hasAttribute('data-pf-autoscroll')) {
            userTookOver = true;
            endAutoScroll();
        }
    }

    window.addEventListener('wheel', onUserScrollInput, { passive: true });
    window.addEventListener('touchstart', onUserScrollInput, { passive: true });
    window.addEventListener('keydown', onUserScrollInput);

    function endAutoScroll() {
        window.clearTimeout(autoTimer);
        window.removeEventListener('scrollend', endAutoScroll);
        /* Settle: if layout shifted during the glide (header/bar resize), fix the last px once. */
        if (scrollTarget && !userTookOver && html.hasAttribute('data-pf-autoscroll')) {
            var fix = targetY(scrollTarget);
            if (Math.abs(fix - window.pageYOffset) > 3) {
                window.scrollTo(0, fix);
            }
        }
        scrollTarget = null;
        if (html.hasAttribute('data-pf-autoscroll')) {
            html.removeAttribute('data-pf-autoscroll');
            nudgeMotion();
        }
    }

    /* Smoothly bring the first result just below header + stuck bar. */
    var scrollTarget = null;

    function targetY(target) {
        var y = target.getBoundingClientRect().top + window.pageYOffset - measureHeader() - measureStuckH() - GAP;
        return Math.max(0, Math.round(y));
    }

    function scrollToResults() {
        var target = firstResult();
        if (!target) {
            return;
        }
        var y = targetY(target);
        if (Math.abs(y - window.pageYOffset) < 2) {
            return;
        }
        if (prm.matches) {
            window.scrollTo(0, y);
            return;
        }
        html.setAttribute('data-pf-autoscroll', '');
        userTookOver = false;
        scrollTarget = target;
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
        onScroll();
    }

    buttons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            var wasStuck = stuck;
            /* Desktop: hero chips and stuck-bar chips both glide to the first match. */
            apply(btn.getAttribute('data-pf-filter'), { scroll: wasStuck || desktopMq.matches });
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
    measureStuckH();
    bindStickyIo();
}());

/* Floating chat button must never sit on top of the filter chips: while any
   visible chip overlaps the FAB, fade the FAB out (portfolio page only). */
(function () {
    'use strict';
    var chips = document.querySelectorAll('[data-pf-bar-list] .pfg-filter');
    if (!chips.length) return;
    var fabSel = '.contact-widget__toggle, .mobile-contact-fab';
    var root = document.documentElement;
    var ticking = false;
    function hit(a, b) {
        return a.width && b.width && a.left < b.right + 8 && a.right > b.left - 8 &&
            a.top < b.bottom + 8 && a.bottom > b.top - 8;
    }
    function check() {
        ticking = false;
        var fabs = document.querySelectorAll(fabSel), over = false;
        for (var i = 0; i < fabs.length && !over; i++) {
            var f = fabs[i].getBoundingClientRect();
            if (!f.width) continue;
            for (var j = 0; j < chips.length; j++) {
                if (hit(chips[j].getBoundingClientRect(), f)) { over = true; break; }
            }
        }
        root.classList.toggle('pfg-fab-dodge', over);
    }
    function queue() { if (!ticking) { ticking = true; requestAnimationFrame(check); } }
    /* Only measure while the in-hero chips are on screen (IO-gated; no work elsewhere on the page). */
    var slot = document.querySelector('[data-pf-bar-slot]');
    var listening = false;
    function listen(on) {
        if (on === listening) { return; }
        listening = on;
        if (on) {
            window.addEventListener('scroll', queue, { passive: true });
            queue();
        } else {
            window.removeEventListener('scroll', queue);
            root.classList.remove('pfg-fab-dodge');
        }
    }
    if (slot && typeof window.IntersectionObserver === 'function') {
        new IntersectionObserver(function (entries) {
            listen(entries[entries.length - 1].isIntersecting);
        }).observe(slot);
    } else {
        listen(true);
    }
    window.addEventListener('resize', queue);
    queue();
})();
