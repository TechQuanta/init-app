__version__ = "0.2.0"

APP_NAME = "init-app"
APP_TAGLINE = "Python Backend Project Generator"

# ✅ Supported Frameworks
FRAMEWORKS = [
    "Python",
    "Flask",
    "FastAPI",
    "Django",
    "Bottle",
    "Falcon",
    "Tornado",
    "Pyramid",
    "Sanic",
]

# ✅ Project Types for specialized Frameworks (Flask, FastAPI, etc.)
# We use "Standard" as the default high-quality starting point
PROJECT_STRUCTURES = ["Standard", "Production"]

STRUCTURE_DESCRIPTIONS = {
    "Standard": "Clean, modern foundation with essential configurations",
    "Production": "Enterprise-ready layout with tests, logs, and advanced scaling",
}

# ✅ Django Specifics
DJANGO_PROJECT_TYPES = ["Standard", "drf"]

DJANGO_DESCRIPTIONS = {
    "Standard": "Full Django project with default configuration",
    "drf": "Django project with REST Framework ready for API development",
}

# ✅ Python Specifics (The "Swiss Army Knife" category)
PYTHON_PROJECT_TYPES = [
    "Standard",               # Basic clean setup
    "CLI Application",        # Command-line tool structure
    "Library",                # PyPI-ready package structure
    "ML Labs",                # Data Science (TF, PyHive, MLflow)
]

PYTHON_DESCRIPTIONS = {
    "Standard": "Refined universal foundation with a clean structure",
    "CLI Application": "Professional CLI tool structure (Click/Rich integrated)",
    "Library": "Standardized PyPI-ready package structure (PEP 621)",
    "ML Labs": "Modern Data Science lab (TensorFlow, PyHive, MLflow tracking)",
}

# ✅ Environment & Database
VENV_OPTIONS = ["Yes (Recommended)", "No"]

DATABASE_OPTIONS = ["None", "SQLAlchemy", "PostgreSQL", "MySQL", "MongoDB"]

DATABASE_DESCRIPTIONS = {
    "None": "No database integration",
    "SQLAlchemy": "Database toolkit / ORM (flexible backend support)",
    "PostgreSQL": "Powerful production-grade relational database",
    "MySQL": "Popular relational database",
    "MongoDB": "NoSQL document database",
}

# ✅ Technical Configs
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

# 🚀 LIFT CORE COMPONENTS (Public API)
from create_app.ui.loader import Spinner
from create_app.ui.prompts import ask_project_details
from create_app.cli.engine import ProjectEngine 
from create_app.generator.generator import generate_project

# ✅ Public API Contract
__all__ = [
    "APP_NAME",
    "APP_TAGLINE",
    "FRAMEWORKS",
    "DJANGO_PROJECT_TYPES",
    "DJANGO_DESCRIPTIONS",
    "PROJECT_STRUCTURES",
    "PYTHON_PROJECT_TYPES",
    "PYTHON_DESCRIPTIONS",
    "STRUCTURE_DESCRIPTIONS",
    "VENV_OPTIONS",
    "DATABASE_OPTIONS",
    "DATABASE_DESCRIPTIONS",
    "DEFAULT_PORTS",
    "Spinner",
    "ask_project_details",
    "ProjectEngine",
    "generate_project",
]