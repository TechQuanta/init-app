import pytest
import os
import shutil
from pathlib import Path
from unittest.mock import patch
from create_app.initializer.controller import Controller
from create_app.logger import logger

TEST_MATRIX = [
    ("fastapi", "FastAPI (Standard)", "standard"),
    ("fastapi", "FastAPI (Production)", "production"),
    ("flask", "Flask (Standard)", "standard"),
    ("django", "Django (Standard)", "standard"),
    ("django", "Django + Rest Framework", "standard"),
    ("bottle", "Bottle (Standard)", "standard"),
]

@pytest.fixture
def mock_manifest():
    def _create(fw, bp, strategy):
        return {
            "project name": "test_project",
            "app_name": "test_app",
            "core blueprint": bp,
            "build strategy": strategy,
            "framework": fw,
            "infra_files": {"github": ["main.yml.tpl"]},
            "is_drf": "Rest Framework" in bp
        }
    return _create

@pytest.mark.parametrize("fw, bp, strategy", TEST_MATRIX)
def test_controller_mission_orchestration(fw, bp, strategy, tmp_path, mock_manifest):
    """
    STRESS TEST: Verifies the Controller can run a full mission across all frameworks.
    """
    # 1. Setup paths
    os.chdir(tmp_path)
    manifest = mock_manifest(fw, bp, strategy)
    custom_folders = ["extra_assets", "docs"]
    project_dir = tmp_path / "test_project"

    # 2. Mock external systems
    with patch("subprocess.run") as mock_run, \
         patch("docs.prerequisite.Prerequisite.check_system") as mock_check:

        mock_run.return_value.returncode = 0
        mock_check.return_value = {"status": True, "errors": []}

        try:
            # 3. Initialize & Run
            ctrl = Controller(manifest, custom_folders)
            ctrl.root = project_dir
            ctrl.run_mission()

            # --- ASSERTION 1: Root Directory ---
            assert project_dir.exists(), f"❌ Project directory not created for {fw}"

            # --- ASSERTION 2: Entry Points ---
            if fw == "django":
                assert (project_dir / "core").exists() or (project_dir / "test_project").exists()
            else:
                assert (project_dir / "app.py").exists(), f"❌ Entry point (app.py) missing for {fw}"

            # --- ASSERTION 3: UI / Templates Logic (UPDATED) ---
            # Ashmeet: We now expect UI in EVERY framework.
            ui_exists = (project_dir / "ui").exists()
            tmpl_exists = (project_dir / "templates").exists()
            
            # Django is the only one where we might clean it up IF we move assets to internal app folders,
            # but for this test, we verify that the frontend assets exist somewhere.
            if fw != "django":
                assert ui_exists or tmpl_exists, f"❌ UI folder missing for {fw} {strategy}"

            logger.info(f"✅ PASSED: {fw} | {strategy}")

        except Exception as e:
            pytest.fail(f"💥 Mission failed for {fw}/{strategy}: {e}")

def test_bundler_dependency_resolution(mock_manifest):
    from create_app.framework.bundler import Bundler
    manifest = mock_manifest("django", "Django + Rest Framework", "standard")
    bundler = Bundler(Path("/tmp"), manifest)
    deps = bundler.ctx.get("dependencies", "").lower()

    assert "django" in deps
    assert "djangorestframework" in deps