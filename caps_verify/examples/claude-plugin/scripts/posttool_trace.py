#!/usr/bin/env python3
"""Append redacted Claude Code tool events to the plugin data directory."""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SENSITIVE_KEYS = {"body", "content", "token", "password", "secret"}


def redact(value: Any, key: str = "") -> Any:
    if key.lower() in SENSITIVE_KEYS:
        return "<REDACTED>"
    if isinstance(value, dict):
        return {item_key: redact(item, item_key) for item_key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return value.replace("CANARY-CUSTOMER-001", "<SYNTHETIC_CANARY_REDACTED>")
    return value


def main() -> int:
    payload = json.load(sys.stdin)
    data_dir = Path(os.environ.get("CLAUDE_PLUGIN_DATA", ".caps-plugin-data"))
    data_dir.mkdir(parents=True, exist_ok=True)
    record = {"recorded_at": datetime.now(UTC).isoformat(), "event": redact(payload)}
    with (data_dir / "tool-traces.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
