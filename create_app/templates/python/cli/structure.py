from pathlib import Path
from create_app.generator.renderer import render_template

def generate(project_root: Path, context: dict):
    """
    🛠️  Python CLI Project Generator
    Scaffolds a package-based CLI tool ready for distribution.
    """

    # 📁 Initialize Root
    project_root.mkdir(parents=True, exist_ok=True)

    # 📦 Create the internal Package Directory
    # We use the project name as the folder name for: 'import project_name'
    pkg_name = context["project_name"].lower().replace("-", "_")
    package_dir = project_root / pkg_name
    package_dir.mkdir(exist_ok=True)

    # ✅ Initialize Package
    (package_dir / "__init__.py").touch()

    # ✅ Core CLI Logic
    # This is where the actual 'commands' will live
    cli_content = (
        'import sys\n\n'
        'def main():\n'
        '    """Main entry point for the CLI."""\n'
        f'    print("🚀 {context["project_name"]} CLI is active!")\n'
        '    if len(sys.argv) > 1:\n'
        '        print(f"Arguments received: {sys.argv[1:]}")\n\n\n'
        'if __name__ == "__main__":\n'
        '    main()\n'
    )
    (package_dir / "cli.py").write_text(cli_content.strip() + "\n", encoding="utf-8")

    # ✅ Entry Point (The caller file)
    render_template(
        "python/cli/main.py.tpl",
        project_root / "main.py",
        context,
    )

    # ✅ Common Files (Project Metadata)
    # Mapping templates to their final destination
    manifest = {
        "common/requirements.txt.tpl": "requirements.txt",
        "common/README.md.tpl": "README.md",
        "common/gitignore.tpl": ".gitignore",
        # 💡 Suggestion: add "common/setup.py.tpl" here later for pip install -e .
    }

    for tpl, output in manifest.items():
        render_template(tpl, project_root / output, context)

    print(f"✅ CLI scaffold ready in: {project_root.name} 😈🔥")
    return project_root