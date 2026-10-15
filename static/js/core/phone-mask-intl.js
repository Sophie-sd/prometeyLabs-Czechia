/**
 * EU phone field (cs/en) — replaces the old free-form IntlPhoneMask, same public API
 * (constructor(input), formatValue, ensurePrefix, validate, getCleanedValue, destroy),
 * so base.js / home-bundle.js / calculator.js / quiz scripts keep working unchanged.
 *
 *  • country-code selector (EU-27 + common), default +420 CZ;
 *  • the field shows "+CC national-grouped" (e.g. "+420 777 123 456"), so every legacy
 *    reader of input.value still gets a full international number;
 *  • paste / browser autofill ("+49151…", "0049…", "420777…") auto-detects the country;
 *  • national trunk "0" is dropped where applicable (DE 0151… → +49 151…);
 *  • per-country digit-count validation + inline error, native setCustomValidity;
 *  • getCleanedValue() → E.164 (+420777123456); server re-validates (form_handlers.py).
 * NOT the Renova +380-only mask.
 */
(function (global) {
    'use strict';
    if (global.IntlPhoneMask && global.IntlPhoneMask.__eu) return; // loaded twice (lazy loaders)

    // iso, dial, min, max (national significant number digits), groups, trunk0 (strip leading 0)
    var C = [
        ['CZ', '420', 9, 9, [3, 3, 3], false], ['SK', '421', 9, 9, [3, 3, 3], true], ['PL', '48', 9, 9, [3, 3, 3], false],
        ['DE', '49', 6, 13, [3, 4, 4, 2], true], ['AT', '43', 7, 13, [3, 3, 4, 3], true], ['HU', '36', 8, 9, [2, 3, 4], false],
        ['BE', '32', 8, 9, [3, 2, 2, 2], true], ['BG', '359', 8, 9, [2, 3, 4], true], ['HR', '385', 8, 9, [2, 3, 4], true],
        ['CY', '357', 8, 8, [2, 3, 3], false], ['DK', '45', 8, 8, [2, 2, 2, 2], false], ['EE', '372', 7, 8, [4, 4], false],
        ['FI', '358', 6, 10, [2, 3, 3, 2], true], ['FR', '33', 9, 9, [1, 2, 2, 2, 2], true], ['GR', '30', 10, 10, [3, 3, 4], false],
        ['IE', '353', 7, 9, [2, 3, 4], true], ['IT', '39', 6, 11, [3, 3, 4, 1], false], ['LV', '371', 8, 8, [2, 3, 3], false],
        ['LT', '370', 8, 8, [3, 2, 3], true], ['LU', '352', 6, 11, [3, 3, 3, 2], false], ['MT', '356', 8, 8, [4, 4], false],
        ['NL', '31', 9, 9, [1, 2, 2, 2, 2], true], ['PT', '351', 9, 9, [3, 3, 3], false], ['RO', '40', 9, 9, [3, 3, 3], true],
        ['SI', '386', 8, 8, [2, 3, 3], true], ['ES', '34', 9, 9, [3, 3, 3], false], ['SE', '46', 7, 10, [2, 3, 2, 3], true],
        ['GB', '44', 10, 10, [4, 6], true], ['CH', '41', 9, 9, [2, 3, 2, 2], true], ['NO', '47', 8, 8, [3, 2, 3], false],
        ['IS', '354', 7, 7, [3, 4], false], ['LI', '423', 7, 7, [3, 2, 2], false], ['UA', '380', 9, 9, [2, 3, 2, 2], true],
        ['MD', '373', 8, 8, [2, 3, 3], true], ['RS', '381', 8, 9, [2, 3, 4], true], ['TR', '90', 10, 10, [3, 3, 2, 2], true],
        ['IL', '972', 8, 9, [2, 3, 4], true], ['AE', '971', 8, 9, [2, 3, 4], true], ['US', '1', 10, 10, [3, 3, 4], false],
        ['CA', '1', 10, 10, [3, 3, 4], false]
    ];
    var BY_ISO = {}, ORDER_TOP = ['CZ', 'SK', 'PL', 'DE', 'AT', 'HU', 'GB', 'UA'];
    C.forEach(function (c) { BY_ISO[c[0]] = { iso: c[0], dial: c[1], min: c[2], max: c[3], groups: c[4], trunk0: c[5] }; });
    var DIALS = C.map(function (c) { return c[1]; }).filter(function (d, i, a) { return a.indexOf(d) === i; })
        .sort(function (a, b) { return b.length - a.length; });

    function lang() { return (document.documentElement.getAttribute('lang') || 'cs').toLowerCase().slice(0, 2); }
    function regionName(iso) {
        try { return new Intl.DisplayNames([lang()], { type: 'region' }).of(iso); } catch (e) { return iso; }
    }
    var T = {
        cs: { cc: 'Předvolba země', bad: 'Zadejte platné číslo ({c}): {n} číslic po předvolbě +{d}.', short: 'Číslo je příliš krátké', long: 'Číslo je příliš dlouhé' },
        en: { cc: 'Country code', bad: 'Enter a valid {c} number: {n} digits after +{d}.', short: 'Number too short', long: 'Number too long' }
    };
    function t(k) { return (T[lang()] || T.en)[k]; }

    function detect(digits) {
        // digits = international digits without "+"/"00"
        for (var i = 0; i < DIALS.length; i++) {
            if (digits.indexOf(DIALS[i]) === 0) {
                var d = DIALS[i];
                if (d === '1') return 'US';
                for (var iso in BY_ISO) { if (BY_ISO[iso].dial === d) return iso; }
            }
        }
        return null;
    }

    function group(nsn, groups) {
        var out = [], pos = 0;
        for (var i = 0; i < groups.length && pos < nsn.length; i++) {
            var g = (i === groups.length - 1) ? nsn.length - pos : groups[i];
            out.push(nsn.substr(pos, g)); pos += g;
        }
        if (pos < nsn.length) out.push(nsn.slice(pos));
        return out.join(' ');
    }

    function defaultIso() { return 'CZ'; }

    function IntlPhoneMask(input) {
        if (input._euPhone) return input._euPhone;
        this.input = input;
        this.country = BY_ISO[input.getAttribute('data-default-country') || defaultIso()] || BY_ISO.CZ;
        this.prefix = '+' + this.country.dial;
        input._euPhone = this;
        this._build();
        this._bind();
        if (input.value && input.value.replace(/\D/g, '').length > this.country.dial.length) this.formatValue(input.value);
        else input.value = '';
    }

    IntlPhoneMask.prototype._build = function () {
        var input = this.input, self = this;
        input.setAttribute('data-eu-phone', '');
        input.setAttribute('autocomplete', 'tel');
        input.setAttribute('inputmode', 'tel');
        if (!input.getAttribute('placeholder') || /^\+?[\d\s]*$/.test(input.getAttribute('placeholder') || '')) {
            input.setAttribute('placeholder', '+420 777 123 456');
        }
        var wrap = document.createElement('div');
        wrap.className = 'eu-phone';
        input.parentNode.insertBefore(wrap, input);
        var cc = document.createElement('label');
        cc.className = 'eu-phone__cc';
        var code = document.createElement('span');
        code.className = 'eu-phone__code';
        code.setAttribute('aria-hidden', 'true');
        var sel = document.createElement('select');
        sel.className = 'eu-phone__select';
        sel.setAttribute('aria-label', t('cc'));
        sel.setAttribute('autocomplete', 'tel-country-code');
        sel.tabIndex = 0;
        var top = ORDER_TOP.map(function (i) { return BY_ISO[i]; });
        var rest = C.map(function (c) { return BY_ISO[c[0]]; }).filter(function (c) { return ORDER_TOP.indexOf(c.iso) < 0; })
            .sort(function (a, b) { return regionName(a.iso).localeCompare(regionName(b.iso), lang()); });
        function add(list, parent) {
            list.forEach(function (c) {
                var o = document.createElement('option');
                o.value = c.iso; o.textContent = regionName(c.iso) + ' +' + c.dial;
                parent.appendChild(o);
            });
        }
        add(top, sel);
        var sep = document.createElement('option'); sep.disabled = true; sep.textContent = '──────────'; sel.appendChild(sep);
        add(rest, sel);
        cc.appendChild(code); cc.appendChild(sel);
        wrap.appendChild(cc);
        wrap.appendChild(input);
        var err = document.createElement('p');
        err.className = 'eu-phone__error';
        err.setAttribute('role', 'alert');
        err.id = (input.id || ('eu-phone-' + Math.random().toString(36).slice(2, 8))) + '-error';
        err.hidden = true;
        wrap.parentNode.insertBefore(err, wrap.nextSibling);
        this.wrap = wrap; this.select = sel; this.codeEl = code; this.errEl = err;
        this._setCountry(this.country.iso, true);
        sel.addEventListener('change', function () {
            var nsn = self._nsn();
            self._setCountry(sel.value);
            self.input.value = self.prefix + (nsn ? ' ' + group(nsn.slice(0, self.country.max), self.country.groups) : ' ');
            self.input.focus();
            self._clearError();
        });
    };

    IntlPhoneMask.prototype._setCountry = function (iso, silent) {
        var c = BY_ISO[iso] || BY_ISO.CZ;
        this.country = c; this.prefix = '+' + c.dial;
        this.select.value = c.iso;
        this.codeEl.textContent = c.iso;
        this.wrap.setAttribute('data-country', c.iso);
    };

    // national significant number currently typed (digits after the dial code)
    IntlPhoneMask.prototype._nsn = function () {
        var v = (this.input.value || '').trim();
        var digits = v.replace(/\D/g, '');
        if (/^(\+|00)/.test(v)) {
            if (v.indexOf('00') === 0) digits = digits.slice(2);
            return digits.indexOf(this.country.dial) === 0 ? digits.slice(this.country.dial.length) : digits;
        }
        return digits;
    };

    IntlPhoneMask.prototype._reformat = function () {
        var input = this.input, raw = input.value || '';
        var trimmed = raw.trim();
        var digits = trimmed.replace(/\D/g, '');
        var nsn;
        if (/^(\+|00)/.test(trimmed)) {
            var intl = trimmed.indexOf('00') === 0 ? digits.slice(2) : digits;
            var iso = detect(intl);
            var keepCurrent = intl.indexOf(this.country.dial) === 0;
            if (!keepCurrent && iso && intl.length > BY_ISO[iso].dial.length) this._setCountry(iso);
            nsn = intl.indexOf(this.country.dial) === 0 ? intl.slice(this.country.dial.length) : (intl.length <= this.country.dial.length ? '' : intl);
        } else {
            // typed without "+": dial-code-looking autofill (420777123456) or national (777123456 / 0151…)
            var iso2 = detect(digits);
            if (iso2 && digits.length > BY_ISO[iso2].max && digits.length - BY_ISO[iso2].dial.length >= BY_ISO[iso2].min) {
                this._setCountry(iso2); nsn = digits.slice(BY_ISO[iso2].dial.length);
            } else nsn = digits;
        }
        if (this.country.trunk0) nsn = nsn.replace(/^0+/, '');
        nsn = nsn.slice(0, this.country.max);
        input.value = this.prefix + ' ' + group(nsn, this.country.groups);
        if (!nsn) input.value = this.prefix + ' ';
    };

    IntlPhoneMask.prototype._bind = function () {
        var self = this, input = this.input;
        input.addEventListener('focus', function () { if (!input.value.trim()) input.value = self.prefix + ' '; });
        input.addEventListener('input', function (e) {
            var atEnd = input.selectionStart === input.value.length;
            self._reformat();
            if (atEnd) { try { input.setSelectionRange(input.value.length, input.value.length); } catch (er) {} }
            if (self.wrap.classList.contains('is-invalid')) self._check(false);
        });
        input.addEventListener('keydown', function (e) {
            // never let Backspace eat into the dial code
            if (e.key === 'Backspace' && input.selectionStart === input.selectionEnd && input.selectionStart <= self.prefix.length + 1) {
                e.preventDefault();
            }
        });
        input.addEventListener('blur', function () {
            if (!self._nsn()) { input.value = ''; self._clearError(); self.input.setCustomValidity(''); return; }
            self._check(true);
        });
    };

    IntlPhoneMask.prototype._check = function (show) {
        var r = this.validate();
        this.input.setCustomValidity(r.valid ? '' : r.message);
        if (r.valid) this._clearError(); else if (show !== false) this._showError(r.message);
        return r;
    };

    IntlPhoneMask.prototype._showError = function (msg) {
        this.errEl.textContent = msg; this.errEl.hidden = false;
        this.wrap.classList.add('is-invalid');
        this.input.setAttribute('aria-invalid', 'true');
        this.input.setAttribute('aria-describedby', this.errEl.id);
    };
    IntlPhoneMask.prototype._clearError = function () {
        this.errEl.hidden = true; this.errEl.textContent = '';
        this.wrap.classList.remove('is-invalid');
        this.input.removeAttribute('aria-invalid');
    };

    // ---- public API (legacy-compatible) ----
    IntlPhoneMask.prototype.formatValue = function (raw) {
        if (!raw) { this.input.value = ''; return; }
        var s = String(raw).trim();
        if (!/^(\+|00)/.test(s)) {
            var d = s.replace(/\D/g, '');
            if (detect(d) && d.length > 9) s = '+' + d;
        }
        this.input.value = s;
        this._reformat();
    };
    IntlPhoneMask.prototype.ensurePrefix = function () { if (!this.input.value || !this.input.value.trim()) this.input.value = ''; };
    IntlPhoneMask.prototype.validate = function () {
        var nsn = this._nsn(), c = this.country;
        if (!nsn) return { valid: true, message: '' };
        if (nsn.length < c.min || nsn.length > c.max) {
            var n = c.min === c.max ? String(c.min) : (c.min + '–' + c.max);
            return { valid: false, message: t('bad').replace('{c}', regionName(c.iso)).replace('{n}', n).replace('{d}', c.dial) };
        }
        return { valid: true, message: '' };
    };
    IntlPhoneMask.prototype.getE164 = function () { var n = this._nsn(); return n ? '+' + this.country.dial + n : ''; };
    IntlPhoneMask.prototype.getCleanedValue = function () { return this.getE164(); };
    IntlPhoneMask.prototype.destroy = function () {};

    IntlPhoneMask.countries = BY_ISO;
    IntlPhoneMask.__eu = true;
    global.IntlPhoneMask = IntlPhoneMask;

    // ---- auto-enhance every public phone field (also those no legacy script touches) ----
    function enhanceAll(root) {
        (root || document).querySelectorAll('input[type="tel"]:not([data-eu-phone]):not([data-no-eu-phone])').forEach(function (i) {
            if (i.closest('[data-no-eu-phone]')) return;
            new IntlPhoneMask(i);
        });
    }
    global.EUPhone = { enhance: enhanceAll };

    // Block submit (capture phase, before page handlers) when a filled phone is invalid
    document.addEventListener('submit', function (e) {
        var form = e.target, bad = null;
        if (!form || !form.querySelectorAll) return;
        form.querySelectorAll('input[data-eu-phone]').forEach(function (i) {
            if (i._euPhone && !i._euPhone._check(true).valid && !bad) bad = i;
        });
        if (bad) { e.preventDefault(); e.stopImmediatePropagation(); bad.focus(); }
    }, true);
    // Some forms submit via button click handlers (no submit event) — validate there too
    document.addEventListener('click', function (e) {
        var btn = e.target.closest && e.target.closest('button[type="submit"], input[type="submit"]');
        if (!btn || !btn.form) return;
        var bad = null;
        btn.form.querySelectorAll('input[data-eu-phone]').forEach(function (i) {
            if (i._euPhone && !i._euPhone._check(true).valid && !bad) bad = i;
        });
        if (bad) { e.preventDefault(); e.stopImmediatePropagation(); bad.focus(); }
    }, true);

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { enhanceAll(); });
    else enhanceAll();
    if ('MutationObserver' in global) {
        new MutationObserver(function (m) {
            for (var k = 0; k < m.length; k++) if (m[k].addedNodes.length) { enhanceAll(); break; }
        }).observe(document.documentElement, { childList: true, subtree: true });
    }
})(typeof window !== 'undefined' ? window : this);
