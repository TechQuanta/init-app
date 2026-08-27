from pathlib import Path


def test_environment_example_is_safe_to_commit():
    example_template = Path("create_app/common/env.example.tpl").read_text(encoding="utf-8")
    assert "SECRET_KEY=change-me-before-production" in example_template


def test_entrypoint_loads_dotenv_and_validates_port():
    entrypoint = Path("create_app/common/entry.py.tpl").read_text(encoding="utf-8")
    assert 'load_dotenv(BASE_DIR / ".env")' in entrypoint
    assert "def environment_port()" in entrypoint
    assert "1 <= port <= 65535" in entrypoint
