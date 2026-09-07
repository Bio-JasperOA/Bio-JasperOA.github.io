#!/usr/bin/env python3
"""Build Journal Club pages; Markdown and assets are permanent source files.

Only generated articles/*/index.html files are replaced. Every published source
is validated before changing output, and draft posts never produce a page.
"""
from __future__ import annotations

import html
import posixpath
import re
import sys
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

import markdown
import yaml

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "journal-club" / "posts"
ARTICLES_DIR = ROOT / "journal-club" / "articles"
INDEX_FILE = ROOT / "journal-club" / "index.html"
START_MARKER = "<!-- JOURNAL_POSTS_START -->"
END_MARKER = "<!-- JOURNAL_POSTS_END -->"
VERSION = "20260907-publishing"
SITE_HOST = "bio-jasperoa.github.io"
CATEGORY_NAMES = {
    "development-virtual-embryos": "Development & Virtual Embryos",
    "virtual-cells": "Virtual Cells",
    "spatial-biology-virtual-tissues": "Spatial Biology & Virtual Tissues",
    "biological-foundation-models": "Biological Foundation Models",
    "algorithms-theory": "Algorithms & Theory",
    "data-benchmarks": "Data & Benchmarks",
}
CATEGORIES = CATEGORY_NAMES
CATEGORY_LOOKUP = {name.casefold(): slug for slug, name in CATEGORY_NAMES.items()}
CATEGORY_LOOKUP.update({slug: slug for slug in CATEGORY_NAMES})
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "journal-club-entry"


def parse_post(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, flags=re.S)
    if not match:
        raise ValueError(f"{path}: missing YAML front matter")
    try:
        metadata = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML front matter: {exc}") from exc
    if not isinstance(metadata, dict):
        raise ValueError(f"{path}: YAML front matter must be a mapping")
    return metadata, match.group(2).strip()


def text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if item is not None)
    return str(value).strip()


def esc(value: object) -> str:
    return html.escape(text(value), quote=True)


def remove_duplicate_leading_title(body: str, title: str) -> str:
    match = re.match(r"^#\s+(.+?)\s*(?:\n+|$)", body)
    if not match:
        return body
    heading = re.sub(r"\s+", " ", match.group(1)).strip().casefold()
    expected = re.sub(r"\s+", " ", title).strip().casefold()
    return body[match.end():].lstrip() if heading == expected else body


def protect_math(value: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}
    def stash(match: re.Match[str], kind: str) -> str:
        token = f"MATHPLACEHOLDER{kind}{len(placeholders)}END"
        placeholders[token] = match.group(0)
        return token
    value = re.sub(r"\\\[(.+?)\\\]", lambda m: stash(m, "DISPLAY"), value, flags=re.S)
    value = re.sub(r"\\\((.+?)\\\)", lambda m: stash(m, "INLINE"), value, flags=re.S)
    return value, placeholders


def restore_math(value: str, placeholders: dict[str, str]) -> str:
    for token, formula in placeholders.items():
        value = value.replace(token, html.escape(formula, quote=False))
    return value


def date_text(value: object) -> str:
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")
    return text(value) or "Undated"


def date_key(value: object) -> tuple[int, str]:
    value = date_text(value)
    try:
        return (1, datetime.fromisoformat(value).date().isoformat())
    except ValueError:
        return (0, "")


def normalize_url(value: object, *, root: Path, source: Path, slug: str,
                  kind: str = "link") -> tuple[str, bool]:
    """Return final-page URL and whether it is same-origin.

    Root-relative URLs are recommended. Relative URLs resolve against the final
    /journal-club/articles/<slug>/ page, never against the Markdown directory.
    Same-origin files are checked locally; remote resources are not fetched.
    """
    value = text(value)
    if not value:
        return "", False
    error = lambda message: ValueError(f"{source}: {message}: {value}")
    decoded = unquote(value)
    if any(ord(char) < 32 for char in decoded) or "\\" in decoded:
        raise error("invalid resource URL (control character or local path)")
    try:
        parsed = urlsplit(value)
        scheme, host = parsed.scheme.casefold(), (parsed.hostname or "").casefold()
        if parsed.port is not None and parsed.port not in (80, 443):
            raise error("unsupported resource URL port")
    except ValueError as exc:
        raise error("invalid resource URL") from exc
    if scheme not in ("", "http", "https") or (not scheme and parsed.netloc):
        raise error("unsupported resource URL protocol; use HTTPS or a site path")
    if scheme and (not host or parsed.username or parsed.password):
        raise error("invalid resource URL host")
    # GitHub's file viewer is a valid code/documentation citation, but cannot
    # serve as the file itself for an image, main PDF, or attachment.
    if kind in ("image", "pdf", "attachment") and host == "github.com" and "/blob/" in parsed.path:
        raise error("GitHub blob URLs are HTML pages; use a site asset path or a raw file URL")
    if kind == "pdf" and Path(parsed.path).suffix.casefold() in {".html", ".htm", ".png", ".jpg", ".jpeg", ".gif", ".svg"}:
        raise error("main PDF URL points to an HTML page or image")
    same_origin = not scheme or host == SITE_HOST
    if not same_origin:
        return value, False
    if not parsed.path and parsed.fragment:
        if kind in ("image", "pdf", "attachment"):
            raise error(f"{kind} needs a file path, not a page fragment")
        return value, True
    raw_path = unquote(parsed.path)
    if raw_path.startswith("//"):
        raise error("protocol-relative resource paths are not supported")
    if raw_path.startswith("/"):
        final_path = posixpath.normpath(raw_path)
    else:
        final_path = posixpath.normpath(f"/journal-club/articles/{slug}/{raw_path}")
    local_path = (root / final_path.lstrip("/")).resolve()
    try:
        local_path.relative_to(root.resolve())
    except ValueError as exc:
        raise error("resource path leaves the website root") from exc
    is_image = local_path.suffix.casefold() in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif", ".tif", ".tiff"}
    if (kind in ("image", "pdf", "attachment") or is_image) and not local_path.is_file():
        raise error(f"missing local {kind} file (resolved to {final_path})")
    # Check local PDFs even when supplied as ordinary Markdown/HTML links.
    if kind == "pdf" or local_path.suffix.casefold() == ".pdf":
        if not local_path.is_file():
            raise error(f"missing local PDF file (resolved to {final_path})")
        with local_path.open("rb") as handle:
            if not handle.read(1024).lstrip().startswith(b"%PDF-"):
                raise error("file is not a PDF (missing %PDF- header)")
    if kind in ("image", "pdf", "attachment") and final_path.startswith("/journal-club/articles/"):
        # Kept for old posts, with a clear migration warning; never delete files.
        print(f"WARNING: {source}: legacy asset in generated directory: {final_path}; move it to /journal-club/assets/ when convenient", file=sys.stderr)
    normalized = urlunsplit(("", "", quote(final_path, safe="/@:+-._~"), parsed.query, parsed.fragment))
    return normalized, True


def prepare_meta(meta: dict, *, root: Path, source: Path, slug: str) -> dict:
    meta = dict(meta)
    mode = text(meta.get("content_mode")) or "article"
    if mode not in ("article", "pdf-first", "hybrid"):
        raise ValueError(f"{source}: content_mode must be article, pdf-first, or hybrid")
    meta["content_mode"] = mode
    topics = meta.get("topics") or []
    if isinstance(topics, str):
        topics = [topics]
    if not isinstance(topics, list):
        raise ValueError(f"{source}: topics must be a list or a string")
    meta["topics"] = list(dict.fromkeys(text(topic) for topic in topics if text(topic)))
    raw_category = meta.get("category")
    if isinstance(raw_category, (list, dict)):
        raise ValueError(f"{source}: category must contain one main category, not a list")
    category = text(raw_category)
    if category:
        # Slugs are stable; display names remain accepted for earlier sources.
        category = CATEGORY_LOOKUP.get(category.casefold(), "")
        if not category:
            print(f"WARNING: {source}: unknown category {raw_category!r}; retained in All. Replace it with one of: {', '.join(CATEGORY_NAMES)}", file=sys.stderr)
    else:
        matches = {CATEGORY_LOOKUP[topic.casefold()] for topic in meta["topics"] if topic.casefold() in CATEGORY_LOOKUP}
        category = next(iter(matches)) if len(matches) == 1 else ""
        if not category:
            print(f"WARNING: {source}: category missing or ambiguous; retained in All. Add one category slug.", file=sys.stderr)
    meta["category"] = category
    meta["summary"] = text(meta.get("summary"))
    if mode == "pdf-first" and not meta["summary"]:
        raise ValueError(f"{source}: pdf-first requires a meaningful summary for the directory and introduction")
    paper_url, _ = normalize_url(meta.get("paper_url"), root=root, source=source, slug=slug)
    pdf_url, pdf_local = normalize_url(meta.get("pdf_url"), root=root, source=source, slug=slug, kind="pdf")
    if mode in ("pdf-first", "hybrid") and not pdf_url:
        raise ValueError(f"{source}: {mode} requires a valid main PDF in pdf_url")
    meta["paper_url"], meta["pdf_url"], meta["_pdf_local"] = paper_url, pdf_url, pdf_local
    meta["pdf_label"] = text(meta.get("pdf_label")) or "Open PDF"
    attachments = meta.get("attachments") or []
    if not isinstance(attachments, list):
        raise ValueError(f"{source}: attachments must be a list of title/url mappings")
    seen = {url for url in (paper_url, pdf_url) if url}
    checked = []
    for attachment in attachments:
        if not isinstance(attachment, dict):
            raise ValueError(f"{source}: each attachment must contain title and url")
        label, value = text(attachment.get("title")), text(attachment.get("url"))
        if not label and not value:
            continue
        if not value:
            raise ValueError(f"{source}: attachment {label!r} is missing url")
        if not label:
            raise ValueError(f"{source}: attachment {value!r} is missing title")
        url, local = normalize_url(value, root=root, source=source, slug=slug, kind="attachment")
        if url not in seen:
            checked.append({"title": label, "url": url, "local": local})
            seen.add(url)
    meta["attachments"] = checked
    return meta


class Element:
    def __init__(self, tag: str, attrs: list[tuple[str, str | None]] | None = None):
        self.tag, self.attrs, self.children = tag, dict(attrs or []), []


def serialize(node: Element | str) -> str:
    if isinstance(node, str):
        return node
    attrs = "".join(f' {key}' if value is None else f' {key}="{html.escape(value, quote=True)}"' for key, value in node.attrs.items())
    if not node.tag:
        return "".join(serialize(child) for child in node.children)
    if node.tag in VOID_TAGS:
        return f"<{node.tag}{attrs}>"
    return f"<{node.tag}{attrs}>" + "".join(serialize(child) for child in node.children) + f"</{node.tag}>"


class BodyParser(HTMLParser):
    """Small HTML tree for link checks and images; raw inline HTML stays usable."""
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.tree = Element("")
        self.stack = [self.tree]

    def handle_starttag(self, tag, attrs):
        node = Element(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)

    def handle_entityref(self, name):
        self.handle_data(f"&{name};")

    def handle_charref(self, name):
        self.handle_data(f"&#{name};")

    def handle_comment(self, value):
        self.handle_data(f"<!--{value}-->")

    def handle_decl(self, value):
        self.handle_data(f"<!{value}>")


def render_body(body: str, *, root: Path, source: Path, slug: str) -> str:
    protected, formulas = protect_math(body)
    output = markdown.markdown(protected, extensions=["extra", "fenced_code", "tables", "toc", "sane_lists"], output_format="html5")
    parser = BodyParser()
    parser.feed(output)
    parser.close()

    def process(node: Element, ancestors: tuple[str, ...] = ()) -> None:
        resource_attrs = ["href", "src", "poster", "xlink:href"]
        if node.tag == "object":
            resource_attrs.append("data")
        for attr in resource_attrs:
            if node.attrs.get(attr):
                kind = "image" if node.tag == "img" or attr == "poster" else "link"
                url, _ = normalize_url(node.attrs[attr], root=root, source=source, slug=slug, kind=kind)
                node.attrs[attr] = url
        if node.attrs.get("srcset"):
            entries = []
            for candidate in node.attrs["srcset"].split(","):
                parts = candidate.strip().split()
                if not parts:
                    continue
                url, _ = normalize_url(parts[0], root=root, source=source, slug=slug, kind="image")
                entries.append(" ".join([url] + parts[1:]))
            node.attrs["srcset"] = ", ".join(entries)
        if node.tag == "img":
            if not node.attrs.get("src"):
                raise ValueError(f"{source}: image is missing its src path")
            node.attrs.setdefault("alt", "")
            node.attrs.setdefault("loading", "lazy")
            node.attrs.setdefault("decoding", "async")
        # Images in standalone Markdown paragraphs gain a figure and optional
        # caption from the Markdown image title. Existing figure captions stay.
        content = [item for item in node.children if not isinstance(item, str) or item.strip()]
        image = None
        if len(content) == 1 and isinstance(content[0], Element):
            if content[0].tag == "img":
                image = content[0]
            elif content[0].tag == "a" and len(content[0].children) == 1 and isinstance(content[0].children[0], Element) and content[0].children[0].tag == "img":
                image = content[0].children[0]
        if node.tag == "p" and image is not None and "figure" not in ancestors:
            node.tag = "figure"
            node.attrs["class"] = "jc-figure"
            if image.attrs.get("title"):
                caption = Element("figcaption")
                caption.children = [html.escape(image.attrs["title"])]
                node.children.append(caption)
        revised = []
        for child in node.children:
            if isinstance(child, Element):
                process(child, ancestors + (node.tag,))
                if child.tag == "img" and node.tag != "a" and "a" not in ancestors:
                    link = Element("a", [("class", "jc-image-link"), ("href", child.attrs["src"]), ("target", "_blank"), ("rel", "noopener noreferrer"), ("aria-label", f"Open original image: {child.attrs.get('alt') or 'figure'}")])
                    link.children = [child]
                    child = link
            revised.append(child)
        node.children = revised
    process(parser.tree)
    return restore_math(serialize(parser.tree), formulas)


def full_navigation() -> str:
    return '''<nav aria-label="Primary navigation">
        <a href="/#about">About</a>
        <a href="/#services">Interests</a>
        <a href="/#news">News</a>
        <a href="/#publications">Publications</a>
        <a href="/#honors">Honors</a>
        <a href="/#education">Education</a>
        <a class="nav-blog" href="/blog/">Blog</a>
        <a class="nav-tutorial" href="/tutorial/">Tutorial</a>
        <a class="nav-gallery" href="/gallery/">Gallery</a>
        <a class="nav-journal-club" href="/journal-club/" aria-current="page">Journal Club</a>
        <a href="/statgen-radar/">AI4Life Radar</a>
      </nav>'''


def category_markup(meta: dict) -> str:
    category = meta.get("category", "")
    if category:
        return f'<span class="jc-tag jc-category">{esc(CATEGORY_NAMES[category])}</span>'
    return '<span class="jc-category-note">Category not assigned</span>'


def render_resources(meta: dict) -> tuple[str, str]:
    """Resource links above body; optional lazy preview below complete body."""
    links = []
    pdf_url = meta.get("pdf_url", "")
    if pdf_url:
        links.append(f'<a class="jc-resource-link" href="{esc(pdf_url)}" target="_blank" rel="noopener noreferrer">{esc(meta["pdf_label"])}</a>')
        if meta["_pdf_local"]:
            links.append(f'<a class="jc-resource-link" href="{esc(pdf_url)}" download>Download PDF</a>')
    for attachment in meta.get("attachments", []):
        links.append(f'<a class="jc-resource-link" href="{esc(attachment["url"])}" target="_blank" rel="noopener noreferrer">{esc(attachment["title"])}</a>')
    resources = '<div class="jc-resources"><div class="jc-resource-links">' + "".join(links) + '</div></div>' if links else ""
    preview = ""
    if pdf_url and meta["_pdf_local"] and meta["content_mode"] in ("pdf-first", "hybrid"):
        opened = " open" if meta["content_mode"] == "pdf-first" else ""
        preview = f'''<details class="jc-pdf-preview"{opened}>
  <summary>Read PDF on this page</summary>
  <p class="jc-pdf-help">If the preview is unavailable, use the PDF link above to open the file directly.</p>
  <iframe class="jc-pdf-frame" data-jc-pdf-frame data-src="{esc(pdf_url)}" title="PDF reading notes: {esc(meta['title'])}" loading="lazy"></iframe>
  <noscript><p>Use the PDF link above to read this document.</p></noscript>
</details>'''
    elif pdf_url and not meta["_pdf_local"] and meta["content_mode"] in ("pdf-first", "hybrid"):
        preview = '<p class="jc-pdf-help">This PDF opens on an external website.</p>'
    return resources, preview


def build_article(meta: dict, body: str, slug: str, *, root: Path = ROOT,
                  source: Path | None = None, prepared: bool = False) -> str:
    source = source or root / "journal-club" / "posts" / f"{slug}.md"
    if not prepared:
        meta = prepare_meta(meta, root=root, source=source, slug=slug)
    raw_title = text(meta.get("title")) or slug.replace("-", " ").title()
    title = esc(raw_title)
    description = esc(meta.get("summary") or meta.get("short_title") or raw_title)
    published = esc(date_text(meta.get("date")))
    article_html = render_body(remove_duplicate_leading_title(body, raw_title), root=root, source=source, slug=slug)
    topic_html = "".join(f'<span class="jc-tag">{esc(topic)}</span>' for topic in meta["topics"])
    metadata = []
    if text(meta.get("authors")):
        metadata.append(f'<span>{esc(meta["authors"])}</span>')
    publication = " · ".join(text(meta.get(field)) for field in ("journal", "year") if text(meta.get(field)))
    if publication:
        metadata.append(f'<span>{esc(publication)}</span>')
    if text(meta.get("status")):
        metadata.append(f'<span>{esc(meta["status"])}</span>')
    if text(meta.get("doi")):
        metadata.append(f'<span>DOI: {esc(meta["doi"])}</span>')
    # A primary PDF URL shared with paper_url gets one primary opening control.
    if meta.get("paper_url") and meta["paper_url"] != meta.get("pdf_url"):
        metadata.append(f'<a href="{esc(meta["paper_url"])}" target="_blank" rel="noopener noreferrer">Original paper ↗</a>')
    meta_html = '<div class="jc-paper-meta">' + "".join(metadata) + '</div>' if metadata else ""
    summary = f'<p class="jc-article-summary">{esc(meta["summary"])}</p>' if meta.get("summary") else ""
    resources, preview = render_resources(meta)
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{description}">
  <title>{title} | Journal Club</title>
  <link rel="stylesheet" href="/styles.css?v=20260811-nav-black">
  <link rel="stylesheet" href="/nav-emphasis.css?v=20260812-nav-underline-restored">
  <link rel="stylesheet" href="/journal-club/journal-club.css?v={VERSION}">
  <script src="/journal-club/journal-club.js?v={VERSION}" defer></script>
  <script>
    window.MathJax = {{tex: {{inlineMath: [['\\\\(', '\\\\)']], displayMath: [['\\\\[', '\\\\]']]}}}};
  </script>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
  <main>
    <header class="site-header">
      <a class="wordmark" href="/">Song Jie</a>
      {full_navigation()}
    </header>
    <article class="jc-article-shell" data-content-mode="{esc(meta['content_mode'])}">
      <a class="back-link" href="/journal-club/">← Journal Club</a>
      <p class="eyebrow">Journal Club · <time>{published}</time></p>
      <h1>{title}</h1>
      {meta_html}
      <div class="jc-tags">{category_markup(meta)}{topic_html}</div>
      {summary}
      {resources}
      <div class="jc-article-body">{article_html}</div>
      {preview}
    </article>
    <footer><p>© 2026 Song Jie</p><a href="/journal-club/">Journal Club →</a></footer>
  </main>
</body>
</html>'''


def build_card(meta: dict, slug: str) -> str:
    title = esc(meta.get("short_title") or meta.get("title") or slug.replace("-", " ").title())
    published = esc(date_text(meta.get("date")))
    journal = f'<span>{esc(meta["journal"])}</span>' if text(meta.get("journal")) else ""
    tags = "".join(f'<span class="jc-tag">{esc(topic)}</span>' for topic in meta.get("topics", [])[:4])
    # Legacy cards retain the full paper title. Never truncate rich body text.
    intro = meta.get("summary") or meta.get("title")
    intro_html = f'<p class="jc-card-summary">{esc(intro)}</p>' if intro else ""
    authors = f'<span>{esc(meta["authors"])}</span>' if text(meta.get("authors")) else ""
    return f'''<article class="jc-card" data-jc-card data-category="{esc(meta.get('category', ''))}">
  <div class="jc-card-meta"><time>{published}</time>{journal}</div>
  <h2><a href="/journal-club/articles/{slug}/">{title}</a></h2>
  {intro_html}
  <div class="jc-tags">{category_markup(meta)}</div>
  <div class="jc-card-footer">{authors}<div class="jc-tags">{tags}</div></div>
</article>'''


def build(root: Path = ROOT) -> int:
    root = Path(root).resolve()
    posts_dir, articles_dir = root / "journal-club/posts", root / "journal-club/articles"
    index_file = root / "journal-club/index.html"
    posts = []
    seen_slugs: dict[str, Path] = {}
    for path in sorted(posts_dir.glob("*.md")):
        meta, body = parse_post(path)
        if "draft" in meta and not isinstance(meta["draft"], bool):
            raise ValueError(f"{path}: draft must be YAML true or false (without quotes)")
        if meta.get("draft") is True:
            continue
        missing = [key for key in ("title", "date") if not text(meta.get(key))]
        if missing:
            raise ValueError(f"{path}: missing required front matter: {', '.join(missing)}")
        slug = slugify(text(meta.get("slug")) or path.stem)
        if slug in seen_slugs:
            raise ValueError(f"{path}: duplicate output slug {slug!r}; also used by {seen_slugs[slug]}")
        seen_slugs[slug] = path
        meta = prepare_meta(meta, root=root, source=path, slug=slug)
        posts.append((meta, body, slug, path))
    posts.sort(key=lambda post: date_key(post[0].get("date")), reverse=True)
    # All resources and body HTML are checked before touching existing output.
    outputs = [(slug, build_article(meta, body, slug, root=root, source=path, prepared=True)) for meta, body, slug, path in posts]
    cards = [build_card(meta, slug) for meta, _, slug, _ in posts]
    listing = '<section class="jc-list" aria-label="Journal Club articles">\n' + "\n".join(cards) + "\n</section>"
    if not cards:
        listing += '''\n<section class="collection-empty">
  <p class="notice-label">Discussions coming soon.</p>
  <p>Research discussions and reading notes will appear here.</p>
</section>'''
    index = index_file.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), flags=re.S)
    if len(pattern.findall(index)) != 1:
        raise ValueError(f"{index_file}: expected exactly one pair of publication markers")
    replacement = f"{START_MARKER}\n{listing}\n{END_MARKER}"
    index = pattern.sub(lambda _: replacement, index)
    articles_dir.mkdir(parents=True, exist_ok=True)
    # Never remove source assets or legacy attachments. Only page index files
    # produced by this builder are removed, including pages now marked draft.
    for old_page in articles_dir.glob("*/index.html"):
        old_page.unlink()
    for slug, output in outputs:
        output_dir = articles_dir / slug
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "index.html").write_text(output, encoding="utf-8")
    # Empty obsolete output directories can be removed without risking files.
    for directory in articles_dir.iterdir():
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
    index_file.write_text(index, encoding="utf-8")
    print(f"Published {len(posts)} Journal Club post(s).")
    return len(posts)


def main() -> None:
    try:
        build()
    except (ValueError, OSError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
