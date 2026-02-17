import sys
import subprocess
import re
from pathlib import Path

from create_app.generator.renderer import render_template

# ✅ Ensure Django Installed 😈🔥 
# Added output capture to keep your CLI UI clean
def ensure_django():
    try:
        subprocess.run(
            [sys.executable, "-m", "django", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        print("📦 Django not found. Installing now to bootstrap DRF...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "django"],
            check=True,
        )


# ✅ Patch settings.py 😈🔥
def patch_settings(settings_path: Path, context: dict):
    if not settings_path.exists():
        return

    # ✅ Added encoding="utf-8" for Windows safety
    content = settings_path.read_text(encoding="utf-8")

    # ✅ Ensure import os exists 😈🔥
    if "import os" not in content:
        content = re.sub(
            r"(from pathlib import Path.*\n)",
            r"\1import os\n",
            content,
        )

    # ✅ Replace SECRET KEY / DEBUG / HOSTS
    secret_block = render_template(
        "django/drf/secret.tpl",
        None,
        context,
        raw=True,
    )

    content = re.sub(
        r"SECRET_KEY\s*=.*",
        secret_block,
        content,
    )

    # ✅ Inject Installed Apps
    apps_block = render_template(
        "django/drf/apps.py.tpl",
        None,
        context,
        raw=True,
    )

    pattern = r"INSTALLED_APPS\s*=\s*\[(.*?)\]"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        raise RuntimeError("INSTALLED_APPS not found in settings.py")

    existing = match.group(1).strip()
    updated = existing + "\n" + apps_block

    content = re.sub(
        pattern,
        f"INSTALLED_APPS = [\n{updated}\n]",
        content,
        flags=re.DOTALL,
    )

    # ✅ Append DRF Config
    drf_config = render_template(
        "django/drf/rf.py.tpl",
        None,
        context,
        raw=True,
    )

    content += "\n\n" + drf_config
    
    # ✅ Added encoding="utf-8"
    settings_path.write_text(content, encoding="utf-8")


# ✅ Overwrite urls.py 😈🔥
def overwrite_urls(urls_path: Path, context: dict):
    if not urls_path.exists():
        return
        
    urls_content = render_template(
        "django/drf/urls.tpl",
        None,
        context,
        raw=True,
    )
    # ✅ Added encoding="utf-8"
    urls_path.write_text(urls_content, encoding="utf-8")


# ✅ MAIN GENERATOR 🚀
def generate(project_root: Path, context: dict):
    project_name = context["project_name"]
    app_name = context["app_name"]
    base_path = project_root.parent

    base_path.mkdir(parents=True, exist_ok=True)

    ensure_django()

    # ✅ Step 1 — Create Project 😈🔥
    subprocess.run(
        [sys.executable, "-m", "django", "startproject", project_name],
        cwd=base_path,
        check=True,
    )

    project_dir = base_path / project_name
    
    # 🛡️ GUARD: Create folders if they don't exist
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / project_name).mkdir(exist_ok=True)

    # ✅ Step 2 — Create App 👍
    subprocess.run(
        [sys.executable, "manage.py", "startapp", app_name],
        cwd=project_dir,
        check=True,
    )
    
    # 🛡️ GUARD: Ensure app folder exists
    (project_dir / app_name).mkdir(exist_ok=True)

    # ✅ Step 3 — Patch Settings 😈🔥
    settings_path = project_dir / project_name / "settings.py"
    patch_settings(settings_path, context)

    # ✅ Step 4 — Overwrite URLs 😈🔥
    urls_path = project_dir / project_name / "urls.py"
    overwrite_urls(urls_path, context)

    # ✅ Step 5 — Common Files 🔥
    # Ensure these templates are rendered and written with UTF-8
    render_template("common/requirements.txt.tpl", project_dir / "requirements.txt", context)
    render_template("common/.env.tpl", project_dir / ".env", context)
    render_template("common/README.md.tpl", project_dir / "README.md", context)
    render_template("common/gitignore.tpl", project_dir / ".gitignore", context)

    return project_dir