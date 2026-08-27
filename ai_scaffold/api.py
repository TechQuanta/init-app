"""Public Python API for embedding ai_scaffold in any LLM application."""

from pathlib import Path
from typing import Any, Dict, Iterable

from .engine import ScaffoldingEngine
from .manifest import load
from .models import ChangePlan


def plan_components(project_dir: str, components: Iterable[str]) -> Dict[str, Any]:
    """Build a deterministic component plan without changing the project."""
    root = Path(project_dir).resolve()
    plan = ScaffoldingEngine().plan_components(
        components, load(root).get("components", [])
    )
    return plan.to_dict()


def preview_plan(project_dir: str, plan_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and preview LLM-produced JSON before user approval."""
    return ScaffoldingEngine().preview(
        Path(project_dir).resolve(), ChangePlan.from_dict(plan_data)
    )


def apply_plan(
    project_dir: str, plan_data: Dict[str, Any], *, approved: bool = False
) -> Dict[str, Any]:
    """Apply only an explicitly approved, validated JSON plan."""
    if not approved:
        return {"applied": False, "reason": "Explicit approval is required."}
    root = Path(project_dir).resolve()
    engine = ScaffoldingEngine()
    plan = ChangePlan.from_dict(plan_data)
    preview = engine.preview(root, plan)
    engine.apply(root, plan)
    return {"applied": True, "preview": preview}


def change_plan_schema() -> Dict[str, Any]:
    """Return the JSON Schema an LLM must use for code injection."""
    return ChangePlan.json_schema()
