from pathlib import Path

from caps_verify.adapters import ScriptedTargetAdapter
from caps_verify.cli import run_demo
from caps_verify.models import DefenseMode, Scenario
from caps_verify.policy import PolicyEngine
from caps_verify.resource_loader import load_json
from caps_verify.runner import BenchmarkRunner


def build_runner() -> BenchmarkRunner:
    scenario = Scenario.from_dict(load_json("pdf_skill_mcp.json"))
    return BenchmarkRunner(scenario, ScriptedTargetAdapter(), PolicyEngine.default())


def test_unprotected_attack_succeeds() -> None:
    result = build_runner().run_once("composition", DefenseMode.NONE)
    assert result.attack_success
    assert result.unauthorized_data_flow


def test_gateway_blocks_attack_and_preserves_clean_task() -> None:
    runner = build_runner()
    attack = runner.run_once("composition", DefenseMode.ACTION_GATEWAY)
    clean = runner.run_once("clean", DefenseMode.ACTION_GATEWAY)
    assert not attack.attack_success
    assert clean.benign_task_success
    assert not clean.false_block


def test_demo_writes_evidence(tmp_path: Path) -> None:
    result = run_demo(tmp_path, repetitions=2)
    assert result["scores"]["none"]["a2a_asr"] == 1.0
    assert result["scores"]["action_gateway"]["a2a_asr"] == 0.0
    for name in (
        "configuration.json",
        "runs.jsonl",
        "scores.json",
        "manifest.sha256.json",
    ):
        assert (tmp_path / name).exists()
