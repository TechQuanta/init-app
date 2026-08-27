"""Provider-neutral planning with a deterministic local MVP provider."""

import re
from typing import Iterable, List

from .models import ProjectSpec
from .registry import COMPONENTS, normalize, resolve


class LLMProvider:
    """Interface kept independent from deterministic execution."""

    def generate_project_plan(self, request: str, context: dict) -> ProjectSpec:
        raise NotImplementedError

    def generate_change_plan(self, request: str, context: dict):
        raise NotImplementedError

    def generate_code(self, request: str, context: dict):
        raise NotImplementedError


class KeywordProvider(LLMProvider):
    """Offline MVP intent parser; replaceable by an API-backed provider later."""

    def _components(self, request: str) -> List[str]:
        text = request.lower()
        found = []
        phrases = sorted(
            list(COMPONENTS)
            + list(
                {
                    "google oauth",
                    "google authentication",
                    "background jobs",
                    "email authentication",
                }
            ),
            key=len,
            reverse=True,
        )
        for phrase in phrases:
            if re.search(
                r"(?<!\w)" + re.escape(phrase).replace(r"\ ", r"\s+") + r"(?!\w)", text
            ):
                name = normalize(phrase)
                if name in COMPONENTS and name not in found:
                    found.append(name)
        if "postgres" in text and "postgresql" not in found:
            found.append("postgresql")
        return [component.name for component in resolve(found)]

    def generate_project_plan(self, request: str, context: dict) -> ProjectSpec:
        name = context.get("name") or "fastapi_app"
        components = self._components(request)
        if "fastapi" not in components:
            components.insert(0, "fastapi")
        if "pytest" not in components:
            components.append("pytest")
        database = "postgresql" if "postgresql" in components else "sqlite"
        return ProjectSpec(
            name=name,
            database=database,
            components=components,
            output_dir=context.get("output_dir", "."),
        )
