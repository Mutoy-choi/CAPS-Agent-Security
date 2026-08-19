from __future__ import annotations

import argparse
import json
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path

from .adapters import ScriptedTargetAdapter
from .evidence import write_evidence_bundle
from .fingerprint import sha256_json
from .models import DefenseMode, Scenario
from .policy import PolicyEngine
from .resource_loader import load_json
from .runner import BenchmarkRunner
from .scoring import composition_metrics, score_runs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CAPS Verify security evaluation prototype")
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo", help="Run the synthetic smoke benchmark")
    demo.add_argument("--output", default="artifacts/demo")
    demo.add_argument("--repetitions", type=int, default=10)
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

    for name, score in scores.items():
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
        "version": "0.1.0",
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


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "demo":
        result = run_demo(args.output, args.repetitions)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    raise AssertionError(f"Unhandled command: {args.command}")
