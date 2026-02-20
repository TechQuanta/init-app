"""
STANDARD ARCHITECTURAL RULES (v0.2.1)
Focus: Lightweight, Rapid Prototyping Structure.
Pattern: Single 'app' package with minimal overhead.
"""

# 📂 Internal Rule Mapping for Standard Builds
# Consumed by Bundler._get_architectural_blueprint()
STANDARD_BLUEPRINT = {
    "FastAPI": {
        "packages": [
            "app", 
            "app/api",       # Basic route separation
            "tests"
        ], 
        "folders": ["static", "public", "docs", "logs"]
    },
    "Flask": {
        "packages": [
            "app", 
            "tests"
        ], 
        "folders": ["static", "templates", "public", "docs", "logs"]
    },
    "Bottle": {
        "packages": [
            "app", 
            "tests"
        ], 
        "folders": ["static", "views", "public", "docs", "logs"]
    },
    "Sanic": {
        "packages": [
            "app", 
            "tests"
        ], 
        "folders": ["static", "public", "docs", "logs"]
    },
    "Falcon": {
        "packages": [
            "app", 
            "tests"
        ], 
        "folders": ["public", "docs", "logs"]
    },
    "Tornado": {
        "packages": [
            "app", 
            "tests"
        ], 
        "folders": ["static", "templates", "public", "docs", "logs"]
    },
    "Pyramid": {
        "packages": [
            "app", 
            "tests"
        ], 
        "folders": ["static", "templates", "public", "docs", "logs"]
    }
}