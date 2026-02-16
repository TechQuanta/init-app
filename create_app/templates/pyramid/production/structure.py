from pathlib import Path
import shutil

from create_app.generator.renderer import render_template


TEMPLATE_ROOT = Path(__file__).parents[2]


TEMPLATES_UI_DIR = TEMPLATE_ROOT / "common"  / "template" / "pyramid"
STATIC_UI_DIR = TEMPLATE_ROOT / "common" / "static"


# ✅ Copy Shared UI 😈🔥
def copy_ui(project_root: Path):

    shutil.copytree(
        TEMPLATES_UI_DIR,
        project_root / "templates",
        dirs_exist_ok=True,
    )

    shutil.copytree(
        STATIC_UI_DIR,
        project_root / "static",
        dirs_exist_ok=True,
    )


def generate(project_root: Path, context: dict):
    """
    Pyramid Production Grade Generator 😈🔥
    Clean layered architecture + Shared UI
    """

    project_root.mkdir(parents=True, exist_ok=True)

    # ✅ Directory Layout 😌🔥
    folders = [
        "config",
        "routes",
        "views",
        "services",
        "models",
        "schemas",
        "utils",
        "logs",
        "tests",

        # ✅ UI Layers 😈🔥
        "templates",
        "static",
    ]

    for folder in folders:
        (project_root / folder).mkdir(exist_ok=True)

    # ✅ Static Subfolders 👍
    for folder in ["css", "js", "assets"]:
        (project_root / "static" / folder).mkdir(parents=True, exist_ok=True)

    # ✅ Python Packages 👍
    packages = [
        "config",
        "routes",
        "views",
        "services",
        "models",
        "schemas",
        "utils",
        "tests",
    ]

    for package in packages:
        (project_root / package / "__init__.py").touch()

    # ✅ ENTRYPOINT 😈🔥
    render_template(
        "pyramid/production/entry.py.tpl",
        project_root / "app.py",
        context,
    )

    # ✅ SETTINGS 👍
    (project_root / "config" / "settings.py").write_text(
        """
import os


class Settings:
    debug = os.getenv("DEBUG", "True") == "True"
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 6543))


settings = Settings()
""".strip() + "\n"
    )

    # ✅ ROUTE REGISTRY 👍
    (project_root / "routes" / "__init__.py").write_text(
        """
def includeme(config):
    config.add_route("home", "/")
    config.add_route("health", "/health")
    config.add_route("auth", "/auth")
""".strip() + "\n"
    )

    # ✅ VIEWS 👍

    (project_root / "views" / "home.py").write_text(
        """
from pyramid.view import view_config


@view_config(route_name="home", renderer="../templates/index.html")
def home_view(request):
    return {}
""".strip() + "\n"
    )

    (project_root / "views" / "health.py").write_text(
        """
from pyramid.view import view_config


@view_config(route_name="health", renderer="json")
def health_view(request):
    return {"status": "healthy"}
""".strip() + "\n"
    )

    (project_root / "views" / "auth.py").write_text(
        """
from pyramid.view import view_config


@view_config(route_name="auth", renderer="json")
def auth_view(request):
    return {"message": "Auth route ready"}
""".strip() + "\n"
    )

    # ✅ SERVICES 👍
    (project_root / "services" / "example_service.py").write_text(
        """
class ExampleService:

    @staticmethod
    def process():
        return {"message": "Service layer working"}
""".strip() + "\n"
    )

    # ✅ PLACEHOLDERS 👍
    (project_root / "models" / "example_model.py").touch()
    (project_root / "schemas" / "example_schema.py").touch()
    (project_root / "utils" / "helpers.py").touch()

    # ✅ LOG FILE 👍
    (project_root / "logs" / "app.log").touch()

    # ✅ TEST FILE 👍
    (project_root / "tests" / "test_health.py").touch()

    # 🔥 COMMON FILES 🔥
    render_template("common/requirements.txt.tpl", project_root / "requirements.txt", context)
    render_template("common/.env.tpl", project_root / ".env", context)
    render_template("common/README.md.tpl", project_root / "README.md", context)
    render_template("common/gitignore.tpl", project_root / ".gitignore", context)

    # ✅ ⭐ Shared UI ⭐ 😈🔥
    copy_ui(project_root)

    return project_root
