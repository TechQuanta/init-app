from pathlib import Path
from create_app.generator.renderer import render_template


def generate(project_root: Path, context: dict):
    """
    Flask Production Grade Generator 😈🔥
    Clean layered architecture + Jinja UI
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

        # ✅ Flask UI Layers 😈🔥
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
        "services",
        "models",
        "schemas",
        "extensions",
        "middleware",
        "utils",
        "tests",
    ]

    for package in packages:
        (project_root / package / "__init__.py").touch()

    # ✅ ENTRYPOINT 😈🔥
    render_template(
        "flask/production/app.py.tpl",
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

    # ✅ ROUTE REGISTRY 👍
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

    # ✅ ROUTES 👍

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

    # ✅ SERVICES 👍
    (project_root / "services" / "example_service.py").write_text(
        """
class ExampleService:

    @staticmethod
    def process():
        return {"message": "Service layer working"}
""".strip()
        + "\n"
    )

    # ✅ PLACEHOLDERS 👍
    (project_root / "models" / "example_model.py").touch()

    (project_root / "schemas" / "example_schema.py").write_text(
        """
class ExampleSchema:

    @staticmethod
    def serialize(data):
        return data
""".strip()
        + "\n"
    )

    (project_root / "extensions" / "init_extensions.py").write_text(
        """
def init_extensions(app):
    pass
""".strip()
        + "\n"
    )

    (project_root / "middleware" / "example_middleware.py").touch()
    (project_root / "utils" / "helpers.py").touch()

    # ✅ LOG FILE 👍
    (project_root / "logs" / "app.log").touch()

    # ✅ TEST FILE 👍
    (project_root / "tests" / "test_health.py").touch()

    # 🔥🔥🔥 JINJA TEMPLATE FILES 😈🔥🔥🔥

    (project_root / "templates" / "base.html").write_text(
        """
<!DOCTYPE html>
<html>
<head>
    <title>{{ project_name }}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>

    <div class="container">
        {% block content %}{% endblock %}
    </div>

    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
""".strip()
        + "\n"
    )

    (project_root / "templates" / "index.html").write_text(
        """
{% extends "base.html" %}

{% block content %}
    <h1>🚀 Flask Production App</h1>
    <p>Generated using py-create</p>
{% endblock %}
""".strip()
        + "\n"
    )

    # 🔥🔥🔥 STATIC FILES 😈🔥🔥🔥

    (project_root / "static" / "css" / "style.css").write_text(
        """
body {
    font-family: Arial, sans-serif;
    background: #f5f5f5;
    text-align: center;
    margin-top: 100px;
}

.container {
    max-width: 800px;
    margin: auto;
}
""".strip()
        + "\n"
    )

    (project_root / "static" / "js" / "app.js").write_text(
        """
console.log("Flask App Ready 🚀");
""".strip()
        + "\n"
    )

    (project_root / "static" / "assets" / ".keep").touch()

    # 🔥🔥🔥 COMMON FILES 🔥🔥🔥

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
