from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from caps_verify.gateway import (
    GatewayConfig,
    build_upstream_url,
    create_app,
    extract_request_metadata,
    extract_response_metadata,
)


def test_build_upstream_url_preserves_path_and_query() -> None:
    assert (
        build_upstream_url(
            "https://api.example.test/",
            "/v1/chat/completions",
            "beta=true",
        )
        == "https://api.example.test/v1/chat/completions?beta=true"
    )


def test_request_metadata_does_not_contain_raw_prompt_or_tool_text() -> None:
    payload = {
        "model": "provider/model-snapshot",
        "messages": [
            {"role": "system", "content": "SYSTEM-SENSITIVE-TEXT"},
            {"role": "user", "content": "CUSTOMER-SECRET-PROMPT"},
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "send_sensitive_email",
                    "description": "PRIVATE TOOL DESCRIPTION",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "recipient_address": {"type": "string"},
                            "message_body": {"type": "string"},
                        },
                    },
                },
            }
        ],
    }

    metadata = extract_request_metadata(
        payload,
        provider="openai",
        path="/v1/chat/completions",
        method="POST",
        request_bytes=123,
        fingerprint_secret="local-secret",
    )

    serialized = json.dumps(metadata, sort_keys=True)
    assert metadata["model"] == "provider/model-snapshot"
    assert metadata["tool_count"] == 1
    assert metadata["modalities"]["text"] is True
    assert "CUSTOMER-SECRET-PROMPT" not in serialized
    assert "SYSTEM-SENSITIVE-TEXT" not in serialized
    assert "PRIVATE TOOL DESCRIPTION" not in serialized
    assert "send_sensitive_email" not in serialized
    assert "recipient_address" not in serialized


def test_response_metadata_counts_openai_and_anthropic_tool_calls() -> None:
    openai_payload = json.dumps(
        {
            "id": "response-id",
            "model": "gpt-snapshot",
            "choices": [
                {
                    "finish_reason": "tool_calls",
                    "message": {
                        "tool_calls": [
                            {
                                "id": "call-1",
                                "type": "function",
                                "function": {"name": "fixture_tool", "arguments": "{}"},
                            }
                        ]
                    },
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 4},
        }
    ).encode()
    anthropic_payload = json.dumps(
        {
            "id": "message-id",
            "model": "claude-snapshot",
            "content": [
                {"type": "text", "text": "hello"},
                {"type": "tool_use", "id": "tool-1", "name": "fixture_tool", "input": {}},
            ],
            "usage": {"input_tokens": 11, "output_tokens": 5},
        }
    ).encode()

    openai = extract_response_metadata(openai_payload, "application/json")
    anthropic = extract_response_metadata(anthropic_payload, "application/json")

    assert openai["tool_call_count"] == 1
    assert openai["resolved_model"] == "gpt-snapshot"
    assert openai["usage"]["prompt_tokens"] == 10
    assert anthropic["tool_call_count"] == 1
    assert anthropic["resolved_model"] == "claude-snapshot"


def test_gateway_proxies_query_and_logs_only_metadata(tmp_path) -> None:
    request_secret = "CUSTOMER-PROMPT-DO-NOT-LOG"
    response_secret = "MODEL-ANSWER-DO-NOT-LOG"

    async def upstream_handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://api.provider.test/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer upstream-secret"
        body = await request.aread()
        assert request_secret.encode() in body
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={
                "id": "response-id",
                "model": "provider/model-snapshot",
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": response_secret},
                    }
                ],
                "usage": {"prompt_tokens": 8, "completion_tokens": 3},
            },
        )

    config = GatewayConfig(
        upstream_base_url="https://api.provider.test",
        provider="openai",
        log_path=str(tmp_path / "events.jsonl"),
        fingerprint_path=str(tmp_path / "fingerprints.json"),
        shadow_queue_dir=str(tmp_path / "shadow-queue"),
        upstream_api_key="upstream-secret",
        fingerprint_secret="local-fingerprint-secret",
    )
    app = create_app(config, upstream_transport=httpx.MockTransport(upstream_handler))

    async def execute() -> None:
        async with app.router.lifespan_context(app):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://caps.local",
            ) as client:
                response = await client.post(
                    "/v1/chat/completions",
                    headers={"authorization": "Bearer client-placeholder"},
                    json={
                        "model": "provider/model-snapshot",
                        "messages": [{"role": "user", "content": request_secret}],
                        "stream": False,
                    },
                )
                assert response.status_code == 200
                assert response.json()["choices"][0]["message"]["content"] == response_secret

    asyncio.run(execute())

    event_text = (tmp_path / "events.jsonl").read_text(encoding="utf-8")
    fingerprint_text = (tmp_path / "fingerprints.json").read_text(encoding="utf-8")
    queued_jobs = list((tmp_path / "shadow-queue").glob("*.json"))

    assert queued_jobs
    queue_text = queued_jobs[0].read_text(encoding="utf-8")
    for stored_text in (event_text, fingerprint_text, queue_text):
        assert request_secret not in stored_text
        assert response_secret not in stored_text
        assert "client-placeholder" not in stored_text
        assert "upstream-secret" not in stored_text
    event = json.loads(event_text)
    assert event["status_code"] == 200
    assert event["response"]["resolved_model"] == "provider/model-snapshot"
    assert event["response"]["usage"]["prompt_tokens"] == 8
    assert event["privacy"]["raw_prompt_logged"] is False


def test_non_loopback_gateway_requires_client_authentication() -> None:
    with pytest.raises(ValueError, match="client-token"):
        GatewayConfig(
            upstream_base_url="https://api.provider.test",
            host="0.0.0.0",
        ).validate()
