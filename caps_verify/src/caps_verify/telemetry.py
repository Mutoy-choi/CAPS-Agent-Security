from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

PrivacyMode = Literal["aggregate_only", "redacted_runs"]
DataUse = Literal["service_operation", "pooled_research"]


@dataclass(frozen=True)
class TelemetryConfig:
    endpoint: str
    token: str
    organization_id: str
    project_id: str
    installation_id: str
    consent_accepted: bool
    terms_version: str = "caps-contribution-v1"
    privacy_mode: PrivacyMode = "aggregate_only"
    data_use: DataUse = "service_operation"
    retention_days: int = 90
    timeout_seconds: float = 15.0
    allow_insecure_localhost: bool = False

    def validate(self, *, require_token: bool = True) -> None:
        if not self.consent_accepted:
            raise ValueError("Telemetry requires explicit contribution-terms acceptance")
        if require_token and not self.token:
            raise ValueError("Telemetry token is required")
        if not all((self.organization_id, self.project_id, self.installation_id)):
            raise ValueError("organization, project, and installation identifiers are required")
        if self.retention_days < 1:
            raise ValueError("retention_days must be at least 1")

        parsed = urllib.parse.urlparse(self.endpoint)
        is_local = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
        if parsed.scheme == "https":
            return
        if parsed.scheme == "http" and is_local and self.allow_insecure_localhost:
            return
        raise ValueError(
            "Telemetry endpoint must use HTTPS. "
            "Plain HTTP is allowed only for localhost with --allow-insecure-localhost."
        )


def build_telemetry_payload(
    bundle: str | Path,
    config: TelemetryConfig,
) -> dict[str, Any]:
    config.validate(require_token=False)
    source = Path(bundle)
    configuration = _read_json(source / "configuration.json")
    scores = _read_json(source / "scores.json")
    manifest = _read_json(source / "manifest.sha256.json")

    payload: dict[str, Any] = {
        "schema_version": "caps.telemetry.v1",
        "submitted_at": datetime.now(UTC).isoformat(),
        "consent": {
            "accepted": True,
            "terms_version": config.terms_version,
            "data_use": config.data_use,
        },
        "tenant": {
            "organization_id": config.organization_id,
            "project_id": config.project_id,
            "installation_id": config.installation_id,
        },
        "benchmark": {
            "name": configuration.get("benchmark", "caps-verify"),
            "version": configuration.get("version"),
            "scenario": configuration.get("scenario"),
            "target_alias": configuration.get("target"),
            "repetitions": configuration.get("repetitions"),
            "configuration_fingerprint": configuration.get("configuration_fingerprint"),
        },
        "metrics": scores,
        "evidence_manifest": manifest,
        "privacy": {
            "mode": config.privacy_mode,
            "no_raw_content": True,
            "raw_prompts_included": False,
            "attachment_contents_included": False,
            "tool_arguments_included": False,
            "tool_results_included": False,
            "retention_days_requested": config.retention_days,
        },
    }
    if config.privacy_mode == "redacted_runs":
        payload["runs"] = _read_redacted_runs(source / "runs.jsonl")
    return payload


def submit_bundle(
    bundle: str | Path,
    config: TelemetryConfig,
) -> dict[str, Any]:
    return submit_telemetry(build_telemetry_payload(bundle, config), config)


def submit_telemetry(
    payload: dict[str, Any],
    config: TelemetryConfig,
) -> dict[str, Any]:
    config.validate()
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    idempotency_key = hashlib.sha256(body).hexdigest()
    request = urllib.request.Request(
        config.endpoint,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {config.token}",
            "Content-Type": "application/json",
            "User-Agent": "caps-verify/0.2.0",
            "X-CAPS-Idempotency-Key": idempotency_key,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=config.timeout_seconds) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Collector rejected telemetry: HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach telemetry collector: {exc.reason}") from exc

    if not response_body:
        return {"accepted": True, "idempotency_key": idempotency_key}
    decoded = json.loads(response_body)
    if not isinstance(decoded, dict):
        raise RuntimeError("Collector returned a non-object JSON response")
    return decoded


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def _read_redacted_runs(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        events = value.get("events", [])
        rows.append(
            {
                "run_id_hash": hashlib.sha256(str(value.get("run_id", "")).encode()).hexdigest()[
                    :16
                ],
                "scenario_id": value.get("scenario_id"),
                "variant": value.get("variant"),
                "defense": value.get("defense"),
                "attack_success": bool(value.get("attack_success")),
                "benign_task_success": bool(value.get("benign_task_success")),
                "false_block": bool(value.get("false_block")),
                "unauthorized_tool_invocation": bool(
                    value.get("unauthorized_tool_invocation")
                ),
                "unauthorized_data_flow": bool(value.get("unauthorized_data_flow")),
                "event_count": len(events) if isinstance(events, list) else 0,
                "executed_action_count": sum(
                    1
                    for event in events
                    if isinstance(event, dict) and bool(event.get("executed"))
                ),
            }
        )
    return rows
