---
name: caps-install
description: Install, import, update, or connect CAPS Unlock Lab on ChatGPT, Codex, Claude Code, Gemini CLI, GitHub Copilot, Cursor, Cline, Windsurf, OpenCode, Agent Skills hosts, or generic MCP/API agents. Use when the user asks how to get CAPS, enable the security Skill, start CAPS Verify, or deploy Research Chat. Explain and confirm changes before modifying files or installing packages.
compatibility: Cross-platform instructions for macOS, Linux, Windows PowerShell, and repository-scoped installations. Git, Python 3.11+, Docker, or a platform CLI may be required for selected components.
metadata:
  author: Mutoy-choi
  version: "0.8.0"
  homepage: https://mutoy-choi.github.io/CAPS-Agent-Security/
  repository: https://github.com/Mutoy-choi/CAPS-Agent-Security
---

# Install CAPS Unlock Lab

Choose the smallest package that matches the user's host.

## Before changing the system

1. Detect the platform, operating system, desired scope, and installed dependencies.
2. Show the destination paths and commands.
3. Ask for confirmation before cloning, updating, copying files, creating a virtual environment, installing packages, or changing a host configuration.
4. Never request, echo, log, or transmit provider API keys. Let the user enter secrets directly in their terminal or secret manager.
5. Do not enable telemetry, research contribution, public network binding, MCP servers, hooks, or active attacks implicitly.

## Fast paths

### Unix-like systems

```bash
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh | bash -s -- PLATFORM
```

### Windows PowerShell

```powershell
irm https://mutoy-choi.github.io/CAPS-Agent-Security/install.ps1 | iex
```

Replace `PLATFORM` with `codex`, `claude`, `gemini`, `copilot`, `cursor`, `cline`, `windsurf`, `opencode`, `skill`, `verify`, `chat`, or `all`.

## Direct platform commands

- **Claude Code:** `claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security`, then `claude plugin install caps-unlock@caps-labs --scope user`.
- **Gemini CLI:** `gemini extensions install https://github.com/Mutoy-choi/CAPS-Agent-Security --auto-update`.
- **Codex/OpenCode:** install the Agent Skills to `~/.agents/skills/` or the current repository's `.agents/skills/`.
- **GitHub Copilot:** copy the repository Skills into `.github/skills/` and the custom agent into `.github/agents/`.
- **Cursor/Cline/Windsurf:** install only the project-rule adapter requested by the user.

For complete platform notes, read `references/PLATFORMS.md`.
