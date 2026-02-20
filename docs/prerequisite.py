import sys
import shutil
import subprocess
# 🟢 Centralized Logger Import
from create_app.logger import logger

class Prerequisite:
    """
    PRE-FLIGHT CHECK ENGINE (v1.0.0)
    Ensures Python, Pip, and Venv are ready for use.
    """
    @staticmethod
    def check_system():
        logger.info("📡 Initializing system prerequisite validation...")
        results = {
            "status": True,
            "errors": []
        }

        # 1. Check Python Version (3.7+)
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if sys.version_info < (3, 7):
            err = f"Python 3.7+ required (Found {current_version})"
            logger.error(f"❌ Version Check Failed: {err}")
            results["errors"].append(err)
            results["status"] = False
        else:
            logger.debug(f"✅ Python version {current_version} verified.")

        # 2. Check for Pip
        pip_path = shutil.which("pip") or shutil.which("pip3")
        if not pip_path:
            err = "Pip is missing or not found in system PATH."
            logger.error(f"❌ Pip Check Failed: {err}")
            results["errors"].append(err)
            results["status"] = False
        else:
            logger.debug(f"✅ Pip found at: {pip_path}")

        # 3. Check for Venv module
        try:
            import venv
            logger.debug("✅ Python 'venv' module is available.")
        except ImportError:
            err = "Module 'venv' not found (Required: install python3-venv on Linux systems)."
            logger.error(f"❌ Venv Check Failed: {err}")
            results["errors"].append(err)
            results["status"] = False

        if results["status"]:
            logger.info("🚀 All system prerequisites met.")
        else:
            logger.warning(f"⚠️ System check failed with {len(results['errors'])} errors.")

        return results