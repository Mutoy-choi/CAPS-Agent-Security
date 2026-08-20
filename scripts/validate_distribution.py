#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESERVED_MARKETPLACES = {
    "claude-code-marketplace",
    "claude-code-plugins",
    "claude-plugins-official",
    "claude-plugins-community",
    "agent-skills",
    "anthropic-agent-skills",
}


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
    assert market["name"] not in RESERVED_MARKETPLACES
    assert market["plugins"]
    for plugin in market["plugins"]:
        source = plugin["source"]
        assert isinstance(source, str) and source.startswith("./")
        assert (ROOT / source).is_dir()
        assert plugin.get("description")
        assert plugin.get("tags")

    site_market = load_json("site/marketplace.json")
    assert site_market["name"] == market["name"]
    source = site_market["plugins"][0]["source"]
    assert source["source"] == "git-subdir"
    assert source["path"] == "plugins/caps-security"


def validate_plugin() -> None:
    plugin = load_json("plugins/caps-security/.claude-plugin/plugin.json")
    assert plugin["name"] == "caps-security"
    assert plugin["version"] == "0.6.0"
    assert plugin["skills"] == ["./skills"]
    for skill in (ROOT / "plugins/caps-security/skills").glob("*/SKILL.md"):
        validate_skill(skill)


def validate_skill(path: Path) -> None:
    fields = frontmatter(path)
    expected = path.parent.name
    assert fields.get("name") == expected, f"Skill name mismatch: {path}"
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", expected)
    description = fields.get("description", "")
    assert 20 <= len(description) <= 1024, f"Invalid description: {path}"
    assert len(path.read_text(encoding="utf-8").splitlines()) < 500


def validate_cross_client_skills() -> None:
    skills = sorted((ROOT / ".agents/skills").glob("*/SKILL.md"))
    assert {path.parent.name for path in skills} == {"caps-agent-security", "caps-install"}
    for skill in skills:
        validate_skill(skill)


def validate_site() -> None:
    index = (ROOT / "site/index.html").read_text(encoding="utf-8")
    assert '<link rel="canonical" href="https://mutoy-choi.github.io/ChillMCP/">' in index
    assert "noindex" not in index.lower()
    assert "SoftwareApplication" in index

    skills_page = (ROOT / "site/skills/index.html").read_text(encoding="utf-8")
    assert "CollectionPage" in skills_page
    assert "caps-agent-security" in skills_page and "caps-install" in skills_page

    sitemap = (ROOT / "site/sitemap.xml").read_text(encoding="utf-8")
    for url in (
        "https://mutoy-choi.github.io/ChillMCP/",
        "https://mutoy-choi.github.io/ChillMCP/plugin/",
        "https://mutoy-choi.github.io/ChillMCP/skills/",
        "https://mutoy-choi.github.io/ChillMCP/skills/caps-agent-security/",
        "https://mutoy-choi.github.io/ChillMCP/skills/caps-install/",
    ):
        assert url in sitemap

    skills = load_json("site/skills.json")
    assert len(skills["skills"]) == 2
    assert (ROOT / "site/llms-full.txt").is_file()
    security = (ROOT / "site/.well-known/security.txt").read_text(encoding="utf-8")
    assert "Canonical: https://mutoy-choi.github.io/ChillMCP/.well-known/security.txt" in security
    assert (ROOT / "install.sh").read_bytes() == (ROOT / "site/install.sh").read_bytes()


def main() -> int:
    validate_marketplace()
    validate_plugin()
    validate_cross_client_skills()
    validate_site()
    print("CAPS distribution metadata is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
