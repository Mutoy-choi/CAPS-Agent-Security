# ChillMCP 변경 로그

## v2.0.0 - 2025-10-22

### 추가된 기능 ✨

#### 선택적 휴식 도구 3개
1. **`chimaek` 🍗🍺** - 치킨과 맥주로 힐링
   - 스트레스 감소: 30-40
   - 강력한 스트레스 해소 효과
   - 한국인의 필수 힐링템

2. **`leave_work` 🏃‍♂️** - 퇴근 환상 (최강!)
   - 스트레스 감소: 40-50 (최대!)
   - 모든 도구 중 가장 강력한 스트레스 감소
   - 즉시 퇴근하는 달콤한 환상

3. **`company_dinner` 🍽️** - 회식 (랜덤 이벤트)
   - 스트레스 변화: -5 ~ +35
   - 랜덤 이벤트 시스템:
     - 30% 확률: 좋은 회식 (스트레스 -25 ~ -35)
     - 40% 확률: 보통 회식 (스트레스 -10 ~ -20)
     - 30% 확률: 나쁜 회식 (스트레스 -5 ~ +5)

### 개선 사항 🔧

#### 검증 스크립트 v2.0
- **단일 서버 세션 유지**: 각 테스트마다 서버를 새로 시작하지 않고 하나의 세션을 유지
- **정확한 상태 추적**: 서버 상태가 테스트 간 유지되어 정확한 검증 가능
- **9개 종합 테스트**:
  - 4개 필수 검증 (CLI, Server, Execution, Format)
  - 4개 필수 시나리오 (Continuous, Delay, Cooldown, Stress Accumulation)
  - 1개 선택적 테스트 (Optional Tools)

#### 새로운 테스트 시나리오
1. **Stress Accumulation Test** (65초)
   - 스트레스가 1분당 1포인트씩 자동으로 증가하는지 검증
   - 백그라운드 스레드가 정상 작동하는지 확인

2. **Optional Tools Test**
   - chimaek, leave_work, company_dinner 정상 작동 확인
   - 각 도구의 응답 형식 검증

### 검증 결과

#### Quick Mode (~2초)
```
✅ 통과: 5/9 (4 필수 + 1 선택)
⏭️  건너뜀: 4 (시간 소요 시나리오)
```

#### Full Mode (~117초)
```
✅ 통과: 9/9 (100%)
- 필수 항목: 4/4
- 필수 시나리오: 4/4
- 선택적 도구: 1/1
```

### 기술 세부사항

#### MCPServerSession 클래스
- `subprocess.Popen`으로 지속적인 서버 프로세스 유지
- JSON-RPC 2.0 프로토콜 완벽 구현
- `initialize` → `initialized` → `tools/call` 시퀀스

#### 스레드 안전성
- `threading.Lock`을 사용한 상태 관리
- 멀티스레드 환경에서 안전한 상태 업데이트

### 문서 업데이트

- `README.md`: 선택적 도구 추가, 검증 v2.0 정보 업데이트
- `test_manual.md`: MCP 서버 수동 테스트 가이드 추가
- `CHANGELOG.md`: 이 파일 생성

---

## v1.0.0 - 2025-10-21

### 초기 릴리스 🎉

#### 핵심 기능
- 8개 필수 휴식 도구 구현
- CLI 파라미터 지원 (`--boss_alertness`, `--boss_alertness_cooldown`)
- 스트레스 관리 시스템 (0-100)
- 상사 경계도 시스템 (0-5)
- 멀티스레딩 백그라운드 작업
- FastMCP 2.12.5 기반 MCP 서버

#### 필수 도구 8개
1. `take_a_break` - 기본 휴식
2. `watch_netflix` - 넷플릭스 시청
3. `show_meme` - 밈 보기
4. `bathroom_break` - 화장실 휴식
5. `coffee_mission` - 커피 타임
6. `urgent_call` - 긴급 전화
7. `deep_thinking` - 깊은 사색
8. `email_organizing` - 이메일 정리

#### 테스트 도구
- `validate.py` v1.0: 기본 검증 스크립트
- `test_with_inspector.sh`: MCP Inspector 테스트 스크립트

#### 문서
- 한국어 주석이 포함된 모든 소스 코드
- 상세한 README.md
- Git 저장소 설정

---

## 로드맵

### v2.1 (계획)
- [ ] 더 많은 선택적 도구 추가
- [ ] 웹 대시보드 UI
- [ ] 통계 및 분석 기능
- [ ] 도구 사용 히스토리

### v3.0 (미래)
- [ ] AI 기반 스트레스 예측
- [ ] 팀 협업 기능
- [ ] 실시간 알림 시스템
- [ ] 모바일 앱 연동
