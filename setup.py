from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="py-create",  # Your library name
    version="0.1.0",
    description="Interactive Python CLI for scaffolding backend projects (Flask, Django, FastAPI, etc.)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="TechQuanta",
    author_email="techquanta.community@gmail.com",
    url="https://github.com/TechQuanta/py-create",
    packages=find_packages(where="."),  # Finds all packages under create_app/
    python_requires=">=3.10",
    install_requires=[],  # Runtime dependencies (empty for now)
    extras_require={
        "dev": ["pytest>=7.0.0", "black>=24.0.0", "isort>=6.0.0"]  # Developer tools
    },
    entry_points={
        "console_scripts": [
            "py-create=create_app.cli:main",  # CLI command
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Build Tools",
    ],
    include_package_data=True,  # Include non-code files like templates
)
