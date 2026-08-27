"""Previewable, transactional deterministic component execution."""

import ast
import shutil
import tempfile
from pathlib import Path
from typing import Iterable, List

from .manifest import load, write
from .models import Change, ChangePlan
from .registry import Component, resolve


class ScaffoldingEngine:
    def plan_components(
        self, names: Iterable[str], installed: Iterable[str] = ()
    ) -> ChangePlan:
        components = resolve(names, installed)
        changes: List[Change] = []
        dependencies, environment = [], []
        for component in components:
            changes.extend(self._changes_for(component))
            dependencies.extend(component.dependencies)
            environment.extend(component.environment)
        component_names = ", ".join(item.name for item in components) or "no-op"
        return ChangePlan(
            "add_components",
            component_names,
            changes,
            sorted(set(dependencies)),
            sorted(set(environment)),
        )

    @staticmethod
    def _changes_for(component: Component) -> List[Change]:
        files = {
            "sqlalchemy": (
                "app/db.py",
                "from sqlalchemy.orm import DeclarativeBase\n\n\nclass Base(DeclarativeBase):\n    pass\n",
            ),
            "redis": (
                "app/redis.py",
                "import os\n\nREDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')\n",
            ),
            "celery": (
                "app/tasks.py",
                "from celery import Celery\nimport os\n\ncelery_app = Celery('app', broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'))\n",
            ),
            "docker": (
                "Dockerfile",
                'FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nCMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]\n',
            ),
            "pytest": (
                "tests/test_health.py",
                "def test_placeholder():\n    assert True\n",
            ),
        }
        if component.name in files:
            path, content = files[component.name]
            return [Change("add_file", path, content)]
        if component.name in {"email-auth", "google-auth"}:
            route_name = "email" if component.name == "email-auth" else "google"
            function = "login" if route_name == "email" else "google_login"
            decorator = (
                "@router.post('/login')"
                if route_name == "email"
                else "@router.get('/google')"
            )
            body = (
                "from fastapi import APIRouter\n\n"
                "router = APIRouter(prefix='/auth', tags=['auth'])\n\n"
                f"{decorator}\n"
                f"def {function}():\n"
                "    return {'detail': 'Configure authentication before enabling this endpoint.'}\n"
            )
            import_line = f"from app.auth.{route_name} import router as {route_name}_auth_router\n"
            changes = [
                Change("add_file", f"app/auth/{route_name}.py", body),
                Change(
                    "insert_after",
                    "app/main.py",
                    import_line,
                    "from fastapi import FastAPI\n",
                ),
                Change(
                    "insert_before",
                    "app/main.py",
                    f"app.include_router({route_name}_auth_router)\n\n",
                    "@app.get('/health')\n",
                ),
            ]
            if route_name == "email":
                changes.insert(0, Change("add_file", "app/auth/__init__.py", ""))
            return changes
        return []

    def apply(self, root: Path, plan: ChangePlan) -> None:
        root = root.resolve()
        if not root.is_dir():
            raise ValueError(f"Project directory does not exist: {root}")
        plan.validate()
        metadata = load(root)
        if plan.is_empty():
            return
        self.preview(root, plan)
        backup_parent = Path(tempfile.mkdtemp(prefix="ai-scaffold-rollback-"))
        backup = backup_parent / "project"
        shutil.copytree(root, backup, dirs_exist_ok=True)
        try:
            for change in plan.changes:
                self._apply_change(root, change)
            self._append_lines(root / "requirements.txt", plan.dependencies)
            self._append_environment(root / ".env.example", plan.environment)
            self.validate(root)
            additions = [
                part for part in plan.component.split(", ") if part and part != "no-op"
            ]
            metadata["components"] = sorted(
                set(metadata.get("components", []) + additions)
            )
            write(root, metadata)
        except Exception:
            shutil.rmtree(root)
            shutil.copytree(backup, root)
            raise
        finally:
            shutil.rmtree(backup_parent, ignore_errors=True)

    def preview(self, root: Path, plan: ChangePlan) -> dict:
        """Validate a plan and report its exact effects without modifying files."""
        root = root.resolve()
        plan.validate()
        result = {
            "files": [],
            "dependencies": plan.dependencies,
            "environment": plan.environment,
        }
        virtual_files = {}
        for change in plan.changes:
            target = self._safe_target(root, change.path)
            if target not in virtual_files:
                virtual_files[target] = (
                    target.exists(),
                    target.read_text(encoding="utf-8") if target.exists() else "",
                )
            exists, text = virtual_files[target]
            virtual_files[target] = self._render_change(change, exists, text)
            result["files"].append({"path": change.path, "operation": change.type})
        return result

    def _apply_change(self, root: Path, change: Change) -> None:
        target = self._safe_target(root, change.path)
        exists = target.exists()
        current = target.read_text(encoding="utf-8") if exists else ""
        _, updated = self._render_change(change, exists, current)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(updated, encoding="utf-8")

    @staticmethod
    def _render_change(change: Change, exists: bool, current: str) -> tuple[bool, str]:
        """Apply one change to in-memory content for preview and execution parity."""
        if change.type == "add_file":
            if exists:
                raise ValueError(f"Refusing to overwrite existing file: {change.path}")
            return True, change.content
        if not exists:
            raise ValueError(f"Cannot modify a missing file: {change.path}")
        if change.type == "append":
            return True, current + change.content
        if change.anchor not in current:
            raise ValueError(f"Anchor was not found in {change.path}")
        if change.type == "replace":
            return True, current.replace(change.anchor, change.content, 1)
        if change.type == "insert_after":
            return True, current.replace(
                change.anchor, change.anchor + change.content, 1
            )
        if change.type == "insert_before":
            return True, current.replace(
                change.anchor, change.content + change.anchor, 1
            )
        raise ValueError(f"Unsupported change type: {change.type}")

    @staticmethod
    def _safe_target(root: Path, relative: str) -> Path:
        target = (root / relative).resolve()
        if root not in target.parents:
            raise ValueError("A planned path escapes the project root.")
        return target

    @staticmethod
    def _append_lines(path: Path, values: Iterable[str]) -> None:
        existing = (
            path.read_text(encoding="utf-8").splitlines() if path.exists() else []
        )
        additions = [value for value in values if value not in existing]
        if additions:
            path.write_text("\n".join(existing + additions) + "\n", encoding="utf-8")

    @staticmethod
    def _append_environment(path: Path, variables: Iterable[str]) -> None:
        existing = (
            path.read_text(encoding="utf-8").splitlines() if path.exists() else []
        )
        additions = [
            f"{variable}="
            for variable in variables
            if not any(line.startswith(f"{variable}=") for line in existing)
        ]
        if additions:
            path.write_text("\n".join(existing + additions) + "\n", encoding="utf-8")

    @staticmethod
    def validate(root: Path) -> None:
        failures = []
        for source in root.rglob("*.py"):
            if any(part in {"venv", ".venv", ".ai-scaffold"} for part in source.parts):
                continue
            try:
                ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
            except (OSError, SyntaxError) as exc:
                failures.append(str(exc))
        if failures:
            raise ValueError("Python syntax validation failed: " + "; ".join(failures))
