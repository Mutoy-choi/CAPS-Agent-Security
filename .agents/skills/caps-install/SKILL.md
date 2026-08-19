---
name: caps-install
description: Install, update, or deploy CAPS Agent Security, CAPS Verify Runtime, and CAPS Research Chat from GitHub. Use when the user asks to install CAPS, import Agent Skills, start the LLM gateway, enable synthetic shadow ASR, deploy the research chat, or troubleshoot CAPS dependencies.
compatibility: Requires git and Python 3.11+ for CAPS Verify. CAPS Research Chat requires Docker. Private GitHub repositories require an authenticated git credential helper.
metadata:
  author: Mutoy-choi
  version: "0.6.0"
  homepage: https://mutoy-choi.github.io/ChillMCP/
  repository: https://github.com/Mutoy-choi/ChillMCP
---

# Install CAPS

Explain and confirm changes before cloning, updating, creating a virtual environment, or installing packages. Never request or print provider API keys, and never enable telemetry or public network exposure implicitly.

```bash
python scripts/install-caps.py --component verify
python scripts/install-caps.py --component chat
python scripts/install-caps.py --component all
```

Use `--yes` only after the user has approved the destination and operations.

Claude Code Plugin:

```bash
claude plugin marketplace add Mutoy-choi/ChillMCP
claude plugin install caps-security@caps-labs --scope user
```

After installing Research Chat:

```bash
cd ~/.local/share/caps-security/ChillMCP/caps_app
./bootstrap.sh
```
