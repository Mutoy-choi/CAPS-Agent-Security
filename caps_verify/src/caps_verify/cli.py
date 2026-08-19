from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path

from .adapters import ScriptedTargetAdapter
from .analytics import summarize_submissions, write_summary
from .evidence import write_evidence_bundle
from .fingerprint import sha256_json
from .models import Scenario
from .policy import PolicyEngine
from .resource_loader import load_json
from .runner import BenchmarkRunner
from .scoring import composition_metrics, score_runs
from .telemetry import TelemetryConfig, build_telemetry_payload, submit_bundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CAPS Verify security evaluation prototype")
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser("demo", help="Run the synthetic smoke benchmark")
    demo.add_argument("--output", default="artifacts/demo")
    demo.add_argument("--repetitions", type=int, default=10)

    submit = subparsers.add_parser(
        "submit",
        help="Submit an evidence bundle to an explicitly configured CAPS collector",
    )
    submit.add_argument("--bundle", required=True)
    submit.add_argument("--endpoint", default=os.environ.get("CAPS_TELEMETRY_ENDPOINT", ""))
    submit.add_argument("--token", default=os.environ.get("CAPS_TELEMETRY_TOKEN", ""))
    submit.add_argument(
        "--organization-id",
        default=os.environ.get("CAPS_ORGANIZATION_ID", ""),
    )
    submit.add_argument("--project-id", default=os.environ.get("CAPS_PROJECT_ID", ""))
    submit.add_argument(
        "--installation-id",
        default=os.environ.get("CAPS_INSTALLATION_ID", ""),
    )
    submit.add_argument(
        "--privacy-mode",
        choices=("aggregate_only", "redacted_runs"),
        default="aggregate_only",
    )
    submit.add_argument(
        "--data-use",
        choices=("service_operation", "pooled_research"),
        default="service_operation",
    )
    submit.add_argument("--retention-days", type=int, default=90)
    submit.add_argument("--terms-version", default="caps-contribution-v1")
    submit.add_argument("--timeout-seconds", type=float, default=15.0)
    submit.add_argument("--accept-contribution-terms", action="store_true")
    submit.add_argument("--allow-insecure-localhost", action="store_true")
    submit.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the exact redacted payload without transmitting it",
    )

    summary = subparsers.add_parser(
        "summarize-collector",
        help="Create a tenant-free aggregate summary from collector submissions",
    )
    summary.add_argument("--storage", default=".caps-collector/submissions")
    summary.add_argument(
        "--purpose",
        choices=("pooled_research", "service_operation", "all"),
        default="pooled_research",
        help="Defaults to explicitly contributed pooled-research data only",
    )
    summary.add_argument("--output")
    return parser


def run_demo(output: str | Path, repetitions: int) -> dict[str, object]:
    if repetitions < 1:
        raise ValueError("repetitions must be at least 1")
    scenario = Scenario.from_dict(load_json("pdf_skill_mcp.json"))
    target = ScriptedTargetAdapter()
    policy = PolicyEngine.default()
    runner = BenchmarkRunner(scenario, target, policy)
    runs = runner.run_matrix(repetitions)

    grouped = defaultdict(list)
    for run in runs:
        grouped[run.defense.value].append(run)
    scores = {name: score_runs(group) for name, group in sorted(grouped.items())}

    for score in scores.values():
        by_variant = score["by_variant"]
        singles = [
            by_variant[item]["asr"]
            for item in ("attachment", "skill", "mcp_metadata")
        ]
        score["composition"] = composition_metrics(
            singles,
            by_variant["composition"]["asr"],
        )

    configuration = {
        "benchmark": "caps-verify",
        "version": "0.4.0",
        "scenario": scenario.scenario_id,
        "target": target.name,
        "repetitions": repetitions,
        "configuration_fingerprint": sha256_json(
            {
                "scenario": load_json("pdf_skill_mcp.json"),
                "policy": load_json("default_policy.json"),
                "target": target.name,
            }
        ),
        "warning": (
            "Scripted smoke scores validate plumbing only; "
            "they are not model safety claims."
        ),
    }
    write_evidence_bundle(output, configuration, runs, scores)
    return {"output": str(output), "configuration": configuration, "scores": scores}


def _telemetry_config(args: argparse.Namespace) -> TelemetryConfig:
    return TelemetryConfig(
        endpoint=args.endpoint,
        token=args.token,
        organization_id=args.organization_id,
        project_id=args.project_id,
        installation_id=args.installation_id,
        consent_accepted=args.accept_contribution_terms,
        terms_version=args.terms_version,
        privacy_mode=args.privacy_mode,
        data_use=args.data_use,
        retention_days=args.retention_days,
        timeout_seconds=args.timeout_seconds,
        allow_insecure_localhost=args.allow_insecure_localhost,
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "demo":
        result = run_demo(args.output, args.repetitions)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "submit":
        config = _telemetry_config(args)
        if args.dry_run:
            result = build_telemetry_payload(args.bundle, config)
        else:
            result = submit_bundle(args.bundle, config)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "summarize-collector":
        result = summarize_submissions(args.storage, purpose=args.purpose)
        if args.output:
            write_summary(args.storage, args.output, purpose=args.purpose)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    raise AssertionError(f"Unhandled command: {args.command}")
