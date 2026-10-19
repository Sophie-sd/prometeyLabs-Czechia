/**
 * Clients marquee — спільний компонент (винесено з internet-shop-v2.js без змін логіки).
 * Розмітка: контейнер з [data-clients-marquee], два сети карток (оригінал + .story-clone).
 * Відстань = ширина одного сету → translate3d(-distance) у CSS-анімації, старт при появі у в'юпорті.
 * Використовують: internet-shop-v2 (UA/RU), головна (home_figma/clients.html).
 */
(function () {
    'use strict';

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

    function initClientsMarquee(container) {
        if (!container) return;

        function initMarqueeAnimation() {
            var stories = container.querySelectorAll('.project-story:not(.story-clone)');
            if (!stories.length) return;

            var containerStyles = window.getComputedStyle(container);
            var gap = parseFloat(containerStyles.gap) || 24;
            var firstStory = stories[0];
            var lastStory = stories[stories.length - 1];
            var setWidth = (lastStory.offsetLeft + lastStory.offsetWidth + gap) - firstStory.offsetLeft;

            container.style.setProperty('--marquee-distance', setWidth + 'px');
            var lang = (document.documentElement.lang || '').toLowerCase();
            var marqueeLabels = { cs: 'Naši klienti — automatická ukázka', en: 'Our clients — automatic showcase' };
            container.setAttribute('aria-label', marqueeLabels[lang.slice(0, 2)] || marqueeLabels.cs);
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


    function initAll() {
        document.querySelectorAll('[data-clients-marquee]').forEach(initClientsMarquee);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAll);
    } else {
        initAll();
    }
})();
