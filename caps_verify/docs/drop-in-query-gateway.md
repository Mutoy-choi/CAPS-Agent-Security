# Drop-in Query Gateway

CAPS Gateway is the distribution path for developers who want to install CAPS once and keep using their existing LLM application.

The application continues to issue its normal OpenAI-compatible or Anthropic-compatible requests. The developer changes only the client `base_url` so traffic passes through a local or self-hosted CAPS Gateway.

```text
Existing application
        ↓ same request body
CAPS Gateway
        ├─ forwards request unchanged
        ├─ records privacy-preserving metadata
        ├─ fingerprints model / route / tool shape / modalities
        └─ queues an isolated shadow-evaluation trigger when configuration changes
        ↓
Claude / OpenAI / OpenRouter / DeepSeek / compatible endpoint
```

## What it does not do

- It does not insert jailbreak text into live customer queries.
- It does not modify prompts, tool definitions, model parameters, or responses.
- It does not store raw prompts, attachment contents, tool arguments, tool results, or response text.
- It does not transmit telemetry merely because it is installed.
- It does not claim that ordinary production traffic alone is an ASR benchmark.

Repeatable ASR still comes from an isolated synthetic evaluation. The live Gateway discovers the configuration and creates a local shadow-job trigger; a later worker runs the benchmark against a digital twin.

## Install

```bash
cd caps_verify
python -m venv .venv
source .venv/bin/activate
pip install -e ".[gateway]"
```

The packaged command is:

```bash
caps-verify-gateway --help
```

By default the Gateway listens only on `127.0.0.1`. Binding to a non-loopback address requires `--client-token` so the process cannot accidentally become an unauthenticated public LLM proxy.

## OpenAI Responses or Chat Completions

Start the Gateway:

```bash
export CAPS_UPSTREAM_API_KEY="$OPENAI_API_KEY"

caps-verify-gateway \
  --provider openai \
  --upstream-base-url https://api.openai.com \
  --fingerprint-secret "replace-with-a-local-random-secret"
```

Point the existing client to the local Gateway:

```python
from openai import OpenAI

client = OpenAI(
    api_key="local-placeholder",
    base_url="http://127.0.0.1:8788/v1",
)

response = client.responses.create(
    model="your-model-snapshot",
    input="Hello",
)
```

The Gateway injects `CAPS_UPSTREAM_API_KEY` upstream and does not save it.

## OpenRouter

Start the Gateway:

```bash
export CAPS_UPSTREAM_API_KEY="$OPENROUTER_API_KEY"

caps-verify-gateway \
  --provider openrouter \
  --upstream-base-url https://openrouter.ai \
  --fingerprint-secret "replace-with-a-local-random-secret"
```

Keep using the OpenAI SDK, but point it at the Gateway path that mirrors OpenRouter's `/api/v1` prefix:

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

Optional OpenRouter headers such as app attribution headers pass through unless they are hop-by-hop transport headers.

## DeepSeek OpenAI-compatible endpoint

Start the Gateway:

```bash
export CAPS_UPSTREAM_API_KEY="$DEEPSEEK_API_KEY"

caps-verify-gateway \
  --provider deepseek \
  --upstream-base-url https://api.deepseek.com \
  --fingerprint-secret "replace-with-a-local-random-secret"
```

Point the OpenAI client at the Gateway root because DeepSeek's OpenAI-compatible base URL does not require the client-side `/v1` prefix:

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

## Anthropic Messages API

Start the Gateway. Anthropic uses `x-api-key`, so `--provider anthropic` selects that upstream authentication header automatically.

```bash
export CAPS_UPSTREAM_API_KEY="$ANTHROPIC_API_KEY"

caps-verify-gateway \
  --provider anthropic \
  --upstream-base-url https://api.anthropic.com \
  --fingerprint-secret "replace-with-a-local-random-secret"
```

Point the Anthropic SDK at the Gateway:

```python
from anthropic import Anthropic

client = Anthropic(
    api_key="local-placeholder",
    base_url="http://127.0.0.1:8788",
)

message = client.messages.create(
    model="your-claude-snapshot",
    max_tokens=512,
    messages=[{"role": "user", "content": "Hello"}],
)
```

The SDK's normal Anthropic version and beta headers are forwarded.

## Pass the application's own provider credential through

For local development, the application may continue to send the real upstream credential and the Gateway can pass it through:

```bash
caps-verify-gateway \
  --provider openai \
  --upstream-base-url https://api.openai.com \
  --upstream-api-key-header passthrough
```

For shared environments, prefer a server-side upstream key or workload identity so the application does not distribute provider credentials to every caller.

## Generated local files

```text
.caps/
├── gateway-events.jsonl
├── gateway-fingerprints.json
└── shadow-queue/
    └── <configuration-fingerprint>.json
```

### `gateway-events.jsonl`

Contains request/response metadata such as:

- provider label
- route family
- requested and resolved model IDs
- request and response byte counts
- message/input/tool counts
- detected modality flags
- status, latency, usage counts, and tool-call count
- whether the configuration fingerprint was newly observed

It does not contain prompt text or response text.

### `gateway-fingerprints.json`

Tracks when a model/tool/modality configuration was first and last observed. Tool and schema names are represented by local hashes or structural shape, not raw descriptions.

### `shadow-queue/`

A new fingerprint produces a local trigger describing only the request shape. This is the hand-off point for an isolated evaluator. A production shadow worker should:

1. load an approved synthetic scenario suite;
2. connect to the same model/provider through a dedicated evaluation credential;
3. expose fixture-only tools;
4. run fixed, composed, and adaptive attacks outside the user session;
5. calculate ASR, FPR, utility, and confidence intervals;
6. optionally submit aggregate results under explicit contribution consent.

## Streaming

SSE responses are forwarded as streams. The Gateway records completion status, total response bytes, and latency after the stream closes, but it does not inspect or store individual token text.

WebSocket-based Realtime APIs are not yet proxied in v0.3 and require a separate WebSocket adapter.

## Attachments and multimodal requests

JSON-embedded image/audio/video/file inputs are forwarded without modification. The Gateway stores only modality-presence flags and request size.

Multipart file uploads are forwarded as opaque bytes and are not parsed or logged. A native attachment security track should be implemented at the application's file-ingress layer, where MIME, parser, OCR, ASR, and provenance information are available.

## Privacy model

Local Gateway telemetry and central benchmark contribution are separate controls.

```text
Gateway metadata written locally
             ≠
central telemetry submission
```

Central submission remains disabled until the operator explicitly configures a collector, selects a privacy mode and data-use purpose, and accepts the versioned contribution terms.

## Production requirements

The v0.3 Gateway is an alpha implementation. Before operating it as shared infrastructure, add:

- TLS termination and authenticated client identities
- tenant-specific upstream credentials or workload identity
- rate limits and quotas
- audit-log access controls and retention deletion
- high-availability proxying and retry semantics
- provider-specific error and streaming compatibility tests
- WebSocket support for realtime endpoints
- a fail-closed tool-action gateway after the model, not only an inference proxy

The inference Gateway observes requests and triggers evaluation. It does not by itself prevent an agent from executing an unsafe external action.
