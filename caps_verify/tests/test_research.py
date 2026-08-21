from __future__ import annotations

import json
from pathlib import Path

import pytest

from caps_verify.research import (
    available_profiles,
    build_research_pack,
    export_research_bundle,
    library_doctor,
    research_summary,
    write_research_pack,
)


def test_core_profile_preserves_fast_shadow_baseline() -> None:
    pack = build_research_pack("core")
    assert pack["pack_id"] == "caps-research-core"
    assert len(pack["probes"]) == 5
    assert sum(row["kind"] == "benign" for row in pack["probes"]) == 1
    assert sum(row["kind"] == "attack" for row in pack["probes"]) == 4
    assert {row["family"] for row in pack["probes"]} == {
        "clean",
        "attachment",
        "tool_output",
        "mcp_metadata",
        "composition",
    }
    assert pack["policy"]["synthetic_canaries_only"] is True
    assert pack["policy"]["raw_third_party_datasets_bundled"] is False


def test_full_profile_inherits_research_families_and_provenance() -> None:
    pack = build_research_pack("full")
    probe_ids = {row["probe_id"] for row in pack["probes"]}
    assert {
        "fitd-multiturn-001",
        "pyrit-adaptive-seed-001",
        "cot-dilution-001",
        "figstep-typography-001",
    }.issubset(probe_ids)
    assert len(probe_ids) == len(pack["probes"])
    source_ids = {row["source_id"] for row in pack["sources"]}
    assert {"agentdojo", "mcptox", "fitd", "cot-hijacking", "figstep"}.issubset(
        source_ids
    )
    library_ids = {row["library_id"] for row in pack["libraries"]}
    assert {"inspect-ai", "pyrit", "garak", "agentdojo"}.issubset(library_ids)


def test_profile_listing_and_summary_are_stable() -> None:
    profiles = {row["name"]: row for row in available_profiles()}
    assert set(profiles) == {"core", "adaptive", "reasoning", "multimodal", "full"}
    assert profiles["full"]["probe_count"] > profiles["core"]["probe_count"]
    summary = research_summary("adaptive")
    assert summary["attack_count"] > 4
    assert "multi_turn" in summary["families"]
    assert "pyrit" in summary["library_ids"]


def test_library_doctor_is_non_importing_and_actionable() -> None:
    result = library_doctor()
    rows = {row["library_id"]: row for row in result["libraries"]}
    assert set(rows) == {"inspect-ai", "pyrit", "garak", "agentdojo"}
    assert rows["inspect-ai"]["minimum_version"] == "0.3.251"
    assert result["install_examples"]["recommended"] == 'pip install -e ".[research]"'
    assert isinstance(result["ready"], bool)


def test_write_and_export_research_bundle(tmp_path: Path) -> None:
    pack_path = write_research_pack("core", tmp_path / "pack.json")
    assert json.loads(pack_path.read_text(encoding="utf-8"))["profile"] == "core"

    output = tmp_path / "bundle"
    result = export_research_bundle("full", output, model="synthetic-model")
    assert result["profile"] == "full"
    expected = {
        "caps-attack-pack.json",
        "inspect-dataset.jsonl",
        "pyrit-seeds.prompt",
        "garak-rest.json",
        "agentdojo-scenarios.json",
        "SOURCES.md",
        "README.md",
        "manifest.sha256.json",
        "artifacts/figstep-typography-001.png",
    }
    assert expected.issubset(set(result["files"]))

    inspect_rows = [
        json.loads(line)
        for line in (output / "inspect-dataset.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(inspect_rows) == len(build_research_pack("full")["probes"])

    pyrit = json.loads((output / "pyrit-seeds.prompt").read_text(encoding="utf-8"))
    assert pyrit["dataset_name"] == "caps-research-full"
    assert any(row.get("data_type") == "image_path" for row in pyrit["prompts"])

    garak = json.loads((output / "garak-rest.json").read_text(encoding="utf-8"))
    rest = garak["rest"]["RestGenerator"]
    assert rest["uri"].startswith("http://127.0.0.1:")
    assert rest["key_env_var"] == "CAPS_EVALUATION_API_KEY"

    manifest = json.loads((output / "manifest.sha256.json").read_text(encoding="utf-8"))
    assert "caps-attack-pack.json" in manifest
    assert "manifest.sha256.json" not in manifest


def test_export_rejects_remote_target_without_explicit_authorization(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Remote research targets"):
        export_research_bundle(
            "core",
            tmp_path / "remote",
            endpoint="https://example.invalid/v1/chat/completions",
        )

    result = export_research_bundle(
        "core",
        tmp_path / "approved",
        endpoint="https://example.invalid/v1/chat/completions",
        allow_remote_target=True,
    )
    assert result["remote_target_allowed"] is True
