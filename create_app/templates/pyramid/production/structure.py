from pathlib import Path
from create_app.generator.renderer import render_template


def generate(project_root: Path, context: dict):
    """
    Pyramid Production Grade Generator 😈🔥
    Clean layered architecture
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
    ]

    for folder in folders:
        (project_root / folder).mkdir(exist_ok=True)

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
    config.add_route("health", "/health")
    config.add_route("auth", "/auth")
    config.add_route("api", "/api")
""".strip() + "\n"
    )

    # ✅ VIEWS 👍

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

    (project_root / "views" / "api.py").write_text(
        """
from pyramid.view import view_config


@view_config(route_name="api", renderer="json")
def api_view(request):
    return {"message": "API route ready"}
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

    # ✅ MODELS 👍
    (project_root / "models" / "example_model.py").touch()

    # ✅ SCHEMAS 👍
    (project_root / "schemas" / "example_schema.py").write_text(
        """
class ExampleSchema:
    pass
""".strip() + "\n"
    )

    # ✅ UTILS 👍
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
