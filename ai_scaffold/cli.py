"""Command line UX for the AI-native scaffolding MVP."""

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from .context import project_context
from .engine import ScaffoldingEngine
from .manifest import load, write
from .models import ChangePlan, ProjectSpec
from .planner import KeywordProvider
from .registry import list_components


def _display(plan) -> None:
    print("\nProposed changes:")
    for change in plan.changes:
        print(f"+ {change.path}")
    if plan.dependencies:
        print("\nDependencies:")
        for dependency in plan.dependencies:
            print(f"+ {dependency}")
    if plan.environment:
        print("\nEnvironment variables:")
        for variable in plan.environment:
            print(f"+ {variable}")


def _read_json(source: str) -> dict:
    """Read a JSON document from a filename or stdin (using '-')."""
    try:
        raw = (
            sys.stdin.read()
            if source == "-"
            else Path(source).read_text(encoding="utf-8")
        )
        return json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not read JSON input {source!r}: {exc}") from exc


def _confirm(yes: bool) -> bool:
    return yes or input("\nApply changes? [y/N] ").strip().lower() in {"y", "yes"}


def _base_project(root: Path, spec) -> None:
    root.mkdir(parents=True)
    (root / "app").mkdir()
    (root / "tests").mkdir()
    (root / "app" / "__init__.py").write_text("", encoding="utf-8")
    (root / "app" / "main.py").write_text(
        "from fastapi import FastAPI\n\napp = FastAPI(title="
        + repr(spec.name)
        + ")\n\n\n@app.get('/health')\ndef health():\n    return {'status': 'ok'}\n",
        encoding="utf-8",
    )
    (root / "requirements.txt").write_text(
        "fastapi\nuvicorn[standard]\n", encoding="utf-8"
    )
    (root / ".env.example").write_text(
        "# Copy this file to .env and fill in values.\n", encoding="utf-8"
    )
    (root / "README.md").write_text(
        f"# {spec.name}\n\nRun with `uvicorn app.main:app --reload`.\n",
        encoding="utf-8",
    )
    write(
        root,
        {
            "version": 1,
            "language": spec.language,
            "framework": spec.framework,
            "database": spec.database,
            "components": ["fastapi"],
        },
    )


def create(args) -> int:
    if args.spec:
        payload = _read_json(args.spec)
        payload.setdefault("name", args.name)
        payload.setdefault("output_dir", args.output_dir)
        spec = ProjectSpec(**payload)
    else:
        provider = KeywordProvider()
        spec = provider.generate_project_plan(
            args.request, {"name": args.name, "output_dir": args.output_dir}
        )
    spec.validate()
    root = (Path(args.output_dir).expanduser() / spec.name).resolve()
    if root.exists():
        raise SystemExit(f"Refusing to overwrite existing path: {root}")
    engine = ScaffoldingEngine()
    plan = engine.plan_components(
        [item for item in spec.components if item != "fastapi"], installed=["fastapi"]
    )
    print(f"\nProject plan: {spec.framework} / {spec.database}")
    print("Components: " + ", ".join(spec.components))
    _display(plan)
    if args.plan or not _confirm(args.yes):
        return 0
    _base_project(root, spec)
    engine.apply(root, plan)
    print(f"\nCreated {root}")
    return 0


def add(args) -> int:
    root = Path(args.project_dir).resolve()
    metadata = load(root)
    components = KeywordProvider()._components(args.request)
    if not components:
        raise SystemExit(
            "No supported component was recognized. Run 'ai-init components'."
        )
    plan = ScaffoldingEngine().plan_components(
        components, metadata.get("components", [])
    )
    if plan.is_empty():
        print("All requested components are already installed.")
        return 0
    _display(plan)
    if args.plan or not _confirm(args.yes):
        return 0
    ScaffoldingEngine().apply(root, plan)
    print("\nComponent changes applied and syntax validated.")
    return 0


def plan_json(args) -> int:
    root = Path(args.project_dir).resolve()
    plan = ChangePlan.from_dict(_read_json(args.input))
    preview = ScaffoldingEngine().preview(root, plan)
    _display(plan)
    print("\nValidated JSON plan:")
    print(json.dumps(preview, indent=2, sort_keys=True))
    return 0


def apply_json(args) -> int:
    root = Path(args.project_dir).resolve()
    plan = ChangePlan.from_dict(_read_json(args.input))
    engine = ScaffoldingEngine()
    preview = engine.preview(root, plan)
    _display(plan)
    if args.plan:
        print("\nValidated JSON plan:")
        print(json.dumps(preview, indent=2, sort_keys=True))
        return 0
    if not _confirm(args.yes):
        return 0
    engine.apply(root, plan)
    print("\nJSON plan applied and syntax validated.")
    return 0


def schema(_args) -> int:
    print(json.dumps(ChangePlan.json_schema(), indent=2, sort_keys=True))
    return 0


def components(_args) -> int:
    for component in list_components():
        print(f"{component.name:<14} {component.description}")
    return 0


def status(args) -> int:
    print(json.dumps(load(Path(args.project_dir).resolve()), indent=2, sort_keys=True))
    return 0


def doctor(args) -> int:
    root = Path(args.project_dir).resolve()
    ScaffoldingEngine.validate(root)
    print(json.dumps(project_context(root), indent=2, sort_keys=True))
    return 0


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--yes", "-y", action="store_true", help="Apply without confirmation."
    )
    parser.add_argument(
        "--plan", action="store_true", help="Preview only; do not write files."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-init", description="AI-native deterministic FastAPI scaffolding"
    )
    sub = parser.add_subparsers(dest="command")
    create_parser = sub.add_parser(
        "create", help="Create a FastAPI project from a natural-language request"
    )
    create_parser.add_argument("name")
    create_parser.add_argument(
        "request", nargs="?", default="FastAPI project with pytest"
    )
    create_parser.add_argument("--output-dir", default=".")
    create_parser.add_argument(
        "--spec",
        metavar="FILE",
        help="ProjectSpec JSON file; use '-' to read JSON from stdin.",
    )
    _common(create_parser)
    create_parser.set_defaults(handler=create)
    add_parser = sub.add_parser("add", help="Plan and add supported components")
    add_parser.add_argument("request")
    add_parser.add_argument("--project-dir", default=".")
    _common(add_parser)
    add_parser.set_defaults(handler=add)
    plan_parser = sub.add_parser("plan", help="Validate and preview a JSON ChangePlan")
    plan_parser.add_argument(
        "--input", required=True, help="ChangePlan JSON file; use '-' for stdin."
    )
    plan_parser.add_argument("--project-dir", default=".")
    plan_parser.set_defaults(handler=plan_json)
    apply_parser = sub.add_parser("apply", help="Preview and apply a JSON ChangePlan")
    apply_parser.add_argument(
        "--input", required=True, help="ChangePlan JSON file; use '-' for stdin."
    )
    apply_parser.add_argument("--project-dir", default=".")
    _common(apply_parser)
    apply_parser.set_defaults(handler=apply_json)
    schema_parser = sub.add_parser(
        "schema", help="Print the accepted ChangePlan JSON schema"
    )
    schema_parser.set_defaults(handler=schema)
    for name, handler, help_text in (
        ("components", components, "List available components"),
        ("status", status, "Show project architecture"),
        ("doctor", doctor, "Validate and index the project"),
    ):
        item = sub.add_parser(name, help=help_text)
        if name != "components":
            item.add_argument("--project-dir", default=".")
        item.set_defaults(handler=handler)
    return parser


def main(argv: Iterable[str] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        # Keep the required interactive entry point useful without an API key.
        request = input("What are you building? ").strip()
        name = input("Project name: ").strip() or "fastapi_app"
        args = parser.parse_args(["create", name, request])
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
