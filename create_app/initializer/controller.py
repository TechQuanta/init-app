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
import create_app.constants as const 
from create_app.engine.ui.spinner import Spinner 
from docs.prerequisite import Prerequisite
from create_app.logger import logger

class Controller:
    """
    MISSION CONTROL (v5.0.2)
    Orchestrator for System Checks, Django Injection, and Architecture Generation.
    FIX: Hardened Boolean + String check for VENV to ensure 'no' is absolute.
    """
    def __init__(self, manifest: dict, folders: list): 
        self.manifest = manifest
        self.p_name = manifest.get("project name", "new_project")
        
        # Resolve Framework and Strategy
        bp_raw = str(manifest.get("core blueprint", "fastapi")).lower()
        self.fw = bp_raw.split(" (")[0].strip().split(" +")[0]
        self.is_drf = "rest framework" in bp_raw or manifest.get("is_drf", False)
        self.strategy = str(manifest.get("build strategy", "standard")).lower()
        
        # ⚡ AUTO-CONFIG OVERRIDE: Inject production suites
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

    def _run_prerequisites(self):
        """Validates system tools before starting the build."""
        with Spinner("Verifying system requirements"):
            check = Prerequisite.check_system()
        
        if not check["status"]:
            logger.error(f"❌ Prerequisites failed: {check.get('errors')}")
            sys.exit(1)

    def _setup_virtual_env(self):
        """Creates a virtual environment only if the user didn't say no."""
        
        # ⚡ THE TRUTH CHECK
        # We look for 'venv_enabled' first. If it's False (bool) or "no" (string), we exit.
        raw_val = self.manifest.get("venv_enabled", self.manifest.get("venv", True))
        
        # 1. Check if it's explicitly False (Boolean)
        if raw_val is False:
            logger.info("🚫 VENV setup skipped (Boolean False).")
            return
            
        # 2. Check if it's a negative String
        if str(raw_val).lower().strip() in ["no", "n", "false", "skip", "no venv"]:
            logger.info(f"🚫 VENV setup skipped (String: {raw_val}).")
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
        """Native Django bootstrapping with Snippet Injection."""
        app_name = self.ctx.get("app_name", "core_app")
        tpl_dir = Path(ROOT_DIR) / "create_app" / "common"
        
        with Spinner(f"Injected Django architecture"):
            subprocess.run([sys.executable, "-m", "django", "startproject", self.p_name, "."], 
                           cwd=self.root, check=True, capture_output=True)
            subprocess.run([sys.executable, "manage.py", "startapp", app_name], 
                           cwd=self.root, check=True, capture_output=True)

            settings_path = self.root / self.p_name / "settings.py"
            if settings_path.exists():
                content = settings_path.read_text(encoding="utf-8")
                
                # Patch logic (preserved from original)
                if (tpl_dir / "secret.tpl").exists():
                    secret_patch = (tpl_dir / "secret.tpl").read_text()
                    pattern = r"SECRET_KEY = .*?ALLOWED_HOSTS = \[\]"
                    content = re.sub(pattern, secret_patch, content, flags=re.DOTALL)
                
                if "import os" not in content:
                    content = content.replace("from pathlib import Path", "from pathlib import Path\nimport os")
                
                settings_path.write_text(content, encoding="utf-8")

    def _render_instructions(self):
        """Displays final summary and activation commands."""
        c = self.colors
        venv_dir = self.root / "venv"
        
        if venv_dir.exists():
            venv_cmd = "venv\\Scripts\\activate" if os.name == "nt" else "source venv/bin/activate"
            os_label = "Windows" if os.name == "nt" else "Linux / macOS"
            print(f"\n  {c['white']}Activate venv:")
            print(f"    {c['accent']}{venv_cmd}    {c['muted']}({os_label})")
        
        print(f"\n  {c['success']}✔ {c['white']}Project ready 🚀")
        print(f"\n  {c['white']}📦 Quick Start")
        print(f"  {c['muted']}{'-'*15}")
        print(f"  {c['white']}cd {self.p_name}")
        print(f"  {c['white']}python app.py")
        print(f"\n  {c['success']}Happy coding! 🚀\n")

    def run_mission(self):
        """Master Build Sequence Orchestrator."""
        try:
            # 1. System Check
            self._run_prerequisites()
            self.root.mkdir(parents=True, exist_ok=True)
            
            # 2. Framework Specific Bootstrapping
            if self.fw == "django": 
                self._handle_django_logic()
            
            # 3. Execution & Generation
            build_data = self.executor.execute()
            self.worker.ctx = build_data.get('ctx') 
            
            with Spinner("Generating project architecture"):
                final_manifest = []
                for rule in build_data.get('manifest', []):
                    if any(x in rule["target"] for x in ["_main.py", "run.py", "entry.py"]):
                        rule["target"] = "app.py"
                    final_manifest.append(rule)

                # Infrastructure Injection
                infra_map = self.manifest.get("infra_files", {})
                for suite, files in infra_map.items():
                    if not files: continue
                    for filename in files:
                        raw_name = os.path.basename(filename).replace('.tpl', '')
                        target = f".github/workflows/{raw_name}" if suite == "github" else f"{suite}/{raw_name}"
                        final_manifest.append({
                            "source": f"common/{os.path.basename(filename)}", 
                            "target": target
                        })
                
                self.worker.run(blueprint=build_data.get('blueprint'), manifest_rules=final_manifest)
            
            # 4. Environment Setup (Respects 'no' inputs)
            self._setup_virtual_env()
            
            # 5. Cleanup
            if (self.root / "ui").exists(): 
                shutil.rmtree(self.root / "ui")

            # 6. Final UI Output
            self._render_instructions()

        except Exception as e:
            logger.error(f"🔥 Controller Failure: {str(e)}", exc_info=True)
            print(f"\n  {self.colors['accent']}✖ {self.colors['white']}controller failure: {str(e).lower()}")

if __name__ == "__main__":
    pass