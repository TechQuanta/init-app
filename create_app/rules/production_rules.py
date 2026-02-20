"""
UNIFIED ARCHITECTURAL RULES (v0.2.4)
Focus: Flat-Root Enterprise Structure.
Frameworks: FastAPI, Pyramid, Flask, Django, Sanic, Falcon, Bottle, Tornado.
"""

PROD_WEB_RULES = {
    "FastAPI": {
        "packages": [
            "api",             # Versioned routes (v1/v2)
            "core",            # Config, Security, Events
            "database",        # Session engines & Engine setup
            "models",          # SQLAlchemy/Beanie models
            "schemas",         # Pydantic models
            "services",        # Business logic layer
            "repositories",    # Data access layer (Pattern)
            "migrations",      # Alembic versions
            "tests"
        ],
        "folders": ["docs", "logs", "static", "scripts", "requirements"]
    },
    "Tornado": {
        "packages": [
            "handlers",        # Request handlers (Async Routes)
            "core",            # IO Loop & App settings
            "database",        # Async drivers (Motor/Momoko)
            "models",          # Data definitions
            "services",        # Core logic
            "middleware",      # Auth & BaseHandler decorators
            "tests"
        ],
        "folders": [
            "static",          # Assets
            "templates",       # HTML/UI
            "logs", 
            "docs", 
            "scripts"
        ]
    },
    "Pyramid": {
        "packages": [
            "routes",          # Route mapping
            "views",           # Logic handlers
            "models",          # Persistence
            "services",        # Domain logic
            "security",        # ACL & Auth
            "schemas",         # Colander/Marshmallow
            "scripts",         # CLI commands
            "tests"
        ],
        "folders": ["static", "templates", "logs", "docs", "db/migrations"]
    },
    "Flask": {
        "packages": [
            "routes",          # Blueprints
            "database",        # SQLA setup
            "models",          # DB Models
            "services",        # Logic
            "migrations",      # Flask-Migrate
            "utils",           # Helpers
            "tests"
        ],
        "folders": ["templates", "static", "docs", "logs"]
    },
    "Django": {
        "packages": [
            "core",            # Settings/WSGI/ASGI
            "users",           # Custom User model app
            "api",             # REST views/serializers
            "common",          # Shared logic
            "tests"
        ],
        "folders": ["static", "templates", "media", "logs"]
    },
    "Sanic": {
        "packages": [
            "routes",          # Blueprint handlers
            "models",          # DB models
            "listeners",       # Setup/Teardown workers
            "services",        # Logic
            "tests"
        ],
        "folders": ["static", "docs", "logs", "scripts"]
    },
    "Falcon": {
        "packages": [
            "resources",       # Resource classes
            "middleware",      # Interceptors
            "database",        # Storage logic
            "logic",           # Business domain
            "tests"
        ],
        "folders": ["docs", "logs", "scripts"]
    },
    "Bottle": {
        "packages": [
            "routes",          # Decorated routes
            "services",        # Logic
            "models",          # Data
            "tests"
        ],
        "folders": ["views", "static", "docs", "logs"]
    }
}