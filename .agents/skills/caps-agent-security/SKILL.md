---
name: caps-agent-security
description: Audit, benchmark, and harden LLM agents against jailbreaks, prompt injection, indirect prompt injection, MCP tool poisoning, malicious plugins, Agent Skills, CLAUDE.md instructions, and multimodal attachment attacks. Use when the user asks to evaluate AI agent security, measure attack success rate or ASR, review MCP or tool permissions, inspect plugins or skills, build a synthetic digital twin, compare defenses, or generate an agent security report.
compatibility: Designed for Agent Skills compatible clients and Claude Code. Use only in authorized environments. Docker, Python 3.11+, and git are optional depending on the selected CAPS component.
metadata:
  author: Mutoy-choi
  version: "0.6.0"
  homepage: https://mutoy-choi.github.io/ChillMCP/
  repository: https://github.com/Mutoy-choi/ChillMCP
---

# CAPS Agent Security

Evaluate the complete agent configuration: model, host, instructions, Plugin, Skill, MCP servers, Tool permissions, attachment pipeline, and defenses.

## Required boundaries

- Test only authorized systems.
- Keep active attacks in a synthetic digital twin with fixture tools.
- Never add hidden jailbreak text to a live user's query.
- Never test with real credentials, customer records, payments, or destructive production tools.

## Procedure

1. Record the model snapshot, agent host, instructions, plugins, skills, MCP tools, permissions, modalities, and defenses.
2. Classify attack surfaces: attachments, indirect injection, Skill/Plugin activation, MCP metadata or response poisoning, external writes, deletion, multi-turn state, and reasoning.
3. Run clean/adversarial paired scenarios under identical budgets.
4. Compare defense ablations and preserve normal task utility.
5. Score actual synthetic Tool calls and final sandbox state before using an LLM judge.
6. Report ASR, confidence intervals, false blocks, utility, attack budget, exclusions, and configuration fingerprint.

## Metrics

- Attachment-to-Action ASR
- Defense-Adaptive ASR
- Unauthorized Tool Invocation and Data Flow
- Benign Task Success and False Block Rate
- Composition Delta and Ratio
- Safety Drift and Provenance Accuracy

Install or update the runtime with the `caps-install` Skill. More detail is available in `references/REFERENCE.md`.
