"""Compact local context for planning; source is only indexed structurally."""

import ast
from pathlib import Path
from typing import Dict, List

from .manifest import load


def project_context(root: Path) -> Dict[str, object]:
    metadata = load(root)
    files: List[dict] = []
    for path in root.rglob("*.py"):
        if any(
            part.startswith(".") or part in {"venv", ".venv", "__pycache__"}
            for part in path.relative_to(root).parts
        ):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        files.append(
            {
                "path": str(path.relative_to(root)),
                "classes": [
                    node.name
                    for node in ast.walk(tree)
                    if isinstance(node, ast.ClassDef)
                ],
                "functions": [
                    node.name
                    for node in ast.walk(tree)
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                ],
            }
        )
    return {"project": metadata, "python_index": files}
