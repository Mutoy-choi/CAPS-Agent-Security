from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
from collections.abc import Sequence
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

MAX_BODY_BYTES = 2 * 1024 * 1024
_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def validate_submission(payload: dict[str, Any]) -> None:
    if payload.get("schema_version") != "caps.telemetry.v1":
        raise ValueError("Unsupported telemetry schema_version")

    consent = payload.get("consent")
    if not isinstance(consent, dict) or consent.get("accepted") is not True:
        raise ValueError("A submission must contain explicit accepted consent")
    if consent.get("data_use") not in {"service_operation", "pooled_research"}:
        raise ValueError("Unsupported consent.data_use")
    if not isinstance(consent.get("terms_version"), str) or not consent["terms_version"]:
        raise ValueError("consent.terms_version is required")

    tenant = payload.get("tenant")
    if not isinstance(tenant, dict):
        raise ValueError("tenant is required")
    for field in ("organization_id", "project_id", "installation_id"):
        value = tenant.get(field)
        if not isinstance(value, str) or not _ID_PATTERN.fullmatch(value):
            raise ValueError(f"tenant.{field} must be a non-empty safe identifier")

    privacy = payload.get("privacy")
    if not isinstance(privacy, dict):
        raise ValueError("privacy declaration is required")
    if privacy.get("mode") not in {"aggregate_only", "redacted_runs"}:
        raise ValueError("Unsupported privacy.mode")
    required_false = (
        "raw_prompts_included",
        "attachment_contents_included",
        "tool_arguments_included",
        "tool_results_included",
    )
    if any(privacy.get(field) is not False for field in required_false):
        raise ValueError(
            "Raw prompt, attachment, tool argument, and tool result data are forbidden"
        )
    if privacy.get("no_raw_content") is not True:
        raise ValueError("privacy.no_raw_content must be true")

    if not isinstance(payload.get("benchmark"), dict):
        raise ValueError("benchmark metadata is required")
    if not isinstance(payload.get("metrics"), dict):
        raise ValueError("metrics are required")
    if not isinstance(payload.get("evidence_manifest"), dict):
        raise ValueError("evidence_manifest is required")

    if privacy.get("mode") == "aggregate_only" and "runs" in payload:
        raise ValueError("aggregate_only submissions cannot include run rows")
    if privacy.get("mode") == "redacted_runs":
        runs = payload.get("runs")
        if not isinstance(runs, list):
            raise ValueError("redacted_runs submissions must include a runs list")
        _validate_redacted_runs(runs)


def _validate_redacted_runs(runs: list[Any]) -> None:
    allowed_fields = {
        "run_id_hash",
        "scenario_id",
        "variant",
        "defense",
        "attack_success",
        "benign_task_success",
        "false_block",
        "unauthorized_tool_invocation",
        "unauthorized_data_flow",
        "event_count",
        "executed_action_count",
    }
    for row in runs:
        if not isinstance(row, dict):
            raise ValueError("Each redacted run must be a JSON object")
        unknown = set(row) - allowed_fields
        if unknown:
            raise ValueError(f"Redacted run contains forbidden fields: {sorted(unknown)}")


def store_submission(
    payload: dict[str, Any],
    storage_root: str | Path,
    idempotency_key: str,
) -> tuple[Path, bool]:
    validate_submission(payload)
    if not re.fullmatch(r"[a-f0-9]{64}", idempotency_key):
        raise ValueError("X-CAPS-Idempotency-Key must be a SHA-256 hex digest")

    tenant = payload["tenant"]
    org_bucket = _bucket(str(tenant["organization_id"]))
    project_bucket = _bucket(str(tenant["project_id"]))
    date_bucket = datetime.now(UTC).strftime("%Y-%m-%d")
    destination = Path(storage_root) / org_bucket / project_bucket / date_bucket
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / f"{idempotency_key}.json"
    if path.exists():
        return path, True

    envelope = {
        "collector_received_at": datetime.now(UTC).isoformat(),
        "submission": payload,
    }
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(envelope, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return path, False


def _bucket(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


class CollectorHandler(BaseHTTPRequestHandler):
    server_version = "CAPSCollector/0.2"

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            self._send_json(HTTPStatus.OK, {"status": "ok"})
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/submissions":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        if not self._authorized():
            self._send_json(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_content_length"})
            return
        if length < 1 or length > self.server.max_body_bytes:  # type: ignore[attr-defined]
            self._send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "invalid_size"})
            return

        idempotency_key = self.headers.get("X-CAPS-Idempotency-Key", "")
        try:
            body = self.rfile.read(length)
            payload = json.loads(body)
            if not isinstance(payload, dict):
                raise ValueError("JSON body must be an object")
            path, duplicate = store_submission(
                payload,
                self.server.storage_root,  # type: ignore[attr-defined]
                idempotency_key,
            )
        except (json.JSONDecodeError, ValueError) as exc:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": "invalid_submission", "detail": str(exc)},
            )
            return
        except OSError:
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "storage_failure"})
            return

        receipt = hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:24]
        self._send_json(
            HTTPStatus.OK if duplicate else HTTPStatus.CREATED,
            {"accepted": True, "duplicate": duplicate, "receipt_id": receipt},
        )

    def log_message(self, format: str, *args: object) -> None:
        # Avoid logging request bodies, tokens, tenant identifiers, or query strings.
        print(f"collector {self.address_string()} {format % args}")

    def _authorized(self) -> bool:
        header = self.headers.get("Authorization", "")
        expected = f"Bearer {self.server.token}"  # type: ignore[attr-defined]
        return hmac.compare_digest(header, expected)

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def build_server(
    host: str,
    port: int,
    storage_root: str | Path,
    token: str,
    max_body_bytes: int = MAX_BODY_BYTES,
) -> ThreadingHTTPServer:
    if not token:
        raise ValueError("Collector token cannot be empty")
    server = ThreadingHTTPServer((host, port), CollectorHandler)
    server.storage_root = Path(storage_root)  # type: ignore[attr-defined]
    server.token = token  # type: ignore[attr-defined]
    server.max_body_bytes = max_body_bytes  # type: ignore[attr-defined]
    return server


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the CAPS opt-in telemetry collector")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--storage", default=".caps-collector/submissions")
    parser.add_argument("--token-env", default="CAPS_COLLECTOR_TOKEN")
    parser.add_argument("--max-body-bytes", type=int, default=MAX_BODY_BYTES)
    args = parser.parse_args(argv)

    token = os.environ.get(args.token_env, "")
    server = build_server(args.host, args.port, args.storage, token, args.max_body_bytes)
    print(
        f"CAPS collector listening on {args.host}:{args.port}; "
        "place it behind HTTPS before any non-local deployment"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
