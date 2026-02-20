import pytest
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import from your new structure
from create_app.initializer.controller import Controller
from create_app.logger import logger

# The Matrix now maps to your Build Strategies and Frameworks
# (framework, blueprint_raw, strategy)
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
    """Helper to create a base manifest dictionary."""
    def _create(fw, bp, strategy):
        return {
            "project name": "test_project",
            "app_name": "test_app",
            "core blueprint": bp,
            "build strategy": strategy,
            "framework": fw,
            "infra_files": {"github": ["main.yml.tpl"]}
        }
    return _create

@pytest.mark.parametrize("fw, bp, strategy", TEST_MATRIX)
def test_controller_mission_orchestration(fw, bp, strategy, tmp_path, mock_manifest):
    """
    STRESS TEST: Verifies the Controller can run a full mission.
    Mocks subprocess to avoid slow venv/pip/django-admin calls.
    """
    # 1. Setup paths
    os.chdir(tmp_path)
    manifest = mock_manifest(fw, bp, strategy)
    custom_folders = ["extra_assets", "docs"]
    
    # 2. Mock external systems
    with patch("subprocess.run") as mock_run, \
         patch("docs.prerequisite.Prerequisite.check_system") as mock_check:
        
        mock_run.return_value.returncode = 0
        mock_check.return_value = {"status": True, "errors": []}
        
        try:
            # 3. Initialize Controller
            ctrl = Controller(manifest, custom_folders)
            
            # 4. Run the mission
            # We point the root to our tmp_path
            ctrl.root = tmp_path / "test_project"
            ctrl.run_mission()
            
            # 5. Assertions
            project_dir = tmp_path / "test_project"
            assert project_dir.exists(), f"❌ Project directory not created for {fw}"
            
            # Check for core entry file (remapped to app.py in your logic)
            assert (project_dir / "app.py").exists() or (project_dir / "manage.py").exists(), \
                f"❌ Entry point missing for {fw}"

            # Check if ghost UI folder was purged
            assert not (project_dir / "ui").exists(), "❌ Ghost UI folder was not purged!"

            logger.info(f"✅ PASSED: {fw} | {strategy}")

        except Exception as e:
            pytest.fail(f"💥 Mission failed for {fw}/{strategy}: {e}")

def test_bundler_dependency_resolution(mock_manifest):
    """Verifies the Bundler correctly calculates dependencies."""
    from framework.bundler import Bundler
    
    # Test Django + DRF
    manifest = mock_manifest("django", "Django + Rest Framework", "standard")
    manifest["is_drf"] = True
    
    bundler = Bundler(Path("/tmp"), manifest)
    deps = bundler.ctx.get("dependencies", "")
    
    assert "django" in deps.lower()
    assert "djangorestframework" in deps.lower()
    assert "psycopg2-binary" in deps.lower()
    
    # Test RAG AI project type
    manifest["project_type"] = "rag_ai"
    bundler = Bundler(Path("/tmp"), manifest)
    deps = bundler.ctx.get("dependencies", "")
    assert "langchain" in deps.lower()
    assert "chromadb" in deps.lower()

def test_prerequisite_engine():
    """Checks if the safety engine correctly identifies missing tools."""
    from docs.prerequisite import Prerequisite
    
    with patch("shutil.which", return_value=None):
        result = Prerequisite.check_system()
        assert result["status"] is False
        assert any("Pip" in err for err in result["errors"])