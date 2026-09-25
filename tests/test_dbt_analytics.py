from pathlib import Path
from unittest.mock import patch

from create_app.dbt_support import ensure_user_profile, resolve_adapter
from create_app.initializer.controller import Controller


def dbt_manifest(tmp_path):
    return {
        "project name": "finance-transform",
        "core blueprint": "dbt_analytics (na)",
        "framework": "dbt_analytics",
        "build strategy": "standard",
        "database": "none",
        "output_dir": str(tmp_path),
        "venv_enabled": False,
        "dbt_adapter": "snowflake",
        "dbt_profile": "finance",
        "dbt_target": "dev",
    }


def test_user_profile_is_credential_free_and_is_not_overwritten(tmp_path):
    home = tmp_path / "home"
    adapter = resolve_adapter("snowflake")
    path, created = ensure_user_profile(home, "finance", "dev", adapter)

    assert created is True
    content = path.read_text(encoding="utf-8")
    assert "type: snowflake" in content
    assert "env_var('DBT_SNOWFLAKE_PASSWORD')" in content
    assert "password: actual-secret" not in content

    _, created_again = ensure_user_profile(home, "finance", "dev", adapter)
    assert created_again is False
    assert path.read_text(encoding="utf-8") == content


def test_controller_creates_project_profile_example_and_user_profile(tmp_path):
    controller = Controller(dbt_manifest(tmp_path), [])
    controller.root = tmp_path / "finance-transform"
    controller._sync_project_paths()
    controller.root.mkdir()

    with patch("create_app.initializer.controller.Path.home", return_value=tmp_path / "home"):
        controller._handle_dbt_analytics()

    assert (controller.root / "dbt_project.yml").exists()
    assert (controller.root / ".dbt" / ".env.example").exists()
    profile = tmp_path / "home" / ".dbt" / "profiles.yml"
    assert "finance:" in profile.read_text(encoding="utf-8")


def test_native_dbt_init_is_the_first_choice(tmp_path):
    controller = Controller(dbt_manifest(tmp_path), [])
    controller.root = tmp_path / "finance-transform"
    controller._sync_project_paths()
    with patch("create_app.initializer.controller.subprocess.run") as run:
        controller._run_dbt_init()
    assert run.call_args.args[0] == ["dbt", "init", "--skip-profile-setup", "finance-transform"]
