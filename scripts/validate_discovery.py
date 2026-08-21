#!/usr/bin/env python3
from __future__ import annotations

import json
import struct
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PAGES = "https://mutoy-choi.github.io/CAPS-Agent-Security/"
SOCIAL_CARD = f"{PAGES}assets/social-card.png"

LOCALES = {
    "en": ("", "en"),
    "ko": ("ko/", "ko"),
    "ja": ("ja/", "ja"),
    "zh-CN": ("zh-cn/", "zh-CN"),
    "es": ("es/", "es"),
}

PLATFORMS = (
    "ChatGPT",
    "Codex",
    "Claude Code",
    "Gemini CLI",
    "GitHub Copilot",
    "Cursor",
    "Cline",
    "Windsurf",
    "OpenCode",
    "MCP",
)


class HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang = ""
        self.title = ""
        self._in_title = False
        self.links: list[dict[str, str]] = []
        self.metas: list[dict[str, str]] = []
        self.scripts: list[dict[str, str]] = []
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_lang = values.get("lang", "")
        elif tag == "title":
            self._in_title = True
        elif tag == "link":
            self.links.append(values)
        elif tag == "meta":
            self.metas.append(values)
        elif tag == "script":
            self.scripts.append(values)
        elif tag == "a":
            self.hrefs.append(values.get("href", ""))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data


def locale_url(path: str) -> str:
    return f"{PAGES}{path}"


def get_meta(parser: HeadParser, *, name: str | None = None, prop: str | None = None) -> str:
    for meta in parser.metas:
        if name is not None and meta.get("name") == name:
            return meta.get("content", "")
        if prop is not None and meta.get("property") == prop:
            return meta.get("content", "")
    return ""


def get_link(parser: HeadParser, rel: str, **expected: str) -> str:
    for link in parser.links:
        rel_tokens = set(link.get("rel", "").split())
        if rel not in rel_tokens:
            continue
        if all(link.get(key) == value for key, value in expected.items()):
            return link.get("href", "")
    return ""


def read_png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"Not a PNG: {path}"
    assert data[12:16] == b"IHDR", f"Missing PNG IHDR: {path}"
    return struct.unpack(">II", data[16:24])


def validate_page(locale: str, path: str, html_lang: str) -> tuple[str, str]:
    file_path = SITE / path / "index.html" if path else SITE / "index.html"
    assert file_path.is_file(), f"Missing localized landing page: {file_path.relative_to(ROOT)}"
    text = file_path.read_text(encoding="utf-8")

    parser = HeadParser()
    parser.feed(text)

    canonical = locale_url(path)
    assert parser.html_lang == html_lang, f"Wrong html lang in {file_path}: {parser.html_lang}"
    assert parser.title and len(parser.title) >= 30, f"Title is too short: {file_path}"
    description = get_meta(parser, name="description")
    assert len(description) >= 100, f"Description is too short: {file_path}"
    assert get_link(parser, "canonical") == canonical, f"Wrong canonical: {file_path}"
    assert "index" in get_meta(parser, name="robots"), f"Landing page must be indexable: {file_path}"
    assert not get_meta(parser, name="keywords"), f"Do not use meta keywords: {file_path}"
    assert get_meta(parser, prop="og:url") == canonical, f"Wrong og:url: {file_path}"
    assert get_meta(parser, prop="og:image") == SOCIAL_CARD, f"Missing social image: {file_path}"
    assert get_meta(parser, name="twitter:card") == "summary_large_image"
    assert "SoftwareApplication" in text, f"Missing SoftwareApplication JSON-LD: {file_path}"
    assert "skip-link" in text and 'id="main-content"' in text
    assert "/CAPS-Agent-Security/llms.txt" in text

    expected_hreflang = {
        locale_code: locale_url(locale_path)
        for locale_code, (locale_path, _) in LOCALES.items()
    }
    expected_hreflang["x-default"] = PAGES
    actual_hreflang = {
        link.get("hreflang", ""): link.get("href", "")
        for link in parser.links
        if link.get("rel") == "alternate" and link.get("hreflang")
    }
    assert actual_hreflang == expected_hreflang, (
        f"Non-reciprocal hreflang set in {file_path}: {actual_hreflang}"
    )

    for platform in PLATFORMS:
        assert platform in text, f"Missing platform in {file_path}: {platform}"
    for locale_path, _ in LOCALES.values():
        assert f"/CAPS-Agent-Security/{locale_path}" in parser.hrefs, (
            f"Missing visible language link in {file_path}: {locale_path}"
        )

    return parser.title, description


def validate_sitemap() -> None:
    sitemap_path = SITE / "sitemap.xml"
    text = sitemap_path.read_text(encoding="utf-8")
    assert 'xmlns:xhtml="http://www.w3.org/1999/xhtml"' in text

    ns = {
        "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "xhtml": "http://www.w3.org/1999/xhtml",
    }
    root = ET.fromstring(text)
    rows: dict[str, dict[str, str]] = {}
    for url in root.findall("sm:url", ns):
        loc = url.findtext("sm:loc", namespaces=ns)
        assert loc
        alternates = {
            link.attrib["hreflang"]: link.attrib["href"]
            for link in url.findall("xhtml:link", ns)
        }
        rows[loc] = alternates

    expected = {
        locale_code: locale_url(locale_path)
        for locale_code, (locale_path, _) in LOCALES.items()
    }
    expected["x-default"] = PAGES
    for locale_path, _ in LOCALES.values():
        url = locale_url(locale_path)
        assert url in rows, f"Localized URL missing from sitemap: {url}"
        assert rows[url] == expected, f"Bad sitemap hreflang cluster: {url}"


def validate_machine_discovery() -> None:
    manifest = json.loads((SITE / "manifest.webmanifest").read_text(encoding="utf-8"))
    assert manifest["lang"] == "en"
    assert manifest["start_url"] == "/CAPS-Agent-Security/"
    assert manifest["scope"] == "/CAPS-Agent-Security/"
    assert "AI-agent security" in manifest["description"]

    robots = (SITE / "robots.txt").read_text(encoding="utf-8")
    assert "User-agent: *" in robots and "Allow: /" in robots
    assert f"Sitemap: {PAGES}sitemap.xml" in robots

    for name in ("llms.txt", "llms-full.txt"):
        text = (SITE / name).read_text(encoding="utf-8")
        for locale_path, _ in LOCALES.values():
            assert locale_url(locale_path) in text, f"{name} omits locale: {locale_path}"

    not_found = (SITE / "404.html").read_text(encoding="utf-8")
    assert 'content="noindex,follow"' in not_found
    for locale_path, _ in LOCALES.values():
        assert f"/CAPS-Agent-Security/{locale_path}" in not_found

    card = SITE / "assets/social-card.png"
    assert card.is_file() and card.stat().st_size > 5_000
    assert read_png_size(card) == (1200, 630)


def main() -> int:
    titles: set[str] = set()
    descriptions: set[str] = set()
    for locale, (path, html_lang) in LOCALES.items():
        title, description = validate_page(locale, path, html_lang)
        assert title not in titles, f"Duplicate localized title: {title}"
        assert description not in descriptions, f"Duplicate localized description: {description}"
        titles.add(title)
        descriptions.add(description)

    validate_sitemap()
    validate_machine_discovery()
    print("CAPS multilingual discovery site is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
