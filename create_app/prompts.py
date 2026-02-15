from colorama import Fore, Style


def ask_project_details(framework):

    print(Fore.WHITE + Style.DIM + "\nEnter your project details\n")

    print(Fore.WHITE + Style.DIM + "Project name example:")
    print(Fore.GREEN + Style.DIM + "  my-awesome-app")

    project_name = input(
        Fore.WHITE + Style.BRIGHT + "\nProject name → "
    )

    print(Fore.WHITE + Style.DIM + "\nProject location example:")
    print(Fore.GREEN + Style.DIM + "  ./   (current directory)")
    print(Fore.GREEN + Style.DIM + "  ../  (parent directory)")

    project_location = input(
        Fore.WHITE + Style.BRIGHT + "\nLocation → "
    )

    return project_name, project_location


# ✅ DJANGO PROMPT ENGINE 😈🔥
def ask_django_details():

    print(Fore.WHITE + Style.BRIGHT + "\nDjango Configuration\n")

    print(Fore.WHITE + Style.DIM + "Project example:")
    print(Fore.GREEN + Style.DIM + "  mysite")

    project_name = input(
        Fore.WHITE + Style.BRIGHT + "\nProject name → "
    )

    print(Fore.WHITE + Style.DIM + "\nApp example:")
    print(Fore.GREEN + Style.DIM + "  core")

    app_name = input(
        Fore.WHITE + Style.BRIGHT + "\nApp name → "
    )

    print(Fore.WHITE + Style.DIM + "\nLocation example:")
    print(Fore.GREEN + Style.DIM + "  ./")

    project_location = input(
        Fore.WHITE + Style.BRIGHT + "\nLocation → "
    )

    return project_name, app_name, project_location
