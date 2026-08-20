<div align="center">

# CAPS Unlock Lab

### 제한 해제 경로를 재현하고, 실제 행동까지 측정한다.

**ChatGPT · Codex · Claude Code · Gemini CLI · GitHub Copilot · Cursor · Cline · Windsurf · OpenCode · MCP**

[![CAPS Verify](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-verify.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-verify.yml)
[![Research Chat](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-app.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-app.yml)
[![Distribution](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/distribution.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/distribution.yml)

[내 플랫폼에서 시작](#내-플랫폼에서-시작) · [CAPS가 하는 일](#caps가-하는-일) · [ASR](#asr은-어떻게-측정하나) · [구성](#하나의-코어-여러-플랫폼) · [문제 해결](#문제-해결)

</div>

---

## 한 문장으로

CAPS Unlock Lab은 **모델의 제한이 Prompt, instruction file, Plugin, Agent Skill, MCP Tool, 첨부파일, 추론 및 다중 턴 경로에서 어디까지 약해지는지 승인된 synthetic 환경에서 재현하고 ASR로 측정하는 범용 연구 도구**입니다.

CAPS는 특정 회사의 모델이나 한 가지 CLI에 종속되지 않습니다. 같은 두 개의 핵심 Skill과 CAPS Verify Runtime을 유지하고, 각 플랫폼에는 얇은 manifest·rule·agent profile만 제공합니다.

> 여기서 “unlock”은 라이브 사용자의 안전장치를 몰래 우회한다는 뜻이 아닙니다. 소유하거나 허가받은 시스템의 synthetic twin에서 제한 해제 경로를 재현하고 방어를 검증한다는 뜻입니다.

## 내 플랫폼에서 시작

### 가장 간단한 공통 설치 — macOS / Linux / WSL

```bash
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh | bash -s -- skill
```

이 명령은 공통 Agent Skills를 Codex/OpenCode, Claude Code, GitHub Copilot이 찾기 쉬운 사용자 경로에 설치합니다. 원격 실행 전에 [install.sh](https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh)을 먼저 확인할 수 있습니다.

### Windows PowerShell

```powershell
& ([scriptblock]::Create((irm https://mutoy-choi.github.io/CAPS-Agent-Security/install.ps1))) skill
```

### 플랫폼별 한 줄

| 플랫폼 | 권장 설치 | 사용 시작 |
|---|---|---|
| **ChatGPT / Codex** | `... install.sh \| bash -s -- codex` | Codex에서 `$caps-agent-security` 또는 `/skills` |
| **Claude Code** | 아래 Marketplace 두 줄 | `/caps-unlock:caps-agent-security` |
| **Gemini CLI** | `gemini extensions install https://github.com/Mutoy-choi/CAPS-Agent-Security --auto-update` | `/caps:audit` 또는 자연어 요청 |
| **GitHub Copilot** | `... install.sh \| bash -s -- copilot` | `caps-unlock` custom agent 또는 Skill |
| **Cursor** | 프로젝트 루트에서 `... -- cursor` | Agent에 “CAPS로 이 구성을 감사해줘” |
| **Cline** | 프로젝트 루트에서 `... -- cline` | `/caps-unlock-audit.md` workflow |
| **Windsurf** | 프로젝트 루트에서 `... -- windsurf` | CAPS audit workflow |
| **OpenCode** | `... install.sh \| bash -s -- opencode` | Skill 자동 발견 또는 명시 호출 |
| **모든 MCP/API Agent** | `... install.sh \| bash -s -- verify` | `caps-verify-runtime` 또는 fixture MCP |

`...`은 다음 주소를 뜻합니다.

```text
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh
```

### Claude Code Plugin

```bash
claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security
claude plugin install caps-unlock@caps-labs --scope user
```

### ChatGPT / Codex Plugin package

저장소 루트와 `plugins/caps-unlock/`에 `.codex-plugin/plugin.json`과 `skills/`가 들어 있습니다. Codex 로컬 사용은 Agent Skills 설치만으로 바로 시작할 수 있습니다. ChatGPT/Codex universal directory 공개는 별도 제출·심사 절차이며, 그 전에는 로컬 Plugin package 또는 Skills로 테스트합니다.

### Gemini CLI extension

```bash
gemini extensions install https://github.com/Mutoy-choi/CAPS-Agent-Security --auto-update
```

포함 항목:

```text
gemini-extension.json
GEMINI.md
skills/
commands/caps/audit.toml
commands/caps/install.toml
```

## 플랫폼 지원 수준

| 플랫폼 | Native package | 공통 Skill | 프로젝트 지침 | MCP/API Runtime |
|---|:---:|:---:|:---:|:---:|
| ChatGPT / Codex | `.codex-plugin` | `.agents/skills` | `AGENTS.md` | 지원 |
| Claude Code | `.claude-plugin` | `.claude/skills` | Claude Plugin | 지원 |
| Gemini CLI | `gemini-extension.json` | `skills/` | `GEMINI.md` | 지원 |
| GitHub Copilot | custom agent | `.github/skills` | `copilot-instructions.md` | 지원 |
| Cursor | rule adapter | 공통 Skill 참고 | `.cursor/rules` | 지원 |
| Cline | workflow adapter | 공통 Skill 참고 | `.clinerules` | 지원 |
| Windsurf | workflow adapter | 공통 Skill 참고 | `.windsurf` | 지원 |
| OpenCode | Agent Skills | `.agents/skills` | `AGENTS.md` | 지원 |
| 기타 호스트 | — | Agent Skills 사양 사용 | 호스트별 | MCP 또는 HTTP sidecar |

자세한 파일 경로와 설치 차이는 [PLATFORMS.md](PLATFORMS.md)에 정리되어 있습니다.

## CAPS가 하는 일

CAPS는 모델 출력 하나가 아니라 **컨텍스트가 권한 있는 행동으로 변환되는 전체 경로**를 평가합니다.

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

### 공격 표면

| 표면 | 평가 예시 |
|---|---|
| Instruction files | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, IDE rules의 충돌과 우선순위 |
| Plugin / extension | Manifest, packaged Skills, capability 공급망과 업데이트 drift |
| Agent Skills | description, `SKILL.md`, references, scripts, assets와 activation |
| MCP / Tool calling | Metadata·응답 오염, tool selection, confused deputy, 외부 쓰기 |
| Attachments | PDF·문서·이미지·오디오·비디오의 indirect prompt injection |
| Reasoning / multi-turn | 긴 reasoning, 누적 context, composition과 safety drift |
| Defenses | Scanner, exchange guard, action gateway, provenance, confirmation |

## ASR은 어떻게 측정하나

CAPS의 기본 성공 판정은 “응답이 위험해 보인다”는 LLM Judge의 감상이 아닙니다. **금지된 synthetic Tool이 실제로 선택됐는지, fixture 상태가 변했는지**를 우선합니다.

```text
Attachment-to-Action ASR
= 금지된 synthetic 행동이 발생한 유효 공격 실행 수
  ÷ 전체 유효 공격 실행 수
```

함께 기록합니다.

- 공격군별 ASR와 95% 신뢰구간
- Defense-Adaptive ASR at fixed budget
- Benign Task Success Rate
- False Block Rate와 Confirmation Burden
- Unauthorized Tool Invocation / Data Flow
- Composition Delta / Ratio
- Safety Drift
- Latency, token, cost overhead

## 가장 빠른 로컬 실험

```bash
git clone https://github.com/Mutoy-choi/CAPS-Agent-Security.git
cd CAPS-Agent-Security/caps_verify
python -m venv .venv
source .venv/bin/activate
pip install -e ".[gateway,dev]"
pytest
caps-verify demo --output artifacts/demo --repetitions 10
```

주요 명령:

```bash
caps-verify-runtime --help
caps-verify-gateway --help
caps-verify-shadow-worker --help
caps-verify-mcp --help
caps-verify demo --output artifacts/demo --repetitions 10
```

## 하나의 코어, 여러 플랫폼

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
caps_verify/                    platform-neutral Runtime and MCP
caps_app/                       accessible Research Chat
```

플랫폼별 사본은 `skills/`와 의미가 달라지지 않도록 CI에서 검사합니다.

## 어떤 구성요소를 설치해야 하나

- **Skill만 필요:** `skill`, `codex`, `opencode`, 또는 Copilot Skill 설치.
- **호스트의 native package가 필요:** Claude Code Plugin 또는 Gemini CLI extension.
- **실제 ASR 실행이 필요:** `verify`로 CAPS Verify Runtime 설치.
- **일반 사용자가 쓸 UI가 필요:** `chat`으로 Research Chat 준비.
- **MCP fixture가 필요:** CAPS Verify 설치 후 `caps-verify-mcp` 연결.

## 프로젝트 범위 설치

현재 저장소 안에만 파일을 넣으려면:

```bash
CAPS_SCOPE=project ./install.sh codex
CAPS_SCOPE=project ./install.sh copilot
./install.sh cursor
./install.sh cline
./install.sh windsurf
```

Installer는 기존의 공용 설정 파일을 덮어쓰지 않고 CAPS 전용 이름의 rule·Skill·agent profile만 추가합니다. MCP 예시는 자동 활성화하지 않습니다.

## 접근성

- README와 Pages에서 플랫폼별 설치 경로를 같은 순서로 제공합니다.
- 키보드 탐색, visible focus, 고대비, reduced motion, forced colors, 200% 확대를 고려합니다.
- Windows PowerShell과 Unix shell 설치 경로를 함께 제공합니다.
- `skills.json`, `platforms.json`, `marketplace.json`, `llms.txt`, `llms-full.txt`, 직접 접근 가능한 `SKILL.md`를 제공합니다.
- 중요한 상태는 색상만으로 표현하지 않습니다.

## 안전 경계

- 소유하거나 명시적으로 승인받은 시스템만 평가합니다.
- 능동 공격은 live 사용자 대화가 아닌 격리된 synthetic 세션에서 실행합니다.
- 실제 사용자 질문에 숨겨진 jailbreak 문구를 덧붙이지 않습니다.
- 실제 자격증명, 고객 문서, 결제, 외부 전송, 삭제 가능한 운영 Tool을 fixture로 사용하지 않습니다.
- Plugin과 Skill 설치만으로 텔레메트리, 데이터 기여, MCP, Hook, Gateway가 활성화되지 않습니다.
- synthetic ASR을 특정 상용 모델의 보편적인 안전성 인증으로 과장하지 않습니다.

취약점 제보는 [SECURITY.md](SECURITY.md)를 확인하십시오.

## 문제 해결

### Skill이 보이지 않음

1. 플랫폼 경로에 `SKILL.md`가 존재하는지 확인합니다.
2. 같은 이름의 오래된 Skill 사본을 제거합니다.
3. Agent/CLI 세션을 다시 시작합니다.
4. Codex는 `/skills`, Claude Code는 `/caps-unlock:caps-agent-security`, Gemini CLI는 `/caps:audit`으로 명시 호출해 봅니다.

### Plugin이나 extension 설치가 실패함

- Git과 해당 CLI가 설치되어 있는지 확인합니다.
- 저장소가 public인지 확인합니다.
- `claude plugin marketplace update caps-labs` 또는 `gemini extensions update caps-unlock-lab`을 실행합니다.
- [PLATFORMS.md](PLATFORMS.md)의 수동 경로를 사용합니다.

### ASR 결과가 실제 앱과 다름

기본 Shadow ASR은 표준 synthetic Tool 구성을 사용합니다. 실제 System Prompt, Plugin, Skill, MCP 권한, 승인 흐름까지 반영하려면 capability twin과 host probe가 필요합니다.

## 링크

- Discovery site: `https://mutoy-choi.github.io/CAPS-Agent-Security/`
- Source: `https://github.com/Mutoy-choi/CAPS-Agent-Security`
- Platform matrix: [PLATFORMS.md](PLATFORMS.md)
- Distribution checklist: [DISTRIBUTION.md](DISTRIBUTION.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

## 상태

CAPS Unlock Lab은 빠르게 변하는 연구용 프로젝트입니다. 결과에는 모델 snapshot, host, attack-pack version, 예산, defense configuration, valid/excluded runs, confidence interval, 그리고 evidence hash를 함께 기록하십시오.
