"""Optional MCP adapter for the deterministic ai_scaffold framework.

Install with ``pip install -e '.[mcp]'`` and configure an MCP client to run
``ai-scaffold-mcp`` over stdio.  The server deliberately exposes plans and
bounded operations, never arbitrary shell or filesystem access.
"""

from pathlib import Path
from typing import Any, Dict

from .api import apply_plan, preview_plan
from .context import project_context
from .engine import ScaffoldingEngine
from .manifest import load
from .planner import KeywordProvider
from .registry import list_components


def _mcp():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise SystemExit(
            "MCP support requires Python 3.10+ and the optional dependency. "
            "Install it with: python3.10 -m pip install -e '.[mcp]'"
        ) from exc
    return FastMCP("ai-scaffold")


def build_server():
    server = _mcp()

    @server.tool()
    def components_list() -> list[dict]:
        """Return all deterministic components the framework can install."""
        return [
            {
                "name": component.name,
                "description": component.description,
                "dependencies": list(component.dependencies),
                "environment": list(component.environment),
                "requires": list(component.requires),
            }
            for component in list_components()
        ]

    @server.tool()
    def project_inspect(project_dir: str = ".") -> dict:
        """Return compact project metadata and an AST-only source index."""
        return project_context(Path(project_dir).resolve())

    @server.tool()
    def plan_from_request(request: str, project_dir: str = ".") -> dict:
        """Resolve supported component intent from natural language without writing files."""
        root = Path(project_dir).resolve()
        metadata = load(root)
        components = KeywordProvider()._components(request)
        if not components:
            return {
                "status": "needs_generated_code",
                "reason": "No registered component matched the request.",
            }
        plan = ScaffoldingEngine().plan_components(
            components, metadata.get("components", [])
        )
        return plan.to_dict()

    @server.tool()
    def plan_preview(project_dir: str, plan: Dict[str, Any]) -> dict:
        """Validate a supplied ChangePlan JSON and report changes without writing files."""
        return preview_plan(project_dir, plan)

    @server.tool()
    def plan_apply(
        project_dir: str, plan: Dict[str, Any], approved: bool = False
    ) -> dict:
        """Apply a validated plan only when the caller has explicitly approved it."""
        return apply_plan(project_dir, plan, approved=approved)

    @server.tool()
    def project_doctor(project_dir: str = ".") -> dict:
        """Run syntax validation and return project metadata."""
        root = Path(project_dir).resolve()
        ScaffoldingEngine.validate(root)
        return {"valid": True, "project": load(root)}

    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
