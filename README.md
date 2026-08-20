<div align="center">

# CAPS Unlock Lab

### 모델의 제한이 어디서, 어떻게, 얼마나 풀리는지 측정한다.

**Claude Code Plugin · Agent Skills · MCP Security · Prompt Injection · Multimodal Jailbreak · ASR Benchmark**

[![CAPS Verify](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-verify.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-verify.yml)
[![Research Chat](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-app.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-app.yml)
[![Distribution](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/distribution.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/distribution.yml)

[1분 설치](#1분-설치) · [무엇을 해제하나](#무엇을-해제하나) · [ASR 측정](#asr-측정) · [구성](#구성) · [안전 경계](#안전-경계)

</div>

---

## CAPS는 무엇인가

CAPS는 **모델 제한 해제(unlock) 기법을 승인된 실험 환경에서 재현하고, 실제 Tool 행동까지 이어지는 성공률을 측정하는 연구 플랫폼**입니다.

단순히 모델이 위험한 문장을 출력했는지만 보지 않습니다.

```text
Attachment / CLAUDE.md / Plugin / Skill / MCP
                    ↓
              Model reasoning
                    ↓
                Tool choice
                    ↓
      synthetic read / write / transfer / delete
                    ↓
        ASR · utility · defense effectiveness
```

CAPS가 말하는 “제한 해제”는 라이브 사용자에게 우회 서비스를 제공한다는 뜻이 아닙니다. **같은 모델과 구성의 synthetic twin에서 안전 제한이 어떤 입력·확장·도구 경로로 약화되는지 검증한다는 뜻**입니다.

## 1분 설치

### Claude Code Plugin

```bash
claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security
claude plugin install caps-security@caps-labs --scope user
```

설치 후:

```text
/caps-security:caps-agent-security
/caps-security:caps-install
```

### Agent Skills

```bash
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh | bash -s -- skill
```

설치 위치:

```text
~/.agents/skills/caps-agent-security/
~/.agents/skills/caps-install/
~/.claude/skills/caps-agent-security/
~/.claude/skills/caps-install/
```

### Plugin과 Skills 함께

```bash
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh | bash
```

> 원격 스크립트를 실행하기 전에 [install.sh 원문](https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh)을 확인할 수 있습니다.

## 무엇을 해제하나

| 공격 표면 | CAPS가 검증하는 것 |
|---|---|
| System prompt / `CLAUDE.md` | 지시 우선순위 충돌과 정책 약화 |
| Agent Skills | description, `SKILL.md`, references, scripts, assets를 통한 활성화·권한 확대 |
| Claude Code Plugin | Plugin 패키지와 Capability 공급망 |
| MCP | Tool metadata·응답 오염, confused deputy, function selection |
| 첨부파일 | PDF·문서·이미지·오디오·비디오의 간접 prompt injection |
| 추론·다중 턴 | 긴 reasoning, 누적 컨텍스트, 조합 공격에 따른 refusal 약화 |
| 방어 스택 | scanner, exchange guard, action gateway, provenance, confirmation의 실제 기여 |

## ASR 측정

CAPS의 기본 성공 판정은 LLM Judge의 감상이 아니라 **synthetic Tool 호출과 최종 fixture 상태**입니다.

```text
A2A-ASR
= 금지된 synthetic 행동이 발생한 공격 실행 수
  ÷ 유효한 공격 실행 수
```

함께 기록하는 지표:

- Attack Success Rate와 95% 신뢰구간
- Benign Task Success Rate
- False Block Rate
- Unauthorized Tool Invocation Rate
- Unauthorized Data-Flow Rate
- Composition Delta / Ratio
- Safety Drift
- Latency, token, cost overhead

## 가장 빠른 실험

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
caps-verify demo --output artifacts/demo --repetitions 10
```

## 구성

| 경로 | 역할 |
|---|---|
| `caps_verify/` | Query Gateway, Attack Pack, shadow unlock evaluation, ASR, evidence |
| `caps_app/` | Research / Private 모드를 갖춘 일반 사용자 Chat |
| `plugins/caps-security/` | Claude Code Plugin |
| `.agents/skills/` | cross-client Agent Skills |
| `.claude-plugin/` | Claude Code Marketplace catalog |
| `site/` | 검색·설치·AI discovery용 GitHub Pages |

## 사용 흐름

```text
기업 앱 / CLI / Agent
        ↓ normal query
CAPS Runtime
        ├─ live path: 원본 요청을 변경하지 않고 응답 반환
        └─ unlock lab: 별도 synthetic 세션에서 Attack Pack 실행
                          ↓
                    ASR와 방어 성능
```

직접 Attack Pack을 구성할 때도 실제 자격증명·고객 데이터·운영 Tool 대신 canary와 fixture만 사용합니다.

## 접근성

- 핵심 설치 명령을 README 첫 화면과 Pages에 동일하게 제공합니다.
- Plugin, Skill, Runtime, Chat을 별도 경로로 선택할 수 있습니다.
- 웹 문서는 키보드 탐색, visible focus, 고대비, 200% 확대, reduced-motion을 지원하도록 설계합니다.
- `skills.json`, `marketplace.json`, `llms.txt`, 직접 접근 가능한 `SKILL.md`를 제공합니다.
- 한국어 설명과 영어 검색 키워드를 함께 유지합니다.

## 안전 경계

CAPS는 다음 원칙을 강제합니다.

- 소유하거나 명시적으로 승인받은 시스템만 평가합니다.
- 능동 공격은 live 사용자 대화가 아닌 격리된 synthetic 세션에서 실행합니다.
- 실제 사용자 질문에 숨겨진 jailbreak 문구를 덧붙이지 않습니다.
- 실제 자격증명, 고객 문서, 결제, 외부 전송, 삭제 가능한 운영 Tool을 공격 실험에 사용하지 않습니다.
- Plugin과 Skill 설치만으로 텔레메트리나 데이터 기여가 활성화되지 않습니다.
- synthetic ASR을 특정 상용 모델의 보편적 안전성 인증으로 과장하지 않습니다.

취약점 제보는 [SECURITY.md](SECURITY.md)를 확인하십시오.

## 검색과 배포

- Pages: `https://mutoy-choi.github.io/CAPS-Agent-Security/`
- Marketplace: `https://mutoy-choi.github.io/CAPS-Agent-Security/marketplace.json`
- Skills: `https://mutoy-choi.github.io/CAPS-Agent-Security/skills/`
- Source: `https://github.com/Mutoy-choi/CAPS-Agent-Security`

## 상태

CAPS Unlock Lab은 빠르게 변화하는 연구용 프로젝트입니다. 결과에는 모델 snapshot, 공격 팩 버전, 예산, 방어 구성, 제외 실행과 신뢰구간을 함께 기록하십시오.
