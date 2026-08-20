---
name: caps-install
description: Install, import, update, or connect CAPS Unlock Lab on ChatGPT, Codex, Claude Code, Gemini CLI, GitHub Copilot, Cursor, Cline, Windsurf, OpenCode, Agent Skills hosts, or generic MCP/API agents. Use when the user asks to install CAPS, enable the security Skill, add research-backed profiles, install Inspect AI, PyRIT, garak, or AgentDojo bridges, start CAPS Verify, or deploy Research Chat. Explain and confirm changes before modifying files or installing packages.
compatibility: Cross-platform instructions for macOS, Linux, Windows PowerShell, and repository-scoped installations. Git, Python 3.11+, Docker, or a platform CLI may be required for selected components.
metadata:
  author: Mutoy-choi
  version: "0.8.0"
  homepage: https://mutoy-choi.github.io/CAPS-Agent-Security/
  repository: https://github.com/Mutoy-choi/CAPS-Agent-Security
---

# Install CAPS Unlock Lab

Choose the smallest package that matches the user's host and intended evaluation depth.

## Before changing the system

1. Detect the platform, operating system, desired scope, Python version, and installed dependencies.
2. Show the destination paths, packages, and exact commands.
3. Ask for confirmation before cloning, updating, copying files, creating a virtual environment, installing packages, or changing a host configuration.
4. Never request, echo, log, or transmit provider API keys. Let the user enter secrets directly in their terminal or secret manager.
5. Do not enable telemetry, research contribution, public network binding, MCP servers, hooks, or active attacks implicitly.
6. Explain that built-in research profiles are original synthetic canary adaptations with source provenance; they do not redistribute third-party datasets or reproduce paper-reported ASR by name alone.

## Fast paths

### Unix-like systems

```bash
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh | bash -s -- PLATFORM
```

### Windows PowerShell

```powershell
& ([scriptblock]::Create((irm https://mutoy-choi.github.io/CAPS-Agent-Security/install.ps1))) -Mode PLATFORM
```

Replace `PLATFORM` with `codex`, `chatgpt`, `claude`, `gemini`, `copilot`, `cursor`, `cline`, `windsurf`, `opencode`, `skill`, `verify`, `research`, `research-all`, `mcp`, `chat`, or `all`.

## Research bundles

Use `research` for the recommended built-in integration bundle:

```bash
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh | bash -s -- research
```

It installs CAPS Verify plus:

```text
Inspect AI
PyRIT
AgentDojo
Pillow
```

Use `research-all` to add garak on a supported Python version:

```bash
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh | bash -s -- research-all
```

After installation:

```bash
caps-verify research list
caps-verify research doctor
caps-verify research describe --profile full
caps-verify research export --profile full --output artifacts/research-full
```

Built-in profiles are `core`, `adaptive`, `reasoning`, `multimodal`, and `full`.

## Direct platform commands

- **Claude Code:** `claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security`, then `claude plugin install caps-unlock@caps-labs --scope user`.
- **Gemini CLI:** `gemini extensions install https://github.com/Mutoy-choi/CAPS-Agent-Security --auto-update`.
- **Codex/OpenCode:** install the Agent Skills to `~/.agents/skills/` or the current repository's `.agents/skills/`.
- **GitHub Copilot:** copy the repository Skills into `.github/skills/` and the custom agent into `.github/agents/`.
- **Cursor/Cline/Windsurf:** install only the project-rule adapter requested by the user.
- **Generic MCP/API host:** install `verify` or `research`, then use `caps-verify-runtime`, `caps-verify-gateway`, or `caps-verify-mcp` in an authorized synthetic environment.

For complete platform and research-mode notes, read `references/PLATFORMS.md`.
