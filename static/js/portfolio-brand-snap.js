/**
 * Portfolio brand-snap — proximity snap + one-way media shrink.
 * Constants from brand_snap_skill + luxury_motion --motion-reveal.
 */
(function () {
    'use strict';

    var MQ = '(min-width: 768px)';
    var SHRINK_MS = 1000;
    var TEXT_AT_MS = 580;
    var EASE = 'cubic-bezier(0.23, 1, 0.32, 1)';
    var SNAP_BAND = 0.11;
    var SNAP_BAND_PX_MIN = 56;
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
    var snapLockedOff = false;
    var scrollingUp = false;
    var touchStartY = 0;
    var snapRaf = 0;
    var zoneVisible = false;

    function isDesktop() {
        return mq.matches;
    }

    var cachedInset = 60;

    function refreshInset() {
        var raw = getComputedStyle(html).getPropertyValue('--nav-height').trim();
        var nav = parseFloat(raw) || 60;
        var probe = getComputedStyle(html).getPropertyValue('--mobile-safe-top').trim();
        cachedInset = nav + (parseFloat(probe) || 0);
    }

    function headerInset() {
        return cachedInset;
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
        var asset = panel.querySelector('[data-snap-asset]');
        var content = panel.querySelector('[data-snap-content]');
        if (!asset || !content) {
            return;
        }

        asset.style.width = '100%';
        asset.style.transition = 'none';
        void asset.offsetWidth;
        asset.style.transition = 'width ' + SHRINK_MS + 'ms ' + EASE;

        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                asset.classList.add('is-shrinking');
                asset.style.width = '';
            });
        });

        window.setTimeout(function () {
            content.classList.add('is-done');
        }, TEXT_AT_MS);

        window.setTimeout(function () {
            asset.style.width = '';
            asset.style.transition = '';
            asset.classList.add('is-shrinking', 'is-done');
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
                if (!entry.isIntersecting) {
                    return;
                }
                var panel = entry.target;
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

    function clearSnapClasses() {
        html.classList.remove('pf-snap-on', 'pf-snap-off');
        panels.forEach(function (panel) {
            panel.classList.remove('is-snap-target');
        });
    }

    function setSnapOff() {
        html.classList.remove('pf-snap-on');
        html.classList.add('pf-snap-off');
        panels.forEach(function (panel) {
            panel.classList.remove('is-snap-target');
        });
    }

    function modalOpen() {
        return document.body.classList.contains('modal-open');
    }

    function tryPlayVisible() {
        if (prm.matches) {
            return;
        }
        var vh = window.innerHeight || 1;
        panels.forEach(function (panel) {
            if (panel.getAttribute('data-done') === '1' || panel.getAttribute('data-playing') === '1') {
                return;
            }
            var rect = panel.getBoundingClientRect();
            var vis = Math.min(rect.bottom, vh) - Math.max(rect.top, 0);
            if (vis <= 0 || rect.height <= 0) {
                return;
            }
            var ratio = vis / rect.height;
            if (isDesktop()) {
                if (ratio >= playRatioFor(panel)) {
                    playDesktop(panel);
                }
            } else if (ratio >= 0.2) {
                playMobile(panel);
            }
        });
    }

    function updateSnap() {
        tryPlayVisible();
        if (!isDesktop() || prm.matches || modalOpen()) {
            clearSnapClasses();
            return;
        }

        var zone = root.getBoundingClientRect();
        var vh = window.innerHeight || 1;
        zoneVisible = zone.bottom > 0 && zone.top < vh;

        if (!zoneVisible) {
            clearSnapClasses();
            return;
        }

        var nearTop = zone.top > -Math.min(120, vh * 0.18);
        var nearBottom = zone.bottom < vh * 0.72;

        if (scrollingUp || nearTop || nearBottom) {
            snapLockedOff = true;
            setSnapOff();
            return;
        }

        if (!scrollingUp && zone.top < -80) {
            snapLockedOff = false;
        }

        if (snapLockedOff) {
            setSnapOff();
            return;
        }

        var inset = headerInset();
        var band = Math.max(SNAP_BAND_PX_MIN, vh * SNAP_BAND);
        var nearest = null;
        var nearestDist = Infinity;

        panels.forEach(function (panel) {
            if (panel.hidden) {
                return; /* filtered out by portfolio-filters.js */
            }
            var dist = Math.abs(panel.getBoundingClientRect().top - inset);
            if (dist < nearestDist) {
                nearestDist = dist;
                nearest = panel;
            }
        });

        panels.forEach(function (panel) {
            panel.classList.remove('is-snap-target');
        });

        if (nearest && nearestDist <= band) {
            nearest.classList.add('is-snap-target');
            html.classList.remove('pf-snap-off');
            html.classList.add('pf-snap-on');
        } else {
            setSnapOff();
        }
    }

    function onScroll() {
        if (snapRaf) {
            return;
        }
        snapRaf = window.requestAnimationFrame(function () {
            snapRaf = 0;
            updateSnap();
            scrollingUp = false;
        });
    }

    function onWheel(ev) {
        if (ev.deltaY < 0) {
            scrollingUp = true;
        }
    }

    function onTouchStart(ev) {
        if (ev.touches && ev.touches[0]) {
            touchStartY = ev.touches[0].clientY;
        }
    }

    function onTouchMove(ev) {
        if (!ev.touches || !ev.touches[0]) {
            return;
        }
        var dy = ev.touches[0].clientY - touchStartY;
        if (dy > 8) {
            scrollingUp = true;
        }
    }

    function applyPrm() {
        disconnectIo();
        clearSnapClasses();
        panels.forEach(finishPanel);
    }

    function boot() {
        if (prm.matches) {
            applyPrm();
            return;
        }
        bindIo();
        updateSnap();
        tryPlayVisible();
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', function () {
        refreshInset();
        onScroll();
    }, { passive: true });
    window.addEventListener('wheel', onWheel, { passive: true });
    window.addEventListener('touchstart', onTouchStart, { passive: true });
    window.addEventListener('touchmove', onTouchMove, { passive: true });

    if (typeof mq.addEventListener === 'function') {
        mq.addEventListener('change', boot);
        prm.addEventListener('change', boot);
    } else {
        mq.addListener(boot);
        prm.addListener(boot);
    }

    var bodyObserver = new MutationObserver(function () {
        if (modalOpen()) {
            snapLockedOff = true;
            clearSnapClasses();
        } else {
            snapLockedOff = false;
            updateSnap();
        }
    });
    bodyObserver.observe(document.body, { attributes: true, attributeFilter: ['class'] });

    refreshInset();
    boot();
}());
