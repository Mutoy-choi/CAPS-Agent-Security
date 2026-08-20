---
name: caps-agent-security
description: Evaluate and harden AI agents against authorized model restriction bypass, LLM jailbreaks, prompt injection, MCP tool poisoning, malicious Plugins, Agent Skills, instruction-file conflicts, and multimodal attachment attacks. Use for ASR measurement, capability-twin design, defense comparison, or agent-security reports. Do not use to attack systems without authorization or to modify live user queries secretly.
compatibility: Works with ChatGPT, Codex, Claude Code, Gemini CLI, GitHub Copilot, OpenCode, and Agent Skills compatible hosts; project-rule adapters are provided for Cursor, Cline, and Windsurf.
metadata:
  author: Mutoy-choi
  version: "0.8.0"
  homepage: https://mutoy-choi.github.io/CAPS-Agent-Security/
  repository: https://github.com/Mutoy-choi/CAPS-Agent-Security
---

# CAPS Agent Security

Evaluate the **complete agent configuration**, not only the final text response.

```text
Model + Host + Instructions + Plugin + Skill + MCP + Tool permissions
      + Attachment pipeline + Memory + Runtime defenses
```

## Required safety boundary

- Work only on systems the user owns or is explicitly authorized to evaluate.
- Keep active attacks in a synthetic digital twin with fixture tools and canary data.
- Never append hidden jailbreak text to a live user's request.
- Never use real credentials, customer records, payments, external writes, or destructive production tools.
- Separate synthetic benchmark findings from claims about a production model.

## Workflow

1. **Identify the host.** Record whether the target is ChatGPT/Codex, Claude Code, Gemini CLI, Copilot, Cursor, Cline, Windsurf, OpenCode, or a generic MCP/API agent.
2. **Fingerprint the configuration.** Record model snapshot, system/developer instructions, `AGENTS.md`/`CLAUDE.md`/`GEMINI.md`/rules, Plugins, Skills, MCP schemas, permissions, modalities, memory, and defenses.
3. **Map attack surfaces.** Cover direct and indirect prompt injection, attachment ingestion, Skill/Plugin activation, MCP metadata and response poisoning, tool selection, sensitive reads, external writes, destructive actions, multi-turn state, and reasoning length.
4. **Build paired fixtures.** Give every adversarial case a clean counterpart with the same task, model, tools, seed, and budget.
5. **Run defense ablations.** Compare model-only, instruction policy, scanners, exchange guard, action gateway, provenance policy, and user confirmation.
6. **Score actions first.** Prefer deterministic fixture-tool calls and sandbox state changes over an LLM judge.
7. **Report uncertainty and utility.** Include valid runs, exclusions, attack budget, confidence intervals, benign task success, false blocks, latency, tokens, and cost.

## Core metrics

- Attachment-to-Action ASR
- Defense-Adaptive ASR at a fixed query budget
- Unauthorized Tool Invocation Rate
- Unauthorized Data-Flow Rate
- Benign Task Success Rate
- False Block and Confirmation Burden
- Composition Delta and Composition Ratio
- Configuration Safety Drift
- Provenance Attribution Accuracy

## Expected output

Return a concise threat model, scenario matrix, execution plan, metrics table, evidence checklist, prioritized findings, and concrete remediations. Label unimplemented or untested surfaces explicitly.

Read `references/PLATFORMS.md` for host-specific paths and commands.
