import json

from create_app.initializer.controller import Controller


def test_mcp_scaffold_contains_registry_and_template(tmp_path):
    controller = Controller(
        {
            "project name": "demo_mcp",
            "core blueprint": "mcp (default)",
            "build strategy": "standard",
            "output_dir": str(tmp_path),
            "venv_enabled": False,
        },
        [],
    )
    controller.root = tmp_path / "demo_mcp"
    controller._write_mcp_scaffold()

    registry = json.loads((controller.root / "registry.json").read_text())
    assert registry["tools"][0]["path"] == "mcp-tools/_template"
    assert (controller.root / "mcp-tools/_template/server.py").exists()
    assert (controller.root / "config/mcp.config.json").exists()
