import json

import pytest

from ai_scaffold.cli import main
from ai_scaffold.models import ChangePlan


def test_creates_and_modifies_a_component_project(tmp_path):
    assert (
        main(
            [
                "create",
                "invoice",
                "FastAPI SaaS with PostgreSQL, Google authentication, Redis, Celery and Docker",
                "--output-dir",
                str(tmp_path),
                "--yes",
            ]
        )
        == 0
    )
    root = tmp_path / "invoice"
    metadata = json.loads((root / ".ai-scaffold" / "project.json").read_text())
    assert {"postgresql", "google-auth", "redis", "celery", "docker"} <= set(
        metadata["components"]
    )
    assert (root / "app" / "auth" / "google.py").exists()
    app = (root / "app" / "main.py").read_text()
    assert "app.include_router(email_auth_router)" in app
    assert "app.include_router(google_auth_router)" in app
    assert (
        main(["add", "email authentication", "--project-dir", str(root), "--yes"]) == 0
    )
    assert (root / "app" / "auth" / "email.py").exists()


def test_preview_does_not_create_project(tmp_path):
    main(
        [
            "create",
            "preview",
            "FastAPI with Docker",
            "--output-dir",
            str(tmp_path),
            "--plan",
        ]
    )
    assert not (tmp_path / "preview").exists()


def test_json_plan_injects_code_with_an_exact_anchor(tmp_path):
    main(["create", "json-demo", "FastAPI", "--output-dir", str(tmp_path), "--yes"])
    root = tmp_path / "json-demo"
    plan = {
        "operation": "inject_code",
        "component": "greeting-route",
        "changes": [
            {
                "type": "insert_after",
                "path": "app/main.py",
                "anchor": "    return {'status': 'ok'}\n",
                "content": "\n\n@app.get('/greeting')\ndef greeting():\n    return {'message': 'hello'}\n",
            }
        ],
        "dependencies": [],
        "environment": [],
    }
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps(plan), encoding="utf-8")

    assert main(["plan", "--input", str(plan_file), "--project-dir", str(root)]) == 0
    assert (
        main(["apply", "--input", str(plan_file), "--project-dir", str(root), "--yes"])
        == 0
    )
    assert "def greeting" in (root / "app" / "main.py").read_text()


def test_json_plan_rejects_paths_outside_project(tmp_path):
    main(["create", "safe-demo", "FastAPI", "--output-dir", str(tmp_path), "--yes"])
    plan_file = tmp_path / "unsafe.json"
    plan_file.write_text(
        json.dumps(
            {
                "operation": "inject_code",
                "component": "unsafe",
                "changes": [
                    {"type": "add_file", "path": "../outside.py", "content": "pass\n"}
                ],
            }
        ),
        encoding="utf-8",
    )
    try:
        main(
            [
                "plan",
                "--input",
                str(plan_file),
                "--project-dir",
                str(tmp_path / "safe-demo"),
            ]
        )
    except ValueError as exc:
        assert "Unsafe project-relative path" in str(exc)
    else:
        raise AssertionError("Unsafe JSON plans must be rejected")


def test_preview_models_sequential_changes_to_the_same_file(tmp_path):
    main(["create", "sequential", "FastAPI", "--output-dir", str(tmp_path), "--yes"])
    root = tmp_path / "sequential"
    plan = {
        "operation": "inject_code",
        "component": "sequential-edit",
        "changes": [
            {"type": "add_file", "path": "app/generated.py", "content": "VALUE = 1\n"},
            {
                "type": "append",
                "path": "app/generated.py",
                "content": "NEXT = VALUE + 1\n",
            },
        ],
    }
    plan_file = tmp_path / "sequential.json"
    plan_file.write_text(json.dumps(plan), encoding="utf-8")
    assert (
        main(["apply", "--input", str(plan_file), "--project-dir", str(root), "--yes"])
        == 0
    )
    assert "NEXT = VALUE + 1" in (root / "app" / "generated.py").read_text()


@pytest.mark.parametrize(
    "plan",
    [
        {
            "operation": "inject_code",
            "component": "bad",
            "changes": [],
            "environment": ["not-valid"],
        },
        {
            "operation": "inject_code",
            "component": "bad",
            "changes": [],
            "dependencies": ["--index-url https://unsafe.example"],
        },
        {"operation": "inject_code", "component": "bad", "changes": "not-an-array"},
    ],
)
def test_json_plan_rejects_unsafe_metadata(plan):
    with pytest.raises(ValueError):
        ChangePlan.from_dict(plan)


def test_failed_validation_restores_the_original_project(tmp_path):
    main(["create", "rollback", "FastAPI", "--output-dir", str(tmp_path), "--yes"])
    root = tmp_path / "rollback"
    original = (root / "app" / "main.py").read_text()
    plan_file = tmp_path / "invalid.py.json"
    plan_file.write_text(
        json.dumps(
            {
                "operation": "inject_code",
                "component": "invalid-python",
                "changes": [
                    {
                        "type": "append",
                        "path": "app/main.py",
                        "content": "def broken(:\n",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="syntax validation failed"):
        main(["apply", "--input", str(plan_file), "--project-dir", str(root), "--yes"])
    assert (root / "app" / "main.py").read_text() == original
