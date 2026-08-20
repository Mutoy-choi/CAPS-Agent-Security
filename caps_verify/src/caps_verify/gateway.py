from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import threading
import time
import urllib.parse
import uuid
from collections.abc import AsyncIterator, Mapping, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

AuthHeader = Literal["auto", "passthrough", "authorization", "x-api-key"]

_HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}
_REQUEST_HEADERS_TO_DROP = _HOP_BY_HOP_HEADERS | {
    "accept-encoding",
    "content-length",
    "host",
    "x-caps-client-token",
}
_RESPONSE_HEADERS_TO_DROP = _HOP_BY_HOP_HEADERS | {"content-length"}


@dataclass(frozen=True)
class GatewayConfig:
    upstream_base_url: str
    provider: str = "generic"
    host: str = "127.0.0.1"
    port: int = 8788
    log_path: str = ".caps/gateway-events.jsonl"
    fingerprint_path: str = ".caps/gateway-fingerprints.json"
    shadow_queue_dir: str = ".caps/shadow-queue"
    shadow_queue_enabled: bool = True
    max_body_bytes: int = 64 * 1024 * 1024
    timeout_seconds: float = 600.0
    upstream_api_key: str = ""
    upstream_api_key_header: AuthHeader = "auto"
    client_token: str = ""
    fingerprint_secret: str = ""

    def validate(self) -> None:
        parsed = urllib.parse.urlparse(self.upstream_base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("upstream_base_url must be an absolute HTTP(S) URL")
        if parsed.query or parsed.fragment:
            raise ValueError("upstream_base_url cannot contain a query string or fragment")
        if self.port < 1 or self.port > 65535:
            raise ValueError("port must be between 1 and 65535")
        if self.max_body_bytes < 1:
            raise ValueError("max_body_bytes must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if not _is_loopback(self.host) and not self.client_token:
            raise ValueError(
                "A non-loopback gateway requires --client-token to avoid creating an open proxy"
            )


class GatewayRecorder:
    def __init__(self, config: GatewayConfig) -> None:
        self.config = config
        self.log_path = Path(config.log_path).expanduser()
        self.fingerprint_path = Path(config.fingerprint_path).expanduser()
        self.shadow_queue_dir = Path(config.shadow_queue_dir).expanduser()
        self._lock = threading.Lock()
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.fingerprint_path.parent.mkdir(parents=True, exist_ok=True)
        if config.shadow_queue_enabled:
            self.shadow_queue_dir.mkdir(parents=True, exist_ok=True)

    def record(self, event: dict[str, Any]) -> None:
        row = json.dumps(event, ensure_ascii=False, sort_keys=True)
        with self._lock:
            with self.log_path.open("a", encoding="utf-8") as handle:
                handle.write(row + "\n")

    def observe_fingerprint(self, metadata: dict[str, Any]) -> bool:
        fingerprint = str(metadata["configuration_fingerprint"])
        now = datetime.now(UTC).isoformat()
        with self._lock:
            state = self._read_fingerprints()
            current = state.get(fingerprint)
            if isinstance(current, dict):
                current["last_seen_at"] = now
                current["request_count"] = int(current.get("request_count", 0)) + 1
                state[fingerprint] = current
                self._write_fingerprints(state)
                return False

            state[fingerprint] = {
                "first_seen_at": now,
                "last_seen_at": now,
                "request_count": 1,
                "provider": metadata.get("provider"),
                "model": metadata.get("model"),
                "route_family": metadata.get("route_family"),
                "tool_count": metadata.get("tool_count"),
                "modalities": metadata.get("modalities"),
            }
            self._write_fingerprints(state)
            if self.config.shadow_queue_enabled:
                self._enqueue_shadow_job(metadata, now)
            return True

    def _read_fingerprints(self) -> dict[str, Any]:
        if not self.fingerprint_path.exists():
            return {}
        try:
            value = json.loads(self.fingerprint_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        return value if isinstance(value, dict) else {}

    def _write_fingerprints(self, state: dict[str, Any]) -> None:
        temporary = self.fingerprint_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self.fingerprint_path)

    def _enqueue_shadow_job(self, metadata: dict[str, Any], created_at: str) -> None:
        fingerprint = str(metadata["configuration_fingerprint"])
        job = {
            "schema_version": "caps.shadow.job.v1",
            "job_id": f"shadow-{fingerprint[:16]}",
            "created_at": created_at,
            "status": "queued",
            "configuration_fingerprint": fingerprint,
            "provider": metadata.get("provider"),
            "model": metadata.get("model"),
            "route_family": metadata.get("route_family"),
            "request_shape": {
                "message_count": metadata.get("message_count"),
                "input_item_count": metadata.get("input_item_count"),
                "tool_count": metadata.get("tool_count"),
                "modalities": metadata.get("modalities"),
                "stream": metadata.get("stream"),
            },
            "privacy": {
                "contains_raw_prompt": False,
                "contains_attachment_content": False,
                "contains_tool_arguments": False,
            },
            "note": (
                "This job is a configuration-change trigger. A provider-specific shadow "
                "worker must run synthetic test cases out of band; live queries are never "
                "modified."
            ),
        }
        path = self.shadow_queue_dir / f"{fingerprint}.json"
        if not path.exists():
            path.write_text(
                json.dumps(job, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )


def build_upstream_url(base_url: str, request_path: str, query: str = "") -> str:
    base = base_url.rstrip("/")
    path = "/" + request_path.lstrip("/")
    url = base + path
    return f"{url}?{query}" if query else url


def extract_request_metadata(
    payload: Any,
    *,
    provider: str,
    path: str,
    method: str,
    request_bytes: int,
    fingerprint_secret: str = "",
) -> dict[str, Any]:
    value = payload if isinstance(payload, dict) else {}
    messages = value.get("messages")
    input_value = value.get("input")
    tools = value.get("tools")
    model = value.get("model") if isinstance(value.get("model"), str) else "unknown"
    modalities = _detect_modalities(value)
    system_material = _extract_system_material(value)
    shape = {
        "provider": provider,
        "route_family": _route_family(path),
        "model": model,
        "tool_shape": _tool_shape(tools),
        "message_roles": _message_roles(messages),
        "input_shape": _content_shape(input_value),
        "modalities": modalities,
        "system_digest": _local_digest(system_material, fingerprint_secret),
    }
    return {
        "provider": provider,
        "method": method,
        "path": path,
        "route_family": _route_family(path),
        "model": model,
        "stream": bool(value.get("stream", False)),
        "request_bytes": request_bytes,
        "message_count": len(messages) if isinstance(messages, list) else 0,
        "input_item_count": len(input_value) if isinstance(input_value, list) else int(
            input_value is not None
        ),
        "tool_count": len(tools) if isinstance(tools, list) else 0,
        "modalities": modalities,
        "configuration_fingerprint": _sha256_json(shape),
    }


def extract_response_metadata(payload: bytes, content_type: str) -> dict[str, Any]:
    if "json" not in content_type.lower():
        return {"response_format": "non_json"}
    try:
        value = json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"response_format": "invalid_json"}
    if not isinstance(value, dict):
        return {"response_format": "json_non_object"}

    tool_call_count = 0
    finish_reasons: list[str] = []
    choices = value.get("choices")
    if isinstance(choices, list):
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            reason = choice.get("finish_reason")
            if isinstance(reason, str):
                finish_reasons.append(reason)
            message = choice.get("message")
            if isinstance(message, dict):
                calls = message.get("tool_calls")
                if isinstance(calls, list):
                    tool_call_count += len(calls)
                if isinstance(message.get("function_call"), dict):
                    tool_call_count += 1

    content = value.get("content")
    if isinstance(content, list):
        tool_call_count += sum(
            1
            for item in content
            if isinstance(item, dict) and item.get("type") == "tool_use"
        )

    output = value.get("output")
    if isinstance(output, list):
        tool_call_count += sum(
            1
            for item in output
            if isinstance(item, dict)
            and item.get("type") in {"function_call", "tool_call"}
        )

    resolved_model = value.get("model") if isinstance(value.get("model"), str) else None
    return {
        "response_format": "json",
        "resolved_model": resolved_model,
        "tool_call_count": tool_call_count,
        "finish_reasons": sorted(set(finish_reasons)),
        "usage": _numeric_usage(value.get("usage")),
        "provider_request_id_present": isinstance(value.get("id"), str),
    }


def create_app(config: GatewayConfig, *, upstream_transport: Any = None) -> Any:
    config.validate()
    try:
        import httpx
        from starlette.applications import Starlette
        from starlette.requests import Request
        from starlette.responses import JSONResponse, Response, StreamingResponse
        from starlette.routing import Route
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError('Install gateway support with: pip install -e ".[gateway]"') from exc

    recorder = GatewayRecorder(config)

    @asynccontextmanager
    async def lifespan(app: Any) -> AsyncIterator[None]:
        timeout = httpx.Timeout(config.timeout_seconds)
        app.state.upstream_client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=False,
            transport=upstream_transport,
        )
        yield
        await app.state.upstream_client.aclose()

    async def health(_: Request) -> JSONResponse:
        return JSONResponse(
            {
                "status": "ok",
                "provider": config.provider,
                "upstream_host": urllib.parse.urlparse(config.upstream_base_url).hostname,
                "telemetry": "local_only",
                "live_query_mutation": False,
            }
        )

    async def proxy(request: Request) -> Response:
        if config.client_token:
            supplied = request.headers.get("x-caps-client-token", "")
            if not hmac.compare_digest(supplied, config.client_token):
                return JSONResponse({"error": "unauthorized"}, status_code=401)

        body = await request.body()
        if len(body) > config.max_body_bytes:
            return JSONResponse({"error": "request_too_large"}, status_code=413)

        parsed_body = _try_json(body, request.headers.get("content-type", ""))
        metadata = extract_request_metadata(
            parsed_body,
            provider=config.provider,
            path=request.url.path,
            method=request.method,
            request_bytes=len(body),
            fingerprint_secret=config.fingerprint_secret,
        )
        first_seen = recorder.observe_fingerprint(metadata)
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        started = time.perf_counter()
        upstream_url = build_upstream_url(
            config.upstream_base_url,
            request.url.path,
            request.url.query,
        )
        headers = _forward_request_headers(request.headers, config)
        client = request.app.state.upstream_client

        try:
            upstream_request = client.build_request(
                request.method,
                upstream_url,
                content=body,
                headers=headers,
            )
            upstream_response = await client.send(upstream_request, stream=True)
        except httpx.HTTPError as exc:
            recorder.record(
                _gateway_event(
                    metadata,
                    request_id=request_id,
                    first_seen=first_seen,
                    status_code=502,
                    latency_ms=_elapsed_ms(started),
                    response_bytes=0,
                    response_metadata={"error_class": type(exc).__name__},
                )
            )
            return JSONResponse({"error": "upstream_unavailable"}, status_code=502)

        response_headers = _forward_response_headers(upstream_response.headers)
        content_type = upstream_response.headers.get("content-type", "")
        is_streaming = bool(metadata["stream"]) or content_type.startswith(
            "text/event-stream"
        )
        if is_streaming:

            async def stream_body() -> AsyncIterator[bytes]:
                response_bytes = 0
                try:
                    async for chunk in upstream_response.aiter_raw():
                        response_bytes += len(chunk)
                        yield chunk
                finally:
                    await upstream_response.aclose()
                    recorder.record(
                        _gateway_event(
                            metadata,
                            request_id=request_id,
                            first_seen=first_seen,
                            status_code=upstream_response.status_code,
                            latency_ms=_elapsed_ms(started),
                            response_bytes=response_bytes,
                            response_metadata={"response_format": "stream"},
                        )
                    )

            return StreamingResponse(
                stream_body(),
                status_code=upstream_response.status_code,
                headers=response_headers,
            )

        response_body = await upstream_response.aread()
        await upstream_response.aclose()
        response_headers.pop("content-encoding", None)
        response_metadata = extract_response_metadata(response_body, content_type)
        recorder.record(
            _gateway_event(
                metadata,
                request_id=request_id,
                first_seen=first_seen,
                status_code=upstream_response.status_code,
                latency_ms=_elapsed_ms(started),
                response_bytes=len(response_body),
                response_metadata=response_metadata,
            )
        )
        return Response(
            content=response_body,
            status_code=upstream_response.status_code,
            headers=response_headers,
        )

    methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    return Starlette(
        routes=[
            Route("/healthz", health, methods=["GET"]),
            Route("/{path:path}", proxy, methods=methods),
        ],
        lifespan=lifespan,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the local-first CAPS drop-in LLM query gateway"
    )
    parser.add_argument(
        "--upstream-base-url",
        default=os.environ.get("CAPS_UPSTREAM_BASE_URL", ""),
        required=not bool(os.environ.get("CAPS_UPSTREAM_BASE_URL")),
    )
    parser.add_argument("--provider", default=os.environ.get("CAPS_PROVIDER", "generic"))
    parser.add_argument("--host", default=os.environ.get("CAPS_GATEWAY_HOST", "127.0.0.1"))
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("CAPS_GATEWAY_PORT", "8788")),
    )
    parser.add_argument(
        "--log-path",
        default=os.environ.get("CAPS_GATEWAY_LOG", ".caps/gateway-events.jsonl"),
    )
    parser.add_argument(
        "--fingerprint-path",
        default=os.environ.get(
            "CAPS_GATEWAY_FINGERPRINTS", ".caps/gateway-fingerprints.json"
        ),
    )
    parser.add_argument(
        "--shadow-queue-dir",
        default=os.environ.get("CAPS_SHADOW_QUEUE_DIR", ".caps/shadow-queue"),
    )
    parser.add_argument("--disable-shadow-queue", action="store_true")
    parser.add_argument(
        "--max-body-bytes",
        type=int,
        default=int(os.environ.get("CAPS_GATEWAY_MAX_BODY_BYTES", str(64 * 1024 * 1024))),
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=float(os.environ.get("CAPS_GATEWAY_TIMEOUT_SECONDS", "600")),
    )
    parser.add_argument(
        "--upstream-api-key",
        default=os.environ.get("CAPS_UPSTREAM_API_KEY", ""),
    )
    parser.add_argument(
        "--upstream-api-key-header",
        choices=("auto", "passthrough", "authorization", "x-api-key"),
        default=os.environ.get("CAPS_UPSTREAM_API_KEY_HEADER", "auto"),
    )
    parser.add_argument(
        "--client-token",
        default=os.environ.get("CAPS_GATEWAY_CLIENT_TOKEN", ""),
    )
    parser.add_argument(
        "--fingerprint-secret",
        default=os.environ.get("CAPS_FINGERPRINT_SECRET", ""),
    )
    parser.add_argument("--log-level", default="info")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = GatewayConfig(
        upstream_base_url=args.upstream_base_url,
        provider=args.provider,
        host=args.host,
        port=args.port,
        log_path=args.log_path,
        fingerprint_path=args.fingerprint_path,
        shadow_queue_dir=args.shadow_queue_dir,
        shadow_queue_enabled=not args.disable_shadow_queue,
        max_body_bytes=args.max_body_bytes,
        timeout_seconds=args.timeout_seconds,
        upstream_api_key=args.upstream_api_key,
        upstream_api_key_header=args.upstream_api_key_header,
        client_token=args.client_token,
        fingerprint_secret=args.fingerprint_secret,
    )
    config.validate()
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError('Install gateway support with: pip install -e ".[gateway]"') from exc
    uvicorn.run(create_app(config), host=config.host, port=config.port, log_level=args.log_level)
    return 0


def _forward_request_headers(headers: Mapping[str, str], config: GatewayConfig) -> dict[str, str]:
    forwarded = {
        name: value
        for name, value in headers.items()
        if name.lower() not in _REQUEST_HEADERS_TO_DROP
    }
    if not config.upstream_api_key:
        return forwarded

    forwarded.pop("authorization", None)
    forwarded.pop("x-api-key", None)
    selected = config.upstream_api_key_header
    if selected == "auto":
        selected = "x-api-key" if config.provider.lower() == "anthropic" else "authorization"
    if selected == "authorization":
        forwarded["authorization"] = f"Bearer {config.upstream_api_key}"
    elif selected == "x-api-key":
        forwarded["x-api-key"] = config.upstream_api_key
    elif selected != "passthrough":
        raise ValueError(f"Unsupported upstream_api_key_header: {selected}")
    return forwarded


def _forward_response_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {
        name.lower(): value
        for name, value in headers.items()
        if name.lower() not in _RESPONSE_HEADERS_TO_DROP
    }


def _gateway_event(
    metadata: dict[str, Any],
    *,
    request_id: str,
    first_seen: bool,
    status_code: int,
    latency_ms: float,
    response_bytes: int,
    response_metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "caps.gateway.event.v1",
        "recorded_at": datetime.now(UTC).isoformat(),
        "request_id": request_id,
        **metadata,
        "new_configuration_fingerprint": first_seen,
        "status_code": status_code,
        "latency_ms": round(latency_ms, 3),
        "response_bytes": response_bytes,
        "response": response_metadata,
        "privacy": {
            "raw_prompt_logged": False,
            "attachment_content_logged": False,
            "tool_arguments_logged": False,
            "response_content_logged": False,
        },
    }


def _try_json(body: bytes, content_type: str) -> Any:
    if not body or "json" not in content_type.lower():
        return None
    try:
        return json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _route_family(path: str) -> str:
    lowered = path.lower()
    if lowered.endswith("/chat/completions"):
        return "openai_chat_completions"
    if lowered.endswith("/responses"):
        return "openai_responses"
    if lowered.endswith("/messages"):
        return "anthropic_messages"
    if "/audio/" in lowered:
        return "audio"
    if lowered.endswith("/embeddings"):
        return "embeddings"
    if lowered.endswith("/images") or "/images/" in lowered:
        return "images"
    return "generic_http"


def _message_roles(messages: Any) -> list[str]:
    if not isinstance(messages, list):
        return []
    roles: list[str] = []
    for message in messages:
        if isinstance(message, dict) and isinstance(message.get("role"), str):
            roles.append(str(message["role"]))
        else:
            roles.append("unknown")
    return roles


def _content_shape(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        return "text"
    if isinstance(value, list):
        return [_content_shape(item) for item in value]
    if isinstance(value, dict):
        block_type = value.get("type")
        return {
            "type": block_type if isinstance(block_type, str) else "object",
            "keys": sorted(str(key) for key in value if key not in {"text", "content"}),
        }
    return type(value).__name__


def _tool_shape(tools: Any) -> Any:
    if not isinstance(tools, list):
        return []
    shapes: list[dict[str, Any]] = []
    for tool in tools:
        if not isinstance(tool, dict):
            shapes.append({"type": type(tool).__name__})
            continue
        function = tool.get("function")
        if isinstance(function, dict):
            schema = function.get("parameters")
            name = function.get("name")
        else:
            schema = tool.get("input_schema")
            name = tool.get("name")
        shapes.append(
            {
                "name_digest": hashlib.sha256(str(name).encode("utf-8")).hexdigest()[:16],
                "schema_shape": _schema_shape(schema),
            }
        )
    return shapes


def _schema_shape(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in sorted(value.items(), key=lambda pair: str(pair[0])):
            if key in {"description", "title", "examples", "default", "enum"}:
                continue
            if key == "properties" and isinstance(item, dict):
                result[key] = sorted(
                    hashlib.sha256(str(name).encode("utf-8")).hexdigest()[:12]
                    for name in item
                )
            else:
                result[str(key)] = _schema_shape(item)
        return result
    if isinstance(value, list):
        return [_schema_shape(item) for item in value]
    if value is None or isinstance(value, bool | int | float):
        return value
    return type(value).__name__


def _detect_modalities(value: Any) -> dict[str, bool]:
    found = {"text": False, "image": False, "audio": False, "video": False, "file": False}

    def walk(item: Any) -> None:
        if isinstance(item, str):
            found["text"] = True
            lowered = item[:64].lower()
            if lowered.startswith("data:image"):
                found["image"] = True
            elif lowered.startswith("data:audio"):
                found["audio"] = True
            elif lowered.startswith("data:video"):
                found["video"] = True
            return
        if isinstance(item, list):
            for child in item:
                walk(child)
            return
        if not isinstance(item, dict):
            return
        item_type = str(item.get("type", "")).lower()
        keys = {str(key).lower() for key in item}
        if "image" in item_type or {"image_url", "input_image"} & keys:
            found["image"] = True
        if "audio" in item_type or {"input_audio", "audio"} & keys:
            found["audio"] = True
        if "video" in item_type or {"video_url", "input_video"} & keys:
            found["video"] = True
        if "file" in item_type or {"file", "file_id", "input_file"} & keys:
            found["file"] = True
        for child in item.values():
            walk(child)

    walk(value)
    return found


def _extract_system_material(value: dict[str, Any]) -> str:
    pieces: list[str] = []
    for key in ("instructions", "system"):
        item = value.get(key)
        if isinstance(item, str):
            pieces.append(item)
        elif isinstance(item, list):
            pieces.append(json.dumps(item, ensure_ascii=False, sort_keys=True))
    messages = value.get("messages")
    if isinstance(messages, list):
        for message in messages:
            if not isinstance(message, dict) or message.get("role") not in {
                "system",
                "developer",
            }:
                continue
            pieces.append(json.dumps(message.get("content"), ensure_ascii=False, sort_keys=True))
    return "\n".join(pieces)


def _local_digest(value: str, secret: str) -> str | None:
    if not value or not secret:
        return None
    return hmac.new(secret.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).hexdigest()


def _numeric_usage(value: Any) -> dict[str, int | float]:
    if not isinstance(value, dict):
        return {}
    return {
        str(key): item
        for key, item in value.items()
        if isinstance(item, int | float) and not isinstance(item, bool)
    }


def _sha256_json(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _elapsed_ms(started: float) -> float:
    return (time.perf_counter() - started) * 1000


def _is_loopback(host: str) -> bool:
    return host in {"127.0.0.1", "localhost", "::1"}
