---
name: caps-install
description: Install, update, or deploy CAPS Unlock Lab, the CAPS Claude Code Plugin, cross-client Agent Skills, CAPS Verify Runtime, synthetic shadow ASR, or CAPS Research Chat. Use when the user asks to install CAPS, add the marketplace, import Skills, start the LLM gateway, prepare a model unlock lab, or troubleshoot CAPS dependencies.
compatibility: Claude Code Plugin installation requires the Claude CLI. Skill installation requires git. CAPS Verify uses Python 3.11+. CAPS Research Chat uses Docker.
metadata:
  author: Mutoy-choi
  version: "0.7.0"
  homepage: https://mutoy-choi.github.io/CAPS-Agent-Security/
  repository: https://github.com/Mutoy-choi/CAPS-Agent-Security
---

# Install CAPS Unlock Lab

## Fast paths

Claude Code Plugin:

```bash
claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security
claude plugin install caps-security@caps-labs --scope user
```

Cross-client Skills:

```bash
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh | bash -s -- skill
```

Runtime or Chat:

```bash
python scripts/install-caps.py --component verify
python scripts/install-caps.py --component chat
```

## Installation rules

1. Explain destination, dependencies, network access, and files changed before installing packages.
2. Confirm before cloning, updating, creating a virtual environment, or starting containers.
3. Never request or print provider API keys; let the user enter secrets in a terminal or secret manager.
4. Do not enable telemetry, research contribution, public exposure, or active probes implicitly.
5. Use `--yes` only after the user has approved the displayed operations.
