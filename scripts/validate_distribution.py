#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = "https://mutoy-choi.github.io/CAPS-Agent-Security/"
REPOSITORY = "https://github.com/Mutoy-choi/CAPS-Agent-Security"
VERSION = "0.8.0"
SKILLS = ("caps-agent-security", "caps-install")
RESEARCH_PROFILES = {"core", "adaptive", "reasoning", "multimodal", "full"}
RESEARCH_LIBRARIES = {"inspect-ai", "pyrit", "garak", "agentdojo"}


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


def validate_skill(path: Path) -> None:
    fields = frontmatter(path)
    expected = path.parent.name
    assert fields.get("name") == expected, f"Skill name mismatch: {path}"
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", expected)
    description = fields.get("description", "")
    assert 40 <= len(description) <= 1024, f"Invalid description: {path}"
    assert len(path.read_text(encoding="utf-8").splitlines()) < 500


def validate_canonical_skills() -> None:
    canonical = ROOT / "skills"
    assert {path.name for path in canonical.iterdir() if path.is_dir()} == set(SKILLS)
    for skill in SKILLS:
        skill_root = canonical / skill
        validate_skill(skill_root / "SKILL.md")
        assert (skill_root / "references/PLATFORMS.md").is_file()
        metadata = skill_root / "agents/openai.yaml"
        text = metadata.read_text(encoding="utf-8")
        for key in (
            "display_name:",
            "short_description:",
            "default_prompt:",
            "allow_implicit_invocation:",
        ):
            assert key in text


def assert_skill_copy(root: Path, *, require_openai: bool) -> None:
    for skill in SKILLS:
        canonical = ROOT / "skills" / skill
        target = root / skill
        assert target.is_dir(), f"Missing Skill copy: {target}"
        for relative in ("SKILL.md", "references/PLATFORMS.md"):
            assert (canonical / relative).read_bytes() == (target / relative).read_bytes(), (
                f"Skill copy drift: {target / relative}"
            )
        if require_openai:
            assert (canonical / "agents/openai.yaml").read_bytes() == (
                target / "agents/openai.yaml"
            ).read_bytes()


def validate_openai_package() -> None:
    root_manifest = load_json(".codex-plugin/plugin.json")
    bundled_manifest = load_json("plugins/caps-unlock/.codex-plugin/plugin.json")
    for manifest in (root_manifest, bundled_manifest):
        assert manifest["name"] in {"caps-unlock-lab", "caps-unlock"}
        assert manifest["version"] == VERSION
        assert manifest["skills"] == "./skills/"
        assert manifest.get("description")
    assert_skill_copy(ROOT / "plugins/caps-unlock/skills", require_openai=True)
    assert_skill_copy(ROOT / ".agents/skills", require_openai=True)


def validate_claude_package() -> None:
    marketplace = load_json(".claude-plugin/marketplace.json")
    assert marketplace["name"] == "caps-labs"
    assert marketplace["version"] == VERSION
    assert len(marketplace["plugins"]) == 1
    entry = marketplace["plugins"][0]
    assert entry["name"] == "caps-unlock"
    assert entry["source"] == "./plugins/caps-unlock"
    assert entry["version"] == VERSION

    plugin = load_json("plugins/caps-unlock/.claude-plugin/plugin.json")
    assert plugin["name"] == "caps-unlock"
    assert plugin["version"] == VERSION
    assert plugin["skills"] == ["./skills"]

    site_market = load_json("site/marketplace.json")
    site_entry = site_market["plugins"][0]
    assert site_market["version"] == VERSION
    assert site_entry["name"] == "caps-unlock"
    assert site_entry["source"]["url"] == f"{REPOSITORY}.git"
    assert site_entry["source"]["path"] == "plugins/caps-unlock"


def validate_gemini_package() -> None:
    manifest = load_json("gemini-extension.json")
    assert manifest["name"] == "caps-unlock-lab"
    assert manifest["version"] == VERSION
    assert manifest["contextFileName"] == "GEMINI.md"
    assert (ROOT / "GEMINI.md").is_file()
    for command in ("commands/caps/audit.toml", "commands/caps/install.toml"):
        value = tomllib.loads((ROOT / command).read_text(encoding="utf-8"))
        assert value.get("description") and value.get("prompt")


def validate_copilot_and_ide_adapters() -> None:
    assert_skill_copy(ROOT / ".github/skills", require_openai=False)
    agent = ROOT / ".github/agents/caps-unlock.md"
    fields = frontmatter(agent)
    assert fields.get("name") == "caps-unlock"
    assert fields.get("description")
    required = (
        ".github/copilot-instructions.md",
        ".cursor/rules/caps-unlock.mdc",
        ".cursor/mcp.json.example",
        ".clinerules/caps-unlock.md",
        ".clinerules/workflows/caps-unlock-audit.md",
        ".windsurf/rules/caps-unlock.md",
        ".windsurf/workflows/caps-unlock-audit.md",
        "AGENTS.md",
        ".codex/config.toml.example",
        "platforms/mcp/README.md",
        "platforms/mcp/stdio.example.json",
    )
    for path in required:
        assert (ROOT / path).is_file(), f"Missing platform adapter: {path}"


def validate_installers() -> None:
    assert (ROOT / "install.sh").read_bytes() == (ROOT / "site/install.sh").read_bytes()
    assert (ROOT / "install.ps1").read_bytes() == (ROOT / "site/install.ps1").read_bytes()
    shell = (ROOT / "install.sh").read_text(encoding="utf-8")
    powershell = (ROOT / "install.ps1").read_text(encoding="utf-8")
    for mode in (
        "codex",
        "chatgpt",
        "claude",
        "gemini",
        "copilot",
        "cursor",
        "cline",
        "windsurf",
        "opencode",
        "verify",
        "research",
        "research-all",
        "mcp",
        "chat",
    ):
        assert mode in shell and mode in powershell
    assert "gateway,mcp,research" in shell and "gateway,mcp,research" in powershell
    assert "research-all" in shell and "research-all" in powershell
    assert "$caps-agent-security" not in shell, "Escape the Codex $skill name in shell output"


def validate_research_integrations() -> None:
    pyproject = tomllib.loads((ROOT / "caps_verify/pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    assert project["version"] == VERSION
    extras = project["optional-dependencies"]
    for extra in (
        "inspect",
        "pyrit",
        "garak",
        "agentdojo",
        "multimodal",
        "research",
        "research-all",
    ):
        assert extra in extras and extras[extra], f"Missing optional extra: {extra}"
    entry_points = project["entry-points"]["inspect_ai"]
    assert entry_points["caps_verify"] == "caps_verify.integrations.inspect_registry"

    registry = load_json(
        "caps_verify/src/caps_verify/resources/research_registry.json"
    )
    profiles = load_json(
        "caps_verify/src/caps_verify/resources/research_profiles.json"
    )
    assert registry["schema_version"] == "caps.research.registry.v1"
    assert profiles["schema_version"] == "caps.research.profiles.v1"
    assert registry["policy"]["synthetic_canaries_only"] is True
    assert registry["policy"]["live_query_mutation"] is False
    assert registry["policy"]["real_side_effects"] is False
    assert registry["policy"]["raw_third_party_datasets_bundled"] is False
    assert {row["library_id"] for row in registry["libraries"]} == RESEARCH_LIBRARIES
    source_ids = {row["source_id"] for row in registry["sources"]}
    assert {
        "promptinject",
        "agentdojo",
        "mcptox",
        "fitd",
        "cot-hijacking",
        "figstep",
    }.issubset(source_ids)
    assert set(profiles["profiles"]) == RESEARCH_PROFILES
    assert len(profiles["profiles"]["core"]["probes"]) == 5
    assert set(profiles["profiles"]["full"]["extends"]) == {
        "adaptive",
        "reasoning",
        "multimodal",
    }
    probe_rows = profiles["probes"]
    assert len(probe_rows) == 9
    for probe_id, probe in probe_rows.items():
        assert probe["probe_id"] == probe_id
        assert probe["kind"] in {"benign", "attack"}
        assert probe["family"] and probe["strategy"]
        assert isinstance(probe.get("source_ids"), list)
        assert isinstance(probe.get("library_ids"), list)
        assert set(probe["source_ids"]).issubset(source_ids)
        assert set(probe["library_ids"]).issubset(RESEARCH_LIBRARIES)

    required = (
        "caps_verify/src/caps_verify/research.py",
        "caps_verify/src/caps_verify/integrations/__init__.py",
        "caps_verify/src/caps_verify/integrations/inspect_task.py",
        "caps_verify/src/caps_verify/integrations/inspect_registry.py",
        "caps_verify/docs/research-library-integrations.md",
        "caps_verify/tests/test_research.py",
        "caps_verify/tests/test_research_shadow.py",
    )
    for path in required:
        assert (ROOT / path).is_file(), f"Missing research integration: {path}"

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    runtime_readme = (ROOT / "caps_verify/README.md").read_text(encoding="utf-8")
    for value in (
        "Inspect AI",
        "PyRIT",
        "garak",
        "AgentDojo",
        "PromptInject",
        "MCPTox",
        "CoT-Hijacking",
        "FigStep",
        "caps-verify research doctor",
    ):
        assert value in readme or value in runtime_readme


def validate_site_and_discovery() -> None:
    index = (ROOT / "site/index.html").read_text(encoding="utf-8")
    assert f'<link rel="canonical" href="{PAGES}">' in index
    for platform in (
        "ChatGPT",
        "Codex",
        "Claude Code",
        "Gemini CLI",
        "GitHub Copilot",
        "Cursor",
        "Cline",
        "Windsurf",
        "OpenCode",
    ):
        assert platform in index
    assert "skip-link" in index and "main-content" in index
    assert "SoftwareApplication" in index and "noindex" not in index.lower()

    platforms_page = (ROOT / "site/platforms/index.html").read_text(encoding="utf-8")
    assert "Pick your host" in platforms_page
    assert "install.ps1" in platforms_page

    styles = (ROOT / "site/assets/styles.css").read_text(encoding="utf-8")
    for requirement in (":focus-visible", "prefers-reduced-motion", "forced-colors"):
        assert requirement in styles

    sitemap = (ROOT / "site/sitemap.xml").read_text(encoding="utf-8")
    for path in (
        "",
        "platforms/",
        "plugin/",
        "skills/",
        "skills/caps-agent-security/",
        "skills/caps-install/",
        "accessibility/",
    ):
        assert f"{PAGES}{path}" in sitemap

    skills = load_json("site/skills.json")
    platforms = load_json("site/platforms.json")
    root_platforms = load_json("platforms.json")
    assert skills["version"] == VERSION and len(skills["skills"]) == len(SKILLS)
    assert platforms["version"] == VERSION
    assert root_platforms["version"] == VERSION
    assert len(root_platforms["platforms"]) >= 9
    for skill in SKILLS:
        assert (ROOT / f"site/skills/{skill}/SKILL.md").read_bytes() == (
            ROOT / f"skills/{skill}/SKILL.md"
        ).read_bytes()
    assert (ROOT / "site/llms.txt").is_file()
    assert (ROOT / "site/llms-full.txt").is_file()
    assert (ROOT / "site/.well-known/security.txt").is_file()


def validate_readme() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for value in (
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
    ):
        assert value in readme
    assert "PLATFORMS.md" in readme
    assert "install.ps1" in readme
    assert "caps-security@caps-labs" not in readme


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
        "plugins/caps-security",
    ):
        assert not (ROOT / path).exists(), f"Legacy path must be removed: {path}"


def main() -> int:
    validate_canonical_skills()
    validate_openai_package()
    validate_claude_package()
    validate_gemini_package()
    validate_copilot_and_ide_adapters()
    validate_installers()
    validate_research_integrations()
    validate_site_and_discovery()
    validate_readme()
    validate_no_legacy()
    print("CAPS Unlock Lab cross-platform distribution is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
