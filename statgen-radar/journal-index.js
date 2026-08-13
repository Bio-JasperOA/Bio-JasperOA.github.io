const JOURNAL_INDEX_URL = '/data/statgen-radar-journals.json';
const journalStars = window.StatGenStars;

const journalState = {
  rows: [],
  page: 1,
  pageSize: 10
};

function journalEscape(value) {
  return String(value ?? '').replace(/[&<>'"]/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[char]));
}

function journalDoi(record) {
  if (!record.doi || record.doi === '—' || record.doi === '-') {
    return '<span class="journal-doi-missing">Unavailable</span>';
  }
  return `<a href="https://doi.org/${encodeURI(record.doi)}" target="_blank" rel="noreferrer">${journalEscape(record.doi)} ↗</a>`;
}

function validNumber(value) {
  if (value === null || value === undefined || value === '') return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function journalBaseCompare(a, b) {
  const scoreA = validNumber(a.score);
  const scoreB = validNumber(b.score);
  if (scoreA === null && scoreB !== null) return 1;
  if (scoreA !== null && scoreB === null) return -1;
  if (scoreA !== scoreB) return (scoreB ?? -1) - (scoreA ?? -1);

  const jifA = validNumber(a.impact_factor);
  const jifB = validNumber(b.impact_factor);
  if (jifA === null && jifB !== null) return 1;
  if (jifA !== null && jifB === null) return -1;
  if (jifA !== jifB) return (jifB ?? -1) - (jifA ?? -1);

  return String(a.journal || '').localeCompare(String(b.journal || ''));
}

function sortedJournalRows() {
  const pinnedKeys = journalStars.keys();
  return [...journalState.rows].sort((a, b) => {
    const pinnedA = pinnedKeys.has(journalStars.key(a));
    const pinnedB = pinnedKeys.has(journalStars.key(b));
    if (pinnedA !== pinnedB) return pinnedA ? -1 : 1;
    return journalBaseCompare(a, b);
  });
}

function journalStarButton(record, pinnedKeys) {
  const pinned = pinnedKeys.has(journalStars.key(record));
  const action = pinned ? 'Unpin' : 'Pin';
  return `<button class="journal-star-button" type="button" data-star-key="${journalEscape(journalStars.key(record))}" aria-pressed="${pinned}" aria-label="${action} ${journalEscape(record.article)}" title="${pinned ? 'Remove from pinned articles' : 'Pin this article'}"><span aria-hidden="true">${pinned ? '★' : '☆'}</span></button>`;
}

function journalJif(record) {
  const value = validNumber(record.impact_factor);
  return value === null
    ? '<span class="journal-jif-value journal-jif-missing">NA</span>'
    : `<strong class="journal-jif-value">${journalEscape(value)}</strong>`;
}

function renderJournalIndex() {
  const body = document.querySelector('#journal-index-body');
  const summary = document.querySelector('#journal-page-summary');
  const number = document.querySelector('#journal-page-number');
  const previous = document.querySelector('#journal-prev');
  const next = document.querySelector('#journal-next');
  if (!body || !summary || !number || !previous || !next) return;

  const sortedRows = sortedJournalRows();
  const pinnedKeys = journalStars.keys();
  const pinnedCount = sortedRows.filter(record => pinnedKeys.has(journalStars.key(record))).length;
  const total = sortedRows.length;
  const pages = Math.max(1, Math.ceil(total / journalState.pageSize));
  journalState.page = Math.min(Math.max(1, journalState.page), pages);
  const start = (journalState.page - 1) * journalState.pageSize;
  const end = Math.min(start + journalState.pageSize, total);
  const visible = sortedRows.slice(start, end);

  if (!visible.length) {
    body.innerHTML = '<tr><td colspan="6">No indexed journal articles are available yet.</td></tr>';
  } else {
    body.innerHTML = visible.map(record => {
      const pinned = pinnedKeys.has(journalStars.key(record));
      return `
      <tr${pinned ? ' class="is-pinned"' : ''}>
        <td><a class="journal-brief-link" href="${journalEscape(record.brief_url)}">${journalEscape(record.inclusion_date)}</a></td>
        <td><div class="journal-article-cell"><span class="journal-article-title">${journalEscape(record.article)}</span>${journalStarButton(record, pinnedKeys)}</div></td>
        <td>${journalEscape(record.journal)}</td>
        <td class="journal-doi">${journalDoi(record)}</td>
        <td class="numeric"><span class="journal-score">${validNumber(record.score) ?? 'NA'}</span></td>
        <td class="numeric">${journalJif(record)}</td>
      </tr>`;
    }).join('');
  }

  summary.textContent = total
    ? `${pinnedCount ? `${pinnedCount} pinned · ` : ''}Showing ${start + 1}–${end} of ${total} indexed articles`
    : '0 indexed articles';
  number.textContent = `Page ${journalState.page} of ${pages}`;
  previous.disabled = journalState.page <= 1;
  next.disabled = journalState.page >= pages;
}

async function loadJournalIndex() {
  const body = document.querySelector('#journal-index-body');
  if (!body) return;
  try {
    const response = await fetch(`${JOURNAL_INDEX_URL}?v=${Date.now()}`);
    if (!response.ok) throw new Error(`Journal index request failed: ${response.status}`);
    const rows = await response.json();
    if (!Array.isArray(rows)) throw new Error('Journal index has an invalid format.');
    journalState.rows = rows.sort(journalBaseCompare);
    renderJournalIndex();
  } catch (error) {
    body.innerHTML = `<tr><td colspan="6">${journalEscape(error.message)}</td></tr>`;
    const summary = document.querySelector('#journal-page-summary');
    if (summary) summary.textContent = 'Unable to load journal index';
  }
}

document.querySelector('#journal-index-body')?.addEventListener('click', event => {
  const button = event.target.closest('.journal-star-button');
  if (!button) return;
  const record = journalState.rows.find(item => journalStars.key(item) === button.dataset.starKey);
  if (!record) return;
  journalStars.toggle(record);
  journalState.page = 1;
  renderJournalIndex();
});

window.addEventListener('storage', event => {
  if (event.key !== journalStars.storageKey) return;
  journalState.page = 1;
  renderJournalIndex();
});

const pageSizeControl = document.querySelector('#journal-page-size');
if (pageSizeControl) {
  pageSizeControl.addEventListener('change', event => {
    journalState.pageSize = Number(event.target.value) || 10;
    journalState.page = 1;
    renderJournalIndex();
  });
}

document.querySelector('#journal-prev')?.addEventListener('click', () => {
  journalState.page -= 1;
  renderJournalIndex();
});

document.querySelector('#journal-next')?.addEventListener('click', () => {
  journalState.page += 1;
  renderJournalIndex();
});

loadJournalIndex();
