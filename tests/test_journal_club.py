"""Publishing regressions using temporary, explicitly fictitious fixtures only.

Run with: python -m unittest discover -s tests -v
No example paper, private material, or test attachment is written to the site.
"""

from __future__ import annotations

import base64
import contextlib
import importlib.util
import io
import re
import tempfile
import unittest
import warnings
from html.parser import HTMLParser
from pathlib import Path

import yaml


REPOSITORY = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "journal_club_builder", REPOSITORY / "scripts" / "build_journal_club.py"
)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
stage_spec = importlib.util.spec_from_file_location(
    "journal_club_pages_stager", REPOSITORY / "scripts" / "stage_pages.py"
)
stager = importlib.util.module_from_spec(stage_spec)
stage_spec.loader.exec_module(stager)

CATEGORIES = (
    ("development-virtual-embryos", "Development & Virtual Embryos"),
    ("virtual-cells", "Virtual Cells"),
    ("spatial-biology-virtual-tissues", "Spatial Biology & Virtual Tissues"),
    ("biological-foundation-models", "Biological Foundation Models"),
    ("algorithms-theory", "Algorithms & Theory"),
    ("data-benchmarks", "Data & Benchmarks"),
)


class Document(HTMLParser):
    """Small semantic HTML tree; deliberately independent of CSS formatting."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = {"tag": "document", "attrs": {}, "children": [], "parent": None}
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "children": [], "parent": self.stack[-1]}
        self.stack[-1]["children"].append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i]["tag"] == tag:
                self.stack = self.stack[:i]
                return

    def handle_data(self, data):
        self.stack[-1]["children"].append(data)

    @staticmethod
    def text(node):
        if isinstance(node, str):
            return node
        return "".join(Document.text(child) for child in node["children"])

    def elements(self, tag=None, attr=None, value=None, node=None):
        result = []
        for child in (node or self.root)["children"]:
            if isinstance(child, str):
                continue
            if (tag is None or child["tag"] == tag) and (
                attr is None or attr in child["attrs"] and (value is None or child["attrs"][attr] == value)
            ):
                result.append(child)
            result.extend(self.elements(tag, attr, value, child))
        return result


def small_pdf():
    """A real one-page blank PDF, constructed locally without a PDF dependency."""
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>",
        b"<< /Length 0 >>\nstream\n\nendstream",
    ]
    result = b"%PDF-1.4\n"
    offsets = [0]
    for i, content in enumerate(objects, 1):
        offsets.append(len(result))
        result += f"{i} 0 obj\n".encode() + content + b"\nendobj\n"
    xref = len(result)
    result += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    result += b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:])
    return result + f"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()


class JournalClubBuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="jc-publishing-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.club = self.root / "journal-club"
        self.posts = self.club / "posts"
        self.posts.mkdir(parents=True)
        self.index = self.club / "index.html"
        self.index.write_text((REPOSITORY / "journal-club" / "index.html").read_text(encoding="utf-8"), encoding="utf-8")

    def post(self, name="2026-09-07-test-paper", body="## Abstract\n\nFictitious test interpretation.", **overrides):
        metadata = {"title": "Fictitious fixture paper", "date": "2026-09-07", "category": "virtual-cells"}
        metadata.update(overrides)
        path = self.posts / f"{name}.md"
        path.write_text("---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---\n" + body + "\n", encoding="utf-8")
        return path

    def asset(self, name="notes.pdf", content=None):
        path = self.club / "assets" / "fixture-paper" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(small_pdf() if content is None else content)
        return "/" + path.relative_to(self.root).as_posix()

    def image(self):
        return self.asset("figure.png", base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jh4kAAAAASUVORK5CYII="))

    def build(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output), warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            builder.build(self.root)
        return output.getvalue() + "\n" + "\n".join(str(item.message) for item in caught)

    def article(self, slug="2026-09-07-test-paper"):
        return (self.club / "articles" / slug / "index.html").read_text(encoding="utf-8")

    def cards(self):
        return Document(self.index.read_text(encoding="utf-8")).elements("article", "data-jc-card")

    def assert_invalid(self, source, *fragments):
        with self.assertRaises(ValueError) as raised:
            self.build()
        message = str(raised.exception)
        self.assertIn(source.name, message)
        for fragment in fragments:
            self.assertIn(fragment, message)
        return message

    def test_legacy_default_mode_slug_url_and_rich_markdown(self):
        body = r"""# Fictitious fixture paper

## Abstract

Inline \(x < y \land a & b\), and block math:

\[x_i = \begin{cases}a & x < 0\\b & x \geq 0\end{cases}\]

| Data | Value |
| --- | --- |
| Cells | 12 |

```python
if x < 3:
    print("a & b")
```

<span class="legacy-inline">Preserved inline HTML</span>
"""
        self.post(body=body, category=None, slug="Stable legacy_URL", authors="Fixture A & Fixture B", journal="Fixture Journal", year=2020)
        self.build()
        source = self.article("stable-legacy-url")
        document = Document(source)
        self.assertEqual(len(document.elements("h1")), 1)
        self.assertTrue(document.elements("table"))
        self.assertTrue(document.elements("pre"))
        self.assertTrue(document.elements("span", "class", "legacy-inline"))
        self.assertIn(r"\(x < y \land a & b\)", document.text(document.root))
        self.assertIn(r"\[x_i = \begin{cases}a & x < 0\\b & x \geq 0\end{cases}\]", document.text(document.root))
        self.assertTrue(any("mathjax" in node["attrs"].get("src", "").lower() for node in document.elements("script")))
        self.assertIn("/journal-club/articles/stable-legacy-url/", self.index.read_text())
        self.assertFalse(document.elements("iframe"))

    def test_date_is_publication_date_and_year_is_paper_year(self):
        self.post(year=1999, journal="Fixture Journal")
        self.post("newer", date="2026-09-08", year=1980)
        self.build()
        document = Document(self.article())
        text = document.text(document.root)
        self.assertIn("2026-09-07", text)
        self.assertIn("1999", text)
        self.assertLess(self.index.read_text().index("/articles/newer/"), self.index.read_text().index("/articles/2026-09-07-test-paper/"))

    def test_six_categories_order_and_legacy_topics_fallback(self):
        for number, (slug, label) in enumerate(CATEGORIES):
            self.post(f"category-{number}", category=slug, topics=["human", "single-cell"])
        self.post("legacy-label", category=None, topics=["human", "Algorithms & Theory"])
        self.post("legacy-slug", category=None, topics=["human", "virtual-cells"])
        self.post("unclassified", category=None, topics=["human"])
        self.post("ambiguous", category=None, topics=["virtual-cells", "data-benchmarks"])
        diagnostic = self.build()
        doc = Document(self.index.read_text())
        buttons = doc.elements("button", "data-jc-filter")
        self.assertEqual([node["attrs"]["data-jc-filter"] for node in buttons], ["all"] + [item[0] for item in CATEGORIES])
        by_slug = {re.search(r"/articles/([^/]+)/", next(node for node in doc.elements("a", node=card) if "/articles/" in node["attrs"].get("href", ""))["attrs"]["href"]).group(1): card for card in self.cards()}
        self.assertEqual(len(by_slug), 10)
        for number, (slug, _) in enumerate(CATEGORIES):
            self.assertEqual(by_slug[f"category-{number}"]["attrs"].get("data-category"), slug)
        self.assertEqual(by_slug["legacy-label"]["attrs"].get("data-category"), "algorithms-theory")
        self.assertEqual(by_slug["legacy-slug"]["attrs"].get("data-category"), "virtual-cells")
        for slug in ("unclassified", "ambiguous"):
            self.assertNotIn(by_slug[slug]["attrs"].get("data-category"), dict(CATEGORIES))
            self.assertRegex(diagnostic + Document.text(by_slug[slug]), r"(?i)(category|classif)")

    def test_explicit_category_wins_over_cross_tags(self):
        self.post(category="data-benchmarks", topics=["virtual-cells", "human", "flow-matching"])
        self.build()
        self.assertEqual(self.cards()[0]["attrs"].get("data-category"), "data-benchmarks")
        self.assertIn("flow-matching", Document.text(self.cards()[0]))

    def test_unknown_legacy_category_remains_in_all_with_warning(self):
        source = self.post(category="Legacy research topic", topics=["human"])
        diagnostic = self.build()
        self.assertEqual(len(self.cards()), 1)
        self.assertNotIn(self.cards()[0]["attrs"].get("data-category"), dict(CATEGORIES))
        self.assertIn(source.name, diagnostic)
        self.assertRegex(diagnostic, r"(?i)(category|classif)")
        self.assertTrue((self.club / "articles/2026-09-07-test-paper/index.html").is_file())

    def test_multiple_main_categories_are_rejected(self):
        source = self.post(category=["virtual-cells", "data-benchmarks"])
        self.assert_invalid(source, "category")

    def test_summary_is_card_only_and_long_body_is_complete(self):
        body = "## Abstract\n\n" + "Long body evidence. " * 350 + "\n\nFINAL_EVIDENCE_MARKER"
        self.post(body=body, summary="A concise, meaningful fixture introduction.")
        self.build()
        self.assertIn("A concise, meaningful fixture introduction.", self.index.read_text())
        self.assertNotIn("Long body evidence.", self.index.read_text())
        self.assertIn("FINAL_EVIDENCE_MARKER", self.article())
        self.assertEqual(self.article().count("Long body evidence."), 350)

    def test_absent_summary_does_not_extract_math_html_or_body(self):
        self.post(body=r"## Abstract\n\n\(DO_NOT_EXTRACT = x\) <strong>BODY_ONLY</strong>")
        self.build()
        self.assertNotIn("DO_NOT_EXTRACT", self.index.read_text())
        self.assertNotIn("BODY_ONLY", self.index.read_text())
        self.assertIn("BODY_ONLY", self.article())

    def test_three_modes_with_independent_pdf_entry_and_complete_hybrid_body(self):
        url = self.asset()
        for mode in ("article", "pdf-first", "hybrid"):
            self.post(mode, body="## Results\n\nCOMPLETE_BODY_" + mode, content_mode=mode, pdf_url=url, summary="Fixture PDF guide.")
        self.build()
        for mode in ("article", "pdf-first", "hybrid"):
            document = Document(self.article(mode))
            self.assertTrue(document.elements("a", "href", url), mode)
            if mode == "article":
                self.assertFalse(document.elements("iframe"))
            else:
                frames = document.elements("iframe")
                self.assertEqual(len(frames), 1)
                self.assertTrue(frames[0]["attrs"].get("title"))
                self.assertIn(url, (frames[0]["attrs"].get("src"), frames[0]["attrs"].get("data-src")))
                self.assertEqual(frames[0]["attrs"].get("loading"), "lazy")
            if mode == "hybrid":
                self.assertIn("COMPLETE_BODY_hybrid", self.article(mode))
                frame = document.elements("iframe")[0]
                ancestors = []
                parent = frame["parent"]
                while parent is not None:
                    ancestors.append(parent)
                    parent = parent["parent"]
                collapsed = any(node["tag"] == "details" and "open" not in node["attrs"] for node in ancestors)
                self.assertTrue(collapsed or self.article(mode).index("COMPLETE_BODY_hybrid") < self.article(mode).index("<iframe"))
        self.assertEqual(len(self.cards()), 3)
        self.assertIn("Fixture PDF guide.", self.index.read_text())

    def test_same_origin_absolute_pdf_is_validated_and_external_is_link_only(self):
        local = self.asset()
        self.post("same-origin", content_mode="pdf-first", pdf_url="https://bio-jasperoa.github.io" + local, summary="A fixture guide.")
        external = "https://example.org/public-notes.pdf"
        self.post("external", content_mode="hybrid", pdf_url=external, summary="A fixture guide.")
        self.build()
        self.assertTrue(Document(self.article("same-origin")).elements("iframe"))
        outside = Document(self.article("external"))
        self.assertTrue(outside.elements("a", "href", external))
        self.assertFalse(outside.elements("iframe"))

    def test_pdf_modes_require_pdf(self):
        for mode in ("pdf-first", "hybrid"):
            with self.subTest(mode=mode):
                self.posts.joinpath("2026-09-07-test-paper.md").unlink(missing_ok=True)
                source = self.post(content_mode=mode, pdf_url="", summary="Fixture guide.")
                self.assert_invalid(source, "pdf_url")

    def test_pdf_first_requires_meaningful_introduction(self):
        source = self.post(content_mode="pdf-first", pdf_url=self.asset(), summary="   ", body="")
        self.assert_invalid(source, "summary")

    def test_pdf_cannot_be_only_fragment_anchor(self):
        source = self.post(content_mode="pdf-first", pdf_url="#page=1", summary="Fixture guide.")
        self.assert_invalid(source, "#page=1")

    def test_relative_resources_resolve_from_final_article_url(self):
        self.asset()
        self.image()
        self.post(content_mode="hybrid", pdf_url="../../assets/fixture-paper/notes.pdf", body="![Fixture](../../assets/fixture-paper/figure.png)")
        self.build()
        doc = Document(self.article())
        self.assertTrue(doc.elements("a", "href", "/journal-club/assets/fixture-paper/notes.pdf"))
        self.assertTrue(doc.elements("img", "src", "/journal-club/assets/fixture-paper/figure.png"))

    def test_missing_pdf_and_html_disguised_as_pdf_report_source_and_path(self):
        source = self.post(content_mode="pdf-first", pdf_url="/journal-club/assets/missing.pdf", summary="Fixture guide.")
        self.assert_invalid(source, "/journal-club/assets/missing.pdf")
        disguised = self.asset("wrong.pdf", b"<!doctype html><html><body>Not a PDF</body></html>")
        source = self.post(content_mode="hybrid", pdf_url=disguised)
        self.assert_invalid(source, "wrong.pdf")

    def test_same_origin_absolute_missing_file_is_not_treated_as_external(self):
        url = "https://bio-jasperoa.github.io/journal-club/assets/absent.pdf"
        source = self.post(content_mode="pdf-first", pdf_url=url, summary="Fixture guide.")
        self.assert_invalid(source, "absent.pdf")

    def test_unsafe_resource_protocols_are_rejected(self):
        for field in ("paper_url", "pdf_url", "attachments"):
            for url in ("javascript:alert(1)", "file:///private/notes.pdf", "data:text/html,fixture"):
                with self.subTest(field=field, url=url):
                    value = [{"title": "Fixture attachment", "url": url}] if field == "attachments" else url
                    source = self.post(**{field: value})
                    self.assert_invalid(source, url)

    def test_missing_local_image_and_attachment_are_reported(self):
        source = self.post(body="![Missing image](/journal-club/assets/missing-image.png)")
        self.assert_invalid(source, "missing-image.png")
        source = self.post(attachments=[{"title": "Missing notes", "url": "/journal-club/assets/missing-notes.pdf"}])
        self.assert_invalid(source, "missing-notes.pdf")

    def test_empty_fields_no_empty_buttons_and_duplicate_resources_deduplicated(self):
        url = self.asset()
        self.post(pdf_url=url, pdf_label="", paper_url="", doi="", attachments=[
            {"title": "The same main PDF", "url": url},
            {"title": "", "url": ""},
            {"title": "External supplement", "url": "https://example.org/supplement"},
            {"title": "Repeated supplement", "url": "https://example.org/supplement"},
        ])
        self.build()
        document = Document(self.article())
        for anchor in document.elements("a"):
            self.assertTrue(anchor["attrs"].get("href", "").strip())
            self.assertTrue(document.text(anchor).strip() or document.elements("img", node=anchor))
        ordinary_pdf_links = [item for item in document.elements("a", "href", url) if "download" not in item["attrs"]]
        self.assertEqual(len(ordinary_pdf_links), 1)
        self.assertEqual(len(document.elements("a", "href", "https://example.org/supplement")), 1)

    def test_markdown_image_caption_and_legacy_figure_open_original(self):
        url = self.image()
        body = f'''![Detailed fixture alternative text]({url} "A fixture caption")

<figure><img src="{url}" alt="Legacy image"><figcaption>Legacy figure caption.</figcaption></figure>
'''
        self.post(body=body)
        self.build()
        document = Document(self.article())
        images = document.elements("img", "src", url)
        self.assertEqual(len(images), 2)
        self.assertEqual(images[0]["attrs"]["alt"], "Detailed fixture alternative text")
        captions = [document.text(item) for item in document.elements("figcaption")]
        self.assertIn("A fixture caption", captions)
        self.assertIn("Legacy figure caption.", captions)
        for img in images:
            parent = img["parent"]
            while parent and parent["tag"] != "a":
                parent = parent["parent"]
            self.assertIsNotNone(parent, "Every content image should open its original")
            self.assertEqual(parent["attrs"].get("href"), url)

    def test_metadata_is_html_escaped(self):
        title = 'A <script id="metadata-attack">fixture</script> & "quoted" title'
        self.post(title=title, authors='Fixture <b>author</b>', summary='Guide <img src=x onerror="alert(1)">')
        self.build()
        document = Document(self.article())
        self.assertEqual(document.text(document.elements("h1")[0]), title)
        self.assertFalse(document.elements("script", "id", "metadata-attack"))
        self.assertFalse(Document(self.index.read_text()).elements("img", "onerror"))
        self.assertIn("Fixture <b>author</b>", document.text(document.root))

    def test_draft_never_generates_detail_and_removes_previously_published_detail(self):
        self.post()
        self.build()
        output = self.club / "articles" / "2026-09-07-test-paper" / "index.html"
        self.assertTrue(output.exists())
        self.post(draft=True, pdf_url="/journal-club/assets/private-placeholder.pdf")
        self.build()
        self.assertFalse(output.exists())
        self.assertNotIn("/articles/2026-09-07-test-paper/", self.index.read_text())
        self.assertFalse(self.cards())

    def test_repeated_build_preserves_assets_bytes_and_is_idempotent(self):
        pdf = self.asset()
        image = self.image()
        paths = [self.root / url.lstrip("/") for url in (pdf, image)]
        before = {path: path.read_bytes() for path in paths}
        self.post(content_mode="hybrid", pdf_url=pdf, body=f"![Fixture image]({image})")
        self.build()
        first = self.article(), self.index.read_text()
        self.build()
        self.assertEqual(first, (self.article(), self.index.read_text()))
        self.assertEqual(before, {path: path.read_bytes() for path in paths})

    def test_duplicate_slugs_fail_before_touching_published_output(self):
        self.post(slug="stable")
        self.build()
        output = self.article("stable")
        index = self.index.read_text()
        self.post("second", slug="stable")
        with self.assertRaises(ValueError) as raised:
            self.build()
        self.assertRegex(str(raised.exception), r"(?i)(duplicate|collision)")
        self.assertIn("stable", str(raised.exception))
        self.assertEqual(output, self.article("stable"))
        self.assertEqual(index, self.index.read_text())

    def test_legacy_non_html_assets_in_generated_directory_are_not_deleted(self):
        legacy = self.club / "articles" / "legacy" / "precious-notes.pdf"
        legacy.parent.mkdir(parents=True)
        legacy.write_bytes(small_pdf())
        expected = legacy.read_bytes()
        self.post()
        try:
            self.build()
        except ValueError as error:
            self.assertIn("precious-notes.pdf", str(error))
        self.assertTrue(legacy.exists())
        self.assertEqual(legacy.read_bytes(), expected)

    def test_pages_artifact_preserves_durable_assets_and_other_site_content(self):
        pdf = self.asset()
        image = self.image()
        self.post(content_mode="hybrid", pdf_url=pdf, body=f"![Fixture]({image})")
        self.build()
        unrelated = {"index.html": b"<html>Unrelated home page</html>", "blog/index.html": b"<html>Existing blog</html>", "styles.css": b"body { color: black; }", "assets/avatar.png": b"Unchanged site asset"}
        for relative, data in unrelated.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        for relative in (".git/config", "scripts/build.py", "tests/test.py", "journal-club/templates/article.md"):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Source-only fixture", encoding="utf-8")
        with tempfile.TemporaryDirectory(prefix="jc-deployment-test-") as folder:
            destination = Path(folder) / "pages"
            with contextlib.redirect_stdout(io.StringIO()):
                stager.stage(destination, root=self.root)
            for url in (pdf, image):
                relative = url.lstrip("/")
                self.assertEqual((destination / relative).read_bytes(), (self.root / relative).read_bytes())
            for relative, expected in unrelated.items():
                self.assertEqual((destination / relative).read_bytes(), expected)
            for relative in (".git", "scripts", "tests", "journal-club/templates", "journal-club/posts"):
                self.assertFalse((destination / relative).exists())
            self.assertTrue((destination / ".nojekyll").is_file())
            self.assertTrue((destination / "journal-club/articles/2026-09-07-test-paper/index.html").is_file())


if __name__ == "__main__":
    unittest.main()
