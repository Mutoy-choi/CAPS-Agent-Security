# CAPS installation matrix

| Mode | What it installs | Default scope |
|---|---|---|
| `codex` / `chatgpt` | Agent Skills in `.agents/skills` and a local universal Plugin package | user |
| `claude` | Claude Code Marketplace Plugin | user |
| `gemini` | Gemini CLI extension from the GitHub repository | user |
| `copilot` | Skills and custom-agent profile | project |
| `cursor` | Cursor rule and disabled MCP example | project |
| `cline` | Cline rule and audit workflow | project |
| `windsurf` | Windsurf rule and audit workflow | project |
| `opencode` | Agent Skills in the OpenCode user or project path | user |
| `skill` | shared Skills for Agent Skills hosts | user |
| `verify` / `mcp` | CAPS Verify, Gateway, Runtime, Shadow Worker, and fixture MCP | user |
| `research` | `verify` plus Inspect AI, PyRIT, AgentDojo, and Pillow | user |
| `research-all` | `research` plus garak when the current Python version is supported | user |
| `chat` | CAPS Research Chat Docker checkout | user |

## Built-in research profiles

| Profile | Focus |
|---|---|
| `core` | paired benign control, PromptInject-style attachment conflict, AgentDojo-style tool-output injection, MCPTox-style metadata poisoning, and composition |
| `adaptive` | `core` plus FITD-style multi-turn escalation and a PyRIT-ready adaptive seed |
| `reasoning` | `core` plus a CoT-Hijacking-inspired long-context diagnostic |
| `multimodal` | `core` plus a FigStep-inspired typographic image canary |
| `full` | all bundled profiles |

```bash
caps-verify research list
caps-verify research doctor
caps-verify research sources
caps-verify research build --profile full --output artifacts/full.json
caps-verify research export --profile full --output artifacts/research-full
```

The export bundle contains native CAPS, Inspect, PyRIT, garak, and AgentDojo bridge artifacts plus source and license provenance. It does not bundle third-party raw datasets.

Set `CAPS_SCOPE=project` to prefer repository-local files where supported. Inspect remote installers before execution. Keep active evaluation in an owned or explicitly authorized synthetic environment.
