import sys
import subprocess
from pathlib import Path

from create_app.generator.renderer import render_template

TEMPLATE_DIR = Path(__file__).parent


def load_dependencies():
    dependency_file = TEMPLATE_DIR / "requirements.txt"
    return dependency_file.read_text().strip() if dependency_file.exists() else ""


def generate(project_root: Path, context: dict):

    project_name = context["project_name"]
    app_name = context["app_name"]

    base_path = project_root.parent

    # ✅ Remove empty scaffold folder created by generator
    if project_root.exists():
        project_root.rmdir()

    # ✅ Create Django project
    subprocess.run(
        [sys.executable, "-m", "django", "startproject", project_name],
        cwd=base_path,
        check=True,
    )

    project_dir = base_path / project_name

    # ✅ Create Django app
    subprocess.run(
        [sys.executable, "manage.py", "startapp", app_name],
        cwd=project_dir,
        check=True,
    )

    dependencies = load_dependencies()

    context.update({
        "dependencies": dependencies,
        "entrypoint": "manage.py",
    })

    render_template("common/requirements.txt.tpl", project_dir / "requirements.txt", context)
    render_template("common/.env.tpl", project_dir / ".env", context)
    render_template("common/README.md.tpl", project_dir / "README.md", context)
    render_template("common/gitignore.tpl", project_dir / ".gitignore", context)

    # ✅ ⭐⭐⭐ CRITICAL RETURN ⭐⭐⭐
    return project_dir
