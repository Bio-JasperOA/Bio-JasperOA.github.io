const ARCHIVE_URL = '/data/statgen-radar.json';

const StatGenStars = (() => {
  const storageKey = 'statgen-radar-pinned-v1';
  let memoryStars = new Set();

  function normalizeText(value) {
    return String(value || '').trim().toLowerCase().replace(/\s+/g, ' ');
  }

  function normalizeDoi(value) {
    const normalized = normalizeText(value)
      .replace(/^doi:\s*/i, '')
      .replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, '')
      .replace(/[?#].*$/, '');
    return /^(?:not provided|unavailable|na|n\/a|none|unknown|—|-)$/i.test(normalized)
      ? ''
      : normalized;
  }

  function key(record) {
    const doi = normalizeDoi(record?.doi ?? record?.DOI);
    if (doi && doi !== '—' && doi !== '-') return `doi:${doi}`;

    const article = normalizeText(record?.article ?? record?.title ?? record?.Article ?? 'untitled');
    const source = normalizeText(record?.journal ?? record?.Journal ?? record?.platform ?? record?.Platform ?? record?.source ?? 'unknown');
    return `article:${article}|source:${source}`;
  }

  function score(record) {
    const value = record?.score ?? record?.total ?? record?.Total;
    if (value === null || value === undefined || value === '') return null;
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
  }

  function read() {
    try {
      const saved = JSON.parse(window.localStorage.getItem(storageKey) || '[]');
      if (Array.isArray(saved)) memoryStars = new Set(saved.map(String));
    } catch (error) {
      // Keep the in-memory selection when browser storage is unavailable.
    }
    return new Set(memoryStars);
  }

  function write(stars) {
    memoryStars = new Set(stars);
    try {
      window.localStorage.setItem(storageKey, JSON.stringify([...memoryStars]));
    } catch (error) {
      // Star controls still work for the current page when storage is unavailable.
    }
  }

  function isPinned(record) {
    return read().has(key(record));
  }

  function toggle(record) {
    const stars = read();
    const recordKey = key(record);
    if (stars.has(recordKey)) stars.delete(recordKey);
    else stars.add(recordKey);
    write(stars);
    return stars.has(recordKey);
  }

  return { storageKey, key, score, normalizeDoi, keys: read, isPinned, toggle };
})();

window.StatGenStars = StatGenStars;

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[char]));
}

function summaryChips(item) {
  return [
    `${item.records ?? 0} records`,
    `${item.journal_articles ?? 0} journal articles`,
    `${item.preprints ?? 0} preprints`,
    `JIF ${item.jif_edition ?? 'N/A'}`
  ].map(text => `<span class="radar-chip">${escapeHtml(text)}</span>`).join('');
}

async function loadArchive() {
  const response = await fetch(`${ARCHIVE_URL}?v=${Date.now()}`);
  if (!response.ok) throw new Error(`Archive request failed: ${response.status}`);
  const items = await response.json();
  if (!Array.isArray(items)) throw new Error('The brief archive has an invalid format.');
  return items.sort((a, b) => String(b.date).localeCompare(String(a.date)));
}

async function renderIndex() {
  const latestRoot = document.querySelector('#latest');
  const archiveRoot = document.querySelector('#archive');
  if (!latestRoot || !archiveRoot) return;

  try {
    const items = await loadArchive();
    if (!items.length) {
      latestRoot.innerHTML = '<p class="notice-label">The first AI for Life Science brief is being prepared.</p><p>Top-journal articles and bioRxiv/arXiv preprints will appear here after the first daily run.</p>';
      archiveRoot.innerHTML = '<p class="notice-label">No daily briefs have been published yet.</p>';
      return;
    }
    const latest = items[0];
    latestRoot.innerHTML = `
      <p class="eyebrow">Latest Brief · ${escapeHtml(latest.date)}</p>
      <h2>${escapeHtml(latest.title || 'AI for Life Science Radar — Daily Brief')}</h2>
      <p>${escapeHtml(latest.summary || '')}</p>
      <div class="radar-meta">${summaryChips(latest)}</div>
      <a class="radar-primary-link" href="${escapeHtml(latest.url)}">Read the full brief →</a>`;

    const archiveLimit = 10;
    archiveRoot.innerHTML = items.map((item, index) => `
      <article class="radar-entry" data-archive-overflow="${index >= archiveLimit}"${index >= archiveLimit ? ' hidden' : ''}>
        <time datetime="${escapeHtml(item.date)}">${escapeHtml(item.date)}</time>
        <div>
          <h3>${escapeHtml(item.title || 'Daily Brief')}</h3>
          <p>${escapeHtml(item.records ?? 0)} records · ${escapeHtml(item.journal_articles ?? 0)} journal articles · ${escapeHtml(item.preprints ?? 0)} preprints</p>
        </div>
        <a href="${escapeHtml(item.url)}">Open →</a>
      </article>`).join('');

    const overflowEntries = [...archiveRoot.querySelectorAll('[data-archive-overflow="true"]')];
    if (overflowEntries.length) {
      const toggle = document.createElement('button');
      toggle.className = 'radar-archive-toggle';
      toggle.type = 'button';
      toggle.setAttribute('aria-expanded', 'false');
      toggle.textContent = `Show ${overflowEntries.length} more briefs ↓`;

      toggle.addEventListener('click', () => {
        const expanded = toggle.getAttribute('aria-expanded') === 'true';
        overflowEntries.forEach(entry => {
          entry.hidden = expanded;
        });
        toggle.setAttribute('aria-expanded', String(!expanded));
        toggle.textContent = expanded
          ? `Show ${overflowEntries.length} more briefs ↓`
          : 'Show fewer briefs ↑';
      });

      archiveRoot.appendChild(toggle);
    }
  } catch (error) {
    latestRoot.innerHTML = '<p class="notice-label">Unable to load the latest brief.</p>';
    archiveRoot.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
  }
}

function parseBriefStats(markdown) {
  const patterns = {
    hits: /Raw relevant hits:\s*(\d+)/i,
    records: /(?:Included records after quality control|Passed threshold):\s*(\d+)/i,
    journals: /Journal articles:\s*(\d+)/i,
    preprints: /Preprints:\s*(\d+)/i,
    jif: /JIF edition:\s*(\d{4})/i
  };
  const result = {};
  Object.entries(patterns).forEach(([key, pattern]) => {
    const match = markdown.match(pattern);
    result[key] = match ? match[1] : null;
  });
  return result;
}

function injectSummaryGrid(root, stats) {
  const title = root.querySelector('h1');
  if (!title) return;
  const items = [
    ['Included', stats.records],
    ['Journal articles', stats.journals],
    ['Preprints', stats.preprints],
    ['JIF edition', stats.jif]
  ].filter(([, value]) => value);
  if (!items.length) return;
  const grid = document.createElement('div');
  grid.className = 'radar-summary-grid';
  grid.innerHTML = items.map(([label, value]) => `
    <div class="radar-summary-stat">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
    </div>`).join('');
  title.insertAdjacentElement('afterend', grid);
}

function linkDoi(value) {
  const text = StatGenStars.normalizeDoi(value);
  if (!text) return '<span class="radar-record-doi">DOI unavailable</span>';
  return `<a class="radar-record-doi" href="https://doi.org/${encodeURI(text)}" target="_blank" rel="noreferrer">${escapeHtml(text)} ↗</a>`;
}

function transformInclusionTable(root) {
  const tables = [...root.querySelectorAll('table')];
  const table = tables.find(candidate => {
    const heads = [...candidate.querySelectorAll('thead th')].map(cell => cell.textContent.trim().toLowerCase());
    return heads.includes('article') && heads.includes('total') && heads.some(head => head.includes('journal'));
  });
  if (!table) return;

  const headers = [...table.querySelectorAll('thead th')].map(cell => cell.textContent.trim());
  const rows = [...table.querySelectorAll('tbody tr')];
  const list = document.createElement('div');
  list.className = 'radar-record-list';
  const entries = [];

  function updateEntry(entry, pinnedKeys) {
    const pinned = pinnedKeys.has(StatGenStars.key(entry.record));
    entry.card.classList.toggle('is-pinned', pinned);
    entry.button.setAttribute('aria-pressed', String(pinned));
    entry.button.setAttribute('aria-label', `${pinned ? 'Unpin' : 'Pin'} ${entry.record.article}`);
    entry.button.title = pinned ? 'Remove from pinned articles' : 'Pin this article';
    entry.button.querySelector('[aria-hidden="true"]').textContent = pinned ? '★' : '☆';
  }

  function arrangeEntries() {
    const pinnedKeys = StatGenStars.keys();
    entries.forEach(entry => updateEntry(entry, pinnedKeys));
    const ordered = [...entries].sort((a, b) => {
      const pinnedA = pinnedKeys.has(StatGenStars.key(a.record));
      const pinnedB = pinnedKeys.has(StatGenStars.key(b.record));
      if (pinnedA !== pinnedB) return pinnedA ? -1 : 1;
      if (pinnedA && pinnedB) {
        const scoreA = StatGenStars.score(a.record) ?? -Infinity;
        const scoreB = StatGenStars.score(b.record) ?? -Infinity;
        if (scoreA !== scoreB) return scoreB - scoreA;
      }
      return a.originalOrder - b.originalOrder;
    });
    list.replaceChildren(...ordered.map(entry => entry.card));
    list.dataset.pinnedCount = String(ordered.filter(entry => pinnedKeys.has(StatGenStars.key(entry.record))).length);
  }

  rows.forEach((row, originalOrder) => {
    const values = [...row.querySelectorAll('td')].map(cell => cell.textContent.trim());
    const sourceRecord = Object.fromEntries(headers.map((header, index) => [header, values[index] || '']));
    const number = sourceRecord['No.'] || sourceRecord['No'] || '';
    const title = sourceRecord.Article || 'Untitled record';
    const type = sourceRecord.Type || '';
    const journal = sourceRecord['Journal / platform'] || sourceRecord.Journal || '';
    const jif = sourceRecord['2025 JIF'] || sourceRecord.JIF || '';
    const relevance = sourceRecord.Relevance || '';
    const publication = sourceRecord.Publication || '';
    const total = sourceRecord.Total || '';
    const doi = sourceRecord.DOI || '';
    const record = { article: title, journal, doi, score: total };

    const card = document.createElement('article');
    card.className = 'radar-record-card';
    card.innerHTML = `
      <div class="radar-record-header">
        <span class="radar-record-number">${escapeHtml(number)}</span>
        <h3 class="radar-record-title">${escapeHtml(title)}</h3>
        <span class="radar-score-badge">Score ${escapeHtml(total)}</span>
        <button class="radar-star-button" type="button" aria-pressed="false"><span aria-hidden="true">☆</span></button>
      </div>
      <div class="radar-record-meta">
        ${type ? `<span><strong>Type</strong> ${escapeHtml(type)}</span>` : ''}
        ${journal ? `<span><strong>Source</strong> ${escapeHtml(journal)}</span>` : ''}
        ${jif ? `<span><strong>JIF</strong> ${escapeHtml(jif)}</span>` : ''}
        ${relevance ? `<span><strong>Relevance</strong> ${escapeHtml(relevance)}</span>` : ''}
        ${publication ? `<span><strong>Publication</strong> ${escapeHtml(publication)}</span>` : ''}
      </div>
      ${linkDoi(doi)}`;

    const button = card.querySelector('.radar-star-button');
    const entry = { record, card, button, originalOrder };
    button.addEventListener('click', () => {
      StatGenStars.toggle(record);
      arrangeEntries();
    });
    entries.push(entry);
  });

  arrangeEntries();
  window.addEventListener('storage', event => {
    if (event.key === StatGenStars.storageKey) arrangeEntries();
  });

  table.classList.add('radar-table-source');
  table.insertAdjacentElement('afterend', list);
}

function tidyBriefMeta(root) {
  const title = root.querySelector('h1');
  if (!title) return;
  let node = title.nextElementSibling;
  while (node && node.tagName === 'P') {
    const next = node.nextElementSibling;
    const text = node.textContent.trim();
    if (/^(Generated|Window|Profile|Raw relevant hits|Included records(?: after quality control)?|Collected records|Scored unique candidates|Eligible before limit|Passed threshold|Filtered out|Omitted by report limit|Journal articles(?: with configured JIF)?|Top-journal articles|Preprints|Report limit|JIF edition):/i.test(text)) {
      node.remove();
      node = next;
    } else {
      break;
    }
  }
}

async function renderArticle() {
  const root = document.querySelector('#brief');
  if (!root || !document.body.hasAttribute('data-radar-article')) return;

  const params = new URLSearchParams(window.location.search);
  const date = params.get('date');
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date || '')) {
    root.innerHTML = '<h1>Brief not found</h1><p>A valid date was not provided.</p>';
    return;
  }

  try {
    const response = await fetch(`reports/${date}.md?v=${Date.now()}`);
    if (!response.ok) throw new Error(`Brief request failed: ${response.status}`);
    const markdown = await response.text();
    root.innerHTML = window.marked ? marked.parse(markdown) : `<pre>${escapeHtml(markdown)}</pre>`;
    const stats = parseBriefStats(markdown);
    tidyBriefMeta(root);
    injectSummaryGrid(root, stats);
    transformInclusionTable(root);
    document.title = `AI for Life Science Radar — ${date} | Song Jie`;
  } catch (error) {
    root.innerHTML = `<h1>Brief unavailable</h1><p>${escapeHtml(error.message)}</p>`;
  }
}

renderIndex();
renderArticle();
