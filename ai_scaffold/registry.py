"""Small, local component registry for the MVP.

Components are declarative so a future LLM only selects them; it never owns
filesystem mutations.
"""

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class Component:
    name: str
    description: str
    dependencies: tuple[str, ...] = ()
    environment: tuple[str, ...] = ()
    requires: tuple[str, ...] = ("fastapi",)


COMPONENTS: Dict[str, Component] = {
    "fastapi": Component(
        "fastapi",
        "FastAPI application runtime",
        ("fastapi", "uvicorn[standard]"),
        requires=(),
    ),
    "postgresql": Component(
        "postgresql",
        "PostgreSQL database adapter",
        ("psycopg[binary]", "sqlalchemy"),
        requires=("fastapi", "sqlalchemy"),
    ),
    "sqlalchemy": Component("sqlalchemy", "SQLAlchemy ORM", ("sqlalchemy",)),
    "email-auth": Component(
        "email-auth",
        "Email/password authentication",
        ("passlib[bcrypt]", "python-jose[cryptography]"),
        ("JWT_SECRET",),
    ),
    "google-auth": Component(
        "google-auth",
        "Google OAuth authentication",
        ("authlib",),
        ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"),
        ("fastapi", "email-auth"),
    ),
    "jwt": Component(
        "jwt", "JWT token support", ("python-jose[cryptography]",), ("JWT_SECRET",)
    ),
    "redis": Component("redis", "Redis client", ("redis",), ("REDIS_URL",)),
    "celery": Component(
        "celery",
        "Celery background jobs",
        ("celery",),
        ("CELERY_BROKER_URL",),
        ("fastapi", "redis"),
    ),
    "docker": Component("docker", "Docker development configuration"),
    "pytest": Component("pytest", "Pytest test runner", ("pytest",)),
}

ALIASES = {
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "google": "google-auth",
    "google oauth": "google-auth",
    "google authentication": "google-auth",
    "email": "email-auth",
    "email authentication": "email-auth",
    "background jobs": "celery",
    "jobs": "celery",
    "containers": "docker",
}


def normalize(name: str) -> str:
    value = " ".join(name.lower().replace("_", "-").split())
    return ALIASES.get(value, value.replace(" ", "-"))


def get(name: str) -> Component:
    key = normalize(name)
    if key not in COMPONENTS:
        raise ValueError(
            f"Unknown component: {name}. Run 'ai-init components' to list supported components."
        )
    return COMPONENTS[key]


def list_components() -> Iterable[Component]:
    return (COMPONENTS[key] for key in sorted(COMPONENTS))


def resolve(names: Iterable[str], installed: Iterable[str] = ()) -> List[Component]:
    resolved: List[Component] = []
    seen = set(installed)

    def include(name: str) -> None:
        component = get(name)
        if component.name in seen:
            return
        for requirement in component.requires:
            include(requirement)
        seen.add(component.name)
        resolved.append(component)

    for name in names:
        include(name)
    return resolved
