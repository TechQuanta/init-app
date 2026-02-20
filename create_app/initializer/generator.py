import os
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
# 🟢 Centralized Logger Import
from create_app.logger import logger

class Generator:
    """
    PHYSICAL EXECUTION ENGINE (v3.5.0)
    Optimized for dynamic Package initialization and Snippet Injection.
    FIX: Corrected Template Lookup for Universal Entrypoint rendering.
    """
    def __init__(self, root: Path, ctx: dict):
        self.root = root
        self.ctx = ctx
        self.fw = str(ctx.get("framework", "fastapi")).lower()
        self.is_drf = ctx.get("is_drf", False)
        self.app_name = ctx.get("app_name", "core_app")
        
        # ⚡ RESOLVE TEMPLATE BASE: Point to the 'templates' directory
        # This assumes your structure is: create_app/templates/common/entry.py.tpl
        self.template_base = Path(__file__).parent.parent.resolve() / "templates"
        
        # Fallback if 'templates' folder doesn't exist (looks in 'create_app/common')
        if not self.template_base.exists():
            self.template_base = Path(__file__).parent.parent.resolve()
        
        logger.info(f"⚙️ Generator Engine Linked: Root={self.root}")
        logger.debug(f"📂 Template Base: {self.template_base}")
        
        # Initialize Jinja2 Environment with the base folder
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_base)),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def _render_and_write(self, tpl_path: str, output_rel_path: str):
        """Renders a Jinja2 template and writes it to the target path."""
        target_path = self.root / output_rel_path
        
        # UI Folder Guard
        if output_rel_path.startswith("ui/") or output_rel_path == "ui":
            logger.debug(f"🛡️ Skipped unauthorized UI asset: {output_rel_path}")
            return

        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            # ⚡ FIX: Use the full relative path from the manifest (e.g., 'common/entry.py.tpl')
            # instead of just the basename. This ensures the correct file is pulled.
            template = self.env.get_template(tpl_path)
            rendered_content = template.render(**self.ctx)
            
            if not rendered_content.strip():
                logger.warning(f"⚠️ Template rendered empty content for: {tpl_path}")

            target_path.write_text(rendered_content, encoding="utf-8")
            logger.debug(f"📝 Rendered: {output_rel_path}")
            
        except Exception as e:
            logger.error(f"❌ Template Error [{tpl_path}]: {str(e)}")
            # Fallback: create empty file ONLY if it's essential for structure
            if not target_path.exists(): 
                target_path.touch()
                logger.warning(f"⚠️ Created empty fallback file: {output_rel_path}")

    def run(self, blueprint: dict, manifest_rules: list):
        """Executes the physical build sequence."""
        if not blueprint: 
            logger.warning("⚠️ No blueprint provided to Generator.")
            blueprint = {}
            
        self.root.mkdir(parents=True, exist_ok=True)
        logger.info("🛠️ Building project filesystem...")

        # 1. Folder & Package Scaffolding
        folders_to_create = (blueprint.get("folders", []) + blueprint.get("packages", []))
        init_strategy = self.ctx.get("init_strategy", {})

        for folder in folders_to_create:
            if not folder or folder == "none" or folder.lower() == "ui":
                continue
            
            target = self.root / folder
            target.mkdir(parents=True, exist_ok=True)
            
            should_init = folder in blueprint.get("packages", []) or init_strategy.get(folder, False)
            
            if should_init:
                init_file = target / "__init__.py"
                if not init_file.exists():
                    init_file.touch()
                    logger.debug(f"🐍 Initialized package: {folder}")

        # 2. File Rendering from Manifest
        if manifest_rules:
            logger.info(f"📄 Rendering {len(manifest_rules)} files from manifest...")
            for rule in manifest_rules:
                # Passes the source path (e.g., 'common/entry.py.tpl') to the renderer
                self._render_and_write(rule["source"], rule["target"])

        # 3. Static Asset Handling
        self._handle_static_assets()
        
        logger.info("🏁 Physical generation phase complete.")
        return True

    def _handle_static_assets(self):
        """Copies or renders static assets if the framework requires them."""
        if self.fw != "django" or self.is_drf: 
            return 
            
        # Standardize search for static inside the template base
        src_static = self.template_base / "common" / "static"
        if not src_static.exists(): 
            return

        target_base = self.root / self.app_name / "static"
        logger.info(f"🖼️ Syncing static assets to {self.app_name}/static...")

        for root_path, _, files in os.walk(src_static):
            for file in files:
                source_file = Path(root_path) / file
                rel_path = source_file.relative_to(src_static)
                
                if file.endswith(".tpl"):
                    clean_name = str(rel_path).replace(".tpl", "")
                    # Ensure path is relative to template base for Jinja2
                    tpl_lookup_path = f"common/static/{rel_path}"
                    rel_to_root = str((target_base / clean_name).relative_to(self.root))
                    self._render_and_write(tpl_lookup_path, rel_to_root)
                else:
                    target_file = target_base / rel_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, target_file)