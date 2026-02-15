import sys
import subprocess
from pathlib import Path


def create_virtualenv(project_root: Path):

    subprocess.run(
        [sys.executable, "-m", "venv", "venv"],
        cwd=project_root,
        check=True,
    )
