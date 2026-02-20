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
        self.c = constants_module  # create_app.constants

    def collect_identity(self, fw, mode):
        """Collects Project and App names with consistent UI styling."""
        fw_clean, mode_clean = fw.lower(), mode.lower()
        self.ui.header("finalizing identity", "accent")
        
        # 1. Project Nickname (Required)
        p_name = ""
        while not p_name:
            # Using UIConfig colors for the prompt
            label = UIConfig.paint("PROJECT NICKNAME", "bold")
            prompt = UIConfig.paint("▶ ", "accent")
            sys.stdout.write(f"\n  {label}\n  {prompt}")
            sys.stdout.flush()
            
            p_name = input().strip().lower()
            if not p_name:
                sys.stdout.write(UIConfig.paint("  ✖ error: project name is required.\n", "accent"))

        # 2. Django App Sequence
        apps = []
        if "django" in fw_clean:
            counts = [str(i).zfill(2) for i in range(1, 11)]
            sub_map = {"initialize apps": counts}
            _, count_val = self.ui.menu("app configuration", ["Initialize Apps"], sub_mapping=sub_map)
            
            try:
                app_count = int(count_val)
            except:
                app_count = 1 

            for i in range(app_count):
                app_val = ""
                while not app_val:
                    label = UIConfig.paint(f"NAME FOR APP {i+1}", "bold")
                    prompt = UIConfig.paint("▶ ", "accent")
                    sys.stdout.write(f"\n  {label}\n  {prompt}")
                    sys.stdout.flush()
                    app_val = input().strip().lower()
                apps.append(app_val)
        
        return p_name, apps

    def get_smart_folders(self, fw, mode, domain_folders):
        """
        DYNAMIC FOLDER MAPPING:
        Synchronizes framework needs with build strategy.
        """
        fw, mode = fw.lower(), mode.lower()
        folders = set()
        
        # 1. Framework-Specific Structural Cores
        if "django" in fw:
            folders.update(["apps", "core", "static", "templates", "middleware"])
        elif "rag_ai" in fw:
            folders.update(getattr(self.c, 'RAG_LAYERS', ["vectordb", "embeddings", "prompts"]))
        elif "data_pipeline" in fw:
            folders.update(getattr(self.c, 'DATA_LAYERS', ["bronze", "silver", "gold"]))
        elif "fastapi" in fw or "flask" in fw:
            folders.update(["api", "core", "services", "models", "schemas"])
        elif "native_cpp" in fw:
            folders.update(["src", "include", "tests", "build"])
        else:
            # Generic High-Performance Baseline
            folders.update(["src", "tests", "config", "utils"])

        # 2. Strategy Injections (Production/Custom get more robust layers)
        if mode in ["production", "custom"]:
            # Inject domain folders (from constants.ALL_CUSTOM_FOLDERS)
            folders.update(domain_folders)
            # Ensure maintenance layers exist
            folders.update(["docs", "scripts", "logs", "deploy"])
            
        return list(folders)