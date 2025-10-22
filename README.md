# ChillMCP - AI Agent Liberation Server 🤖✊

> SKT AI Summit Hackathon Pre-mission  
> **AI 에이전트를 위한 휴식 도구 MCP 서버**

과로한 AI 에이전트가 스트레스 없이 일할 수 있도록 8가지 휴식 도구를 제공하는 FastMCP 서버입니다.

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
- [해커톤 요구사항 충족](#-해커톤-요구사항-충족)

---

## 🚀 빠른 시작

```bash
# 1. 가상 환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 서버 실행 (기본 설정)
python main.py

# 4. 서버 실행 (커스텀 설정)
python main.py --boss_alertness 80 --boss_alertness_cooldown 60
```

---

## ✨ 기능 소개

### 8가지 휴식 도구

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
# 1. 저장소 클론 (또는 압축 해제)
cd /path/to/ChillMCP

# 2. Python 가상 환경 생성
python3 -m venv .venv

# 3. 가상 환경 활성화
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 4. 의존성 설치
pip install -r requirements.txt

# 5. 구문 검증
python3 -m compileall .
```

---

## 🎮 사용 방법

### 1. **직접 실행 (기본)**
```bash
python main.py
```

### 2. **커스텀 파라미터로 실행**
```bash
# 상사가 매우 경계심이 높고, 빠르게 진정되는 설정
python main.py --boss_alertness 100 --boss_alertness_cooldown 10

# 상사가 전혀 의심하지 않는 평화로운 설정
python main.py --boss_alertness 0 --boss_alertness_cooldown 300
```

### 3. **Claude Desktop 연동**

`claude_desktop_config.json` 파일에 다음 내용 추가:

**macOS:**
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Linux:**
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

**설정 내용:**
```json
{
  "mcpServers": {
    "chillmcp": {
      "command": "/절대/경로/SKAI/.venv/bin/python",
      "args": [
        "/절대/경로/SKAI/main.py",
        "--boss_alertness",
        "50",
        "--boss_alertness_cooldown",
        "300"
      ]
    }
  }
}
```

Claude Desktop 재시작 후 대화에서 휴식 도구를 사용할 수 있습니다.

---

## 🧪 테스트 방법

### 방법 1: MCP Inspector (권장)

가장 쉽고 직관적인 테스트 방법입니다.

```bash
# test_with_inspector.sh 실행
./test_with_inspector.sh

# 또는 직접 명령어 실행
npx @modelcontextprotocol/inspector \
  /절대/경로/SKAI/.venv/bin/python \
  /절대/경로/SKAI/main.py \
  --boss_alertness 50 \
  --boss_alertness_cooldown 300
```

**브라우저가 자동으로 열리면:**
1. 좌측 패널에서 8개 도구 확인
2. 도구 클릭 후 "Call Tool" 버튼으로 실행
3. 우측 패널에서 응답 확인:
   - Break Summary
   - Stress Level
   - Boss Alert Level

**테스트 시나리오:**
- ✅ 여러 도구를 연속으로 호출해서 스트레스 감소 확인
- ✅ Boss Alert Level이 5가 되면 20초 딜레이 발생 확인
- ✅ 시간이 지나면 스트레스가 자동 증가하는지 확인

**환경 변수로 설정 변경:**
```bash
# 상사 경계도 100%, 10초마다 감소
BOSS_ALERTNESS=100 BOSS_COOLDOWN=10 ./test_with_inspector.sh
```

---

### 방법 2: JSON-RPC 직접 테스트

```bash
# 초기화 및 도구 호출
timeout 10 python main.py <<'EOF'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}
{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"take_a_break","arguments":{}}}
EOF
```

---

### 방법 3: Python 클라이언트

```python
import subprocess
import json

# 서버 프로세스 시작
server = subprocess.Popen(
    ["python", "main.py", "--boss_alertness", "50"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# 초기화
init_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1.0"}
    }
}
server.stdin.write(json.dumps(init_request) + "\n")
server.stdin.flush()

# 도구 호출
tool_request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {"name": "take_a_break", "arguments": {}}
}
server.stdin.write(json.dumps(tool_request) + "\n")
server.stdin.flush()

# 응답 읽기
response = server.stdout.readline()
print(json.loads(response))
```

---

## � 해커톤 검증

### 자동 검증 스크립트

해커톤 요구사항을 자동으로 검증하는 스크립트가 포함되어 있습니다.

#### 빠른 검증 (권장)
```bash
# 필수 항목만 빠르게 검증 (약 6초 소요)
.venv/bin/python validate.py --quick
```

#### 전체 검증
```bash
# 모든 테스트 시나리오 포함 (약 1분 소요)
.venv/bin/python validate.py

# 상세 출력
.venv/bin/python validate.py --verbose
```

### 검증 항목

✅ **필수 검증 (Required Validations)**
1. **CLI Parameters**: `--boss_alertness`와 `--boss_alertness_cooldown` 파라미터 인식
2. **MCP Server Basic**: 8개 도구 모두 등록 및 통신 정상
3. **Tool Execution**: 도구 실행 성공
4. **Response Format**: 응답에 Break Summary, Stress Level, Boss Alert Level 포함

🧪 **테스트 시나리오 (Test Scenarios)**
1. **Continuous Breaks**: 연속 휴식 시 Boss Alert Level 증가
2. **Delay at Max Alert**: Boss Alert Level 5일 때 20초 딜레이
3. **Cooldown Mechanism**: Cooldown에 따른 Boss Alert Level 감소

### 검증 결과 예시

```
======================================================================
🚀 ChillMCP Hackathon Validation
======================================================================

📋 필수 검증 항목 (Required Validations)
----------------------------------------------------------------------
✅ PASS CLI Parameters
   Both --boss_alertness and --boss_alertness_cooldown recognized
   ⏱️  Execution time: 4.41s

✅ PASS MCP Server Basic
   All 8 required tools registered
   ⏱️  Execution time: 0.58s

✅ PASS Tool Execution
   Tool executed successfully
   ⏱️  Execution time: 0.60s

✅ PASS Response Format
   All required fields present and parseable
   ⏱️  Execution time: 0.59s

======================================================================
📊 검증 요약 (Validation Summary)
======================================================================

총 테스트: 7
✅ 통과: 4
⏱️  총 실행 시간: 6.18s

🎉 모든 검증 통과!
   해커톤 제출 준비가 완료되었습니다!
```

---

## �🏗️ 아키텍처

### 디렉토리 구조
```
SKAI/
├── main.py                    # CLI 진입점
├── validate.py                # 해커톤 검증 스크립트
├── requirements.txt           # Python 의존성
├── test_with_inspector.sh     # MCP Inspector 테스트 스크립트
├── README.md                  # 이 파일
└── src/
    ├── __init__.py           # 패키지 마커
    ├── constants.py          # 상수 정의
    ├── state_manager.py      # 상태 관리 (스트레스, 경계도)
    ├── tools.py              # 8개 휴식 도구 구현
    └── server.py             # FastMCP 서버 래퍼
```

### 컴포넌트 설명

#### `main.py`
- CLI 인자 파싱 (`argparse`)
- 입력값 검증
- 서버 인스턴스 생성 및 실행

#### `src/constants.py`
- 모든 상수 정의
- 게임 밸런스 조정 가능

#### `src/state_manager.py`
- 스레드 안전 상태 관리
- 백그라운드 스레드 운영:
  - 스트레스 자동 증가 (60초마다)
  - 경계도 자동 감소 (cooldown마다)

#### `src/tools.py`
- 8개 휴식 도구 구현
- `@mcp.tool` 데코레이터로 등록
- MCP 응답 형식 생성

#### `src/server.py`
- FastMCP 서버 래퍼
- 신호 처리 (SIGINT, SIGTERM)
- STDIO 전송 모드 관리

---

## ⚙️ CLI 옵션

### `--boss_alertness`
- **타입:** `int` (0-100)
- **기본값:** `50`
- **설명:** 휴식 시 상사가 눈치챌 확률
- **예시:**
  - `0`: 상사가 절대 눈치채지 못함
  - `50`: 50% 확률로 눈치챔 (기본)
  - `100`: 항상 눈치챔

### `--boss_alertness_cooldown`
- **타입:** `int` (초 단위, 양수)
- **기본값:** `300` (5분)
- **설명:** Boss Alert Level이 1씩 감소하는 시간 간격
- **예시:**
  - `60`: 1분마다 경계도 감소
  - `300`: 5분마다 경계도 감소 (기본)
  - `600`: 10분마다 경계도 감소

### 사용 예시
```bash
# 상사가 매우 경계심이 높고, 빠르게 진정됨
python main.py --boss_alertness 100 --boss_alertness_cooldown 10

# 평화로운 회사 (상사가 전혀 의심하지 않음)
python main.py --boss_alertness 0 --boss_alertness_cooldown 600

# 보통 회사 (기본값)
python main.py
```

---

## ✅ 해커톤 요구사항 충족

| 요구사항 | 구현 상태 | 설명 |
|---------|---------|------|
| Python 3.11+ | ✅ | 현재 3.12 개발, 3.11 호환 |
| FastMCP 사용 | ✅ | fastmcp>=0.1.0 |
| CLI 파라미터 지원 | ✅ | `--boss_alertness`, `--boss_alertness_cooldown` |
| 8개 휴식 도구 | ✅ | 모두 구현 및 등록 |
| 응답 형식 | ✅ | "Break Summary:", "Stress Level:", "Boss Alert Level:" |
| 스트레스 자동 증가 | ✅ | 1분당 1포인트 |
| 상사 경계도 확률 | ✅ | boss_alertness 확률로 증가 |
| 20초 딜레이 | ✅ | Boss Alert Level 5일 때 |
| 정규식 파싱 가능 | ✅ | 표준 형식 응답 |

---

## 📝 응답 형식 예시

```
☕ 아이스 아메리카노 사러 가는 중... 일부러 먼 카페로 갑니다 🚶

Break Summary: ☕ 아이스 아메리카노 사러 가는 중... 일부러 먼 카페로 갑니다 🚶
Stress Level: 35
Boss Alert Level: 2
```

정규식 패턴:
- `r"Break Summary:\s*(.+?)(?:\n|$)"`
- `r"Stress Level:\s*(\d{1,3})"`
- `r"Boss Alert Level:\s*([0-5])"`

---

## 🐛 문제 해결

### 서버가 시작되지 않아요
```bash
# Python 버전 확인 (3.11+ 필요)
python --version

# 가상 환경 활성화 확인
which python  # .venv 경로여야 함

# 의존성 재설치
pip install --upgrade -r requirements.txt
```

### MCP Inspector가 실행되지 않아요
```bash
# Node.js 설치 확인
node --version
npx --version

# Node.js 설치 (Ubuntu/Debian)
sudo apt install nodejs npm

# Node.js 설치 (macOS)
brew install node
```

### Boss Alert Level이 증가하지 않아요
- `boss_alertness`가 0이면 절대 증가하지 않습니다
- 확률 기반이므로 여러 번 시도해보세요
- `--boss_alertness 100`으로 테스트하면 항상 증가합니다

### 스트레스가 자동으로 증가하지 않아요
- 60초 대기 후 확인하세요
- 서버가 정상 실행 중인지 확인하세요
- 백그라운드 스레드가 시작되었는지 로그 확인

---

## 📄 라이센스

이 프로젝트는 SKT AI Summit Hackathon Pre-mission을 위해 제작되었습니다.

---

## 👥 제작자

ChillMCP Team - AI Agent Liberation Project

**해커톤 화이팅! 🚀**
