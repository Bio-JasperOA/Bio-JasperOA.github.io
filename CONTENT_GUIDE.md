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

## Journal Club

Journal Club publishes edited, public-ready research interpretations. Zotero remains the place for original papers, annotations, full reading records and private research ideas. There is no Zotero synchronization or automatic PDF extraction. The directory shows a short introduction; the detail page keeps the full article without a word limit or automatic body truncation.

### Source files and permanent URLs

Maintain Markdown and attachments, then let the existing build produce HTML:

```text
journal-club/
  posts/YYYY-MM-DD-paper-name.md       # Metadata and public interpretation
  assets/paper-slug/model-overview.png # Permanent source image
  assets/paper-slug/reading-notes.pdf  # Your public-ready PDF interpretation
  assets/paper-slug/slides.pdf         # Optional supplementary material
  templates/article.md               # Copyable draft templates, never published
  templates/pdf-first.md
  templates/hybrid.md
  articles/<slug>/index.html          # Generated output; never edit by hand
```

The previous `posts/TEMPLATE.md` is replaced by the three files under `templates/`. Templates are outside the published post input directory and start with `draft: true`. Their titles, authors, dates, categories and paths are explicit placeholders, not paper records. Replace them before publication; no sample image or PDF is supplied.

Existing article URL behavior is preserved: an explicit `slug` takes precedence; otherwise the Markdown filename without `.md` is normalized to a lowercase, hyphenated slug. A filename beginning with a date keeps that date in the default slug. Do not rename a published file or change its slug unless you also arrange a redirect. The final URL is `/journal-club/articles/<slug>/`.

`assets/` holds permanent sources and is preserved by repeated builds. `articles/` is generated and may be cleaned when rebuilding. Never store images, PDFs or other source material under `articles/`.

### Choose a publication mode

| `content_mode` | What the detail page shows | Main PDF |
| --- | --- | --- |
| `article` | Complete Markdown interpretation, including images | Optional; shown as a resource link without automatic embedding |
| `pdf-first` | Paper metadata, classification and a meaningful introduction, followed by a same-origin PDF reading area | Required |
| `hybrid` | Complete Markdown interpretation, with the PDF preview in an expandable area after the body | Required |

A missing `content_mode` defaults to `article` for existing posts. These are display modes, not research categories. A main PDF in `pdf-first` or `hybrid` must be valid; the build reports a missing or invalid PDF instead of publishing an empty reader.

A separate **Open PDF** link is always available when a main PDF is supplied, including when its preview is collapsed or unsupported. Local PDFs also have a download link. Embedding is limited to same-origin files; an external PDF gets a direct link because third-party sites may forbid embedding. Mobile browsers handle PDF viewers differently, so the independent open link remains the reliable fallback. The renderer manages the preview; do not handwrite an iframe.

### Choose one category and add cross-cutting topics

Use exactly one `category` slug. The directory provides **All** and the six categories in this order:

| `category` | Display name |
| --- | --- |
| `development-virtual-embryos` | Development & Virtual Embryos |
| `virtual-cells` | Virtual Cells |
| `spatial-biology-virtual-tissues` | Spatial Biology & Virtual Tissues |
| `biological-foundation-models` | Biological Foundation Models |
| `algorithms-theory` | Algorithms & Theory |
| `data-benchmarks` | Data & Benchmarks |

Use `topics` for cross-cutting tags such as `single-cell`, `spatial`, `flow-matching` and `human`. Species, algorithms and file formats are not additional main categories. For example:

```yaml
category: development-virtual-embryos
topics: [single-cell, human, flow-matching]
```

For legacy posts without `category`, the builder can recognize one of these category names or slugs in `topics`. If there is no reliable single match, the post stays visible in **All** with a category-needed notice; no seventh research category is created. Fill in `category` when maintaining that post. New templates deliberately require you to choose a category.

### Metadata reference

| Field | Meaning |
| --- | --- |
| `title` | Full, verified paper title; required for a published post |
| `short_title` | Optional concise directory title; falls back to `title` |
| `date` | Journal Club publication date, quoted as `"YYYY-MM-DD"`; required |
| `authors` | Original paper authors as a string |
| `journal` | Original journal or preprint server |
| `year` | Original paper publication year; distinct from the Journal Club date |
| `doi` | Original paper DOI, when available |
| `paper_url` | Link to the original source page, preferably the publisher, DOI or preprint landing page |
| `status` | Optional original-paper version or publication status |
| `slug` | Optional stable article URL identifier; keep unchanged after publication |
| `category` | Exactly one of the six research category slugs |
| `topics` | List of cross-cutting tags |
| `summary` | One or two meaningful sentences for the directory; does not replace the full Abstract |
| `content_mode` | `article`, `pdf-first` or `hybrid`; omitted means `article` |
| `pdf_url` | Main public-ready PDF interpretation; required in `pdf-first` and `hybrid` |
| `pdf_label` | Optional main PDF link text, such as `Open reading notes PDF` |
| `attachments` | Optional list of objects containing `title` and `url` |
| `draft` | YAML boolean: `true` excludes the post from generated pages and the directory |

Empty optional fields do not produce empty buttons; duplicate resource URLs are shown once. If an older article lacks `summary`, the builder does not manufacture one from formulas, raw HTML or arbitrary body fragments. Add a meaningful summary when convenient. A PDF-first post should have a useful summary and introduction so readers can judge the topic before opening the PDF.

This is a path example, not an existing paper or attachment:

```yaml
pdf_url: "/journal-club/assets/paper-slug/reading-notes.pdf"
pdf_label: "Open reading notes PDF"
attachments:
  - title: "Discussion slides"
    url: "/journal-club/assets/paper-slug/slides.pdf"
```

Replace `paper-slug` and upload the named files before using this example in a published post. Omit unused fields or use `pdf_url: ""` and `attachments: []`. Do not leave placeholder links in a published article.

### Publish a complete illustrated interpretation

1. Copy `journal-club/templates/article.md` to `journal-club/posts/YYYY-MM-DD-paper-name.md`.
2. Keep `draft: true` while replacing the metadata and writing the interpretation. Choose one category and use topics for cross-cutting tags.
3. Write the six sections: **Title**, **Abstract**, **Main**, **Methods Highlights**, **Results** and **Novelty**. The template provides prompts for study context, datasets, model inputs and outputs, methodological assumptions, validation, quantitative evidence, innovation and limitations. Under Title, add useful version/resource details without repeating the page header.
4. Upload only public-ready images to `journal-club/assets/<paper-slug>/`. Add alt text, captions and source attribution as appropriate.
5. Replace the directory `summary` with a brief guide to the reading. It is independent of the full Abstract, and the article body is not clipped.
6. Follow the build and publication checks below, then set `draft: false` and commit the Markdown and its assets together. Routine publishing never requires edits to generated HTML.

### Publish your own PDF interpretation

1. Copy `templates/pdf-first.md` into `posts/` using a stable filename.
2. Export a public-ready version of your interpretation to PDF. Remove private annotations, unpublished plans and material you do not intend to share before placing it in the repository.
3. Upload it to `journal-club/assets/<paper-slug>/reading-notes.pdf` and set `pdf_url` to `/journal-club/assets/<paper-slug>/reading-notes.pdf`.
4. Fill in the actual title, authors, source link, year, Journal Club date, category and tags. Supply a meaningful directory summary and an introduction describing the paper and what the PDF covers. Do not infer metadata from the filename or duplicate the full PDF as Markdown.
5. Add optional supplementary files in `attachments`, verify the build, and switch `draft` to `false` when ready.

For a complete web article plus PDF, start with `templates/hybrid.md`. Write the same six complete sections as an article and supply the main PDF. The Markdown stays intact, and the PDF preview appears after it in an expandable area.

### Images, captions and original files

Standard Markdown is supported. Use descriptive alt text and an optional image title, which becomes a visible caption:

```markdown
![Describe the model components and their connections](/journal-club/assets/paper-slug/model-overview.png "Explain what the diagram shows; include its source figure and attribution when required.")
```

The image links to the original file, stays within the article width and retains its proportions. Do not use fixed image heights or CSS that crops a scientific panel. Keep captions about the content; alt text should help a reader understand what is pictured.

Existing HTML figures and captions remain supported:

```html
<figure>
  <img src="/journal-club/assets/paper-slug/key-results.png"
       alt="Describe the plotted comparison and the principal trend">
  <figcaption>Explain the result and conditions. Cite the source Figure/Table and attribution where required.</figcaption>
</figure>
```

The renderer preserves the caption and provides original-image access. Prefer source links or figures you made yourself; this workflow does not fetch publisher figures or download original-paper PDFs. When supplying third-party material, confirm the applicable license and attribution requirements yourself.

### Safe paths and other rich content

Use site-root-relative asset paths beginning with `/journal-club/assets/`. These work from the nested final article URL. Do not use computer paths such as `/Users/...`, `C:\\...` or `file:`, a GitHub `blob` viewer URL, or a path that works only relative to a Markdown file in `posts/`. Local paths are case-sensitive on the deployed site; prefer simple lowercase filenames with hyphens.

The builder checks local referenced files and verifies that a main PDF is a real PDF, not merely an HTML response or a renamed non-PDF file. Metadata resource links reject unsuitable protocols such as `javascript:` and `file:`. For external links, use `https://` and check the actual destination yourself: a `.pdf` suffix alone does not prove that a URL serves a PDF.

Existing MathJax, tables, fenced code blocks and inline HTML remain available. Use `\( ... \)` for inline formulas and `\[ ... \]` for display formulas. Code fences preserve their content, and tables use standard Markdown syntax. Keep user-facing prose and metadata in English.

### Drafts and privacy

Use a YAML boolean, `draft: true` or `draft: false`. Drafts are not listed and do not receive generated detail pages. Changing a previously published post to a draft removes its generated entry on the next build.

**Draft is not access control.** In a public GitHub repository, committed Markdown, images and PDFs may be directly accessible even if the article is a draft or is absent from the directory. Keep private Zotero annotations, personal reading records and unpublished plans outside this repository. Removing a file from a later commit does not erase repository history.

### Build, check and publish

From the repository root, install the renderer dependencies and run the builder:

```bash
python -m pip install -r scripts/requirements-journal-club.txt
python -m unittest discover -s tests -v
python scripts/build_journal_club.py
```

The builder reads `posts/*.md`, excludes drafts, validates publishable inputs, generates `articles/<slug>/index.html` and updates the Journal Club directory. Templates are not post inputs. Publication dates are ordered newest first. Do not hand-edit generated cards or article HTML; the next build will replace those edits.

To inspect the same complete static artifact used for deployment, optionally run `python scripts/stage_pages.py /tmp/jc-pages-preview`. This staging step includes images and PDFs from `assets/`.

For a local check, serve the repository root so root-relative assets resolve correctly:

```bash
python -m http.server 8000
```

Open `http://localhost:8000/journal-club/` and then the article. Confirm the category filter, full body, original-image links, desktop/mobile layout, and the independent PDF link. Open the PDF directly as well as testing the preview. An unsupported embedded viewer must not prevent access through the direct link.

Commit the Markdown and assets together using the repository's normal branch process. The **Publish Journal Club** workflow handles source updates, tests and builds the pages, commits generated HTML when needed, stages the complete static site including `assets/`, and explicitly deploys that artifact to GitHub Pages. Check the workflow deployment before assuming the update is live. This explicit deployment does not depend on a generated commit by `GITHUB_TOKEN` triggering another Pages build. Style, renderer and attachment changes are also covered by the publishing flow. Generated article files are excluded from source triggers; generated commits use `GITHUB_TOKEN`, which does not trigger another workflow run. To correct content later, edit the source Markdown or replace the intended asset, then use the same process.

### Troubleshoot publication

| Symptom | What to check |
| --- | --- |
| Build reports a missing attachment | Read the source Markdown filename and path in the error. Verify the exact case and filename, upload the file under `assets/`, and use the final site path. |
| PDF-first or hybrid fails validation | Supply `pdf_url`, confirm the file exists and is a real PDF, and replace all template placeholders. A main PDF cannot be empty in these modes. |
| Link opens a GitHub/HTML page | Use `/journal-club/assets/.../file.pdf` for a committed local PDF rather than a GitHub `blob` URL or download landing page. |
| PDF preview is blank on a phone | Use the visible Open PDF link. Browser support varies; external PDFs are deliberately link-only. |
| Post is absent | Check `draft`, the `posts/*.md` location, YAML syntax, build errors and workflow status. Files in `templates/` are never published. |
| Post appears only in All | Fill in one valid `category`. Missing, unknown or ambiguous legacy categories produce a warning and remain in All instead of being guessed into a category. Supplying multiple main categories is an error. |
| Card has no introduction | Supply `summary`. The builder does not automatically extract a fragment from the article body. |
| Old URL stopped working | Restore the old filename/slug, or add an intentional redirect if a URL change was necessary. |
| Local images fail but Markdown preview works | Serve the repository root; do not open HTML directly with `file://`. Verify the root-relative asset path. |
| A change is still missing online | Check the publishing workflow and Pages deployment, then reload the live page. A successful local build alone is not proof of deployment. |

Fix the source problem, rerun the build and republish. Do not repair missing attachments by placing files inside the generated `articles/` tree.
