import pytest
import create_app

class TestAppLogic:

    def test_default_ports(self):
        """Check if every framework has its correct industry-standard port."""
        assert create_app.DEFAULT_PORTS["flask"] == "5000"
        assert create_app.DEFAULT_PORTS["fastapi"] == "8000"
        assert create_app.DEFAULT_PORTS["pyramid"] == "6543"

    def test_framework_metadata(self):
        """Ensure critical metadata exists in the exported constants."""
        assert "django" in create_app.FRAMEWORKS
        assert "others" in create_app.FRAMEWORKS
        # Updated to match DB_ENGINES in constants.py
        assert len(create_app.DB_ENGINES) > 0
        assert "postgresql" in create_app.DB_ENGINES

    def test_project_type_descriptions(self):
        """Verify that descriptions exist for the new project types."""
        # Check 'others' project types (RAG, Data Pipeline, etc)
        for p_type in create_app.OTHERS_PROJECT_TYPES:
            assert p_type in create_app.DESCRIPTIONS

    def test_suite_completeness(self):
        """Ensure DevOps suites are correctly defined as lists."""
        assert isinstance(create_app.DOCKER_SUITE, list)
        assert "docker/Dockerfile" in create_app.DOCKER_SUITE
        assert len(create_app.GITHUB_SUITE) > 0

    def test_mapping_logic(self):
        """Ensure framework to server/UI mappings are intact."""
        assert create_app.UI_MAPPING["flask"] == "templates"
        assert "uvicorn" in create_app.FRAMEWORK_SERVER_MAPPING["fastapi"]

    def test_public_api_contract(self):
        """Ensure __all__ contains the new Unified Architectural constants."""
        required = ["APP_NAME", "OTHERS_PROJECT_TYPES", "RAG_LAYERS", "DB_ENGINES"]
        for item in required:
            assert item in create_app.__all__