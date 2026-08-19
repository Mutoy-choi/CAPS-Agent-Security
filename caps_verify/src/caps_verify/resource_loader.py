from __future__ import annotations

import json
from importlib.resources import files
from typing import Any


def load_json(name: str) -> dict[str, Any]:
    resource = files("caps_verify.resources").joinpath(name)
    return json.loads(resource.read_text(encoding="utf-8"))
