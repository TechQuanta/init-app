import os
from pathlib import Path
import create_app.constants as const 

# 🟢 Centralized Logger Import
from create_app.logger import logger

from create_app.rules.global_rules import get_global_manifest
from create_app.rules.standard_rules import STANDARD_BLUEPRINT
from create_app.rules.production_rules import PROD_WEB_RULES
from create_app.rules.django_rules import DJANGO_PATCH_RULES
from create_app.rules.others_rules import OTHERS_RULES

class Bundler:
    """
    SILENT LOGIC BUNDLER (v3.0.0)
    Resolves architecture, INJECTS constants, and POPULATES dependencies.
    Optimized for RAG AI, MLOps, and Enterprise Django/FastAPI.
    """
    def __init__(self, root: Path, ctx: dict):
        self.root = root  
        self.ctx = ctx
        
        # Mapping incoming context to internal logic
        self.fw_name = ctx.get('framework', 'fastapi').lower()
        self.strategy = ctx.get('build_strategy', 'standard').lower()
        self.project_type = ctx.get('project_type', 'base').lower()
        self.is_drf = ctx.get('is_drf', False)
        self.db_engine = ctx.get('database', 'sqlite').lower()
        
        logger.info(f"🏗️ Bundler Init: FW={self.fw_name}, Strategy={self.strategy}, DRF={self.is_drf}")
        
        # ⚡ 1. Inject Raw Constants
        constants_dict = {k: v for k, v in const.__dict__.items() if not k.startswith("__")}
        self.ctx.update(constants_dict)
        
        # ⚡ 2. Intelligent Context & Dependencies
        self._inject_dynamic_defaults()
        self._resolve_dependencies()

    def _resolve_dependencies(self):
        """
        Comprehensive Dependency Resolver.
        Detects FW, DB, AI, and DevOps requirements.
        """
        logger.debug(f"🔍 Deep Scanning dependencies for {self.fw_name}...")
        
        # 1. CORE BASE
        deps = ["python-dotenv", "jinja2", "pyyaml", "loguru"]

        # 2. FRAMEWORK & EXTENSIONS
        if self.fw_name == "fastapi":
            deps += ["fastapi", "uvicorn[standard]", "pydantic[email]", "pydantic-settings", "httpx"]
            if self.strategy == "production":
                deps += ["slowapi", "fastapi-pagination", "python-jose[cryptography]", "passlib[bcrypt]"]
        
        elif self.fw_name == "flask":
            deps += ["flask", "flask-cors", "flask-marshmallow", "python-dotenv", "gunicorn"]
            if self.strategy == "production":
                deps += ["flask-jwt-extended", "flask-migrate", "flask-smorest"]

        elif self.fw_name == "django":
            deps += ["django", "django-environ", "django-cors-headers"]
            if self.is_drf:
                deps += [
                    "djangorestframework", 
                    "django-filter", 
                    "drf-spectacular", # Swagger UI for DRF
                    "djangorestframework-simplejwt"
                ]
            if self.strategy == "production":
                deps += ["django-redis", "django-health-check", "whitenoise"]

        elif self.fw_name in ["bottle", "falcon", "pyramid"]:
            deps += [self.fw_name, "waitress"]

        # 3. DATABASE ADAPTERS
        if "postgres" in self.db_engine:
            deps += ["psycopg2-binary", "sqlalchemy", "alembic"]
        elif "mysql" in self.db_engine:
            deps += ["mysqlclient", "sqlalchemy", "alembic"]
        elif "mongodb" in self.db_engine:
            deps += ["pymongo", "motor", "beanie" if self.fw_name == "fastapi" else "mongoengine"]
        elif "sqlite" in self.db_engine:
            deps += ["sqlalchemy", "alembic"]

        # 4. SPECIALIZED DOMAIN ENGINES (RAG, Data, MLOps)
        if self.project_type == "rag_ai":
            deps += [
                "openai", "langchain", "langchain-community", 
                "chromadb", "qdrant-client", "tiktoken", 
                "sentence-transformers", "unstructured", "pypdf"
            ]
        elif self.project_type == "data_pipeline":
            deps += ["pandas", "numpy", "sqlalchemy", "pyarrow", "dask", "prefect"]
        elif self.project_type == "mlops_core":
            deps += ["scikit-learn", "mlflow", "joblib", "bentoml", "optuna"]
        elif self.project_type == "hp_cli":
            deps += ["click", "typer", "rich", "shellingham"]

        # 5. INFRASTRUCTURE & TOOLS
        if self.ctx.get("infra_suites"):
            if "docker" in str(self.ctx["infra_suites"]):
                deps += ["docker"] # for python-docker integration if needed

        # Clean, Sort, and Format
        unique_deps = sorted(list(set(deps)))
        self.ctx["dependencies"] = "\n".join(unique_deps)
        
        logger.info(f"📦 Successfully resolved {len(unique_deps)} libraries for {self.fw_name}.")

    def _inject_dynamic_defaults(self):
        """Retrieves framework-specific values from constants.py."""
        default_port = const.DEFAULT_PORTS.get(self.fw_name, "8000")
        servers = const.FRAMEWORK_SERVER_MAPPING.get(self.fw_name, ["na"])
        default_server = servers[0] if servers else "uvicorn"

        self.ctx.update({
            "version": const.__version__,
            "app_name": self.ctx.get("app_name", const.APP_NAME),
            "port": self.ctx.get("port", default_port),
            "host": self.ctx.get("host", "0.0.0.0"),
            "debug": "True" if self.strategy == "standard" else "False",
            "server_type": default_server,
            "fw_name": self.fw_name
        })

    def _get_architectural_blueprint(self):
        blueprint = {}
        if self.fw_name == "django":
            mode = "drf" if self.is_drf else "standard"
            blueprint = DJANGO_PATCH_RULES.get(mode, DJANGO_PATCH_RULES["standard"])
        elif self.fw_name == "others":
            blueprint = OTHERS_RULES.get(self.project_type, OTHERS_RULES.get("base"))
        else:
            lookup_map = {"fastapi": "FastAPI", "flask": "Flask", "bottle": "Bottle"}
            lookup = lookup_map.get(self.fw_name, self.fw_name.capitalize())
            source_dict = PROD_WEB_RULES if "production" in self.strategy else STANDARD_BLUEPRINT
            blueprint = source_dict.get(lookup) or source_dict.get("FastAPI") or {}

        # UI Guard
        if self.fw_name != "django" or self.is_drf:
            if "folders" in blueprint:
                blueprint["folders"] = [f for f in blueprint["folders"] if f.lower() != "ui"]
            if "packages" in blueprint:
                blueprint["packages"] = [p for p in blueprint["packages"] if p.lower() != "ui"]

        return blueprint

    def execute(self):
        logger.info("🚀 Bundler Execution Started.")
        blueprint = self._get_architectural_blueprint()
        manifest = get_global_manifest(self.ctx)
        
        for rule in manifest:
            if any(x in rule["target"] for x in ["_main.py", "run.py", "entry.py"]):
                rule["target"] = "app.py"

        return {"blueprint": blueprint, "manifest": manifest, "ctx": self.ctx}