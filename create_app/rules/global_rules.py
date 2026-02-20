"""
GLOBAL ARCHITECTURAL RULES (v1.1.0)
Focus: Universal Root Metadata and Strict UI Filtering.
"""

# ✅ Root Package Rules (Standardized for all builds)
CORE_METADATA_FILES = {
    "gitignore.tpl":        ".gitignore",
    "README.md.tpl":        "README.md",
    "requirements.txt.tpl": "requirements.txt",
    "env.tpl":              ".env",
    "Makefile.tpl":         "Makefile" 
}

def get_global_manifest(context: dict):
    """
    Returns the mapping of global templates to their final project paths.
    Strictly filters 'ui' to prevent ghost folders in RAG/API projects.
    """
    manifest = []
    fw = str(context.get("fw_name", context.get("framework", "fastapi"))).lower()
    is_drf = context.get("is_drf", False)
    app_name = context.get("app_name", "core_app")
    
    # 1. Map Core Metadata (Project Root)
    # Note: We don't force a root __init__.py unless the project is a package.
    for tpl, output in CORE_METADATA_FILES.items():
        manifest.append({
            "source": tpl,  # Generator handles pathing via search_paths
            "target": output
        })

    # 2. 🚨 THE UI FILTER (The Ghost Killer)
    # We ONLY add index.html if it's Standard Django (SSR).
    # We place it inside the internal app folder, NEVER at the root 'ui/'
    if "django" in fw and not is_drf:
        manifest.append({
            "source": "index.html.tpl",
            "target": f"{app_name}/templates/index.html"
        })
    # If it's RAG, FastAPI, or others, we do NOT append any UI files here.

    # 3. Entrypoint Logic (The 'app.py' Standard)
    # Django uses manage.py (handled by Controller), so we exclude app.py for Django.
    if "django" not in fw:
        manifest.append({
            "source": "app.py.tpl",
            "target": "app.py"
        })

    return manifest