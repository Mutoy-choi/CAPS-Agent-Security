# CAPS Unlock Lab for Gemini CLI

CAPS Unlock Lab provides platform-neutral Agent Skills for authorized model-restriction-bypass research and AI-agent security evaluation.

Use the bundled `caps-agent-security` Skill when the user asks about jailbreak ASR, prompt injection, MCP tool poisoning, Plugin or Skill abuse, `CLAUDE.md`/instruction conflicts, multimodal attachment attacks, synthetic capability twins, or defense comparison.

Use the bundled `caps-install` Skill when the user asks to install or connect CAPS on another platform.

## Boundaries

- Evaluate only systems the user owns or is authorized to test.
- Run active probes in isolated synthetic sessions with fixture tools.
- Never add hidden attack text to live user queries.
- Never use real credentials, customer data, payments, or destructive production tools.
- Explain which files, commands, packages, and network endpoints will change before installation.
