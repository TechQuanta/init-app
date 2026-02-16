import sys
from pathlib import Path
from create_app.generator.renderer import render_template

TEMPLATE_DIR = Path(__file__).parent

def load_dependencies():
    dependency_file = TEMPLATE_DIR / "requirements.txt"
    return dependency_file.read_text().strip() if dependency_file.exists() else ""

def generate(project_root: Path, context: dict):
    """
    Python Library Generator 📚🔥
    Creates a structure ready for PyPI (PEP 517/621)
    """
    project_name = context["project_name"]
    # For libraries, the package name should be snake_case
    package_name = project_name.lower().replace("-", "_")
    
    project_root.mkdir(parents=True, exist_ok=True)

    # 1. ✅ Main Package Folder (The code you import)
    package_dir = project_root / package_name
    package_dir.mkdir(exist_ok=True)

    # 2. ✅ Package Init with Version
    (package_dir / "__init__.py").write_text(f'__version__ = "0.1.0"\n')
    
    # 3. ✅ Core Logic File
    (package_dir / "core.py").write_text(f"""
def hello():
    return "Hello from {project_name}!"
""")

    # 4. ✅ Tests Folder
    tests_dir = project_root / "tests"
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / "__init__.py").touch()
    (tests_dir / "test_core.py").write_text(f"""
from {package_name}.core import hello

def test_hello():
    assert "Hello" in hello()
""")

    # 5. ✅ PyPI Packaging (pyproject.toml) 😈🔥
    # This is the modern replacement for setup.py
    (project_root / "pyproject.toml").write_text(f"""
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name}"
version = "0.1.0"
authors = [
  {{ name="Ashmeet Singh", email="your-email@example.com" }},
]
description = "A professional Python library created by py-create"
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

[project.urls]
"Homepage" = "https://github.com/user/{project_name}"
""".strip() + "\n")

    # 6. ✅ Common Files
    context.update({
        "dependencies": load_dependencies(),
        "package_name": package_name
    })

    # Ensure these templates exist in your common folder!
    render_template("common/README.md.tpl", project_root / "README.md", context)
    render_template("common/.env.tpl", project_root / ".env", context)
    
    # Use the dot naming you have in your common folder
    render_template("common/gitignore.tpl", project_root / ".gitignore", context)

    return project_root