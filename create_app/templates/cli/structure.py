from pathlib import Path
from create_app.generator.renderer import render_template


def generate(project_root: Path, context: dict):
    """
    Python CLI Project Generator 😈🔥
    """

    project_root.mkdir(parents=True, exist_ok=True)

    package_dir = project_root / context["project_name"]
    package_dir.mkdir(exist_ok=True)

    # ✅ Python Package
    (package_dir / "__init__.py").touch()

    # ✅ CLI Logic
    (package_dir / "cli.py").write_text(
        """
def main():
    print("🚀 CLI Tool Running")


if __name__ == "__main__":
    main()
""".strip() + "\n"
    )

    # ✅ Entry Point
    render_template(
        "python/cli/main.py.tpl",
        project_root / "main.py",
        context,
    )

    # ✅ Common Files
    render_template("common/requirements.txt.tpl", project_root / "requirements.txt", context)
    render_template("common/README.md.tpl", project_root / "README.md", context)
    render_template("common/.gitignore.tpl", project_root / ".gitignore", context)
