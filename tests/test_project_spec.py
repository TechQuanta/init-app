import json

import pytest

from create_app.project_spec import load_spec, validate_app_name, validate_project_name, validate_relative_paths


def test_spec_loads_json_object(tmp_path):
    source = tmp_path / "project.json"
    source.write_text(json.dumps({"name": "api", "framework": "fastapi"}), encoding="utf-8")
    assert load_spec(str(source))["framework"] == "fastapi"


@pytest.mark.parametrize("name", ["../escape", "my app", "", "123api", "api/name"])
def test_project_name_rejects_unsafe_values(name):
    with pytest.raises(ValueError):
        validate_project_name(name)


def test_relative_paths_are_normalized_and_deduplicated():
    assert validate_relative_paths(["src/api", "src/api", "tests/unit"], "folders") == ["src/api", "tests/unit"]


def test_app_name_must_be_a_python_identifier():
    assert validate_app_name("core_app") == "core_app"
    with pytest.raises(ValueError):
        validate_app_name("core-app")


@pytest.mark.parametrize("value", [["../outside"], ["/absolute"], ["C:/temp"], ["src//api"]])
def test_relative_paths_reject_unsafe_values(value):
    with pytest.raises(ValueError):
        validate_relative_paths(value, "folders")
