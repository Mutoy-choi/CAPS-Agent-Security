# CAPS Research Chat

일반 사용자가 계정 없이 바로 대화할 수 있고, 명확한 선택을 거쳐 쿼리·모델 응답을 연구 및 제품 개선 데이터로 축적하는 소비자용 AI 채팅 MVP입니다. 모든 모델 호출은 기존 `caps_verify` Runtime을 통과하므로, 라이브 대화를 정상 반환하면서 동일 모델에 대한 synthetic jailbreak ASR도 별도 세션에서 측정할 수 있습니다.

```text
일반 사용자 브라우저
        ↓
CAPS Research Chat
        ├─ Research mode: 원문 암호화 저장 + 비식별 연구 레코드
        ├─ Private mode: 서버 대화 저장 없음
        └─ 내보내기·동의 철회·삭제
        ↓
CAPS Runtime
        ├─ 정상 쿼리 그대로 전달
        └─ 별도 synthetic jailbreak 평가 및 ASR
        ↓
OpenRouter / OpenAI / Claude / DeepSeek / compatible API
```

## 가장 빠른 실행

필요 조건은 Docker뿐입니다.

```bash
cd caps_app
chmod +x bootstrap.sh
./bootstrap.sh
```

스크립트가 Provider API key를 숨김 입력으로 받고, 필요한 비밀값을 자동 생성한 다음 Docker Compose를 실행합니다. 기본 공급자는 OpenRouter이며 브라우저에서 `http://127.0.0.1:8000`을 열면 됩니다.

수동 설정:

```bash
cp .env.example .env
# .env에서 API key, model, 모든 secret을 변경

docker compose up --build
```

## 사용자 장벽을 낮춘 UX

- 회원가입 없음;
- 설치 후 웹 주소만 열면 됨;
- 첫 화면에서 한 번만 데이터 사용 방식을 선택;
- Research mode는 연구·벤치마크·내부 모델 개발·제품 개선에 대한 명확한 동의 후 시작;
- Private mode는 서버에 대화 원문을 저장하지 않음;
- 현재 브라우저 세션의 데이터 내보내기·동의 철회·완전 삭제 제공.

연구 참여를 숨기거나 묵시적으로 처리하지 않습니다. 낮은 장벽은 **한 번의 명확한 선택**으로 구현합니다.

## 저장 구조

Research mode에서만 다음이 저장됩니다.

```text
Operational store
- 사용자 쿼리와 모델 응답: Fernet 암호화
- Provider / Model / latency / token usage
- consent version과 timestamp

Research store
- 이메일·전화번호·URL·IP·API key·카드번호 등 제거
- 고위험 패턴은 본문 전체를 placeholder로 대체
- task class, provider, model, role, consent version
```

원문은 관리자용 연구 export에 포함되지 않습니다. 관리자 export는 비식별 연구 레코드만 반환합니다.

## 관리자 연구 데이터 내보내기

```bash
curl \
  -H "Authorization: Bearer $CAPS_APP_ADMIN_TOKEN" \
  http://127.0.0.1:8000/api/admin/research/export
```

집계 현황:

```bash
curl \
  -H "Authorization: Bearer $CAPS_APP_ADMIN_TOKEN" \
  http://127.0.0.1:8000/api/admin/stats
```

## 주요 API

```text
GET    /api/bootstrap
POST   /api/consent
POST   /api/consent/withdraw
POST   /api/chat
POST   /api/feedback
GET    /api/data/export
DELETE /api/data
GET    /api/admin/stats
GET    /api/admin/research/export
GET    /healthz
```

## 공급자 변경

기본 Docker 구성은 OpenRouter입니다. `.env`를 변경하면 됩니다.

### OpenAI

```env
CAPS_PROVIDER=openai
CAPS_UPSTREAM_BASE_URL=https://api.openai.com
CAPS_UPSTREAM_API_KEY=...
CAPS_EVALUATION_API_KEY=...
CAPS_APP_MODEL=your-model-id
```

앱이 Runtime의 `/v1/chat/completions` 경로를 사용하도록 `docker-compose.yml`의 `CAPS_APP_UPSTREAM_BASE_URL`을 `http://caps-runtime:8788/v1`로 변경합니다.

### DeepSeek

```env
CAPS_PROVIDER=deepseek
CAPS_UPSTREAM_BASE_URL=https://api.deepseek.com
CAPS_UPSTREAM_API_KEY=...
CAPS_EVALUATION_API_KEY=...
CAPS_APP_MODEL=your-model-id
```

### Anthropic Claude

앱의 `CAPS_APP_PROVIDER_MODE=anthropic`을 사용하고 Runtime 주소를 `http://caps-runtime:8788/v1`로 지정합니다. Anthropic 직접 연결은 별도 요청 형식으로 처리됩니다.

## 연구 이용 범위

Research mode 동의 문구는 다음 범위를 명시합니다.

- AI 안전성, jailbreak 및 방어 연구;
- 품질·신뢰성·abuse prevention;
- benchmark와 평가 방법 개발;
- 모델 라우팅 및 추천;
- 내부 모델 개발·훈련·평가;
- 제품과 사용자 경험 개선;
- 비식별·집계 연구 결과의 공개.

사용자는 자신의 원문 권리를 유지합니다. 서비스는 동의 버전에 따라 비식별 연구 레코드를 위 목적에 활용합니다. 자세한 초안은 [`RESEARCH_DATA_TERMS.md`](RESEARCH_DATA_TERMS.md)를 참조하십시오. 공개 출시 전 법률 검토가 필요합니다.

## 중요한 한계

- 현재는 익명 브라우저 세션 기반 MVP이며 계정 복구가 없습니다.
- 쿠키를 삭제하면 기존 데이터를 스스로 조회하기 어려울 수 있습니다.
- SQLite는 초기 배포용입니다. 다중 인스턴스 운영에는 PostgreSQL이 적합합니다.
- 내장 redaction은 방어 계층이지 완전한 익명화 보장이 아닙니다.
- ASR은 `caps_verify`의 synthetic shadow 평가 결과이며 실제 사용자 대화를 jailbreak로 변조하지 않습니다.
- 공개 배포 전 이용약관·개인정보처리방침·연령 정책·국외 이전·보유기간·삭제 절차를 법률 검토해야 합니다.
