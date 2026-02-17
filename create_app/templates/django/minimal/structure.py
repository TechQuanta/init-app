import sys
import subprocess
import re
import shutil
from pathlib import Path

# 🟢 Custom Logger & Renderer Imports
from create_app.ui.logger import logger
from create_app.generator.renderer import render_template

TEMPLATE_DIR = Path(__file__).parent
TEMPLATE_ROOT = Path(__file__).resolve().parents[2]

# Shared UI Paths
TEMPLATES_UI_DIR = TEMPLATE_ROOT / "common" / "template" / "django"
STATIC_UI_DIR = TEMPLATE_ROOT / "common" / "static"

def load_dependencies():
    """Returns content of requirements.txt with UTF-8 safety."""
    dependency_file = TEMPLATE_DIR / "requirements.txt"
    return dependency_file.read_text(encoding="utf-8").strip() if dependency_file.exists() else ""

def copy_ui(app_dir: Path):
    """Copies global templates and static files into the Django APP directory."""
    templates_dest = app_dir / "templates"
    static_dest = app_dir / "static"

    if TEMPLATES_UI_DIR.exists():
        shutil.copytree(TEMPLATES_UI_DIR, templates_dest, dirs_exist_ok=True)
        logger.info(f"✅ Templates copied to app: {templates_dest}")
    else:
        logger.warning(f"⚠ Shared Templates not found at {TEMPLATES_UI_DIR}")

    if STATIC_UI_DIR.exists():
        shutil.copytree(STATIC_UI_DIR, static_dest, dirs_exist_ok=True)
        logger.info(f"✅ Static files copied to app: {static_dest}")

def patch_settings(settings_path: Path, context: dict):
    """Updates settings.py with OS imports, Templates, and App registration."""
    if not settings_path.exists():
        return

    content = settings_path.read_text(encoding="utf-8")
    app_name = context["app_name"]

    # 1. Ensure import os
    if "import os" not in content:
        content = content.replace(
            "from pathlib import Path",
            "from pathlib import Path\nimport os",
        )

    # 2. Configure DIRS to look inside the specific App's templates folder
    content = re.sub(
        r"'DIRS': \[(.*?)\]",
        f"'DIRS': [BASE_DIR / '{app_name}' / 'templates'],",
        content,
        flags=re.DOTALL,
    )

    # 3. Register Installed App
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

    settings_path.write_text(content, encoding="utf-8")

def generate(project_root: Path, context: dict):
    """
    Django Standard Generator 😈🔥
    Dependency Checked | UTF-8 Fixed | App-Level UI
    """
    # --- 🛡️ DEPENDENCY CHECK ---
    try:
        import django
    except ImportError:
        print("\n" + "!" * 60)
        print("❌ CRITICAL ERROR: Django is not installed in your environment.")
        print("To fix this, run:")
        print("\n    pip install django")
        print("\nThen run 'init-app' again. 🚀")
        print("!" * 60 + "\n")
        sys.exit(1)

    project_name = context["project_name"]
    app_name = context["app_name"]
    base_path = project_root.parent

    # Clean up empty scaffold directory if it exists
    if project_root.exists() and not any(project_root.iterdir()):
        project_root.rmdir()

    # 1. Create Django Project
    logger.info(f"🚀 Running django-admin startproject {project_name}")
    subprocess.run(
        [sys.executable, "-m", "django", "startproject", project_name],
        cwd=base_path,
        check=True,
    )
    
    project_dir = base_path / project_name

    # 2. Create Django App
    logger.info(f"📦 Creating app: {app_name}")
    subprocess.run(
        [sys.executable, "manage.py", "startapp", app_name],
        cwd=project_dir,
        check=True,
    )
    
    app_dir = project_dir / app_name

    # 3. Patch Settings
    settings_path = project_dir / project_name / "settings.py"
    patch_settings(settings_path, context)

    # 4. Setup View logic
    (app_dir / "views.py").write_text(f"""from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
""", encoding="utf-8")

    # 5. Copy Shared UI into the APP directory 😈🔥
    copy_ui(app_dir)

    # 6. Common Project Files
    context.update({"dependencies": load_dependencies(), "entrypoint": "manage.py"})
    
    render_template("common/requirements.txt.tpl", project_dir / "requirements.txt", context)
    render_template("common/.env.tpl", project_dir / ".env", context)
    render_template("common/README.md.tpl", project_dir / "README.md", context)
    render_template("common/gitignore.tpl", project_dir / ".gitignore", context)

    logger.info(f"🏁 Django project {project_name} built successfully with app {app_name}")
    return project_dir