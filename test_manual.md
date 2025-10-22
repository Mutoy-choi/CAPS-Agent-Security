# ChillMCP 서버 수동 테스트 가이드

## 🔍 MCP 서버 작동 원리

MCP 서버는 **JSON-RPC 2.0** 프로토콜을 사용하여 stdin/stdout으로 통신합니다.

### 메시지 흐름

```
클라이언트                                     서버
   |                                           |
   |  1. initialize 요청                        |
   |------------------------------------------>|
   |                                           |
   |  <-- 서버 정보 (name, version, tools)      |
   |<------------------------------------------|
   |                                           |
   |  2. tools/list 요청                        |
   |------------------------------------------>|
   |                                           |
   |  <-- 도구 목록 (8개 필수 + 3개 선택)         |
   |<------------------------------------------|
   |                                           |
   |  3. tools/call 요청 (도구명: take_a_break)  |
   |------------------------------------------>|
   |                                           |
   |  <-- 실행 결과 (스트레스 감소, Boss Alert 등)|
   |<------------------------------------------|
   |                                           |
```

## 🧪 수동 테스트 방법

### 방법 1: 직접 JSON-RPC 메시지 보내기

서버를 실행한 상태에서, **새 터미널**에서 다음을 입력:

```bash
# 서버 실행 (터미널 1)
cd ~/SKAI
source .venv/bin/activate
python main.py --boss_alertness 50 --boss_alertness_cooldown 10
```

그런 다음 **stdin으로 직접 메시지** 입력:

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}
```

**Enter를 두 번** 누르면 서버가 응답을 반환합니다.

### 방법 2: Python 스크립트로 테스트

```python
import subprocess
import json

# 서버 시작
process = subprocess.Popen(
    ['python', 'main.py', '--boss_alertness', '50', '--boss_alertness_cooldown', '10'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Initialize 요청
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

# 메시지 전송
process.stdin.write(json.dumps(init_request) + '\n')
process.stdin.flush()

# 응답 읽기
response = process.stdout.readline()
print("서버 응답:", response)
```

### 방법 3: MCP Inspector (가장 쉬움) ✨

```bash
./test_with_inspector.sh
```

브라우저가 열리면:
1. 좌측에 **Tools** 목록 표시
2. 도구 클릭 → **Execute** 버튼
3. 결과 확인

## 📋 테스트 시나리오

### 시나리오 1: 기본 휴식
1. `take_a_break` 도구 실행
2. 결과 확인:
   ```
   Break Summary: 잠깐 쉬었습니다
   Stress Level: 40 (50 → 40, -10)
   Boss Alert Level: 0
   ```

### 시나리오 2: 연속 휴식 (Boss Alert 증가)
1. `take_a_break` 5회 연속 실행
2. Boss Alert Level이 증가하는지 확인 (0 → 1 → 2 → ...)

### 시나리오 3: 최대 경계 상태
1. Boss Alert Level을 5까지 올림
2. 다음 휴식 시 **20초 딜레이** 발생 확인

### 시나리오 4: 선택 도구
1. `chimaek` (치맥): 스트레스 -30~40
2. `leave_work` (퇴근): 스트레스 -40~50 (최강!)
3. `company_dinner` (회식): 랜덤 이벤트

## 🔄 자동 검증

모든 시나리오를 자동으로 테스트:

```bash
# 빠른 검증 (시간 소요 시나리오 제외)
python validate.py --quick

# 전체 검증 (2분 소요)
python validate.py
```

## 🛑 서버 종료

서버를 실행한 터미널에서:
- **Ctrl+C** 누르기
- 또는 클라이언트에서 연결 종료

## 📚 추가 정보

- **MCP 공식 문서**: https://spec.modelcontextprotocol.io/
- **FastMCP 문서**: https://gofastmcp.com
- **JSON-RPC 2.0 스펙**: https://www.jsonrpc.org/specification
