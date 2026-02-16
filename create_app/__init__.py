# create_app/__init__.py

from .constants import *

# We only export the constants here. 
# The engine and generator are called directly by the CLI entry point.
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
]