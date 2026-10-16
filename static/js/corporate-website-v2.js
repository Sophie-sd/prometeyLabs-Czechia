(function () {
    'use strict';

    var root = document.getElementById('plCorpRoot');
    if (!root) return;

    var reduceMotion = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function initReveal() {
        var els = root.querySelectorAll('[data-reveal]');
        if (!els.length) return;
        if (reduceMotion) return;

        els.forEach(function (el) {
            if (el.__rev) return;
            el.__rev = 1;
            el.style.opacity = '0';
            el.style.transform = 'translateY(26px)';
            el.style.transition = 'opacity .7s cubic-bezier(.2,.7,.2,1), transform .7s cubic-bezier(.2,.7,.2,1)';
        });

        function reveal(el) {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
            window.setTimeout(function () {
                el.style.removeProperty('transform');
                el.style.removeProperty('opacity');
                el.style.removeProperty('transition');
            }, 720);
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

    function initHeroMockup() {
        var mockup = root.querySelector('[data-hero-mockup]');
        if (!mockup) return null;

        var panels = mockup.querySelectorAll('[data-hero-panel]');
        var tabBtns = mockup.querySelectorAll('[data-hero-tab]');
        var currentPanel = 'economy';

        function showPanel(id) {
            var exists = false;
            panels.forEach(function (panel) {
                if (panel.getAttribute('data-hero-panel') === id) exists = true;
            });
            if (!exists) id = 'economy';
            currentPanel = id;

            panels.forEach(function (panel) {
                var active = panel.getAttribute('data-hero-panel') === id;
                panel.classList.toggle('is-active', active);
                panel.setAttribute('aria-hidden', active ? 'false' : 'true');
            });

            tabBtns.forEach(function (btn) {
                var selected = btn.getAttribute('data-hero-tab') === id;
                btn.classList.toggle('is-active', selected);
                btn.setAttribute('aria-selected', selected ? 'true' : 'false');
            });
        }

        return {
            showPanel: showPanel,
            getCurrentPanel: function () { return currentPanel; }
        };
    }

    function initHeroSequence() {
        var stage = root.querySelector('[data-hero-stage]');
        if (!stage) return;

        var mockupApi = initHeroMockup();
        if (!mockupApi) return;

        var mockup = root.querySelector('[data-hero-mockup]');
        var rings = root.querySelectorAll('[data-hero-ring]');
        var cardsWrap = root.querySelector('[data-hero-win-cards]');
        var tabIds = ['economy', 'tech', 'scale'];
        var CYCLE_MS = 3200;
        var cycleTimer = null;
        var paused = false;
        var index = 0;

        function show(id) {
            var i = tabIds.indexOf(id);
            index = i < 0 ? 0 : i;
            mockupApi.showPanel(tabIds[index]);
        }

        function tick() {
            if (paused || document.hidden) return;
            show(tabIds[(index + 1) % tabIds.length]);
        }

        function restart() {
            if (reduceMotion) return;
            if (cycleTimer) clearInterval(cycleTimer);
            cycleTimer = setInterval(tick, CYCLE_MS);
        }

        root.querySelectorAll('[data-hero-tab]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                show(btn.getAttribute('data-hero-tab'));
                restart();
            });
        });

        root.querySelectorAll('[data-hero-back]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                show('economy');
                restart();
            });
        });

        root.querySelectorAll('[data-hero-tab-trigger]').forEach(function (chip) {
            function activate() {
                show(chip.getAttribute('data-hero-tab-trigger'));
                restart();
            }
            chip.addEventListener('click', activate);
            chip.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    activate();
                }
            });
        });

        if (cardsWrap) {
            cardsWrap.addEventListener('keydown', function (e) {
                if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
                e.preventDefault();
                var step = e.key === 'ArrowRight' ? 1 : tabIds.length - 1;
                show(tabIds[(index + step) % tabIds.length]);
                var next = cardsWrap.querySelector('[data-hero-tab="' + tabIds[index] + '"]');
                if (next) next.focus();
                restart();
            });
        }

        [mockup, cardsWrap].forEach(function (el) {
            if (!el) return;
            el.addEventListener('mouseenter', function () { paused = true; });
            el.addEventListener('mouseleave', function () { paused = false; });
            el.addEventListener('focusin', function () { paused = true; });
            el.addEventListener('focusout', function () { paused = false; });
        });

        function lightRings() {
            rings.forEach(function (ring, i) {
                if (reduceMotion) {
                    ring.classList.add('is-on');
                    return;
                }
                setTimeout(function () { ring.classList.add('is-on'); }, 120 * i);
            });
        }

        show('economy');

        if ('IntersectionObserver' in window && !reduceMotion) {
            var io = new IntersectionObserver(function (ents) {
                ents.forEach(function (en) {
                    if (!en.isIntersecting) return;
                    lightRings();
                    restart();
                    io.disconnect();
                });
            }, { threshold: 0.2 });
            io.observe(stage);
        } else {
            lightRings();
        }
    }

    /* Modal a11y on this page: focus trap + focus restore for the global .modal partials
       (open/close/Esc are handled by base.js). */
    function initModalA11y() {
        var FOCUSABLE = 'a[href], button:not([disabled]), input:not([type="hidden"]):not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
        var lastTrigger = null;

        document.addEventListener('click', function (e) {
            var trigger = e.target.closest ? e.target.closest('[data-modal]') : null;
            if (trigger) lastTrigger = trigger;
        }, true);

        function visibleFocusables(modal) {
            return Array.prototype.filter.call(modal.querySelectorAll(FOCUSABLE), function (el) {
                return el.offsetWidth > 0 || el.offsetHeight > 0 || el.getClientRects().length > 0;
            });
        }

        document.querySelectorAll('.modal').forEach(function (modal) {
            if (!modal.hasAttribute('aria-modal')) modal.setAttribute('aria-modal', 'true');

            var wasActive = modal.classList.contains('active');
            new MutationObserver(function () {
                var isActive = modal.classList.contains('active');
                if (isActive === wasActive) return;
                wasActive = isActive;
                if (isActive) {
                    var focusables = visibleFocusables(modal);
                    var first = focusables[0];
                    if (first && !modal.contains(document.activeElement)) {
                        setTimeout(function () {
                            if (!modal.contains(document.activeElement)) first.focus();
                        }, 320);
                    }
                } else if (lastTrigger && document.contains(lastTrigger)) {
                    lastTrigger.focus({ preventScroll: true });
                    lastTrigger = null;
                }
            }).observe(modal, { attributes: true, attributeFilter: ['class'] });

            modal.addEventListener('keydown', function (e) {
                if (e.key !== 'Tab' || !modal.classList.contains('active')) return;
                var focusables = visibleFocusables(modal);
                if (!focusables.length) return;
                var first = focusables[0];
                var last = focusables[focusables.length - 1];
                if (e.shiftKey && document.activeElement === first) {
                    e.preventDefault();
                    last.focus();
                } else if (!e.shiftKey && document.activeElement === last) {
                    e.preventDefault();
                    first.focus();
                }
            });
        });
    }

    function waitForImages(container) {
        return new Promise(function (resolve, reject) {
            var images = container.querySelectorAll('img');
            if (!images.length) {
                resolve();
                return;
            }

            var loadedCount = 0;
            var totalImages = images.length;
            var timeout = setTimeout(function () { reject(new Error('timeout')); }, 3000);

            function done() {
                loadedCount += 1;
                if (loadedCount === totalImages) {
                    clearTimeout(timeout);
                    resolve();
                }
            }

            images.forEach(function (img) {
                if (img.complete) {
                    done();
                } else {
                    img.addEventListener('load', done, { once: true });
                    img.addEventListener('error', done, { once: true });
                }
            });
        });
    }

    function initClientsMarquee() {
        var container = root.querySelector('.pl-corp__clients-stories-container');
        if (!container) return;

        function initMarqueeAnimation() {
            var stories = container.querySelectorAll('.project-story:not(.story-clone)');
            if (!stories.length) return;

            var containerStyles = window.getComputedStyle(container);
            var gap = parseFloat(containerStyles.columnGap || containerStyles.gap) || 14;
            var firstStory = stories[0];
            var lastStory = stories[stories.length - 1];
            var setWidth = (lastStory.offsetLeft + lastStory.offsetWidth + gap) - firstStory.offsetLeft;

            container.style.setProperty('--marquee-distance', setWidth + 'px');
            container.setAttribute('aria-label', 'Наші клієнти — автоматична демонстрація');
            // Не перезаписуємо role: контейнер уже має role="list" у шаблоні.
            // role="marquee" — невалідна ARIA-роль і ламає list/listitem.

            if ('IntersectionObserver' in window) {
                var observer = new IntersectionObserver(function (entries) {
                    entries.forEach(function (entry) {
                        if (entry.isIntersecting) {
                            requestAnimationFrame(function () {
                                container.classList.add('marquee-active');
                            });
                            observer.unobserve(container);
                        }
                    });
                }, { threshold: 0.1, rootMargin: '50px' });
                observer.observe(container);
            } else {
                requestAnimationFrame(function () {
                    container.classList.add('marquee-active');
                });
            }
        }

        waitForImages(container).then(initMarqueeAnimation).catch(function () {
            setTimeout(initMarqueeAnimation, 500);
        });
    }

    function initScaleDiagram() {
        var diagram = root.querySelector('.pl-corp__scale-diagram');
        if (!diagram) return;

        function activate() {
            if (diagram.classList.contains('is-live')) return;
            diagram.classList.add('is-live');
        }

        if (reduceMotion) {
            activate();
            return;
        }

        if ('IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (ents) {
                ents.forEach(function (en) {
                    if (en.isIntersecting) {
                        activate();
                        io.unobserve(diagram);
                    }
                });
            }, { threshold: 0.2, rootMargin: '0px 0px -8% 0px' });

            io.observe(diagram);

            requestAnimationFrame(function () {
                var vh = window.innerHeight || 800;
                var rect = diagram.getBoundingClientRect();
                if (rect.top < vh * 0.92) {
                    activate();
                    io.unobserve(diagram);
                }
            });
        } else {
            activate();
        }
    }

    function initFabGuard() {
        var card = document.querySelector('.pl-corp__hero-card');
        if (!card || !('IntersectionObserver' in window)) return;
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                document.body.classList.toggle('pl-corp-fab-off', entry.isIntersecting);
            });
        }, { threshold: 0 });
        io.observe(card);
    }

    function init() {
        initReveal();
        initHeroSequence();
        initClientsMarquee();
        initScaleDiagram();
        initModalA11y();
        initFabGuard();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init, { once: true });
    } else {
        init();
    }
})();
