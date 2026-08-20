#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = "https://mutoy-choi.github.io/CAPS-Agent-Security/"
REPOSITORY = "https://github.com/Mutoy-choi/CAPS-Agent-Security"


def load_json(path: str) -> dict:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"Expected JSON object: {path}")
    return value


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise AssertionError(f"Missing YAML frontmatter: {path}")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if line.startswith(" ") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields


def validate_marketplace() -> None:
    market = load_json(".claude-plugin/marketplace.json")
    assert market["name"] == "caps-labs"
    assert market["version"] == "0.7.0"
    for plugin in market["plugins"]:
        source = plugin["source"]
        assert isinstance(source, str) and source.startswith("./")
        assert (ROOT / source).is_dir()
        assert plugin["version"] == "0.7.0"
        assert plugin.get("description") and plugin.get("tags")

    site_market = load_json("site/marketplace.json")
    assert site_market["name"] == market["name"]
    source = site_market["plugins"][0]["source"]
    assert source["source"] == "git-subdir"
    assert source["url"] == f"{REPOSITORY}.git"
    assert source["path"] == "plugins/caps-security"


def validate_skill(path: Path) -> None:
    fields = frontmatter(path)
    expected = path.parent.name
    assert fields.get("name") == expected
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", expected)
    description = fields.get("description", "")
    assert 20 <= len(description) <= 1024
    assert len(path.read_text(encoding="utf-8").splitlines()) < 500


def validate_plugin_and_skills() -> None:
    plugin = load_json("plugins/caps-security/.claude-plugin/plugin.json")
    assert plugin["name"] == "caps-security"
    assert plugin["version"] == "0.7.0"
    assert plugin["skills"] == ["./skills"]
    for root in (ROOT / "plugins/caps-security/skills", ROOT / ".agents/skills"):
        skills = sorted(root.glob("*/SKILL.md"))
        assert {path.parent.name for path in skills} == {"caps-agent-security", "caps-install"}
        for path in skills:
            validate_skill(path)


def validate_site() -> None:
    index = (ROOT / "site/index.html").read_text(encoding="utf-8")
    assert f'<link rel="canonical" href="{PAGES}">' in index
    assert "skip-link" in index and "main-content" in index
    assert "SoftwareApplication" in index and "noindex" not in index.lower()

    styles = (ROOT / "site/assets/styles.css").read_text(encoding="utf-8")
    for requirement in (":focus-visible", "prefers-reduced-motion", "forced-colors"):
        assert requirement in styles

    sitemap = (ROOT / "site/sitemap.xml").read_text(encoding="utf-8")
    for path in ("", "plugin/", "skills/", "skills/caps-agent-security/", "skills/caps-install/", "accessibility/"):
        assert f"{PAGES}{path}" in sitemap

    skills = load_json("site/skills.json")
    assert len(skills["skills"]) == 2
    assert (ROOT / "site/llms-full.txt").is_file()
    assert (ROOT / "site/.well-known/security.txt").is_file()
    assert (ROOT / "install.sh").read_bytes() == (ROOT / "site/install.sh").read_bytes()


def validate_no_legacy() -> None:
    for path in (
        "AIDA.tar.gz",
        "main.py",
        "requirements.txt",
        "src",
        "test_delay.sh",
        "test_manual.md",
        "test_with_inspector.sh",
        "validate.py",
    ):
        assert not (ROOT / path).exists(), f"Legacy path must be removed: {path}"


def main() -> int:
    validate_marketplace()
    validate_plugin_and_skills()
    validate_site()
    validate_no_legacy()
    print("CAPS Unlock Lab distribution is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
