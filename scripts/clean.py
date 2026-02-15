import shutil
from pathlib import Path


def main():
    print("\n🧹 Cleaning workspace...\n")

    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("dist", ignore_errors=True)

    for item in Path(".").glob("*.egg-info"):
        shutil.rmtree(item, ignore_errors=True)

    for pycache in Path(".").rglob("__pycache__"):
        shutil.rmtree(pycache, ignore_errors=True)

    print("✔ Clean workspace 😌🔥\n")


if __name__ == "__main__":
    main()
