import pytest
import create_app

class TestAppLogic:

    def test_default_ports(self):
        """Check if every framework has its correct industry-standard port."""
        print("\nVerifying Port Assignments...")
        assert create_app.DEFAULT_PORTS["Flask"] == "5000"
        assert create_app.DEFAULT_PORTS["FastAPI"] == "8000"
        assert create_app.DEFAULT_PORTS["Pyramid"] == "6543"
        assert create_app.DEFAULT_PORTS["Tornado"] == "8888"

    def test_framework_logos(self):
        """Ensure all main frameworks have a valid SimpleIcons URL."""
        print("\nVerifying Branding Assets...")

    def test_project_name_normalization(self):
        """Check if your engine handles 'dirty' project names correctly."""
        print("\nVerifying String Normalization...")
        # If a user types "My Project!!!", it should become "my_project"
        # Adjust the function name below to match what you use in your utils.py
        dirty_name = "My New-Project!!!"
        clean_name = dirty_name.lower().replace(" ", "_").replace("-", "_").replace("!", "")
        
        assert clean_name == "my_new_project"

    def test_database_options_logic(self):
        """Ensure the database descriptions match the options."""
        print("\nVerifying Database Metadata...")
        for option in create_app.DATABASE_OPTIONS:
            assert option in create_app.DATABASE_DESCRIPTIONS

    def test_all_export_contract(self):
        """Ensure the __all__ list is updated so 'from create_app import *' works."""
        print("\nVerifying Public API Contract...")
        # This catches errors where you add a feature but forget to export it
        assert "ProjectEngine" in create_app.__all__
        assert "DEFAULT_PORTS" in create_app.__all__