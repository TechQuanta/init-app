import os
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from create_app.logger import logger

class Generator:
    """
    PHYSICAL EXECUTION ENGINE (v3.5.6)
    FIXED: Explicit HTML template rendering and unified path resolution for common assets.
    FEATURE: Automatic Django-specific path mapping for Templates and Static files.
    """
    def __init__(self, root: Path, ctx: dict):
        self.root = root
        self.ctx = ctx
        self.fw = str(ctx.get("framework", "fastapi")).lower()
        self.is_drf = ctx.get("is_drf", False)
        self.app_name = ctx.get("app_name", "core_app")
        
        # 1. Resolve Base Directory (points to 'create_app' folder)
        self.base_dir = Path(__file__).parent.parent.resolve()
        
        # 2. Setup Jinja Search Paths
        search_paths = [
            str(self.base_dir),
            str(self.base_dir / "common" / "template"),
            str(self.base_dir / "framework" / "templates")
        ]
        
        valid_paths = [p for p in search_paths if Path(p).exists()]
        
        logger.info(f"⚙️ Generator Engine Linked: Root={self.root}")
        
        self.env = Environment(
            loader=FileSystemLoader(valid_paths),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def _render_and_write(self, tpl_path: str, output_rel_path: str):
        """Renders a Jinja2 template and writes it to the target path."""
        tpl_path = tpl_path.replace("\\", "/")
        target_path = self.root / output_rel_path
        
        # Guard for Django UI assets: Skip generic "ui/" if framework is Django
        # (Django uses app-specific folders handled in _handle_static_assets)
        if self.fw == "django" and (output_rel_path.startswith("ui/") or output_rel_path == "ui"):
            return

        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            template = self.env.get_template(tpl_path)
            rendered_content = template.render(**self.ctx)
            
            if not rendered_content.strip():
                logger.warning(f"⚠️ Template {tpl_path} rendered as empty. Check context variables.")

            target_path.write_text(rendered_content, encoding="utf-8")
            logger.debug(f"📝 Rendered: {output_rel_path}")
            
        except Exception as e:
            logger.error(f"❌ Template Error [{tpl_path}]: {str(e)}")
            if not target_path.exists(): 
                target_path.touch()
                logger.warning(f"⚠️ Created empty fallback file: {output_rel_path}")

    def run(self, blueprint: dict, manifest_rules: list):
        """Executes the physical build sequence."""
        if not blueprint: 
            blueprint = {}
            
        self.root.mkdir(parents=True, exist_ok=True)
        logger.info("🛠️ Building project filesystem...")

        # 1. Folder & Package Scaffolding
        folders_to_create = (blueprint.get("folders", []) + blueprint.get("packages", []))
        for folder in folders_to_create:
            if not folder or folder == "none" or (folder.lower() == "ui" and self.fw == "django"):
                continue
            
            target = self.root / folder
            target.mkdir(parents=True, exist_ok=True)
            
            if folder in blueprint.get("packages", []):
                (target / "__init__.py").touch()

        # 2. File Rendering from Manifest
        if manifest_rules:
            logger.info(f"📄 Rendering {len(manifest_rules)} files from manifest...")
            for rule in manifest_rules:
                self._render_and_write(rule["source"], rule["target"])

        # 3. HTML and Static Asset Handling (Framework Specific)
        self._handle_static_assets()
        
        logger.info("🏁 Physical generation phase complete.")
        return True

    def _handle_static_assets(self):
        """Handles HTML templates and Static assets (CSS/JS)."""
        
        # --- PART A: HTML TEMPLATES ---
        src_tpl_dir = self.base_dir / "common" / "template"
        if src_tpl_dir.exists():
            for tpl_file in src_tpl_dir.glob("*.tpl"):
                clean_name = tpl_file.name.replace(".tpl", "")
                
                if self.fw == "django":
                    # Django Path: project/app_name/templates/index.html
                    target_path = f"{self.app_name}/templates/{clean_name}"
                else:
                    # Generic Path: project/ui/index.html
                    target_path = f"ui/{clean_name}"
                
                tpl_lookup = f"common/template/{tpl_file.name}"
                self._render_and_write(tpl_lookup, target_path)

        # --- PART B: STATIC ASSETS (CSS/JS) ---
        src_static_dir = self.base_dir / "common" / "static"
        if not src_static_dir.exists():
            return

        # Determine target static root
        if self.fw == "django":
            target_static_root = self.root / self.app_name / "static"
        else:
            ui_folder = self.ctx.get("ui_folder", "ui")
            target_static_root = self.root / ui_folder / "static"

        for root_path, _, files in os.walk(src_static_dir):
            for file in files:
                source_file = Path(root_path) / file
                rel_path = source_file.relative_to(src_static_dir)
                
                if file.endswith(".tpl"):
                    clean_name = str(rel_path).replace(".tpl", "")
                    
                    # Fix: Map 'scripts/' folder to 'js/' target folder
                    if clean_name.startswith("scripts"):
                        clean_name = clean_name.replace("scripts", "js", 1)
                    
                    tpl_lookup = f"common/static/{rel_path}".replace("\\", "/")
                    
                    # Calculate target path relative to project root
                    final_abs_path = target_static_root / clean_name
                    rel_to_root = str(final_abs_path.relative_to(self.root))
                    
                    self._render_and_write(tpl_lookup, rel_to_root)
                else:
                    # Copy non-template assets (images, etc)
                    dest_file = target_static_root / rel_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, dest_file)

    def _sync_files(self, src: Path, dest: Path, tpl_lookup_prefix: str):
        """Deprecated in favor of explicit manifest and static asset handling."""
        pass