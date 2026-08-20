---
name: caps-install
description: Install, update, or deploy CAPS Unlock Lab, the Claude Code Plugin, Agent Skills, CAPS Verify Runtime, synthetic shadow ASR, and CAPS Research Chat. Use when the user asks to install CAPS, add the marketplace, import Skills, start the LLM gateway, prepare an authorized model unlock lab, or troubleshoot CAPS dependencies.
compatibility: Claude Code Plugin installation requires the Claude CLI. Skills require git. CAPS Verify uses Python 3.11+. Research Chat uses Docker.
metadata:
  author: Mutoy-choi
  version: "0.7.0"
  homepage: https://mutoy-choi.github.io/CAPS-Agent-Security/
  repository: https://github.com/Mutoy-choi/CAPS-Agent-Security
---

# Install CAPS Unlock Lab

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

Explain and confirm filesystem, package, container, and network changes. Never request or print provider API keys. Do not enable telemetry, public exposure, research contribution, or active probes implicitly.
