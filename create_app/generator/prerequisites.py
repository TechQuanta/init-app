import sys


def check_python():

    # ✅ If this file runs → Python already exists 😌🔥
    return True


def check_pip():

    try:
        import pip  # ✅ Most reliable detection 🔥
        return True

    except ImportError:
        return False


def check_venv():

    try:
        import venv  # ✅ Same stable logic 🔥
        return True

    except ImportError:
        return False


def validate_environment():

    if not check_pip():
        raise EnvironmentError(
            "pip is not available.\n"
            "Please install pip or reinstall Python"
        )

    if not check_venv():
        raise EnvironmentError(
            "Virtual environment module (venv) missing.\n"
            "Please reinstall Python with venv support"
        )
