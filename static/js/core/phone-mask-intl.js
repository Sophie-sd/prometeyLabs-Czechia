/**
 * Intl phone helper: used only for cs/en interface language.
 * cs and en → prefilled +420 (Czech site default), fully editable to any
 * free international format; other languages fall back to +38 defensively
 * (should not normally be reached — uk/ru use the strict PhoneMask instead).
 * Never hard-locks to a single country format.
 */
(function (global) {
    'use strict';

    function defaultPrefix() {
        var lang = (document.documentElement.getAttribute('lang') || 'uk').toLowerCase();
        if (lang.indexOf('cs') === 0) return '+420';
        if (lang.indexOf('en') === 0) return '+420'; // Czech site: +420 default for en too (fully editable)
        return '+38';
    }

    function IntlPhoneMask(input) {
        this.input = input;
        this.prefix = defaultPrefix();
        this.init();
    }

    IntlPhoneMask.prototype.init = function () {
        var self = this;
        if (!this.input.value || !this.input.value.trim()) {
            this.input.value = this.prefix;
        }
        this.input.addEventListener('focus', function () {
            if (!self.input.value.trim()) {
                self.input.value = self.prefix;
            }
        });
        this.input.addEventListener('input', function () {
            var v = self.input.value.replace(/[^\d+]/g, '');
            if (v && v.charAt(0) !== '+') {
                v = '+' + v.replace(/\+/g, '');
            }
            // Keep leading +, strip extra +
            var plus = v.indexOf('+') === 0 ? '+' : '';
            var digits = v.replace(/\D/g, '');
            if (digits.length > 15) {
                digits = digits.slice(0, 15);
            }
            self.input.value = plus + digits;
        });
        this.input.addEventListener('blur', function () {
            var digits = (self.input.value || '').replace(/\D/g, '');
            if (!digits) {
                self.input.value = '';
            }
        });
    };

    IntlPhoneMask.prototype.ensurePrefix = function () {
        if (!this.input.value || !this.input.value.trim()) {
            this.input.value = this.prefix;
        }
    };

    IntlPhoneMask.prototype.formatValue = function (raw) {
        if (!raw) {
            this.input.value = this.prefix;
            return;
        }
        var digits = String(raw).replace(/\D/g, '');
        this.input.value = digits ? '+' + digits : this.prefix;
    };

    IntlPhoneMask.prototype.validate = function () {
        var digits = (this.input.value || '').replace(/\D/g, '');
        if (!digits) {
            return { valid: true, message: '' };
        }
        if (digits.length < 7) {
            return {
                valid: false,
                message: (window.I18N && window.I18N.phoneInvalid) || 'Введіть коректний номер телефону',
            };
        }
        return { valid: true, message: '' };
    };

    IntlPhoneMask.prototype.getCleanedValue = function () {
        return (this.input.value || '').replace(/[^\d+]/g, '');
    };

    IntlPhoneMask.prototype.destroy = function () {};

    global.IntlPhoneMask = IntlPhoneMask;
})(typeof window !== 'undefined' ? window : this);
