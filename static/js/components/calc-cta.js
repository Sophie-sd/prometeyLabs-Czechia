/* Calc CTA: analytics (cta_calc_click), smooth scroll to the on-page quiz,
   mobile sticky bar (≤767px) after the first screen; hidden while the quiz,
   a lead form or the footer is on screen, while typing, or a modal/menu is open. */
(function () {
    'use strict';
    if (window.__plCalcCta) return;
    window.__plCalcCta = true;

    var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    document.addEventListener('click', function (e) {
        var link = e.target && e.target.closest ? e.target.closest('[data-calc-cta]') : null;
        if (!link) return;
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({
            event: 'cta_calc_click',
            page: link.getAttribute('data-calc-page') || '',
            position: link.getAttribute('data-calc-cta') || 'hero'
        });
        var sel = link.getAttribute('data-calc-scroll');
        if (!sel) return;
        var target = document.querySelector(sel);
        if (!target) return;
        e.preventDefault();
        target.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
        if (window.history && history.replaceState) history.replaceState(null, '', sel);
    });

    function initSticky() {
        var bar = document.querySelector('[data-calc-sticky]');
        if (!bar || !('IntersectionObserver' in window)) return;
        // Рендериться всередині hero; переносимо в <body>, щоб stacking context hero
        // (z-index/isolation секції) не ховав fixed-бар під наступні секції.
        if (bar.parentNode !== document.body) document.body.appendChild(bar);
        var btn = bar.querySelector('a');
        var hero = document.querySelector('[data-calc-cta-hero]');
        var mq = window.matchMedia('(max-width: 767px)');
        var pastHero = false;
        var typing = false;
        var blockers = new Set();

        function update() {
            var body = document.body;
            var show = mq.matches && pastHero && blockers.size === 0 && !typing &&
                !body.classList.contains('modal-open') && !body.classList.contains('menu-open');
            bar.classList.toggle('is-visible', show);
            bar.setAttribute('aria-hidden', show ? 'false' : 'true');
            if (btn) btn.tabIndex = show ? 0 : -1;
            body.classList.toggle('pl-calc-sticky-on', show);
            var fab = document.querySelector('.mobile-contact-fab');
            body.classList.toggle('pl-calc-has-fab', !!fab && getComputedStyle(fab).display !== 'none');
        }

        if (hero) {
            new IntersectionObserver(function (entries) {
                entries.forEach(function (en) {
                    pastHero = !en.isIntersecting && en.boundingClientRect.top < 0;
                });
                update();
            }).observe(hero);
        } else {
            pastHero = true;
        }

        var watch = [];
        var targetSel = bar.getAttribute('data-calc-target');
        if (targetSel) {
            var t = document.querySelector(targetSel);
            if (t) watch.push(t);
        }
        document.querySelectorAll('main form, form[data-form-type], footer, .footer, .site-footer').forEach(function (el) {
            if (el.closest('.modal, [role="dialog"], [data-calc-sticky]')) return;
            if (watch.indexOf(el) === -1) watch.push(el);
        });
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (en) {
                if (en.isIntersecting) blockers.add(en.target); else blockers.delete(en.target);
            });
            update();
        });
        watch.forEach(function (el) { io.observe(el); });

        document.addEventListener('focusin', function (e) {
            if (e.target && e.target.matches && e.target.matches('input, textarea, select')) { typing = true; update(); }
        });
        document.addEventListener('focusout', function () { typing = false; update(); });
        new MutationObserver(update).observe(document.body, { attributes: true, attributeFilter: ['class'] });
        if (mq.addEventListener) mq.addEventListener('change', update);
        update();
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initSticky);
    else initSticky();
})();
