"""Structured, deterministic AI-native scaffolding for FastAPI projects."""

from .api import apply_plan, change_plan_schema, plan_components, preview_plan
from .models import ChangePlan, ProjectSpec

__all__ = [
    "ChangePlan",
    "ProjectSpec",
    "apply_plan",
    "change_plan_schema",
    "plan_components",
    "preview_plan",
]
__version__ = "0.1.0"
