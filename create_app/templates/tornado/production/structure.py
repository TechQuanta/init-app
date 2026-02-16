from pathlib import Path
import shutil

from create_app.generator.renderer import render_template


TEMPLATE_ROOT = Path(__file__).parents[2]


TEMPLATES_UI_DIR = TEMPLATE_ROOT / "common"  / "template" / "tornado"
STATIC_UI_DIR = TEMPLATE_ROOT / "common"  / "static"


# ✅ Copy entire UI folders 😈🔥
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
    Tornado Production Grade Generator 😈🔥
    Clean layered architecture + REAL UI
    """

    project_root.mkdir(parents=True, exist_ok=True)

    # ✅ Backend Folders 😌🔥
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

    # ✅ Python Packages 👍
    for package in folders:
        if package not in ["logs"]:
            (project_root / package / "__init__.py").touch()

    # ✅ ENTRYPOINT 😈🔥
    render_template(
        "tornado/production/entry.py.tpl",
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
    port = int(os.getenv("PORT", 8888))


settings = Settings()
""".strip() + "\n"
    )

    # ✅ ROUTES 👍
    (project_root / "routes" / "__init__.py").write_text(
        """
from .health import HealthHandler
from .auth import AuthHandler
from .api import ApiHandler


def register_routes():
    return [
        (r"/", ApiHandler),
        (r"/health", HealthHandler),
        (r"/auth", AuthHandler),
    ]
""".strip() + "\n"
    )

    # ✅ HANDLERS 👍
    (project_root / "routes" / "health.py").write_text(
        """
import tornado.web


class HealthHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"status": "healthy"})
""".strip() + "\n"
    )

    (project_root / "routes" / "auth.py").write_text(
        """
import tornado.web


class AuthHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"message": "Auth route ready"})
""".strip() + "\n"
    )

    (project_root / "routes" / "api.py").write_text(
        """
import tornado.web


class ApiHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")
""".strip() + "\n"
    )

    # ✅ ⭐ COPY REAL UI ⭐ 😈🔥
    copy_ui(project_root)

    # ✅ LOG / TEST 👍
    (project_root / "logs" / "app.log").touch()
    (project_root / "tests" / "test_health.py").touch()

    # 🔥 COMMON FILES 🔥
    render_template("common/requirements.txt.tpl", project_root / "requirements.txt", context)
    render_template("common/.env.tpl", project_root / ".env", context)
    render_template("common/README.md.tpl", project_root / "README.md", context)
    render_template("common/gitignore.tpl", project_root / ".gitignore", context)
