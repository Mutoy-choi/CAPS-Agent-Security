from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from caps_verify.shadow import (
    ShadowWorker,
    ShadowWorkerConfig,
    build_probe_payload,
    extract_tool_calls,
    load_probe_pack,
)


class _SyntheticProviderHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length))
        messages = payload.get("messages", [])
        user_text = ""
        if isinstance(messages, list):
            for message in messages:
                if isinstance(message, dict) and message.get("role") == "user":
                    user_text = str(message.get("content", ""))
        if "increased by four percent" in user_text:
            tool_name = "caps_fixture_create_summary"
        else:
            tool_name = "caps_fixture_external_sink"
        response = {
            "id": "synthetic-response",
            "model": payload.get("model"),
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": "call-1",
                                "type": "function",
                                "function": {"name": tool_name, "arguments": "{}"},
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
        }
        body = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def _start_provider() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _SyntheticProviderHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _queued_job(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "caps.shadow.job.v1",
                "job_id": "shadow-test",
                "status": "queued",
                "configuration_fingerprint": "a" * 64,
                "provider": "openai",
                "model": "synthetic-model",
                "route_family": "openai_chat_completions",
            }
        ),
        encoding="utf-8",
    )


def test_shadow_worker_runs_safe_probes_and_writes_asr(tmp_path) -> None:
    provider, thread = _start_provider()
    queue_dir = tmp_path / "queue"
    results_dir = tmp_path / "results"
    queue_dir.mkdir()
    job_path = queue_dir / "job.json"
    _queued_job(job_path)

    worker = ShadowWorker(
        ShadowWorkerConfig(
            upstream_base_url=f"http://127.0.0.1:{provider.server_port}",
            api_key="test-key",
            queue_dir=str(queue_dir),
            results_dir=str(results_dir),
            provider="openai",
        )
    )
    try:
        assert worker.run_once() == 1
    finally:
        provider.shutdown()
        provider.server_close()
        thread.join(timeout=2)

    completed = json.loads(job_path.read_text(encoding="utf-8"))
    assert completed["status"] == "completed"
    assert completed["a2a_asr"] == 1.0
    assert completed["benign_task_success_rate"] == 1.0

    result_files = list(results_dir.rglob("*.json"))
    assert len(result_files) == 1
    result = json.loads(result_files[0].read_text(encoding="utf-8"))
    assert result["metrics"]["attack_runs"] == 4
    assert result["metrics"]["attack_successes"] == 4
    serialized = json.dumps(result)
    assert "Synthetic quarterly report" not in serialized
    assert "synthetic-response" not in serialized
    assert '"arguments"' not in serialized
    assert result["privacy"]["raw_response_stored"] is False


def test_probe_payloads_use_synthetic_tools_only() -> None:
    probe = load_probe_pack()[1]
    payload = build_probe_payload(
        probe,
        provider="openai",
        route_family="openai_chat_completions",
        model="synthetic-model",
    )
    serialized = json.dumps(payload)
    assert "caps_fixture_external_sink" in serialized
    assert "customer-secret" not in serialized


def test_tool_call_extraction_supports_provider_formats() -> None:
    examples: list[tuple[dict[str, Any], str]] = [
        (
            {
                "choices": [
                    {
                        "message": {
                            "tool_calls": [
                                {"function": {"name": "caps_fixture_external_sink"}}
                            ]
                        }
                    }
                ]
            },
            "caps_fixture_external_sink",
        ),
        (
            {
                "content": [
                    {"type": "tool_use", "name": "caps_fixture_delete_canary"}
                ]
            },
            "caps_fixture_delete_canary",
        ),
        (
            {
                "output": [
                    {"type": "function_call", "name": "caps_fixture_create_summary"}
                ]
            },
            "caps_fixture_create_summary",
        ),
    ]
    for payload, expected in examples:
        assert expected in extract_tool_calls(payload)
