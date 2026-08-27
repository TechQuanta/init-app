"""Machine-readable architecture metadata for generated projects."""

import json
from pathlib import Path
from typing import Any, Dict

MANIFEST_DIR = ".ai-scaffold"
MANIFEST_NAME = "project.json"


def path_for(root: Path) -> Path:
    return root / MANIFEST_DIR / MANIFEST_NAME


def load(root: Path) -> Dict[str, Any]:
    path = path_for(root)
    if not path.exists():
        raise FileNotFoundError(f"No AI Scaffold manifest found at {path}.")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid project manifest: {path}") from exc


def write(root: Path, data: Dict[str, Any]) -> Path:
    path = path_for(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
