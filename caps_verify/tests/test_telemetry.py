from __future__ import annotations

import hashlib
import json
from threading import Thread

import pytest

from caps_verify.cli import run_demo
from caps_verify.collector import build_server, store_submission, validate_submission
from caps_verify.telemetry import (
    TelemetryConfig,
    build_telemetry_payload,
    submit_bundle,
)


def _config(
    *,
    privacy_mode: str = "aggregate_only",
    consent: bool = True,
    endpoint: str = "https://collector.example/v1/submissions",
    token: str = "",
    allow_insecure_localhost: bool = False,
):
    return TelemetryConfig(
        endpoint=endpoint,
        token=token,
        organization_id="example-org",
        project_id="agent-prod",
        installation_id="install-001",
        consent_accepted=consent,
        privacy_mode=privacy_mode,  # type: ignore[arg-type]
        allow_insecure_localhost=allow_insecure_localhost,
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


def test_bundle_reaches_local_collector_and_returns_receipt(tmp_path) -> None:
    bundle = tmp_path / "bundle"
    storage = tmp_path / "collector"
    run_demo(bundle, repetitions=1)

    server = build_server("127.0.0.1", 0, storage, token="test-secret")
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_address[1]
        receipt = submit_bundle(
            bundle,
            _config(
                endpoint=f"http://127.0.0.1:{port}/v1/submissions",
                token="test-secret",
                allow_insecure_localhost=True,
            ),
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert receipt["accepted"] is True
    assert receipt["duplicate"] is False
    assert receipt["receipt_id"]
    assert len(list(storage.rglob("*.json"))) == 1
