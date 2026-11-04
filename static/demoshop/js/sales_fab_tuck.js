/* The fixed sales helper collapses to its icon while it would cover page content.
   IntersectionObserver only (no scroll handler), so scrolling stays smooth. */

const AVOID_SELECTOR = '[data-ds-fab-avoid]';
const GAP = 8;

function initSalesFabTuck() {
    const root = document.querySelector('[data-ds-sales-chrome]');
    const fab = root && root.querySelector('.ds-sales-fab');
    const targets = document.querySelectorAll(AVOID_SELECTOR);
    if (!fab || !targets.length || !('IntersectionObserver' in window)) return;

    let observer = null;
    const overlapping = new Set();

    function build() {
        if (observer) observer.disconnect();
        overlapping.clear();
        root.classList.remove('is-tucked');
        // Measure the expanded pill: deriving the band from a tucked pill would oscillate.
        const box = fab.getBoundingClientRect();
        if (!box.width) return;
        const top = Math.max(0, box.top - GAP);
        const bottom = Math.max(0, window.innerHeight - box.bottom - GAP);
        const left = Math.max(0, box.left - GAP);
        const right = Math.max(0, window.innerWidth - box.right - GAP);
        observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) overlapping.add(entry.target);
                    else overlapping.delete(entry.target);
                });
                root.classList.toggle('is-tucked', overlapping.size > 0);
            },
            { rootMargin: `${-top}px ${-right}px ${-bottom}px ${-left}px`, threshold: 0 },
        );
        targets.forEach((el) => observer.observe(el));
    }

    build();

    let resizeTimer = 0;
    window.addEventListener('resize', () => {
        window.clearTimeout(resizeTimer);
        resizeTimer = window.setTimeout(build, 200);
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSalesFabTuck);
} else {
    initSalesFabTuck();
}
