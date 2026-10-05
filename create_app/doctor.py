from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


VALID_STATUSES = {"passed", "warning", "error", "skipped"}


@dataclass
class CheckResult:
    name: str
    category: str
    status: str
    message: str
    details: dict[str, Any] | None = None
    file: str | None = None
    line: int | None = None
    recommendation: str | None = None

    def __post_init__(self):
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Unsupported status: {self.status!r}")

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "category": self.category,
            "status": self.status,
            "message": self.message,
        }
        if self.details:
            payload["details"] = self.details
        if self.file:
            payload["file"] = self.file
        if self.line is not None:
            payload["line"] = self.line
        if self.recommendation:
            payload["recommendation"] = self.recommendation
        return payload


@dataclass
class ProjectContext:
    root: Path
    metadata: dict[str, Any]
    metadata_error: str | None = None
    framework: str | None = None
    project_name: str | None = None
    python_version: str = field(default_factory=lambda: ".".join(str(part) for part in sys.version_info[:3]))
    gitignore_text: str = ""
    python_files: list[Path] = field(default_factory=list)


@dataclass
class HealthReport:
    project: dict[str, str]
    checks: list[CheckResult]

    @property
    def summary(self) -> dict[str, int]:
        counts = {"passed": 0, "warnings": 0, "errors": 0, "skipped": 0}
        for check in self.checks:
            if check.status == "passed":
                counts["passed"] += 1
            elif check.status == "warning":
                counts["warnings"] += 1
            elif check.status == "error":
                counts["errors"] += 1
            elif check.status == "skipped":
                counts["skipped"] += 1
        return counts

    @property
    def exit_code(self) -> int:
        summary = self.summary
        if summary["errors"] > 0:
            return 1
        if summary["warnings"] > 0:
            return 1
        return 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "project": self.project,
            "summary": self.summary,
            "checks": [check.as_dict() for check in self.checks],
        }

    def render_human(self, verbose: bool = False) -> str:
        project_name = self.project.get("name", "unknown")
        framework = self.project.get("framework", "unknown")
        python_version = self.project.get("python_version") or "unknown"
        lines = [
            "init-app Doctor",
            "",
            f"Project: {project_name}",
            f"Framework: {framework}",
            f"Python: {python_version}",
            "",
        ]
        categories: dict[str, list[CheckResult]] = {}
        for check in self.checks:
            categories.setdefault(check.category, []).append(check)

        for category in ["project", "environment", "dependencies", "configuration", "git", "docker", "python", "security"]:
            if category not in categories:
                continue
            lines.append(category.title())
            for check in categories[category]:
                icon = {
                    "passed": "✓",
                    "warning": "⚠",
                    "error": "✗",
                    "skipped": "-",
                }[check.status]
                lines.append(f"  {icon} {check.name}")
                if verbose and check.status in {"warning", "error"}:
                    lines.append(f"    {check.message}")
                    if check.recommendation:
                        lines.append(f"    Recommendation: {check.recommendation}")
            lines.append("")

        summary = self.summary
        lines.extend([
            "────────────────────────────",
            "",
            "Summary",
            "",
            f"✓ {summary['passed']} passed",
            f"⚠ {summary['warnings']} warnings",
            f"✗ {summary['errors']} errors",
            "",
            f"Health: {'HEALTHY' if summary['errors'] == 0 and summary['warnings'] == 0 else 'NEEDS ATTENTION'}",
        ])
        if summary["errors"] > 0 or summary["warnings"] > 0:
            lines.append("")
            lines.append("Run `init-app doctor --verbose` for details.")
        return "\n".join(lines)


class HealthCheck:
    name: str = ""
    category: str = "project"

    def run(self, project: ProjectContext) -> CheckResult:
        raise NotImplementedError


class ProjectMetadataCheck(HealthCheck):
    name = "Project metadata"
    category = "project"

    def run(self, project: ProjectContext) -> CheckResult:
        if project.metadata_error:
            return CheckResult(
                self.name,
                self.category,
                "error",
                project.metadata_error,
                recommendation="Create the project with init-app and keep .init-app.json in the project root.",
            )
        metadata = project.metadata
        if not isinstance(metadata, dict):
            return CheckResult(self.name, self.category, "error", "Project metadata is unreadable.")
        project_name = metadata.get("project_name") or metadata.get("name") or project.root.name
        framework = metadata.get("framework") or project.framework or "unknown"
        if not project_name:
            return CheckResult(self.name, self.category, "error", "Project metadata is missing the project name.")
        issues: list[str] = []
        if project.root.name != str(project_name) and project.root.name not in {str(project_name), str(project_name).replace("_", "-")}: 
            issues.append("Project folder name does not match metadata.")
        if not framework or framework == "unknown":
            issues.append("Framework could not be identified from project metadata.")
        if issues:
            return CheckResult(self.name, self.category, "warning", "; ".join(issues), recommendation="Keep .init-app.json consistent with the generated project folder and framework.")
        return CheckResult(self.name, self.category, "passed", f"{project_name} metadata is valid.")


class RequiredFilesCheck(HealthCheck):
    name = "Required files"
    category = "project"

    def run(self, project: ProjectContext) -> CheckResult:
        required = ["README.md", "requirements.txt", ".gitignore"]
        if not any((project.root / path).exists() for path in required):
            missing = [path for path in required if not (project.root / path).exists()]
            return CheckResult(self.name, self.category, "error", f"Missing required files: {', '.join(missing)}")
        missing = [path for path in required if not (project.root / path).exists()]
        if missing:
            return CheckResult(self.name, self.category, "error", f"Missing required files: {', '.join(missing)}")
        if ".env.example" not in [item.name for item in project.root.iterdir() if item.is_file()]:
            return CheckResult(self.name, self.category, "warning", "The project does not include a .env.example template.")
        return CheckResult(self.name, self.category, "passed", "Required project files are present.")


class ProjectStructureCheck(HealthCheck):
    name = "Project structure"
    category = "project"

    def run(self, project: ProjectContext) -> CheckResult:
        framework = (project.framework or "").lower()
        expected = ["app", "src"]
        present = [name for name in expected if (project.root / name).is_dir()]
        if framework == "fastapi":
            if present:
                return CheckResult(self.name, self.category, "passed", f"Framework directory present: {', '.join(present)}")
            return CheckResult(self.name, self.category, "warning", "FastAPI project structure is not obvious from the root folders.")
        if framework == "django":
            if (project.root / "manage.py").exists() or any((project.root / item).exists() for item in ("manage.py", "settings.py")):
                return CheckResult(self.name, self.category, "passed", "Django project root looks structurally valid.")
            return CheckResult(self.name, self.category, "warning", "Django project structure does not include manage.py or settings.py.")
        if present:
            return CheckResult(self.name, self.category, "passed", f"Project folders detected: {', '.join(present)}")
        return CheckResult(self.name, self.category, "warning", "No obvious application directories were detected.")


class FrameworkSpecificCheck(HealthCheck):
    name = "Framework checks"
    category = "project"

    def run(self, project: ProjectContext) -> CheckResult:
        framework = (project.framework or "").lower()
        if not framework or framework == "unknown":
            return CheckResult(self.name, self.category, "skipped", "Framework-specific checks are skipped when the framework cannot be determined.")
        checks = {
            "fastapi": ["app/main.py", "src/main.py"],
            "flask": ["app.py", "wsgi.py"],
            "django": ["manage.py", "settings.py"],
            "mcp": ["registry.json", "mcp-tools"],
        }
        markers = checks.get(framework, [])
        if not markers:
            return CheckResult(self.name, self.category, "passed", f"Framework {framework} has no special structural rule in this project.")
        found = [marker for marker in markers if (project.root / marker).exists()]
        if found:
            return CheckResult(self.name, self.category, "passed", f"Framework {framework} markers found: {', '.join(found)}")
        return CheckResult(self.name, self.category, "warning", f"Framework {framework} markers are missing from the generated project.")


class PythonVersionCheck(HealthCheck):
    name = "Python version"
    category = "environment"

    def run(self, project: ProjectContext) -> CheckResult:
        current = sys.version_info[:3]
        requirement = project.metadata.get("requires_python") or project.metadata.get("python_requires")
        if not requirement:
            return CheckResult(self.name, self.category, "passed", f"Python {project.python_version}")
        if not _version_satisfies(current, requirement):
            return CheckResult(
                self.name,
                self.category,
                "error",
                f"Python {project.python_version} does not satisfy required version {requirement}.",
                recommendation="Install or select a matching Python interpreter for this project.",
            )
        return CheckResult(self.name, self.category, "passed", f"Python {project.python_version} matches {requirement}.")


class VirtualEnvironmentCheck(HealthCheck):
    name = "Virtual environment"
    category = "environment"

    def run(self, project: ProjectContext) -> CheckResult:
        executable = Path(sys.executable).resolve()
        text = str(executable).lower()
        root_markers = [project.root / "venv", project.root / ".venv"]
        if sys.prefix != sys.base_prefix or any(marker.exists() for marker in root_markers) or ".venv" in text or "venv" in text:
            return CheckResult(self.name, self.category, "passed", "Virtual environment detected.")
        if any((project.root / item).exists() for item in ["requirements.txt", "pyproject.toml", "setup.py"]):
            return CheckResult(self.name, self.category, "warning", "Python project is present but no local virtual environment was detected.")
        return CheckResult(self.name, self.category, "skipped", "No Python runtime requirements were detected for this project.")


class DependencyCheck(HealthCheck):
    name = "Dependencies"
    category = "dependencies"

    def run(self, project: ProjectContext) -> CheckResult:
        req_path = project.root / "requirements.txt"
        if not req_path.exists():
            return CheckResult(self.name, self.category, "skipped", "No requirements.txt file was found, so dependency validation was skipped.")
        packages: list[str] = []
        missing: list[str] = []
        for line in req_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            candidate = line.strip()
            if not candidate or candidate.startswith("#"):
                continue
            pkg = candidate.split(";", 1)[0].strip()
            if not pkg:
                continue
            pkg_name = re.split(r"[<>=!\[]", pkg, maxsplit=1)[0].strip()
            if not pkg_name:
                continue
            packages.append(pkg_name)
            if not importlib.util.find_spec(_module_name(pkg_name)):
                missing.append(pkg_name)
        if missing:
            return CheckResult(
                self.name,
                self.category,
                "warning",
                f"Declared dependencies are not all importable: {', '.join(missing)}.",
                recommendation="Install the project dependencies in the active environment before validating runtime behavior.",
            )
        return CheckResult(self.name, self.category, "passed", f"{len(packages)} dependency entries are available to Python.")


class EnvironmentConfigCheck(HealthCheck):
    name = ".env.example"
    category = "configuration"

    def run(self, project: ProjectContext) -> CheckResult:
        env_example = project.root / ".env.example"
        env_file = project.root / ".env"
        if not env_example.exists():
            return CheckResult(self.name, self.category, "warning", ".env.example is missing.", recommendation="Add a .env.example file that documents required environment variables.")
        if env_file.exists():
            env_value = env_file.read_text(encoding="utf-8", errors="ignore")
            if "DATABASE_URL" in env_value or "SECRET_KEY" in env_value:
                return CheckResult(self.name, self.category, "passed", ".env.example is present and the environment template declares common variables.")
        return CheckResult(self.name, self.category, "passed", ".env.example is present.")


class DotenvIgnoreCheck(HealthCheck):
    name = ".env ignored"
    category = "configuration"

    def run(self, project: ProjectContext) -> CheckResult:
        gitignore = project.gitignore_text.lower()
        if ".env" in gitignore or ".env.*" in gitignore:
            return CheckResult(self.name, self.category, "passed", ".env is included in the git ignore rules.")
        return CheckResult(self.name, self.category, "warning", ".env is not ignored by git.", recommendation="Add .env and .env.* to .gitignore to prevent local secrets from being committed.")


class GitCheck(HealthCheck):
    name = "Git repository"
    category = "git"

    def run(self, project: ProjectContext) -> CheckResult:
        git_dir = project.root / ".git"
        if not git_dir.exists():
            return CheckResult(self.name, self.category, "warning", "This directory is not a git repository.", recommendation="Initialize Git if the project should be versioned.")
        ignore_file = project.root / ".gitignore"
        if not ignore_file.exists():
            return CheckResult(self.name, self.category, "warning", ".gitignore is missing.", recommendation="Add a repository .gitignore file to track generated artifacts and local secrets appropriately.")
        content = ignore_file.read_text(encoding="utf-8", errors="ignore")
        patterns = {"__pycache__/", ".venv/", ".env", "build/", "dist/"}
        missing = [item for item in sorted(patterns) if item not in content]
        if missing:
            return CheckResult(self.name, self.category, "warning", "Common generated artifacts are not all covered by .gitignore: " + ", ".join(missing), recommendation="Add the missing ignore rules to .gitignore.")
        return CheckResult(self.name, self.category, "passed", "Git repository and important ignore rules look healthy.")


class DockerfileCheck(HealthCheck):
    name = "Dockerfile"
    category = "docker"

    def run(self, project: ProjectContext) -> CheckResult:
        dockerfile = project.root / "Dockerfile"
        if not dockerfile.exists():
            return CheckResult(self.name, self.category, "skipped", "Docker is not configured for this project.")
        content = dockerfile.read_text(encoding="utf-8", errors="ignore")
        if "FROM " not in content:
            return CheckResult(self.name, self.category, "error", "Dockerfile is missing a valid FROM instruction.")
        if "WORKDIR " not in content:
            return CheckResult(self.name, self.category, "warning", "Dockerfile does not include a WORKDIR instruction.")
        if "CMD " not in content and "ENTRYPOINT " not in content:
            return CheckResult(self.name, self.category, "warning", "Dockerfile does not define a startup command.")
        return CheckResult(self.name, self.category, "passed", "Dockerfile exists and has basic runtime instructions.")


class DockerHealthCheck(HealthCheck):
    name = "Docker healthcheck"
    category = "docker"

    def run(self, project: ProjectContext) -> CheckResult:
        dockerfile = project.root / "Dockerfile"
        if not dockerfile.exists():
            return CheckResult(self.name, self.category, "skipped", "No Dockerfile exists, so health checks were skipped.")
        content = dockerfile.read_text(encoding="utf-8", errors="ignore")
        if "HEALTHCHECK" in content:
            return CheckResult(self.name, self.category, "passed", "Docker healthcheck is configured.")
        return CheckResult(self.name, self.category, "warning", "Docker healthcheck is missing.", recommendation="Add a HEALTHCHECK instruction to confirm the app's service is healthy.")


class DockerIgnoreCheck(HealthCheck):
    name = ".dockerignore"
    category = "docker"

    def run(self, project: ProjectContext) -> CheckResult:
        dockerignore = project.root / ".dockerignore"
        if not (project.root / "Dockerfile").exists():
            return CheckResult(self.name, self.category, "skipped", "Docker files are not present in this project.")
        if dockerignore.exists():
            return CheckResult(self.name, self.category, "passed", ".dockerignore is present.")
        return CheckResult(self.name, self.category, "warning", ".dockerignore is missing.", recommendation="Exclude large directories such as .git, .venv, and __pycache__ from Docker build context.")


class PythonSyntaxCheck(HealthCheck):
    name = "Python syntax"
    category = "python"

    def run(self, project: ProjectContext) -> CheckResult:
        files = project.python_files
        if not files:
            return CheckResult(self.name, self.category, "skipped", "No Python files were found to validate.")
        errors: list[str] = []
        for path in files:
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError as exc:
                errors.append(f"{path.relative_to(project.root)}:{exc.lineno}: {exc.msg}")
        if errors:
            error_text = "; ".join(errors[:3])
            return CheckResult(self.name, self.category, "error", f"Syntax errors detected in Python files: {error_text}", details={"errors": errors[:5]})
        return CheckResult(self.name, self.category, "passed", f"{len(files)} Python files compiled successfully.")


class SecurityCheck(HealthCheck):
    name = "Potential secrets"
    category = "security"

    def run(self, project: ProjectContext) -> CheckResult:
        items: list[tuple[str, int, str]] = []
        for path in _iter_project_files(project.root):
            if path.name in {".env.example", ".env.sample", ".env.template"}:
                continue
            if path.name.startswith(".") and path.name != ".env":
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for idx, line in enumerate(content.splitlines(), start=1):
                if _looks_like_secret(line):
                    items.append((str(path.relative_to(project.root)), idx, _secret_type(line)))
        if not items:
            return CheckResult(self.name, self.category, "passed", "No obvious credential patterns were detected.")
        item = items[0]
        return CheckResult(
            self.name,
            self.category,
            "warning",
            f"Potential secret detected in {item[0]}:{item[1]} ({item[2]}).",
            file=item[0],
            line=item[1],
            recommendation="Rotate the secret if it is real and move it to a secret manager or a local .env that remains ignored by git.",
        )


def _module_name(package_name: str) -> str:
    return package_name.lower().replace("-", "_").replace(".", "_")


def _version_satisfies(current: tuple[int, ...], requirement: str) -> bool:
    if not requirement:
        return True
    target_str = requirement.strip()
    if not target_str:
        return True
    for operator in (">=", "<=", ">", "<", "==", "!="):
        if operator in target_str:
            left, right = re.split(operator, target_str, maxsplit=1)
            if not right:
                return True
            right = right.strip()
            version = re.findall(r"\d+", right)
            if not version:
                return True
            target = tuple(int(part) for part in version[:3])
            current_version = current[:len(target)]
            if operator == ">=":
                return current_version >= target
            if operator == "<=":
                return current_version <= target
            if operator == ">":
                return current_version > target
            if operator == "<":
                return current_version < target
            if operator == "==":
                return current_version == target
            if operator == "!=":
                return current_version != target
            break
    return True


def _iter_project_files(root: Path):
    exclude_dirs = {".git", ".venv", "venv", "__pycache__", "node_modules", "dist", "build", ".mypy_cache", ".pytest_cache"}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name.endswith(".pyc"):
            continue
        if any(part in exclude_dirs for part in path.parts):
            continue
        yield path


def _looks_like_secret(line: str) -> bool:
    normalized = line.strip()
    if not normalized or normalized.startswith("#"):
        return False
    markers = [
        "API_KEY", "SECRET_KEY", "PASSWORD", "TOKEN", "PRIVATE_KEY",
        "SESSION_SECRET", "ACCESS_TOKEN", "DB_PASSWORD", "CLIENT_SECRET",
        "JWT_SECRET", "AUTH_TOKEN", "OPENAI_API_KEY", "DATABASE_URL",
    ]
    if re.search(r"(?:BEGIN (?:RSA |DSA |EC )?PRIVATE KEY)", normalized, re.IGNORECASE):
        return True
    if any(marker in normalized.upper() for marker in markers):
        return True
    return False


def _secret_type(line: str) -> str:
    value = line.strip()
    upper = value.upper()
    for marker in ["API_KEY", "SECRET_KEY", "PASSWORD", "TOKEN", "PRIVATE_KEY", "CLIENT_SECRET", "ACCESS_TOKEN", "SESSION_SECRET"]:
        if marker in upper:
            return marker.lower().replace("_", " ")
    if "BEGIN " in upper and "PRIVATE KEY" in upper:
        return "private key"
    return "possible secret"


def _collect_python_files(root: Path) -> list[Path]:
    exclude_dirs = {".git", ".venv", "venv", "__pycache__", "node_modules", "dist", "build", ".mypy_cache", ".pytest_cache"}
    files: list[Path] = []
    for path in root.rglob("*.py"):
        if any(part in exclude_dirs for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def _project_metadata(root: Path) -> tuple[dict[str, Any], str | None]:
    metadata_path = root / ".init-app.json"
    if not metadata_path.exists():
        return {}, "Project metadata file .init-app.json is missing."
    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, f"Project metadata is invalid JSON: {exc.msg} (line {exc.lineno})."
    except OSError as exc:
        return {}, f"Unable to read project metadata: {exc}."
    if not isinstance(data, dict):
        return {}, "Project metadata must be a JSON object."
    return data, None


def _project_framework(metadata: dict[str, Any], root: Path) -> str | None:
    field_value = metadata.get("framework") or metadata.get("fw_name")
    if field_value:
        return str(field_value).lower()
    text = (root / "requirements.txt").read_text(encoding="utf-8", errors="ignore") if (root / "requirements.txt").exists() else ""
    if "fastapi" in text.lower():
        return "fastapi"
    if "django" in text.lower():
        return "django"
    if "flask" in text.lower():
        return "flask"
    if (root / "manage.py").exists():
        return "django"
    return None


def analyze_project(project_dir: str | Path) -> HealthReport:
    root = Path(project_dir).expanduser().resolve()
    metadata, metadata_error = _project_metadata(root)
    framework = _project_framework(metadata, root)
    project_name = str(metadata.get("project_name") or metadata.get("name") or root.name)
    gitignore_text = (root / ".gitignore").read_text(encoding="utf-8", errors="ignore") if (root / ".gitignore").exists() else ""
    context = ProjectContext(
        root=root,
        metadata=metadata,
        metadata_error=metadata_error,
        framework=framework,
        project_name=project_name,
        gitignore_text=gitignore_text,
        python_files=_collect_python_files(root),
    )
    checks = [
        ProjectMetadataCheck().run(context),
        RequiredFilesCheck().run(context),
        ProjectStructureCheck().run(context),
        FrameworkSpecificCheck().run(context),
        PythonVersionCheck().run(context),
        VirtualEnvironmentCheck().run(context),
        DependencyCheck().run(context),
        EnvironmentConfigCheck().run(context),
        DotenvIgnoreCheck().run(context),
        GitCheck().run(context),
        DockerfileCheck().run(context),
        DockerHealthCheck().run(context),
        DockerIgnoreCheck().run(context),
        PythonSyntaxCheck().run(context),
        SecurityCheck().run(context),
    ]
    report = HealthReport(
        project={
            "name": project_name,
            "framework": framework or "unknown",
            "python_version": context.python_version,
        },
        checks=checks,
    )
    return report


def run_doctor_command(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="init-app doctor", description="Analyze a generated project and report health issues.")
    parser.add_argument("project_dir", nargs="?", default=".", help="Project directory to inspect. Defaults to the current directory.")
    parser.add_argument("--verbose", action="store_true", help="Print detailed diagnostics and recommendations.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--category", choices=["project", "environment", "dependencies", "configuration", "git", "docker", "python", "security"], help="Filter the diagnostic output to a single category.")

    args = argv if argv is not None else sys.argv[1:]
    try:
        parsed = parser.parse_args(list(args))
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) and exc.code in {0, 1, 2} else 2

    project_dir = Path(parsed.project_dir).expanduser().resolve()
    if not project_dir.exists() or not project_dir.is_dir():
        print(f"Project directory does not exist: {project_dir}", file=sys.stderr)
        return 2

    report = analyze_project(project_dir)
    if parsed.category:
        filtered = [check for check in report.checks if check.category == parsed.category]
        report = HealthReport(project=report.project, checks=filtered)

    if parsed.json:
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    else:
        print(report.render_human(verbose=parsed.verbose))
    return report.exit_code


__all__ = ["CheckResult", "HealthReport", "HealthCheck", "ProjectContext", "analyze_project", "run_doctor_command"]
