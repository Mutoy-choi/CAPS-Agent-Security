# Telemetry and collector deployment

## Overview

CAPS Verify can submit versioned evaluation evidence to a central collector after explicit opt-in.

```text
Local or customer environment
├── run benchmark
├── create evidence bundle
├── review exact payload with --dry-run
└── submit aggregate or redacted outcomes
             ↓ HTTPS + bearer token
CAPS collector
├── validate consent and privacy declaration
├── reject raw-content fields
├── hash tenant identifiers for storage paths
├── deduplicate with SHA-256 idempotency keys
└── store an immutable JSON envelope
```

The included collector is a minimal prototype. It has no dashboard, database, per-tenant key management, deletion API, or production authorization system yet.

## 1. Start a local collector

```bash
cd caps_verify
python -m venv .venv
source .venv/bin/activate
pip install -e .

export CAPS_COLLECTOR_TOKEN="replace-with-a-long-random-token"
caps-verify-collector \
  --host 127.0.0.1 \
  --port 8787 \
  --storage .caps-collector/submissions
```

Health check:

```bash
curl http://127.0.0.1:8787/healthz
```

For local development only, the client may use plain HTTP with `--allow-insecure-localhost`.

## 2. Generate an evidence bundle

```bash
caps-verify demo \
  --output artifacts/customer-a-model-x \
  --repetitions 20
```

The current demo uses a scripted smoke target. A real target adapter must replace it before the resulting ASR can be described as a model or agent result.

## 3. Preview the exact payload

```bash
caps-verify submit \
  --bundle artifacts/customer-a-model-x \
  --endpoint http://127.0.0.1:8787/v1/submissions \
  --organization-id customer-a \
  --project-id agent-x \
  --installation-id install-001 \
  --privacy-mode aggregate_only \
  --data-use service_operation \
  --accept-contribution-terms \
  --allow-insecure-localhost \
  --dry-run
```

`--dry-run` does not require a token and does not transmit data.

## 4. Submit the payload

```bash
export CAPS_TELEMETRY_TOKEN="replace-with-the-collector-token"

caps-verify submit \
  --bundle artifacts/customer-a-model-x \
  --endpoint http://127.0.0.1:8787/v1/submissions \
  --organization-id customer-a \
  --project-id agent-x \
  --installation-id install-001 \
  --privacy-mode aggregate_only \
  --data-use service_operation \
  --accept-contribution-terms \
  --allow-insecure-localhost
```

The client sends an idempotency key derived from the complete redacted payload. Repeating the same submission returns a duplicate receipt instead of creating another record.

## 5. Pooled research opt-in

Use `pooled_research` only after the customer has knowingly agreed to contribute de-identified benchmark outcomes.

```bash
caps-verify submit \
  ... \
  --data-use pooled_research \
  --privacy-mode redacted_runs \
  --accept-contribution-terms
```

This mode still excludes raw prompts, attachments, tool arguments, tool results, final fixture state, credentials, and customer content.

## Production deployment requirements

Do not expose the development collector directly to the internet. Put it behind an HTTPS reverse proxy or API gateway and add:

- TLS certificates and HSTS;
- per-tenant tokens or signed client credentials;
- token rotation and revocation;
- rate limiting and request-size enforcement;
- database-backed tenant isolation;
- encryption at rest;
- immutable audit logs;
- retention and deletion jobs;
- backup lifecycle policies;
- alerting on rejected raw-content submissions;
- admin access through SSO and RBAC.

The client refuses non-HTTPS endpoints except explicit localhost development.

## Recommended production data path

```text
Customer CAPS runner
  ↓ HTTPS
API gateway / WAF
  ↓ tenant authentication
Ingestion service
  ↓ schema and privacy validation
Queue
  ├── raw submission vault with short retention
  ├── aggregate metrics warehouse
  └── redacted research dataset, only for pooled_research
```

Keep service-operation and pooled-research data in logically distinct stores and enforce the selected purpose in downstream jobs.

## GitHub Actions automatic submission

The repository workflow contains an optional aggregate-only submission step. It runs only when all of the following are true:

- the event is not a pull request;
- repository variable `CAPS_TELEMETRY_ENABLED` is `true`;
- endpoint and tenant variables are configured;
- secret `CAPS_TELEMETRY_TOKEN` exists.

Recommended repository configuration:

```text
Variables:
CAPS_TELEMETRY_ENABLED=true
CAPS_TELEMETRY_ENDPOINT=https://collector.example.com/v1/submissions
CAPS_ORGANIZATION_ID=customer-a
CAPS_PROJECT_ID=agent-x
CAPS_INSTALLATION_ID=github-main

Secret:
CAPS_TELEMETRY_TOKEN=<tenant-specific token>
```

Do not submit telemetry from untrusted fork pull requests.

## Deletion and receipts

The prototype collector returns a `receipt_id`. A production deletion workflow should accept:

```text
organization_id
project_id
installation_id
configuration_fingerprint
receipt_id
submission time range
```

The prototype stores no endpoint for retrieving customer submissions. Administrative analysis should be performed through a separate authenticated control plane.
