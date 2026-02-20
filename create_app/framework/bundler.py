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
    SILENT LOGIC BUNDLER (v3.5.0)
    Resolves architecture, INJECTS constants, and POPULATES dependencies.
    Optimized for RAG AI, MLOps, and Enterprise Django/FastAPI.
    FEATURE: Universal entry.py.tpl force-filling for app.py.
    """
    def __init__(self, root: Path, ctx: dict):
        self.root = root  
        self.ctx = ctx
        
        # 1. Normalize Context keys to match AppEngine / Controller
        self.fw_name = ctx.get('fw_name', ctx.get('framework', 'fastapi')).lower()
        self.strategy = ctx.get('build_strategy', 'standard').lower()
        self.is_drf = ctx.get('is_drf', False)
        self.db_engine = str(ctx.get('database', 'sqlite')).lower()
        
        logger.info(f"🏗️ Bundler Init: FW={self.fw_name}, Strategy={self.strategy}, DRF={self.is_drf}")
        
        # ⚡ 2. Inject Raw Constants from constants.py into Jinja2 Context
        constants_dict = {k: v for k, v in const.__dict__.items() if not k.startswith("__")}
        self.ctx.update(constants_dict)
        
        # ⚡ 3. Intelligent Context & Dependencies
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
            if self.strategy in ["production", "auto_config"]:
                deps += ["slowapi", "fastapi-pagination", "python-jose[cryptography]", "passlib[bcrypt]", "gunicorn"]
        
        elif self.fw_name == "flask":
            deps += ["flask", "flask-cors", "flask-marshmallow", "gunicorn"]
            if self.strategy in ["production", "auto_config"]:
                deps += ["flask-jwt-extended", "flask-migrate", "flask-smorest"]

        elif self.fw_name == "django":
            deps += ["django", "django-environ", "django-cors-headers"]
            if self.is_drf:
                deps += [
                    "djangorestframework", 
                    "django-filter", 
                    "drf-spectacular", 
                    "djangorestframework-simplejwt"
                ]
            if self.strategy in ["production", "auto_config"]:
                deps += ["django-redis", "django-health-check", "whitenoise", "gunicorn", "psycopg2-binary"]

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

        # 4. SPECIALIZED DOMAIN ENGINES
        if self.fw_name == "rag_ai":
            deps += ["openai", "langchain", "langchain-community", "chromadb", "qdrant-client", "tiktoken", "pypdf"]
        elif self.fw_name == "data_pipeline":
            deps += ["pandas", "numpy", "sqlalchemy", "pyarrow", "dask", "prefect"]
        elif self.fw_name == "mlops_core":
            deps += ["scikit-learn", "mlflow", "joblib", "bentoml", "optuna"]
        elif self.fw_name == "hp_cli":
            deps += ["click", "typer", "rich", "shellingham"]

        # Clean, Sort, and Format
        unique_deps = sorted(list(set(deps)))
        self.ctx["dependencies"] = "\n".join(unique_deps)
        
        logger.info(f"📦 Successfully resolved {len(unique_deps)} libraries for {self.fw_name}.")

    def _inject_dynamic_defaults(self):
        """Retrieves framework-specific values from constants.py."""
        default_port = const.DEFAULT_PORTS.get(self.fw_name, "8000")
        
        # Ensure server_type is set for the template engine
        servers = const.FRAMEWORK_SERVER_MAPPING.get(self.fw_name, ["uvicorn"])
        default_server = servers[0] if servers else "uvicorn"

        self.ctx.update({
            "version": const.__version__,
            "app_name": self.ctx.get("app_name", const.APP_NAME),
            "port": self.ctx.get("port", default_port),
            "host": self.ctx.get("host", "0.0.0.0"),
            "debug": "True" if self.strategy == "standard" else "False",
            "server_type": self.ctx.get("server_type", default_server),
            "server": self.ctx.get("server_type", default_server), # Alias for template
            "fw_name": self.fw_name
        })

    def _get_architectural_blueprint(self):
        """
        Resolves the folder/package structure based on FW and Mode.
        """
        blueprint = {}
        
        # 1. Django Branch
        if "django" in self.fw_name:
            mode = "drf" if self.is_drf else "standard"
            blueprint = DJANGO_PATCH_RULES.get(mode, DJANGO_PATCH_RULES["standard"])
            
        # 2. Others Branch (RAG, MLOps, etc.)
        elif self.fw_name in OTHERS_RULES:
            blueprint = OTHERS_RULES.get(self.fw_name)
            
        # 3. Standard Web Frameworks
        else:
            lookup_map = {"fastapi": "FastAPI", "flask": "Flask", "bottle": "Bottle", "tornado": "Tornado"}
            lookup = lookup_map.get(self.fw_name, self.fw_name.capitalize())
            
            source_dict = PROD_WEB_RULES if self.strategy in ["production", "auto_config"] else STANDARD_BLUEPRINT
            blueprint = source_dict.get(lookup, source_dict.get("FastAPI"))

        for key in ["folders", "packages"]:
            if key in blueprint:
                blueprint[key] = [item for item in blueprint[key] if item.lower() != "ui"]

        return blueprint

    def execute(self):
        """Finalizes build data and forces entry.py.tpl for app.py."""
        logger.info("🚀 Bundler Execution Started.")
        blueprint = self._get_architectural_blueprint()
        manifest = get_global_manifest(self.ctx)
        
        # ⚡ 1. Resolve UI Mapping for Universal Template logic
        # Tells the template whether to look in 'ui', 'templates', etc.
        ui_map = {"fastapi": "ui", "flask": "templates", "bottle": "templates", "sanic": "ui"}
        self.ctx["ui_folder"] = ui_map.get(self.fw_name, "templates")

        # ⚡ 2. DYNAMIC APP.PY POPULATION
        # We loop through and force the source to entry.py.tpl
        entry_found = False
        for rule in manifest:
            if any(x in rule["target"] for x in ["_main.py", "run.py", "entry.py", "app.py"]):
                rule["target"] = "app.py"
                if "django" not in self.fw_name:
                    rule["source"] = "common/entry.py.tpl"
                    entry_found = True

        # ⚡ 3. Safety Guard: If no entry point was defined, force inject it
        if not entry_found and "django" not in self.fw_name:
            manifest.append({
                "source": "common/entry.py.tpl",
                "target": "app.py"
            })

        return {"blueprint": blueprint, "manifest": manifest, "ctx": self.ctx}