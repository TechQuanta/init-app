from pathlib import Path
from create_app.generator.renderer import render_template

def generate(project_root: Path, context: dict):
    """
    FastAPI Minimal Structure Generator 🚀
    """

    # 1. Create the base directory
    project_root.mkdir(parents=True, exist_ok=True)

    # 2. ✅ Render the Entry Point (app.py)
    # This now includes the uvicorn.run() block we fixed!
    render_template(
        "fastapi/minimal/entry.py.tpl",
        project_root / "app.py",
        context,
    )

    # 3. ✅ Render Common Project Files
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

    # 4. Return the root so the engine knows it's finished
    return project_root