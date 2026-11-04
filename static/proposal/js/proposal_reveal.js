/**
 * Proposal motion: bars, words, reveal, progress, rail, metric, modules.
 */
(function () {
  'use strict';

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  function pad2(n) {
    return String(n).padStart(2, '0');
  }

  function splitWords() {
    const title = document.querySelector('[data-prop-words]');
    if (!title) return;
    const text = title.textContent.trim();
    const words = text.split(/\s+/).filter(Boolean);
    if (words.length < 2) return;
    title.textContent = '';
    words.forEach(function (word, i) {
      const span = document.createElement('span');
      span.className = 'prop-word';
      if (i >= words.length - 2) span.classList.add('prop-word--accent');
      span.style.setProperty('--word-i', String(i));
      span.textContent = word;
      title.appendChild(span);
      title.appendChild(document.createTextNode(' '));
    });
  }

  function initBars() {
    const bars = document.querySelectorAll('[data-prop-bar]');
    if (!bars.length || reduceMotion.matches) {
      bars.forEach(function (bar) { bar.classList.add('is-gone'); });
      return;
    }
    document.body.classList.add('is-bars');
    window.setTimeout(function () {
      bars.forEach(function (bar) { bar.classList.add('is-gone'); });
    }, 1500);
  }

  function revealAll() {
    document.querySelectorAll('[data-prop-reveal]').forEach(function (el) {
      el.classList.add('is-revealed');
    });
    document.querySelectorAll('[data-prop-anim]').forEach(function (el) {
      el.classList.add('is-in');
    });
    const hero = document.getElementById('prop-hero');
    if (hero) hero.classList.add('is-in');
  }

  function initReveal() {
    const hero = document.getElementById('prop-hero');
    if (hero) hero.classList.add('is-in');

    const nodes = document.querySelectorAll('[data-prop-reveal], [data-prop-anim]');
    if (reduceMotion.matches || !('IntersectionObserver' in window)) {
      revealAll();
      return;
    }

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          if (entry.target.hasAttribute('data-prop-anim')) {
            entry.target.classList.add('is-in');
          }
          if (entry.target.hasAttribute('data-prop-reveal')) {
            entry.target.classList.add('is-revealed');
          }
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.06, rootMargin: '0px 0px -6% 0px' }
    );

    nodes.forEach(function (el) {
      observer.observe(el);
    });
  }

  function initProgress() {
    const bar = document.querySelector('[data-prop-progress]');
    if (!bar) return;

    function onScroll() {
      const el = document.scrollingElement || document.documentElement;
      const h = el.scrollHeight - el.clientHeight;
      const p = h > 8 ? Math.min(1, Math.max(0, el.scrollTop / h)) : 0;
      bar.style.transform = 'scaleX(' + p + ')';
    }

    document.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    onScroll();
  }

  function initParallax() {
    const img = document.querySelector('[data-prop-hero-img]');
    if (!img || reduceMotion.matches) return;

    function onScroll() {
      const y = window.scrollY;
      img.style.transform = 'translateY(' + Math.min(y * 0.22, 160) + 'px)';
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  function initRail() {
    const nav = document.querySelector('.prop-rail');
    const count = document.querySelector('[data-prop-navcount]');
    if (!nav) return;

    const hero = document.getElementById('prop-hero');
    const rest = Array.prototype.slice.call(
      document.querySelectorAll('[data-prop-section]')
    );
    const items = [];
    if (hero) items.push(hero);
    rest.forEach(function (el) {
      if (el !== hero && el.id) items.push(el);
    });
    if (!items.length) return;

    nav.replaceChildren();
    items.forEach(function (el, i) {
      const a = document.createElement('a');
      a.href = '#' + el.id;
      a.setAttribute('data-prop-rail', String(i));
      const h = el.querySelector('h1, h2, h3');
      const label = (el.getAttribute('aria-label') || (h && h.textContent) || el.id).trim().replace(/\s+/g, ' ');
      a.setAttribute('aria-label', label);
      a.appendChild(document.createElement('span'));
      nav.appendChild(a);
    });

    const rail = nav.querySelectorAll('[data-prop-rail]');
    const total = items.length;

    function setRail(i) {
      rail.forEach(function (a) {
        a.classList.toggle('is-on', Number(a.getAttribute('data-prop-rail')) === i);
      });
    }

    function setCount(n) {
      if (count) count.textContent = pad2(n) + ' / ' + pad2(total);
    }

    setCount(1);
    setRail(0);

    if (!('IntersectionObserver' in window)) return;

    const io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          const i = items.indexOf(entry.target);
          if (i < 0) return;
          setCount(i + 1);
          setRail(i);
        });
      },
      { rootMargin: '-45% 0px -45% 0px', threshold: 0 }
    );

    items.forEach(function (el) {
      io.observe(el);
    });
  }

  function initStickyHide() {
    const sticky = document.querySelector('.prop-sticky-cta');
    const hero = document.getElementById('prop-hero');
    const finalCta = document.querySelector('.prop-cta-sec');
    if (!sticky || !('IntersectionObserver' in window)) return;

    sticky.classList.add('is-hidden');

    function sync() {
      const heroOn = hero && hero.getBoundingClientRect().bottom > window.innerHeight * 0.55;
      const ctaOn = finalCta && finalCta.getBoundingClientRect().top < window.innerHeight * 0.85;
      sticky.classList.toggle('is-hidden', Boolean(heroOn || ctaOn));
    }

    window.addEventListener('scroll', sync, { passive: true });
    window.addEventListener('resize', sync, { passive: true });
    if (hero) {
      const io = new IntersectionObserver(sync, { threshold: [0, 0.2, 0.55, 1] });
      io.observe(hero);
      if (finalCta) io.observe(finalCta);
    }
    sync();
  }

  function initMetric() {
    const host = document.querySelector('[data-prop-metric]');
    if (!host) return;
    const first = host.querySelector('li');
    if (!first) return;

    const html = first.innerHTML;
    const match = html.match(/90\+/);
    if (match) {
      first.innerHTML = html.replace(
        '90+',
        '<span class="prop-metric__num" data-prop-metric-num>90+</span>'
      );
      const strong = first.querySelector('strong');
      if (strong && first.querySelector('[data-prop-metric-num]')) {
        first.classList.add('prop-metric');
      }
    }

    const metric = document.querySelector('[data-prop-metric-num]');
    if (!metric || reduceMotion.matches || !('IntersectionObserver' in window)) return;

    const observer = new IntersectionObserver(function (entries) {
      if (!entries[0] || !entries[0].isIntersecting) return;
      observer.disconnect();
      const t0 = performance.now();
      const dur = 1400;
      function tick(now) {
        const p = Math.min(1, (now - t0) / dur);
        const eased = 1 - Math.pow(1 - p, 3);
        metric.textContent = Math.round(eased * 90) + '+';
        if (p < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    }, { threshold: 0.5 });

    observer.observe(metric);
  }

  function initPayPct() {
    document.querySelectorAll('[data-prop-pct]').forEach(function (el) {
      const m = el.textContent.match(/(\d+)\s*%/);
      if (!m) return;
      el.innerHTML = m[1] + '<em>%</em>';
    });
  }

  function initModules() {
    const index = document.querySelector('[data-prop-mod-index]');
    const mods = document.querySelectorAll('[data-mi]');
    if (!index || !mods.length) return;

    let shown = '01';
    let pending = null;
    let queued = false;

    function pick() {
      queued = false;
      const mid = window.innerHeight / 2;
      let best = null;
      let bestD = Infinity;
      mods.forEach(function (row) {
        const r = row.getBoundingClientRect();
        const d = Math.abs((r.top + r.bottom) / 2 - mid);
        if (d < bestD) {
          bestD = d;
          best = row;
        }
      });
      if (!best) return;
      const val = pad2(best.getAttribute('data-mi') || '1');
      if (val === shown) return;
      shown = val;
      window.clearTimeout(pending);
      index.style.opacity = '0';
      pending = window.setTimeout(function () {
        index.textContent = shown;
        index.style.opacity = '1';
      }, 160);
    }

    function onScroll() {
      if (queued) return;
      queued = true;
      requestAnimationFrame(pick);
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    pick();
  }

  function init() {
    splitWords();
    initBars();
    initReveal();
    initProgress();
    initParallax();
    initRail();
    initStickyHide();
    initMetric();
    initPayPct();
    initModules();
    window.setTimeout(revealAll, 2200);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
