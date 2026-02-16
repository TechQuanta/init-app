# create_app/constants.py

__version__ = "0.2.3"

APP_NAME = "init-app"
APP_TAGLINE = "Python Backend Project Generator"

# ✅ Supported Frameworks
FRAMEWORKS = [
    "Python", "Flask", "FastAPI", "Django", "Bottle", 
    "Falcon", "Tornado", "Pyramid", "Sanic"
]

PROJECT_STRUCTURES = ["Standard", "Production"]

STRUCTURE_DESCRIPTIONS = {
    "Standard": "Clean, modern foundation with essential configurations",
    "Production": "Enterprise-ready layout with tests, logs, and advanced scaling",
}

DJANGO_PROJECT_TYPES = ["Standard", "drf"]

DJANGO_DESCRIPTIONS = {
    "Standard": "Full Django project with default configuration",
    "drf": "Django project with REST Framework ready for API development",
}

PYTHON_PROJECT_TYPES = [
    "Standard", 
    "CLI Application", 
    "Library", 
    "ML Labs"
]

PYTHON_DESCRIPTIONS = {
    "Standard": "Refined universal foundation with a clean structure",
    "CLI Application": "Professional CLI tool structure (Click/Rich integrated)",
    "Library": "Standardized PyPI-ready package structure (PEP 621)",
    "ML Labs": "Modern Data Science lab (TensorFlow, PyHive, MLflow tracking)",
}

VENV_OPTIONS = ["Yes (Recommended)", "No"]
DATABASE_OPTIONS = ["None", "SQLAlchemy", "PostgreSQL", "MySQL", "MongoDB"]

DATABASE_DESCRIPTIONS = {
    "None": "No database integration",
    "SQLAlchemy": "Database toolkit / ORM (flexible backend support)",
    "PostgreSQL": "Powerful production-grade relational database",
    "MySQL": "Popular relational database",
    "MongoDB": "NoSQL document database",
}

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