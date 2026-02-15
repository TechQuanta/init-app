import sys
import time

import readchar
from colorama import init, Fore, Style
from pyfiglet import Figlet
from importlib.metadata import version

from create_app import (
    APP_NAME,
    APP_TAGLINE,
    FRAMEWORKS,
    DJANGO_PROJECT_TYPES,
    PROJECT_STRUCTURES,
    DJANGO_DESCRIPTIONS,
    STRUCTURE_DESCRIPTIONS,
    VENV_OPTIONS,
    DATABASE_OPTIONS,
    DATABASE_DESCRIPTIONS,
    Spinner,
    ask_project_details,
)

from create_app.generator.generator import generate_project
from create_app.generator.database import resolve_database_dependencies
from create_app.generator.prerequisites import validate_environment
from create_app.generator.renderer import render_template

init(autoreset=True)

APP_VERSION = version(APP_NAME)


def clear_screen():
    print("\033c", end="")


def show_banner():
    figlet = Figlet(font="slant")
    banner = figlet.renderText(APP_NAME)

    print(Fore.WHITE + Style.DIM + f"{APP_NAME} CLI • Version {APP_VERSION}")
    print(Fore.WHITE + Style.DIM + APP_TAGLINE + "\n")

    print(Fore.WHITE + Style.BRIGHT + banner)
    print(Fore.WHITE + Style.DIM + "Create your Python backend project in seconds")
    print(Fore.WHITE + Style.DIM + "────────────────────────────────────────────")


def interactive_menu(title, options, descriptions=None, highlight_color=Fore.GREEN):
    selected = 0

    print(highlight_color + Style.BRIGHT + f"\n{title}")
    print(Fore.WHITE + Style.DIM + "Use ↑ ↓ to navigate • Enter to select\n")

    while True:
        for i, option in enumerate(options):

            description_text = ""
            if descriptions:
                description_text = (
                    Fore.WHITE + Style.DIM + f" — {descriptions.get(option, '')}"
                )

            if i == selected:
                print(highlight_color + Style.BRIGHT + f" ● {option}" + description_text)
            else:
                print(Fore.WHITE + Style.DIM + f" ○ {option}" + description_text)

        key = readchar.readkey()
        print("\033[F" * len(options), end="")

        if key == readchar.key.UP:
            selected = (selected - 1) % len(options)

        elif key == readchar.key.DOWN:
            selected = (selected + 1) % len(options)

        elif key == readchar.key.ENTER:
            print("\n")
            return options[selected]


def handle_selection(choice):

    if choice == "Exit":
        print("\n")
        print(Fore.WHITE + Style.BRIGHT + "👋 Thanks for using py-create")
        print(Fore.WHITE + Style.DIM + "Happy coding 🚀\n")
        sys.exit()

    try:
        clear_screen()
        show_banner()

        # ✅ Structure Selection
        if choice == "Django":

            structure = interactive_menu(
                "Choose Django Project Type",
                DJANGO_PROJECT_TYPES,
                DJANGO_DESCRIPTIONS,
            )

        else:

            structure = interactive_menu(
                "Choose Project Structure",
                PROJECT_STRUCTURES,
                STRUCTURE_DESCRIPTIONS,
            )

        print(Fore.WHITE + Style.DIM + "────────────────────────────────────────────")

        # ✅ Virtual Environment Choice
        venv_choice = interactive_menu(
            "Create Virtual Environment?",
            VENV_OPTIONS,
            highlight_color=Fore.CYAN,
        )

        print(Fore.WHITE + Style.DIM + "────────────────────────────────────────────")

        # ✅ Database Backend Selection
        database_dependencies = ""

        if choice != "Django":

            database_choice = interactive_menu(
                "Choose Database Backend",
                DATABASE_OPTIONS,
                DATABASE_DESCRIPTIONS,
                highlight_color=Fore.MAGENTA,
            )

            database_dependencies = resolve_database_dependencies(database_choice)

            print(Fore.WHITE + Style.DIM + "────────────────────────────────────────────")

        # ✅ Project Details
        project_name, project_location = ask_project_details(choice)

        print()

        loader = Spinner("Generating project")
        loader.start()

        try:
            project_root = generate_project(
                project_name,
                project_location,
                choice,
                structure,
                database_dependencies,
                create_venv="Yes" in venv_choice,
            )

            time.sleep(0.2)

        finally:
            loader.stop()

        print()

        # ✅ Prepare template context
        venv_section = ""

        if "Yes" in venv_choice:
            venv_section = render_template(
                "common/venv.txt.tpl",
                None,
                {},
                raw=True,
            )

        # ✅ Render final output via template 🔥
        render_template(
            "common/work.txt.tpl",
            None,
            {
                "project_root": project_root,
                "entrypoint": "app.py",
                "venv_section": venv_section,
            },
            raw_print=True,
        )

    except KeyboardInterrupt:
        print("\n")
        print(Fore.RED + Style.BRIGHT + "❌ Failed to create project")
        print(Fore.WHITE + Style.DIM + "Operation cancelled by user\n")

    sys.exit()


def main():
    try:
        validate_environment()

        clear_screen()
        show_banner()

        choice = interactive_menu(
            "Create Your Project",
            [*FRAMEWORKS, "Exit"],
        )

        handle_selection(choice)

    except EnvironmentError as e:

        print("\n")
        print(Fore.RED + Style.BRIGHT + "❌ Environment Error\n")
        print(Fore.WHITE + Style.DIM + str(e) + "\n")
        sys.exit()

    except KeyboardInterrupt:
        print("\n")
        print(Fore.WHITE + Style.BRIGHT + "👋 Exiting py-create")
        print(Fore.WHITE + Style.DIM + "Session ended by user\n")
        sys.exit()


if __name__ == "__main__":
    main()
