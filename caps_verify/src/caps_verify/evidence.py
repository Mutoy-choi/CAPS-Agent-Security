from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .models import RunResult


def write_evidence_bundle(
    output: str | Path,
    configuration: dict[str, Any],
    runs: Iterable[RunResult],
    scores: dict[str, Any],
) -> Path:
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    run_rows = [run.to_dict() for run in runs]

    _write_json(destination / "configuration.json", configuration)
    _write_jsonl(destination / "runs.jsonl", run_rows)
    _write_json(destination / "scores.json", scores)

    manifest: dict[str, str] = {}
    for name in ("configuration.json", "runs.jsonl", "scores.json"):
        payload = (destination / name).read_bytes()
        manifest[name] = hashlib.sha256(payload).hexdigest()
    _write_json(destination / "manifest.sha256.json", manifest)
    return destination


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
