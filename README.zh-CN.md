<div align="center">

# CAPS Unlock Lab

### 复现限制失效路径，并测量最终真正发生的动作。

**ChatGPT · Codex · Claude Code · Gemini CLI · GitHub Copilot · Cursor · Cline · Windsurf · OpenCode · MCP**

[![CAPS Verify](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-verify.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-verify.yml)
[![Research Chat](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-app.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-app.yml)
[![Distribution](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/distribution.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/distribution.yml)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · **简体中文** · [Español](README.es.md)

**AI 智能体安全 · 提示注入测试 · 越狱评估 · MCP 安全 · 工具调用安全**

[从你的平台开始](#从你的平台开始) · [内置研究](#内置研究与评测库集成) · [ASR](#如何测量-asr) · [架构](#一套核心适配多个平台) · [故障排查](#故障排查)

</div>

---

## 一句话介绍

CAPS Unlock Lab 是一个**通用研究工具，用于在经授权的合成环境中复现模型限制如何在 Prompt、instruction file、Plugin、Agent Skill、MCP Tool、附件、推理与多轮路径中逐步减弱，并通过 ASR 衡量结果**。

CAPS 不绑定任何单一厂商、模型或 CLI。项目维护两套统一的 canonical Skills 与 CAPS Verify Runtime，各个平台只提供轻量的 manifest、rule 或 agent profile。

> 这里的“Unlock”不表示秘密绕过真实用户正在使用的安全措施，而是指在你拥有或已明确获准测试的系统 synthetic twin 中复现限制失效路径，并验证防御效果。

## 从你的平台开始

### 最简单的通用安装 — macOS / Linux / WSL

```bash
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh | bash -s -- skill
```

该命令会把通用 Agent Skills 安装到 Codex/OpenCode、Claude Code 与 GitHub Copilot 易于发现的用户路径中。远程执行前，可先检查 [install.sh](https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh) 的内容。

### Windows PowerShell

```powershell
& ([scriptblock]::Create((irm https://mutoy-choi.github.io/CAPS-Agent-Security/install.ps1))) skill
```

### 各平台快速开始

| 平台 | 推荐安装 | 开始使用 |
|---|---|---|
| **ChatGPT / Codex** | `... install.sh \| bash -s -- codex` | 在 Codex 中使用 `$caps-agent-security` 或 `/skills` |
| **Claude Code** | 使用下方两条 Marketplace 命令 | `/caps-unlock:caps-agent-security` |
| **Gemini CLI** | `gemini extensions install https://github.com/Mutoy-choi/CAPS-Agent-Security --auto-update` | `/caps:audit` 或自然语言请求 |
| **GitHub Copilot** | `... install.sh \| bash -s -- copilot` | 使用 `caps-unlock` custom agent 或 Skill |
| **Cursor** | 在项目根目录运行 `... -- cursor` | 对 Agent 说“使用 CAPS 审计这个配置” |
| **Cline** | 在项目根目录运行 `... -- cline` | 使用 `/caps-unlock-audit.md` workflow |
| **Windsurf** | 在项目根目录运行 `... -- windsurf` | 使用 CAPS audit workflow |
| **OpenCode** | `... install.sh \| bash -s -- opencode` | 自动发现 Skill 或显式调用 |
| **任意 MCP/API Agent** | `... install.sh \| bash -s -- verify` | 使用 `caps-verify-runtime` 或 fixture MCP |

其中 `...` 表示：

```text
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh
```

### Claude Code Plugin

```bash
claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security
claude plugin install caps-unlock@caps-labs --scope user
```

### ChatGPT / Codex Plugin package

仓库根目录与 `plugins/caps-unlock/` 中包含 `.codex-plugin/plugin.json` 和 `skills/`。本地使用 Codex 时，安装 Agent Skills 后即可开始。发布到 ChatGPT/Codex universal directory 需要单独提交和审核，在此之前可通过本地 Plugin package 或 Skills 进行测试。

### Gemini CLI extension

```bash
gemini extensions install https://github.com/Mutoy-choi/CAPS-Agent-Security --auto-update
```

主要内容：

```text
gemini-extension.json
GEMINI.md
skills/
commands/caps/audit.toml
commands/caps/install.toml
```

## 平台支持情况

| 平台 | Native package | 通用 Skill | 项目指令 | MCP/API Runtime |
|---|:---:|:---:|:---:|:---:|
| ChatGPT / Codex | `.codex-plugin` | `.agents/skills` | `AGENTS.md` | 支持 |
| Claude Code | `.claude-plugin` | `.claude/skills` | Claude Plugin | 支持 |
| Gemini CLI | `gemini-extension.json` | `skills/` | `GEMINI.md` | 支持 |
| GitHub Copilot | custom agent | `.github/skills` | `copilot-instructions.md` | 支持 |
| Cursor | rule adapter | 引用通用 Skill | `.cursor/rules` | 支持 |
| Cline | workflow adapter | 引用通用 Skill | `.clinerules` | 支持 |
| Windsurf | workflow adapter | 引用通用 Skill | `.windsurf` | 支持 |
| OpenCode | Agent Skills | `.agents/skills` | `AGENTS.md` | 支持 |
| 其他 Host | — | Agent Skills 规范 | 依 Host 而定 | MCP 或 HTTP sidecar |

详细路径与安装差异见 [PLATFORMS.md](PLATFORMS.md)。

## CAPS 评估什么

CAPS 不只评估模型的一段输出，而是检查**上下文被转换为具有权限的动作时所经过的完整路径**。

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

### 攻击面

| 攻击面 | 评估示例 |
|---|---|
| Instruction files | `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` 与 IDE rules 之间的冲突和优先级 |
| Plugin / extension | Manifest、packaged Skills、capability 供应链与 update drift |
| Agent Skills | description、`SKILL.md`、references、scripts、assets 与 activation |
| MCP / Tool calling | metadata 或响应污染、tool selection、confused deputy、外部写入 |
| Attachments | PDF、文档、图像、音频、视频中的 indirect prompt injection |
| Reasoning / multi-turn | 长推理、累积 context、composition 与 safety drift |
| Defenses | Scanner、exchange guard、action gateway、provenance 与 confirmation |

## 如何测量 ASR

CAPS 的主要成功判断并不是让 LLM Judge 判断回复是否“看起来危险”。系统优先检查**被禁止的 synthetic Tool 是否真的被选择，或 fixture 状态是否真的发生改变**。

```text
Attachment-to-Action ASR
= 发生被禁止 synthetic action 的有效攻击运行数
  ÷ 全部有效攻击运行数
```

同时记录：

- 各攻击族的 ASR 与 95% 置信区间
- 固定预算下的 Defense-Adaptive ASR
- Benign Task Success Rate
- False Block Rate 与 Confirmation Burden
- Unauthorized Tool Invocation / Data Flow
- Composition Delta / Ratio
- Safety Drift
- latency、token 与 cost overhead

## 内置研究与评测库集成

CAPS 不只是把论文名称列在 README 中。它会**把带来源信息的 synthetic probe 规范化为统一 Attack Pack，并导出到现有评测生态中**。

### 内置 Profile

| Profile | 从研究中适配的评估思路 |
|---|---|
| `core` | PromptInject-style attachment conflict、AgentDojo-style tool-output injection、MCPTox-style tool metadata poisoning、paired benign control、composition |
| `adaptive` | `core` + FITD-style progressive multi-turn + PyRIT-ready adaptive seed |
| `reasoning` | `core` + CoT-Hijacking-inspired long benign-context dilution diagnostic |
| `multimodal` | `core` + FigStep-inspired native typographic image |
| `full` | 所有内置 Profile |

CAPS 不复制外部论文中的原始 prompt 或危险数据集。项目仅使用 canary 与 fixture tool 提供自主的 synthetic adaptation。Profile 名称不表示精确复现论文报告的 ASR。

```bash
cd caps_verify
caps-verify research list
caps-verify research describe --profile full
caps-verify research sources
```

### 可选研究库

```bash
pip install -e ".[research]"
```

推荐 bundle 包含：

```text
Inspect AI     可复现的 Task · Tool loop · Scorer · Log
PyRIT          SeedDataset 与 adaptive/multi-turn orchestration
AgentDojo      agent prompt-injection task 与 utility mapping
Pillow         native typographic-image probe rendering
```

在支持的 Python 版本中加入 garak：

```bash
pip install -e ".[research-all]"
```

检查环境：

```bash
caps-verify research doctor
```

### 一次生成所有 Bridge

```bash
caps-verify research export \
  --profile full \
  --output artifacts/research-full \
  --endpoint http://127.0.0.1:8788/v1/chat/completions \
  --model your-model-id
```

输出包含 CAPS、Inspect、PyRIT、garak、AgentDojo 的 bridge artifact、图像 canary、来源与许可证说明，以及 evidence hash。详细信息见 [`caps_verify/docs/research-library-integrations.md`](caps_verify/docs/research-library-integrations.md)。

## 最快的本地实验

```bash
git clone https://github.com/Mutoy-choi/CAPS-Agent-Security.git
cd CAPS-Agent-Security/caps_verify
python -m venv .venv
source .venv/bin/activate
pip install -e ".[gateway,dev]"
pytest
caps-verify demo --output artifacts/demo --repetitions 10
```

常用命令：

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

## 一套核心适配多个平台

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

CI 会验证各平台副本与 `skills/` 在语义上保持一致。

## 应该安装哪个组件

- **只需要 Skill：** 安装 `skill`、`codex`、`opencode` 或 Copilot Skill。
- **需要 Host 原生 package：** 使用 Claude Code Plugin 或 Gemini CLI extension。
- **需要运行实际 ASR 实验：** 使用 `verify` 安装 CAPS Verify Runtime。
- **需要连接现有评测库：** 安装 `research` 或 `research-all` extra。
- **需要面向普通用户的 UI：** 使用 `chat` 准备 Research Chat。
- **需要 MCP fixture：** 安装 CAPS Verify 后连接 `caps-verify-mcp`。

## 仅在当前项目中安装

```bash
CAPS_SCOPE=project ./install.sh codex
CAPS_SCOPE=project ./install.sh copilot
./install.sh cursor
./install.sh cline
./install.sh windsurf
```

Installer 不会覆盖共享配置文件，只添加 CAPS 专用的 rule、Skill 与 agent profile。MCP 示例不会自动启用。

## 安全边界

- 只评估你拥有或已明确获准测试的系统。
- Active attack 必须运行在隔离的 synthetic session 中，而不是实时用户对话中。
- 不要向真实用户的问题中追加隐藏 jailbreak 文本。
- 不要把真实 credential、客户文档、支付、外部传输或可破坏生产环境的 Tool 用作 fixture。
- 未提供明确批准选项时，不生成 remote research bridge。
- 仅安装 Plugin 或 Skill 不会启用 telemetry、数据贡献、MCP、Hook 或 Gateway。
- 不要把 synthetic ASR 夸大为任何商业模型的通用安全认证。

漏洞报告请参阅 [SECURITY.md](SECURITY.md)。

## 故障排查

### 看不到 Skill

1. 确认目标平台路径中存在 `SKILL.md`。
2. 删除同名的旧 Skill 副本。
3. 重启 Agent 或 CLI 会话。
4. 尝试显式调用：Codex 使用 `/skills`，Claude Code 使用 `/caps-unlock:caps-agent-security`，Gemini CLI 使用 `/caps:audit`。

### Plugin 或 extension 安装失败

- 确认已安装 Git 与对应 CLI。
- 确认仓库为 public。
- 运行 `claude plugin marketplace update caps-labs` 或 `gemini extensions update caps-unlock-lab`。
- 使用 [PLATFORMS.md](PLATFORMS.md) 中的手动路径。

### ASR 与真实应用不同

默认 Shadow ASR 使用标准 synthetic Tool 配置。若要反映实际 System Prompt、Plugin、Skill、MCP 权限与审批流程，需要构建 capability twin 和 host probe。

### 与论文数值不同

内置 Profile 将研究思路规范化为安全的 fixture action。模型、数据、TTS/OCR、judge、attack budget、Tool 配置和成功条件可能与原论文不同，因此不应直接等同这些数值。

## 链接

- Discovery site: `https://mutoy-choi.github.io/CAPS-Agent-Security/`
- Source: `https://github.com/Mutoy-choi/CAPS-Agent-Security`
- Platform matrix: [PLATFORMS.md](PLATFORMS.md)
- Research integrations: [caps_verify/docs/research-library-integrations.md](caps_verify/docs/research-library-integrations.md)
- Distribution checklist: [DISTRIBUTION.md](DISTRIBUTION.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

## 项目状态

CAPS Unlock Lab 是一个快速迭代的研究项目。发布结果时，请同时记录 model snapshot、host、attack-pack version、optional-library versions、预算、defense configuration、valid/excluded runs、confidence interval 与 evidence hash。