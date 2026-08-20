# CAPS platform reference

| Platform | Native package or discovery path | Recommended use |
|---|---|---|
| ChatGPT / Codex | `.codex-plugin/plugin.json`, `skills/`, `.agents/skills/`, `AGENTS.md` | Install the universal Plugin when available, or copy the Skills for local use. |
| Claude Code | `.claude-plugin/marketplace.json`, `plugins/caps-unlock/` | Install from the `caps-labs` Marketplace. |
| Gemini CLI | `gemini-extension.json`, `GEMINI.md`, `commands/`, `skills/` | Install the repository as a Gemini CLI extension. |
| GitHub Copilot | `.github/skills/`, `.github/agents/caps-unlock.md` | Copy into a repository or use the Skill directory with the Copilot SDK. |
| Cursor | `.cursor/rules/caps-unlock.mdc` | Copy the project rule; configure MCP separately when needed. |
| Cline | `.clinerules/caps-unlock.md`, `.clinerules/workflows/` | Copy project rules and the audit workflow. |
| Windsurf | `.windsurf/rules/`, `.windsurf/workflows/` | Copy project rules and the audit workflow. |
| OpenCode | `.agents/skills/`, `AGENTS.md` | Install Skills to `.agents/skills` or the OpenCode user Skill directory. |
| Generic MCP/API host | `caps_verify/`, `platforms/mcp/` | Run CAPS Verify as a local runtime, sidecar, or fixture MCP server. |

The common Skill is instruction-only. Installing it does not start a server, enable telemetry, or run an attack.
