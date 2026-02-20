import time
import sys
from create_app.engine.ui.ui_config import UIConfig

class BuildPrompts:
    """
    Identity & Strategy Resolver:
    Handles dynamic naming and framework-specific folder mapping.
    """
    def __init__(self, ui_instance, constants_module):
        self.ui = ui_instance
        self.const = constants_module  # create_app.constants

    def get_project_name(self):
        """
        Standalone Project Name prompt for Auto-Config or Quick Starts.
        Prevents 'AttributeError' in AppEngine.
        """
        p_name = ""
        while not p_name:
            label = UIConfig.paint("PROJECT NICKNAME", "bold")
            prompt = UIConfig.paint("▶ ", "accent")
            sys.stdout.write(f"\n  {label}\n  {prompt}")
            sys.stdout.flush()
            
            p_name = input().strip().lower().replace(" ", "_")
            if not p_name:
                sys.stdout.write(UIConfig.paint("  ✖ error: project name is required.\n", "accent"))
        return p_name

    def collect_identity(self, fw, mode):
        """
        Collects Project and App names with consistent UI styling.
        Handles both Standard and Django-specific flows.
        """
        fw_clean, mode_clean = fw.lower(), mode.lower()
        self.ui.header("finalizing identity", "accent")
        
        # 1. Get Project Name using the internal method
        p_name = self.get_project_name()

        # 2. Django App Sequence (Only triggered for Django builds)
        apps = []
        if "django" in fw_clean:
            counts = [str(i).zfill(2) for i in range(1, 11)]
            sub_map = {"initialize apps": counts}
            
            # Using the UI menu to pick number of apps
            _, count_val = self.ui.menu(
                "app configuration", 
                ["Initialize Apps"], 
                sub_mapping=sub_map,
                flow=[fw_clean, "identity", "apps"]
            )
            
            try:
                app_count = int(count_val)
            except (ValueError, TypeError):
                app_count = 1 

            for i in range(app_count):
                app_val = ""
                while not app_val:
                    label = UIConfig.paint(f"NAME FOR APP {i+1}", "bold")
                    prompt = UIConfig.paint("▶ ", "accent")
                    sys.stdout.write(f"\n  {label}\n  {prompt}")
                    sys.stdout.flush()
                    app_val = input().strip().lower().replace(" ", "_")
                    if not app_val:
                        sys.stdout.write(UIConfig.paint("  ✖ error: app name cannot be empty.\n", "accent"))
                apps.append(app_val)
        
        return p_name, apps

    def get_smart_folders(self, fw, mode, domain_folders):
        """
        DYNAMIC FOLDER MAPPING:
        Synchronizes framework needs with build strategy.
        Uses a fallback chain to ensure no project is born empty.
        """
        fw, mode = fw.lower(), mode.lower()
        folders = set()
        
        # 1. Framework-Specific Structural Cores
        if "django" in fw:
            folders.update(["apps", "core", "static", "templates", "middleware"])
        elif "rag_ai" in fw:
            # Fallback to defaults if constants aren't defined
            layers = getattr(self.const, 'RAG_LAYERS', ["src/engine", "src/storage", "src/prompts", "data/vector_store"])
            folders.update(layers)
        elif "data_pipeline" in fw:
            layers = getattr(self.const, 'DATA_LAYERS', ["src/dags", "src/transformers", "staging", "sql"])
            folders.update(layers)
        elif "fastapi" in fw or "flask" in fw:
            folders.update(["api", "core", "services", "models", "schemas"])
        elif "native_cpp" in fw:
            folders.update(["src", "include", "tests", "build"])
        else:
            # Generic High-Performance Baseline
            folders.update(["src", "tests", "config", "utils"])

        # 2. Strategy Injections
        # Production/Custom builds get the full Enterprise suite
        if mode in ["production", "custom", "auto_config"]:
            # Inject domain folders (Standard generic list)
            if domain_folders:
                folders.update(domain_folders)
            
            # Maintenance & Ops Layers
            folders.update(["docs", "scripts", "logs"])
            
        # Clean out any empty strings or 'none' tags
        return sorted([f for f in folders if f and f.lower() != "none"])