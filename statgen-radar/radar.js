const ARCHIVE_URL = '/data/statgen-radar.json';

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
  if (!Array.isArray(items) || !items.length) throw new Error('No Radar briefs are available.');
  return items.sort((a, b) => String(b.date).localeCompare(String(a.date)));
}

async function renderIndex() {
  const latestRoot = document.querySelector('#latest');
  const archiveRoot = document.querySelector('#archive');
  if (!latestRoot || !archiveRoot) return;

  try {
    const items = await loadArchive();
    const latest = items[0];
    latestRoot.innerHTML = `
      <p class="eyebrow">Latest Brief · ${escapeHtml(latest.date)}</p>
      <h2>${escapeHtml(latest.title || 'StatGen Radar — Daily Brief')}</h2>
      <p>${escapeHtml(latest.summary || '')}</p>
      <div class="radar-meta">${summaryChips(latest)}</div>
      <a class="radar-primary-link" href="${escapeHtml(latest.url)}">Read the full brief →</a>`;

    archiveRoot.innerHTML = items.map(item => `
      <article class="radar-entry">
        <time datetime="${escapeHtml(item.date)}">${escapeHtml(item.date)}</time>
        <div>
          <h3>${escapeHtml(item.title || 'Daily Brief')}</h3>
          <p>${escapeHtml(item.records ?? 0)} records · ${escapeHtml(item.journal_articles ?? 0)} journal articles · ${escapeHtml(item.preprints ?? 0)} preprints</p>
        </div>
        <a href="${escapeHtml(item.url)}">Open →</a>
      </article>`).join('');
  } catch (error) {
    latestRoot.innerHTML = '<p class="notice-label">Unable to load the latest brief.</p>';
    archiveRoot.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
  }
}

function parseBriefStats(markdown) {
  const patterns = {
    hits: /Raw relevant hits:\s*(\d+)/i,
    records: /Included records after quality control:\s*(\d+)/i,
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
  const text = String(value || '').trim();
  if (!text || text === '—' || text === '-') return '<span class="radar-record-doi">DOI unavailable</span>';
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

  rows.forEach(row => {
    const values = [...row.querySelectorAll('td')].map(cell => cell.textContent.trim());
    const record = Object.fromEntries(headers.map((header, index) => [header, values[index] || '']));
    const number = record['No.'] || record['No'] || '';
    const title = record.Article || 'Untitled record';
    const type = record.Type || '';
    const journal = record['Journal / platform'] || record.Journal || '';
    const jif = record['2025 JIF'] || record.JIF || '';
    const relevance = record.Relevance || '';
    const publication = record.Publication || '';
    const total = record.Total || '';
    const doi = record.DOI || '';

    const card = document.createElement('article');
    card.className = 'radar-record-card';
    card.innerHTML = `
      <div class="radar-record-header">
        <span class="radar-record-number">${escapeHtml(number)}</span>
        <h3 class="radar-record-title">${escapeHtml(title)}</h3>
        <span class="radar-score-badge">Score ${escapeHtml(total)}</span>
      </div>
      <div class="radar-record-meta">
        ${type ? `<span><strong>Type</strong> ${escapeHtml(type)}</span>` : ''}
        ${journal ? `<span><strong>Source</strong> ${escapeHtml(journal)}</span>` : ''}
        ${jif ? `<span><strong>JIF</strong> ${escapeHtml(jif)}</span>` : ''}
        ${relevance ? `<span><strong>Relevance</strong> ${escapeHtml(relevance)}</span>` : ''}
        ${publication ? `<span><strong>Publication</strong> ${escapeHtml(publication)}</span>` : ''}
      </div>
      ${linkDoi(doi)}`;
    list.appendChild(card);
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
    if (/^(Generated|Window|Raw relevant hits|Included records|Journal articles|Preprints|JIF edition):/i.test(text)) {
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
    document.title = `StatGen Radar — ${date} | Song Jie`;
  } catch (error) {
    root.innerHTML = `<h1>Brief unavailable</h1><p>${escapeHtml(error.message)}</p>`;
  }
}

renderIndex();
renderArticle();