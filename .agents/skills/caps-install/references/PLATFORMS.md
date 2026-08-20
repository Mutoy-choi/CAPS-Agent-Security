# CAPS installation matrix

| Mode | What it installs | Default scope |
|---|---|---|
| `codex` | Agent Skills in `.agents/skills`; Codex plugin package remains available in the checkout | user |
| `claude` | Claude Code Marketplace Plugin | user |
| `gemini` | Gemini CLI extension from the GitHub repository | user |
| `copilot` | Skills and custom-agent profile | project |
| `cursor` | Cursor rule and MCP example | project |
| `cline` | Cline rule and audit workflow | project |
| `windsurf` | Windsurf rule and audit workflow | project |
| `opencode` | Agent Skills in the OpenCode user or project path | user |
| `skill` | shared Skills for Agent Skills hosts | user |
| `verify` | CAPS Verify Python environment | user |
| `chat` | CAPS Research Chat Docker checkout | user |

Set `CAPS_SCOPE=project` to prefer repository-local files where supported. Inspect remote installers before execution.
