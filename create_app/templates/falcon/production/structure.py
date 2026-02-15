from pathlib import Path
from create_app.generator.renderer import render_template


def generate(project_root: Path, context: dict):
    """
    Falcon Production Grade Generator 😈🔥
    """

    project_root.mkdir(parents=True, exist_ok=True)

    # ✅ Directory Layout
    folders = [
        "config",
        "routes",
        "services",
        "models",
        "schemas",
        "middleware",
        "utils",
        "logs",
        "tests",
    ]

    for folder in folders:
        (project_root / folder).mkdir(exist_ok=True)

    # ✅ Python Packages
    packages = [
        "config",
        "routes",
        "services",
        "models",
        "schemas",
        "middleware",
        "utils",
        "tests",
    ]

    for package in packages:
        (project_root / package / "__init__.py").touch()

    # ✅ ENTRYPOINT 😈🔥
    render_template(
        "falcon/production/entry.py.tpl",
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
    port = int(os.getenv("PORT", 8000))


settings = Settings()
""".strip()
        + "\n"
    )

    # ✅ ROUTES REGISTRY 👍
    (project_root / "routes" / "__init__.py").write_text(
        """
from .health import HealthResource
from .auth import AuthResource
from .api import ApiResource


def register_routes(app):
    app.add_route("/health", HealthResource())
    app.add_route("/auth", AuthResource())
    app.add_route("/api", ApiResource())
""".strip()
        + "\n"
    )

    # ✅ ROUTE HANDLERS 👍
    (project_root / "routes" / "health.py").write_text(
        """
import json


class HealthResource:

    def on_get(self, req, resp):
        resp.media = {"status": "healthy"}
""".strip()
        + "\n"
    )

    (project_root / "routes" / "auth.py").write_text(
        """
class AuthResource:

    def on_get(self, req, resp):
        resp.media = {"message": "Auth route ready"}
""".strip()
        + "\n"
    )

    (project_root / "routes" / "api.py").write_text(
        """
class ApiResource:

    def on_get(self, req, resp):
        resp.media = {"message": "API route ready"}
""".strip()
        + "\n"
    )

    # ✅ PLACEHOLDERS 👍
    (project_root / "services" / "example_service.py").touch()
    (project_root / "models" / "example_model.py").touch()
    (project_root / "schemas" / "example_schema.py").touch()
    (project_root / "middleware" / "example_middleware.py").touch()
    (project_root / "utils" / "helpers.py").touch()

    # ✅ LOG FILE 👍
    (project_root / "logs" / "app.log").touch()

    # ✅ TEST FILE 👍
    (project_root / "tests" / "test_health.py").touch()

    # 🔥 COMMON FILES 🔥
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
