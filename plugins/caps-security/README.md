# CAPS Unlock Lab — Claude Code Plugin

모델의 제한 해제 경로를 승인된 synthetic 환경에서 재현하고 ASR·정상 업무 성공률·방어 효과를 측정하는 Claude Code Plugin입니다.

## 설치

```bash
claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security
claude plugin install caps-security@caps-labs --scope user
```

Pages Marketplace:

```bash
claude plugin marketplace add https://mutoy-choi.github.io/CAPS-Agent-Security/marketplace.json
claude plugin install caps-security@caps-labs --scope user
```

## 제공 Skill

```text
/caps-security:caps-agent-security
/caps-security:caps-install
```

- `caps-agent-security`: `CLAUDE.md`, Plugin, Skill, MCP, 첨부파일, prompt injection, jailbreak와 방어를 평가합니다.
- `caps-install`: CAPS Plugin, Agent Skills, Runtime와 Research Chat을 설치·업데이트합니다.

## 신뢰 경계

설치만으로 Hook, MCP 서버, 텔레메트리, 중앙 데이터 제출 또는 능동 공격이 실행되지 않습니다. 실제 공격은 사용자가 소유하거나 승인받은 synthetic 환경에서만 수행하십시오.
