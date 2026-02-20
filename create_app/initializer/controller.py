import os
import sys
import subprocess
import shutil
import re
from pathlib import Path
import jinja2

# --- AGGRESSIVE PATH RESOLUTION ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path: 
    sys.path.insert(0, ROOT_DIR)

from create_app.framework.bundler import Bundler
from create_app.engine.ui.ui_config import UIConfig 
from create_app.initializer.generator import Generator
import create_app.constants as const 
from create_app.engine.ui.spinner import Spinner 
from docs.prerequisite import Prerequisite
from create_app.logger import logger

class Controller:
    """
    MISSION CONTROL (v5.2.1)
    Orchestrator for System Checks, Django Injection, and Architecture Generation.
    FEATURE: Renders and displays work.txt.tpl and venv.txt.tpl directly to terminal.
    FIXED: Conditional DRF injection and clean app_name appending for normal Django.
    """
    def __init__(self, manifest: dict, folders: list): 
        self.manifest = manifest
        self.p_name = manifest.get("project name", "new_project")
        
        # Resolve Framework and Strategy
        bp_raw = str(manifest.get("core blueprint", "fastapi")).lower()
        self.fw = bp_raw.split(" (")[0].strip().split(" +")[0]
        self.is_drf = "rest framework" in bp_raw or manifest.get("is_drf", False)
        self.strategy = str(manifest.get("build strategy", "standard")).lower()
        
        # ⚡ AUTO-CONFIG OVERRIDE
        if self.strategy == "auto_config":
            logger.info("⚡ Auto-Config: Forcing Every Production Suite & Folder.")
            folders = list(const.ALL_CUSTOM_FOLDERS)
            self.manifest["infra_files"] = {
                "docker": list(const.DOCKER_SUITE),
                "jenkins": list(const.JENKINS_SUITE),
                "kubernetes": list(const.K8S_FILES),
                "github": list(const.GITHUB_SUITE)
            }
            self.manifest["init_strategy"] = {f: True for f in folders}

        self.root = Path.cwd().resolve() / self.p_name
        self.colors = UIConfig.C
        
        # DNA of the build
        self.ctx = {
            "project_name": self.p_name,
            "app_name": manifest.get("app_name", "core_app"),
            "framework": self.fw,
            "build_strategy": self.strategy,
            "is_drf": self.is_drf,
            "custom_folders": folders,
            "init_strategy": self.manifest.get("init_strategy", {}),
            **self.manifest 
        }

        logger.info(f"🚀 Controller linked for mission: {self.p_name}")
        self.executor = Bundler(self.root, self.ctx)
        self.worker = Generator(self.root, self.executor.ctx)
        
        # ⚡ Template Engine for Terminal Output
        self.tpl_path = Path(ROOT_DIR) / "create_app" / "common"
        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(self.tpl_path)))

    def _run_prerequisites(self):
        """Validates system tools before starting the build."""
        with Spinner("Verifying system requirements"):
            check = Prerequisite.check_system()
        
        if not check["status"]:
            logger.error(f"❌ Prerequisites failed: {check.get('errors')}")
            sys.exit(1)

    def _setup_virtual_env(self):
        """Creates a virtual environment only if requested."""
        raw_val = self.manifest.get("venv_enabled", self.manifest.get("venv", True))
        
        if raw_val in [False, "no", "n", "false", "skip"]:
            logger.info("🚫 VENV setup skipped.")
            return

        venv_path = self.root / "venv"
        req_file = self.root / "requirements.txt"

        try:
            with Spinner("Setting up virtual environment"):
                subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True, capture_output=True)
            
            if req_file.exists():
                with Spinner("Installing dependencies (pip)"):
                    pip_exe = venv_path / ("Scripts" if os.name == "nt" else "bin") / "pip"
                    subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], capture_output=True)
                    subprocess.run([str(pip_exe), "install", "-r", str(req_file)], check=True, capture_output=True)
                logger.info("✅ Dependencies installed.")
        except Exception as e:
            logger.error(f"⚠️ VENV warning: {str(e)}")

    def _handle_django_logic(self):
        """Native Django bootstrapping with Dynamic Snippet Injection."""
        app_name = self.ctx.get("app_name", "core_app")
        tpl_dir = self.tpl_path
        
        with Spinner(f"Injected Django architecture"):
            # 1. Standard Bootstrap
            subprocess.run([sys.executable, "-m", "django", "startproject", self.p_name, "."], 
                           cwd=self.root, check=True, capture_output=True)
            subprocess.run([sys.executable, "manage.py", "startapp", app_name], 
                           cwd=self.root, check=True, capture_output=True)

            settings_path = self.root / self.p_name / "settings.py"
            if settings_path.exists():
                content = settings_path.read_text(encoding="utf-8")
                
                # --- A. SECRET KEY & HOSTS ---
                if (tpl_dir / "secret.tpl").exists():
                    secret_patch = (tpl_dir / "secret.tpl").read_text()
                    pattern = r"SECRET_KEY = .*?ALLOWED_HOSTS = \[\]"
                    content = re.sub(pattern, secret_patch, content, flags=re.DOTALL)
                
                # --- B. INSTALLED_APPS INJECTION ---
                if self.is_drf:
                    # Case 1: Django REST Framework selected - Inject from apps.py.tpl
                    apps_tpl = tpl_dir / "apps.py.tpl"
                    if apps_tpl.exists():
                        apps_list_raw = apps_tpl.read_text().replace('{{app_name}}', app_name).strip()
                        pattern = r"(INSTALLED_APPS = \[.*?)(^])"
                        content = re.sub(pattern, rf"\1    {apps_list_raw},\n\2", content, flags=re.DOTALL | re.MULTILINE)
                else:
                    # Case 2: Normal Django - Just add the app name at the end of the list
                    pattern = r"(INSTALLED_APPS = \[.*?)(^])"
                    content = re.sub(pattern, rf"\1    '{app_name}',\n\2", content, flags=re.DOTALL | re.MULTILINE)

                # --- C. REST_FRAMEWORK CONFIG (DRF ONLY) ---
                if self.is_drf:
                    rf_tpl = tpl_dir / "rf.py.tpl"
                    if rf_tpl.exists() and "REST_FRAMEWORK =" not in content:
                        rf_config = rf_tpl.read_text().strip()
                        content += f"\n\n{rf_config}\n"

                # --- D. UTILITY IMPORTS ---
                if "import os" not in content:
                    content = content.replace("from pathlib import Path", "from pathlib import Path\nimport os")
                
                settings_path.write_text(content, encoding="utf-8")
                logger.info(f"✅ Django settings.py patched. Mode: {'DRF' if self.is_drf else 'Standard'}")

    def _display_tpl(self, tpl_name: str):
        """Renders a specific template directly to terminal output."""
        try:
            template = self.jinja_env.get_template(tpl_name)
            output = template.render(self.executor.ctx)
            print(f"{self.colors['white']}{output}")
        except Exception as e:
            logger.debug(f"Terminal render skipped for {tpl_name}: {e}")

    def _render_instructions(self):
        """Displays final summary by populating templates directly."""
        print("\n" + "—"*50)
        self._display_tpl("venv.txt.tpl")
        self._display_tpl("work.txt.tpl")
        print("—"*50 + "\n")

    def run_mission(self):
        """Master Build Sequence Orchestrator."""
        try:
            self._run_prerequisites()
            self.root.mkdir(parents=True, exist_ok=True)
            
            if self.fw == "django": 
                self._handle_django_logic()
            
            # 3. Execution & Generation
            build_data = self.executor.execute()
            self.worker.ctx = build_data.get('ctx', self.ctx) 
            
            with Spinner("Generating project architecture"):
                final_manifest = []
                for rule in build_data.get('manifest', []):
                    if any(x in rule["target"] for x in ["work.txt", "venv.txt"]):
                        continue

                    if any(x in rule["target"] for x in ["_main.py", "run.py", "entry.py"]):
                        rule["target"] = "app.py"
                    
                    if not rule["source"].startswith("common/") and not rule["source"].startswith("framework/"):
                        rule["source"] = f"common/{rule['source']}"
                        
                    final_manifest.append(rule)

                # --- INFRASTRUCTURE & UI INJECTION ---
                infra_map = self.manifest.get("infra_files", {})
                for suite, files in infra_map.items():
                    if not files: continue
                    for filename in files:
                        base_file = os.path.basename(filename)
                        raw_name = base_file.replace('.tpl', '')
                        src_path = f"common/template/{base_file}" if raw_name == "index.html" else f"common/{base_file}"
                        target = f".github/workflows/{raw_name}" if suite == "github" else f"{suite}/{raw_name}"
                        final_manifest.append({"source": src_path, "target": target})
                
                self.worker.run(blueprint=build_data.get('blueprint'), manifest_rules=final_manifest)
            
            # 4. Environment Setup
            self._setup_virtual_env()
            
            if self.fw == "django":
                ui_dir = self.root / "ui"
                if ui_dir.exists(): 
                    shutil.rmtree(ui_dir)
            
            # ⚡ 6. FINAL TERMINAL OUTPUT
            self._render_instructions()

        except Exception as e:
            logger.error(f"🔥 Controller Failure: {str(e)}", exc_info=True)
            print(f"\n  {self.colors['accent']}✖ {self.colors['white']}failure: {str(e).lower()}")

if __name__ == "__main__":
    pass