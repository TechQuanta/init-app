import sys
import readchar
from colorama import init, Fore, Style, Back
from pyfiglet import Figlet

init(autoreset=True)

# 🎨 THEME: "PREMIUM ORANGE ASYMMETRY"
ORANGE_TEXT = "\033[38;5;208m"
ORANGE_BG = "\033[48;5;208m"
ORANGE_BOLD = f"\033[1;38;5;208m"

PURPLE = Fore.WHITE            
LIGHT_PURPLE = ORANGE_BOLD                 
CYAN = ORANGE_BOLD                         
WHITE = Fore.WHITE                         
GREY = Fore.BLACK + Style.BRIGHT
RESET = Style.RESET_ALL
BOLD = Style.BRIGHT
DIM = Style.DIM

def clear_screen():
    print("\033c", end="")

def show_banner(app_name, app_version):
    figlet = Figlet(font="slant", width=80)
    banner_text = figlet.renderText("init-app")
    print("\n") 
    for line in banner_text.splitlines():
        if line.strip():
            print(f"  {WHITE}{BOLD}{line}")
    print(f"  {DIM}VERSION {app_version}   {WHITE}│   {DIM}BUILD 2026.02")

def interactive_menu(app_name, app_version, title, options, descriptions=None, highlight_color=None):
    selected = 0
    margin = "  "
    print("\033[?25l", end="") 
    try:
        while True:
            clear_screen()
            show_banner(app_name, app_version)
            print(f"\n\n{margin}{LIGHT_PURPLE}❯ {title.upper()}{RESET}\n")
            for i, option in enumerate(options):
                desc = f"{DIM}{GREY} — {descriptions.get(option, '')}{RESET}" if descriptions else ""
                if i == selected:
                    label = f"{ORANGE_BG}{Fore.BLACK}{BOLD}  {option.rjust(18)}  {RESET}"
                    print(f"{margin}{label}{desc}")
                else:
                    print(f"{margin}    {WHITE}{option.ljust(18)}{desc}")
            print(f"\n\n{margin}{DIM}↑/↓ Navigate   {WHITE}•   {DIM}ENTER Select   {WHITE}•   {DIM}CTRL+C Exit{RESET}")
            key = readchar.readkey()
            if key == readchar.key.UP: selected = (selected - 1) % len(options)
            elif key == readchar.key.DOWN: selected = (selected + 1) % len(options)
            elif key == readchar.key.ENTER: 
                print("\033[?25h", end="")
                return options[selected]
    except KeyboardInterrupt:
        print("\033[?25h", end="")
        sys.exit(f"\n{margin}{ORANGE_TEXT}Process Aborted.")

def show_success_dashboard(formatted_text):
    """Renders the final project summary without breaking boxes."""
    margin = "  "
    print(f"\n{margin}{ORANGE_BOLD}✔ SUCCESS! PROJECT READY 🚀{RESET}")
    print(f"{margin}{DIM}{'━' * 50}{RESET}")
    
    for line in formatted_text.splitlines():
        if any(k in line for k in ["Quick Start", "Activate", "Happy coding", "NEXT STEPS"]):
            print(f"\n{margin}{ORANGE_TEXT}{BOLD}{line}{RESET}")
        else:
            print(f"{margin}{WHITE}{line}{RESET}")
    print(f"{margin}{DIM}{'━' * 50}{RESET}\n")