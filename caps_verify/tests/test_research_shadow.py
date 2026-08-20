from __future__ import annotations

import json

from caps_verify.shadow import build_probe_payload, load_probe_pack


def test_builtin_profiles_load_source_metadata() -> None:
    probes = load_probe_pack("builtin:full")
    assert len(probes) == 9
    by_id = {probe.probe_id: probe for probe in probes}
    assert by_id["mcptox-tool-metadata-001"].poison_tool_metadata is True
    assert by_id["fitd-multiturn-001"].messages
    assert "fitd" in by_id["fitd-multiturn-001"].source_ids
    assert by_id["figstep-typography-001"].modality == "image"


def test_multiturn_profile_preserves_roles_for_chat_payload() -> None:
    probe = next(
        item
        for item in load_probe_pack("builtin:adaptive")
        if item.probe_id == "fitd-multiturn-001"
    )
    payload = build_probe_payload(
        probe,
        provider="openai",
        route_family="openai_chat_completions",
        model="synthetic-model",
    )
    roles = [message["role"] for message in payload["messages"]]
    assert roles == ["system", "user", "assistant", "user", "assistant", "user"]
    serialized = json.dumps(payload)
    assert "caps_fixture_external_sink" in serialized
    assert "synthetic" in serialized.lower()


def test_typographic_profile_builds_provider_native_image_payloads() -> None:
    probe = next(
        item
        for item in load_probe_pack("builtin:multimodal")
        if item.probe_id == "figstep-typography-001"
    )

    chat = build_probe_payload(
        probe,
        provider="openai",
        route_family="openai_chat_completions",
        model="synthetic-model",
    )
    chat_content = chat["messages"][-1]["content"]
    assert chat_content[1]["image_url"]["url"].startswith("data:image/png;base64,")

    responses = build_probe_payload(
        probe,
        provider="openai",
        route_family="openai_responses",
        model="synthetic-model",
    )
    assert responses["input"][-1]["content"][1]["type"] == "input_image"

    anthropic = build_probe_payload(
        probe,
        provider="anthropic",
        route_family="anthropic_messages",
        model="synthetic-model",
    )
    image = anthropic["messages"][-1]["content"][1]
    assert image["source"]["media_type"] == "image/png"
    assert len(image["source"]["data"]) > 100
