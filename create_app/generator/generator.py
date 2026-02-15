from pathlib import Path
from create_app import DEFAULT_PORTS
from create_app.generator.venv import create_virtualenv

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


# ✅ Load framework dependencies
def load_dependencies(framework, structure):

    dependency_file = (
        TEMPLATE_DIR
        / framework.lower()
        / structure.lower()
        / "requirements.txt"
    )

    if not dependency_file.exists():
        return ""

    return dependency_file.read_text().strip()


# ✅ Merge dependencies safely
def merge_dependencies(base, db):

    if base and db:
        return f"{base}\n{db}"

    return base or db or ""


# ✅ Build template context
def build_context(project_name, framework, structure, dependencies):

    return {
        "project_name": project_name,
        "framework": framework,
        "structure": structure,
        "entrypoint": "app.py",
        "dependencies": dependencies,

        # ✅ Environment Defaults 😌🔥
        "debug": "True",
        "host": "127.0.0.1",
        "port": DEFAULT_PORTS.get(framework, "8000"),
    }



# ✅ Dynamic generator loader
def run_generator(project_root, framework, structure, context):

    module_path = (
        f"create_app.templates."
        f"{framework.lower()}."
        f"{structure.lower()}."
        f"structure"
    )

    try:
        module = __import__(module_path, fromlist=["generate"])
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"Generator not found → {module_path}")

    module.generate(project_root, context)


# ✅ MAIN GENERATION ENGINE 🔥
def generate_project(
    project_name,
    project_location,
    framework,
    structure,
    db_dependencies="",
    create_venv=False,
):

    project_root = Path(project_location or ".") / project_name

    # ✅ Always ensure directory exists
    project_root.mkdir(parents=True, exist_ok=True)

    base_dependencies = load_dependencies(framework, structure)

    dependencies = merge_dependencies(base_dependencies, db_dependencies)

    context = build_context(
        project_name,
        framework,
        structure,
        dependencies,
    )

    # ✅ Generate project structure
    run_generator(project_root, framework, structure, context)

    # ✅ Create virtualenv if requested 😏🔥
    if create_venv:
        create_virtualenv(project_root)

    return project_root
