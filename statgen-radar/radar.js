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
    latestRoot.innerHTML = `<p class="notice-label">Unable to load the latest brief.</p>`;
    archiveRoot.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
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
    document.title = `StatGen Radar — ${date} | Song Jie`;
  } catch (error) {
    root.innerHTML = `<h1>Brief unavailable</h1><p>${escapeHtml(error.message)}</p>`;
  }
}

renderIndex();
renderArticle();
