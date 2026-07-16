#!/usr/bin/env python3
"""Build Journal Club pages from Markdown files in journal-club/posts/."""

from __future__ import annotations

import html
import re
import shutil
from datetime import date, datetime
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "journal-club" / "posts"
ARTICLES_DIR = ROOT / "journal-club" / "articles"
INDEX_FILE = ROOT / "journal-club" / "index.html"
START_MARKER = "<!-- JOURNAL_POSTS_START -->"
END_MARKER = "<!-- JOURNAL_POSTS_END -->"


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "journal-club-entry"


def parse_post(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, flags=re.S)
    if not match:
        raise ValueError(f"{path}: missing YAML front matter")
    metadata = yaml.safe_load(match.group(1)) or {}
    body = match.group(2).strip()
    return metadata, body


def date_text(value: object) -> str:
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")
    return str(value or "Undated")


def build_article(meta: dict, body: str, slug: str) -> str:
    title = html.escape(str(meta.get("title", slug.replace("-", " ").title())) )
    short_title = html.escape(str(meta.get("short_title", meta.get("title", title))))
    published = html.escape(date_text(meta.get("date")))
    journal = html.escape(str(meta.get("journal", "")))
    authors = html.escape(str(meta.get("authors", "")))
    doi = html.escape(str(meta.get("doi", "")))
    paper_url = html.escape(str(meta.get("paper_url", "")), quote=True)
    topics = meta.get("topics", []) or []
    if isinstance(topics, str):
        topics = [topics]

    article_html = markdown.markdown(
        body,
        extensions=["extra", "fenced_code", "tables", "toc", "sane_lists"],
        output_format="html5",
    )
    topic_html = "".join(f'<span class="jc-tag">{html.escape(str(topic))}</span>' for topic in topics)
    source_link = f'<a href="{paper_url}" target="_blank" rel="noreferrer">Original paper ↗</a>' if paper_url else ""
    doi_line = f'<span>DOI: {doi}</span>' if doi else ""

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{short_title} — Journal Club by Song Jie">
  <title>{title} | Journal Club</title>
  <link rel="stylesheet" href="../../../styles.css?v=20260716-nav-separate">
  <link rel="stylesheet" href="../../../nav-emphasis.css?v=20260716-nav-grey">
  <link rel="stylesheet" href="../../journal-club.css?v=20260716-auto-publish">
  <script>
    window.MathJax = {{tex: {{inlineMath: [['\\\\(', '\\\\)']], displayMath: [['\\\\[', '\\\\]']]}}}};
  </script>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
  <main>
    <header class="site-header">
      <a class="wordmark" href="/">Song Jie</a>
      <nav aria-label="Collection navigation">
        <a href="/">Home</a><a href="/blog/">Blog</a><a href="/tutorial/">Tutorial</a><a href="/gallery/">Gallery</a>
        <a class="nav-journal-club" href="/journal-club/" aria-current="page">Journal Club</a>
        <a href="/statgen-radar/">StatGen Radar</a>
      </nav>
    </header>
    <article class="jc-article-shell">
      <a class="back-link" href="/journal-club/">← Journal Club</a>
      <p class="eyebrow">Journal Club · {published}</p>
      <h1>{title}</h1>
      <div class="jc-paper-meta"><span>{authors}</span><span>{journal}</span>{doi_line}{source_link}</div>
      <div class="jc-tags">{topic_html}</div>
      <div class="jc-article-body">{article_html}</div>
    </article>
    <footer><p>© 2026 Song Jie</p><a href="/journal-club/">Journal Club →</a></footer>
  </main>
</body>
</html>'''


def build_card(meta: dict, slug: str) -> str:
    title = html.escape(str(meta.get("short_title", meta.get("title", slug.replace("-", " ").title()))))
    full_title = html.escape(str(meta.get("title", title)))
    published = html.escape(date_text(meta.get("date")))
    journal = html.escape(str(meta.get("journal", "")))
    authors = html.escape(str(meta.get("authors", "")))
    topics = meta.get("topics", []) or []
    if isinstance(topics, str):
        topics = [topics]
    tags = "".join(f'<span class="jc-tag">{html.escape(str(topic))}</span>' for topic in topics[:4])
    return f'''<article class="jc-card">
  <div class="jc-card-meta"><time>{published}</time><span>{journal}</span></div>
  <h2><a href="/journal-club/articles/{slug}/">{title}</a></h2>
  <p>{full_title}</p>
  <div class="jc-card-footer"><span>{authors}</span><div class="jc-tags">{tags}</div></div>
</article>'''


def main() -> None:
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    posts = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        meta, body = parse_post(path)
        if bool(meta.get("draft", False)):
            continue
        required = ["title", "date"]
        missing = [key for key in required if not meta.get(key)]
        if missing:
            raise ValueError(f"{path}: missing required front matter: {', '.join(missing)}")
        slug = slugify(str(meta.get("slug") or path.stem))
        posts.append((meta, body, slug))

    posts.sort(key=lambda item: date_text(item[0].get("date")), reverse=True)
    if ARTICLES_DIR.exists():
        shutil.rmtree(ARTICLES_DIR)
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    cards = []
    for meta, body, slug in posts:
        output_dir = ARTICLES_DIR / slug
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "index.html").write_text(build_article(meta, body, slug), encoding="utf-8")
        cards.append(build_card(meta, slug))

    if cards:
        listing = '<section class="jc-list" aria-label="Journal Club articles">\n' + "\n".join(cards) + "\n</section>"
    else:
        listing = '''<section class="collection-empty">
  <p class="notice-label">Discussions coming soon.</p>
  <p>Upload a Markdown file to <code>journal-club/posts/</code>; it will be published automatically.</p>
</section>'''

    index = INDEX_FILE.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), flags=re.S)
    replacement = f"{START_MARKER}\n{listing}\n{END_MARKER}"
    if not pattern.search(index):
        raise ValueError("Journal Club index is missing publication markers")
    INDEX_FILE.write_text(pattern.sub(replacement, index), encoding="utf-8")
    print(f"Published {len(posts)} Journal Club post(s).")


if __name__ == "__main__":
    main()
