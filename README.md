# CAPS Agent Security

**Claude Code Plugin Marketplace · Agent Skills · MCP Security · LLM Jailbreak & Prompt-Injection Benchmark**

CAPS는 Claude Code, MCP 기반 에이전트, Agent Skills, Plugin, `CLAUDE.md`, 멀티모달 첨부파일을 대상으로 **승인된 synthetic 환경에서 ASR·정상 업무 성공률·방어 효과를 측정하는 AI 에이전트 보안 도구 모음**입니다.

[![CAPS Verify](https://github.com/Mutoy-choi/ChillMCP/actions/workflows/caps-verify.yml/badge.svg)](https://github.com/Mutoy-choi/ChillMCP/actions/workflows/caps-verify.yml)
[![Distribution](https://github.com/Mutoy-choi/ChillMCP/actions/workflows/distribution.yml/badge.svg)](https://github.com/Mutoy-choi/ChillMCP/actions/workflows/distribution.yml)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-5c6ac4)](https://agentskills.io/)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin%20Marketplace-d97757)](https://code.claude.com/docs/en/plugin-marketplaces)

## 60초 설치

### Claude Code Plugin

```bash
claude plugin marketplace add Mutoy-choi/ChillMCP
claude plugin install caps-security@caps-labs --scope user
```

Claude Code 안에서는 다음 Skill을 직접 실행할 수 있습니다.

```text
/caps-security:caps-agent-security
/caps-security:caps-install
```

### 모든 Agent Skills 호환 클라이언트

```bash
curl -fsSL https://mutoy-choi.github.io/ChillMCP/install.sh | bash -s -- skill
```

이 명령은 다음 두 위치에 Skill을 설치합니다.

```text
~/.agents/skills/     # cross-client Agent Skills convention
~/.claude/skills/     # Claude compatibility
```

### Plugin + Skills 한 번에

```bash
curl -fsSL https://mutoy-choi.github.io/ChillMCP/install.sh | bash
```

스크립트를 실행하기 전에 [내용을 먼저 확인](https://mutoy-choi.github.io/ChillMCP/install.sh)할 수 있습니다.

> 현재 저장소는 private입니다. 외부 사용자가 검색·설치하려면 PR을 `main`에 병합한 뒤 저장소 또는 별도 배포 저장소를 public으로 공개하고 GitHub Pages를 활성화해야 합니다. Private 상태에서는 `gh auth login` 등 Git 인증 권한이 있는 사용자만 설치할 수 있습니다.

## 무엇을 설치하나

| 패키지 | 역할 |
|---|---|
| `caps-security` Claude Code Plugin | Agent security audit와 설치 Skill 제공 |
| `caps-agent-security` Agent Skill | MCP·Plugin·Skill·prompt injection·첨부파일 위험 평가 절차 |
| `caps-install` Agent Skill | CAPS Verify Runtime 또는 CAPS Research Chat 설치·업데이트 |
| `caps_verify/` | Query Gateway, synthetic shadow jailbreak ASR, evidence bundle |
| `caps_app/` | 동의 기반 일반 사용자 Research Chat 및 비식별 연구 데이터 파이프라인 |

## 검색 가능한 주요 분야

CAPS는 다음 검색어와 사용 사례를 명시적으로 지원합니다.

- Claude Code plugin marketplace
- Agent Skills install and discovery
- MCP security, tool poisoning, function hijacking
- LLM jailbreak benchmark and attack success rate (ASR)
- prompt injection and indirect prompt injection
- AI agent security and tool-use security
- `CLAUDE.md`, Plugin, Skill, MCP supply-chain review
- PDF, image, audio, video attachment security
- continuous AI red teaming and defense evaluation
- 한국어 LLM 탈옥·프롬프트 인젝션·MCP 보안 벤치마크

## 빠른 사용

### 보안 평가 코어

```bash
cd caps_verify
python -m venv .venv
source .venv/bin/activate
pip install -e ".[gateway,dev]"
pytest
caps-verify demo --output artifacts/demo --repetitions 10
```

### 일반 사용자 Research Chat

```bash
cd caps_app
./bootstrap.sh
```

브라우저에서 `http://127.0.0.1:8000`을 엽니다.

## 설치 경로

### GitHub Marketplace

```bash
claude plugin marketplace add Mutoy-choi/ChillMCP
claude plugin install caps-security@caps-labs
```

### Pages Marketplace URL

```bash
claude plugin marketplace add https://mutoy-choi.github.io/ChillMCP/marketplace.json
claude plugin install caps-security@caps-labs
```

### Project scope

```bash
CAPS_SCOPE=project ./install.sh all
```

## 보안 및 데이터 원칙

- Plugin과 Skill 설치만으로 중앙 텔레메트리가 활성화되지 않습니다.
- 실제 사용자 쿼리에 jailbreak 문구를 몰래 삽입하지 않습니다.
- 능동 공격 평가는 승인된 별도 synthetic 세션과 fixture Tool에서 실행합니다.
- Research Chat의 연구 데이터 활용은 첫 화면에서 명확히 선택하며 철회·삭제 경로를 제공합니다.
- 실제 자격증명, 고객 문서, 결제 정보, 운영 Tool을 공격 실험에 사용하지 않습니다.

## 배포 및 검색 노출

- Claude Code Marketplace: [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)
- Claude Code Plugin: [`plugins/caps-security`](plugins/caps-security)
- Cross-client Skills: [`.agents/skills`](.agents/skills)
- 검색 랜딩 사이트: [`site/`](site)
- 설치 스크립트: [`install.sh`](install.sh)
- 인용 메타데이터: [`CITATION.cff`](CITATION.cff), [`codemeta.json`](codemeta.json)
- 공개 체크리스트: [`DISTRIBUTION.md`](DISTRIBUTION.md)

## 프로젝트 구조

```text
.claude-plugin/             Claude Code marketplace catalog
plugins/caps-security/      installable Claude Code plugin
.agents/skills/             cross-client Agent Skills
site/                       GitHub Pages discovery and install site
caps_verify/                security evaluation runtime
caps_app/                   consumer research chat
src/                        original ChillMCP server
```

## Legacy ChillMCP

이 저장소는 원래 SKT AI Summit용 **ChillMCP AI Agent Liberation Server**로 시작했습니다. 기존 FastMCP 휴식 도구 서버 코드는 `main.py`, `src/`, `validate.py`에 그대로 유지됩니다.

## 상태

현재 모든 신규 기능은 Draft PR에서 개발 중입니다. 실제 특정 모델에 대한 ASR 수치는 synthetic fixture 파이프라인 검증치와 구분해야 하며, 외부 안전성 인증으로 해석해서는 안 됩니다.
