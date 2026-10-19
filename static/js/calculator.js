/**
 * CALCULATOR.JS - Calculator logic
 * Використовує: base.js form system
 * БЕЗ inline styles - всі стилі в CSS
 */

class ProjectCalculator {
    constructor() {
        this.testForm = document.getElementById('calculator-test');
        this.totalSteps = 5;
        this.answers = {};
        this.userInfo = {};
        this.steps = [];
        this.currentStepIndex = 0;
        this.stepNav = null;
        this.prevBtn = null;
        this.nextBtn = null;
        this.skipBtn = null;
        this.contactStepIndex = -1;

        this.init();
    }

    init() {
        if (!this.testForm) return;

        this.setupSteps();
        this.setupEventListeners();
        this.addProgressIndicator();
        this.loadSavedData();
        this.initStepWizard();
    }

    setupSteps() {
        const questions = Array.from(this.testForm.querySelectorAll('.calc-question'));
        const userData = this.testForm.querySelector('.calc-user-data');
        this.steps = userData ? [...questions, userData] : questions;
        this.contactStepIndex = userData ? this.steps.length - 1 : -1;
    }

    setupEventListeners() {
        const radios = this.testForm.querySelectorAll('input[type="radio"]');
        radios.forEach(radio => {
            radio.addEventListener('change', (e) => this.handleAnswerChange(e));
        });

        const checkboxes = this.testForm.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => this.handleAnswerChange(e));
        });

        const userFields = this.testForm.querySelectorAll('[name="name"], [name="phone"]');
        userFields.forEach(field => {
            field.addEventListener('blur', (e) => {
                this.saveUserInfo(e.target.name, e.target.value);
            });
        });

        const startBtn = document.querySelector('.start-test-btn');
        startBtn?.addEventListener('click', () => this.showTestForm());
    }

    initStepWizard() {
        this.stepNav = document.getElementById('calc-step-nav');
        this.prevBtn = this.stepNav?.querySelector('.calc-step-nav__prev') ?? null;
        this.skipBtn = this.stepNav?.querySelector('.calc-step-nav__skip') ?? null;
        this.nextBtn = this.stepNav?.querySelector('.calc-step-nav__next') ?? null;

        this.prevBtn?.addEventListener('click', () => this.goPrev());
        this.skipBtn?.addEventListener('click', () => this.goSkip());
        this.nextBtn?.addEventListener('click', () => this.goNext());

        if (this.steps.length) {
            this.showStep(0);
        }
    }

    addProgressIndicator() {
        const questionLabel = this.testForm?.dataset.questionLabel || (((document.documentElement.getAttribute('lang') || 'cs').toLowerCase().indexOf('en') === 0) ? 'Question' : 'Otázka');
        const ofLabel = this.testForm?.dataset.ofLabel || (((document.documentElement.getAttribute('lang') || 'cs').toLowerCase().indexOf('en') === 0) ? 'of' : 'z');

        const progressHtml = `
            <div class="calculator-progress mb-md">
                <div class="calculator-progress__bar">
                    <div class="calculator-progress__fill" data-progress="0"></div>
                </div>
                <span class="calculator-progress__text">
                    ${questionLabel} <span class="calculator-progress__current">0</span> ${ofLabel}
                    <span class="calculator-progress__total">${this.totalSteps}</span>
                </span>
            </div>
        `;

        this.testForm.insertAdjacentHTML('afterbegin', progressHtml);
    }

    isContactStep(step) {
        return step === this.steps[this.contactStepIndex];
    }

    isCheckboxStep(step) {
        return step?.querySelector('.calc-options[data-question-type="checkbox"]') !== null;
    }

    isStepAnswered(step) {
        if (!step) return false;
        if (this.isContactStep(step)) {
            const name = step.querySelector('[name="name"]')?.value?.trim();
            const phone = step.querySelector('[name="phone"]')?.value?.trim();
            const consent = step.querySelector('[name="consent"]')?.checked;
            return Boolean(name && phone && consent);
        }

        const options = step.querySelector('.calc-options');
        if (!options) return false;

        if (options.dataset.questionType === 'checkbox') {
            return !!step.querySelector('input[type="checkbox"]:checked');
        }

        return !!step.querySelector('input[type="radio"]:checked');
    }

    showStep(idx) {
        if (!this.steps.length) return;

        const safeIdx = Math.max(0, Math.min(idx, this.steps.length - 1));

        this.steps.forEach((step, i) => {
            step.hidden = i !== safeIdx;
        });

        this.currentStepIndex = safeIdx;
        const currentStep = this.steps[safeIdx];
        const isContact = this.isContactStep(currentStep);

        if (this.stepNav) {
            this.stepNav.hidden = isContact;
        }

        if (this.prevBtn) {
            this.prevBtn.hidden = isContact || safeIdx === 0;
        }

        if (this.skipBtn) {
            this.skipBtn.hidden = isContact;
        }

        if (this.nextBtn) {
            this.nextBtn.hidden = isContact;
            this.nextBtn.disabled = !this.isStepAnswered(currentStep);
        }

        this.updateProgress();
    }

    goNext() {
        if (this.currentStepIndex < this.steps.length - 1) {
            this.showStep(this.currentStepIndex + 1);
        }
    }

    goSkip() {
        if (this.isContactStep(this.steps[this.currentStepIndex])) return;
        if (this.currentStepIndex < this.steps.length - 1) {
            this.showStep(this.currentStepIndex + 1);
        }
    }

    goPrev() {
        if (this.currentStepIndex > 0) {
            this.showStep(this.currentStepIndex - 1);
        }
    }

    handleAnswerChange(event) {
        const questionName = event.target.name;
        const input = event.target;

        if (input.type === 'checkbox') {
            const group = input.closest('.calc-options');
            const checkedValues = Array.from(
                group.querySelectorAll(`input[name="${questionName}"]:checked`)
            ).map(cb => cb.value);
            this.answers[questionName] = checkedValues;
        } else {
            this.answers[questionName] = input.value;
        }

        try {
            sessionStorage.setItem('calculator_answers', JSON.stringify(this.answers));
        } catch (error) {
            console.error('Failed to save answers:', error);
        }

        const currentStep = this.steps[this.currentStepIndex];

        if (input.type === 'radio') {
            setTimeout(() => this.goNext(), 400);
        } else if (this.isCheckboxStep(currentStep) && this.nextBtn) {
            this.nextBtn.disabled = !this.isStepAnswered(currentStep);
        }
    }

    updateProgress() {
        const currentStep = this.steps[this.currentStepIndex];
        const isContact = this.isContactStep(currentStep);
        const stepNum = isContact ? this.totalSteps : this.currentStepIndex + 1;
        const progress = isContact ? 100 : (stepNum / this.totalSteps) * 100;

        const progressFill = this.testForm?.querySelector('.calculator-progress__fill');
        const currentSpan = this.testForm?.querySelector('.calculator-progress__current');

        if (progressFill) progressFill.setAttribute('data-progress', Math.round(progress));
        if (currentSpan) currentSpan.textContent = isContact ? this.totalSteps : stepNum;
    }

    getFirstIncompleteStepIndex() {
        const lastQuestion = this.contactStepIndex >= 0
            ? this.contactStepIndex
            : this.steps.length;

        for (let i = 0; i < lastQuestion; i++) {
            if (!this.isStepAnswered(this.steps[i])) {
                return i;
            }
        }

        return this.contactStepIndex >= 0 ? this.contactStepIndex : lastQuestion - 1;
    }

    loadSavedData() {
        try {
            const savedAnswers = sessionStorage.getItem('calculator_answers');
            if (savedAnswers) {
                this.answers = JSON.parse(savedAnswers);
                this.restoreAnswers();
            }
        } catch (error) {
            console.error('Failed to load answers:', error);
        }

        try {
            const savedUserData = sessionStorage.getItem('prometey_user_data');
            if (savedUserData) {
                const userData = JSON.parse(savedUserData);
                this.prefillUserData(userData);
            }
        } catch (error) {
            console.error('Failed to load user data:', error);
        }
    }

    restoreAnswers() {
        Object.entries(this.answers).forEach(([question, answer]) => {
            if (Array.isArray(answer)) {
                answer.forEach(val => {
                    const checkbox = this.testForm.querySelector(`input[name="${question}"][value="${val}"]`);
                    if (checkbox) checkbox.checked = true;
                });
            } else {
                const radio = this.testForm.querySelector(`input[name="${question}"][value="${answer}"]`);
                if (radio) radio.checked = true;
            }
        });

        const testSection = document.getElementById('test-section');
        if (testSection && !testSection.classList.contains('hidden')) {
            this.showStep(this.getFirstIncompleteStepIndex());
        } else {
            this.updateProgress();
        }
    }

    prefillUserData(userData) {
        if (userData.name) {
            const nameField = document.querySelector('#test-name');
            if (nameField) nameField.value = userData.name;
        }

        if (userData.phone) {
            const phoneField = document.querySelector('#test-phone');
            if (phoneField) {
                const app = window.prometeyApp;
                if (app && app.phoneMasks && app.phoneMasks.has(phoneField)) {
                    const mask = app.phoneMasks.get(phoneField);
                    mask.formatValue(userData.phone);
                } else {
                    phoneField.value = userData.phone;
                    if (app && typeof PhoneMask !== 'undefined') {
                        app.initPhoneMasksForElement(document);
                        if (app.phoneMasks && app.phoneMasks.has(phoneField)) {
                            const mask = app.phoneMasks.get(phoneField);
                            mask.formatValue(userData.phone);
                        }
                    }
                }
            }
        } else {
            const phoneField = document.querySelector('#test-phone');
            if (phoneField) {
                const app = window.prometeyApp;
                if (app && app.phoneMasks && app.phoneMasks.has(phoneField)) {
                    const mask = app.phoneMasks.get(phoneField);
                    mask.ensurePrefix();
                } else if (app && typeof PhoneMask !== 'undefined') {
                    app.initPhoneMasksForElement(document);
                }
            }
        }
    }

    saveUserInfo(field, value) {
        this.userInfo[field] = value;

        try {
            let globalData = {};
            const saved = sessionStorage.getItem('prometey_user_data');
            if (saved) globalData = JSON.parse(saved);

            globalData[field] = value;
            globalData.timestamp = Date.now();
            sessionStorage.setItem('prometey_user_data', JSON.stringify(globalData));
        } catch (error) {
            console.error('Failed to save user info:', error);
        }
    }

    showTestForm() {
        const testSection = document.getElementById('test-section');
        if (!testSection) return;

        testSection.classList.remove('hidden');
        this.showStep(0);

        const isMobile = window.matchMedia('(max-width: 767px)').matches;
        if (isMobile) {
            testSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    clearSavedData() {
        try {
            sessionStorage.removeItem('calculator_answers');
            sessionStorage.removeItem('prometey_user_data');
        } catch (error) {
            console.error('Failed to clear data:', error);
        }
    }

    clearForm() {
        const form = this.testForm;
        if (!form) return;

        const inputs = form.querySelectorAll('input[type="radio"], input[type="checkbox"]');
        inputs.forEach(input => {
            input.checked = false;
            input.classList.remove('error');
        });

        const nameField = form.querySelector('[name="name"]');
        const phoneField = form.querySelector('[name="phone"]');

        if (nameField) {
            nameField.value = '';
            nameField.classList.remove('error');
        }
        if (phoneField) {
            const app = window.prometeyApp;
            if (app && app.phoneMasks && app.phoneMasks.has(phoneField)) {
                const mask = app.phoneMasks.get(phoneField);
                mask.ensurePrefix();
            } else {
                const lang = (document.documentElement.lang || 'cs').split('-')[0].toLowerCase();
                phoneField.value = (lang === 'en') ? '' : '+420';
            }
            phoneField.classList.remove('error');
        }

        this.answers = {};
        this.clearSavedData();

        const progressFill = form.querySelector('.calculator-progress__fill');
        const currentSpan = form.querySelector('.calculator-progress__current');

        if (progressFill) progressFill.setAttribute('data-progress', '0');
        if (currentSpan) currentSpan.textContent = '0';

        const errorMessages = form.querySelectorAll('.calc-field__error');
        errorMessages.forEach(msg => {
            msg.textContent = '';
            msg.classList.remove('show');
        });

        this.showStep(0);
    }
}

let calculatorInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    calculatorInstance = new ProjectCalculator();
    window.calculatorInstance = calculatorInstance;
});

window.CalculatorUtils = {
    showTestForm() {
        calculatorInstance?.showTestForm();
    },
    getInstance() {
        return calculatorInstance;
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProjectCalculator;
}
