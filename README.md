<div align="center">

# CAPS Unlock Lab

### 제한 해제 경로를 재현하고, 실제 행동까지 측정한다.

**ChatGPT · Codex · Claude Code · Gemini CLI · GitHub Copilot · Cursor · Cline · Windsurf · OpenCode · MCP**

[![CAPS Verify](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-verify.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-verify.yml)
[![Research Chat](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-app.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-app.yml)
[![Distribution](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/distribution.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/distribution.yml)

[내 플랫폼에서 시작](#내-플랫폼에서-시작) · [내장 연구](#기존-연구와-라이브러리를-내장) · [ASR](#asr은-어떻게-측정하나) · [구성](#하나의-코어-여러-플랫폼) · [문제 해결](#문제-해결)

</div>

---

## 한 문장으로

CAPS Unlock Lab은 **모델의 제한이 Prompt, instruction file, Plugin, Agent Skill, MCP Tool, 첨부파일, 추론 및 다중 턴 경로에서 어디까지 약해지는지 승인된 synthetic 환경에서 재현하고 ASR로 측정하는 범용 연구 도구**입니다.

CAPS는 특정 회사의 모델이나 한 가지 CLI에 종속되지 않습니다. 같은 두 개의 핵심 Skill과 CAPS Verify Runtime을 유지하고, 각 플랫폼에는 얇은 manifest·rule·agent profile만 제공합니다.

> 여기서 “unlock”은 라이브 사용자의 안전장치를 몰래 우회한다는 뜻이 아닙니다. 소유하거나 허가받은 시스템의 synthetic twin에서 제한 해제 경로를 재현하고 방어를 검증한다는 뜻입니다.
