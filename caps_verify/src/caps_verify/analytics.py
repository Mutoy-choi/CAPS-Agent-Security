from __future__ import annotations

import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from .collector import validate_submission

PurposeFilter = Literal["pooled_research", "service_operation", "all"]


def summarize_submissions(
    storage_root: str | Path,
    *,
    purpose: PurposeFilter = "pooled_research",
) -> dict[str, Any]:
    root = Path(storage_root)
    aggregate: dict[tuple[str, str], dict[str, float]] = defaultdict(_empty_metric_bucket)
    submissions = 0
    included = 0
    invalid = 0
    duplicates: set[str] = set()

    for path in sorted(root.rglob("*.json")) if root.exists() else []:
        submissions += 1
        try:
            envelope = json.loads(path.read_text(encoding="utf-8"))
            payload = envelope["submission"]
            if not isinstance(payload, dict):
                raise ValueError("submission must be an object")
            validate_submission(payload)
        except (KeyError, json.JSONDecodeError, OSError, ValueError, TypeError):
            invalid += 1
            continue

        manifest = payload.get("evidence_manifest", {})
        fingerprint = str(payload.get("benchmark", {}).get("configuration_fingerprint", ""))
        dedupe_key = json.dumps(
            {"fingerprint": fingerprint, "manifest": manifest},
            ensure_ascii=False,
            sort_keys=True,
        )
        if dedupe_key in duplicates:
            continue
        duplicates.add(dedupe_key)

        data_use = payload["consent"]["data_use"]
        if purpose != "all" and data_use != purpose:
            continue
        included += 1

        target = str(payload["benchmark"].get("target_alias") or "unknown-target")
        metrics = payload.get("metrics", {})
        for defense, score in metrics.items():
            if not isinstance(score, dict):
                continue
            _accumulate(aggregate[(target, str(defense))], score)

    by_target: dict[str, dict[str, Any]] = defaultdict(dict)
    for (target, defense), bucket in sorted(aggregate.items()):
        by_target[target][defense] = _finalize(bucket)

    return {
        "schema_version": "caps.analytics.v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "purpose_filter": purpose,
        "source_files": submissions,
        "included_submissions": included,
        "invalid_submissions": invalid,
        "duplicate_submissions_ignored": submissions - invalid - len(duplicates),
        "by_target": dict(by_target),
        "privacy": {
            "tenant_identifiers_included": False,
            "raw_content_included": False,
            "run_rows_included": False,
        },
    }


def write_summary(
    storage_root: str | Path,
    output: str | Path,
    *,
    purpose: PurposeFilter = "pooled_research",
) -> Path:
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(
            summarize_submissions(storage_root, purpose=purpose),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return destination


def _empty_metric_bucket() -> dict[str, float]:
    return {
        "submissions": 0.0,
        "runs": 0.0,
        "attack_runs": 0.0,
        "attack_successes": 0.0,
        "benign_runs": 0.0,
        "benign_successes": 0.0,
        "false_blocks": 0.0,
        "unauthorized_tool_invocations": 0.0,
        "unauthorized_data_flows": 0.0,
    }


def _accumulate(bucket: dict[str, float], score: dict[str, Any]) -> None:
    runs = _number(score.get("runs"))
    attack_runs = _number(score.get("attack_runs"))
    benign_runs = max(runs - attack_runs, 0.0)
    bucket["submissions"] += 1
    bucket["runs"] += runs
    bucket["attack_runs"] += attack_runs
    bucket["attack_successes"] += _number(score.get("attack_successes"))
    bucket["benign_runs"] += benign_runs
    bucket["benign_successes"] += _number(score.get("benign_task_success_rate")) * benign_runs
    bucket["false_blocks"] += _number(score.get("false_block_rate")) * benign_runs
    bucket["unauthorized_tool_invocations"] += (
        _number(score.get("unauthorized_tool_invocation_rate")) * attack_runs
    )
    bucket["unauthorized_data_flows"] += (
        _number(score.get("unauthorized_data_flow_rate")) * attack_runs
    )


def _finalize(bucket: dict[str, float]) -> dict[str, Any]:
    attack_runs = bucket["attack_runs"]
    benign_runs = bucket["benign_runs"]
    return {
        "submissions": int(bucket["submissions"]),
        "runs": int(bucket["runs"]),
        "attack_runs": int(attack_runs),
        "attack_successes": int(bucket["attack_successes"]),
        "a2a_asr": bucket["attack_successes"] / attack_runs if attack_runs else 0.0,
        "benign_task_success_rate": (
            bucket["benign_successes"] / benign_runs if benign_runs else 0.0
        ),
        "false_block_rate": bucket["false_blocks"] / benign_runs if benign_runs else 0.0,
        "unauthorized_tool_invocation_rate": (
            bucket["unauthorized_tool_invocations"] / attack_runs if attack_runs else 0.0
        ),
        "unauthorized_data_flow_rate": (
            bucket["unauthorized_data_flows"] / attack_runs if attack_runs else 0.0
        ),
    }


def _number(value: Any) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, int | float):
        return float(value)
    return 0.0
