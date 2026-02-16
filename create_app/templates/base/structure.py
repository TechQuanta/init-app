from pathlib import Path
from create_app.generator.renderer import render_template


def generate(project_root: Path, context: dict):
    """
    Base Python Project Generator 😈🔥
    """

    project_root.mkdir(parents=True, exist_ok=True)

    folders = ["config", "utils", "tests"]

    for folder in folders:
        (project_root / folder).mkdir(exist_ok=True)
        (project_root / folder / "__init__.py").touch()

    # ✅ Entry File
    (project_root / "app.py").write_text(
        """
def main():
    print("🚀 Python App Running")


if __name__ == "__main__":
    main()
""".strip() + "\n"
    )

    # ✅ Common Files
    render_template("common/requirements.txt.tpl", project_root / "requirements.txt", context)
    render_template("common/README.md.tpl", project_root / "README.md", context)
    render_template("common/.gitignore.tpl", project_root / ".gitignore", context)
