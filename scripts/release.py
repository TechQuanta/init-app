import subprocess
import sys


def main():
    print("\n🚀 Releasing py-create...\n")

    try:
        subprocess.check_call([sys.executable, "-m", "build"])
        subprocess.check_call([sys.executable, "-m", "twine", "upload", "dist/*"])

        print("\n✔ Release complete 😌🔥\n")

    except Exception:
        print("\n❌ Release failed\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
