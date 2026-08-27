from pathlib import Path


def test_dev_installer_provisions_dev_extras():
    installer = Path("scripts/install_dev.py").read_text(encoding="utf-8")
    assert '"-e", ".[dev]"' in installer
