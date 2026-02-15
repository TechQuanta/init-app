import shutil
from pathlib import Path
from create_app.generator.renderer import render_template

# ✅ Match Flask's working logic exactly
# parents[2] takes us from templates/tornado/minimal/ -> templates/
TEMPLATE_ROOT = Path(__file__).resolve().parents[2]

# Source folders for the UI
TEMPLATES_UI_DIR = TEMPLATE_ROOT / "common" / "template" / "tornado"
STATIC_UI_DIR = TEMPLATE_ROOT / "common" / "static"

def copy_ui(project_root: Path, context: dict):
    """
    Renders the HTML templates and copies static assets.
    """
    templates_dest = project_root / "templates"
    static_dest = project_root / "static"

    # ✅ Fix: We must RENDER the HTML files so variables like {{project_name}} work
    templates_dest.mkdir(exist_ok=True)
    
    if TEMPLATES_UI_DIR.exists():
        for tpl_file in TEMPLATES_UI_DIR.glob("*.html*"):
            # Construct relative path for renderer
            relative_tpl_path = f"common/template/tornado/{tpl_file.name}"
            output_name = tpl_file.name.replace(".tpl", "")
            
            # ✅ Injecting the context here!
            render_template(
                relative_tpl_path,
                templates_dest / output_name,
                context
            )
    else:
        print(f"⚠ Tornado Templates not found → {TEMPLATES_UI_DIR}")

    # ✅ Static assets can just be copied
    if STATIC_UI_DIR.exists():
        shutil.copytree(STATIC_UI_DIR, static_dest, dirs_exist_ok=True)

def generate(project_root: Path, context: dict):
    """
    Tornado Minimal Structure Generator 😈🔥
    """
    project_root.mkdir(parents=True, exist_ok=True)

    # ✅ 1. Render Entry Point (app.py)
    render_template(
        "tornado/minimal/entry.py.tpl",
        project_root / "app.py",
        context,
    )

    # ✅ 2. Render Common Files
    common_files = {
        "common/__init__.py.tpl": "__init__.py",
        "common/requirements.txt.tpl": "requirements.txt",
        "common/.env.tpl": ".env",
        "common/README.md.tpl": "README.md",
        "common/gitignore.tpl": ".gitignore",
    }

    for tpl, output in common_files.items():
        render_template(tpl, project_root / output, context)

    # ✅ 3. Setup UI (passing context so HTML is rendered)
    copy_ui(project_root, context)

    return project_root