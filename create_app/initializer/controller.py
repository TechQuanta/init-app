import os
import sys
import subprocess
import shutil
import re
from pathlib import Path

# --- AGGRESSIVE PATH RESOLUTION ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path: 
    sys.path.insert(0, ROOT_DIR)

from create_app.framework.bundler import Bundler
from create_app.engine.ui.ui_config import UIConfig 
from create_app.initializer.generator import Generator
from create_app.rules.django_rules import DJANGO_PATCH_RULES
from create_app.engine.ui.spinner import Spinner 
from docs.prerequisite import Prerequisite
from create_app.logger import logger

class Controller:
    """
    MISSION CONTROL (v4.6.0)
    Orchestrator for System Checks, Django Injection, and Architecture Generation.
    """
    def __init__(self, manifest: dict, folders: list): 
        self.manifest = manifest
        self.p_name = manifest.get("project name", "new_project")
        
        # Resolve Framework and DRF Status
        bp_raw = str(manifest.get("core blueprint", "fastapi")).lower()
        self.fw = bp_raw.split(" (")[0].strip().split(" +")[0]
        self.is_drf = "rest framework" in bp_raw or manifest.get("is_drf", False)
        
        self.strategy = str(manifest.get("build strategy", "standard")).lower()
        self.root = Path.cwd().resolve() / self.p_name
        self.colors = UIConfig.C
        
        # DNA of the build: Ensure init_strategy is captured for the Generator
        self.ctx = {
            "project_name": self.p_name,
            "app_name": manifest.get("app_name", "core_app"),
            "framework": self.fw,
            "build_strategy": self.strategy,
            "is_drf": self.is_drf,
            "custom_folders": folders,
            "init_strategy": manifest.get("init_strategy", {}),
            **self.manifest 
        }

        logger.info(f"🚀 Controller linked for mission: {self.p_name}")
        self.executor = Bundler(self.root, self.ctx)
        self.worker = Generator(self.root, self.executor.ctx)

    def _run_prerequisites(self):
        """Validates system tools (Python, Pip, Git) before starting the build."""
        c = self.colors
        logger.info("📡 Running pre-flight system check...")
        with Spinner("Verifying system requirements"):
            check = Prerequisite.check_system()
        
        if not check["status"]:
            logger.error(f"❌ Prerequisites failed: {check['errors']}")
            print(f"\n  {c['accent']}✖ {c['white']}prerequisite failure:")
            for err in check["errors"]:
                print(f"    {c['muted']}- {err}")
            sys.exit(1)

    def _setup_virtual_env(self):
        """Creates a virtual environment and installs requirements."""
        c = self.colors
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
        """Native Django bootstrapping with Snippet Injection."""
        app_name = self.ctx.get("app_name", "core_app")
        tpl_dir = Path(ROOT_DIR) / "create_app" / "common"
        
        logger.info(f"⚡ Bootstrapping Django ({'DRF' if self.is_drf else 'Plain'})")
        
        with Spinner(f"Injected Django architecture"):
            # 1. Base Project Creation
            subprocess.run([sys.executable, "-m", "django", "startproject", self.p_name, "."], 
                           cwd=self.root, check=True, capture_output=True)
            subprocess.run([sys.executable, "manage.py", "startapp", app_name], 
                           cwd=self.root, check=True, capture_output=True)

            # 2. Patch Settings.py
            settings_path = self.root / self.p_name / "settings.py"
            if settings_path.exists():
                content = settings_path.read_text(encoding="utf-8")
                
                # A. Inject Environment Logic (secret.tpl)
                if (tpl_dir / "secret.tpl").exists():
                    secret_patch = (tpl_dir / "secret.tpl").read_text()
                    pattern = r"SECRET_KEY = .*?ALLOWED_HOSTS = \[\]"
                    content = re.sub(pattern, secret_patch, content, flags=re.DOTALL)

                # B. Inject Installed Apps (app.py.tpl)
                if (tpl_dir / "app.py.tpl").exists():
                    apps_raw = (tpl_dir / "app.py.tpl").read_text().replace("{{app_name}}", app_name)
                    apps_patch = apps_raw.strip() if self.is_drf else f"    '{app_name}',"
                    
                    content = content.replace(
                        "INSTALLED_APPS = [", 
                        f"INSTALLED_APPS = [\n{apps_patch}"
                    )

                # C. Inject DRF Configuration (rf.py.tpl)
                if self.is_drf and (tpl_dir / "rf.py.tpl").exists():
                    rf_patch = (tpl_dir / "rf.py.tpl").read_text()
                    content += f"\n\n{rf_patch}"

                # D. Ensure OS import is present
                if "import os" not in content:
                    content = content.replace("from pathlib import Path", "from pathlib import Path\nimport os")
                
                settings_path.write_text(content, encoding="utf-8")

            # 3. Overwrite URLs (urls.tpl)
            if (tpl_dir / "urls.tpl").exists():
                urls_path = self.root / self.p_name / "urls.py"
                urls_content = (tpl_dir / "urls.tpl").read_text()
                urls_path.write_text(urls_content, encoding="utf-8")

    def _render_instructions(self):
        """Displays the 'Quick Start' guide after a successful build."""
        c = self.colors
        work_file = Path(ROOT_DIR) / "create_app" / "common" / "work.txt.tpl"
        if work_file.exists():
            content = work_file.read_text().replace("{{project_name}}", self.p_name).replace("{{entrypoint}}", "app.py")
            print(f"\n  {c['white']}📦 Quick Start\n  {c['muted']}{'-'*15}\n{c['white']}{content.strip()}")

    def run_mission(self):
        """Master Build Sequence Orchestrator."""
        c = self.colors
        try:
            self._run_prerequisites()
            self.root.mkdir(parents=True, exist_ok=True)
            
            # 1. Framework Specific Pre-Bootstrap
            if self.fw == "django": 
                self._handle_django_logic()
            
            # 2. Architecture Logic Resolution
            build_data = self.executor.execute()
            self.worker.ctx = build_data.get('ctx') # Sync Bundler context back to Worker
            
            with Spinner("Generating project architecture"):
                final_manifest = []
                for rule in build_data.get('manifest', []):
                    # Standardize entrypoint name
                    if any(x in rule["target"] for x in ["_main.py", "run.py", "entry.py"]):
                        rule["target"] = "app.py"
                    final_manifest.append(rule)

                # 3. Process Infra files (Docker, K8s, GitHub)
                infra_map = self.manifest.get("infra_files", {})
                for suite, files in infra_map.items():
                    if not files: continue
                    for filename in files:
                        prefix = f"{suite}/" if suite != "github" else ".github/workflows/"
                        target = f"{prefix}{filename.replace('.tpl', '')}"
                        final_manifest.append({"source": filename, "target": target})
                
                # Hand over to Generator
                self.worker.run(blueprint=build_data.get('blueprint'), manifest_rules=final_manifest)
            
            # 4. Environment Setup
            if self.manifest.get("venv_enabled", True):
                self._setup_virtual_env()
            
            # 5. Final Housekeeping
            ghost_ui = self.root / "ui"
            if ghost_ui.exists(): shutil.rmtree(ghost_ui)

            print(f"\n  {c['success']}✔ {c['white']}mission success: {self.p_name} is ready.")
            self._render_instructions()

        except Exception as e:
            logger.error(f"🔥 Controller Failure: {str(e)}", exc_info=True)
            print(f"\n  {c['accent']}✖ {c['white']}controller failure: {str(e).lower()}")