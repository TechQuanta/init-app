import json
import sys

from create_app.doctor import analyze_project, run_doctor_command


def _make_healthy_project(tmp_path):
    project = tmp_path / "billing-api"
    project.mkdir()
    (project / ".git").mkdir()
    (project / ".init-app.json").write_text(
        json.dumps(
            {
                "project_name": "billing-api",
                "framework": "fastapi",
                "build_strategy": "standard",
                "project_path": str(project),
                "generated_by": "init-app",
                "generator_version": "3.2.0",
                "requires_python": ">=3.9",
            }
        ),
        encoding="utf-8",
    )
    (project / ".gitignore").write_text(
        ".env\n.env.*\n__pycache__/\n.venv/\nvenv/\nbuild/\ndist/\n*.pyc\n",
        encoding="utf-8",
    )
    (project / ".env.example").write_text("DATABASE_URL=sqlite:///db.sqlite3\n", encoding="utf-8")
    (project / "requirements.txt").write_text("pytest\n", encoding="utf-8")
    (project / "README.md").write_text("# billing-api\n", encoding="utf-8")
    (project / "app").mkdir()
    (project / "app" / "main.py").write_text(
        "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef home():\n    return {'ok': True}\n",
        encoding="utf-8",
    )
    (project / "Dockerfile").write_text(
        "FROM python:3.12-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nHEALTHCHECK CMD python -c 'print(1)'\nCMD ['python', 'app/main.py']\n",
        encoding="utf-8",
    )
    (project / ".dockerignore").write_text(".git\n__pycache__/\n", encoding="utf-8")
    return project


def test_doctor_reports_healthy_project(tmp_path):
    project = _make_healthy_project(tmp_path)
    report = analyze_project(project)
    assert report.summary["errors"] == 0
    assert report.summary["warnings"] <= 2
    assert any(check.name == "Project metadata" for check in report.checks)


def test_doctor_reports_missing_metadata(tmp_path):
    report = analyze_project(tmp_path)
    statuses = {check.name: check.status for check in report.checks}
    assert statuses.get("Project metadata") == "error"


def test_doctor_reports_invalid_metadata(tmp_path):
    project = tmp_path / "broken"
    project.mkdir()
    (project / ".init-app.json").write_text("{not valid json}", encoding="utf-8")
    report = analyze_project(project)
    assert any(check.name == "Project metadata" and check.status == "error" for check in report.checks)


def test_doctor_reports_missing_required_files(tmp_path):
    project = _make_healthy_project(tmp_path)
    (project / ".env.example").unlink()
    (project / "README.md").unlink()
    report = analyze_project(project)
    assert any(check.name == "Required files" and check.status == "error" for check in report.checks)


def test_doctor_identifies_invalid_python_syntax(tmp_path):
    project = _make_healthy_project(tmp_path)
    (project / "app" / "main.py").write_text("def broken(:\n    pass\n", encoding="utf-8")
    report = analyze_project(project)
    assert any(check.name == "Python syntax" and check.status == "error" for check in report.checks)


def test_doctor_reports_python_version_mismatch(tmp_path):
    project = _make_healthy_project(tmp_path)
    metadata = json.loads((project / ".init-app.json").read_text(encoding="utf-8"))
    metadata["requires_python"] = ">=99.0"
    (project / ".init-app.json").write_text(json.dumps(metadata), encoding="utf-8")
    report = analyze_project(project)
    assert any(check.name == "Python version" and check.status == "error" for check in report.checks)


def test_doctor_reports_dependency_mismatch(tmp_path):
    project = _make_healthy_project(tmp_path)
    (project / "requirements.txt").write_text("definitely-not-installed-package-xyz==99.0\n", encoding="utf-8")
    report = analyze_project(project)
    assert any(check.name == "Dependencies" and check.status == "warning" for check in report.checks)


def test_doctor_reports_missing_env_example(tmp_path):
    project = _make_healthy_project(tmp_path)
    (project / ".env.example").unlink()
    report = analyze_project(project)
    assert any(check.name == ".env.example" and check.status == "warning" for check in report.checks)


def test_doctor_reports_dotenv_not_ignored(tmp_path):
    project = _make_healthy_project(tmp_path)
    (project / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    report = analyze_project(project)
    assert any(check.name == ".env ignored" and check.status == "warning" for check in report.checks)


def test_doctor_reports_docker_healthcheck_missing(tmp_path):
    project = _make_healthy_project(tmp_path)
    (project / "Dockerfile").write_text("FROM python:3.12-slim\nWORKDIR /app\nCMD ['python', 'app/main.py']\n", encoding="utf-8")
    report = analyze_project(project)
    assert any(check.name == "Docker healthcheck" and check.status == "warning" for check in report.checks)


def test_doctor_reports_docker_healthcheck_ok(tmp_path):
    project = _make_healthy_project(tmp_path)
    report = analyze_project(project)
    assert any(check.name == "Docker healthcheck" and check.status == "passed" for check in report.checks)


def test_doctor_ignores_documented_env_examples(tmp_path):
    project = _make_healthy_project(tmp_path)
    (project / ".env.example").write_text("DATABASE_URL=postgresql://user:pass@localhost/app\n", encoding="utf-8")
    report = analyze_project(project)
    assert not any(check.category == "security" and check.status == "warning" for check in report.checks)


def test_doctor_detects_potential_secret(tmp_path):
    project = _make_healthy_project(tmp_path)
    settings = project / "app" / "settings.py"
    settings.write_text("API_KEY = 'super-secret-value'\n", encoding="utf-8")
    report = analyze_project(project)
    assert any(check.category == "security" and check.status == "warning" for check in report.checks)


def test_doctor_handles_non_git_directory(tmp_path):
    project = _make_healthy_project(tmp_path)
    (project / ".git").rmdir()
    report = analyze_project(project)
    assert any(check.name == "Git repository" and check.status in {"warning", "skipped"} for check in report.checks)


def test_doctor_supports_framework_specific_checks(tmp_path):
    project = _make_healthy_project(tmp_path)
    report = analyze_project(project)
    assert any(check.category == "project" and "framework" in (check.message or "").lower() for check in report.checks)


def test_doctor_json_output(tmp_path, capsys):
    project = _make_healthy_project(tmp_path)
    code = run_doctor_command([str(project), "--json"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["project"]["name"] == "billing-api"
    assert payload["summary"]["passed"] >= 1
    assert code in {0, 1}


def test_doctor_exit_codes_for_error(tmp_path):
    project = tmp_path / "bad"
    project.mkdir()
    code = run_doctor_command([str(project)])
    assert code == 1


def test_doctor_exit_code_for_invalid_usage():
    code = run_doctor_command(["--bad-flag"])
    assert code == 2
