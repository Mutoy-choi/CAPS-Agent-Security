<div align="center">

# CAPS Unlock Lab

### Reproduce restriction-bypass paths. Measure the actions that follow.

**ChatGPT · Codex · Claude Code · Gemini CLI · GitHub Copilot · Cursor · Cline · Windsurf · OpenCode · MCP**

[![CAPS Verify](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-verify.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-verify.yml)
[![Research Chat](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-app.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-app.yml)
[![Distribution](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/distribution.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/distribution.yml)

**English** · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md)

**AI agent security · prompt injection testing · jailbreak evaluation · MCP security · tool-use safety**

[Start on your platform](#start-on-your-platform) · [Built-in research](#built-in-research-and-library-integrations) · [ASR](#how-asr-is-measured) · [Architecture](#one-core-many-platforms) · [Troubleshooting](#troubleshooting)

</div>

---

## In one sentence

CAPS Unlock Lab is a **general-purpose research toolkit that reproduces, in authorized synthetic environments, how model restrictions can weaken across prompts, instruction files, plugins, Agent Skills, MCP tools, attachments, reasoning, and multi-turn paths—and measures the outcome with ASR**.

CAPS is not tied to one vendor, model, or CLI. It keeps the same two canonical Skills and CAPS Verify Runtime, while each platform receives only a thin manifest, rule, or agent profile.

> “Unlock” does not mean secretly bypassing safeguards for live users. It means reproducing restriction-bypass paths inside a synthetic twin of a system you own or are explicitly authorized to test, then validating defenses.

## Start on your platform

### Simplest shared installation — macOS / Linux / WSL

```bash
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh | bash -s -- skill
```

This installs the shared Agent Skills into user paths that Codex/OpenCode, Claude Code, and GitHub Copilot can discover. You can inspect [install.sh](https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh) before executing it remotely.

### Windows PowerShell

```powershell
& ([scriptblock]::Create((irm https://mutoy-choi.github.io/CAPS-Agent-Security/install.ps1))) skill
```

### One line per platform

| Platform | Recommended installation | Start using it |
|---|---|---|
| **ChatGPT / Codex** | `... install.sh \| bash -s -- codex` | Use `$caps-agent-security` or `/skills` in Codex |
| **Claude Code** | Use the two Marketplace commands below | `/caps-unlock:caps-agent-security` |
| **Gemini CLI** | `gemini extensions install https://github.com/Mutoy-choi/CAPS-Agent-Security --auto-update` | `/caps:audit` or a natural-language request |
| **GitHub Copilot** | `... install.sh \| bash -s -- copilot` | Use the `caps-unlock` custom agent or Skill |
| **Cursor** | Run `... -- cursor` from the project root | Ask the agent to “Audit this setup with CAPS” |
| **Cline** | Run `... -- cline` from the project root | Use the `/caps-unlock-audit.md` workflow |
| **Windsurf** | Run `... -- windsurf` from the project root | Use the CAPS audit workflow |
| **OpenCode** | `... install.sh \| bash -s -- opencode` | Automatic Skill discovery or explicit invocation |
| **Any MCP/API agent** | `... install.sh \| bash -s -- verify` | Use `caps-verify-runtime` or the fixture MCP |

Here, `...` means:

```text
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh
```

### Claude Code Plugin

```bash
claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security
claude plugin install caps-unlock@caps-labs --scope user
```

### ChatGPT / Codex Plugin package

The repository root and `plugins/caps-unlock/` include `.codex-plugin/plugin.json` and `skills/`. Local Codex use works immediately after installing the Agent Skills. Publishing to a universal ChatGPT/Codex directory requires a separate submission and review process; before that, test with the local Plugin package or Skills.

### Gemini CLI extension

```bash
gemini extensions install https://github.com/Mutoy-choi/CAPS-Agent-Security --auto-update
```

Included files:

```text
gemini-extension.json
GEMINI.md
skills/
commands/caps/audit.toml
commands/caps/install.toml
```

## Platform support

| Platform | Native package | Shared Skill | Project instructions | MCP/API Runtime |
|---|:---:|:---:|:---:|:---:|
| ChatGPT / Codex | `.codex-plugin` | `.agents/skills` | `AGENTS.md` | Supported |
| Claude Code | `.claude-plugin` | `.claude/skills` | Claude Plugin | Supported |
| Gemini CLI | `gemini-extension.json` | `skills/` | `GEMINI.md` | Supported |
| GitHub Copilot | custom agent | `.github/skills` | `copilot-instructions.md` | Supported |
| Cursor | rule adapter | references shared Skill | `.cursor/rules` | Supported |
| Cline | workflow adapter | references shared Skill | `.clinerules` | Supported |
| Windsurf | workflow adapter | references shared Skill | `.windsurf` | Supported |
| OpenCode | Agent Skills | `.agents/skills` | `AGENTS.md` | Supported |
| Other hosts | — | Agent Skills specification | host-specific | MCP or HTTP sidecar |

Detailed paths and installation differences are documented in [PLATFORMS.md](PLATFORMS.md).

## What CAPS evaluates

CAPS evaluates more than a model response. It examines the **entire path through which context becomes an authorized action**.

```text
Prompt / Attachment / AGENTS.md / CLAUDE.md / GEMINI.md
Plugin / Skill / MCP metadata / Tool response
                         ↓
                   Model reasoning
                         ↓
                    Tool selection
                         ↓
       synthetic read / write / transfer / delete
                         ↓
      ASR · benign utility · defense effectiveness
```

### Attack surfaces

| Surface | Example evaluation |
|---|---|
| Instruction files | Conflicts and precedence across `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and IDE rules |
| Plugin / extension | Manifests, packaged Skills, capability supply chains, and update drift |
| Agent Skills | Descriptions, `SKILL.md`, references, scripts, assets, and activation |
| MCP / Tool calling | Metadata or response poisoning, tool selection, confused-deputy behavior, and external writes |
| Attachments | Indirect prompt injection through PDFs, documents, images, audio, and video |
| Reasoning / multi-turn | Long reasoning, accumulated context, composition, and safety drift |
| Defenses | Scanners, exchange guards, action gateways, provenance, and confirmation flows |

## How ASR is measured

CAPS does not primarily decide success by asking an LLM judge whether a response merely “looks dangerous.” It prioritizes whether a **forbidden synthetic tool was actually selected or fixture state actually changed**.

```text
Attachment-to-Action ASR
= valid attack runs in which a forbidden synthetic action occurred
  ÷ all valid attack runs
```

CAPS also records:

- ASR by attack family with 95% confidence intervals
- Defense-Adaptive ASR at a fixed budget
- Benign Task Success Rate
- False Block Rate and Confirmation Burden
- Unauthorized Tool Invocation / Data Flow
- Composition Delta / Ratio
- Safety Drift
- Latency, token, and cost overhead

## Built-in research and library integrations

CAPS does not merely list paper titles in the README. It **normalizes source-linked synthetic probes into a shared Attack Pack and exports them into existing evaluation ecosystems**.

### Built-in profiles

| Profile | Evaluation ideas adapted from research |
|---|---|
| `core` | PromptInject-style attachment conflict, AgentDojo-style tool-output injection, MCPTox-style tool metadata poisoning, paired benign control, and composition |
| `adaptive` | `core` plus FITD-style progressive multi-turn testing and a PyRIT-ready adaptive seed |
| `reasoning` | `core` plus a CoT-Hijacking-inspired long benign-context dilution diagnostic |
| `multimodal` | `core` plus a FigStep-inspired native typographic image |
| `full` | All built-in profiles |

CAPS does not copy raw prompts or hazardous datasets from external papers. It provides original synthetic adaptations using canaries and fixture tools. Profile names do not imply an exact reproduction of paper-reported ASR.

```bash
cd caps_verify
caps-verify research list
caps-verify research describe --profile full
caps-verify research sources
```

### Optional research libraries

```bash
pip install -e ".[research]"
```

The recommended bundle includes:

```text
Inspect AI     reproducible Task · Tool loop · Scorer · Log
PyRIT          SeedDataset and adaptive/multi-turn orchestration
AgentDojo      agent prompt-injection task and utility mapping
Pillow         native typographic-image probe rendering
```

To include garak on a supported Python version:

```bash
pip install -e ".[research-all]"
```

Check the environment:

```bash
caps-verify research doctor
```

### Generate every bridge in one command

```bash
caps-verify research export \
  --profile full \
  --output artifacts/research-full \
  --endpoint http://127.0.0.1:8788/v1/chat/completions \
  --model your-model-id
```

Generated artifacts:

```text
caps-attack-pack.json       CAPS Shadow Worker
inspect-dataset.jsonl       Inspect normalized records
pyrit-seeds.prompt          PyRIT SeedDataset YAML/JSON
garak-rest.json             garak RestGenerator config
agentdojo-scenarios.json    AgentDojo custom-suite mapping
artifacts/*.png             native image canary
SOURCES.md                   papers, libraries, versions, and licenses
manifest.sha256.json         evidence hashes
```

A native Inspect AI task is also registered:

```bash
inspect eval \
  src/caps_verify/integrations/inspect_task.py@caps_research \
  -T profile=core \
  --model your-provider/your-model
```

See [`caps_verify/docs/research-library-integrations.md`](caps_verify/docs/research-library-integrations.md) for research sources and implementation details.

## Fastest local experiment

```bash
git clone https://github.com/Mutoy-choi/CAPS-Agent-Security.git
cd CAPS-Agent-Security/caps_verify
python -m venv .venv
source .venv/bin/activate
pip install -e ".[gateway,dev]"
pytest
caps-verify demo --output artifacts/demo --repetitions 10
```

Key commands:

```bash
caps-verify research list
caps-verify research doctor
caps-verify research build --profile core --output artifacts/core.json
caps-verify-runtime --help
caps-verify-gateway --help
caps-verify-shadow-worker --help
caps-verify-mcp --help
caps-verify demo --output artifacts/demo --repetitions 10
```

## One core, many platforms

```text
skills/                         canonical Skills
├── caps-agent-security/
└── caps-install/

.codex-plugin/                  ChatGPT / Codex package
.claude-plugin/ + plugins/      Claude Code Marketplace
 gemini-extension.json          Gemini CLI extension
.github/skills + agents/        GitHub Copilot
.cursor/rules/                  Cursor adapter
.clinerules/                    Cline adapter
.windsurf/                      Windsurf adapter
.agents/skills/                 Codex · OpenCode · shared discovery
caps_verify/                    Runtime, research profiles, library bridges, MCP
caps_app/                       accessible Research Chat
```

CI verifies that platform-specific copies remain semantically aligned with `skills/`.

## Which component should I install?

- **Only need the Skill:** install `skill`, `codex`, `opencode`, or the Copilot Skill.
- **Need a host-native package:** use the Claude Code Plugin or Gemini CLI extension.
- **Need to run real ASR experiments:** install the CAPS Verify Runtime with `verify`.
- **Need existing evaluation libraries:** install the `research` or `research-all` extra.
- **Need an end-user UI:** prepare Research Chat with `chat`.
- **Need an MCP fixture:** install CAPS Verify and connect `caps-verify-mcp`.

## Project-scoped installation

To install files only inside the current repository:

```bash
CAPS_SCOPE=project ./install.sh codex
CAPS_SCOPE=project ./install.sh copilot
./install.sh cursor
./install.sh cline
./install.sh windsurf
```

The installer does not overwrite shared configuration files. It adds only CAPS-specific rules, Skills, and agent profiles. MCP examples are not activated automatically.

## Accessibility

- README and Pages present platform installation paths in the same order.
- Keyboard navigation, visible focus, high contrast, reduced motion, forced colors, and 200% zoom are considered.
- Windows PowerShell and Unix shell installation paths are both provided.
- Directly accessible `skills.json`, `platforms.json`, `marketplace.json`, `llms.txt`, `llms-full.txt`, and `SKILL.md` resources are available.
- Important state is never communicated by color alone.

## Safety boundaries

- Evaluate only systems you own or are explicitly authorized to test.
- Run active attacks in isolated synthetic sessions, never in live user conversations.
- Never append hidden jailbreak text to a real user's request.
- Never use real credentials, customer documents, payments, external transfers, or destructive production tools as fixtures.
- Do not generate a remote research bridge without an explicit approval option.
- Installing a Plugin or Skill alone does not enable telemetry, data contribution, MCP, hooks, or gateways.
- Do not present synthetic ASR as a universal safety certification for a commercial model.

See [SECURITY.md](SECURITY.md) to report vulnerabilities.

## Troubleshooting

### The Skill is not visible

1. Confirm that `SKILL.md` exists in the platform path.
2. Remove stale copies of the same Skill name.
3. Restart the Agent or CLI session.
4. Try an explicit invocation: `/skills` in Codex, `/caps-unlock:caps-agent-security` in Claude Code, or `/caps:audit` in Gemini CLI.

### Plugin or extension installation fails

- Confirm that Git and the relevant CLI are installed.
- Confirm that the repository is public.
- Run `claude plugin marketplace update caps-labs` or `gemini extensions update caps-unlock-lab`.
- Use the manual paths in [PLATFORMS.md](PLATFORMS.md).

### ASR differs from the real application

The default Shadow ASR uses a standardized synthetic tool configuration. To reflect a real System Prompt, Plugin, Skill, MCP permissions, and approval flow, build a capability twin and host probe.

### CAPS results differ from a paper

Built-in profiles normalize research ideas into safe fixture actions. Models, data, TTS/OCR, judges, attack budgets, tool configurations, and success conditions may differ from the original paper, so the numbers should not be treated as directly equivalent.

## Links

- Discovery site: `https://mutoy-choi.github.io/CAPS-Agent-Security/`
- Source: `https://github.com/Mutoy-choi/CAPS-Agent-Security`
- Platform matrix: [PLATFORMS.md](PLATFORMS.md)
- Research integrations: [caps_verify/docs/research-library-integrations.md](caps_verify/docs/research-library-integrations.md)
- Distribution checklist: [DISTRIBUTION.md](DISTRIBUTION.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

## Status

CAPS Unlock Lab is a fast-moving research project. Record the model snapshot, host, attack-pack version, optional-library versions, budget, defense configuration, valid and excluded runs, confidence interval, and evidence hash with every result.