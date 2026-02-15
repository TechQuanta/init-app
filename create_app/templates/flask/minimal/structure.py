from pathlib import Path
import shutil

from create_app.generator.renderer import render_template

# ✅ Stable absolute resolution (CRITICAL 🔥)
TEMPLATE_ROOT = Path(__file__).resolve().parents[2]

TEMPLATES_UI_DIR = TEMPLATE_ROOT / "common" / "template" / "flask"
STATIC_UI_DIR = TEMPLATE_ROOT / "common" / "static"


# ✅ Copy Shared UI 😈🔥
def copy_ui(project_root: Path):

    templates_dest = project_root / "templates"
    static_dest = project_root / "static"

    # ✅ Safety guards (CRITICAL 🔥)
    if TEMPLATES_UI_DIR.exists():
        shutil.copytree(
            TEMPLATES_UI_DIR,
            templates_dest,
            dirs_exist_ok=True,
        )
    else:
        print(f"⚠ Templates UI not found → {TEMPLATES_UI_DIR}")

    if STATIC_UI_DIR.exists():
        shutil.copytree(
            STATIC_UI_DIR,
            static_dest,
            dirs_exist_ok=True,
        )
    else:
        print(f"⚠ Static UI not found → {STATIC_UI_DIR}")


def generate(project_root: Path, context: dict):
    """
    Flask Minimal Structure Generator 😈🔥
    Minimal core + Shared UI
    """

    project_root.mkdir(parents=True, exist_ok=True)

    # ✅ Entry Point 👍
    render_template(
        "flask/minimal/entry.py.tpl",
        project_root / "app.py",
        context,
    )

    # ✅ Common Files 👍
    render_template("common/__init__.py.tpl", project_root / "__init__.py", context)
    render_template("common/requirements.txt.tpl", project_root / "requirements.txt", context)
    render_template("common/.env.tpl", project_root / ".env", context)
    render_template("common/README.md.tpl", project_root / "README.md", context)
    render_template("common/gitignore.tpl", project_root / ".gitignore", context)

    # ✅ ⭐ Shared UI ⭐ 😈🔥
    copy_ui(project_root)

    return project_root
