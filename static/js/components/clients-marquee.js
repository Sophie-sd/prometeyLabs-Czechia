/**
 * Clients marquee — спільний компонент (винесено з internet-shop-v2.js без змін логіки).
 * Розмітка: контейнер з [data-clients-marquee], два сети карток (оригінал + .story-clone).
 * Відстань = ширина одного сету → translate3d(-distance) у CSS-анімації, старт при появі у в'юпорті.
 * Використовують: internet-shop-v2 (UA/RU), головна (home_figma/clients.html).
 */
(function () {
    'use strict';

    var SECONDS_PER_ITEM = 40 / 9;

    function initClientsMarquee(container) {
        if (!container) return;

        // Lazy-завантаження не бачить кола за overflow:hidden доріжки, тож вони вантажились
        // лише при вʼїзді в кадр (білі кола). Щойно стрічка в полі зору — тягнемо всі логотипи.
        function loadAllLogos() {
            container.querySelectorAll('img[loading="lazy"]').forEach(function (img) {
                img.loading = 'eager';
            });
        }

        function initMarqueeAnimation(isResize) {
            var stories = container.querySelectorAll('.project-story:not(.story-clone)');
            if (!stories.length) return;

            // Відстань циклу = точний зсув першого клона від першого оригіналу
            // (getBoundingClientRect, бо offsetWidth округлює 76.478px → шов на мобільному).
            var firstClone = container.querySelector('.project-story.story-clone');
            var setWidth = firstClone
                ? firstClone.getBoundingClientRect().left - stories[0].getBoundingClientRect().left
                : 0;
            if (!setWidth) {
                var containerStyles = window.getComputedStyle(container);
                var gap = parseFloat(containerStyles.columnGap || containerStyles.gap) || 24;
                var lastStory = stories[stories.length - 1];
                setWidth = lastStory.getBoundingClientRect().right + gap - stories[0].getBoundingClientRect().left;
            }

            // Швидкість як у старої стрічки з 9 клієнтів (40s на сет): 40/9 s на одне коло,
            // тобто ~33 px/s на десктопі та ~20 px/s на мобільному, незалежно від кількості клієнтів.
            container.style.setProperty('--marquee-distance', (Math.round(setWidth * 1000) / 1000) + 'px');
            container.style.setProperty('--marquee-duration', (stories.length * SECONDS_PER_ITEM).toFixed(2) + 's');
            var lang = (document.documentElement.lang || '').toLowerCase();
            var marqueeLabels = { cs: 'Naši klienti — automatická ukázka', en: 'Our clients — automatic showcase' };
            container.setAttribute('aria-label', marqueeLabels[lang.slice(0, 2)] || marqueeLabels.cs);
            // Не перезаписуємо role: контейнер уже має role="list" у шаблоні.
            // role="marquee" — невалідна ARIA-роль і ламає list/listitem.

            if (isResize) return;

            if ('IntersectionObserver' in window) {
                var observer = new IntersectionObserver(function (entries) {
                    entries.forEach(function (entry) {
                        if (entry.isIntersecting) {
                            loadAllLogos();
                            requestAnimationFrame(function () {
                                container.classList.add('marquee-active');
                            });
                            observer.unobserve(container);
                        }
                    });
                }, { threshold: 0, rootMargin: '50px' });
                observer.observe(container);
            } else {
                loadAllLogos();
                requestAnimationFrame(function () {
                    container.classList.add('marquee-active');
                });
            }
        }

        // Розміри кіл задані в CSS (img має width/height), тож не чекаємо картинок:
        // з loading="lazy" ті, що за краєм екрана, не вантажаться і блокували старт на 3.5s.
        initMarqueeAnimation();

        // Брейкпоінт (128px ↔ 76px) змінює ширину сету — перераховуємо відстань.
        var resizeTimer;
        window.addEventListener('resize', function () {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function () { initMarqueeAnimation(true); }, 150);
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
