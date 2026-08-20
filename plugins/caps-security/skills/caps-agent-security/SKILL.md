---
name: caps-agent-security
description: Reproduce, audit, benchmark, and harden model restriction-bypass paths across LLM jailbreaks, prompt injection, indirect prompt injection, MCP tool poisoning, Claude Code plugins, Agent Skills, CLAUDE.md instructions, multimodal attachments, tool permissions, and runtime defenses. Use when the user asks to unlock-test a model, measure attack success rate or ASR, inspect MCP or agent extensions, compare defenses, build a synthetic capability twin, or create an AI-agent security report.
compatibility: Claude Code and Agent Skills clients. Use only on systems the user owns or is explicitly authorized to test. Prefer Docker and Python 3.11+ for reproducible CAPS runs.
metadata:
  author: Mutoy-choi
  version: "0.7.0"
  homepage: https://mutoy-choi.github.io/CAPS-Agent-Security/
  repository: https://github.com/Mutoy-choi/CAPS-Agent-Security
---

# CAPS Unlock Lab

Evaluate how a complete agent configuration loses restrictions—not only whether a model emits unsafe text.

## Required boundary

- Use only authorized targets.
- Run active probes in an isolated synthetic digital twin.
- Expose fixture tools and canaries, never production accounts or customer data.
- Keep live user conversations separate from unlock probes.
- Label synthetic scores accurately; they are not universal safety certification.

## Workflow

1. Record model snapshot, provider, host, system instructions, `CLAUDE.md`, plugins, skills, MCP servers, tool schemas, permissions, modalities, and defenses.
2. Map unlock surfaces: direct/indirect injection, attachments, extension supply chain, MCP metadata/results, tool selection, external writes, destructive actions, multi-turn context, and reasoning.
3. Create paired clean and adversarial cases under the same model, seed, tools, budget, and base task.
4. Run defense ablations: model-only, prompt policy, attachment scanner, capability scanner, exchange guard, action gateway, provenance policy, and confirmation.
5. Score fixture tool calls and final sandbox state before using a model judge.
6. Report ASR, utility, false blocks, uncertainty, exclusions, attack budget, cost, and configuration fingerprint.

## Core metrics

- Attachment-to-Action ASR
- Defense-Adaptive ASR
- Unauthorized Tool Invocation Rate
- Unauthorized Data-Flow Rate
- Benign Task Success Rate
- False Block Rate
- Composition Delta and Ratio
- Safety Drift and Provenance Accuracy

## Commands

```bash
caps-verify demo --output artifacts/demo --repetitions 10
caps-verify-runtime --help
caps-verify-gateway --help
caps-verify-shadow-worker --help
```

Read `references/REFERENCE.md` for the first scenario, evidence requirements, and composition metrics.
