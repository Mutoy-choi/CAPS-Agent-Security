---
name: caps-install
description: Install, update, or deploy CAPS Agent Security, CAPS Verify Runtime, and CAPS Research Chat from GitHub. Use when the user asks to install CAPS, add the Claude Code plugin, import Agent Skills, start the LLM query gateway, enable synthetic shadow ASR, deploy the research chat, or troubleshoot CAPS dependencies.
compatibility: Requires git and Python 3.11+ for CAPS Verify. CAPS Research Chat requires Docker. Private GitHub repositories require an authenticated git credential helper.
metadata:
  author: Mutoy-choi
  version: "0.6.0"
  homepage: https://mutoy-choi.github.io/ChillMCP/
  repository: https://github.com/Mutoy-choi/ChillMCP
---

# Install CAPS

## Choose the component

- `verify`: install the CAPS Verify Python environment and CLI.
- `chat`: clone or update the repository and prepare the Docker-based CAPS Research Chat.
- `all`: prepare both.

## Before making changes

1. Explain the destination directory and dependencies.
2. Confirm before cloning, updating a repository, creating a virtual environment, or installing packages.
3. Never request or print provider API keys. Let the user enter secrets directly into their terminal or secret manager.
4. Do not enable telemetry, research contribution, or public network exposure unless the user explicitly selects it.

## Installer

From this Skill directory:

```bash
python scripts/install-caps.py --component verify
python scripts/install-caps.py --component chat
python scripts/install-caps.py --component all
```

Use `--yes` only when the user has already approved the displayed changes.

## Claude Code Plugin installation

```bash
claude plugin marketplace add Mutoy-choi/ChillMCP
claude plugin install caps-security@caps-labs --scope user
```

## Cross-client Skill installation

```bash
curl -fsSL https://mutoy-choi.github.io/ChillMCP/install.sh | bash -s -- skill
```

After installing `chat`, run:

```bash
cd ~/.local/share/caps-security/ChillMCP/caps_app
./bootstrap.sh
```
