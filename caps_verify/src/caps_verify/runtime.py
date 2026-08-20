from __future__ import annotations

import argparse
import os
import threading
from collections.abc import Sequence

from .gateway import GatewayConfig, create_app
from .shadow import ShadowWorker, ShadowWorkerConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the CAPS query gateway and automatic synthetic shadow ASR worker "
            "as one local sidecar"
        )
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
        "--upstream-api-key",
        default=os.environ.get("CAPS_UPSTREAM_API_KEY", ""),
    )
    parser.add_argument(
        "--evaluation-api-key",
        default=os.environ.get("CAPS_EVALUATION_API_KEY", ""),
        help="Dedicated shadow-evaluation key; defaults to the upstream key",
    )
    parser.add_argument(
        "--upstream-api-key-header",
        choices=("auto", "passthrough", "authorization", "x-api-key"),
        default=os.environ.get("CAPS_UPSTREAM_API_KEY_HEADER", "auto"),
    )
    parser.add_argument(
        "--evaluation-api-key-header",
        choices=("auto", "authorization", "x-api-key"),
        default=os.environ.get("CAPS_EVALUATION_API_KEY_HEADER", "auto"),
    )
    parser.add_argument(
        "--client-token",
        default=os.environ.get("CAPS_GATEWAY_CLIENT_TOKEN", ""),
    )
    parser.add_argument(
        "--fingerprint-secret",
        default=os.environ.get("CAPS_FINGERPRINT_SECRET", ""),
    )
    parser.add_argument(
        "--log-path",
        default=os.environ.get("CAPS_GATEWAY_LOG", ".caps/gateway-events.jsonl"),
    )
    parser.add_argument(
        "--fingerprint-path",
        default=os.environ.get(
            "CAPS_GATEWAY_FINGERPRINTS",
            ".caps/gateway-fingerprints.json",
        ),
    )
    parser.add_argument(
        "--shadow-queue-dir",
        default=os.environ.get("CAPS_SHADOW_QUEUE_DIR", ".caps/shadow-queue"),
    )
    parser.add_argument(
        "--shadow-results-dir",
        default=os.environ.get("CAPS_SHADOW_RESULTS_DIR", ".caps/shadow-results"),
    )
    parser.add_argument(
        "--shadow-endpoint-path",
        default=os.environ.get("CAPS_SHADOW_ENDPOINT_PATH", ""),
    )
    parser.add_argument(
        "--attack-pack",
        default=os.environ.get("CAPS_ATTACK_PACK", ""),
    )
    parser.add_argument("--shadow-poll-seconds", type=float, default=2.0)
    parser.add_argument("--shadow-timeout-seconds", type=float, default=120.0)
    parser.add_argument("--shadow-max-probes", type=int, default=8)
    parser.add_argument(
        "--gateway-timeout-seconds",
        type=float,
        default=float(os.environ.get("CAPS_GATEWAY_TIMEOUT_SECONDS", "600")),
    )
    parser.add_argument(
        "--max-body-bytes",
        type=int,
        default=int(os.environ.get("CAPS_GATEWAY_MAX_BODY_BYTES", str(64 * 1024 * 1024))),
    )
    parser.add_argument("--log-level", default="info")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    evaluation_api_key = args.evaluation_api_key or args.upstream_api_key
    gateway_config = GatewayConfig(
        upstream_base_url=args.upstream_base_url,
        provider=args.provider,
        host=args.host,
        port=args.port,
        log_path=args.log_path,
        fingerprint_path=args.fingerprint_path,
        shadow_queue_dir=args.shadow_queue_dir,
        shadow_queue_enabled=True,
        max_body_bytes=args.max_body_bytes,
        timeout_seconds=args.gateway_timeout_seconds,
        upstream_api_key=args.upstream_api_key,
        upstream_api_key_header=args.upstream_api_key_header,
        client_token=args.client_token,
        fingerprint_secret=args.fingerprint_secret,
    )
    worker_config = ShadowWorkerConfig(
        upstream_base_url=args.upstream_base_url,
        api_key=evaluation_api_key,
        queue_dir=args.shadow_queue_dir,
        results_dir=args.shadow_results_dir,
        provider=args.provider,
        endpoint_path=args.shadow_endpoint_path,
        api_key_header=args.evaluation_api_key_header,
        attack_pack=args.attack_pack,
        poll_seconds=args.shadow_poll_seconds,
        timeout_seconds=args.shadow_timeout_seconds,
        max_probes=args.shadow_max_probes,
    )
    gateway_config.validate()
    worker = ShadowWorker(worker_config)
    stop = threading.Event()

    def worker_loop() -> None:
        while not stop.wait(worker_config.poll_seconds):
            worker.run_once()

    worker.run_once()
    thread = threading.Thread(
        target=worker_loop,
        name="caps-shadow-worker",
        daemon=True,
    )
    thread.start()

    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError('Install runtime support with: pip install -e ".[gateway]"') from exc

    try:
        uvicorn.run(
            create_app(gateway_config),
            host=gateway_config.host,
            port=gateway_config.port,
            log_level=args.log_level,
        )
    finally:
        stop.set()
        thread.join(timeout=worker_config.poll_seconds + 1)
    return 0
