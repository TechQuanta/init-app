import importlib
import re
import importlib.util
from pathlib import Path

# 🟢 Custom Logger & Config Imports
from create_app.ui.logger import logger, log_info, log_error
from create_app import DEFAULT_PORTS
from create_app.generator.venv import create_virtualenv

# 📁 Template Source
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

def normalize(name: str) -> str:
    """
    Standardizes names for folders and modules.
    Maps UI display names to physical template folder names.
    """
    clean = name.lower().strip()
    
    # ⚡ Updated Mapping to match your clean UI in __init__.py
    mapping = {
        "ml labs": "mllabs",           # Maps "ML Labs" -> mllabs/
        "cli application": "cli",      # Maps "CLI Application" -> cli/
        "library": "library",          # Maps "Library" -> library/
        "normal": "base",
        "standard":"minimal",
        "production": "production",    # Standard production structure
        "drf": "drf"                   # Django Rest Framework
    }
    
    if clean in mapping:
        return mapping[clean]

    # Fallback: Replace spaces/hyphens with underscores for framework names
    return re.sub(r"[^a-z0-9_]", "_", clean)

def load_dependencies(framework, structure):
    """🔍 Locates requirements.txt based on the chosen stack."""
    path_parts = [normalize(framework), normalize(structure), "requirements.txt"]
    dependency_file = TEMPLATE_DIR.joinpath(*path_parts)

    logger.info(f"Searching for requirements at: {dependency_file}")

    if not dependency_file.exists():
        logger.warning(f"No requirements.txt found for {framework}/{structure}")
        return ""

    return dependency_file.read_text().strip()

def merge_dependencies(base, db):
    """🛠️ Combines base and DB requirements while removing duplicates."""
    logger.info("Merging base and database dependencies...")
    if not base and not db:
        return ""
    
    all_deps = set((base or "").splitlines()) | set((db or "").splitlines())
    return "\n".join(filter(None, all_deps))

def build_context(project_name, framework, structure, dependencies):
    """🏗️ Prepares the global variables for template injection."""
    logger.info(f"Building template context for project: {project_name}")
    
    # Clean project name for internal package naming (snake_case)
    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())

    # ✅ Logic for internal directory/app naming and entrypoints
    f_low = framework.lower()
    s_low = structure.lower()

    if f_low == "django":
        app_name = "core"
        entrypoint = "manage.py"
    elif s_low == "cli application":
        app_name = safe_name
        entrypoint = "main.py"
    elif s_low == "library":
        app_name = safe_name
        entrypoint = None # Libraries don't usually have a single entry app.py
    else:
        app_name = safe_name
        entrypoint = "app.py"

    colors = {
        "Python": "3776ab", "Flask": "000000", "FastAPI": "05998b",
        "Django": "092e20", "Bottle": "e33e38", "Falcon": "ffdf00",
        "Tornado": "005f87", "Sanic": "ff0068", "Pyramid": "313333"
    }

    logos = {
        "Python": "python", "Flask": "flask", "FastAPI": "fastapi",
        "Django": "django", "Sanic": "sanic", "Pyramid": "pyramid",
        "Bottle": "python", "Tornado": "python", "Falcon": "python",
    }

    return {
        "project_name": project_name,
        "app_name": app_name, 
        "framework": framework,
        "structure": structure,
        "entrypoint": entrypoint,
        "dependencies": dependencies,
        "debug": "True",
        "host": "127.0.0.1",
        "port": DEFAULT_PORTS.get(framework, "8000"),
        "accent_color": colors.get(framework, "3776ab"),
        "framework_logo": logos.get(framework, "python")
    }

def run_generator(project_root, framework, structure, context):
    """🚀 Dynamically imports and runs the framework-specific generator."""
    f_mod = normalize(framework)
    s_mod = normalize(structure)
    
    module_path = f"create_app.templates.{f_mod}.{s_mod}.structure"

    expected_dir = TEMPLATE_DIR / f_mod / s_mod
    structure_file = expected_dir / "structure.py"

    logger.info(f"Searching for generator file at: {structure_file}")

    if not structure_file.exists():
        logger.error(f"Missing structure.py at {structure_file}")
        raise FileNotFoundError(
            f"\n❌ Generator Not Found!\n"
            f"Expected file: {structure_file}\n"
            f"Check that your folder is named '{s_mod}' inside 'templates/{f_mod}/'"
        )

    # 💡 Package Validation (__init__.py checks)
    missing_inits = []
    for folder in [TEMPLATE_DIR, TEMPLATE_DIR / f_mod, expected_dir]:
        if not (folder / "__init__.py").exists():
            missing_inits.append(str(folder))

    if missing_inits:
        logger.warning(f"Missing __init__.py in: {missing_inits}")

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        logger.error(f"Import failed for {module_path}", exc_info=True)
        fix_cmd = " && ".join([f"touch {m}/__init__.py" for m in missing_inits])
        raise ModuleNotFoundError(
            f"\n❌ Python cannot import the template.\n"
            f"Reason: {e}\n"
            f"Try running this: {fix_cmd if missing_inits else 'Check module path'}"
        ) from e

    if not hasattr(module, "generate"):
        logger.error(f"Module {module_path} is missing the 'generate' function")
        raise AttributeError(f"Invalid generator: 'generate' function missing in {structure_file}")

    return module.generate(project_root, context)

def generate_project(
    project_name,
    project_location,
    framework,
    structure,
    db_dependencies="",
    create_venv=False,
    extra_context=None,
):
    """⚡ The Big Bang: Orchestrates the entire project creation."""
    project_root = (Path(project_location or ".") / project_name).resolve()
    
    logger.info(f"🚀 GENERATION START: {project_name} at {project_root}")

    try:
        # 🧬 Setup Content
        base_dependencies = load_dependencies(framework, structure)
        dependencies = merge_dependencies(base_dependencies, db_dependencies)

        # 📋 Build Context
        context = build_context(project_name, framework, structure, dependencies)
        if extra_context:
            context.update(extra_context)

        # 🚧 Initialize Directory (Django handles its own directory creation)
        if framework.lower() != "django":
            project_root.mkdir(parents=True, exist_ok=True)

        # ✨ Run Generator (imports from create_app.templates...)
        actual_root = run_generator(project_root, framework, structure, context)
        final_root = actual_root or project_root

        # 🐍 Post-Generation: Virtual Environment
        if create_venv:
            create_virtualenv(final_root)

        logger.info(f"🏁 GENERATION SUCCESS: {project_name}")
        return final_root

    except Exception as e:
        logger.critical(f"FATAL ERROR during generation of {project_name}", exc_info=True)
        raise e