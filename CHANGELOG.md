# Changelog

## 0.8.0 — 2026-08-20

### Universal platform distribution

- Added a ChatGPT/Codex skills-only Plugin manifest at `.codex-plugin/plugin.json`.
- Added OpenAI Skill metadata under `agents/openai.yaml`.
- Added a Gemini CLI extension manifest, `GEMINI.md`, custom commands, and bundled Skills.
- Added GitHub Copilot Skills, a custom agent profile, and repository instructions.
- Added Cursor, Cline, Windsurf, OpenCode, and generic MCP adapters.
- Renamed the Claude Code package to `caps-unlock` and made its directory dual-manifest.
- Added Unix and Windows universal installers with platform-specific modes.
- Rewrote README and Pages around a platform-first quick-start matrix.
- Added machine-readable `platforms.json` and expanded AI/search discovery documents.

### Preserved boundaries

- No native adapter starts active probes, telemetry, hooks, or MCP servers automatically.
- Live user requests remain separate from synthetic evaluation sessions.

## 0.7.0 — 2026-08-20

- Removed the original ChillMCP demo server and legacy root scripts.
- Rebranded the repository as CAPS Unlock Lab.
- Improved Pages and Research Chat accessibility.

## 0.6.0 — 2026-08-19

- Added CAPS Verify, Research Chat, Claude Code Marketplace, Agent Skills, and discovery site.
