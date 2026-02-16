import sys
import subprocess
import re
import shutil
from pathlib import Path

from create_app.generator.renderer import render_template

TEMPLATE_DIR = Path(__file__).parent
TEMPLATE_ROOT = Path(__file__).resolve().parents[2]


TEMPLATES_UI_DIR = TEMPLATE_ROOT / "common" / "template" / "django"
STATIC_UI_DIR = TEMPLATE_ROOT / "common" / "static"


def load_dependencies():
    dependency_file = TEMPLATE_DIR / "requirements.txt"
    return dependency_file.read_text().strip() if dependency_file.exists() else ""


# ✅ Copy Shared UI 😈🔥
def copy_ui(project_dir: Path):
    """Copies global templates and static files to the Django project root."""
    templates_dest = project_dir / "templates"
    static_dest = project_dir / "static"

    if TEMPLATES_UI_DIR.exists():
        shutil.copytree(TEMPLATES_UI_DIR, templates_dest, dirs_exist_ok=True)
    else:
        print(f"⚠ Shared Templates not found → {TEMPLATES_UI_DIR}")

    if STATIC_UI_DIR.exists():
        shutil.copytree(STATIC_UI_DIR, static_dest, dirs_exist_ok=True)


# ✅ Patch Django settings.py 😈🔥
def patch_settings(settings_path: Path, context: dict):
    if not settings_path.exists():
        return

    content = settings_path.read_text()
    app_name = context["app_name"]

    # ✅ Ensure import os
    if "import os" not in content:
        content = content.replace(
            "from pathlib import Path",
            "from pathlib import Path\nimport os",
        )

    # ✅ Configure Templates DIR to look at root/templates
    content = re.sub(
        r"'DIRS': \[(.*?)\]",
        "'DIRS': [BASE_DIR / 'templates'],",
        content,
        flags=re.DOTALL,
    )

    # ✅ Register Installed App
    apps_pattern = r"INSTALLED_APPS\s*=\s*\[(.*?)\]"
    match = re.search(apps_pattern, content, re.DOTALL)

    if match:
        existing_apps = match.group(1)
        if f"'{app_name}'" not in existing_apps:
            updated_apps = existing_apps.strip() + f"\n    '{app_name}',\n"
            content = re.sub(
                apps_pattern,
                f"INSTALLED_APPS = [\n    {updated_apps}]",
                content,
                flags=re.DOTALL,
            )

    settings_path.write_text(content)


def generate(project_root: Path, context: dict):
    """
    Django Standard Generator 😈🔥
    Now with Shared UI and Test-Safety Guards
    """
    project_name = context["project_name"]
    app_name = context["app_name"]
    base_path = project_root.parent

    # ✅ Remove empty scaffold folder
    if project_root.exists() and not any(project_root.iterdir()):
        project_root.rmdir()

    # ✅ 1. Create Django Project
    subprocess.run(
        [sys.executable, "-m", "django", "startproject", project_name],
        cwd=base_path,
        check=True,
    )

    # 🛡️ GUARD: Ensure project_dir exists for the next steps (needed for MOCK tests)
    project_dir = base_path / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / project_name).mkdir(exist_ok=True)

    # ✅ 2. Create Django App
    subprocess.run(
        [sys.executable, "manage.py", "startapp", app_name],
        cwd=project_dir,
        check=True,
    )

    # 🛡️ GUARD: Ensure app folder exists before writing files
    app_dir = project_dir / app_name
    app_dir.mkdir(exist_ok=True)

    # ✅ 3. Patch Settings
    settings_path = project_dir / project_name / "settings.py"
    if settings_path.exists():
        patch_settings(settings_path, context)

    # ✅ 4. Setup View logic
    views_file = app_dir / "views.py"
    views_file.write_text(f"""from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
""")

    # ✅ 5. Copy Shared UI (index.html, CSS, JS) 😈🔥
    copy_ui(project_dir)

    # ✅ 6. Common Project Files
    context.update({"dependencies": load_dependencies(), "entrypoint": "manage.py"})
    
    render_template("common/requirements.txt.tpl", project_dir / "requirements.txt", context)
    render_template("common/.env.tpl", project_dir / ".env", context)
    render_template("common/README.md.tpl", project_dir / "README.md", context)
    
    # Ensure this matches your physical file: .gitignore.tpl
    render_template("common/gitignore.tpl", project_dir / ".gitignore", context)

    return project_dir