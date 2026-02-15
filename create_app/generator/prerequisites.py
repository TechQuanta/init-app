import sys
# 🟢 Import the internal logger from your UI package
from create_app.ui.logger import logger

# ✅ Python Check
def check_python():
    """ 
    🐍 Validates the Python version.
    Ensures the user is on 3.10+ for modern syntax support. 
    """
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    logger.info(f"System Check: Python Version {current_version}")

    if sys.version_info < (3, 10):
        logger.error(f"Incompatible Python version: {current_version}")
        raise EnvironmentError(
            f"❌ Python {current_version} detected.\n"
            "py-create requires Python 3.10 or higher! 🚀"
        )
    return True

# ✅ Pip Check
def check_pip():
    """ 📦 Checks if the package manager is installed. """
    logger.info("System Check: Checking for pip installation...")
    try:
        import pip
        logger.info("✅ pip is available.")
        return True
    except ImportError:
        logger.warning("❌ pip import failed.")
        return False

# ✅ Venv Check
def check_venv():
    """ 🛠️ Checks for the virtual environment module. """
    logger.info("System Check: Checking for venv module...")
    try:
        import venv
        logger.info("✅ venv is available.")
        return True
    except ImportError:
        logger.warning("❌ venv import failed (Likely a stripped Linux install).")
        return False

# ✅ GLOBAL VALIDATION ENGINE 🔥🔥🔥
def validate_environment():
    """
    🛡️  Ensures the host system is ready for project generation.
    """
    logger.info("🛡️  Starting Global Environment Validation...")
    
    try:
        # 1. Check Python Version first
        check_python()

        # 2. Check for Pip
        if not check_pip():
            raise EnvironmentError(
                "❌ pip is not available.\n"
                "Please install pip or repair your Python installation! 🛠️"
            )

        # 3. Check for Venv
        if not check_venv():
            raise EnvironmentError(
                "❌ Virtual environment module (venv) is missing.\n"
                "On Linux, try: sudo apt install python3-venv 🐧"
            )
        
        logger.info("✨ Environment Validation Passed.")
        return True 

    except EnvironmentError as e:
        # 🪵 Capture the failure in the log file with a full trace if needed
        logger.critical(f"Environment Validation FAILED: {str(e)}")
        raise e