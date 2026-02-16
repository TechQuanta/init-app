import sys
import time
import argparse
import os
from pathlib import Path
from colorama import init, Fore, Style, Back

# 🟢 Custom UI, Generator, and Logging Imports
from create_app.ui.logger import logger
from create_app.ui.interface import (
    clear_screen, show_banner, interactive_menu, show_success_dashboard,
    PURPLE, LIGHT_PURPLE, CYAN, WHITE, GREY, RESET
)
from create_app.constants import (
    APP_NAME, FRAMEWORKS, DJANGO_PROJECT_TYPES,
    PROJECT_STRUCTURES, DJANGO_DESCRIPTIONS, STRUCTURE_DESCRIPTIONS,
    VENV_OPTIONS, DATABASE_OPTIONS, DATABASE_DESCRIPTIONS,
    PYTHON_PROJECT_TYPES, PYTHON_DESCRIPTIONS,
    __version__ 
)
from create_app.ui.prompts import ask_project_details, ask_django_details
from create_app.generator.generator import generate_project
from create_app.generator.database import resolve_database_dependencies
from create_app.ui.loader import Spinner
from create_app.generator.prerequisites import validate_environment

# Initialize colorama
init(autoreset=True)
APP_VERSION = __version__

# ──────────────────────────────────────────────────────────
# 🏗️ CLASS-BASED ENGINE
# ──────────────────────────────────────────────────────────

class ProjectEngine:
    """The core logic engine that orchestrates project creation."""
    def __init__(self, name, framework, structure, location=".", venv=False, db=None, extra_ctx=None):
        self.name = name
        self.framework = framework.capitalize() if framework.lower() != "fastapi" else "FastAPI"
        self.structure = structure or "Standard"
        self.location = location
        self.venv = venv
        self.db = db
        self.extra_ctx = extra_ctx or {}

    def _load_template(self, template_name, context):
        """
        Imports .tpl files from templates/common/ and replaces placeholders.
        Path: /home/singh-pc/Documents/py-create/create_app/templates/common/
        """
        # Resolves the path to the 'create_app' directory
        base_dir = Path(__file__).resolve().parent.parent
        template_path = base_dir / "templates" / "common" / template_name

        if not template_path.exists():
            return f"\n[!] Missing template at: {template_path}"

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace {{tags}} with actual values
            for key, value in context.items():
                placeholder = "{{" + str(key) + "}}"
                content = content.replace(placeholder, str(value))
            return content
        except Exception as e:
            return f"\n[!] Template Error: {e}"

    def start(self):
        """🚀 Triggers the generation process."""
        db_deps = resolve_database_dependencies(self.db) if self.db else ""
        
        self.extra_ctx.update({
            "project_name": self.name,
            "framework": self.framework,
            "structure": self.structure,
            "database": self.db or "None"
        })
        
        try:
            clear_screen()
            show_banner(APP_NAME, APP_VERSION)
            # Use LIGHT_PURPLE which is our Orange Bold
            print(f"\n{LIGHT_PURPLE}🏗️  PREPARING ARCHITECTURE...{RESET}\n")

            with Spinner(f"Generating {self.framework} Scaffolding") as loader:
                project_root = generate_project(
                    self.name, 
                    self.location, 
                    self.framework, 
                    self.structure,
                    db_deps, 
                    create_venv=self.venv,
                    extra_context=self.extra_ctx
                )
                time.sleep(0.8)

            self.show_dashboard(project_root)
            return True
        except Exception as e:
            logger.exception("Engine build failed")
            print(f"\n{Fore.RED}❌ Generation Failed: {e}")
            return False

    def show_dashboard(self, project_root):
        """🏁 Renders the final dashboard using work.txt.tpl and venv.txt.tpl."""
        clear_screen()
        show_banner(APP_NAME, APP_VERSION)
        
        entrypoint = "manage.py runserver" if self.framework == "Django" else "app.py"
        
        # Data to inject into templates
        context = {
            "project_name": self.name,
            "framework": self.framework,
            "path": str(project_root),
            "entrypoint": entrypoint,
            "venv_section": ""
        }

        # Load Venv instructions if user selected Venv
        if self.venv:
            context["venv_section"] = self._load_template("venv.txt.tpl", context)
        else:
            context["venv_section"] = "Venv not initialized."

        # Load the main output template (work.txt.tpl)
        final_output = self._load_template("work.txt.tpl", context)
        
        # Display via the interface
        show_success_dashboard(final_output)

# ──────────────────────────────────────────────────────────
# ⌨️ INTERACTIVE UI LOGIC
# ──────────────────────────────────────────────────────────

def run_interactive():
    """Starts the keyboard-controlled guided setup."""
    choice = interactive_menu(APP_NAME, APP_VERSION, "What are we building today?", [*FRAMEWORKS, "Exit"])
    
    if choice == "Exit":
        sys.exit()

    db_choice = None
    extra_ctx = {}

    if choice == "Django":
        structure = interactive_menu(APP_NAME, APP_VERSION, "Project Type", DJANGO_PROJECT_TYPES, DJANGO_DESCRIPTIONS)
        venv_choice = interactive_menu(APP_NAME, APP_VERSION, "Setup Venv?", VENV_OPTIONS)
        proj_name, app_name, proj_loc = ask_django_details()
        extra_ctx = {"app_name": app_name}
    elif choice == "Python":
        structure = interactive_menu(APP_NAME, APP_VERSION, "Project Type", PYTHON_PROJECT_TYPES, PYTHON_DESCRIPTIONS)
        venv_choice = interactive_menu(APP_NAME, APP_VERSION, "Setup Venv?", VENV_OPTIONS)
        proj_name, proj_loc = ask_project_details(choice)
    else:
        structure = interactive_menu(APP_NAME, APP_VERSION, "Structure", PROJECT_STRUCTURES, STRUCTURE_DESCRIPTIONS)
        venv_choice = interactive_menu(APP_NAME, APP_VERSION, "Setup Venv?", VENV_OPTIONS)
        db_choice = interactive_menu(APP_NAME, APP_VERSION, "Database", DATABASE_OPTIONS, DATABASE_DESCRIPTIONS)
        proj_name, proj_loc = ask_project_details(choice)

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

def main():
    parser = argparse.ArgumentParser(
        prog="init-app",
        description="init-app: Modern Python Backend Bootstrapper"
    )
    parser.add_argument("-v", "--version", action="version", version=f"init-app {APP_VERSION}")
    
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create", help="Create a new project using flags")
    create_parser.add_argument("-n", "--name", help="Project name")
    create_parser.add_argument("-f", "--framework", help="Framework")
    create_parser.add_argument("-s", "--structure", help="Structure")
    create_parser.add_argument("-l", "--location", default=".", help="Project location")
    create_parser.add_argument("--venv", action="store_true", help="Initialize venv")
    create_parser.add_argument("-d", "--database", "--db", dest="db", help="Database type")

    subparsers.add_parser("doctor", help="Check system prerequisites")
    subparsers.add_parser("list", help="List available frameworks")

    args = parser.parse_args()

    try:
        validate_environment()

        if args.command == "doctor":
            print(f"\n{PURPLE}🩺 System Check:")
            print(f"{Fore.GREEN}✔ Python {sys.version.split()[0]} detected.")
            print(f"{Fore.GREEN}✔ {APP_NAME} v{APP_VERSION} environment is healthy.\n")
            return

        if args.command == "list":
            print(f"\n{PURPLE}Available Frameworks:{RESET}")
            for fw in FRAMEWORKS:
                print(f" {PURPLE}●{RESET} {fw}")
            return

        name = getattr(args, 'name', None)
        framework = getattr(args, 'framework', None)

        if name and framework:
            engine = ProjectEngine(
                name=name,
                framework=framework,
                structure=getattr(args, 'structure', None),
                location=getattr(args, 'location', "."),
                venv=getattr(args, 'venv', False),
                db=getattr(args, 'db', None)
            )
            engine.start()
        elif args.command == "create" or args.command is None:
            run_interactive()
        else:
            parser.print_help()

    except KeyboardInterrupt:
        print(f"\n{Fore.RED}❌ Cancelled by user.{RESET}")
    except Exception as e:
        logger.critical("Terminal Failure", exc_info=True)
        print(f"\n{Fore.RED}❌ Unexpected Error: {e}")
    finally:
        print("\033[?25h", end="")
        sys.exit()

if __name__ == "__main__":
    main()