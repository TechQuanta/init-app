from pathlib import Path
import importlib
import re

from create_app import DEFAULT_PORTS
from create_app.generator.venv import create_virtualenv

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


# ✅ Normalize names (CRITICAL 🔥🔥🔥)
def normalize(name: str) -> str:
    """
    Converts:
    "Production Grade" → production_grade
    "FastAPI" → fastapi
    "my-app" → my_app
    """
    return re.sub(r"[^a-z0-9_]", "_", name.lower())


# ✅ Load framework dependencies
def load_dependencies(framework, structure):

    dependency_file = (
        TEMPLATE_DIR
        / normalize(framework)
        / normalize(structure)
        / "requirements.txt"
    )

    if not dependency_file.exists():
        return ""

    return dependency_file.read_text().strip()


# ✅ Merge dependencies safely 😌🔥
def merge_dependencies(base, db):

    if not base and not db:
        return ""

    if base and db:
        return f"{base}\n{db}"

    return base or db


# ✅ Build template context 😈🔥
def build_context(project_name, framework, structure, dependencies):

    return {
        "project_name": project_name,
        "framework": framework,
        "structure": structure,
        "entrypoint": "app.py",
        "dependencies": dependencies,
        "debug": "True",
        "host": "127.0.0.1",
        "port": DEFAULT_PORTS.get(framework, "8000"),
    }


# ✅ Dynamic generator loader 🔥🔥🔥
def run_generator(project_root, framework, structure, context):

    module_path = (
        f"create_app.templates."
        f"{normalize(framework)}."
        f"{normalize(structure)}."
        f"structure"
    )

    try:
        module = importlib.import_module(module_path)

    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            f"\n❌ Generator not found\n"
            f"Expected → {module_path}\n"
            f"Check folder naming inside templates/\n"
        )

    if not hasattr(module, "generate"):
        raise AttributeError(
            f"\n❌ Invalid generator module\n"
            f"{module_path}\n"
            f"'generate(project_root, context)' missing\n"
        )

    # ✅ ⭐ CRITICAL ⭐
    return module.generate(project_root, context)


# ✅ MAIN GENERATION ENGINE 😈🔥🔥🔥
def generate_project(
    project_name,
    project_location,
    framework,
    structure,
    db_dependencies="",
    create_venv=False,
    extra_context=None,
):

    project_root = Path(project_location or ".") / project_name

    base_dependencies = load_dependencies(framework, structure)
    dependencies = merge_dependencies(base_dependencies, db_dependencies)

    context = build_context(
        project_name,
        framework,
        structure,
        dependencies,
    )

    if extra_context:
        context.update(extra_context)

    # ✅ ⭐ CRITICAL FIX ⭐ 😈🔥🔥🔥
    if framework != "Django":
        project_root.mkdir(parents=True, exist_ok=True)

    # ✅ Let framework generator decide structure
    actual_root = run_generator(project_root, framework, structure, context)

    final_root = actual_root or project_root

    # ✅ Virtualenv AFTER generation 👍🔥
    if create_venv:
        try:
            create_virtualenv(final_root)
        except Exception as e:
            raise RuntimeError(
                f"\n❌ Virtualenv creation failed\n{str(e)}\n"
            )

    return final_root
