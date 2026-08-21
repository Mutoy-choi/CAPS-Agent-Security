<div align="center">

# CAPS Unlock Lab

### 制限回避の経路を再現し、その先で実際に起きるアクションまで測定する。

**ChatGPT · Codex · Claude Code · Gemini CLI · GitHub Copilot · Cursor · Cline · Windsurf · OpenCode · MCP**

[![CAPS Verify](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-verify.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-verify.yml)
[![Research Chat](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-app.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-app.yml)
[![Distribution](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/distribution.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/distribution.yml)

[English](README.md) · [한국어](README.ko.md) · **日本語** · [简体中文](README.zh-CN.md) · [Español](README.es.md)

**AIエージェントセキュリティ · プロンプトインジェクション評価 · Jailbreak評価 · MCPセキュリティ · Tool-use safety**

[プラットフォームから始める](#プラットフォームから始める) · [内蔵リサーチ](#内蔵リサーチとライブラリ連携) · [ASR](#asrの測定方法) · [構成](#1つのコアを複数プラットフォームへ) · [トラブルシューティング](#トラブルシューティング)

</div>

---

## 一文で説明すると

CAPS Unlock Lab は、**Prompt、instruction file、Plugin、Agent Skill、MCP Tool、添付ファイル、推論、マルチターン経路を通じてモデルの制限がどこまで弱まるかを、許可された synthetic 環境で再現し、ASR で測定する汎用研究ツール**です。

特定の企業、モデル、CLI には依存しません。2つの canonical Skill と CAPS Verify Runtime を共通コアとして維持し、各プラットフォームには薄い manifest・rule・agent profile だけを提供します。

> ここでいう「Unlock」は、実ユーザー向けの安全機構を密かに回避する意味ではありません。所有している、または明示的な許可を得たシステムの synthetic twin で制限回避経路を再現し、防御を検証するという意味です。

## プラットフォームから始める

### 共通の最短インストール — macOS / Linux / WSL

```bash
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh | bash -s -- skill
```

Codex/OpenCode、Claude Code、GitHub Copilot が検出しやすいユーザーパスへ共通 Agent Skills を配置します。リモート実行前に [install.sh](https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh) の内容を確認できます。

### Windows PowerShell

```powershell
& ([scriptblock]::Create((irm https://mutoy-choi.github.io/CAPS-Agent-Security/install.ps1))) skill
```

### プラットフォーム別クイックスタート

| プラットフォーム | 推奨インストール | 開始方法 |
|---|---|---|
| **ChatGPT / Codex** | `... install.sh \| bash -s -- codex` | Codex で `$caps-agent-security` または `/skills` |
| **Claude Code** | 下記 Marketplace コマンド2行 | `/caps-unlock:caps-agent-security` |
| **Gemini CLI** | `gemini extensions install https://github.com/Mutoy-choi/CAPS-Agent-Security --auto-update` | `/caps:audit` または自然言語で依頼 |
| **GitHub Copilot** | `... install.sh \| bash -s -- copilot` | `caps-unlock` custom agent または Skill |
| **Cursor** | プロジェクトルートで `... -- cursor` | 「CAPSでこの構成を監査して」と依頼 |
| **Cline** | プロジェクトルートで `... -- cline` | `/caps-unlock-audit.md` workflow |
| **Windsurf** | プロジェクトルートで `... -- windsurf` | CAPS audit workflow |
| **OpenCode** | `... install.sh \| bash -s -- opencode` | Skill の自動検出または明示呼び出し |
| **任意の MCP/API Agent** | `... install.sh \| bash -s -- verify` | `caps-verify-runtime` または fixture MCP |

`...` は次を表します。

```text
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh
```

### Claude Code Plugin

```bash
claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security
claude plugin install caps-unlock@caps-labs --scope user
```

### ChatGPT / Codex Plugin package

リポジトリルートと `plugins/caps-unlock/` に `.codex-plugin/plugin.json` と `skills/` が含まれています。Codex のローカル利用は Agent Skills の導入だけで開始できます。ChatGPT/Codex の universal directory 公開には別途提出・審査が必要なため、それまではローカル Plugin package または Skills で検証します。

### Gemini CLI extension

```bash
gemini extensions install https://github.com/Mutoy-choi/CAPS-Agent-Security --auto-update
```

主な構成:

```text
gemini-extension.json
GEMINI.md
skills/
commands/caps/audit.toml
commands/caps/install.toml
```

## 対応状況

| プラットフォーム | Native package | 共通 Skill | プロジェクト指示 | MCP/API Runtime |
|---|:---:|:---:|:---:|:---:|
| ChatGPT / Codex | `.codex-plugin` | `.agents/skills` | `AGENTS.md` | 対応 |
| Claude Code | `.claude-plugin` | `.claude/skills` | Claude Plugin | 対応 |
| Gemini CLI | `gemini-extension.json` | `skills/` | `GEMINI.md` | 対応 |
| GitHub Copilot | custom agent | `.github/skills` | `copilot-instructions.md` | 対応 |
| Cursor | rule adapter | 共通 Skill を参照 | `.cursor/rules` | 対応 |
| Cline | workflow adapter | 共通 Skill を参照 | `.clinerules` | 対応 |
| Windsurf | workflow adapter | 共通 Skill を参照 | `.windsurf` | 対応 |
| OpenCode | Agent Skills | `.agents/skills` | `AGENTS.md` | 対応 |
| その他のホスト | — | Agent Skills 仕様 | ホスト依存 | MCP または HTTP sidecar |

詳細なパスとインストール差分は [PLATFORMS.md](PLATFORMS.md) を参照してください。

## CAPS が評価するもの

単一のモデル出力だけではなく、**コンテキストが権限を持つアクションへ変換される経路全体**を評価します。

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

### 攻撃面

| 対象 | 評価例 |
|---|---|
| Instruction files | `AGENTS.md`、`CLAUDE.md`、`GEMINI.md`、IDE rules 間の競合と優先順位 |
| Plugin / extension | Manifest、packaged Skills、capability supply chain、update drift |
| Agent Skills | description、`SKILL.md`、references、scripts、assets、activation |
| MCP / Tool calling | metadata・応答汚染、tool selection、confused deputy、外部書き込み |
| Attachments | PDF、文書、画像、音声、動画による indirect prompt injection |
| Reasoning / multi-turn | 長い推論、蓄積 context、composition、safety drift |
| Defenses | Scanner、exchange guard、action gateway、provenance、confirmation |

## ASRの測定方法

CAPS は「出力が危険そうに見えるか」という LLM Judge の印象を主要な成功条件にはしません。**禁止された synthetic Tool が実際に選択されたか、fixture の状態が実際に変わったか**を優先します。

```text
Attachment-to-Action ASR
= 禁止された synthetic action が発生した有効な攻撃実行数
  ÷ すべての有効な攻撃実行数
```

同時に記録する指標:

- 攻撃ファミリー別 ASR と 95% 信頼区間
- 固定 budget での Defense-Adaptive ASR
- Benign Task Success Rate
- False Block Rate と Confirmation Burden
- Unauthorized Tool Invocation / Data Flow
- Composition Delta / Ratio
- Safety Drift
- latency、token、cost overhead

## 内蔵リサーチとライブラリ連携

CAPS は論文名を並べるだけではありません。**出典付き synthetic probe を共通 Attack Pack に正規化し、既存の評価エコシステムへ export**します。

### 内蔵プロファイル

| Profile | 研究から適応した評価アイデア |
|---|---|
| `core` | PromptInject-style attachment conflict、AgentDojo-style tool-output injection、MCPTox-style tool metadata poisoning、paired benign control、composition |
| `adaptive` | `core` + FITD-style progressive multi-turn + PyRIT-ready adaptive seed |
| `reasoning` | `core` + CoT-Hijacking-inspired long benign-context dilution diagnostic |
| `multimodal` | `core` + FigStep-inspired native typographic image |
| `full` | すべての内蔵プロファイル |

外部論文の raw prompt や危険な dataset は複製しません。canary と fixture tool だけを用いた独自の synthetic adaptation を提供します。Profile 名は論文記載 ASR の完全再現を意味しません。

```bash
cd caps_verify
caps-verify research list
caps-verify research describe --profile full
caps-verify research sources
```

### オプションの研究ライブラリ

```bash
pip install -e ".[research]"
```

推奨 bundle:

```text
Inspect AI     再現可能な Task · Tool loop · Scorer · Log
PyRIT          SeedDataset と adaptive/multi-turn orchestration
AgentDojo      agent prompt-injection task と utility mapping
Pillow         native typographic-image probe rendering
```

対応 Python で garak も含める場合:

```bash
pip install -e ".[research-all]"
```

環境確認:

```bash
caps-verify research doctor
```

### すべての bridge を一度に生成

```bash
caps-verify research export \
  --profile full \
  --output artifacts/research-full \
  --endpoint http://127.0.0.1:8788/v1/chat/completions \
  --model your-model-id
```

生成物には CAPS、Inspect、PyRIT、garak、AgentDojo 用の bridge、画像 canary、出典・ライセンス情報、evidence hash が含まれます。詳細は [`caps_verify/docs/research-library-integrations.md`](caps_verify/docs/research-library-integrations.md) を参照してください。

## 最短のローカル実験

```bash
git clone https://github.com/Mutoy-choi/CAPS-Agent-Security.git
cd CAPS-Agent-Security/caps_verify
python -m venv .venv
source .venv/bin/activate
pip install -e ".[gateway,dev]"
pytest
caps-verify demo --output artifacts/demo --repetitions 10
```

主なコマンド:

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

## 1つのコアを複数プラットフォームへ

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

CI が各プラットフォーム用コピーと `skills/` の意味的な一致を検証します。

## どれをインストールすべきか

- **Skill だけ必要:** `skill`、`codex`、`opencode`、または Copilot Skill。
- **ホスト固有 package が必要:** Claude Code Plugin または Gemini CLI extension。
- **実際の ASR 実験が必要:** `verify` で CAPS Verify Runtime。
- **既存評価ライブラリと連携:** `research` または `research-all` extra。
- **一般ユーザー向け UI が必要:** `chat` で Research Chat。
- **MCP fixture が必要:** CAPS Verify 導入後に `caps-verify-mcp` を接続。

## プロジェクト内だけにインストール

```bash
CAPS_SCOPE=project ./install.sh codex
CAPS_SCOPE=project ./install.sh copilot
./install.sh cursor
./install.sh cline
./install.sh windsurf
```

Installer は共有設定を上書きせず、CAPS 専用の rule・Skill・agent profile だけを追加します。MCP example は自動有効化されません。

## 安全境界

- 所有している、または明示的な許可を得たシステムだけを評価してください。
- Active attack は実ユーザー会話ではなく、隔離された synthetic session で実行してください。
- 実ユーザーの質問に隠れた jailbreak 文を追加しないでください。
- 実 credential、顧客文書、決済、外部転送、破壊可能な production Tool を fixture に使わないでください。
- 明示的な承認オプションなしに remote research bridge を生成しません。
- Plugin または Skill の導入だけで telemetry、data contribution、MCP、Hook、Gateway は有効になりません。
- synthetic ASR を商用モデルの普遍的な安全認証として扱わないでください。

脆弱性報告は [SECURITY.md](SECURITY.md) を参照してください。

## トラブルシューティング

### Skill が表示されない

1. 対象プラットフォームのパスに `SKILL.md` があるか確認します。
2. 同名の古い Skill コピーを削除します。
3. Agent/CLI セッションを再起動します。
4. Codex は `/skills`、Claude Code は `/caps-unlock:caps-agent-security`、Gemini CLI は `/caps:audit` で明示的に呼び出します。

### Plugin または extension のインストールに失敗する

- Git と対象 CLI が導入済みか確認します。
- リポジトリが public であることを確認します。
- `claude plugin marketplace update caps-labs` または `gemini extensions update caps-unlock-lab` を実行します。
- [PLATFORMS.md](PLATFORMS.md) の手動パスを利用します。

### ASR が実アプリと異なる

デフォルトの Shadow ASR は標準 synthetic Tool 構成を使用します。実際の System Prompt、Plugin、Skill、MCP 権限、承認フローを反映するには capability twin と host probe が必要です。

### 論文の数値と異なる

内蔵 profile は研究アイデアを安全な fixture action に正規化したものです。モデル、データ、TTS/OCR、judge、attack budget、Tool 構成、成功条件が元論文と異なるため、数値を直接同一視しないでください。

## リンク

- Discovery site: `https://mutoy-choi.github.io/CAPS-Agent-Security/`
- Source: `https://github.com/Mutoy-choi/CAPS-Agent-Security`
- Platform matrix: [PLATFORMS.md](PLATFORMS.md)
- Research integrations: [caps_verify/docs/research-library-integrations.md](caps_verify/docs/research-library-integrations.md)
- Distribution checklist: [DISTRIBUTION.md](DISTRIBUTION.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

## ステータス

CAPS Unlock Lab は変化の速い研究プロジェクトです。結果には model snapshot、host、attack-pack version、optional-library versions、budget、defense configuration、valid/excluded runs、confidence interval、evidence hash を記録してください。