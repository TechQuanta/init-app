from pathlib import Path
import shutil

from create_app.generator.renderer import render_template

# ✅ Correct root resolution 👍
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
    Flask Production Grade Generator 😈🔥
    Clean layered architecture + Shared UI
    """

    project_root.mkdir(parents=True, exist_ok=True)

    # ✅ Core Directory Layout
    folders = [
        "config",
        "routes",
        "services",
        "models",
        "schemas",
        "extensions",
        "middleware",
        "utils",
        "logs",
        "tests",
    ]

    for folder in folders:
        (project_root / folder).mkdir(exist_ok=True)

    # ✅ Python Packages 👍
    for package in folders[:-2]:  # exclude logs/tests
        (project_root / package / "__init__.py").touch()

    (project_root / "tests" / "__init__.py").touch()

    # ✅ ENTRYPOINT 😈🔥
    render_template(
        "flask/production/entry.py.tpl",
        project_root / "app.py",
        context,
    )

    # ✅ CONFIGURATION 👍
    (project_root / "config" / "settings.py").write_text(
        """
import os


class Settings:
    debug = os.getenv("DEBUG", "True") == "True"
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8080))


settings = Settings()
""".strip()
        + "\n"
    )

    # ✅ ROUTES 👍
    (project_root / "routes" / "__init__.py").write_text(
        """
from .health import register_health
from .auth import register_auth
from .api import register_api


def register_routes(app):
    register_health(app)
    register_auth(app)
    register_api(app)
""".strip()
        + "\n"
    )

    (project_root / "routes" / "health.py").write_text(
        """
def register_health(app):

    @app.route("/health")
    def health():
        return {"status": "healthy"}
""".strip()
        + "\n"
    )

    (project_root / "routes" / "auth.py").write_text(
        """
def register_auth(app):

    @app.route("/auth")
    def auth():
        return {"message": "Auth route ready"}
""".strip()
        + "\n"
    )

    (project_root / "routes" / "api.py").write_text(
        """
from flask import render_template


def register_api(app):

    @app.route("/")
    def index():
        return render_template("index.html")
""".strip()
        + "\n"
    )

    # ✅ PLACEHOLDERS 👍
    (project_root / "services" / "example_service.py").touch()
    (project_root / "models" / "example_model.py").touch()
    (project_root / "schemas" / "example_schema.py").touch()
    (project_root / "extensions" / "init_extensions.py").touch()
    (project_root / "middleware" / "example_middleware.py").touch()
    (project_root / "utils" / "helpers.py").touch()

    (project_root / "logs" / "app.log").touch()
    (project_root / "tests" / "test_health.py").touch()

    # ✅ ⭐ COPY SHARED UI ⭐ 😈🔥
    copy_ui(project_root)

    # ✅ COMMON FILES 👍
    render_template("common/requirements.txt.tpl", project_root / "requirements.txt", context)
    render_template("common/.env.tpl", project_root / ".env", context)
    render_template("common/README.md.tpl", project_root / "README.md", context)
    render_template("common/gitignore.tpl", project_root / ".gitignore", context)

    return project_root
