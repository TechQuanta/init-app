import subprocess
import sys
from pathlib import Path

from create_app.loader import Spinner


def generate_django_project(project_name, app_name, location):

    base_path = Path(location or ".")
    project_root = base_path / project_name

    loader = Spinner("Creating Django project")
    loader.start()

    try:
        subprocess.run(
            ["django-admin", "startproject", project_name],
            cwd=base_path,
            check=True,
        )

        subprocess.run(
            [sys.executable, "manage.py", "startapp", app_name],
            cwd=project_root,
            check=True,
        )

    finally:
        loader.stop()

    return project_root
