import sys
import subprocess
from pathlib import Path

from create_app.generator.venv import create_virtualenv
from create_app.generator.renderer import render_template


# ✅ Ensure Django Installed 😈🔥
def ensure_django():

    try:
        subprocess.run(
            [sys.executable, "-m", "django", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

    except subprocess.SubprocessError:

        print("\n📦 Django not found. Installing Django...\n")

        subprocess.run(
            [sys.executable, "-m", "pip", "install", "django"],
            check=True,
        )


# ✅ MAIN DJANGO ENGINE 🚀
def generate_django_project(
    project_name,
    app_name,
    project_location,
    create_venv=False,
    project_type="Standard Django Project",  # kept for future 😌
):

    base_path = Path(project_location or ".")
    project_root = base_path / project_name

    base_path.mkdir(parents=True, exist_ok=True)

    # ✅ Step 1 — Ensure Django FIRST 😈🔥
    ensure_django()

    # ✅ Step 2 — Create Django Project (PROPER WAY 🔥)
    subprocess.run(
        [sys.executable, "-m", "django", "startproject", project_name],
        cwd=base_path,
        check=True,
    )

    # ✅ Step 3 — Create Django App 👍
    subprocess.run(
        [sys.executable, "manage.py", "startapp", app_name],
        cwd=project_root,
        check=True,
    )

    # ✅ Step 4 — Virtualenv AFTER project success 😌🔥
    if create_venv:
        create_virtualenv(project_root)

    # ✅ Step 5 — Common Files 😈🔥
    context = {
        "project_name": project_name,
        "app_name": app_name,
        "entrypoint": "manage.py",
        "debug": "True",
        "host": "127.0.0.1",
        "port": "8000",
    }

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
        "common/.gitignore.tpl",
        project_root / ".gitignore",
        context,
    )

    return project_root
