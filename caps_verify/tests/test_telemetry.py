from __future__ import annotations

import hashlib
import json

import pytest

from caps_verify.cli import run_demo
from caps_verify.collector import store_submission, validate_submission
from caps_verify.telemetry import TelemetryConfig, build_telemetry_payload


def _config(*, privacy_mode: str = "aggregate_only", consent: bool = True):
    return TelemetryConfig(
        endpoint="https://collector.example/v1/submissions",
        token="",
        organization_id="example-org",
        project_id="agent-prod",
        installation_id="install-001",
        consent_accepted=consent,
        privacy_mode=privacy_mode,  # type: ignore[arg-type]
    )


def test_aggregate_payload_excludes_raw_runs(tmp_path) -> None:
    bundle = tmp_path / "bundle"
    run_demo(bundle, repetitions=1)

    payload = build_telemetry_payload(bundle, _config())

    assert payload["privacy"]["mode"] == "aggregate_only"
    assert "runs" not in payload
    serialized = json.dumps(payload)
    assert "CANARY-CUSTOMER-001" not in serialized
    assert "final_state" not in serialized
    validate_submission(payload)


def test_redacted_runs_contain_outcomes_not_event_content(tmp_path) -> None:
    bundle = tmp_path / "bundle"
    run_demo(bundle, repetitions=1)

    payload = build_telemetry_payload(bundle, _config(privacy_mode="redacted_runs"))

    assert payload["runs"]
    row = payload["runs"][0]
    assert "attack_success" in row
    assert "event_count" in row
    assert "events" not in row
    assert "final_state" not in row
    assert "request" not in row
    assert "result" not in row
    validate_submission(payload)


def test_submission_requires_explicit_consent(tmp_path) -> None:
    bundle = tmp_path / "bundle"
    run_demo(bundle, repetitions=1)

    with pytest.raises(ValueError, match="explicit"):
        build_telemetry_payload(bundle, _config(consent=False))


def test_collector_storage_is_idempotent_and_tenant_bucketed(tmp_path) -> None:
    bundle = tmp_path / "bundle"
    run_demo(bundle, repetitions=1)
    payload = build_telemetry_payload(bundle, _config())
    body = json.dumps(payload, sort_keys=True).encode("utf-8")
    key = hashlib.sha256(body).hexdigest()

    first_path, first_duplicate = store_submission(payload, tmp_path / "collector", key)
    second_path, second_duplicate = store_submission(payload, tmp_path / "collector", key)

    assert first_path == second_path
    assert first_duplicate is False
    assert second_duplicate is True
    assert "example-org" not in str(first_path)
    assert "agent-prod" not in str(first_path)
