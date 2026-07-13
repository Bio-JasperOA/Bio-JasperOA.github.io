(() => {
  const type = document.body.dataset.collection;
  const root = document.getElementById("collection-root");
  if (!type || !root) return;

  const escapeHTML = (value = "") => String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  })[char]);

  const renderTextItem = (item) => {
    const tags = Array.isArray(item.tags) ? item.tags.map(escapeHTML).join(" · ") : "";
    const title = item.url
      ? `<a href="${escapeHTML(item.url)}">${escapeHTML(item.title)}</a>`
      : escapeHTML(item.title);
    return `<article class="archive-item">
      <time>${escapeHTML(item.date)}</time>
      <div><h2>${title}</h2><p>${escapeHTML(item.summary)}</p>
      ${tags ? `<span class="archive-tags">${tags}</span>` : ""}</div>
    </article>`;
  };

  const renderGalleryItem = (item) => `<figure class="gallery-item">
    <img src="${escapeHTML(item.image)}" alt="${escapeHTML(item.alt || item.title)}" loading="lazy">
    <figcaption><strong>${escapeHTML(item.title)}</strong>
    ${item.caption ? `<span>${escapeHTML(item.caption)}</span>` : ""}</figcaption>
  </figure>`;

  fetch(`../data/${type}.json`)
    .then((response) => {
      if (!response.ok) throw new Error("Content could not be loaded.");
      return response.json();
    })
    .then((items) => {
      if (!Array.isArray(items) || items.length === 0) {
        const label = type === "gallery" ? "gallery entries" : type === "tutorials" ? "tutorials" : "posts";
        root.innerHTML = `<div class="collection-empty"><p class="notice-label">No ${label} published yet</p><p>New, verified content will appear here in reverse chronological order.</p></div>`;
        return;
      }
      root.innerHTML = type === "gallery"
        ? `<div class="gallery-grid">${items.map(renderGalleryItem).join("")}</div>`
        : items.map(renderTextItem).join("");
    })
    .catch(() => {
      root.innerHTML = '<div class="collection-empty"><p class="notice-label">Content unavailable</p><p>Please try again later.</p></div>';
    });
})();