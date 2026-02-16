import sys
import time
import argparse
import readchar
from colorama import init, Fore, Style
from pyfiglet import Figlet
from importlib.metadata import version

# 🟢 Custom UI, Generator, and Logging Imports
from create_app.ui.logger import logger
from create_app import (
    APP_NAME, APP_TAGLINE, FRAMEWORKS, DJANGO_PROJECT_TYPES,
    PROJECT_STRUCTURES, DJANGO_DESCRIPTIONS, STRUCTURE_DESCRIPTIONS,
    VENV_OPTIONS, DATABASE_OPTIONS, DATABASE_DESCRIPTIONS,
    PYTHON_PROJECT_TYPES, PYTHON_DESCRIPTIONS, Spinner,
)
from create_app.ui.prompts import ask_project_details, ask_django_details
from create_app.generator.generator import generate_project
from create_app.generator.database import resolve_database_dependencies
from create_app.generator.prerequisites import validate_environment
from create_app.generator.renderer import render_template

init(autoreset=True)
try:
    APP_VERSION = version(APP_NAME)
except:
    APP_VERSION = "1.0.0"

# ──────────────────────────────────────────────────────────
# 🏗️ CLASS-BASED ENGINE
# ──────────────────────────────────────────────────────────

class ProjectEngine:
    """The core logic engine that orchestrates project creation."""
    def __init__(self, name, framework, structure, location=".", venv=False, db=None, extra_ctx=None):
        self.name = name
        self.framework = framework
        self.structure = structure
        self.location = location
        self.venv = venv
        self.db = db
        self.extra_ctx = extra_ctx or {}

    def start(self):
        """🚀 Triggers the generation process."""
        db_deps = resolve_database_dependencies(self.db) if self.db else ""
        
        try:
            with Spinner(f"Initializing {self.framework} Project") as loader:
                project_root = generate_project(
                    self.name, self.location, self.framework, self.structure,
                    db_deps, create_venv=self.venv,
                    extra_context=self.extra_ctx
                )
                time.sleep(0.5)

            self.show_dashboard(project_root)
            return True
        except Exception as e:
            logger.exception("Engine build failed")
            print(f"\n{Fore.RED}❌ Generation Failed: {e}")
            return False

    def show_dashboard(self, project_root):
        """🏁 Renders the final guide using templates."""
        entrypoint = "manage.py runserver" if self.framework == "Django" else "app.py"
        
        venv_section = ""
        if self.venv:
            venv_section = render_template("common/venv.txt.tpl", None, {}, raw=True)

        context = {
            "project_name": self.name,
            "entrypoint": entrypoint,
            "venv_section": venv_section
        }

        try:
            dashboard_content = render_template("common/work.txt.tpl", None, context, raw=True)
            print("\n" + Fore.GREEN + Style.BRIGHT + "────────────────────────────────────────────")
            print(Fore.WHITE + dashboard_content)
            print(Fore.GREEN + Style.BRIGHT + "────────────────────────────────────────────\n")
        except:
            print(Fore.GREEN + f"✔ Project {self.name} created at {project_root}")

# ──────────────────────────────────────────────────────────
# ⌨️ INTERACTIVE UI LOGIC
# ──────────────────────────────────────────────────────────

def clear_screen():
    print("\033c", end="")

def show_banner():
    figlet = Figlet(font="slant")
    print(Fore.WHITE + Style.DIM + f"{APP_NAME} CLI • v{APP_VERSION}")
    print(Fore.CYAN + Style.BRIGHT + figlet.renderText(APP_NAME))
    print(Fore.WHITE + Style.DIM + "────────────────────────────────────────────")

def interactive_menu(title, options, descriptions=None, highlight_color=Fore.GREEN):
    selected = 0
    print(highlight_color + Style.BRIGHT + f"\n{title}")
    print(Fore.WHITE + Style.DIM + "Use ↑ ↓ to navigate • Enter to select\n")

    while True:
        for i, option in enumerate(options):
            desc = f" — {descriptions.get(option, '')}" if descriptions else ""
            if i == selected:
                print(f"{highlight_color}{Style.BRIGHT} ● {option}{Fore.WHITE}{Style.DIM}{desc}")
            else:
                print(f"{Fore.WHITE}{Style.DIM} ○ {option}{desc}")

        key = readchar.readkey()
        print("\033[F" * len(options), end="")

        if key == readchar.key.UP:
            selected = (selected - 1) % len(options)
        elif key == readchar.key.DOWN:
            selected = (selected + 1) % len(options)
        elif key == readchar.key.ENTER:
            print("\n" * (len(options) // 2))
            return options[selected]

def run_interactive():
    """Starts the keyboard-controlled guided setup."""
    clear_screen()
    show_banner()
    
    choice = interactive_menu("What are we building today?", [*FRAMEWORKS, "Exit"])
    
    if choice == "Exit":
        sys.exit()

    clear_screen()
    show_banner()

    db_choice = None
    extra_ctx = {}

    if choice == "Django":
        structure = interactive_menu("Project Type", DJANGO_PROJECT_TYPES, DJANGO_DESCRIPTIONS)
        venv_choice = interactive_menu("Setup Venv?", VENV_OPTIONS, highlight_color=Fore.CYAN)
        proj_name, app_name, proj_loc = ask_django_details()
        extra_ctx = {"app_name": app_name}
    elif choice == "Python":
        structure = interactive_menu("Project Type", PYTHON_PROJECT_TYPES, PYTHON_DESCRIPTIONS)
        venv_choice = interactive_menu("Setup Venv?", VENV_OPTIONS, highlight_color=Fore.CYAN)
        proj_name, proj_loc = ask_project_details(choice)
    else:
        structure = interactive_menu("Structure", PROJECT_STRUCTURES, STRUCTURE_DESCRIPTIONS)
        venv_choice = interactive_menu("Setup Venv?", VENV_OPTIONS, highlight_color=Fore.CYAN)
        db_choice = interactive_menu("Database", DATABASE_OPTIONS, DATABASE_DESCRIPTIONS, highlight_color=Fore.MAGENTA)
        proj_name, proj_loc = ask_project_details(choice)

    # Trigger Engine
    engine = ProjectEngine(
        name=proj_name,
        framework=choice,
        structure=structure,
        location=proj_loc,
        venv=("Yes" in venv_choice),
        db=db_choice,
        extra_ctx=extra_ctx
    )
    engine.start()

# ──────────────────────────────────────────────────────────
# 🏁 MAIN ENTRY POINT (FLAGS + ARGS)
# ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Py-Create: Modern Python Backend Bootstrapper")
    parser.add_argument("-n", "--name", help="Project name")
    parser.add_argument("-f", "--framework", help="Framework (Flask, FastAPI, etc.)")
    parser.add_argument("-s", "--structure", help="Structure (simple, mvc, etc.)")
    parser.add_argument("-v", "--venv", action="store_true", help="Initialize virtual environment")
    parser.add_argument("-d", "--db", help="Database (sqlite, postgres, etc.)")

    args = parser.parse_args()

    try:
        validate_environment()

        # If user provides Name AND Framework, skip menus
        if args.name and args.framework:
            engine = ProjectEngine(
                name=args.name,
                framework=args.framework,
                structure=args.structure or "simple",
                venv=args.venv,
                db=args.db
            )
            engine.start()
        else:
            run_interactive()

    except KeyboardInterrupt:
        print(f"\n{Fore.RED}❌ Cancelled by user.{Style.RESET_ALL}")
    except Exception as e:
        logger.critical("Terminal Failure", exc_info=True)
        print(f"\n{Fore.RED}❌ Unexpected Error: {e}")
    finally:
        sys.exit()

if __name__ == "__main__":
    main()