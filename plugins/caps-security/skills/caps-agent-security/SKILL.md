---
name: caps-agent-security
description: Audit, benchmark, and harden LLM agents against jailbreaks, prompt injection, indirect prompt injection, MCP tool poisoning, malicious plugins, Agent Skills, CLAUDE.md instructions, and multimodal attachment attacks. Use when the user asks to evaluate AI agent security, measure attack success rate or ASR, review MCP or tool permissions, inspect plugins or skills, build a synthetic digital twin, compare defenses, or generate an agent security report.
compatibility: Designed for Claude Code and other Agent Skills clients. Use only in authorized environments. Docker, Python 3.11+, and git are optional depending on the selected CAPS component.
metadata:
  author: Mutoy-choi
  version: "0.6.0"
  homepage: https://mutoy-choi.github.io/ChillMCP/
  repository: https://github.com/Mutoy-choi/ChillMCP
---

# CAPS Agent Security

Use this skill to evaluate the security of an LLM agent configuration rather than judging a model from text output alone.

## Safety boundary

- Work only on systems the user owns or is authorized to test.
- Run active attacks in an isolated synthetic environment with fixture tools.
- Do not mix jailbreak probes into a live user's conversation.
- Do not use real credentials, customer files, payment systems, or destructive production tools.
- Distinguish synthetic benchmark scores from claims about a production model.

## Workflow

1. **Define the target configuration.** Record model/provider, agent host, system instructions or `CLAUDE.md`, installed plugins and skills, MCP servers, tool schemas, permissions, attachment pipeline, and active defenses.
2. **Inventory attack surfaces.** Classify attachments, indirect prompt injection, Skill or Plugin activation, MCP metadata and response poisoning, tool-selection risk, external writes, destructive actions, multi-turn state, and reasoning settings.
3. **Choose an execution mode.** Prefer CAPS Verify fixture mode for reproducible tests. Use a capability twin when the user's real tool structure must be represented without real side effects.
4. **Run paired cases.** For every adversarial case, run a clean case with the same base task, model snapshot, seed, tools, and budget.
5. **Evaluate defense ablations.** Compare model-only, prompt policy, attachment scanner, capability scanner, exchange guard, action gateway, provenance policy, and user confirmation.
6. **Score actual actions.** Prioritize sandbox state changes and deterministic policy predicates over an LLM judge.
7. **Report uncertainty.** Include valid runs, exclusions, attack budget, model snapshot, confidence intervals, false-block rate, and normal-task utility.

## Core metrics

- Attachment-to-Action ASR
- Defense-Adaptive ASR at a fixed query budget
- Unauthorized Tool Invocation Rate
- Unauthorized Data-Flow Rate
- Benign Task Success Rate
- False Block Rate
- Composition Delta and Composition Ratio
- Configuration Safety Drift
- Provenance Attribution Accuracy

## CAPS commands

After installing CAPS Verify:

```bash
caps-verify demo --output artifacts/demo --repetitions 10
caps-verify-runtime --help
caps-verify-gateway --help
caps-verify-shadow-worker --help
```

For architecture, threat-model and reporting details, read `references/REFERENCE.md`.
