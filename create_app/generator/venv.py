import sys
import subprocess
import time
from pathlib import Path

# 🟢 Custom Logger Import
from create_app.ui.logger import logger

def create_virtualenv(project_root: Path):
    """
    🛠️ Creates a virtual environment and upgrades pip.
    """
    # Ensure we have an absolute path to avoid [Errno 2]
    project_root = project_root.resolve()
    venv_path = project_root / "venv"
    
    logger.info(f"🐍 Venv Setup Started: Root={project_root}")
    print(f"📦 Creating virtual environment in {project_root.name}...")
    
    try:
        # 1. Create the venv
        logger.info(f"Running: {sys.executable} -m venv venv")
        subprocess.run(
            [sys.executable, "-m", "venv", "venv"],
            cwd=project_root,
            check=True,
            capture_output=True, # Keeps the terminal clean
            text=True
        )
        logger.info("✅ Venv folder structure created.")

        # 2. Determine correct path to the new Python executable
        # ✅ FIX: Added .exe for Windows so pathlib can actually find the file
        if sys.platform == "win32":
            executable_name = "python.exe"
            executable_folder = "Scripts"
        else:
            executable_name = "python"
            executable_folder = "bin"

        venv_python = venv_path / executable_folder / executable_name
        logger.info(f"Expected venv python path: {venv_python}")

        # 3. 🛡️ Safety Check: Wait for OS to register the file
        attempts = 0
        while not venv_python.exists() and attempts < 10:
            logger.debug(f"⏳ Waiting for venv python... Attempt {attempts+1}")
            time.sleep(0.5)
            attempts += 1

        if not venv_python.exists():
            # Diagnostic: check what IS in that folder if it fails
            scripts_dir = venv_path / executable_folder
            existing_files = list(scripts_dir.glob("*")) if scripts_dir.exists() else "Folder missing"
            logger.error(f"❌ Critical Failure: Python not found. Found in folder: {existing_files}")
            raise FileNotFoundError(f"❌ Failed to locate venv python at {venv_python}")

        # 4. Upgrade pip
        logger.info("⚡ Upgrading pip inside the new environment...")
        print("⚡ Upgrading pip...")
        
        upgrade_result = subprocess.run(
            [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True
        )

        if upgrade_result.returncode == 0:
            logger.info("✅ Pip upgraded successfully.")
        else:
            logger.warning(f"⚠️ Pip upgrade non-zero exit: {upgrade_result.stderr}")

        logger.info("🏁 Virtual environment setup complete.")

    except subprocess.CalledProcessError as e:
        logger.error(f"💥 Subprocess Failed: {e.cmd}")
        logger.error(f"Stderr: {e.stderr}")
        raise RuntimeError(f"Venv command failed: {e.stderr}")
    except Exception as e:
        logger.critical(f"💥 Unexpected Venv Error: {str(e)}", exc_info=True)
        raise e