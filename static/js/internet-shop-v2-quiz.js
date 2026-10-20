/* internet-shop-v2-quiz.js — multi-step quiz + package recommendation */

(function () {
    'use strict';

    var form = document.getElementById('pl-shop-quiz-form');
    if (!form) return;

    var lang = (document.documentElement.lang || 'cs').split('-')[0].toLowerCase();

    var PKG_MAP_BY_LANG = {
        cs: {
            base: {
                label: 'BASE',
                price: 'od 1\u00a0400\u00a0€',
                term: '3–4 týdny',
                features: [
                    'Základní konverzní design pro vaši niku',
                    'AI obsah a základní SEO příprava',
                    'Nasazení na klíč na vaší doméně'
                ]
            },
            premium: {
                label: 'PREMIUM',
                price: 'od 2\u00a0800\u00a0€',
                term: '5–8 týdnů',
                features: [
                    'Individuální UI/UX design od nuly',
                    'Integrace: platby, logistika, CRM',
                    'Content marketing a SEO články'
                ]
            },
            platinum: {
                label: 'PLATINUM',
                price: 'od 8\u00a0000\u00a0€',
                term: '2–4 měsíce',
                features: [
                    'Premium UI/UX + filmové animace',
                    'AI ekosystém administrace a Telegram bot',
                    '6 měsíců content marketingu a mediakampaní'
                ]
            }
        },
        en: {
            base: {
                label: 'BASE',
                price: 'from €1,400',
                term: '3–4 weeks',
                features: [
                    'Conversion-focused design for your niche',
                    'AI content and basic SEO setup',
                    'Turnkey deploy on your domain'
                ]
            },
            premium: {
                label: 'PREMIUM',
                price: 'from €2,800',
                term: '5–8 weeks',
                features: [
                    'Custom UI/UX design from scratch',
                    'Integrations: payments, logistics, CRM',
                    'Content marketing and SEO articles'
                ]
            },
            platinum: {
                label: 'PLATINUM',
                price: 'from €8,000',
                term: '2–4 months',
                features: [
                    'Premium UI/UX + cinematic animation',
                    'Admin AI ecosystem and Telegram bot',
                    '6 months of content marketing and media campaigns'
                ]
            }
        }
    };
    var PKG_MAP = PKG_MAP_BY_LANG[lang] || PKG_MAP_BY_LANG.cs;

    var steps = Array.from(form.querySelectorAll('.pl-shop__quiz-step'));
    var progressBar = form.querySelector('[data-quiz-progress]');
    var stepNumEl = form.querySelector('[data-quiz-step-num]');
    var prevBtn = form.querySelector('.pl-shop__quiz-prev');
    var skipBtn = form.querySelector('.pl-shop__quiz-skip');
    var nextBtn = form.querySelector('.pl-shop__quiz-next');
    var navDiv = form.querySelector('.pl-shop__quiz-nav');
    var revealBtn = form.querySelector('[data-quiz-reveal]');
    var nameInput = form.querySelector('#pl-shop-quiz-name');
    var phoneInput = form.querySelector('#pl-shop-quiz-phone');
    var detailsInput = document.getElementById('pl-shop-quiz-details');
    var resultRoot = form.querySelector('[data-quiz-result]');

    var QUESTION_STEPS = steps.filter(function (s) {
        return !s.classList.contains('pl-shop__quiz-step--contact')
            && !s.classList.contains('pl-shop__quiz-step--result');
    }).length;

    var resultStepIdx = steps.findIndex(function (s) {
        return s.classList.contains('pl-shop__quiz-step--result');
    });

    var currentIdx = 0;

    function getPkgHint() {
        try {
            return sessionStorage.getItem('pl_shop_pkg_hint');
        } catch (e) {
            return null;
        }
    }

    function clearPkgHint() {
        try {
            sessionStorage.removeItem('pl_shop_pkg_hint');
        } catch (e) { /* ignore */ }
    }

    function getCheckedValue(name) {
        var input = form.querySelector('input[name="' + name + '"]:checked');
        return input ? input.value : null;
    }

    function getCheckedFeatures() {
        return Array.from(form.querySelectorAll('input[name="q_features"]:checked'))
            .map(function (cb) { return cb.value; });
    }

    function recommendPackage() {
        var score = { base: 0, premium: 0, platinum: 0 };
        var start = getCheckedValue('q_start');
        var products = getCheckedValue('q_products');
        var features = getCheckedFeatures();
        var timeline = getCheckedValue('q_timeline');

        if (start === 'scratch') score.base += 2;
        if (start === 'migration') score.premium += 2;
        if (start === 'scale_marketing') score.platinum += 3;
        if (start === 'undecided') score.premium += 1;

        if (products === 'up_to_100') score.base += 2;
        if (products === '100_1000') score.premium += 2;
        if (products === '1000_10000') score.platinum += 2;
        if (products === 'over_10000') score.platinum += 3;

        features.forEach(function (val) {
            if (val === 'crm_telegram') { score.premium += 2; }
            if (val === 'seo_articles') { score.premium += 2; score.platinum += 1; }
            if (val === 'ai_admin_bot') { score.platinum += 3; }
            if (val === 'ads_promotion') { score.platinum += 2; }
        });

        if (features.length <= 1) score.base += 1;
        if (features.length >= 2 && features.length <= 3) score.premium += 1;
        if (features.length >= 4) score.platinum += 2;

        if (timeline === 'asap_2w') score.base += 2;
        if (timeline === 'within_month') score.premium += 2;
        if (timeline === '1_3_months') score.platinum += 1;
        if (timeline === 'flexible') score.platinum += 1;

        var pkgHint = getPkgHint();
        if (pkgHint && PKG_MAP[pkgHint]) {
            score[pkgHint] += 1;
        }

        var best = 'premium';
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
        var priceEl = resultRoot.querySelector('[data-quiz-result-price]');
        var termEl = resultRoot.querySelector('[data-quiz-result-term]');
        var featuresEl = resultRoot.querySelector('[data-quiz-result-features]');

        if (pkgEl) pkgEl.textContent = data.label;
        if (priceEl) priceEl.textContent = data.price;
        if (termEl) termEl.textContent = data.term;

        if (featuresEl) {
            featuresEl.innerHTML = '';
            data.features.forEach(function (text) {
                var li = document.createElement('li');
                li.textContent = text;
                featuresEl.appendChild(li);
            });
        }
    }

    function isStepAnswered(step) {
        return !!step.querySelector('input[type="radio"]:checked, input[type="checkbox"]:checked');
    }

    function isQuestionStep(step) {
        return step
            && !step.classList.contains('pl-shop__quiz-step--contact')
            && !step.classList.contains('pl-shop__quiz-step--result');
    }

    function validateContactFields() {
        var emailInput = form.querySelector('#pl-shop-quiz-email');
        var phoneInputLocal = form.querySelector('#pl-shop-quiz-phone');
        var telegramInput = form.querySelector('#pl-shop-quiz-telegram');
        var consentInput = form.querySelector('[name="consent"]');
        var nameInputLocal = form.querySelector('#pl-shop-quiz-name');
        var ruleEl = form.querySelector('[data-lead-contact-rule]');

        if (nameInputLocal && nameInputLocal.value.trim() && nameInputLocal.value.trim().length < 2) {
            nameInputLocal.reportValidity();
            return false;
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
        }
        return true;
    }

    function compileDetails() {
        if (!detailsInput) return;

        var pkgKey = recommendPackage();
        var data = PKG_MAP[pkgKey];
        var pkgHint = getPkgHint();
        var fields = [
            // CRM keys only; human labels are mapped on the server (apps/core/quiz_options.py)
            { name: 'q_start' },
            { name: 'q_products' },
            { name: 'q_features', multi: true },
            { name: 'q_timeline' }
        ];

        var parts = ['page: ' + (form.dataset.sourceLabel || 'internet_shop_v2')];

        if (data) {
            parts.push('package: ' + data.label + ' · ' + data.price + ' · ' + data.term);
        }

        fields.forEach(function (field) {
            if (field.multi) {
                var vals = getCheckedFeatures();
                if (vals.length) parts.push(field.name + ': ' + vals.join(', '));
            } else {
                var val = getCheckedValue(field.name);
                if (val) parts.push(field.name + ': ' + val);
            }
        });

        if (pkgHint && PKG_MAP[pkgHint]) {
            parts.push('pkg_hint: ' + PKG_MAP[pkgHint].label);
        }

        detailsInput.value = parts.join('\n');
    }

    function showStep(idx) {
        steps.forEach(function (s, i) { s.hidden = i !== idx; });

        var currentStep = steps[idx];
        var isContact = currentStep && currentStep.classList.contains('pl-shop__quiz-step--contact');
        var isResult = currentStep && currentStep.classList.contains('pl-shop__quiz-step--result');
        var isQuestion = isQuestionStep(currentStep);
        var stepNum = isResult ? QUESTION_STEPS : (isContact ? QUESTION_STEPS : idx + 1);
        var progress = (isContact || isResult) ? 100 : ((idx + 1) / QUESTION_STEPS) * 100;

        if (progressBar) progressBar.style.width = progress + '%';
        if (stepNumEl) stepNumEl.textContent = String(stepNum);

        var showPrev = idx > 0;
        var showNext = isQuestion;
        var showSkip = isQuestion;

        if (navDiv) navDiv.hidden = !showPrev && !showNext && !showSkip;

        if (prevBtn) prevBtn.hidden = !showPrev;

        if (skipBtn) skipBtn.hidden = !showSkip;

        if (nextBtn) {
            nextBtn.hidden = !showNext;
            if (showNext) {
                nextBtn.disabled = !isStepAnswered(currentStep);
            }
        }

        currentIdx = idx;
    }

    function prepareSubmit() {
        compileDetails();
        clearPkgHint();
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
        var option = input.closest('.pl-shop__quiz-option');
        if (option) option.classList.toggle('pl-shop__quiz-option--selected', input.checked);

        if (nextBtn) {
            var anyChecked = step.querySelector('input[type="checkbox"]:checked');
            nextBtn.disabled = !anyChecked;
        }
    }

    form.addEventListener('change', function (e) {
        var input = e.target;
        if (input.type !== 'radio' && input.type !== 'checkbox') return;

        var step = input.closest('.pl-shop__quiz-step');
        if (!step || !isQuestionStep(step)) return;

        var isMulti = step.dataset.multi === 'true';

        if (isMulti) {
            handleMultiChange(input, step);
            return;
        }

        step.querySelectorAll('.pl-shop__quiz-option').forEach(function (opt) {
            opt.classList.remove('pl-shop__quiz-option--selected');
        });
        var selected = input.closest('.pl-shop__quiz-option');
        if (selected) selected.classList.add('pl-shop__quiz-option--selected');
        if (nextBtn) nextBtn.disabled = false;
    });

    if (revealBtn) revealBtn.addEventListener('click', prepareSubmit);
    /* Enter on a question step = "Next" (never Skip, never the contact submit) */
    form.addEventListener('keydown', function (e) {
        if (e.key !== 'Enter' || e.isComposing) return;
        if (!isQuestionStep(steps[currentIdx])) return;
        var tag = e.target && e.target.tagName;
        if (tag === 'BUTTON' || tag === 'TEXTAREA' || tag === 'A') return;
        e.preventDefault();
        goNext();
    });

    if (skipBtn) skipBtn.addEventListener('click', goSkip);
    if (nextBtn) nextBtn.addEventListener('click', goNext);
    if (prevBtn) prevBtn.addEventListener('click', goPrev);

    showStep(0);
})();
