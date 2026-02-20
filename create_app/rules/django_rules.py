"""
DJANGO ENTERPRISE PATCH RULESET (v0.6.5)
Centralized Template Mapping: Points to create_app/common/
"""

DJANGO_PATCH_RULES = {
    "standard": {
        "folders": [
            "apps", 
            "core", 
            "static", 
            "templates", 
            "middleware",
            "templates/layouts"
        ],
        "packages": [
            "apps",
            "core",
            "middleware"
        ],
        "patches": [
            {
                "target": "settings.py",
                "template": "app.py.tpl", # Maps to common/app.py.tpl
            },
            {
                "target": "urls.py",
                "template": "urls.tpl",    # Maps to common/urls.tpl
            }
        ]
    },
    "drf": {
        "folders": [
            "api", 
            "core", 
            "static", 
            "middleware",
            "api/serializers",
            "api/viewsets"
        ],
        "packages": [
            "api",
            "core",
            "middleware",
            "api/serializers",
            "api/viewsets"
        ],
        "extra_files": [
            "api/serializers.py",
            "api/urls.py"
        ],
        "patches": [
            {
                "target": "settings.py",
                "template_secret": "secret.tpl",
                "template_apps": "app.py.tpl",
                "template_rest": "rf.py.tpl",
            },
            {
                "target": "urls.py",
                "template": "urls.tpl",
            }
        ]
    }
}