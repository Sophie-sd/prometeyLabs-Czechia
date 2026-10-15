(function () {
    'use strict';

    var root = document.getElementById('plShopRoot');
    if (!root) return;

    var reduceMotion = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function initReveal() {
        var els = root.querySelectorAll('[data-reveal]');
        if (!els.length) return;

        // CZ: never hide content behind a scroll observer (full-page captures, slow devices).
        if (reduceMotion || true) return;

        els.forEach(function (el) {
            if (el.__rev) return;
            el.__rev = 1;
            el.style.opacity = '0';
            el.style.transform = 'translateY(28px)';
            el.style.transition = 'opacity .75s cubic-bezier(.2,.7,.2,1), transform .75s cubic-bezier(.2,.7,.2,1)';
        });

        function reveal(el) {
            el.style.opacity = '1';
            el.style.transform = 'none';
        }

        if ('IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (ents) {
                ents.forEach(function (en) {
                    if (en.isIntersecting) {
                        reveal(en.target);
                        io.unobserve(en.target);
                    }
                });
            }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });

            els.forEach(function (el) {
                if (!el.__obs) {
                    el.__obs = 1;
                    io.observe(el);
                }
            });

            requestAnimationFrame(function () {
                var vh = window.innerHeight || 800;
                els.forEach(function (el) {
                    var r = el.getBoundingClientRect();
                    if (r.top < vh * 0.95) {
                        reveal(el);
                        io.unobserve(el);
                    }
                });
            });
        } else {
            els.forEach(reveal);
        }
    }

    function initCalcPkgLinks() {
        root.querySelectorAll('[data-calc-pkg]').forEach(function (link) {
            link.addEventListener('click', function () {
                var pkg = link.getAttribute('data-calc-pkg');
                if (!pkg) return;
                try {
                    sessionStorage.setItem('pl_shop_pkg_hint', pkg);
                } catch (e) { /* ignore */ }
            });
        });
    }

    function observeReveal(el, onReveal) {
        if (!el) return;

        if (reduceMotion) {
            onReveal();
            return;
        }

        if ('IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        onReveal();
                        io.disconnect();
                    }
                });
            }, { threshold: 0.14, rootMargin: '0px 0px -8% 0px' });

            io.observe(el);

            requestAnimationFrame(function () {
                var rect = el.getBoundingClientRect();
                if (rect.top < (window.innerHeight || 800) * 0.92) {
                    onReveal();
                    io.disconnect();
                }
            });
        } else {
            onReveal();
        }
    }

    function initPkgReadMore() {
        root.querySelectorAll('.pl-shop__pkg-read-more').forEach(function (btn) {
            var extraId = btn.getAttribute('aria-controls');
            var extra = extraId ? document.getElementById(extraId) : null;
            if (!extra) return;

            btn.addEventListener('click', function () {
                var isOpen = btn.getAttribute('aria-expanded') === 'true';
                btn.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
                extra.hidden = isOpen;
                btn.textContent = btn.getAttribute(isOpen ? 'data-label-open' : 'data-label-close') || btn.textContent;
            });
        });
    }

    function formatCountValue(value) {
        return String(value).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }

    function setSvobodaStatFinalValues(block) {
        block.querySelectorAll('.pl-shop__stat-num[data-count-to]').forEach(function (el) {
            var target = parseInt(el.getAttribute('data-count-to'), 10);
            if (!target || isNaN(target)) return;

            var suffix = el.getAttribute('data-count-suffix') || '';
            var unitSpan = el.querySelector('span');
            var unitText = el.getAttribute('data-count-unit') || '';

            el.textContent = formatCountValue(target) + suffix;
            if (unitSpan || unitText) {
                var span = document.createElement('span');
                span.textContent = unitText || unitSpan.textContent;
                el.appendChild(span);
            }
        });
    }

    function runSvobodaStatCounters(block) {
        block.querySelectorAll('.pl-shop__stat-num[data-count-to]').forEach(function (el, index) {
            var target = parseInt(el.getAttribute('data-count-to'), 10);
            if (!target || isNaN(target)) return;

            var suffix = el.getAttribute('data-count-suffix') || '';
            var unitSpan = el.querySelector('span');
            var duration = target >= 1000 ? 1600 : 1100;
            var delay = index * 140;
            var startTime = null;

            function updateDisplay(value) {
                var mainText = formatCountValue(value) + suffix;
                if (unitSpan) {
                    if (el.firstChild && el.firstChild.nodeType === 3) {
                        el.firstChild.textContent = mainText;
                    } else {
                        el.insertBefore(document.createTextNode(mainText), unitSpan);
                    }
                    return;
                }
                el.textContent = mainText;
            }

            function tick(now) {
                if (!startTime) startTime = now;
                var progress = Math.min((now - startTime) / duration, 1);
                var eased = 1 - Math.pow(1 - progress, 3);
                updateDisplay(Math.round(target * eased));

                if (progress < 1) {
                    requestAnimationFrame(tick);
                }
            }

            setTimeout(function () {
                requestAnimationFrame(tick);
            }, delay);
        });
    }

    function initSvobodaReveal() {
        var block = root.querySelector('[data-svoboda-reveal]');
        if (!block) return;

        observeReveal(block, function () {
            if (reduceMotion) {
                setSvobodaStatFinalValues(block);
            } else {
                runSvobodaStatCounters(block);
            }
        });
    }

    function initPkgCompareTabs() {
        var modal = document.getElementById('pl-shop-pkg-compare-modal');
        if (!modal) return;

        var wrap = modal.querySelector('.pl-shop__pkg-matrix-wrap');
        var tabBtns = modal.querySelectorAll('[data-pkg-tab-btn]');
        if (!wrap || !tabBtns.length) return;

        var defaultTab = 'premium';

        function setTab(tabKey) {
            if (!tabKey) return;
            wrap.setAttribute('data-pkg-tab', tabKey);
            tabBtns.forEach(function (btn) {
                var isActive = btn.getAttribute('data-pkg-tab-btn') === tabKey;
                btn.classList.toggle('pl-shop__pkg-matrix-tab--active', isActive);
                btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
            });
        }

        tabBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                setTab(btn.getAttribute('data-pkg-tab-btn'));
            });
        });

        document.querySelectorAll('[data-modal="pl-shop-pkg-compare-modal"]').forEach(function (trigger) {
            trigger.addEventListener('click', function () {
                setTab(defaultTab);
            });
        });
    }

    function init() {
        initReveal();
        initPkgReadMore();
        initSvobodaReveal();
        initCalcPkgLinks();
        /* Clients marquee → static/js/components/clients-marquee.js (спільний з головною). */
        initPkgCompareTabs();
        if (typeof window.initAdminMock === 'function') {
            window.initAdminMock();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init, { once: true });
    } else {
        init();
    }
})();
