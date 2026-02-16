from pathlib import Path
import shutil

from create_app.generator.renderer import render_template


TEMPLATE_ROOT = Path(__file__).parents[2]


TEMPLATES_UI_DIR = TEMPLATE_ROOT / "common"  / "template" / "tornado"
STATIC_UI_DIR = TEMPLATE_ROOT / "common"  / "static"

# ✅ Copy REAL UI 😈🔥
def copy_ui(project_root: Path):

    shutil.copytree(
        TEMPLATES_UI_DIR,
        project_root / "templates",
        dirs_exist_ok=True,
    )

    shutil.copytree(
        STATIC_UI_DIR,
        project_root / "static",
        dirs_exist_ok=True,
    )


def generate(project_root: Path, context: dict):
    """
    Tornado Minimal Structure Generator 😈🔥
    Minimal backend + REAL UI
    """

    project_root.mkdir(parents=True, exist_ok=True)

    # ✅ Entry Point
    render_template(
        "tornado/minimal/entry.py.tpl",
        project_root / "app.py",
        context,
    )

    # ✅ Common Files
    render_template("common/__init__.py.tpl", project_root / "__init__.py", context)
    render_template("common/requirements.txt.tpl", project_root / "requirements.txt", context)
    render_template("common/.env.tpl", project_root / ".env", context)
    render_template("common/README.md.tpl", project_root / "README.md", context)
    render_template("common/gitignore.tpl", project_root / ".gitignore", context)

    # ✅ ⭐ COPY UI ⭐ 😈🔥
    copy_ui(project_root)

    return project_root
