/**
 * BASE.JS - Базовий JavaScript для PrometeyLabs
 * Рефакторинг 2025: БЕЗ дублювань, чиста архітектура
 * 
 * Залежності: MobileCore, Utils (опціонально)
 */

class PrometeyApp {
    constructor() {
        this.config = {
            scrollThreshold: 50,
            menuTransitionDuration: 400,
            notificationDuration: 5000
        };

        this.state = {
            menuOpen: false,
            activeModal: null
        };

        this.elements = {}; // Кеш DOM елементів
        this.phoneMasks = new Map(); // Зберігаємо інстанси PhoneMask

        this.init();
    }

    init() {
        // Чекаємо MobileCore
        if (window.MobileCore?.isInitialized()) {
            this.initWithMobileCore();
        } else {
            document.addEventListener('mobilecore:initialized', () => {
                this.initWithMobileCore();
            });
        }
    }

    initWithMobileCore() {
        // Кешуємо часто використовувані елементи
        this.cacheElements();

        // Ініціалізація систем
        this.setupNavigation();
        this.setupNavDropdown();
        this.setupMobileMenu();
        this.setupModals();
        this.setupPhoneMasks();
        this.setupForms();
        this.setupLanguageSwitcher();
        this.setupAccessibility();
        this.setupFooterAccordion();
        this.setupContactWidget();
        this.setupScrollStateDetection();

        // DOM ready actions
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.onDOMReady());
        } else {
            this.onDOMReady();
        }
    }

    cacheElements() {
        this.elements = {
            nav: document.querySelector('.main-navigation'),
            burgerBtn: document.querySelector('.burger-menu'),
            mobileMenu: document.querySelector('.mobile-menu'),
            mobileMenuClose: document.querySelector('.mobile-menu-close'),
            mobileNavLinks: document.querySelectorAll('.mobile-nav-link'),
            langDropdown: document.querySelector('.lang-dropdown'),
            langDropdownBtn: document.querySelector('.lang-dropdown-btn'),
            langSwitchers: document.querySelectorAll('.lang-switcher-link')
        };
    }

    onDOMReady() {
        // Ініціалізуємо PhoneMask для полів, які могли з'явитися після початкової ініціалізації
        this.initPhoneMasksForElement(document);
    }

    // ===== NAVIGATION SYSTEM =====
    setupNavigation() {
        if (!this.elements.nav) return;

        let ticking = false;
        let lastScrollTop = 0;
        let isScrolled = false;

        const handleScroll = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                    const shouldBeScrolled = scrollTop > this.config.scrollThreshold;

                    if (shouldBeScrolled !== isScrolled) {
                        this.elements.nav.classList.toggle('scrolled', shouldBeScrolled);
                        isScrolled = shouldBeScrolled;
                    }

                    lastScrollTop = scrollTop;
                    ticking = false;
                });
                ticking = true;
            }
        };

        window.addEventListener('scroll', handleScroll, { passive: true });
        handleScroll();

        this.setupSmoothScroll();
    }

    setupNavDropdown() {
        const dropdowns = document.querySelectorAll('.nav-dropdown');
        if (!dropdowns.length) return;

        const isDesktop = () => window.matchMedia('(min-width: 768px)').matches;
        let leaveTimer = null;

        dropdowns.forEach((dropdown) => {
            const toggle = dropdown.querySelector('.nav-dropdown__toggle');
            if (!toggle) return;

            dropdown.addEventListener('mouseenter', () => {
                if (!isDesktop()) return;
                clearTimeout(leaveTimer);
                dropdown.classList.add('is-open');
                toggle.setAttribute('aria-expanded', 'true');
            });

            dropdown.addEventListener('mouseleave', () => {
                if (!isDesktop()) return;
                leaveTimer = setTimeout(() => {
                    dropdown.classList.remove('is-open');
                    toggle.setAttribute('aria-expanded', 'false');
                }, 100);
            });

            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const isOpen = dropdown.classList.contains('is-open');
                this.closeAllNavDropdowns();
                if (!isOpen) {
                    dropdown.classList.add('is-open');
                    toggle.setAttribute('aria-expanded', 'true');
                }
            });
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.nav-dropdown')) {
                this.closeAllNavDropdowns();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllNavDropdowns();
            }
        });
    }

    closeAllNavDropdowns() {
        document.querySelectorAll('.nav-dropdown.is-open').forEach((dropdown) => {
            dropdown.classList.remove('is-open');
            const toggle = dropdown.querySelector('.nav-dropdown__toggle');
            if (toggle) toggle.setAttribute('aria-expanded', 'false');
        });
    }

    setupSmoothScroll() {
        const links = document.querySelectorAll('a[href^="#"]');

        links.forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                if (href === '#') return;

                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    const offsetTop = target.offsetTop - 80;
                    window.scrollTo({ top: offsetTop, behavior: 'smooth' });
                }
            }, { passive: false }); // НЕ passive через preventDefault
        });
    }

    setupScrollStateDetection() {
        let scrollTimeout;
        let isScrolling = false;
        
        const handleScroll = () => {
            if (!isScrolling) {
                document.body.classList.add('is-scrolling');
                isScrolling = true;
            }
            
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                document.body.classList.remove('is-scrolling');
                isScrolling = false;
            }, 100);
        };
        
        window.addEventListener('scroll', handleScroll, { passive: true, capture: true });
    }

    // ===== MOBILE MENU SYSTEM =====
    setupMobileMenu() {
        const { burgerBtn, mobileMenu, mobileMenuClose, mobileNavLinks } = this.elements;

        if (!burgerBtn || !mobileMenu) return;

        // Відкриття/закриття
        burgerBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleMobileMenu();
        });

        // Закриття через кнопку
        mobileMenuClose?.addEventListener('click', (e) => {
            e.preventDefault();
            this.closeMobileMenu();
        });

        // Закриття при кліку на посилання
        mobileNavLinks.forEach(link => {
            link.addEventListener('click', () => this.closeMobileMenu());
        });

        // Закриття при кліку на backdrop
        mobileMenu.addEventListener('click', (e) => {
            if (e.target === mobileMenu) this.closeMobileMenu();
        });

        // Закриття при ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.state.menuOpen) {
                this.closeMobileMenu();
            }
        });

        // Touch оптимізації для iOS
        if ('ontouchstart' in window) {
            this.setupMenuTouchOptimizations();
        }
    }

    setupMenuTouchOptimizations() {
        const { mobileMenu, mobileNavLinks } = this.elements;

        mobileMenu?.addEventListener('touchstart', (e) => {
            e.stopPropagation();
        }, { passive: true });

        mobileNavLinks.forEach(link => {
            link.addEventListener('touchstart', (e) => {
                e.stopPropagation();
            }, { passive: true });
        });
    }

    toggleMobileMenu() {
        if (this.state.menuOpen) {
            this.closeMobileMenu();
        } else {
            this.openMobileMenu();
        }
    }

    openMobileMenu() {
        const { burgerBtn, mobileMenu } = this.elements;

        this.saveScrollPosition();
        burgerBtn.classList.add('active');
        burgerBtn.setAttribute('aria-expanded', 'true');
        mobileMenu.classList.add('active');
        document.body.style.top = `-${this.scrollPosition}px`;
        document.body.style.overflow = 'hidden';
        document.body.classList.add('menu-open');

        this.state.menuOpen = true;

        this.emit('menu:opened');
    }

    closeMobileMenu() {
        const { burgerBtn, mobileMenu } = this.elements;

        burgerBtn.classList.remove('active');
        burgerBtn.setAttribute('aria-expanded', 'false');
        mobileMenu.classList.remove('active');
        document.body.style.overflow = '';
        document.body.style.top = '';
        document.body.classList.remove('menu-open');

        this.state.menuOpen = false;
        this.restoreScrollPosition();

        this.emit('menu:closed');
    }

    // ===== MODAL SYSTEM =====
    setupModals() {
        const isServiceModal = (el) => /^service-.+-modal$/.test(el?.id ?? '');

        const modalTriggers = document.querySelectorAll('[data-modal]');
        const closeButtons = document.querySelectorAll('.modal-close, .modal-close-specific');

        // Відкриття модалок
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.getAttribute('data-modal');
                this.openModal(modalId);
            });
        });

        // Закриття модалок
        closeButtons.forEach(button => {
            if (isServiceModal(button.closest('.modal'))) return;

            button.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = button.getAttribute('data-modal-id');
                this.closeModal(modalId);
            });
        });

        // Закриття при кліку на backdrop
        document.querySelectorAll('.modal').forEach(modal => {
            if (isServiceModal(modal)) return;

            modal.addEventListener('click', (e) => {
                if (e.target === modal || e.target.classList.contains('modal-backdrop')) {
                    this.closeModal(modal.id);
                }
            });
        });

        // Закриття при ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.state.activeModal) {
                this.closeModal();
            }
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        this.saveScrollPosition();
        
        // Ініціалізуємо PhoneMask для полів телефону в модальному вікні ПЕРЕД prefill
        this.initPhoneMasksForElement(modal);
        
        this.prefillModalForm(modal);

        if (modalId === 'call-request-modal') {
            const pageSrc = document.body.getAttribute('data-modal-source-page') || '';
            const sourceInput = document.getElementById('call-modal-source-page');
            if (sourceInput) {
                sourceInput.value = pageSrc;
            }
        }

        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
        document.body.classList.add('modal-open');
        document.body.style.top = `-${this.scrollPosition}px`;
        // overflow/position locked via body.modal-open CSS; modal-content scrolls

        this.state.activeModal = modalId;

        const firstInput = modal.querySelector('input:not([type="hidden"]), textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 300);
        }

        this.emit('modal:opened', { modalId });
    }

    closeModal(modalId = null) {
        const modal = modalId
            ? document.getElementById(modalId)
            : document.querySelector('.modal.active');

        if (!modal) return;

        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('modal-open');
        document.body.style.top = '';
        document.body.style.overflow = '';
        document.body.style.position = '';
        document.body.style.width = '';
        document.body.style.height = '';

        this.state.activeModal = null;
        this.restoreScrollPosition();

        this.emit('modal:closed', { modalId: modal.id });
    }

    prefillModalForm(modal) {
        const userData = this.getStoredUserData();
        if (!userData) return;

        const nameField = modal.querySelector('input[name="name"]');
        const phoneField = modal.querySelector('input[name="phone"]');

        if (nameField && userData.name) nameField.value = userData.name;
        
        // Для телефону використовуємо PhoneMask якщо він ініціалізований
        if (phoneField && userData.phone) {
            // Переконуємось що PhoneMask ініціалізований
            if (!this.phoneMasks.has(phoneField)) {
                // Якщо PhoneMask не ініціалізований, ініціалізуємо його
                this.initPhoneMasksForElement(modal);
            }
            
            if (this.phoneMasks.has(phoneField)) {
                // Якщо PhoneMask ініціалізований, встановлюємо значення через нього
                const mask = this.phoneMasks.get(phoneField);
                // Використовуємо formatValue для правильного форматування
                mask.formatValue(userData.phone);
            } else {
                // Якщо PhoneMask все ще не доступний, встановлюємо значення і форматуємо вручну
                phoneField.value = userData.phone;
                // Спробуємо ініціалізувати PhoneMask ще раз
                setTimeout(() => {
                    this._attachPhoneMask(phoneField);
                    const mask = this.phoneMasks.get(phoneField);
                    if (mask && typeof mask.formatValue === 'function') {
                        mask.formatValue(userData.phone);
                    }
                }, 0);
            }
        } else if (phoneField) {
            // Якщо немає збереженого телефону, переконуємось що +38 відображається
            if (!this.phoneMasks.has(phoneField)) {
                this.initPhoneMasksForElement(modal);
            }
            if (this.phoneMasks.has(phoneField)) {
                const mask = this.phoneMasks.get(phoneField);
                mask.ensurePrefix();
            }
        }
    }

    // ===== PHONE MASK SYSTEM =====
    setupPhoneMasks() {
        // Ініціалізуємо маску для всіх полів телефону
        this.initPhoneMasksForElement(document);
    }
    
    _useIntlPhoneMask(input) {
        // Маска обирається лише за мовою інтерфейсу, не за контейнером поля:
        // cs/en → вільний міжнародний формат, uk/ru → жорсткий український +38.
        const lang = (document.documentElement.getAttribute('lang') || 'uk').toLowerCase();
        const isIntlLang = lang.indexOf('cs') === 0 || lang.indexOf('en') === 0;
        return isIntlLang && typeof IntlPhoneMask !== 'undefined';
    }

    _attachPhoneMask(input) {
        if (this.phoneMasks.has(input)) return;
        if (this._useIntlPhoneMask(input)) {
            this.phoneMasks.set(input, new IntlPhoneMask(input));
        } else if (typeof PhoneMask !== 'undefined') {
            this.phoneMasks.set(input, new PhoneMask(input));
        }
    }

    initPhoneMasksForElement(container) {
        const phoneInputs = container.querySelectorAll('input[type="tel"]');
        phoneInputs.forEach((input) => this._attachPhoneMask(input));
    }
    
    /**
     * Відновлює префікс +38 для всіх полів телефону в формі після reset
     */
    restorePhonePrefixes(form) {
        const phoneInputs = form.querySelectorAll('input[type="tel"]');
        
        phoneInputs.forEach(input => {
            if (this.phoneMasks.has(input)) {
                const mask = this.phoneMasks.get(input);
                mask.ensurePrefix();
            } else {
                this._attachPhoneMask(input);
            }
        });
    }

    // ===== FORM SYSTEM =====
    setupForms() {
        const forms = document.querySelectorAll('form[data-form-type]');

        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmit(form);
            });

            // Додаємо обробники для очищення помилок при редагуванні
            const inputs = form.querySelectorAll('[required], [name="name"], [name="phone"]');
            inputs.forEach(input => {
                input.addEventListener('input', () => {
                    if (input.classList.contains('error')) {
                        input.classList.remove('error');
                        this.clearFieldError(input);
                    }
                });
            });
        });
    }

    async handleFormSubmit(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn?.textContent;

        // При помилці валідації на клієнті - форма НЕ очищається, відповіді залишаються
        if (!this.validateForm(form)) return;

        // Показуємо loading
        if (submitBtn) {
            submitBtn.classList.add('btn-loading');
            submitBtn.disabled = true;
        }

        try {
            const formData = new FormData(form);
            const formType = form.getAttribute('data-form-type');

            // Оновлюємо значення телефону з PhoneMask якщо доступний
            const phoneField = form.querySelector('[name="phone"]');
            if (phoneField && this.phoneMasks.has(phoneField)) {
                const mask = this.phoneMasks.get(phoneField);
                const cleanedValue = mask.getCleanedValue();
                formData.set('phone', cleanedValue);
            }

            // Зберігаємо дані користувача
            this.saveUserData(formData);

            // AJAX відправка
            const response = await this.submitForm(formData, formType);
            const data = await response.json();

            if (response.ok && data.success) {
                // Enhanced Conversions: phone for GTM before thank-you redirect
                if (data.redirect && window.ECPhone) {
                    window.ECPhone.saveFromRaw(formData.get('phone'));
                }

                // ТІЛЬКИ при успішній відправці - очищаємо форму
                // Для тесту - виклик спеціального очищення
                if (formType === 'test' && window.calculatorInstance) {
                    window.calculatorInstance.clearForm();
                } else {
                    form.reset();
                    // Після reset відновлюємо префікс +38 для всіх полів телефону
                    this.restorePhonePrefixes(form);
                }
                
                // КРИТИЧНО: Очищаємо збережені дані користувача після успішної відправки
                // щоб вони не з'являлися в інших формах
                // (не чіпає ec_phone — потрібен на /thank-you/ для Google Ads)
                this.clearUserData();

                this.closeModal();
                this.handleFormSuccess(data);
            } else {
                // При помилці від сервера - форма НЕ очищається, відповіді залишаються
                // Обробляємо помилку від сервера
                const errorMessage = data.message || (window.I18N?.errorSending || 'Помилка при відправці. Спробуйте ще раз.');
                
                // Перевіримо чи це помилка валідації конкретного поля
                if (errorMessage.includes('ім\'я') || errorMessage.includes('name') || errorMessage.includes('коректне ім')) {
                    const nameField = form.querySelector('[name="name"]');
                    if (nameField) {
                        nameField.classList.add('error');
                        this.showFieldError(nameField, errorMessage);
                    }
                } else if (errorMessage.includes('телефон') || errorMessage.includes('phone') || errorMessage.includes('номер')) {
                    const phoneField = form.querySelector('[name="phone"]');
                    if (phoneField) {
                        phoneField.classList.add('error');
                        this.showFieldError(phoneField, errorMessage);
                    }
                } else {
                    this.showNotification(errorMessage, 'error');
                }
            }

        } catch (error) {
            // При помилці мережі/винятку - форма НЕ очищається, відповіді залишаються
            console.error('Form error:', error);
            this.showNotification(window.I18N?.errorSubmittingForm || 'Помилка при відправці форми. Спробуйте ще раз.', 'error');
        } finally {
            if (submitBtn) {
                submitBtn.classList.remove('btn-loading');
                submitBtn.disabled = false;
                if (originalText) submitBtn.textContent = originalText;
            }
        }
    }

    validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (field.type === 'checkbox') {
                if (!field.checked) {
                    field.classList.add('error');
                    this.showFieldError(field, window.I18N?.fieldRequired || 'Це поле обов\'язкове');
                    isValid = false;
                } else {
                    field.classList.remove('error');
                    this.clearFieldError(field);
                }
                return;
            }
            if (!field.value.trim()) {
                field.classList.add('error');
                this.showFieldError(field, window.I18N?.fieldRequired || 'Це поле обов\'язкове');
                isValid = false;
            } else {
                field.classList.remove('error');
                this.clearFieldError(field);
            }
        });

        // Додаткова валідація для імені та телефону (як на сервері)
        const nameField = form.querySelector('[name="name"]');
        const phoneField = form.querySelector('[name="phone"]');
        const emailField = form.querySelector('[name="email"]');

        if (nameField && nameField.value) {
            const name = nameField.value.trim();
            let nameError = null;

            if (name.length < 2) {
                nameError = window.I18N?.nameMinLength || 'Введіть коректне ім\'я (мінімум 2 символи)';
            } else if (/^\d+$/.test(name)) {
                nameError = window.I18N?.nameDigitsOnly || 'Ім\'я не може складатися тільки з цифр';
            } else if (!/\p{L}/u.test(name)) {
                nameError = window.I18N?.nameNeedsLetter || 'Введіть коректне ім\'я (хоча б одна літера)';
            }

            if (nameError) {
                nameField.classList.add('error');
                this.showFieldError(nameField, nameError);
                isValid = false;
            } else {
                nameField.classList.remove('error');
                this.clearFieldError(nameField);
            }
        }

        if (emailField) {
            const email = (emailField.value || '').trim();
            const mustHave = emailField.hasAttribute('required');
            if (mustHave || email) {
                const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
                if (!emailOk) {
                    emailField.classList.add('error');
                    this.showFieldError(emailField, window.I18N?.emailInvalid || 'Введіть коректний email');
                    isValid = false;
                } else {
                    emailField.classList.remove('error');
                    this.clearFieldError(emailField);
                }
            }
        }

        if (phoneField && phoneField.value) {
            const digitsOnly = phoneField.value.replace(/\D/g, '');
            // Порожній або лише префікс (+38 / +420) — для lead-форм ок
            const isPrefixOnly = digitsOnly.length <= 3;
            if (!isPrefixOnly) {
                let phoneError = null;

                if (this.phoneMasks.has(phoneField)) {
                    const mask = this.phoneMasks.get(phoneField);
                    const validation = mask.validate();

                    if (!validation.valid) {
                        phoneError = validation.message;
                    }
                } else if (digitsOnly.length < 7) {
                    phoneError = window.I18N?.phoneInvalid || 'Введіть коректний номер телефону';
                }

                if (phoneError) {
                    phoneField.classList.add('error');
                    this.showFieldError(phoneField, phoneError);
                    isValid = false;
                } else {
                    phoneField.classList.remove('error');
                    this.clearFieldError(phoneField);
                }
            }
        }

        const telegramField = form.querySelector('[name="telegram"]');
        if (telegramField && telegramField.value.trim()) {
            let tg = telegramField.value.trim().replace(/^@+/, '');
            if (tg.startsWith('https://t.me/') || tg.startsWith('http://t.me/')) {
                tg = tg.replace(/\/$/, '').split('/').pop();
            }
            telegramField.value = tg;
            if (!/^[A-Za-z0-9_]{5,32}$/.test(tg)) {
                telegramField.classList.add('error');
                this.showFieldError(telegramField, window.I18N?.telegramInvalid || 'Zadejte platný Telegram (@username).');
                isValid = false;
            } else {
                telegramField.classList.remove('error');
                this.clearFieldError(telegramField);
            }
        }

        // FAIL-CLOSED contact rule for shared lead fields
        if (form.querySelector('[data-lead-form-fields]')) {
            const phoneDigits = phoneField ? phoneField.value.replace(/\D/g, '') : '';
            const phoneOk = phoneDigits.length >= 7;
            const emailOk = emailField && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test((emailField.value || '').trim());
            const tgRaw = telegramField ? telegramField.value.trim().replace(/^@+/, '') : '';
            const tgOk = /^[A-Za-z0-9_]{5,32}$/.test(tgRaw);
            const ruleEl = form.querySelector('[data-lead-contact-rule]');
            if (!(phoneOk || emailOk || tgOk)) {
                const msg = window.I18N?.contactRule || 'Zadejte telefon, e-mail nebo Telegram.';
                if (ruleEl) {
                    ruleEl.hidden = false;
                    ruleEl.textContent = msg;
                    ruleEl.classList.add('lead-form-contact-rule--error');
                }
                isValid = false;
            } else if (ruleEl) {
                ruleEl.hidden = true;
                ruleEl.textContent = '';
                ruleEl.classList.remove('lead-form-contact-rule--error');
            }
        }

        return isValid;
    }

    showFieldError(field, message) {
        const errorEl = field.parentElement?.querySelector('.calc-field__error')
            || field.closest('.form-group')?.querySelector('.lead-form-contact-rule');
        if (errorEl && errorEl.hasAttribute && errorEl.hasAttribute('data-lead-contact-rule')) {
            errorEl.hidden = false;
            errorEl.textContent = message;
            errorEl.classList.add('lead-form-contact-rule--error');
            return;
        }
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.add('show');
        }
    }

    clearFieldError(field) {
        const errorEl = field.parentElement?.querySelector('.calc-field__error');
        if (errorEl) {
            errorEl.textContent = '';
            errorEl.classList.remove('show');
        }
    }

    localizedFormUrl(path) {
        const lang = (document.documentElement.lang || 'uk').split('-')[0].toLowerCase();
        if (!lang || lang === 'uk') return path;
        return `/${lang}${path}`;
    }

    async submitForm(formData, formType) {
        const raw = formType === 'test' ? '/forms/test/' : '/forms/submit/';
        const url = this.localizedFormUrl(raw);

        if (formType !== 'test') {
            formData.append('form_type', formType);
        }

        if (window.GCLIDCapture) {
            window.GCLIDCapture.appendToFormData(formData);
        }

        return fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            }
        });
    }

    handleFormSuccess(data) {
        if (data.redirect) {
            window.location.href = data.redirect;
        }
    }

    // ===== LANGUAGE SWITCHER =====
    setupLanguageSwitcher() {
        const { langDropdown, langDropdownBtn, langSwitchers } = this.elements;

        // Dropdown toggle
        langDropdownBtn?.addEventListener('click', (e) => {
            e.preventDefault();
            langDropdown?.classList.toggle('active');
        });

        // Close dropdown при кліку поза
        document.addEventListener('click', (e) => {
            if (langDropdown && !langDropdown.contains(e.target)) {
                langDropdown.classList.remove('active');
            }
        });

        // Language switcher links
        langSwitchers.forEach(switcher => {
            switcher.addEventListener('click', (e) => {
                e.preventDefault();
                const langCode = switcher.getAttribute('data-language-code');
                if (langCode) this.setLanguage(langCode);
            });
        });
    }

    setLanguage(langCode) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/i18n/set_language/';

        // CSRF token
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = this.getCSRFToken();
        form.appendChild(csrfInput);

        // Language
        const langInput = document.createElement('input');
        langInput.type = 'hidden';
        langInput.name = 'language';
        langInput.value = langCode;
        form.appendChild(langInput);

        // Next URL - видаляємо префікс мови якщо є
        let nextUrl = window.location.pathname + window.location.search;
        const originalUrl = nextUrl;
        // Видаляємо мовний префікс (/en/, /ru/, /cs/) — uk не має префікса
        nextUrl = nextUrl.replace(/^\/(en|ru|cs)\//, '/');

        const nextInput = document.createElement('input');
        nextInput.type = 'hidden';
        nextInput.name = 'next';
        nextInput.value = nextUrl;
        form.appendChild(nextInput);

        document.body.appendChild(form);
        form.submit();
    }

    // ===== ACCESSIBILITY =====
    setupAccessibility() {
        const animatedElements = document.querySelectorAll('.animate-on-scroll');

        if (animatedElements.length === 0) return;
        if (!('IntersectionObserver' in window)) {
            animatedElements.forEach(el => el.classList.add('visible'));
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    
                    setTimeout(() => {
                        entry.target.classList.add('animated');
                    }, 600);
                    
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.05,
            rootMargin: '0px 0px -20px 0px'
        });

        animatedElements.forEach(el => observer.observe(el));
    }

    // ===== FOOTER ACCORDION (Mobile) =====
    setupFooterAccordion() {
        const footerSections = document.querySelectorAll('.footer-section:not(.footer-form-section)');
        
        if (footerSections.length === 0) return;

        footerSections.forEach(section => {
            const heading = section.querySelector('h3');
            if (!heading) return;

            heading.addEventListener('click', () => {
                // Тільки на мобільних пристроях (< 768px)
                if (window.innerWidth >= 768) return;

                // Toggle активного стану
                section.classList.toggle('footer-accordion-active');

                // Emit подію для аналітики
                this.emit('footer:accordion-toggle', {
                    section: heading.textContent,
                    isOpen: section.classList.contains('footer-accordion-active')
                });
            });
        });

        // Закриваємо всі акордеони при зміні розміру на desktop
        window.addEventListener('resize', () => {
            if (window.innerWidth >= 768) {
                footerSections.forEach(section => {
                    section.classList.remove('footer-accordion-active');
                });
            }
        });
    }

    // ===== CONTACT WIDGET =====
    setupContactWidget() {
        const widget = document.getElementById('contact-widget');
        const toggle = document.getElementById('contact-widget-toggle');
        const panel  = document.getElementById('contact-widget-panel');

        if (!widget || !toggle || !panel) return;

        const openWidget = () => {
            widget.classList.add('contact-widget--open');
            toggle.setAttribute('aria-expanded', 'true');
            panel.setAttribute('aria-hidden', 'false');
        };

        const closeWidget = () => {
            widget.classList.remove('contact-widget--open');
            toggle.setAttribute('aria-expanded', 'false');
            panel.setAttribute('aria-hidden', 'true');
        };

        const isWidgetOpen = () => widget.classList.contains('contact-widget--open');

        toggle.addEventListener('click', () => {
            isWidgetOpen() ? closeWidget() : openWidget();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && isWidgetOpen()) closeWidget();
        });

        document.addEventListener('click', (e) => {
            if (isWidgetOpen() && !widget.contains(e.target)) closeWidget();
        });
    }

    // ===== SCROLL POSITION MANAGEMENT =====
    saveScrollPosition() {
        this.scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
    }

    restoreScrollPosition() {
        if (this.scrollPosition !== undefined) {
            window.scrollTo({
                top: this.scrollPosition,
                behavior: 'auto'
            });
        }
    }

    // ===== UTILITY METHODS =====
    getCSRFToken() {
        // Використовуємо Utils якщо доступний
        if (window.PrometeyUtils?.getCSRFToken) {
            return window.PrometeyUtils.getCSRFToken();
        }

        // 1. Спробуємо з meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            const token = metaTag.getAttribute('content');
            if (token) return token;
        }

        // 2. Fallback на input
        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        if (input) return input.value;

        // 3. Fallback на cookie
        const match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }

    saveUserData(formData) {
        const userData = {
            name: formData.get('name'),
            phone: formData.get('phone'),
            timestamp: Date.now()
        };

        try {
            sessionStorage.setItem('prometey_user_data', JSON.stringify(userData));
        } catch (error) {
            console.error('Failed to save user data:', error);
        }
    }

    getStoredUserData() {
        try {
            const data = sessionStorage.getItem('prometey_user_data');
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Failed to get user data:', error);
            return null;
        }
    }
    
    /**
     * Очищає збережені дані користувача з sessionStorage
     */
    clearUserData() {
        try {
            sessionStorage.removeItem('prometey_user_data');
        } catch (error) {
            console.error('Failed to clear user data:', error);
        }
    }

    // ===== EVENT BUS =====
    emit(eventName, data = null) {
        const event = new CustomEvent(eventName, { detail: data });
        document.dispatchEvent(event);
        window.dispatchEvent(event);
    }

    on(eventName, callback) {
        document.addEventListener(eventName, callback);
    }

    off(eventName, callback) {
        document.removeEventListener(eventName, callback);
    }

    // ===== STATIC METHOD =====
    static getInstance() {
        if (!window.prometeyApp) {
            window.prometeyApp = new PrometeyApp();
        }
        return window.prometeyApp;
    }
}

// ===== NOTIFICATION STYLES (одноразове додавання) =====
const notificationStyles = document.createElement('style');
notificationStyles.id = 'prometey-notification-styles';
notificationStyles.textContent = `
.prometey-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10000;
    padding: 15px 20px;
    background: var(--color-white);
    border: 2px solid var(--color-brand-orange);
    font-weight: 600;
    font-size: var(--font-base);
    transform: translateX(400px);
    transition: transform var(--transition-normal) var(--easing-default);
    display: flex;
    align-items: center;
    gap: 10px;
    box-shadow: var(--shadow-lg);
}

.prometey-notification--show {
    transform: translateX(0);
}

.prometey-notification--error {
    border-color: var(--color-brand-orange);
    color: var(--color-brand-orange);
    background: #ffebee;
}

.prometey-notification__close {
    background: none;
    border: none;
    font-size: 20px;
    line-height: 1;
    cursor: pointer;
    color: inherit;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform var(--transition-fast) var(--easing-default);
}

.prometey-notification__close:hover {
    transform: rotate(90deg);
}

@media (max-width: 767px) {
    .prometey-notification {
        top: 20px;
        right: var(--space-xs);
        left: var(--space-xs);
        width: calc(100% - var(--space-xs) * 2);
        max-width: none;
        font-size: var(--font-small);
        padding: 12px 16px;
    }
}
`;

if (!document.getElementById('prometey-notification-styles')) {
    document.head.appendChild(notificationStyles);
}

// ===== ІНІЦІАЛІЗАЦІЯ =====
const app = PrometeyApp.getInstance();

// Експорт
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PrometeyApp;
}
