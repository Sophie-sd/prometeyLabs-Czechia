/* Footer accordion (mobile), menu services toggle, menu language dropdown — Figma footer/menu */
(function () {
    'use strict';
    function init() {
        var mq = window.matchMedia('(max-width: 767px)');
        document.querySelectorAll('[data-plf-acc]').forEach(function (col, i) {
            var head = col.querySelector('.plf__acc-head');
            if (!head) return;
            head.addEventListener('click', function () {
                if (!mq.matches) return;
                var open = col.classList.toggle('is-open');
                head.setAttribute('aria-expanded', open ? 'true' : 'false');
            });
        });
        document.querySelectorAll('.plm__toggle').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var g = btn.closest('.plm__group');
                var open = g.classList.toggle('is-open');
                btn.setAttribute('aria-expanded', open ? 'true' : 'false');
            });
        });
        document.querySelectorAll('.plm__lang').forEach(function (lang) {
            var btn = lang.querySelector('.plm__lang-btn');
            if (!btn) return;
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var open = lang.classList.toggle('is-open');
                btn.setAttribute('aria-expanded', open ? 'true' : 'false');
            });
            document.addEventListener('click', function (e) {
                if (!lang.contains(e.target)) { lang.classList.remove('is-open'); btn.setAttribute('aria-expanded', 'false'); }
            });
        });
    }
    function fabFooter() {
        var f = document.querySelector('footer.plf');
        if (!f || !('IntersectionObserver' in window)) return;
        new IntersectionObserver(function (es) {
            document.body.classList.toggle('plf-footer-visible', es[0].isIntersecting);
        }, { rootMargin: '0px 0px -40px 0px' }).observe(f);
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function(){init();fabFooter();}); else {init();fabFooter();}
})();
