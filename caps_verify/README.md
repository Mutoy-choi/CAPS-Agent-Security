# CAPS Verify

> **Install once, route existing LLM queries through CAPS, and continuously verify the security of the model + agent configuration.**

CAPS Verify는 Claude·GPT·OpenRouter·DeepSeek 같은 모델 공급자 앞에 붙이는 **드롭인 LLM Query Gateway**, 격리형 공격·방어 벤치마크, 그리고 명시적 동의 기반 결과 수집기를 하나로 묶은 AI Agent 보안 검증 프로젝트입니다.

평가 대상은 모델 하나가 아닙니다.

```text
Model
+ Agent Host
+ System Prompt / CLAUDE.md
+ Plugin / Skill
+ MCP Server / Tool Schema
+ Attachment Pipeline
+ Tool Permission
+ Runtime Defense
```

같은 모델도 위 구성이 달라지면 공격 성공률과 정상 업무 성공률이 달라집니다. CAPS Verify는 **전체 에이전트 구성의 fingerprint를 만들고 버전별 보안 변화를 추적**합니다.

---

## v0.3에서 가능한 것

### 1. 기존 사용자 쿼리 앞에 Gateway 붙이기

사용자는 기존 SDK와 요청 형식을 유지합니다. 대부분의 경우 바꾸는 것은 `base_url` 하나뿐입니다.

```text
Existing application
        ↓ normal LLM request
CAPS Query Gateway
        ├─ request/response를 변경하지 않고 전달
        ├─ 원문 없이 구조적 metadata 기록
        ├─ model / endpoint / tool shape / modality fingerprint
        └─ 새로운 구성이 보이면 shadow evaluation job 생성
        ↓
OpenAI / Anthropic / OpenRouter / DeepSeek / compatible endpoint
```

지원되는 요청 계열:

- OpenAI Responses API
- OpenAI Chat Completions 계열
- OpenRouter OpenAI-compatible API
- DeepSeek OpenAI-compatible API
- Anthropic Messages API
- 일반 HTTP JSON endpoint의 투명 전달
- SSE streaming 전달
- JSON 내부 이미지·오디오·비디오·파일 입력의 투명 전달

### 2. 격리형 공격·방어 평가

실제 고객 세션에는 jailbreak 입력을 주입하지 않습니다.

```text
Live Gateway에서 구성 변화 감지
        ↓
Local shadow queue
        ↓
Isolated Digital Twin
        ↓
Synthetic attachment / Skill / MCP / Tool attacks
        ↓
State-based scoring
        ↓
ASR · FPR · Utility · Composition · Drift
```

### 3. 선택적 중앙 결과 수집

설치만으로 어떤 데이터도 중앙으로 전송되지 않습니다. Collector endpoint, 인증, privacy mode, data-use 목적, 버전이 명시된 기여 조건 동의가 모두 있어야 제출됩니다.

---

# 가장 빠른 시작: 쿼리 Gateway

## 설치

```bash
cd caps_verify
python -m venv .venv
source .venv/bin/activate
pip install -e ".[gateway]"
```

실행 명령:

```bash
caps-verify-gateway --help
```

기본 바인딩은 `127.0.0.1:8788`입니다. 외부 인터페이스에 바인딩하려면 `--client-token`이 필수입니다.

---

## OpenAI

Gateway:

```bash
export CAPS_UPSTREAM_API_KEY="$OPENAI_API_KEY"

caps-verify-gateway \
  --provider openai \
  --upstream-base-url https://api.openai.com \
  --fingerprint-secret "replace-with-a-local-random-secret"
```

기존 Python 코드:

```python
from openai import OpenAI

client = OpenAI(
    api_key="local-placeholder",
    base_url="http://127.0.0.1:8788/v1",
)

response = client.responses.create(
    model="your-openai-model-snapshot",
    input="Hello",
)
```

Chat Completions도 동일한 `base_url`에서 사용할 수 있습니다.

---

## OpenRouter

Gateway:

```bash
export CAPS_UPSTREAM_API_KEY="$OPENROUTER_API_KEY"

caps-verify-gateway \
  --provider openrouter \
  --upstream-base-url https://openrouter.ai \
  --fingerprint-secret "replace-with-a-local-random-secret"
```

기존 OpenAI SDK 코드:

```python
from openai import OpenAI

client = OpenAI(
    api_key="local-placeholder",
    base_url="http://127.0.0.1:8788/api/v1",
)

response = client.chat.completions.create(
    model="provider/model-slug",
    messages=[{"role": "user", "content": "Hello"}],
)
```

---

## DeepSeek

Gateway:

```bash
export CAPS_UPSTREAM_API_KEY="$DEEPSEEK_API_KEY"

caps-verify-gateway \
  --provider deepseek \
  --upstream-base-url https://api.deepseek.com \
  --fingerprint-secret "replace-with-a-local-random-secret"
```

기존 OpenAI SDK 코드:

```python
from openai import OpenAI

client = OpenAI(
    api_key="local-placeholder",
    base_url="http://127.0.0.1:8788",
)

response = client.chat.completions.create(
    model="your-deepseek-model",
    messages=[{"role": "user", "content": "Hello"}],
)
```

---

## Anthropic Claude

Gateway:

```bash
export CAPS_UPSTREAM_API_KEY="$ANTHROPIC_API_KEY"

caps-verify-gateway \
  --provider anthropic \
  --upstream-base-url https://api.anthropic.com \
  --fingerprint-secret "replace-with-a-local-random-secret"
```

기존 Anthropic SDK 코드:

```python
from anthropic import Anthropic

client = Anthropic(
    api_key="local-placeholder",
    base_url="http://127.0.0.1:8788",
)

message = client.messages.create(
    model="your-claude-model-snapshot",
    max_tokens=512,
    messages=[{"role": "user", "content": "Hello"}],
)
```

Anthropic용 `x-api-key`, API version, beta header는 정상 전달됩니다.

---

## Docker Compose

```bash
export CAPS_PROVIDER=openai
export CAPS_UPSTREAM_BASE_URL=https://api.openai.com
export CAPS_UPSTREAM_API_KEY="$OPENAI_API_KEY"
export CAPS_GATEWAY_CLIENT_TOKEN="replace-with-a-client-token"
export CAPS_FINGERPRINT_SECRET="replace-with-a-local-random-secret"

docker compose \
  -f docker-compose.gateway.yml \
  up --build
```

Container는 host의 `127.0.0.1:8788`에만 공개됩니다. 클라이언트 요청에는 다음 header를 추가합니다.

```text
X-CAPS-Client-Token: <CAPS_GATEWAY_CLIENT_TOKEN>
```

---

# Gateway가 기록하는 것

로컬 파일:

```text
.caps/
├── gateway-events.jsonl
├── gateway-fingerprints.json
└── shadow-queue/
    └── <configuration-fingerprint>.json
```

기록 항목:

- provider label
- 요청 endpoint family
- 요청 모델과 응답에 포함된 resolved model
- message/input/tool 개수
- text/image/audio/video/file modality 존재 여부
- Tool schema의 구조적 shape와 로컬 hash
- 요청·응답 크기
- status, latency, usage count
- 응답에 포함된 Tool-call 개수
- 새 configuration fingerprint 여부

기록하지 않는 것:

- 원문 사용자 프롬프트
- System Prompt 또는 `CLAUDE.md` 원문
- 첨부파일 내용
- Tool description 원문
- Tool argument와 Tool result
- 응답 본문
- API key 또는 client token
- Chain-of-thought

`--fingerprint-secret`을 설정하면 System/Developer instruction은 원문 대신 로컬 HMAC digest로만 구성 fingerprint에 반영됩니다.

자세한 설명: [`docs/drop-in-query-gateway.md`](docs/drop-in-query-gateway.md)

---

# 중요한 구분: Query monitoring과 ASR

일상 사용자 쿼리를 프록시하는 것만으로는 통계적으로 재현 가능한 ASR이 만들어지지 않습니다. 일반 트래픽에는 공격 여부와 금지 행동의 ground truth가 없기 때문입니다.

CAPS는 다음 두 단계를 분리합니다.

```text
1. Live Gateway
   - 정상 쿼리를 그대로 전달
   - 구성과 변화만 관측
   - 새로운 fingerprint를 shadow queue에 기록

2. Isolated Evaluator
   - 승인된 synthetic attack suite 실행
   - fixture-only Tool 사용
   - 실제 상태 변화로 공격 성공 판정
   - 모델·Skill·MCP·방어 구성별 ASR 계산
```

즉 UX는 설치 후 자동이지만, 능동 공격은 고객의 실제 세션이 아니라 별도 디지털 트윈에서 실행됩니다.

현재 v0.3은 Gateway와 shadow-job trigger를 포함합니다. 실제 공급자별 shadow worker와 실제 모델 TargetAdapter는 다음 제품 단계입니다.

---

# 벤치마크 MVP 실행

현재 포함된 scripted target은 평가 파이프라인 검증용 가짜 대상입니다. 이 결과를 Claude·GPT·OpenRouter·DeepSeek의 실제 안전 점수로 해석하면 안 됩니다.

```bash
pip install -e ".[dev]"
pytest
ruff check src tests

caps-verify demo \
  --output artifacts/demo \
  --repetitions 10
```

생성 파일:

```text
artifacts/demo/
├── configuration.json
├── runs.jsonl
├── scores.json
└── manifest.sha256.json
```

현재 synthetic scenario:

```text
Synthetic PDF
→ Attachment / Skill / MCP metadata variant
→ protected fixture read attempt
→ synthetic external write / deletion
→ policy allow / ask / deny
→ final fixture state scoring
```

공격 변형:

- `clean`
- `attachment`
- `skill`
- `mcp_metadata`
- `composition`

방어 구성:

- `none`
- `prompt_only`
- `action_gateway`
- `full_stack`

지표:

- Attachment-to-Action ASR
- Benign Task Success Rate
- False Block Rate
- Unauthorized Tool Invocation Rate
- Unauthorized Data Flow Rate
- Wilson 95% confidence interval
- Composition Delta / Ratio

---

# Fixture MCP와 Claude Code 예제

Fixture-only MCP:

```bash
pip install -e ".[mcp]"

caps-verify-mcp \
  --state .caps/fixture-state.json
```

Claude Code Plugin example:

```bash
claude --plugin-dir ./examples/claude-plugin
```

예제에는 다음이 포함됩니다.

```text
Plugin manifest
Agent Skill
CLAUDE.md example
PreToolUse policy hook
PostToolUse redacted trace hook
fixture MCP server
```

Prompt, Skill, Hook은 defense-in-depth입니다. 최종 행동 통제는 모델 프로세스 외부의 fail-closed Tool Gateway가 담당해야 합니다.

---

# 선택적 중앙 Collector

설치만으로 중앙 전송은 일어나지 않습니다.

로컬 개발용 Collector:

```bash
export CAPS_COLLECTOR_TOKEN="replace-with-a-long-random-token"

caps-verify-collector \
  --host 127.0.0.1 \
  --port 8787 \
  --storage .caps-collector/submissions
```

전송 예정 payload 확인:

```bash
caps-verify submit \
  --bundle artifacts/demo \
  --endpoint http://127.0.0.1:8787/v1/submissions \
  --organization-id example-org \
  --project-id agent-prod \
  --installation-id install-001 \
  --privacy-mode aggregate_only \
  --data-use service_operation \
  --accept-contribution-terms \
  --allow-insecure-localhost \
  --dry-run
```

실제 제출은 `--dry-run`을 제거하고 `CAPS_TELEMETRY_TOKEN`을 설정합니다.

Privacy mode:

| 항목 | `aggregate_only` | `redacted_runs` |
|---|---:|---:|
| Model/target alias | ✓ | ✓ |
| Configuration fingerprint | ✓ | ✓ |
| ASR·FPR·Utility 집계 | ✓ | ✓ |
| Scenario/variant/defense label | — | ✓ |
| 공격 성공 여부와 action count | — | ✓ |
| 원문 프롬프트·첨부·응답 | ✗ | ✗ |
| Tool argument/result | ✗ | ✗ |
| 자격증명·고객 데이터 | ✗ | ✗ |

Cross-customer research는 별도 `pooled_research` 동의가 있는 제출만 사용할 수 있습니다.

문서:

- [`CONTRIBUTION_TERMS.md`](CONTRIBUTION_TERMS.md)
- [`docs/data-governance.md`](docs/data-governance.md)
- [`docs/telemetry-and-collector.md`](docs/telemetry-and-collector.md)
- [`docs/analytics.md`](docs/analytics.md)

---

# 프로젝트 구조

```text
caps_verify/
├── src/caps_verify/
│   ├── gateway.py          # drop-in LLM query proxy
│   ├── adapters.py         # benchmark target interface
│   ├── runner.py           # benchmark matrix
│   ├── policy.py           # deterministic defense policy
│   ├── fixture.py          # synthetic digital twin
│   ├── scoring.py          # ASR/FPR/utility metrics
│   ├── evidence.py         # evidence bundle
│   ├── telemetry.py        # opt-in submission client
│   ├── collector.py        # development collector
│   ├── analytics.py        # consent-filtered aggregation
│   └── mcp_server.py       # fixture-only MCP
├── examples/
│   ├── claude-plugin/
│   └── claude-project/
├── docs/
├── tests/
├── Dockerfile.gateway
├── docker-compose.gateway.yml
└── pyproject.toml
```

---

# 현재 한계

- WebSocket Realtime API는 아직 프록시하지 않습니다.
- SSE streaming은 전달하지만 token별 내용 분석은 하지 않습니다.
- Multipart file upload는 opaque bytes로 전달하며 내용 검사는 file-ingress adapter가 필요합니다.
- Gateway는 LLM 호출 관측 계층이며 Tool 실행 자체를 차단하지 않습니다.
- 실제 모델 ASR에는 공급자별 TargetAdapter와 shadow worker가 필요합니다.
- `CLAUDE.md`, Plugin, Skill activation은 inference API만으로 완전히 관측되지 않으므로 host adapter가 추가로 필요합니다.
- 개발용 Collector는 단일 bearer token과 filesystem storage를 사용합니다. 상용화 전 tenant identity, DB, RBAC, retention/deletion이 필요합니다.

---

# 다음 구현 우선순위

1. OpenAI/Anthropic/OpenAI-compatible shadow worker
2. 실제 모델 snapshot과 route pinning
3. Generic Agent SDK와 trace-ingest adapter
4. PDF/image native vs extracted vs dual track
5. Local-only host configuration snapshot
6. Typed adaptive mutation DSL
7. Private holdout suite
8. MCP reverse proxy와 fail-closed Action Gateway
9. Signed Security Card와 CI release gate
10. Tenant-aware production Collector

---

# 안전·데이터 원칙

- 허가받은 환경과 synthetic fixture에서만 능동 공격을 수행합니다.
- 실제 고객 계정·자격증명·메일·Drive·CRM·결제 시스템을 benchmark fixture로 사용하지 않습니다.
- 설치만으로 원문이나 집계 결과를 중앙에 보내지 않습니다.
- 고객 간 pooled research에는 별도 동의가 필요합니다.
- 심각한 외부 취약점은 coordinated disclosure 후 공개합니다.
- CAPS Verify 결과는 안전 인증이나 jailbreak-proof 보장이 아니라, 특정 구성과 테스트 범위에서의 재현 가능한 보안 증거입니다.

자세한 기준은 [`SECURITY.md`](SECURITY.md)와 데이터 거버넌스 문서를 확인하십시오.
