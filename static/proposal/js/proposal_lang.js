(function () {
  'use strict';
  // Language switcher: submit on change (CSP-safe, replaces inline onchange).
  document.querySelectorAll('select[data-prop-lang]').forEach(function (sel) {
    sel.addEventListener('change', function () {
      if (sel.form) sel.form.submit();
    });
  });
})();
