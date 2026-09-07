(function () {
  'use strict';

  var filterGroup = document.querySelector('.jc-filters');
  var buttons = Array.from(document.querySelectorAll('[data-jc-filter]'));
  var cards = Array.from(document.querySelectorAll('[data-jc-card]'));
  var status = document.getElementById('jc-filter-status');
  var empty = document.getElementById('jc-filter-empty');

  function filterDiscussions(button) {
    var category = button.dataset.jcFilter;
    var visible = 0;
    cards.forEach(function (card) {
      var matches = category === 'all' || card.dataset.category === category;
      card.hidden = !matches;
      if (matches) visible += 1;
    });
    buttons.forEach(function (item) {
      item.setAttribute('aria-pressed', String(item === button));
    });
    if (status) {
      var noun = visible === 1 ? 'discussion' : 'discussions';
      status.textContent = category === 'all'
        ? visible + ' ' + noun
        : visible + ' ' + noun + ' in ' + button.textContent.trim();
    }
    // The generated empty collection already explains an entirely empty site.
    if (empty) empty.hidden = cards.length === 0 || visible !== 0;
  }

  if (filterGroup && buttons.length) {
    filterGroup.hidden = false;
    buttons.forEach(function (button) {
      button.addEventListener('click', function () {
        filterDiscussions(button);
      });
    });
    filterDiscussions(buttons.find(function (button) {
      return button.dataset.jcFilter === 'all';
    }) || buttons[0]);
  }

  // A closed hybrid preview never requests its PDF. Native lazy loading also
  // defers an open preview when it is far below the viewport.
  document.querySelectorAll('details.jc-pdf-preview').forEach(function (details) {
    function loadPreview() {
      if (!details.open) return;
      details.querySelectorAll('[data-jc-pdf-frame][data-src]').forEach(function (frame) {
        var source = frame.dataset.src;
        if (!source) return;
        // The builder checks links; this also prevents off-site iframe requests.
        try {
          var url = new URL(source, window.location.href);
          if (!/^https?:$/.test(url.protocol) || url.origin !== window.location.origin) return;
          frame.src = url.href;
          frame.removeAttribute('data-src');
        } catch (_) {
          // The independent Open PDF link remains available if preview fails.
        }
      });
    }
    details.addEventListener('toggle', loadPreview);
    loadPreview();
  });
})();
