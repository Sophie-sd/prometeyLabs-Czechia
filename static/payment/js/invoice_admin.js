(function () {
  function placePdfButton() {
    var btn = document.getElementById('invoice-save-pdf-btn');
    if (!btn) return;
    var row = document.querySelector('.submit-row');
    if (!row) return;
    btn.hidden = false;
    row.insertBefore(btn, row.firstChild);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', placePdfButton);
  } else {
    placePdfButton();
  }
})();

/* Due date (valid_until) = invoice date + 3 days by default, still editable:
   auto-fills only while the admin has not typed their own due date. */
(function () {
  var DUE_DAYS = 3;

  function parseDate(value) {
    var v = (value || '').trim();
    var m = v.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (m) return new Date(+m[1], +m[2] - 1, +m[3]);
    m = v.match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})$/);
    if (m) return new Date(+m[3], +m[2] - 1, +m[1]);
    return null;
  }

  function pad(n) { return String(n).padStart(2, '0'); }

  function formatLike(sample, d) {
    if (/^\d{1,2}\.\d{1,2}\.\d{4}$/.test((sample || '').trim())) {
      return pad(d.getDate()) + '.' + pad(d.getMonth() + 1) + '.' + d.getFullYear();
    }
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
  }

  function initDueDate() {
    var dateInput = document.getElementById('id_invoice_date');
    var dueInput = document.getElementById('id_valid_until');
    if (!dateInput || !dueInput) return;
    var touched = false;
    dueInput.addEventListener('input', function () { touched = true; });

    function sync() {
      if (touched) return;
      var d = parseDate(dateInput.value);
      if (!d) return;
      d.setDate(d.getDate() + DUE_DAYS);
      dueInput.value = formatLike(dateInput.value, d);
    }
    dateInput.addEventListener('change', sync);
    dateInput.addEventListener('input', sync);
    if (!dueInput.value) sync();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDueDate);
  } else {
    initDueDate();
  }
})();
