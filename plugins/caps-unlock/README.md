# CAPS Unlock Lab universal Plugin

This directory is a portable, skills-only Plugin package for both supported Claude Code and ChatGPT/Codex packaging formats.

```text
.claude-plugin/plugin.json
.codex-plugin/plugin.json
skills/
```

## Claude Code

```bash
claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security
claude plugin install caps-unlock@caps-labs --scope user
```

## ChatGPT and Codex

Use this directory as the local Plugin package during development, or install the published CAPS Plugin from the universal directory when a listing is available. The same Skills can also be installed directly to `.agents/skills/`.

Installing the package does not start CAPS Verify, enable telemetry, or run active probes.
