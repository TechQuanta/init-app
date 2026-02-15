from pathlib import Path
from create_app.generator.renderer import render_template


def generate(project_root: Path, context: dict):
    """
    FastAPI Minimal Structure Generator
    """

    project_root.mkdir(parents=True, exist_ok=True)

    # ✅ Entry Point
    render_template(
        "fastapi/minimal/entry.py.tpl",
        project_root / "app.py",
        context,
    )

    # ✅ Common Files

    render_template(
        "common/__init__.py.tpl",
        project_root / "__init__.py",
        context,
    )

    render_template(
        "common/requirements.txt.tpl",
        project_root / "requirements.txt",
        context,
    )

    render_template(
        "common/.env.tpl",
        project_root / ".env",
        context,
    )

    render_template(
        "common/README.md.tpl",
        project_root / "README.md",
        context,
    )

    render_template(
        "common/gitignore.tpl",
        project_root / ".gitignore",
        context,
    )
