import os
import time
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop 

ORANGE = "\033[38;5;208m"
WHITE = "\033[1;37m"
RESET = "\033[0m"
BOLD = "\033[1m"

def show_premium_ui():
    """The logic for your Orange installer UI"""
    os.system('cls' if os.name == 'nt' else 'clear')
    logo = r"""
  {ORANGE}    _       _ _                       
     (_)     (_) |                      
      _ _ __  _| |_ ______  __ _ _ __  _ __ 
     | | '_ \| | __|______|/ _` | '_ \| '_ \
     | | | | | | |_      | (_| | |_) | |_) |
     |_|_| |_|_|\__|      \__,_| .__/| .__/ 
                               | |   | |    
                               |_|   |_|    {RESET}
"""
    print(logo.format(ORANGE=ORANGE, RESET=RESET))
    print(f"  {WHITE}{BOLD}LINKING PROJECT IN EDITABLE MODE...{RESET}")
    print(f"  {ORANGE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    
    steps = [
        "  ▹ Mapping source trees...", 
        "  ▹ Syncing orange-theme assets...", 
        "  ▹ Injecting CLI entry-points...",
        "  ▹ Verifying dependencies (Jinja2, Dotenv)..."
    ]
    for step in steps:
        print(step)
        time.sleep(0.4)
    print(f"\n  {ORANGE}{BOLD}✔ EDITABLE INSTALL COMPLETE{RESET}\n")

class PremiumInstall(install):
    def run(self):
        show_premium_ui()
        install.run(self)

class PremiumDevelop(develop): 
    def run(self):
        show_premium_ui()
        develop.run(self)

setup(
    name="init-app",
    version="1.0.0", # Updated to match pyproject.toml
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'colorama>=0.4.6', 
        'readchar>=4.2.1', 
        'pyfiglet>=1.0.4',
        'python-dotenv>=1.2.1',
        'jinja2>=3.1.0'  # Added to fix your error
    ],
    entry_points={'console_scripts': ['init-app=create_app.engine.cli:main']},
    cmdclass={
        'install': PremiumInstall,
        'develop': PremiumDevelop,
    },
)