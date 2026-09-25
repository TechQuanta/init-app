import configparser
from pathlib import Path


def test_package_version_is_stable_major_release():
    config = configparser.ConfigParser()
    config.read(Path(__file__).resolve().parents[1] / "setup.cfg")

    assert config["metadata"]["version"] == "3.2.0"
    classifiers = "\n".join(config["metadata"]["classifiers"].splitlines())
    assert "Development Status :: 5 - Production/Stable" in classifiers
