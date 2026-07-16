const JOURNAL_INDEX_URL = '/data/statgen-radar-journals.json';

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
  if (!record.doi) return '<span class="journal-doi-missing">Unavailable</span>';
  return `<a href="https://doi.org/${encodeURI(record.doi)}" target="_blank" rel="noreferrer">${journalEscape(record.doi)} ↗</a>`;
}

function renderJournalIndex() {
  const body = document.querySelector('#journal-index-body');
  const summary = document.querySelector('#journal-page-summary');
  const number = document.querySelector('#journal-page-number');
  const previous = document.querySelector('#journal-prev');
  const next = document.querySelector('#journal-next');
  if (!body || !summary || !number || !previous || !next) return;

  const total = journalState.rows.length;
  const pages = Math.max(1, Math.ceil(total / journalState.pageSize));
  journalState.page = Math.min(Math.max(1, journalState.page), pages);
  const start = (journalState.page - 1) * journalState.pageSize;
  const end = Math.min(start + journalState.pageSize, total);
  const visible = journalState.rows.slice(start, end);

  if (!visible.length) {
    body.innerHTML = '<tr><td colspan="6">No indexed journal articles are available yet.</td></tr>';
  } else {
    body.innerHTML = visible.map(record => `
      <tr>
        <td><a class="journal-brief-link" href="${journalEscape(record.brief_url)}">${journalEscape(record.inclusion_date)}</a></td>
        <td><span class="journal-article-title">${journalEscape(record.article)}</span></td>
        <td>${journalEscape(record.journal)}</td>
        <td class="journal-doi">${journalDoi(record)}</td>
        <td class="numeric"><span class="journal-score">${record.score ?? '—'}</span></td>
        <td class="numeric"><strong>${record.impact_factor ?? '—'}</strong></td>
      </tr>`).join('');
  }

  summary.textContent = total ? `Showing ${start + 1}–${end} of ${total} indexed articles` : '0 indexed articles';
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
    journalState.rows = rows.sort((a, b) => {
      const jifDifference = (Number(b.impact_factor) || -1) - (Number(a.impact_factor) || -1);
      if (jifDifference) return jifDifference;
      const scoreDifference = (Number(b.score) || -1) - (Number(a.score) || -1);
      if (scoreDifference) return scoreDifference;
      return String(a.journal || '').localeCompare(String(b.journal || ''));
    });
    renderJournalIndex();
  } catch (error) {
    body.innerHTML = `<tr><td colspan="6">${journalEscape(error.message)}</td></tr>`;
    const summary = document.querySelector('#journal-page-summary');
    if (summary) summary.textContent = 'Unable to load journal index';
  }
}

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
