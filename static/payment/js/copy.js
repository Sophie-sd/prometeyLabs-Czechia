/* Universal copy-to-clipboard helper used on the public payment page and in
   the Django admin. Avoids any inline JS in templates by binding delegated
   click handlers to elements that carry [data-copy] or [data-copy-all]. */
(function () {
    'use strict';

    var COPIED_CLASS = 'copied';
    var COPIED_TIMEOUT_MS = 1800;

    function copyText(text, onDone) {
        if (text == null) {
            text = '';
        }
        text = String(text);

        if (window.navigator && window.navigator.clipboard && window.isSecureContext) {
            window.navigator.clipboard.writeText(text)
                .then(function () { if (onDone) onDone(true); })
                .catch(function () { fallbackCopy(text, onDone); });
            return;
        }
        fallbackCopy(text, onDone);
    }

    function fallbackCopy(text, onDone) {
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.className = 'pl-clipboard-fallback';
        document.body.appendChild(ta);

        var selection = document.getSelection();
        var savedRange = selection && selection.rangeCount > 0 ? selection.getRangeAt(0) : null;

        ta.focus();
        ta.select();
        ta.setSelectionRange(0, text.length);

        var ok = false;
        try { ok = document.execCommand('copy'); } catch (e) { ok = false; }

        document.body.removeChild(ta);
        if (savedRange && selection) {
            selection.removeAllRanges();
            selection.addRange(savedRange);
        }
        if (onDone) onDone(ok);
    }

    function flashCopied(btn, doneText) {
        if (!btn) return;
        btn.classList.add(COPIED_CLASS);
        btn.setAttribute('aria-pressed', 'true');

        var labelEl = btn.querySelector('[data-copy-label]');
        var savedLabel = null;
        if (labelEl && doneText) {
            savedLabel = labelEl.textContent;
            labelEl.textContent = doneText;
        } else if (!labelEl && doneText && !btn.querySelector('svg')) {
            savedLabel = btn.textContent;
            btn.textContent = doneText;
        }

        // Icon-only buttons have no visible label: announce the result through
        // the page's polite live region (labels with aria-live announce themselves).
        var statusEl = document.querySelector('[data-copy-status]');
        if (statusEl && doneText && !labelEl) {
            statusEl.textContent = '';
            window.setTimeout(function () { statusEl.textContent = doneText; }, 50);
        }

        var iconDefault = btn.querySelector('[data-copy-icon="default"]');
        var iconDone = btn.querySelector('[data-copy-icon="done"]');
        if (iconDefault) iconDefault.hidden = true;
        if (iconDone) iconDone.hidden = false;

        window.setTimeout(function () {
            btn.classList.remove(COPIED_CLASS);
            btn.setAttribute('aria-pressed', 'false');
            if (labelEl && savedLabel !== null) {
                labelEl.textContent = savedLabel;
            } else if (!labelEl && savedLabel !== null) {
                btn.textContent = savedLabel;
            }
            if (iconDefault) iconDefault.hidden = false;
            if (iconDone) iconDone.hidden = true;
            if (statusEl && !labelEl) statusEl.textContent = '';
        }, COPIED_TIMEOUT_MS);
    }

    function readPayload(selector) {
        if (!selector) return null;
        var node = document.querySelector(selector);
        if (!node) return null;
        try {
            return JSON.parse(node.textContent || 'null');
        } catch (e) {
            return null;
        }
    }

    function buildText(payload, separator) {
        if (payload == null) return '';
        if (Array.isArray(payload)) {
            return payload.join(separator || '\n');
        }
        if (typeof payload === 'object') {
            var lines = [];
            Object.keys(payload).forEach(function (k) {
                lines.push(k + ': ' + payload[k]);
            });
            return lines.join(separator || '\n');
        }
        return String(payload);
    }

    function handleCopyClick(btn) {
        var value = btn.getAttribute('data-copy-value');
        if (value == null) {
            var sourceSel = btn.getAttribute('data-copy-source');
            if (sourceSel) {
                var src = document.querySelector(sourceSel);
                if (src) {
                    value = (src.value !== undefined ? src.value : src.textContent) || '';
                }
            }
        }
        if (value == null) return;
        var doneText = btn.getAttribute('data-copy-done') || '';
        copyText(value, function () { flashCopied(btn, doneText); });
    }

    function handleCopyAllClick(btn) {
        var sourceSel = btn.getAttribute('data-copy-source');
        var separator = btn.getAttribute('data-copy-separator') || '\n';
        var payload = readPayload(sourceSel);
        var text = buildText(payload, separator);
        var doneText = btn.getAttribute('data-copy-done') || '';
        copyText(text, function () { flashCopied(btn, doneText); });
    }

    document.addEventListener('click', function (event) {
        var copyAllBtn = event.target.closest('[data-copy-all]');
        if (copyAllBtn) {
            event.preventDefault();
            handleCopyAllClick(copyAllBtn);
            return;
        }
        var copyBtn = event.target.closest('[data-copy]');
        if (copyBtn) {
            event.preventDefault();
            handleCopyClick(copyBtn);
        }
    });

    window.PaymentCopy = { copyText: copyText, flashCopied: flashCopied };
})();
