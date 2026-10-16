/**
 * Portfolio brand-snap — one-way media shrink on scroll-in (natural scroll, no scroll-snap).
 * Snap toggling removed 2026-10-16 (owner: "scroll twice to change direction" + lag).
 * Constants from brand_snap_skill + luxury_motion --motion-reveal.
 */
(function () {
    'use strict';

    var MQ = '(min-width: 768px)';
    var SHRINK_MS = 1000;
    var TEXT_AT_MS = 580;
    var EASE = 'cubic-bezier(0.23, 1, 0.32, 1)';
    var PLAY_RATIO = 0.4;
    var PLAY_RATIO_FIRST = 0.55;
    var SETTLE_MS = SHRINK_MS + 140;

    var root = document.querySelector('[data-portfolio-snap]');
    if (!root) {
        return;
    }

    var panels = Array.prototype.slice.call(root.querySelectorAll('[data-project-snap]'));
    if (!panels.length) {
        return;
    }

    var html = document.documentElement;
    var mq = window.matchMedia(MQ);
    var prm = window.matchMedia('(prefers-reduced-motion: reduce)');
    var io = null;
    /* Latest IO ratio per panel (kept even while a programmatic scroll defers play). */
    var ratios = new Map();

    function isDesktop() {
        return mq.matches;
    }

    var cachedInset = 60;

    function refreshInset() {
        var raw = getComputedStyle(html).getPropertyValue('--nav-height').trim();
        var nav = parseFloat(raw) || 60;
        var probe = getComputedStyle(html).getPropertyValue('--mobile-safe-top').trim();
        var bar = parseFloat(getComputedStyle(html).getPropertyValue('--pfg-bar-h')) || 0;
        cachedInset = nav + (parseFloat(probe) || 0) + bar;
    }

    function headerInset() {
        return cachedInset;
    }

    /* portfolio-filters.js marks programmatic scrolls; cards play once it settles. */
    function autoScrolling() {
        return html.hasAttribute('data-pf-autoscroll');
    }

    /* Generation token: timers/rAFs of a play cancelled by a filter reset never land. */
    function genOf(panel) {
        return panel.getAttribute('data-gen') || '0';
    }

    function finishPanel(panel) {
        var asset = panel.querySelector('[data-snap-asset]');
        var content = panel.querySelector('[data-snap-content]');
        if (asset) {
            asset.style.width = '';
            asset.style.transition = '';
            asset.classList.add('is-shrinking', 'is-done');
            asset.style.willChange = '';
        }
        if (content) {
            content.classList.add('is-done');
        }
        panel.setAttribute('data-done', '1');
    }

    function playDesktop(panel) {
        if (!isDesktop() || panel.getAttribute('data-done') === '1' || panel.getAttribute('data-playing') === '1') {
            return;
        }
        panel.setAttribute('data-playing', '1');
        var gen = genOf(panel);
        var asset = panel.querySelector('[data-snap-asset]');
        var content = panel.querySelector('[data-snap-content]');
        if (!asset || !content) {
            return;
        }

        /* Compositor-only shrink: the frame keeps its layout box; clip-path + picture scale animate
           (no width transition -> no per-frame layout / layout shift while the user scrolls). */
        asset.style.setProperty('--pf-ms', SHRINK_MS + 'ms');
        asset.style.setProperty('--pf-ease', EASE);
        asset.classList.add('pf-anim');

        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                if (genOf(panel) !== gen) {
                    return;
                }
                asset.classList.add('is-shrinking');
            });
        });

        window.setTimeout(function () {
            if (genOf(panel) !== gen) {
                return;
            }
            content.classList.add('is-done');
        }, TEXT_AT_MS);

        window.setTimeout(function () {
            if (genOf(panel) !== gen) {
                return;
            }
            asset.classList.add('is-shrinking', 'is-done');
            asset.classList.remove('pf-anim');
            panel.setAttribute('data-done', '1');
        }, SETTLE_MS);
    }

    function playMobile(panel) {
        if (isDesktop() || panel.getAttribute('data-done') === '1') {
            return;
        }
        var asset = panel.querySelector('[data-snap-asset]');
        var content = panel.querySelector('[data-snap-content]');
        if (asset) {
            asset.style.width = '';
            asset.style.transition = '';
            asset.classList.add('is-done');
        }
        if (content) {
            content.classList.add('is-done');
        }
        panel.setAttribute('data-done', '1');
    }

    function playRatioFor(panel) {
        var idx = parseInt(panel.getAttribute('data-index'), 10);
        return idx === 0 ? PLAY_RATIO_FIRST : PLAY_RATIO;
    }

    function disconnectIo() {
        if (io) {
            io.disconnect();
            io = null;
        }
    }

    function bindIo() {
        disconnectIo();
        if (prm.matches) {
            return;
        }

        var desktop = isDesktop();
        var options = desktop
            ? {
                threshold: [0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75],
                rootMargin: '0px 0px -10% 0px'
            }
            : {
                threshold: 0.2,
                rootMargin: '0px 0px -8% 0px'
            };

        io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                var panel = entry.target;
                if (!entry.isIntersecting) {
                    ratios.delete(panel);
                    return;
                }
                ratios.set(panel, entry.intersectionRatio);
                if (autoScrolling()) {
                    return;
                }
                if (panel.getAttribute('data-done') === '1') {
                    io.unobserve(panel);
                    return;
                }
                if (isDesktop()) {
                    if (entry.intersectionRatio >= playRatioFor(panel)) {
                        playDesktop(panel);
                        io.unobserve(panel);
                    }
                } else {
                    playMobile(panel);
                    io.unobserve(panel);
                }
            });
        }, options);

        panels.forEach(function (panel) {
            if (panel.getAttribute('data-done') !== '1') {
                io.observe(panel);
            }
        });
    }

    /* Play cards the IO reported as visible (no layout reads; used after a programmatic scroll). */
    function tryPlayVisible() {
        if (prm.matches || autoScrolling()) {
            return;
        }
        ratios.forEach(function (ratio, panel) {
            if (panel.hidden || panel.getAttribute('data-done') === '1' || panel.getAttribute('data-playing') === '1') {
                return;
            }
            if (isDesktop()) {
                if (ratio >= playRatioFor(panel)) {
                    playDesktop(panel);
                }
            } else if (ratio >= 0.2) {
                playMobile(panel);
            }
        });
    }

    function applyPrm() {
        disconnectIo();
        panels.forEach(finishPanel);
    }

    /* --pf-k = panel width / final frame width: the pre-play picture scale (desktop CSS). */
    function measureK() {
        if (!isDesktop()) {
            return;
        }
        panels.forEach(function (panel) {
            var pic = panel.querySelector('[data-snap-asset] picture');
            var w = pic ? pic.offsetWidth : 0;
            if (w > 0) {
                panel.style.setProperty('--pf-k', String(panel.clientWidth / w));
            }
        });
    }

    var kRaf = 0;
    window.addEventListener('resize', function () {
        if (!kRaf) {
            kRaf = requestAnimationFrame(function () {
                kRaf = 0;
                measureK();
            });
        }
    }, { passive: true });

    function boot() {
        measureK();
        if (prm.matches) {
            applyPrm();
            return;
        }
        bindIo();
    }

    window.addEventListener('resize', refreshInset, { passive: true });
    /* portfolio-filters.js: programmatic glide finished -> play what is on screen now. */
    document.addEventListener('pf:autoscroll-end', tryPlayVisible);

    if (typeof mq.addEventListener === 'function') {
        mq.addEventListener('change', boot);
        prm.addEventListener('change', boot);
    } else {
        mq.addListener(boot);
        prm.addListener(boot);
    }

    /*
     * Replay after a filter change (portfolio-filters.js → 'pf:snap-reset').
     * Back to the pre-play state with transitions off for one reflow (no reverse
     * fade), then re-observed: in-viewport cards play on the next scroll tick
     * (dispatched by the filter), the rest on scroll-in — same timings as first play.
     */
    function resetPanel(panel) {
        var asset = panel.querySelector('[data-snap-asset]');
        var content = panel.querySelector('[data-snap-content]');
        panel.setAttribute('data-gen', String((parseInt(genOf(panel), 10) || 0) + 1));
        panel.classList.add('pf-snap--resetting');
        panel.removeAttribute('data-done');
        panel.removeAttribute('data-playing');
        if (asset) {
            asset.classList.remove('is-shrinking', 'is-done', 'pf-anim');
            asset.style.width = '';
            asset.style.transition = '';
            asset.style.willChange = '';
        }
        if (content) {
            content.classList.remove('is-done');
        }
    }

    document.addEventListener('pf:snap-reset', function (event) {
        var list = (event.detail && event.detail.panels) || panels;
        if (prm.matches) {
            list.forEach(finishPanel);
            return;
        }
        if (!io) {
            bindIo();
        }
        /* Batch: write all, ONE forced layout for the whole set, then re-arm the observer. */
        list.forEach(resetPanel);
        void root.offsetWidth;
        list.forEach(function (panel) {
            panel.classList.remove('pf-snap--resetting');
            ratios.delete(panel);
            if (io) {
                io.unobserve(panel);
                io.observe(panel);
            }
        });
    });

    refreshInset();
    boot();
}());
