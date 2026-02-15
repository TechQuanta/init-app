import subprocess
import sys


def main():
    print("\n🚀 Setting up py-create dev environment...\n")

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"])

        print("\n✔ Dev environment ready 😌🔥\n")

    except Exception:
        print("\n❌ Dev setup failed\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
