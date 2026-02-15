from pathlib import Path
import re


INIT_FILE = Path("create_app/__init__.py")


def main():
    content = INIT_FILE.read_text()

    match = re.search(r'__version__ = "([^"]+)"', content)

    if not match:
        print("❌ Version not found")
        return

    current_version = match.group(1)

    print(f"\nCurrent version → {current_version}")

    new_version = input("New version → ")

    updated = content.replace(
        f'__version__ = "{current_version}"',
        f'__version__ = "{new_version}"',
    )

    INIT_FILE.write_text(updated)

    print(f"\n✔ Version updated → {new_version} 😌🔥\n")


if __name__ == "__main__":
    main()
