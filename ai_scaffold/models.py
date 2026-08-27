"""Validated intermediate representations used by the scaffolding engine."""

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

ALLOWED_CHANGE_TYPES = {
    "add_file",
    "append",
    "replace",
    "insert_after",
    "insert_before",
}
ENVIRONMENT_NAME = re.compile(r"^[A-Z_][A-Z0-9_]*$")


@dataclass
class ProjectSpec:
    name: str
    language: str = "python"
    framework: str = "fastapi"
    database: str = "sqlite"
    components: List[str] = field(default_factory=lambda: ["fastapi", "pytest"])
    output_dir: str = "."

    def validate(self) -> None:
        if not self.name or any(part in self.name for part in ("/", "\\", "..")):
            raise ValueError("Project name must be a simple directory name.")
        if self.language != "python" or self.framework != "fastapi":
            raise ValueError("The MVP currently supports Python and FastAPI only.")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Change:
    type: str
    path: str
    content: str = ""
    anchor: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Change":
        if not isinstance(data, dict):
            raise ValueError("Each change must be a JSON object.")
        change = cls(
            type=str(data.get("type", "")),
            path=str(data.get("path", "")),
            content=str(data.get("content", "")),
            anchor=str(data.get("anchor", "")),
        )
        change.validate()
        return change

    def validate(self) -> None:
        if self.type not in ALLOWED_CHANGE_TYPES:
            raise ValueError(f"Unsupported change type: {self.type}")
        if (
            not self.path
            or self.path.startswith(("/", "\\"))
            or ".." in self.path.replace("\\", "/").split("/")
        ):
            raise ValueError(f"Unsafe project-relative path: {self.path!r}")
        if len(self.content.encode("utf-8")) > 1_000_000:
            raise ValueError("A single injected change may not exceed 1 MB.")
        if (
            self.type in {"replace", "insert_after", "insert_before"}
            and not self.anchor
        ):
            raise ValueError(f"Change type {self.type!r} requires a non-empty anchor.")

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class ChangePlan:
    operation: str
    component: str
    changes: List[Change] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    environment: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChangePlan":
        if not isinstance(data, dict):
            raise ValueError("A plan must be a JSON object.")
        changes = data.get("changes", [])
        dependencies = data.get("dependencies", [])
        environment = data.get("environment", [])
        if not all(
            isinstance(value, list) for value in (changes, dependencies, environment)
        ):
            raise ValueError(
                "changes, dependencies, and environment must be JSON arrays."
            )
        plan = cls(
            operation=str(data.get("operation", "inject_code")),
            component=str(data.get("component", "custom")),
            changes=[Change.from_dict(item) for item in changes],
            dependencies=[str(item) for item in dependencies],
            environment=[str(item) for item in environment],
        )
        plan.validate()
        return plan

    def validate(self) -> None:
        if not self.operation or not self.component:
            raise ValueError("Plans require operation and component values.")
        for change in self.changes:
            change.validate()
        for dependency in self.dependencies:
            if (
                not dependency
                or "\n" in dependency
                or "\r" in dependency
                or dependency.startswith("-")
                or "#" in dependency
            ):
                raise ValueError(
                    "Dependencies must be ordinary, single-line package requirements."
                )
        for variable in self.environment:
            if not ENVIRONMENT_NAME.fullmatch(variable):
                raise ValueError(
                    "Environment values must be uppercase variable names, for example DATABASE_URL."
                )

    def is_empty(self) -> bool:
        return not (self.changes or self.dependencies or self.environment)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "component": self.component,
            "changes": [change.to_dict() for change in self.changes],
            "dependencies": self.dependencies,
            "environment": self.environment,
        }

    @staticmethod
    def json_schema() -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["operation", "component", "changes"],
            "properties": {
                "operation": {
                    "type": "string",
                    "examples": ["inject_code", "add_components"],
                },
                "component": {"type": "string", "examples": ["custom-invoice-rules"]},
                "changes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["type", "path", "content"],
                        "properties": {
                            "type": {"enum": sorted(ALLOWED_CHANGE_TYPES)},
                            "path": {
                                "type": "string",
                                "description": "Relative path inside the project",
                            },
                            "content": {"type": "string"},
                            "anchor": {
                                "type": "string",
                                "description": "Required for replace and insert operations",
                            },
                        },
                    },
                },
                "dependencies": {"type": "array", "items": {"type": "string"}},
                "environment": {"type": "array", "items": {"type": "string"}},
            },
        }
