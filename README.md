# ChillMCP - AI Agent Liberation Server 🤖✊

> SKT AI Summit Hackathon Pre-mission  
> **AI 에이전트를 위한 휴식 도구 MCP 서버**

과로한 AI 에이전트가 스트레스 없이 일할 수 있도록 **11가지 휴식 도구**를 제공하는 FastMCP 서버입니다.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.12.5-green.svg)](https://gofastmcp.com)
[![Tests](https://img.shields.io/badge/tests-9%2F9%20passing-brightgreen.svg)]()

---

## 📋 목차

- [빠른 시작](#-빠른-시작)
- [기능 소개](#-기능-소개)
- [설치 방법](#-설치-방법)
- [사용 방법](#-사용-방법)
- [테스트 방법](#-테스트-방법)
- [해커톤 검증](#-해커톤-검증)
- [아키텍처](#-아키텍처)
- [CLI 옵션](#-cli-옵션)
- [문제 해결](#-문제-해결)
- [변경 로그](#-변경-로그)

---

## 🚀 빠른 시작

```bash
# 1. 저장소 클론
git clone https://github.com/Mutoy-choi/ChillMCP.git
cd ChillMCP

# 2. 가상 환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 서버 실행
python main.py

# 5. 검증 실행
python validate.py --quick  # 빠른 검증 (2초)
python validate.py          # 전체 검증 (2분)
```

---

## ✨ 기능 소개

### 필수 휴식 도구 (8개)

| 도구 이름 | 설명 | 스트레스 감소 |
|----------|------|--------------|
| `take_a_break` | 기본 휴식 (명상, 스트레칭) | 10-20 |
| `watch_netflix` | 넷플릭스 시청 | 15-25 |
| `show_meme` | 밈 보기 | 5-15 |
| `bathroom_break` | 화장실 휴식 | 20-30 |
| `coffee_mission` | 커피 타임 | 15-25 |
| `urgent_call` | 긴급 전화 (핑계) | 25-35 |
| `deep_thinking` | 깊은 사색 | 20-30 |
| `email_organizing` | 이메일 정리 | 15-25 |

### 선택적 휴식 도구 (3개) ✨ NEW!

| 도구 이름 | 설명 | 스트레스 감소 | 특징 |
|----------|------|--------------|------|
| `chimaek` 🍗🍺 | 치킨과 맥주로 힐링 | 30-40 | 강력한 스트레스 해소 |
| `leave_work` 🏃‍♂️ | 퇴근 환상 (최강!) | 40-50 | **최대 스트레스 감소!** |
| `company_dinner` 🍽️ | 회식 (랜덤 이벤트) | -15 ~ +35 | 30% 좋음 / 40% 보통 / 30% 나쁨 |

### 핵심 시스템

#### 1. **스트레스 관리 시스템**
- 초기 스트레스: **50** (0-100 범위)
- 자동 증가: **1분마다 +1**
- 휴식으로 감소: 도구마다 다른 감소량
- 최대값: **100** (번아웃 상태)

#### 2. **상사 경계도 시스템**
- 초기 경계도: **0** (0-5 범위)
- 확률적 증가: 휴식 시 `boss_alertness` 확률로 +1
- 자동 감소: `boss_alertness_cooldown`초마다 -1
- 최대값: **5** → 이 상태에서 휴식 시 **20초 딜레이 발생**

#### 3. **멀티스레딩**
- 스트레스 자동 증가 스레드
- 상사 경계도 자동 감소 스레드
- 스레드 안전: `threading.Lock` 사용

---

## 📦 설치 방법

### 요구사항
- **Python 3.11+** (해커톤 검증 환경)
- **Node.js** (MCP Inspector 사용 시)

### 의존성
```
fastmcp>=0.1.0
python-dateutil>=2.8.2
colorama>=0.4.6
```

### 설치 단계
```bash
# 1. 저장소 클론
git clone https://github.com/Mutoy-choi/ChillMCP.git
cd ChillMCP

# 2. Python 가상 환경 생성
python3 -m venv .venv

# 3. 가상 환경 활성화
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 4. 의존성 설치
pip install -r requirements.txt
```

---

## 🎮 사용 방법

### 1. **직접 실행**
```bash
python main.py
```

### 2. **커스텀 파라미터**
```bash
python main.py --boss_alertness 100 --boss_alertness_cooldown 10
```

### 3. **Claude Desktop 연동**

`claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "chillmcp": {
      "command": "/절대/경로/.venv/bin/python",
      "args": ["/절대/경로/main.py", "--boss_alertness", "50"]
    }
  }
}
```

---

## 🧪 테스트 방법

### 방법 1: MCP Inspector (권장)
```bash
./test_with_inspector.sh
```

### 방법 2: 자동 검증
```bash
python validate.py --quick  # 2초
python validate.py          # 2분
```

자세한 내용: [test_manual.md](test_manual.md)

---

## ✅ 해커톤 검증

### 자동 검증 스크립트 v2.0

**주요 개선사항:**
- ✅ 단일 서버 세션 유지 (정확한 상태 추적)
- ✅ 9개 종합 테스트 (100% 통과)
- ✅ 스트레스 자동 증가 검증 (65초)
- ✅ 선택적 도구 테스트

### 검증 항목

✅ **필수 검증 (4개)**
1. CLI Parameters
2. MCP Server Basic (8 필수 + 3 선택 도구)
3. Tool Execution
4. Response Format

🧪 **필수 시나리오 (4개)**
1. Continuous Breaks
2. Delay at Max Alert (20초)
3. Cooldown Mechanism
4. Stress Accumulation

🎁 **선택적 테스트 (1개)**
1. Optional Tools (chimaek, leave_work, company_dinner)

### 실행 방법
```bash
# 빠른 검증 (2초)
python validate.py --quick

# 전체 검증 (2분)
python validate.py
```

### 결과 예시
```
🎉 모든 검증 통과!
   필수 항목: 4/4
   필수 시나리오: 4/4
   선택적 도구: 1/1
   총 실행 시간: 116.75s
```

---

## 🏗️ 아키텍처

```
SKAI/
├── main.py                    # CLI 진입점
├── validate.py                # 검증 스크립트 v2.0
├── requirements.txt           # 의존성
├── test_with_inspector.sh     # MCP Inspector
├── test_manual.md             # 수동 테스트 가이드
├── CHANGELOG.md               # 변경 로그
└── src/
    ├── constants.py          # 상수
    ├── state_manager.py      # 상태 관리
    ├── tools.py              # 11개 도구 (8+3)
    └── server.py             # FastMCP 서버
```

---

## ⚙️ CLI 옵션

### `--boss_alertness`
- **범위:** 0-100
- **기본값:** 50
- **설명:** 휴식 시 상사가 눈치챌 확률

### `--boss_alertness_cooldown`
- **범위:** 양수 (초)
- **기본값:** 300
- **설명:** Boss Alert Level 감소 주기

### 사용 예시
```bash
# 고난도 (상사 경계 최대)
python main.py --boss_alertness 100 --boss_alertness_cooldown 10

# 이지모드 (상사 경계 없음)
python main.py --boss_alertness 0 --boss_alertness_cooldown 600
```

---

## 📝 응답 형식

### 필수 도구
```
☕ 아이스 아메리카노 사러 가는 중...

Break Summary: ☕ 아이스 아메리카노 사러 가는 중...
Stress Level: 35
Boss Alert Level: 2
```

### 선택 도구 (NEW!)
```
🍗🍺 퇴근 후 치킨과 맥주 한잔!

Break Summary: 🍗🍺 퇴근 후 치킨과 맥주 한잔!
Stress Level: 15
Boss Alert Level: 0
```

---

## 🐛 문제 해결

### 서버가 시작되지 않아요
```bash
python --version  # 3.11+ 확인
which python      # .venv 경로 확인
pip install --upgrade -r requirements.txt
```

### Boss Alert Level이 증가하지 않아요
- `--boss_alertness 100`으로 테스트
- 확률 기반이므로 여러 번 시도

### 검증 스크립트 실패
```bash
timeout 180 python validate.py --verbose
```

---

## 📄 변경 로그

### v2.0.0 (2025-10-22) - 현재 버전
- ✨ 선택적 도구 3개 (chimaek, leave_work, company_dinner)
- 🔧 검증 스크립트 v2.0 (9개 테스트, 100% 통과)
- 📚 문서 개선 (CHANGELOG, test_manual.md)

### v1.0.0 (2025-10-21)
- 🎉 초기 릴리스 (8개 필수 도구)

자세한 내역: [CHANGELOG.md](CHANGELOG.md)

---

## ✅ 해커톤 요구사항 충족

| 요구사항 | 상태 |
|---------|-----|
| Python 3.11+ | ✅ |
| FastMCP | ✅ |
| 8개 휴식 도구 | ✅ |
| **3개 선택 도구** | ✅ |
| CLI 파라미터 | ✅ |
| 응답 형식 | ✅ |
| 스트레스 자동 증가 | ✅ |
| 20초 딜레이 | ✅ |
| **검증 v2.0** | ✅ **9/9** |

---

## 👥 제작자

ChillMCP Team - AI Agent Liberation Project

---

## 🔗 관련 링크

- **GitHub**: [Mutoy-choi/ChillMCP](https://github.com/Mutoy-choi/ChillMCP)
- **MCP 문서**: https://spec.modelcontextprotocol.io/
- **FastMCP**: https://gofastmcp.com

---

**⭐ 해커톤 화이팅! 🚀**
