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

    # ✅ NEW 😈🔥
    PYTHON_PROJECT_TYPES,
    PYTHON_DESCRIPTIONS,

    Spinner,
)

from create_app.prompts import (
    ask_project_details,
    ask_django_details,
)

from create_app.generator.generator import generate_project
from create_app.generator.database import resolve_database_dependencies
from create_app.generator.prerequisites import validate_environment

init(autoreset=True)

APP_VERSION = version(APP_NAME)


# ✅ UI Helpers
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


# ✅ Interactive Menu Engine 😈🔥
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


# ✅ MAIN FLOW 😈🔥
def handle_selection(choice):

    if choice == "Exit":
        print("\n")
        print(Fore.WHITE + Style.BRIGHT + "👋 Thanks for using py-create")
        print(Fore.WHITE + Style.DIM + "Happy coding 🚀\n")
        sys.exit()

    try:

        clear_screen()
        show_banner()

        # ✅ DJANGO FLOW 😈🔥
        if choice == "Django":

            structure = interactive_menu(
                "Choose Django Project Type",
                DJANGO_PROJECT_TYPES,
                DJANGO_DESCRIPTIONS,
            )

            print(Fore.WHITE + Style.DIM + "────────────────────────────────────────────")

            venv_choice = interactive_menu(
                "Create Virtual Environment?",
                VENV_OPTIONS,
                highlight_color=Fore.CYAN,
            )

            project_name, app_name, project_location = ask_django_details()

            print()

            loader = Spinner("Generating Django project")
            loader.start()

            try:
                project_root = generate_project(
                    project_name,
                    project_location,
                    choice,
                    structure,
                    "",  # Django dependencies handled internally
                    create_venv="Yes" in venv_choice,
                    extra_context={
                        "app_name": app_name
                    },
                )

                time.sleep(0.2)

            finally:
                loader.stop()

        # ✅ PYTHON FLOW 😈🔥🔥🔥
        elif choice == "Python":

            structure = interactive_menu(
                "Choose Python Project Type",
                PYTHON_PROJECT_TYPES,
                PYTHON_DESCRIPTIONS,
            )

            print(Fore.WHITE + Style.DIM + "────────────────────────────────────────────")

            venv_choice = interactive_menu(
                "Create Virtual Environment?",
                VENV_OPTIONS,
                highlight_color=Fore.CYAN,
            )

            project_name, project_location = ask_project_details(choice)

            print()

            loader = Spinner("Generating Python project")
            loader.start()

            try:
                project_root = generate_project(
                    project_name,
                    project_location,
                    choice,
                    structure,
                    "",
                    create_venv="Yes" in venv_choice,
                )

                time.sleep(0.2)

            finally:
                loader.stop()

        # ✅ OTHER FRAMEWORKS 🔥🔥🔥
        else:

            structure = interactive_menu(
                "Choose Project Structure",
                PROJECT_STRUCTURES,
                STRUCTURE_DESCRIPTIONS,
            )

            print(Fore.WHITE + Style.DIM + "────────────────────────────────────────────")

            venv_choice = interactive_menu(
                "Create Virtual Environment?",
                VENV_OPTIONS,
                highlight_color=Fore.CYAN,
            )

            database_choice = interactive_menu(
                "Choose Database Backend",
                DATABASE_OPTIONS,
                DATABASE_DESCRIPTIONS,
                highlight_color=Fore.MAGENTA,
            )

            database_dependencies = resolve_database_dependencies(database_choice)

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
        print(Fore.GREEN + Style.BRIGHT + "✔ Project initialized successfully!\n")
        print(Fore.WHITE + Style.DIM + f"Location → {project_root}\n")

    except KeyboardInterrupt:

        print("\n")
        print(Fore.RED + Style.BRIGHT + "❌ Failed to create project")
        print(Fore.WHITE + Style.DIM + "Operation cancelled by user\n")

    sys.exit()


# ✅ ENTRYPOINT 🚀
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
