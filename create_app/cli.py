import sys
import readchar
from colorama import init, Fore, Style
from pyfiglet import Figlet
from importlib.metadata import version

from create_app import APP_NAME, APP_TAGLINE, FRAMEWORKS

init(autoreset=True)

APP_VERSION = version(APP_NAME)

frameworks = [*FRAMEWORKS, "Exit"]

selected_index = 0


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


def render_menu():
    print(Fore.WHITE + Style.BRIGHT + "\nCreate Your Project")
    print(Fore.WHITE + Style.DIM + "Choose a framework to initialize")
    print(Fore.WHITE + Style.DIM + "Use ↑ ↓ to navigate • Enter to select\n")

    for i, framework in enumerate(frameworks):
        if i == selected_index:
            print(Fore.GREEN + Style.BRIGHT + f" ● {framework}")
        else:
            print(Fore.WHITE + Style.DIM + f" ○ {framework}")


def handle_selection(choice):
    if choice == "Exit":
        print("\n")
        print(Fore.WHITE + Style.BRIGHT + "👋 Thanks for using py-create")
        print(Fore.WHITE + Style.DIM + "Happy coding 🚀\n")
        sys.exit()

    clear_screen()
    print(Fore.GREEN + Style.BRIGHT + f"✔ Setting up {choice} project...\n")

    input(Fore.WHITE + Style.DIM + "Press Enter to continue...")


def main():
    global selected_index

    while True:
        clear_screen()
        show_banner()
        render_menu()

        key = readchar.readkey()

        if key == readchar.key.UP:
            selected_index = (selected_index - 1) % len(frameworks)

        elif key == readchar.key.DOWN:
            selected_index = (selected_index + 1) % len(frameworks)

        elif key == readchar.key.ENTER:
            handle_selection(frameworks[selected_index])


if __name__ == "__main__":
    main()
