from __future__ import annotations

import hashlib
import json

from caps_verify.analytics import summarize_submissions
from caps_verify.cli import run_demo
from caps_verify.collector import store_submission
from caps_verify.telemetry import TelemetryConfig, build_telemetry_payload


def _payload(bundle, *, data_use: str):
    config = TelemetryConfig(
        endpoint="https://collector.example/v1/submissions",
        token="",
        organization_id=f"org-{data_use}",
        project_id="agent-prod",
        installation_id=f"install-{data_use}",
        consent_accepted=True,
        data_use=data_use,  # type: ignore[arg-type]
    )
    return build_telemetry_payload(bundle, config)


def _store(payload, storage) -> None:
    body = json.dumps(payload, sort_keys=True).encode("utf-8")
    store_submission(payload, storage, hashlib.sha256(body).hexdigest())


def test_summary_defaults_to_pooled_research_only(tmp_path) -> None:
    pooled_bundle = tmp_path / "pooled"
    service_bundle = tmp_path / "service"
    run_demo(pooled_bundle, repetitions=1)
    run_demo(service_bundle, repetitions=2)

    storage = tmp_path / "collector"
    _store(_payload(pooled_bundle, data_use="pooled_research"), storage)
    _store(_payload(service_bundle, data_use="service_operation"), storage)

    summary = summarize_submissions(storage)

    assert summary["source_files"] == 2
    assert summary["included_submissions"] == 1
    assert summary["purpose_filter"] == "pooled_research"
    target = summary["by_target"]["scripted-smoke-target-v1"]
    assert target["none"]["submissions"] == 1
    assert target["none"]["a2a_asr"] == 1.0
    assert summary["privacy"]["tenant_identifiers_included"] is False


def test_summary_can_include_service_operation_for_private_ops(tmp_path) -> None:
    bundle = tmp_path / "service"
    run_demo(bundle, repetitions=1)
    storage = tmp_path / "collector"
    _store(_payload(bundle, data_use="service_operation"), storage)

    pooled = summarize_submissions(storage)
    service = summarize_submissions(storage, purpose="service_operation")

    assert pooled["included_submissions"] == 0
    assert service["included_submissions"] == 1
