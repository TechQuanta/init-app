"""Provider-aware dbt setup shared by the CLI, generator, and MCP contract.

The catalog intentionally contains the adapters most commonly used in production.
``custom`` keeps the integration open to every dbt-compatible adapter published
on PyPI without requiring an init-app release for each new provider.
"""

from __future__ import annotations

import re
from pathlib import Path


DBT_ADAPTERS: dict[str, dict[str, str]] = {
    "snowflake": {"package": "dbt-snowflake", "type": "snowflake"},
    "databricks": {"package": "dbt-databricks", "type": "databricks"},
    "bigquery": {"package": "dbt-bigquery", "type": "bigquery"},
    "redshift": {"package": "dbt-redshift", "type": "redshift"},
    "postgres": {"package": "dbt-postgres", "type": "postgres"},
    "duckdb": {"package": "dbt-duckdb", "type": "duckdb"},
    "spark": {"package": "dbt-spark", "type": "spark"},
    "athena": {"package": "dbt-athena-community", "type": "athena"},
    "trino": {"package": "dbt-trino", "type": "trino"},
    "clickhouse": {"package": "dbt-clickhouse", "type": "clickhouse"},
    "dremio": {"package": "dbt-dremio", "type": "dremio"},
    "exasol": {"package": "dbt-exasol", "type": "exasol"},
    "oracle": {"package": "dbt-oracle", "type": "oracle"},
    "teradata": {"package": "dbt-teradata", "type": "teradata"},
    "sqlserver": {"package": "dbt-sqlserver", "type": "sqlserver"},
    "mysql": {"package": "dbt-mysql", "type": "mysql"},
    "synapse": {"package": "dbt-synapse", "type": "synapse"},
    "fabric": {"package": "dbt-fabric", "type": "fabric"},
    "motherduck": {"package": "dbt-motherduck", "type": "duckdb"},
}
DBT_ADAPTER_CHOICES = tuple((*DBT_ADAPTERS, "custom"))
_PACKAGE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_PROFILE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")


def project_identifier(name: str) -> str:
    """Return a dbt-compatible identifier from an init-app project name."""
    value = re.sub(r"[^A-Za-z0-9_]", "_", name).strip("_")
    if not value or value[0].isdigit():
        value = f"dbt_{value or 'project'}"
    return value.lower()


def resolve_adapter(adapter: str, package: str | None = None, adapter_type: str | None = None) -> dict[str, str]:
    """Validate an adapter request and return install/configuration metadata."""
    key = str(adapter or "duckdb").lower().strip()
    if key in DBT_ADAPTERS:
        if package or adapter_type:
            raise ValueError("--dbt-adapter-package and --dbt-adapter-type are only valid with --dbt-adapter custom")
        return {"id": key, **DBT_ADAPTERS[key]}
    if key != "custom":
        raise ValueError(f"Unsupported dbt adapter: {adapter}. Choose one of: {', '.join(DBT_ADAPTER_CHOICES)}")
    package = str(package or "").strip()
    adapter_type = str(adapter_type or "").strip().lower()
    if not _PACKAGE.fullmatch(package):
        raise ValueError("custom dbt adapter requires a safe PyPI package name via --dbt-adapter-package")
    if not _PROFILE.fullmatch(adapter_type):
        raise ValueError("custom dbt adapter requires a safe dbt adapter type via --dbt-adapter-type")
    return {"id": "custom", "package": package, "type": adapter_type}


def validate_profile_name(value: str) -> str:
    value = str(value).strip()
    if not _PROFILE.fullmatch(value):
        raise ValueError("dbt profile and target names must use letters, numbers, underscores, or hyphens and start with a letter or underscore")
    return value


def profile_yaml(profile: str, target: str, adapter: dict[str, str]) -> str:
    """Create a credential-free profile that can be completed through env vars."""
    adapter_type = adapter["type"]
    common = "    threads: {{ env_var('DBT_THREADS', '4') | int }}\n"
    outputs: dict[str, str] = {
        "snowflake": "    type: snowflake\n    account: \"{{ env_var('DBT_SNOWFLAKE_ACCOUNT') }}\"\n    user: \"{{ env_var('DBT_SNOWFLAKE_USER') }}\"\n    password: \"{{ env_var('DBT_SNOWFLAKE_PASSWORD') }}\"\n    role: \"{{ env_var('DBT_SNOWFLAKE_ROLE', 'TRANSFORMER') }}\"\n    database: \"{{ env_var('DBT_SNOWFLAKE_DATABASE') }}\"\n    warehouse: \"{{ env_var('DBT_SNOWFLAKE_WAREHOUSE') }}\"\n    schema: \"{{ env_var('DBT_SCHEMA', 'analytics_dev') }}\"\n",
        "databricks": "    type: databricks\n    host: \"{{ env_var('DBT_DATABRICKS_HOST') }}\"\n    http_path: \"{{ env_var('DBT_DATABRICKS_HTTP_PATH') }}\"\n    token: \"{{ env_var('DBT_DATABRICKS_TOKEN') }}\"\n    catalog: \"{{ env_var('DBT_DATABRICKS_CATALOG', 'main') }}\"\n    schema: \"{{ env_var('DBT_SCHEMA', 'analytics_dev') }}\"\n",
        "bigquery": "    type: bigquery\n    method: service-account-json\n    project: \"{{ env_var('DBT_BIGQUERY_PROJECT') }}\"\n    keyfile_json: \"{{ env_var('DBT_BIGQUERY_KEYFILE_JSON') }}\"\n    dataset: \"{{ env_var('DBT_SCHEMA', 'analytics_dev') }}\"\n    location: \"{{ env_var('DBT_BIGQUERY_LOCATION', 'US') }}\"\n",
        "duckdb": "    type: duckdb\n    path: \"{{ env_var('DBT_DUCKDB_PATH', 'warehouse.duckdb') }}\"\n    schema: \"{{ env_var('DBT_SCHEMA', 'analytics_dev') }}\"\n",
        "postgres": "    type: postgres\n    host: \"{{ env_var('DBT_HOST', 'localhost') }}\"\n    port: \"{{ env_var('DBT_PORT', '5432') | int }}\"\n    user: \"{{ env_var('DBT_USER') }}\"\n    password: \"{{ env_var('DBT_PASSWORD') }}\"\n    dbname: \"{{ env_var('DBT_DATABASE') }}\"\n    schema: \"{{ env_var('DBT_SCHEMA', 'analytics_dev') }}\"\n",
        "redshift": "    type: redshift\n    host: \"{{ env_var('DBT_HOST') }}\"\n    port: \"{{ env_var('DBT_PORT', '5439') | int }}\"\n    user: \"{{ env_var('DBT_USER') }}\"\n    password: \"{{ env_var('DBT_PASSWORD') }}\"\n    dbname: \"{{ env_var('DBT_DATABASE') }}\"\n    schema: \"{{ env_var('DBT_SCHEMA', 'analytics_dev') }}\"\n",
        "trino": "    type: trino\n    host: \"{{ env_var('DBT_HOST') }}\"\n    port: \"{{ env_var('DBT_PORT', '443') | int }}\"\n    user: \"{{ env_var('DBT_USER') }}\"\n    catalog: \"{{ env_var('DBT_CATALOG') }}\"\n    schema: \"{{ env_var('DBT_SCHEMA', 'analytics_dev') }}\"\n",
        "spark": "    type: spark\n    method: thrift\n    host: \"{{ env_var('DBT_HOST') }}\"\n    port: \"{{ env_var('DBT_PORT', '10000') | int }}\"\n    schema: \"{{ env_var('DBT_SCHEMA', 'analytics_dev') }}\"\n",
        "athena": "    type: athena\n    s3_staging_dir: \"{{ env_var('DBT_ATHENA_S3_STAGING_DIR') }}\"\n    region_name: \"{{ env_var('DBT_AWS_REGION', 'us-east-1') }}\"\n    database: \"{{ env_var('DBT_DATABASE') }}\"\n    schema: \"{{ env_var('DBT_SCHEMA', 'analytics_dev') }}\"\n",
        "clickhouse": "    type: clickhouse\n    host: \"{{ env_var('DBT_HOST') }}\"\n    port: \"{{ env_var('DBT_PORT', '8443') | int }}\"\n    user: \"{{ env_var('DBT_USER') }}\"\n    password: \"{{ env_var('DBT_PASSWORD') }}\"\n    schema: \"{{ env_var('DBT_SCHEMA', 'analytics_dev') }}\"\n",
        "mysql": "    type: mysql\n    server: \"{{ env_var('DBT_HOST', 'localhost') }}\"\n    port: \"{{ env_var('DBT_PORT', '3306') | int }}\"\n    username: \"{{ env_var('DBT_USER') }}\"\n    password: \"{{ env_var('DBT_PASSWORD') }}\"\n    schema: \"{{ env_var('DBT_DATABASE') }}\"\n",
    }
    output = outputs.get(adapter_type)
    if output is None:
        output = f"    type: {adapter_type}\n    # Add this adapter's required fields using env_var(), never literal credentials.\n    schema: \"{{{{ env_var('DBT_SCHEMA', 'analytics_dev') }}}}\"\n"
    return f"{profile}:\n  target: {target}\n  outputs:\n  {target}:\n{output}{common}"


def profile_env_example(adapter: dict[str, str]) -> str:
    """Provide a non-secret starting point for local credential configuration."""
    prefix = adapter["type"].upper().replace("-", "_")
    return (
        "# Copy values into your shell/secret manager. Do not commit real credentials.\n"
        "DBT_THREADS=4\nDBT_SCHEMA=analytics_dev\n"
        f"# DBT_{prefix}_... connection values are defined in ~/.dbt/profiles.yml\n"
    )


def ensure_profile(profiles_dir: Path, profile: str, target: str, adapter: dict[str, str]) -> tuple[Path, bool]:
    """Create a dbt ``profiles.yml`` or append one missing profile safely.

    dbt only reads a file named ``profiles.yml`` from the selected profiles
    directory. This deliberately does not treat files such as ``user.yml`` as
    dbt configuration.
    """
    dbt_dir = Path(profiles_dir)
    profile_path = dbt_dir / "profiles.yml"
    dbt_dir.mkdir(parents=True, exist_ok=True)
    existing = profile_path.read_text(encoding="utf-8") if profile_path.exists() else ""
    if re.search(rf"(?m)^{re.escape(profile)}:\s*$", existing):
        return profile_path, False
    entry = profile_yaml(profile, target, adapter)
    separator = "\n\n" if existing.strip() else ""
    profile_path.write_text(f"{existing.rstrip()}{separator}{entry}", encoding="utf-8")
    return profile_path, True


def ensure_project_profile(root: Path, profile: str, target: str, adapter: dict[str, str]) -> tuple[Path, bool]:
    """Create or preserve the portable project-local ``.dbt/profiles.yml``."""
    return ensure_profile(Path(root) / ".dbt", profile, target, adapter)


def ensure_user_profile(home: Path, profile: str, target: str, adapter: dict[str, str]) -> tuple[Path, bool]:
    """Create ~/.dbt/profiles.yml or append a missing profile without overwriting it."""
    return ensure_profile(Path(home) / ".dbt", profile, target, adapter)
