import argparse
import json
import os
import sys
from pathlib import Path

import readchar

# Allow direct execution from a source checkout as well as installed console use.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from create_app.engine.ui.user_interface import InitUI
from create_app.engine.prompts import BuildPrompts
import create_app.constants as const
from create_app.initializer.controller import Controller 
from create_app.path_config import PathConfig
from create_app.gitignore import available_presets, normalize_patterns
from create_app.rag_context import write_project_context
from create_app.project_spec import load_spec, validate_app_name, validate_project_name, validate_relative_paths

class AppEngine(InitUI):
    """Coordinates the two public channels: flag-driven CLI and interactive UI."""

    def __init__(self):
        super().__init__(const.APP_NAME, const.__version__)
        self.prompter = BuildPrompts(self, const)
        self.infra_keys = ["docker", "jenkins", "k8s", ".github", "db"]
        self.domain_folders = [f.lower() for f in const.ALL_CUSTOM_FOLDERS if f.lower() not in self.infra_keys]
        # The manifest is the hand-off contract between the UI/CLI and Controller.
        self.manifest = { 
            "infra_suites": [], 
            "infra_files": {}, 
            "init_strategy": {},
            "is_drf": False 
        } 

    def _setup_parser(self):
        """Defines the CLI command structure with high-performance overrides."""
        parser = argparse.ArgumentParser(description=f"{const.APP_NAME} - Advanced Project Engine")
        
        # Identity & Version
        parser.add_argument("name", nargs="?", help="Project name")
        parser.add_argument("--spec", metavar="FILE", help="JSON project specification; command flags override its values.")
        parser.add_argument("--dry-run", action="store_true", help="Validate and print the resolved project configuration without writing files.")
        parser.add_argument("--force", action="store_true", help="Allow generation into an existing project directory.")
        parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {const.__version__}")
        parser.add_argument("--output-dir", help="Explicit parent directory where the project folder is created. Defaults to the current directory.")
        parser.add_argument("--here", action="store_true", help="Create the project in the current working directory.")
        parser.add_argument("--path-behavior", choices=["documents", "current", "custom"], help="One-off path behavior for this project.")
        parser.add_argument("--set-default-path-behavior", choices=["documents", "current", "custom"], help="Persist the default project path behavior.")
        parser.add_argument("--set-default-output-dir", help="Persist a custom default output directory.")
        parser.add_argument("--show-path-config", action="store_true", help="Show saved path defaults and exit.")
        parser.add_argument("--reset-path-config", action="store_true", help="Reset saved path defaults and exit.")
        parser.add_argument(
            "--refresh-rag-context", metavar="PROJECT_DIR",
            help="Refresh the local RAG inventory for an existing generated project and exit.",
        )
        
        # Core Configuration
        parser.add_argument("-f", "--framework", choices=const.FRAMEWORKS + const.OTHERS_PROJECT_TYPES, help="Target framework")
        parser.add_argument("-s", "--server", help="Specific server (e.g., uvicorn, gunicorn, hypercorn)")
        parser.add_argument("-t", "--type", choices=["standard", "production", "custom", "auto_config"], dest="strategy", help="Build strategy")
        parser.add_argument("--drf", action="store_true", help="Enable Django Rest Framework (Django only)")
        
        # Architecture Overrides
        parser.add_argument("--folders", nargs="+", help="Manually specify folders (Custom mode only)")
        parser.add_argument("--packages", nargs="+", help="Specify which folders get __init__.py")
        parser.add_argument(
            "--gitignore-preset", choices=available_presets(),
            help=".gitignore preset (default: framework-aware)",
        )
        parser.add_argument(
            "--gitignore", "--ignore", dest="gitignore", nargs="+", metavar="PATTERN",
            help="Custom .gitignore file/folder patterns; accepts [a, b/] or separate values",
        )
        parser.add_argument(
            "--no-rag-context", action="store_true",
            help="Do not create the local RAG context bundle (enabled by default)",
        )
        
        # Environment & Database
        parser.add_argument("--db", help="Database engine (sqlite, postgres, mysql, mongodb)")
        parser.add_argument("--dbt-service", help="Select dbt service/adapter (e.g., databricks, snowflake, bigquery)")
        parser.add_argument("--venv", choices=["y", "n"], help="Enable virtual environment (y/n)")
        parser.add_argument("--app-name", help="Application package name (default: core_app)")
        parser.add_argument("--apps", nargs="+", help="Django application package names")
        
        # Infrastructure Modules
        parser.add_argument("--docker", nargs="+", help="Select Docker files")
        parser.add_argument("--github", nargs="+", help="Select GitHub actions")
        parser.add_argument("--k8s", nargs="+", help="Select Kubernetes manifests")
        parser.add_argument("--jenkins", nargs="+", help="Select Jenkins pipeline files")
        parser.add_argument("--community", nargs="+", help="Select community files")
        parser.add_argument("--package-files", nargs="+", help="Select package metadata files")
        
        return parser

    def start(self):
        """Route the request to the CLI channel or the interactive channel."""
        parser = self._setup_parser()
        args = parser.parse_args()

        if args.refresh_rag_context:
            self._refresh_rag_context(args.refresh_rag_context)
            return

        self._handle_path_config_flags(args)

        if (args.name and args.framework) or args.spec:
            self._handle_cli_mode(args)
        else:
            self._handle_interactive_mode()

    @staticmethod
    def _refresh_rag_context(project_dir):
        """Refresh a local context snapshot after a project changes."""
        root = Path(project_dir).expanduser().resolve()
        if not root.is_dir():
            raise SystemExit(f"Project directory does not exist: {root}")
        metadata_path = root / ".init-app.json"
        metadata = {}
        if metadata_path.exists():
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                pass
        write_project_context(root, metadata)
        print(f"Refreshed local RAG context: {root / '.init-app' / 'rag-context.json'}")

    def _handle_path_config_flags(self, args):
        """Handle persistent default path behavior flags before project creation."""
        if args.reset_path_config:
            path = PathConfig.reset()
            print(f"Reset path config: {path}")
            sys.exit(0)

        if args.show_path_config:
            print(PathConfig.describe())
            sys.exit(0)

        if args.set_default_path_behavior or args.set_default_output_dir:
            config = PathConfig.load()

            if args.set_default_path_behavior:
                config["path_behavior"] = args.set_default_path_behavior

            if args.set_default_output_dir:
                config["output_dir"] = str(Path(args.set_default_output_dir).expanduser().resolve())
                if not args.set_default_path_behavior:
                    config["path_behavior"] = "custom"

            path = PathConfig.save(config)
            print(f"Saved path config: {path}")
            print(PathConfig.describe())

            if not args.name:
                sys.exit(0)

    def _handle_cli_mode(self, args):
        """Processes logic based on CLI flags with full Django-aware support."""
        try:
            spec = load_spec(args.spec) if args.spec else {}
            p_name = validate_project_name(args.name or spec.get("name"))
            fw_slug = str(args.framework or spec.get("framework", "")).lower()
            if fw_slug not in const.FRAMEWORKS + const.OTHERS_PROJECT_TYPES:
                raise ValueError(f"framework must be one of: {', '.join(const.FRAMEWORKS + const.OTHERS_PROJECT_TYPES)}")
            strategy = str(args.strategy or spec.get("strategy", "standard")).lower()
            if strategy not in {"standard", "production", "custom", "auto_config"}:
                raise ValueError("strategy must be standard, production, custom, or auto_config")
        except ValueError as exc:
            raise SystemExit(f"Invalid project input: {exc}")

        def setting(name, default=None):
            value = getattr(args, name, None)
            return value if value is not None else spec.get(name, default)

        try:
            app_name = validate_app_name(setting("app_name", "core_app"))
            raw_apps = setting("apps")
            if raw_apps is None:
                app_names = [app_name]
            else:
                if not isinstance(raw_apps, list) or not raw_apps:
                    raise ValueError("apps must be a non-empty list")
                app_names = [validate_app_name(value) for value in raw_apps]
                app_name = app_names[0]
            folders = validate_relative_paths(setting("folders"), "folders")
            packages = validate_relative_paths(setting("packages"), "packages")
        except ValueError as exc:
            raise SystemExit(f"Invalid project input: {exc}")
        if fw_slug != "django" and (setting("apps") is not None or len(app_names) > 1):
            raise SystemExit("Invalid project input: --apps is only supported for Django projects")
        if strategy == "custom" and packages and not set(packages).issubset(folders):
            raise SystemExit("Invalid project input: every package must also appear in folders")
        
        # Convert optional flag groups into a single infrastructure manifest.
        infra_map = {
            "docker": setting("docker"),
            "github": setting("github"),
            "kubernetes": setting("k8s"),
            "jenkins": setting("jenkins"),
            "community": setting("community"),
            "pkg": setting("package_files"),
        }
        for key, files in infra_map.items():
            if files:
                if not isinstance(files, list) or not all(isinstance(item, str) and item.strip() for item in files):
                    raise SystemExit(f"Invalid project input: {key} must be a non-empty list of file names")
                self.manifest["infra_suites"].append(key)
                self.manifest["infra_files"][key] = files

        # Custom mode respects explicit folder lists; other modes use defaults.
        if strategy == "custom" and folders:
            selected_folders = folders
        else:
            selected_folders = self.prompter.get_smart_folders(fw_slug, strategy, self.domain_folders)

        # The init strategy decides which generated folders become Python packages.
        if strategy == "custom" and (packages or setting("packages") is not None):
            init_map = {folder: (folder in packages) for folder in selected_folders}
        else:
            init_map = {folder: True for folder in selected_folders}

        try:
            gitignore_patterns = normalize_patterns(setting("gitignore"))
        except ValueError as exc:
            raise SystemExit(f"Invalid --gitignore value: {exc}")

        self.manifest.update({
            "project name": p_name,
            "core blueprint": f"{fw_slug} ({setting('server', 'default')})",
            "fw_name": fw_slug, 
            "is_drf": args.drf or bool(spec.get("drf", False)),
            "build strategy": strategy,
            "environment": "venv" if setting("venv", "y") == "y" else "no venv",
            "apps": ", ".join(app_names),
            "app_names": app_names,
            "database": setting("db", "sqlite"),
            "dbt_service": setting("dbt_service"),
            "venv_enabled": setting("venv", "y") == "y",
            "app_name": app_name,
            "init_strategy": init_map,
            "output_dir": setting("output_dir"),
            "create_in_current_dir": args.here or bool(spec.get("here", False)),
            "path_behavior": setting("path_behavior"),
            "gitignore_preset": setting("gitignore_preset", "framework"),
            "gitignore_patterns": gitignore_patterns,
            "rag_context_enabled": not args.no_rag_context and spec.get("rag_context", True),
        })

        mission = Controller(self.manifest, list(selected_folders))
        if args.dry_run:
            preview = {
                "name": p_name,
                "framework": fw_slug,
                "strategy": strategy,
                "app_name": self.manifest["app_name"],
                "apps": self.manifest["app_names"],
                "database": self.manifest["database"],
                "project_path": str(mission.root),
                "folders": list(selected_folders),
                "packages": [folder for folder, enabled in init_map.items() if enabled],
                "infrastructure": self.manifest["infra_files"],
                "venv": self.manifest["venv_enabled"],
                "rag_context": self.manifest["rag_context_enabled"],
            }
            print(json.dumps(preview, indent=2, sort_keys=True))
            return
        if mission.root.exists() and any(mission.root.iterdir()) and not args.force:
            raise SystemExit(f"Refusing to modify existing project directory: {mission.root}. Use --force to continue.")
        mission.run_mission()

    def _handle_interactive_mode(self):
        """Interactive flow utilizing the High-Performance UI layer."""
        try:
            selected_folders = set()
            fw_display, _ = self.menu("core blueprint", const.FRAMEWORKS, sub_mapping=const.FRAMEWORK_SERVER_MAPPING, flow=["blueprint"])
            fw_slug = fw_display.split(" (")[0].lower()
            
            # The menu label carries the DRF choice, so normalize it into the manifest.
            self.manifest["is_drf"] = "rest framework" in fw_display.lower()

            if fw_slug == "others":
                project_type_display, _ = self.menu("engine type", const.OTHERS_PROJECT_TYPES, flow=["others"])
                fw_slug = project_type_display.lower()

                # If dbt_pipeline selected, prompt for dbt service immediately
                if fw_slug == "dbt_pipeline":
                    services = const.DBT_SERVICE_ALIASES
                    svc_display, _ = self.menu("Select your dbt data platform", [const.DBT_SERVICE_DISPLAY.get(s, s) for s in services], flow=["dbt_pipeline", "service"])
                    # Map selected display back to alias
                    selected_alias = None
                    for alias in services:
                        if const.DBT_SERVICE_DISPLAY.get(alias, alias) == svc_display:
                            selected_alias = alias
                            break
                    self.manifest["dbt_service"] = selected_alias

            mode_raw, _ = self.menu("build strategy", const.PROJECT_MODES, flow=[fw_slug, "mode"])
            mode = mode_raw.lower()
            
            # The following choices become the generation context passed to Controller.
            db_raw, _ = self.menu("data nexus", const.DB_ENGINES, flow=[fw_slug, mode, "database"])
            db = db_raw.lower()
            
            if mode == "auto_config":
                env_display, _ = self.menu("environment", ["venv (recommended)", "no venv"], flow=[fw_slug, mode, "env"])
                p_name = self.prompter.get_project_name()
                apps_list = [] 
                selected_folders = self.prompter.get_smart_folders(fw_slug, "standard", self.domain_folders)
                self.manifest["init_strategy"] = {f: True for f in selected_folders}
            else:
                selected_folders = self._orchestrate_infra(fw_slug, mode)
                env_display, _ = self.menu("environment", ["venv (recommended)", "no venv"], flow=[fw_slug, mode, "env"])
                p_name, apps_list = self.prompter.collect_identity(fw_slug, mode)

            self._collect_gitignore_options(fw_slug)

            self.manifest.update({
                    "project name": p_name,
                    "core blueprint": fw_display,
                    "fw_name": fw_slug, 
                    "build strategy": mode,
                    "environment": env_display,
                    "apps": ", ".join(apps_list) if apps_list else "none", 
                    "app_names": apps_list or ["core_app"],
                    "app_name": apps_list[0] if apps_list else "core_app",
                    "database": db,
                    "venv_enabled": "no venv" not in env_display.lower(),
                })

            self._run_mission_control(fw_slug, p_name, mode, selected_folders)

        except (KeyboardInterrupt, EOFError):
            self.exit_gracefully()
        except Exception as e:
            self.cfg.write(f"\n  {self.cfg.C['accent']}✖ critical engine error: {self.cfg.C['white']}{str(e).lower()}")
            sys.exit(1)

    def _collect_gitignore_options(self, framework):
        """Collect a preset plus explicit file, folder, and custom ignore rules."""
        preset, _ = self.menu(
            "gitignore preset", available_presets(framework),
            flow=[framework, "gitignore"],
        )
        file_options = [
            ".env", ".env.local", ".env.production", "*.local", "*.secret",
            "*.pem", "*.key", "coverage.xml", ".DS_Store",
        ]
        folder_options = [
            "uploads/", "data/", "tmp/", "coverage/", ".pytest_cache/",
            ".mypy_cache/", ".ruff_cache/", ".vectorstore/", "chroma_db/",
            "qdrant_storage/", "models/",
        ]
        selected_files = self.checklist(
            "gitignore files", "files to ignore", file_options, flow=[framework, "gitignore", "files"]
        )
        selected_folders = self.checklist(
            "gitignore folders", "folders to ignore", folder_options, flow=[framework, "gitignore", "folders"]
        )
        raw = input(
            "\n  Additional patterns (comma-separated or [file, folder/], optional): "
        ).strip()
        try:
            custom = normalize_patterns(list(selected_files) + list(selected_folders) + ([raw] if raw else []))
        except ValueError as exc:
            self.cfg.write(f"  {self.cfg.C['accent']}✖ invalid ignore pattern: {exc}")
            custom = normalize_patterns(list(selected_files) + list(selected_folders))
        self.manifest["gitignore_preset"] = preset
        self.manifest["gitignore_patterns"] = custom

    def _orchestrate_infra(self, fw, mode):
        """Handles manual infrastructure selection logic."""
        f_list = [fw, mode, "infra"]
        if mode == "custom":
            selected_dirs, init_map = self.architect(self.domain_folders, fw_slug=fw, flow=[fw, "architect"])
            self.manifest["init_strategy"] = init_map
        else:
            selected_dirs = self.prompter.get_smart_folders(fw, mode, self.domain_folders)
            self.manifest["init_strategy"] = {d: True for d in selected_dirs}

        infra_options = [("docker", const.DOCKER_SUITE), ("jenkins", const.JENKINS_SUITE), ("github", const.GITHUB_SUITE)]
        if mode in ["production", "custom"]:
            infra_options.extend([
                ("community", const.COMMUNITY_CORE),
                ("pkg", const.PACKAGE_FILES),
                ("kubernetes", const.K8S_FILES),
            ])

        for key, suite in infra_options:
            res = self.checklist("infra forge", key, suite, flow=f_list)
            if res:
                self.manifest["infra_suites"].append(key)
                self.manifest["infra_files"][key] = list(res)
        return selected_dirs

    def _run_mission_control(self, fw, p_name, mode, folders):
        """Final summary matrix and execution trigger."""
        c = self.cfg.C
        self.header("mission control", "success")
        infra_total = sum(len(f) for f in self.manifest['infra_files'].values())
        db_clean = self.manifest['database'].split(' ')[0]
        
        # High-performance buffered write for the matrix
        matrix = [
            f"  {c['muted']}┌──────────────────────────────────────────┐",
            f"  {c['muted']}│ {c['white']}NAME  : {c['primary']}{p_name[:12].ljust(12)} {c['white']}ENGINE: {c['primary']}{fw[:10].ljust(10)} {c['muted']}│",
            f"  {c['muted']}│ {c['white']}MODE  : {c['primary']}{mode[:12].ljust(12)} {c['white']}DB    : {c['primary']}{db_clean[:10].ljust(10)} {c['muted']}│",
            f"  {c['muted']}│ {c['white']}DIRS  : {c['primary']}{str(len(folders)).ljust(12)} {c['white']}DRF   : {c['primary']}{str(self.manifest['is_drf']).ljust(10)} {c['muted']}│",
            f"  {c['muted']}└──────────────────────────────────────────┘"
        ]
        self.cfg.write("\n".join(matrix))

        sys.stdout.write(f"\n  {c['success']}? {c['white']}Initialize build sequence? (y/n): ")
        sys.stdout.flush()

        if readchar.readkey().lower() == 'y':
            self.cfg.write(f"{c['success']}yes")
            self.finalize(p_name)
            mission = Controller(self.manifest, list(folders))
            mission.run_mission()
        else:
            self.cfg.write(f"{c['accent']}no\n  {c['muted']}build cancelled.")
            sys.exit(0)

def main():
    """Entry point for the console script."""
    try:
        engine = AppEngine()
        engine.start()
    except KeyboardInterrupt:
        print("\n  Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
