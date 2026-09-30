/* corporate-website-v2-quiz.js — multi-step calculator + package recommendation */

(function () {
    'use strict';

    var form = document.getElementById('pl-corp-quiz-form');
    if (!form) return;

    var lang = (document.documentElement.lang || 'uk').split('-')[0].toLowerCase();

    var PKG_MAP_BY_LANG = {
        uk: {
            starter: {
                label: 'СТАРТОВИЙ',
                term: '5–7 днів',
                features: [
                    '1-сторінковий лендинг під бренд',
                    'Базове SEO та форма заявки',
                    'Інтеграція Telegram або CRM',
                    'Адаптивна мобільна версія'
                ]
            },
            corporate: {
                label: 'КОРПОРАТИВНИЙ',
                term: '2–3 тижні',
                features: [
                    '5–9 сторінок, блог для SEO',
                    'Розширене SEO та Core Web Vitals',
                    'CRM + Google Ads у пакеті',
                    'Каталог послуг або продукції'
                ]
            },
            premium: {
                label: 'БІЗНЕС-ПРЕМІУМ',
                term: '3–6 тижнів',
                features: [
                    '10+ сторінок, мультимовність',
                    'Інтеграція 1С / Bitrix24',
                    'Маркетинг під ключ: Google, Meta, TikTok',
                    'SEO-просування та складний функціонал'
                ]
            }
        },
        cs: {
            starter: {
                label: 'START',
                term: '5–7 dní',
                features: [
                    'Jednostránkový landing na míru značky',
                    'Základní SEO a poptávkový formulář',
                    'Integrace Telegram nebo CRM',
                    'Responzivní mobilní verze'
                ]
            },
            corporate: {
                label: 'FIREMNÍ',
                term: '2–3 týdny',
                features: [
                    '5–9 stránek, blog pro SEO',
                    'Rozšířené SEO a Core Web Vitals',
                    'CRM + Google Ads v balíčku',
                    'Katalog služeb nebo produktů'
                ]
            },
            premium: {
                label: 'BUSINESS PREMIUM',
                term: '3–6 týdnů',
                features: [
                    '10+ stránek, vícejazyčnost',
                    'Integrace Pohoda / Money S3 / ABRA',
                    'Marketing na klíč: Google, Meta, TikTok',
                    'SEO propagace a pokročilé funkce'
                ]
            }
        },
        en: {
            starter: {
                label: 'STARTER',
                term: '5–7 days',
                features: [
                    'One-page landing for your brand',
                    'Basic SEO and lead form',
                    'Telegram or CRM integration',
                    'Responsive mobile version'
                ]
            },
            corporate: {
                label: 'CORPORATE',
                term: '2–3 weeks',
                features: [
                    '5–9 pages, blog for SEO',
                    'Advanced SEO and Core Web Vitals',
                    'CRM + Google Ads included',
                    'Services or product catalog'
                ]
            },
            premium: {
                label: 'BUSINESS PREMIUM',
                term: '3–6 weeks',
                features: [
                    '10+ pages, multilingual',
                    'Pohoda / Money S3 / ABRA integration',
                    'Turnkey marketing: Google, Meta, TikTok',
                    'SEO growth and advanced features'
                ]
            }
        }
    };
    PKG_MAP_BY_LANG.ru = PKG_MAP_BY_LANG.uk;
    var PKG_MAP = PKG_MAP_BY_LANG[lang] || PKG_MAP_BY_LANG.uk;

    var steps = Array.from(form.querySelectorAll('.pl-corp__quiz-step'));
    var stage = form.querySelector('.pl-corp__quiz-stage');
    var progressBar = form.querySelector('[data-quiz-progress]');
    var stepNumEl = form.querySelector('[data-quiz-step-num]');
    var prevBtn = form.querySelector('.pl-corp__quiz-prev');
    var prevResultBtn = form.querySelector('.pl-corp__quiz-prev-result');
    var skipBtn = form.querySelector('.pl-corp__quiz-skip');
    var nextBtn = form.querySelector('.pl-corp__quiz-next');
    var navDiv = form.querySelector('.pl-corp__quiz-nav');
    var revealBtn = form.querySelector('[data-quiz-reveal]');
    var nameInput = form.querySelector('#pl-corp-quiz-name');
    var phoneInput = form.querySelector('#pl-corp-quiz-phone');
    var detailsInput = document.getElementById('pl-corp-quiz-details');
    var resultRoot = form.querySelector('[data-quiz-result]');

    var QUESTION_STEPS = steps.filter(function (s) {
        return !s.classList.contains('pl-corp__quiz-step--contact')
            && !s.classList.contains('pl-corp__quiz-step--result');
    }).length;

    var resultStepIdx = steps.findIndex(function (s) {
        return s.classList.contains('pl-corp__quiz-step--result');
    });

    var currentIdx = 0;
    var resizeTimer;
    var lockedStageHeight = 0;
    var isMeasuring = false;

    function setNavSlot(btn, visible) {
        if (!btn) return;
        btn.classList.toggle('pl-corp__quiz-nav-slot--hidden', !visible);
        btn.setAttribute('aria-hidden', visible ? 'false' : 'true');
        btn.tabIndex = visible ? 0 : -1;
    }

    var questionSteps = steps.filter(function (s) {
        return !s.classList.contains('pl-corp__quiz-step--contact')
            && !s.classList.contains('pl-corp__quiz-step--result');
    });

    function measureStageHeight() {
        if (!stage || !steps.length || isMeasuring) return;

        isMeasuring = true;
        var activeIdx = currentIdx;
        var max = 0;
        var measureSteps = questionSteps.length ? questionSteps : steps;

        stage.classList.add('pl-corp__quiz-stage--measure');
        stage.style.removeProperty('height');
        stage.style.removeProperty('min-height');
        form.style.removeProperty('--pl-corp-quiz-stage-h');

        measureSteps.forEach(function (step) {
            steps.forEach(function (item) {
                item.classList.remove('pl-corp__quiz-step--active', 'pl-corp__quiz-step--measure-target');
            });
            step.classList.add('pl-corp__quiz-step--active', 'pl-corp__quiz-step--measure-target');
            max = Math.max(max, stage.offsetHeight);
        });

        stage.classList.remove('pl-corp__quiz-stage--measure');
        lockedStageHeight = Math.max(lockedStageHeight, max);
        applyStageHeight();
        showStep(activeIdx);
        isMeasuring = false;
    }

    function applyStageHeight() {
        if (!stage) return;

        var currentStep = steps[currentIdx];
        var isFluidStep = currentStep && (
            currentStep.classList.contains('pl-corp__quiz-step--contact')
            || currentStep.classList.contains('pl-corp__quiz-step--result')
        );

        stage.classList.toggle('pl-corp__quiz-stage--fluid', !!isFluidStep);

        if (isFluidStep) {
            stage.style.height = 'auto';
            stage.style.minHeight = '0';
            form.style.removeProperty('--pl-corp-quiz-stage-h');
            return;
        }

        stage.classList.remove('pl-corp__quiz-stage--fluid');

        if (!lockedStageHeight) return;
        var heightValue = lockedStageHeight + 'px';
        stage.style.height = heightValue;
        stage.style.minHeight = heightValue;
        form.style.setProperty('--pl-corp-quiz-stage-h', heightValue);
    }

    function scheduleMeasure() {
        if (isMeasuring) return;
        window.clearTimeout(resizeTimer);
        resizeTimer = window.setTimeout(measureStageHeight, 60);
    }

    function countDigits(str) {
        return (str.match(/\d/g) || []).length;
    }

    function getCheckedValue(name) {
        var input = form.querySelector('input[name="' + name + '"]:checked');
        return input ? input.value : null;
    }

    function getCheckedValues(name) {
        return Array.from(form.querySelectorAll('input[name="' + name + '"]:checked'))
            .map(function (input) { return input.value; });
    }

    function getCheckedOptions() {
        return getCheckedValues('q_options');
    }

    function recommendPackage() {
        var score = { starter: 0, corporate: 0, premium: 0 };
        var business = getCheckedValue('q_business');
        var goal = getCheckedValue('q_goal');
        var pages = getCheckedValue('q_pages');
        var options = getCheckedOptions();
        var timeline = getCheckedValue('q_timeline');

        if (pages === '1 сторінка (лендинг)') score.starter += 4;
        if (pages === 'до 10 сторінок') score.corporate += 4;
        if (pages === '11–20 сторінок') score.premium += 3;
        if (pages === '21+ сторінок') score.premium += 5;

        if (business === 'Виробництво / опт') score.corporate += 1;
        if (business === 'Торгівля') score.corporate += 1;
        if (business === 'Інше / не визначився') score.corporate += 1;

        if (goal === 'Збір заявок та контактів') score.starter += 2;
        if (goal === 'Презентація бренду або послуг') score.corporate += 2;
        if (goal === 'Прямі онлайн-продажі') score.corporate += 2;
        if (goal === 'Масштабування') score.premium += 3;

        options.forEach(function (option) {
            if (option === 'Рекламні послуги' || option === 'SEO розвиток сайту') {
                score.corporate += 2;
            }
            if (option === 'CRM та автоматизація') score.corporate += 2;
            if (option === 'Мультимовність') score.premium += 3;
        });

        if (timeline === 'Якнайшвидше (до 7 днів)') score.starter += 3;
        if (timeline === 'Протягом 2 тижнів') score.corporate += 2;
        if (timeline === 'Протягом місяця') score.corporate += 1;
        if (timeline === 'Терміни гнучкі') score.premium += 2;

        var best = 'corporate';
        var bestScore = -1;
        Object.keys(score).forEach(function (key) {
            if (score[key] > bestScore) {
                bestScore = score[key];
                best = key;
            }
        });

        return best;
    }

    function updateResultPreview(pkgKey) {
        var data = PKG_MAP[pkgKey];
        if (!data || !resultRoot) return;

        var pkgEl = resultRoot.querySelector('[data-quiz-result-pkg]');
        var termEl = resultRoot.querySelector('[data-quiz-result-term]');
        var featuresEl = resultRoot.querySelector('[data-quiz-result-features]');

        if (pkgEl) pkgEl.textContent = data.label;
        if (termEl) termEl.textContent = data.term;

        if (featuresEl) {
            featuresEl.innerHTML = '';
            data.features.forEach(function (text) {
                var li = document.createElement('li');
                li.textContent = text;
                featuresEl.appendChild(li);
            });
            scheduleMeasure();
        }
    }

    function isStepAnswered(step) {
        return !!step.querySelector('input[type="radio"]:checked, input[type="checkbox"]:checked');
    }

    function isQuestionStep(step) {
        return step
            && !step.classList.contains('pl-corp__quiz-step--contact')
            && !step.classList.contains('pl-corp__quiz-step--result');
    }

    function showPhoneError(message) {
        if (!phoneInput) return;
        phoneInput.classList.add('error');
        var existing = phoneInput.parentElement.querySelector('.pl-corp__quiz-field-error');
        if (existing) existing.remove();
        var err = document.createElement('p');
        err.className = 'pl-corp__quiz-field-error';
        err.setAttribute('role', 'alert');
        err.textContent = message;
        phoneInput.parentElement.appendChild(err);
    }

    function clearPhoneError() {
        if (!phoneInput) return;
        phoneInput.classList.remove('error');
        var existing = phoneInput.parentElement.querySelector('.pl-corp__quiz-field-error');
        if (existing) existing.remove();
    }

    function validateContactFields() {
        var valid = true;
        var emailInput = form.querySelector('#pl-corp-quiz-email');
        var phoneInputLocal = form.querySelector('#pl-corp-quiz-phone');
        var telegramInput = form.querySelector('#pl-corp-quiz-telegram');
        var consentInput = form.querySelector('[name="consent"]');
        var nameInputLocal = form.querySelector('#pl-corp-quiz-name');
        var ruleEl = form.querySelector('[data-lead-contact-rule]');

        if (nameInputLocal && nameInputLocal.value.trim()) {
            if (nameInputLocal.value.trim().length < 2) {
                nameInputLocal.reportValidity();
                return false;
            }
        }
        if (emailInput && emailInput.value.trim() && !emailInput.checkValidity()) {
            emailInput.reportValidity();
            return false;
        }
        if (consentInput && !consentInput.checked) {
            consentInput.reportValidity();
            return false;
        }
        var phoneDigits = phoneInputLocal ? phoneInputLocal.value.replace(/\D/g, '') : '';
        var phoneOk = phoneDigits.length >= 7;
        var emailOk = emailInput && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test((emailInput.value || '').trim());
        var tg = telegramInput ? telegramInput.value.trim().replace(/^@+/, '') : '';
        if (telegramInput) telegramInput.value = tg;
        var tgOk = /^[A-Za-z0-9_]{5,32}$/.test(tg);
        if (tg && !tgOk) {
            if (ruleEl) {
                ruleEl.hidden = false;
                ruleEl.textContent = form.getAttribute('data-error-phone-invalid') || (window.I18N && window.I18N.telegramInvalid) || 'Zadejte platný Telegram (@username).';
                ruleEl.classList.add('lead-form-contact-rule--error');
            }
            return false;
        }
        if (!(phoneOk || emailOk || tgOk)) {
            var msg = form.getAttribute('data-error-contact-rule') || (window.I18N && window.I18N.contactRule) || 'Zadejte telefon, e-mail nebo Telegram.';
            if (ruleEl) {
                ruleEl.hidden = false;
                ruleEl.textContent = msg;
                ruleEl.classList.add('lead-form-contact-rule--error');
            }
            return false;
        }
        if (ruleEl) {
            ruleEl.hidden = true;
            ruleEl.textContent = '';
            ruleEl.classList.remove('lead-form-contact-rule--error');
        }
        return valid;
    }

    function compileDetails() {
        if (!detailsInput) return;

        var pkgKey = recommendPackage();
        var data = PKG_MAP[pkgKey];
        var fields = [
            { name: 'q_business', label: 'Тип бізнесу' },
            { name: 'q_goal', label: 'Бізнес-ціль' },
            { name: 'q_pages', label: 'Кількість сторінок' },
            { name: 'q_options', label: 'Додаткові опції', multi: true },
            { name: 'q_timeline', label: 'Терміни' }
        ];

        var parts = ['Сторінка: ' + (form.dataset.sourceLabel || 'Корпоративний сайт v2')];

        if (data) {
            parts.push('Рекомендований пакет: ' + data.label + ' · ' + data.term);
        }

        fields.forEach(function (field) {
            if (field.multi) {
                var vals = getCheckedValues(field.name);
                if (vals.length) parts.push(field.label + ': ' + vals.join(', '));
                return;
            }
            var val = getCheckedValue(field.name);
            if (val) parts.push(field.label + ': ' + val);
        });

        detailsInput.value = parts.join('\n');
    }

    function showStep(idx) {
        currentIdx = idx;

        steps.forEach(function (s, i) {
            var isActive = i === idx;
            s.classList.toggle('pl-corp__quiz-step--active', isActive);
            s.removeAttribute('hidden');
            s.setAttribute('aria-hidden', isActive ? 'false' : 'true');
        });

        applyStageHeight();

        var currentStep = steps[idx];
        var isContact = currentStep && currentStep.classList.contains('pl-corp__quiz-step--contact');
        var isResult = currentStep && currentStep.classList.contains('pl-corp__quiz-step--result');
        var isQuestion = isQuestionStep(currentStep);
        var stepNum = isResult ? QUESTION_STEPS : (isContact ? QUESTION_STEPS : idx + 1);
        var progress = (isContact || isResult) ? 100 : ((idx + 1) / QUESTION_STEPS) * 100;

        if (progressBar) progressBar.style.width = progress + '%';
        if (stepNumEl) stepNumEl.textContent = String(stepNum);

        var showPrev = idx > 0 && !isResult;
        var showNext = isQuestion;
        var showSkip = isQuestion;

        if (navDiv) navDiv.hidden = isResult || (!showPrev && !showNext && !showSkip);

        setNavSlot(prevBtn, showPrev);
        setNavSlot(skipBtn, showSkip);

        if (nextBtn) {
            setNavSlot(nextBtn, showNext);
            if (showNext) {
                nextBtn.disabled = !isStepAnswered(currentStep);
            }
        }
    }

    function prepareSubmit() {
        compileDetails();
    }

    function goNext() {
        var currentStep = steps[currentIdx];
        if (!isQuestionStep(currentStep)) return;
        if (!isStepAnswered(currentStep)) return;
        if (currentIdx < steps.length - 1) showStep(currentIdx + 1);
    }

    function goSkip() {
        var currentStep = steps[currentIdx];
        if (!isQuestionStep(currentStep)) return;
        if (currentIdx < steps.length - 1) showStep(currentIdx + 1);
    }

    function goPrev() {
        if (currentIdx > 0) showStep(currentIdx - 1);
    }

    function handleMultiChange(input, step) {
        var option = input.closest('.pl-corp__quiz-option');
        if (option) option.classList.toggle('pl-corp__quiz-option--selected', input.checked);

        if (nextBtn) {
            var anyChecked = step.querySelector('input[type="checkbox"]:checked');
            nextBtn.disabled = !anyChecked;
        }
    }

    form.addEventListener('change', function (e) {
        var input = e.target;
        if (input.type !== 'radio' && input.type !== 'checkbox') return;

        var step = input.closest('.pl-corp__quiz-step');
        if (!step || !isQuestionStep(step)) return;

        var isMulti = step.dataset.multi === 'true';

        if (isMulti) {
            handleMultiChange(input, step);
            return;
        }

        step.querySelectorAll('.pl-corp__quiz-option').forEach(function (opt) {
            opt.classList.remove('pl-corp__quiz-option--selected');
        });
        var selected = input.closest('.pl-corp__quiz-option');
        if (selected) selected.classList.add('pl-corp__quiz-option--selected');
        if (nextBtn) nextBtn.disabled = false;
    });

    form.addEventListener('submit', function () {
        compileDetails();
    });

    if (phoneInput) {
        phoneInput.addEventListener('input', clearPhoneError);
    }

    if (revealBtn) revealBtn.addEventListener('click', prepareSubmit);
    if (prevResultBtn) prevResultBtn.addEventListener('click', goPrev);
    if (skipBtn) skipBtn.addEventListener('click', goSkip);
    if (nextBtn) nextBtn.addEventListener('click', goNext);
    if (prevBtn) prevBtn.addEventListener('click', goPrev);

    showStep(0);
    measureStageHeight();

    window.addEventListener('resize', scheduleMeasure, { passive: true });

    if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(measureStageHeight);
    }
})();
