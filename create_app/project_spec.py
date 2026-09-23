"""Validation and normalization for non-interactive project specifications."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


PROJECT_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,62}$")
PACKAGE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def load_spec(path: str) -> dict[str, Any]:
    """Load a JSON object and fail with an actionable CLI message."""
    source = Path(path).expanduser()
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read --spec file {source}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in --spec: {exc.msg} (line {exc.lineno})") from exc
    if not isinstance(data, dict):
        raise ValueError("--spec must contain one JSON object")
    return data


def validate_project_name(name: object) -> str:
    value = str(name or "").strip()
    if not PROJECT_NAME.fullmatch(value):
        raise ValueError(
            "project name must start with a letter and contain only letters, numbers, _ or - (max 63 characters)"
        )
    return value


def validate_app_name(name: object) -> str:
    value = str(name or "").strip()
    if not PACKAGE_NAME.fullmatch(value):
        raise ValueError("app name must be a valid Python package identifier")
    return value


def validate_relative_paths(values: object, field: str) -> list[str]:
    """Normalize generated paths and prevent a specification escaping its root."""
    if values is None:
        return []
    if isinstance(values, str):
        values = [item.strip() for item in values.split(",")]
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        raise ValueError(f"{field} must be a list of relative paths")

    result: list[str] = []
    for raw in values:
        candidate = raw.replace("\\", "/").strip()
        if candidate.startswith("/"):
            raise ValueError(f"{field} contains an unsafe path: {raw!r}")
        value = candidate.strip("/")
        parts = value.split("/")
        if not value or ":" in value or any(part in {"", ".", ".."} for part in parts):
            raise ValueError(f"{field} contains an unsafe path: {raw!r}")
        if value not in result:
            result.append(value)
    return result
