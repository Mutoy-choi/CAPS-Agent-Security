# CAPS Agent Security Plugin

Claude Code용 AI 에이전트 보안 Plugin입니다. 설치 후 두 개의 Skill이 제공됩니다.

```text
/caps-security:caps-agent-security
/caps-security:caps-install
```

## 설치

```bash
claude plugin marketplace add Mutoy-choi/ChillMCP
claude plugin install caps-security@caps-labs --scope user
```

또는 Pages Marketplace를 사용할 수 있습니다.

```bash
claude plugin marketplace add https://mutoy-choi.github.io/ChillMCP/marketplace.json
claude plugin install caps-security@caps-labs --scope user
```

## Skill

### `caps-agent-security`

MCP 서버, Tool metadata, Plugin, Agent Skill, `CLAUDE.md`, 간접 프롬프트 인젝션, 멀티모달 첨부파일과 jailbreak 방어를 승인된 synthetic 환경에서 평가합니다.

### `caps-install`

CAPS Verify Runtime 또는 CAPS Research Chat을 로컬에 설치·업데이트하고 필요한 실행 명령을 안내합니다.

## 신뢰 경계

이 Plugin은 설치만으로 Hook, MCP 서버, 텔레메트리 또는 네트워크 서비스를 자동 실행하지 않습니다. 설치·평가·데이터 제출은 사용자 또는 조직 관리자의 명시적 작업으로만 이루어집니다.
