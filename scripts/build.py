import subprocess
import sys


def main():
    print("\n📦 Building py-create package...\n")

    try:
        subprocess.check_call([sys.executable, "-m", "build"])

        print("\n✔ Build complete 😌🔥\n")

    except Exception:
        print("\n❌ Build failed\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
