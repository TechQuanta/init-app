import time
from pathlib import Path
from create_app.ui.logger import logger
from create_app.generator.generator import generate_project
from create_app.generator.database import resolve_database_dependencies
from create_app.generator.renderer import render_template
from create_app.ui.loader import Spinner

class AppGeneratorEngine:
    def __init__(self, project_name, framework, structure, location=".", venv=False, db=None, extra_ctx=None):
        self.project_name = project_name
        self.framework = framework
        self.structure = structure
        self.location = Path(location)
        self.venv = venv
        self.db = db
        self.extra_ctx = extra_ctx or {}

    def run(self):
        """🚀 Executes the generation process."""
        logger.info(f"Engine starting build: {self.framework} ({self.structure})")
        
        db_deps = resolve_database_dependencies(self.db) if self.db else ""

        try:
            with Spinner(f"Initializing {self.framework} Project") as loader:
                project_root = generate_project(
                    self.project_name, 
                    str(self.location), 
                    self.framework, 
                    self.structure,
                    db_deps, 
                    create_venv=self.venv,
                    extra_context=self.extra_ctx
                )
                time.sleep(0.5)
            
            self._show_success(project_root)
            return True
        except Exception as e:
            logger.exception("Engine encountered a fatal error")
            print(f"\n❌ Generation Failed: {e}")
            return False

    def _show_success(self, project_root):
        """🏁 Renders the final dashboard."""
        entrypoint = "manage.py runserver" if self.framework == "Django" else "app.py"
        
        venv_section = ""
        if self.venv:
            venv_section = render_template("common/venv.txt.tpl", None, {}, raw=True)

        context = {
            "project_name": self.project_name,
            "entrypoint": entrypoint,
            "venv_section": venv_section
        }

        dashboard = render_template("common/work.txt.tpl", None, context, raw=True)
        
        print("\n" + "-" * 44)
        print(dashboard)
        print("-" * 44 + "\n")