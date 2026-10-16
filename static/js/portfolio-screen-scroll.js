/**
 * Portfolio screen scroll — рахує дистанцію скролу знімка головної сторінки
 * (--pf-scroll-y / --pf-scroll-ms) і паузить mobile ping-pong поза viewport.
 * CSS (portfolio-screen.css) відповідає за сам рух (:hover / .is-motion).
 */
(function () {
    'use strict';

    var HOVER_SPEED_PX_S = 160;
    var MOBILE_SPEED_PX_S = 110;
    var MOBILE_MOVE_SHARE = 0.82; // частка циклу на рух; решта — паузи на краях
    var RESIZE_DEBOUNCE_MS = 200;

    var prm = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (prm.matches) {
        return;
    }

    var touchMq = window.matchMedia('(hover: none), (max-width: 767px)');
    var assets = Array.prototype.slice.call(document.querySelectorAll('[data-pf-screen]'));
    if (!assets.length) {
        return;
    }

    function computeFor(asset) {
        var img = asset.querySelector('[data-pf-shot]');
        if (!img) {
            return;
        }
        var containerH = asset.clientHeight;
        var imgH = img.offsetHeight;
        var dist = Math.max(0, Math.round(imgH - containerH));

        asset.style.setProperty('--pf-scroll-y', dist > 0 ? '-' + dist + 'px' : '0px');

        if (dist <= 0) {
            asset.style.setProperty('--pf-scroll-ms', '0ms');
            return;
        }

        var ms;
        if (touchMq.matches) {
            var moveMs = (2 * dist / MOBILE_SPEED_PX_S) * 1000;
            ms = Math.max(1, Math.round(moveMs / MOBILE_MOVE_SHARE));
        } else {
            ms = Math.max(1, Math.round((dist / HOVER_SPEED_PX_S) * 1000));
        }
        asset.style.setProperty('--pf-scroll-ms', ms + 'ms');
    }

    function computeAll() {
        assets.forEach(computeFor);
    }

    assets.forEach(function (asset) {
        var img = asset.querySelector('[data-pf-shot]');
        if (!img) {
            return;
        }
        if (img.complete) {
            computeFor(asset);
        } else {
            img.addEventListener('load', function () {
                computeFor(asset);
            }, { once: true });
        }
        // Desktop: картка показує легке прев'ю (srcset); повний знімок для hover-скролу
        // вантажиться лише при першому наведенні, далі дистанцію перераховано.
        if (img.hasAttribute('data-pf-full')) {
            // Swap only after a real hover dwell (not when cards slide under a still cursor while scrolling).
            var dwell = 0;
            var swap = function () {
                if (touchMq.matches || !img.hasAttribute('srcset') || !asset.matches(':hover')) {
                    return;
                }
                img.addEventListener('load', function () {
                    computeFor(asset);
                }, { once: true });
                img.loading = 'eager';
                img.removeAttribute('sizes');
                img.removeAttribute('srcset');
                img.src = img.getAttribute('data-pf-full');
            };
            asset.addEventListener('mouseenter', function () {
                if (!img.hasAttribute('srcset')) {
                    return;
                }
                window.clearTimeout(dwell);
                dwell = window.setTimeout(swap, 450);
            });
            asset.addEventListener('mouseleave', function () {
                window.clearTimeout(dwell);
            });
        }
        // Desktop: перерахунок після завершення shrink-анімації ширини (brand-snap).
        asset.addEventListener('transitionend', function (event) {
            if (event.target === asset && event.propertyName === 'width') {
                computeFor(asset);
            }
        });
    });

    var resizeTimer = 0;
    window.addEventListener('resize', function () {
        window.clearTimeout(resizeTimer);
        resizeTimer = window.setTimeout(computeAll, RESIZE_DEBOUNCE_MS);
    }, { passive: true });

    // Mobile/touch: пауза ping-pong поза viewport — один IO на всі картки.
    var io = null;

    function bindMobileIo() {
        if (io) {
            io.disconnect();
            io = null;
        }
        if (!touchMq.matches) {
            assets.forEach(function (asset) {
                asset.classList.remove('is-motion');
            });
            return;
        }
        io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                entry.target.classList.toggle('is-motion', entry.isIntersecting);
            });
        }, { threshold: 0.25 });
        assets.forEach(function (asset) {
            io.observe(asset);
        });
    }

    bindMobileIo();
    computeAll();

    if (typeof touchMq.addEventListener === 'function') {
        touchMq.addEventListener('change', function () {
            bindMobileIo();
            computeAll();
        });
    }
})();
