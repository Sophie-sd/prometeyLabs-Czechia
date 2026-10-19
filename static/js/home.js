/**
 * HOME.JS - Home page specific logic
 * Використовує: MobileCore, VideoSystem, base.js
 * БЕЗ дублювань viewport/scroll/modal logic
 */

document.addEventListener('DOMContentLoaded', () => {
    initServiceModals();
    initProjectStories();
    initAnalytics();
    initLazyBackgrounds();
    initWhyChooseAnimations();
});

function initServiceAnimations() {
    const serviceCards = document.querySelectorAll('.service-card');
    if (serviceCards.length === 0) return;
    if (!('IntersectionObserver' in window)) {
        serviceCards.forEach(card => card.classList.add('visible'));
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                
                setTimeout(() => {
                    entry.target.style.willChange = 'auto';
                }, 600);
                
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.01,
        rootMargin: '0px'
    });

    serviceCards.forEach(card => {
        const rect = card.getBoundingClientRect();
        const isInViewport = rect.top < window.innerHeight && rect.bottom > 0;
        
        if (isInViewport) {
            card.classList.add('visible');
            setTimeout(() => {
                card.style.willChange = 'auto';
            }, 600);
        } else {
            observer.observe(card);
        }
    });
}

function initServiceModals() {
    let savedScrollPosition = 0;

    const lockScroll = () => {
        savedScrollPosition = window.pageYOffset || document.documentElement.scrollTop;
        document.body.style.top = `-${savedScrollPosition}px`;
        document.body.classList.add('modal-open', 'service-modal-open');
        document.documentElement.style.backgroundColor = '#000';
    };

    const unlockScroll = () => {
        document.body.style.top = '';
        document.body.classList.remove('modal-open', 'service-modal-open');
        document.documentElement.style.backgroundColor = '';
        window.scrollTo({
            top: savedScrollPosition,
            behavior: 'auto'
        });
    };

    const openModal = (serviceType) => {
        const modalId = `service-${serviceType}-modal`;
        const modal = document.getElementById(modalId);

        if (!modal) return;

        lockScroll();
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');

        const closeModal = () => {
            modal.classList.remove('active');
            modal.setAttribute('aria-hidden', 'true');
            unlockScroll();
        };

        const closeBtn = modal.querySelector('.modal-close');
        const backdrop = modal.querySelector('.modal-backdrop');

        closeBtn.removeEventListener('click', closeModal);
        backdrop.removeEventListener('click', closeModal);

        closeBtn.addEventListener('click', closeModal);
        backdrop.addEventListener('click', closeModal);

        document.addEventListener('keydown', function escHandler(e) {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', escHandler);
            }
        });
    };

    document.querySelectorAll('.service-card').forEach(card => {
        card.addEventListener('click', (e) => {
            if (e.target.closest('.service-detail-btn')) return;
            openModal(card.dataset.service);
        });
    });

    document.querySelectorAll('.service-detail-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            openModal(btn.closest('.service-card').dataset.service);
        });
    });
}

// ===== PROJECT STORIES MARQUEE =====
function initProjectStories() {
    const container = document.querySelector('.projects-stories-container');
    if (!container) return;
    
    waitForImages(container).then(() => {
        initMarqueeAnimation(container);
    }).catch(() => {
        setTimeout(() => initMarqueeAnimation(container), 500);
    });
}

function waitForImages(container) {
    return new Promise((resolve, reject) => {
        const images = container.querySelectorAll('img');
        if (images.length === 0) {
            resolve();
            return;
        }
        
        let loadedCount = 0;
        const totalImages = images.length;
        const timeout = setTimeout(() => reject('timeout'), 3000);
        
        images.forEach(img => {
            if (img.complete) {
                loadedCount++;
                if (loadedCount === totalImages) {
                    clearTimeout(timeout);
                    resolve();
                }
            } else {
                img.addEventListener('load', () => {
                    loadedCount++;
                    if (loadedCount === totalImages) {
                        clearTimeout(timeout);
                        resolve();
                    }
                }, { once: true });
                
                img.addEventListener('error', () => {
                    loadedCount++;
                    if (loadedCount === totalImages) {
                        clearTimeout(timeout);
                        resolve();
                    }
                }, { once: true });
            }
        });
    });
}

function initMarqueeAnimation(container) {
    const stories = container.querySelectorAll('.project-story:not(.story-clone)');
    if (stories.length === 0) return;
    
    const containerStyles = window.getComputedStyle(container);
    const gap = parseFloat(containerStyles.gap) || 24;
    
    const firstStory = stories[0];
    const lastStory = stories[stories.length - 1];
    const setWidth = (lastStory.offsetLeft + lastStory.offsetWidth + gap) - firstStory.offsetLeft;
    
    container.style.setProperty('--marquee-distance', `${setWidth}px`);
    container.setAttribute('aria-label', (((document.documentElement.getAttribute('lang') || 'cs').toLowerCase().indexOf('en') === 0) ? 'Our projects — automatic showcase' : 'Naše projekty — automatická ukázka'));
    container.setAttribute('role', 'marquee');
    
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    requestAnimationFrame(() => {
                        container.classList.add('marquee-active');
                    });
                    observer.unobserve(container);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });
        
        observer.observe(container);
    } else {
        requestAnimationFrame(() => {
            container.classList.add('marquee-active');
        });
    }
}

// ===== ANALYTICS =====
function initAnalytics() {
    // Tracking button clicks (passive listener)
    document.addEventListener('click', (e) => {
        const button = e.target.closest('.btn');
        if (button && typeof gtag !== 'undefined') {
            gtag('event', 'button_click', {
                button_text: button.textContent.trim(),
                page_location: window.location.href
            });
        }
    }, { passive: true });

    // Time on page tracking (оптимізовано)
    let timeOnPage = 0;
    let trackedEngagement = false;

    const timeTracker = setInterval(() => {
        timeOnPage += 1;
        if (timeOnPage === 30 && !trackedEngagement && typeof gtag !== 'undefined') {
            gtag('event', 'engaged_session', {
                time_on_page: timeOnPage
            });
            trackedEngagement = true;
            clearInterval(timeTracker); // Зупинити після трекінгу
        }
    }, 1000);
}

function initLazyBackgrounds() {
    const lazyBgElements = document.querySelectorAll('.lazy-bg');
    if (lazyBgElements.length === 0) return;

    if (!('IntersectionObserver' in window)) {
        lazyBgElements.forEach(el => loadBackground(el));
        return;
    }

    const bgObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                loadBackground(entry.target);
                bgObserver.unobserve(entry.target);
            }
        });
    }, {
        rootMargin: '0px',
        threshold: 0.01
    });

    lazyBgElements.forEach(el => {
        const rect = el.getBoundingClientRect();
        const isInViewport = rect.top < window.innerHeight && rect.bottom > 0;
        
        if (isInViewport) {
            loadBackground(el);
        } else {
            bgObserver.observe(el);
        }
    });
}

function loadBackground(element) {
    const isMobile = window.innerWidth <= 767;
    const bgUrl = isMobile 
        ? element.getAttribute('data-bg-mobile') 
        : element.getAttribute('data-bg-desktop');
    
    if (bgUrl) {
        const img = new Image();
        img.onload = () => {
            element.style.backgroundImage = `url('${bgUrl}')`;
            element.classList.add('lazy-bg-loaded');
            element.classList.remove('lazy-bg');
        };
        img.src = bgUrl;
    }
}

function initWhyChooseAnimations() {
    const whyGrid = document.querySelector('.v2-why-grid');
    const whyCards = document.querySelectorAll('.v2-why-grid .v2-why-card');
    if (whyCards.length === 0) return;

    const reduceMotion = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (!whyGrid || reduceMotion) return;
    if (whyGrid.dataset.whyReady === '1') return;
    whyGrid.dataset.whyReady = '1';

    const canHover = () =>
        window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;

    function setActiveCard(target) {
        whyCards.forEach(card => {
            card.classList.toggle('v2-why-card--active', card === target);
        });
    }

    whyCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            if (!canHover()) return;
            setActiveCard(card);
        });

        card.addEventListener('click', () => {
            setActiveCard(card);
        });
    });

    whyGrid.addEventListener('mouseleave', () => {
        if (!canHover()) return;
        setActiveCard(null);
    });
}
