#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/Mutoy-choi/CAPS-Agent-Security"
ADVISORY_URL = f"{REPOSITORY}/security/advisories/new"

READMES = {
    "en": ROOT / "README.md",
    "ko": ROOT / "README.ko.md",
    "ja": ROOT / "README.ja.md",
    "zh-CN": ROOT / "README.zh-CN.md",
    "es": ROOT / "README.es.md",
}

LANGUAGE_LINKS = {
    "en": "README.md",
    "ko": "README.ko.md",
    "ja": "README.ja.md",
    "zh-CN": "README.zh-CN.md",
    "es": "README.es.md",
}

REQUIRED_SHARED_STRINGS = (
    "CAPS Unlock Lab",
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
    "PLATFORMS.md",
    "install.sh",
    "install.ps1",
    "caps-verify research doctor",
    "caps-verify research export",
    "SECURITY.md",
    REPOSITORY,
)

FORBIDDEN_STRINGS = (
    "github.com/Mutoy-choi/ChillMCP/security/advisories/new",
    "caps-security@caps-labs",
)


def read(path: Path) -> str:
    assert path.is_file(), f"Missing required file: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def assert_balanced_fences(path: Path, text: str) -> None:
    fence_lines = [line for line in text.splitlines() if line.lstrip().startswith("```")]
    assert len(fence_lines) % 2 == 0, f"Unbalanced code fences: {path.name}"


def assert_language_selector(path: Path, text: str) -> None:
    header = "\n".join(text.splitlines()[:35])
    for target in LANGUAGE_LINKS.values():
        if target == path.name:
            assert f"]({target})" not in header, (
                f"Current language should not link to itself in {path.name}: {target}"
            )
            continue
        assert f"]({target})" in header, f"Missing language link in {path.name}: {target}"


def assert_markdown_targets_exist(path: Path, text: str) -> None:
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        relative = target.split("#", 1)[0]
        if not relative:
            continue
        candidate = ROOT / relative
        assert candidate.exists(), f"Broken local link in {path.name}: {target}"


def validate_readmes() -> None:
    for locale, path in READMES.items():
        text = read(path)
        assert_language_selector(path, text)
        assert_balanced_fences(path, text)
        assert_markdown_targets_exist(path, text)
        for value in REQUIRED_SHARED_STRINGS:
            assert value in text, f"Missing shared value in {path.name}: {value}"
        for value in FORBIDDEN_STRINGS:
            assert value not in text, f"Forbidden legacy value in {path.name}: {value}"
        assert len(text.splitlines()) >= 200, f"Localized README is unexpectedly short: {locale}"


def validate_security_and_citation() -> None:
    security = read(ROOT / "SECURITY.md")
    assert ADVISORY_URL in security, "SECURITY.md must point to the CAPS advisory flow"
    assert "Mutoy-choi/ChillMCP" not in security, "SECURITY.md contains a legacy repository link"

    citation = read(ROOT / "CITATION.cff")
    assert "Restriction-Bypass" in citation, "CITATION.cff title capitalization is stale"
    assert "Restriction-BYpass" not in citation, "CITATION.cff contains the old typo"


def validate_translation_docs() -> None:
    guide = read(ROOT / "docs/TRANSLATIONS.md")
    contributing = read(ROOT / "CONTRIBUTING.md")
    for path in LANGUAGE_LINKS.values():
        assert f"`{path}`" in guide, f"Translation guide does not list {path}"
    assert "scripts/validate_readmes.py" in contributing


def main() -> int:
    validate_readmes()
    validate_security_and_citation()
    validate_translation_docs()
    print("CAPS multilingual README documentation is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
