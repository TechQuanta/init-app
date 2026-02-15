from colorama import Fore, Style

def ask_project_details(framework):
    """ ✨ Standard Prompt: Name and Location setup """
    print(Fore.WHITE + Style.DIM + f"\n--- Configuration: {framework} ---")

    # 🚀 Get Project Name
    print(Fore.WHITE + Style.DIM + "Project name example: " + Fore.GREEN + "my-awesome-app")
    while True:
        project_name = input(Fore.WHITE + Style.BRIGHT + "Project name → ").strip()
        if project_name:
            break
        print(Fore.RED + "⚠ Project name cannot be empty!")

    # 📂 Get Project Location
    print(Fore.WHITE + Style.DIM + "\nLocation example: " + Fore.GREEN + "./ " + Fore.WHITE + "(current directory)")
    project_location = input(Fore.WHITE + Style.BRIGHT + "Location [./] → ").strip() or "./"

    return project_name, project_location


# ✅ DJANGO PROMPT ENGINE 😈🔥
def ask_django_details():
    """ 🏗️  Specialized Prompt for Django's Project/App structure """
    print(Fore.WHITE + Style.BRIGHT + "\n--- Django Enterprise Config ---")

    # 🧱 Project Name (The container)
    print(Fore.WHITE + Style.DIM + "Project name (e.g., 'mysite' or 'config')")
    project_name = input(Fore.WHITE + Style.BRIGHT + "Project name → ").strip() or "mysite"

    # 📱 Internal App Name
    print(Fore.WHITE + Style.DIM + "\nMain App name (e.g., 'core' or 'api')")
    app_name = input(Fore.WHITE + Style.BRIGHT + "App name → ").strip() or "core"

    # 📂 Location
    print(Fore.WHITE + Style.DIM + "\nLocation example: ./")
    project_location = input(Fore.WHITE + Style.BRIGHT + "Location [./] → ").strip() or "./"

    return project_name, app_name, project_location