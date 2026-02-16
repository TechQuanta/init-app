__version__ = "1.0.0"

APP_NAME = "py-create"
APP_TAGLINE = "Python Backend Project Generator"


# ✅ Supported Frameworks
FRAMEWORKS = [
    "Python",      # ✅ ADD THIS 😈🔥🔥🔥
    "Flask",
    "FastAPI",
    "Bottle",
    "Falcon",
    "Tornado",
    "Pyramid",
    "Sanic",
    "Django",
]



# ✅ Django Project Types
DJANGO_PROJECT_TYPES = [
    "Standard",
    "drf",
]


DJANGO_DESCRIPTIONS = {
    "Standard Django Project":
        "Full Django project with default configuration",

    "Django + REST Framework":
        "Django project with DRF ready for API development",
}


# ✅ Project Structures (Non-Django Frameworks)
PROJECT_STRUCTURES = [
    "Minimal",
    "Production",
]

PYTHON_PROJECT_TYPES = [
    "Base Python Project",
    "Python CLI Application",
    "Python Library",
]


PYTHON_DESCRIPTIONS = {
    "Base Python Project": "Simple Python starter structure",
    "Python CLI Application": "Command-line tool structure",
    "Python Library": "Reusable pip-installable package",
}




STRUCTURE_DESCRIPTIONS = {
    "Minimal":
        "Single app entry file (quick start, lightweight setup)",

    "Production":
        "Structured layout (apps, models, routes, logs, configs, tests)",
}


# ✅ Public Components Re-export
from create_app.loader import Spinner
from create_app.prompts import ask_project_details


# ✅ Public API Contract
__all__ = [
    "APP_NAME",
    "APP_TAGLINE",
    "FRAMEWORKS",
    "DJANGO_PROJECT_TYPES",
    "PROJECT_STRUCTURES",
    "DJANGO_DESCRIPTIONS",
    "STRUCTURE_DESCRIPTIONS",
    "Spinner",
    "ask_project_details",
]

VENV_OPTIONS = [
    "Yes (Recommended)",
    "No"
]

DATABASE_OPTIONS = [
    "None",
    "SQLAlchemy",
    "PostgreSQL",
    "MySQL",
    "MongoDB",
]

DATABASE_DESCRIPTIONS = {
    "None": "No database integration",

    "SQLAlchemy": "Database toolkit / ORM (flexible backend support)",

    "PostgreSQL": "Powerful production-grade relational database",

    "MySQL": "Popular relational database",

    "MongoDB": "NoSQL document database",
}

# ✅ Default Ports Per Framework 😌🔥

DEFAULT_PORTS = {
    "Flask": "5000",
    "FastAPI": "8000",
    "Django": "8000",
    "Sanic": "8000",
    "Tornado": "8888",
    "Falcon": "8000",
    "Bottle": "8080",
    "Pyramid": "6543",
}
