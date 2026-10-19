/* tz-generator-3.js — marquee strip, quiz engine + submit + upsell, FAQ, sticky CTA */
(function () {
    'use strict';

    var root = document.getElementById('tzRoot');
    if (!root) return;

    // UI language: cs (default) / en
    var IS_EN = (document.documentElement.getAttribute('lang') || 'cs').toLowerCase().indexOf('en') === 0;
    var MSG = IS_EN ? {
        name: 'Enter a valid name',
        consent: 'Please confirm consent to personal data processing.',
        phone: 'Enter a valid phone number',
        email: 'Enter a valid email',
        sending: 'Sending failed. Please try again.',
        network: 'Network error. Please try again.'
    } : {
        name: 'Zadejte platné jméno',
        consent: 'Potvrďte prosím souhlas se zpracováním osobních údajů.',
        phone: 'Zadejte platné telefonní číslo',
        email: 'Zadejte platný e-mail',
        sending: 'Odeslání se nezdařilo. Zkuste to znovu.',
        network: 'Chyba sítě. Zkuste to znovu.'
    };

    var reduceMotion = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* ===== PAGE STRIP (seamless_loop) ===== */
    function initMarquee() {
        var loop = root.querySelector('[data-loop]');
        if (!loop || reduceMotion) return;

        var target = loop.closest('.pl-tz__section') || loop;

        function setMotion(on) {
            loop.classList.toggle('is-motion', !!on);
        }

        function inView() {
            var rect = target.getBoundingClientRect();
            var vh = window.innerHeight || document.documentElement.clientHeight;
            return rect.bottom > 0 && rect.top < vh;
        }

        if ('IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    setMotion(entry.isIntersecting);
                });
            }, { rootMargin: '80px 0px', threshold: 0 });
            io.observe(target);
        }

        setMotion(inView());
        window.addEventListener('scroll', function () {
            setMotion(inView());
        }, { passive: true });
    }

    /* ===== QUIZ ENGINE ===== */
    function initQuiz() {
        var form = root.querySelector('[data-quiz-form]');
        if (!form) return;

        var steps = Array.prototype.slice.call(form.querySelectorAll('.pl-tz__quiz-step'));
        var progressBar = form.querySelector('[data-quiz-progress]');
        var stepNumEl = form.querySelector('[data-quiz-step-num]');
        var prevBtn = form.querySelector('.pl-tz__quiz-prev');
        var skipBtn = form.querySelector('.pl-tz__quiz-skip');
        var nextBtn = form.querySelector('.pl-tz__quiz-next');
        var submitBtn = form.querySelector('[data-quiz-submit]');
        var submitNote = form.querySelector('[data-quiz-submit-note]');
        var errorEl = form.querySelector('[data-quiz-submit-error]');

        var QUESTION_STEPS = steps.filter(function (s) {
            return !s.classList.contains('pl-tz__quiz-step--contact') &&
                !s.classList.contains('pl-tz__quiz-step--success');
        }).length;

        var currentIdx = 0;
        var successToken = null;

        function isContact(step) {
            return step && step.classList.contains('pl-tz__quiz-step--contact');
        }
        function isSuccess(step) {
            return step && step.classList.contains('pl-tz__quiz-step--success');
        }
        function isQuestionStep(step) {
            return step && !isContact(step) && !isSuccess(step);
        }

        function isStepAnswered(step) {
            if (!step) return false;
            if (step.dataset.text === 'true') {
                var ta = step.querySelector('textarea[name="description"]');
                return !!(ta && ta.value.trim().length > 0);
            }
            return !!step.querySelector('input[type="radio"]:checked, input[type="checkbox"]:checked');
        }

        function syncOptionSelected(step) {
            if (!step) return;
            step.querySelectorAll('.pl-tz__quiz-option').forEach(function (opt) {
                var input = opt.querySelector('input');
                opt.classList.toggle('pl-tz__quiz-option--selected', !!(input && input.checked));
            });
        }

        function syncNextEnabled(step) {
            if (!nextBtn || !step || !isQuestionStep(step)) return;
            nextBtn.disabled = !isStepAnswered(step);
        }

        function isContactValid() {
            var nameInput = form.querySelector('#pl-tz-quiz-name');
            var phoneInput = form.querySelector('#pl-tz-quiz-phone');
            var emailInput = form.querySelector('#pl-tz-quiz-email');
            var consentInput = form.querySelector('#pl-tz-quiz-consent');
            return validName(nameInput && nameInput.value) &&
                validPhone(phoneInput && phoneInput.value) &&
                validEmail(emailInput && emailInput.value) &&
                (!consentInput || consentInput.checked);
        }

        function syncSubmitEnabled() {
            if (!submitBtn) return;
            submitBtn.disabled = !isContactValid();
        }

        function showStep(idx) {
            steps.forEach(function (s, i) { s.hidden = i !== idx; });
            var step = steps[idx];
            var contact = isContact(step);
            var success = isSuccess(step);
            var question = isQuestionStep(step);

            var questionIdx = 0;
            for (var i = 0; i <= idx; i++) {
                if (isQuestionStep(steps[i])) questionIdx = i + 1;
            }
            var stepNum = success ? QUESTION_STEPS : (contact ? QUESTION_STEPS : questionIdx);
            var progress = (contact || success) ? 100 : (questionIdx / QUESTION_STEPS) * 100;

            if (progressBar) progressBar.style.width = progress + '%';
            if (stepNumEl) stepNumEl.textContent = String(stepNum);

            if (prevBtn) prevBtn.hidden = idx === 0 || success;
            if (skipBtn) skipBtn.hidden = !question;
            if (nextBtn) {
                nextBtn.hidden = !question;
                if (question) {
                    syncOptionSelected(step);
                    syncNextEnabled(step);
                }
            }
            if (submitBtn) {
                submitBtn.hidden = !contact;
                if (contact) {
                    syncSubmitEnabled();
                } else {
                    submitBtn.disabled = true;
                }
            }
            if (submitNote) submitNote.hidden = !contact;

            currentIdx = idx;
        }

        function goNext() {
            var step = steps[currentIdx];
            if (!isQuestionStep(step)) return;
            if (!isStepAnswered(step)) return;
            if (currentIdx < steps.length - 1) showStep(currentIdx + 1);
        }

        function goSkip() {
            var step = steps[currentIdx];
            if (!isQuestionStep(step)) return;
            if (currentIdx < steps.length - 1) showStep(currentIdx + 1);
        }

        function goPrev() {
            if (currentIdx > 0) showStep(currentIdx - 1);
        }

        function applyOptionSelection(input) {
            var step = input.closest('.pl-tz__quiz-step');
            if (!step || !isQuestionStep(step)) return;

            if (step.dataset.multi === 'true') {
                syncOptionSelected(step);
                syncNextEnabled(step);
                return;
            }

            syncOptionSelected(step);
            syncNextEnabled(step);
        }

        form.addEventListener('change', function (e) {
            var input = e.target;
            if (input.name === 'consent') {
                setError('');
                syncSubmitEnabled();
                return;
            }
            if (input.type !== 'radio' && input.type !== 'checkbox') return;
            applyOptionSelection(input);
        });

        form.addEventListener('click', function (e) {
            var option = e.target.closest('.pl-tz__quiz-option');
            if (!option) return;
            var input = option.querySelector('input');
            if (!input) return;
            var step = option.closest('.pl-tz__quiz-step');
            if (!step || !isQuestionStep(step)) return;

            /* iOS: label click may not fire change reliably with absolute opacity:0 input */
            requestAnimationFrame(function () {
                applyOptionSelection(input);
            });
        });

        form.addEventListener('input', function (e) {
            var step = e.target.closest('.pl-tz__quiz-step');
            if (!step) return;
            if (step.dataset.text === 'true') {
                syncNextEnabled(step);
            }
            if (isContact(step)) {
                setError('');
                syncSubmitEnabled();
            }
        });

        if (nextBtn) nextBtn.addEventListener('click', goNext);
        if (skipBtn) skipBtn.addEventListener('click', goSkip);
        if (prevBtn) prevBtn.addEventListener('click', goPrev);

        function getRadioValue(name) {
            var el = form.querySelector('input[name="' + name + '"]:checked');
            return el ? el.value : '';
        }
        function getCheckboxValues(name) {
            return Array.prototype.map.call(
                form.querySelectorAll('input[name="' + name + '"]:checked'),
                function (el) { return el.value; }
            );
        }

        function validName(v) {
            v = (v || '').trim();
            if (v.length < 2) return false;
            if (/^\d+$/.test(v)) return false;
            // Any letters incl. Czech diacritics (e.g. "Jiří Novák"), spaces, apostrophes, hyphens
            return /^[\p{L} '\u2019\-]{2,}$/u.test(v);
        }
        function validPhone(v) {
            return (v || '').replace(/\D/g, '').length >= 7;
        }
        function validEmail(v) {
            return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test((v || '').trim());
        }

        function getCSRFToken() {
            var input = form.querySelector('[name=csrfmiddlewaretoken]');
            if (input) return input.value;
            var match = document.cookie.match(/csrftoken=([^;]+)/);
            return match ? match[1] : '';
        }

        function setError(msg) {
            if (errorEl) errorEl.textContent = msg || '';
        }

        function showSuccess(data) {
            successToken = data.token || null;
            var successStep = form.querySelector('[data-step="success"]');
            var idx = steps.indexOf(successStep);
            if (idx >= 0) showStep(idx);

            var msgEl = form.querySelector('[data-quiz-success-message]');
            if (msgEl && data.message) msgEl.textContent = data.message;

            var pdfLink = form.querySelector('[data-quiz-pdf-link]');
            if (pdfLink && data.pdf_url) pdfLink.setAttribute('href', data.pdf_url);

            if (window.__tzInitReveal) window.__tzInitReveal();
        }

        function handleSubmit(e) {
            e.preventDefault();

            var step = steps[currentIdx];
            if (isQuestionStep(step)) {
                goNext();
                return;
            }
            if (!isContact(step)) return;

            var nameInput = form.querySelector('#pl-tz-quiz-name');
            var phoneInput = form.querySelector('#pl-tz-quiz-phone');
            var emailInput = form.querySelector('#pl-tz-quiz-email');

            setError('');

            if (!validName(nameInput.value)) {
                setError(MSG.name);
                nameInput.focus();
                return;
            }
            if (!validPhone(phoneInput.value)) {
                setError(MSG.phone);
                phoneInput.focus();
                return;
            }
            if (!validEmail(emailInput.value)) {
                setError(MSG.email);
                emailInput.focus();
                return;
            }
            var consentInput = form.querySelector('#pl-tz-quiz-consent');
            if (consentInput && !consentInput.checked) {
                setError(MSG.consent);
                consentInput.focus();
                return;
            }

            var quiz = {
                site_type: getRadioValue('site_type'),
                goals: getCheckboxValues('goals'),
                sections: getCheckboxValues('sections'),
                features: getCheckboxValues('features'),
                style: getRadioValue('style'),
                timeline: getRadioValue('timeline'),
                budget: getRadioValue('budget'),
                description: (form.querySelector('#pl-tz-quiz-description') || {}).value || '',
                extra: (form.querySelector('#pl-tz-quiz-extra') || {}).value || ''
            };

            var fd = new FormData();
            fd.append('name', nameInput.value.trim());
            fd.append('phone', phoneInput.value.trim());
            fd.append('email', emailInput.value.trim());
            fd.append('quiz', JSON.stringify(quiz));
            // GDPR consent + gclid/UTM/landing (same as other lead forms via gclid-capture.js)
            if (consentInput && consentInput.checked) fd.append('consent', '1');
            if (window.GCLIDCapture && typeof window.GCLIDCapture.appendToFormData === 'function') {
                window.GCLIDCapture.appendToFormData(fd);
            }

            var submitUrl = root.dataset.tzSubmit;
            if (!submitUrl) return;

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.classList.add('is-loading');
            }

            fetch(submitUrl, {
                method: 'POST',
                body: fd,
                headers: { 'X-CSRFToken': getCSRFToken() }
            })
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    if (data.success) {
                        showSuccess(data);
                    } else {
                        setError(data.message || MSG.sending);
                    }
                })
                .catch(function () {
                    setError(MSG.network);
                })
                .finally(function () {
                    if (submitBtn) {
                        submitBtn.classList.remove('is-loading');
                        var step = steps[currentIdx];
                        if (isContact(step)) {
                            syncSubmitEnabled();
                        } else {
                            submitBtn.disabled = true;
                            submitBtn.hidden = true;
                        }
                    }
                });
        }

        form.addEventListener('submit', handleSubmit);

        function initUpsell() {
            var upsellBlock = form.querySelector('[data-quiz-upsell]');
            var noteEl = form.querySelector('[data-quiz-upsell-done]');
            if (!upsellBlock) return;

            upsellBlock.querySelectorAll('[data-upsell-choice]').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    var choice = btn.getAttribute('data-upsell-choice');
                    var tpl = root.dataset.tzUpsellTpl;
                    if (!tpl || !successToken) return;
                    var url = tpl.replace('TOKEN', successToken);

                    var fd = new FormData();
                    fd.append('choice', choice);

                    upsellBlock.querySelectorAll('button').forEach(function (b) { b.disabled = true; });

                    fetch(url, {
                        method: 'POST',
                        body: fd,
                        headers: { 'X-CSRFToken': getCSRFToken() }
                    })
                        .then(function (r) { return r.json(); })
                        .then(function (data) {
                            upsellBlock.hidden = true;
                            if (noteEl) {
                                noteEl.hidden = false;
                                noteEl.textContent = data.message || '';
                            }
                        })
                        .catch(function () {
                            upsellBlock.querySelectorAll('button').forEach(function (b) { b.disabled = false; });
                        });
                });
            });
        }

        initUpsell();
        showStep(0);
    }

    /* ===== FAQ ACCORDION ===== */
    function initFaq() {
        var list = root.querySelector('[data-faq]');
        if (!list) return;

        var items = Array.prototype.slice.call(list.querySelectorAll('.pl-tz__faq-item'));

        function closeItem(item) {
            var answer = item.querySelector('.pl-tz__faq-a');
            var btn = item.querySelector('[data-faq-toggle]');
            item.classList.remove('is-open');
            if (btn) btn.setAttribute('aria-expanded', 'false');
            if (answer) answer.style.maxHeight = '0px';
        }

        function openItem(item) {
            var answer = item.querySelector('.pl-tz__faq-a');
            var btn = item.querySelector('[data-faq-toggle]');
            item.classList.add('is-open');
            if (btn) btn.setAttribute('aria-expanded', 'true');
            if (answer) answer.style.maxHeight = answer.scrollHeight + 'px';
        }

        items.forEach(function (item) {
            var btn = item.querySelector('[data-faq-toggle]');
            if (!btn) return;
            btn.addEventListener('click', function () {
                var isOpen = item.classList.contains('is-open');
                items.forEach(closeItem);
                if (!isOpen) openItem(item);
            });
        });
    }

    /* ===== STICKY MOBILE CTA ===== */
    function initSticky() {
        var sticky = document.getElementById('tzSticky');
        var hero = root.querySelector('.pl-tz__hero');
        var quiz = root.querySelector('#tz-quiz');
        if (!sticky || !hero) return;

        var pastHero = false;
        var inQuiz = false;

        function sync() {
            sticky.classList.toggle('is-visible', pastHero && !inQuiz);
        }

        if ('IntersectionObserver' in window) {
            new IntersectionObserver(function (ents) {
                ents.forEach(function (en) {
                    pastHero = !en.isIntersecting;
                    sync();
                });
            }, { threshold: 0 }).observe(hero);

            if (quiz) {
                new IntersectionObserver(function (ents) {
                    ents.forEach(function (en) {
                        inQuiz = en.isIntersecting;
                        sync();
                    });
                }, { threshold: 0.15 }).observe(quiz);
            }
        }
    }

    function init() {
        initMarquee();
        initQuiz();
        initFaq();
        initSticky();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
