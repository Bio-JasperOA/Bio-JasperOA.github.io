# Content Input Guide

The website separates content from layout. Do not edit page structure when adding routine content.

## Blog

Edit `data/blog.json`. Add the newest item at the top:

```json
{
  "title": "Post title",
  "date": "2026-07-13",
  "summary": "One or two sentences describing the post.",
  "url": "https://example.com/full-post",
  "tags": ["Statistical Genetics", "Research Notes"]
}
```

The URL may point to a local HTML post, a DOI, a notebook, or an external article.

## Tutorial

Edit `data/tutorials.json`:

```json
{
  "title": "Tutorial title",
  "date": "2026-07-13",
  "summary": "What the reader will learn.",
  "url": "https://example.com/tutorial",
  "tags": ["GWAS", "R", "Beginner"]
}
```

## Gallery

1. Upload the image to `gallery/images/`.
2. Add an item to `data/gallery.json`:

```json
{
  "title": "Image title",
  "date": "2026-07-13",
  "image": "/gallery/images/file-name.jpg",
  "alt": "A factual description for screen readers",
  "caption": "Short context for the image"
}
```

## Recommended message format for assisted updates

Send the following to Codex:

```text
Type: Blog / Tutorial / Gallery
Title:
Date:
Summary or caption:
Full text or target URL:
Tags:
Image: attach if applicable
```

For long Blog posts or Tutorials, send the complete text. A dedicated local article page can then be created and linked automatically.
