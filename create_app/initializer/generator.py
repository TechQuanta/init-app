import os
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
# 🟢 Centralized Logger Import
from create_app.logger import logger

class Generator:
    """
    PHYSICAL EXECUTION ENGINE (v3.4.0)
    Optimized for dynamic Package initialization and Snippet Injection.
    """
    def __init__(self, root: Path, ctx: dict):
        self.root = root
        self.ctx = ctx
        self.fw = str(ctx.get("framework", "fastapi")).lower()
        self.is_drf = ctx.get("is_drf", False)
        self.app_name = ctx.get("app_name", "core_app")
        # Resolve the common templates directory
        self.common_dir = Path(__file__).parent.parent.resolve() / "common"
        
        logger.info(f"⚙️ Generator Engine Linked: Root={self.root}")
        
        # Prepare Jinja2 search paths (Recursive directory scanning)
        search_paths = [str(self.common_dir)]
        if self.common_dir.exists():
            for p in self.common_dir.rglob('*'):
                if p.is_dir(): 
                    search_paths.append(str(p))
        
        logger.debug(f"📂 Jinja2 search paths: {len(search_paths)} directories identified.")
        self.env = Environment(loader=FileSystemLoader(search_paths))

    def _render_and_write(self, tpl_path: str, output_rel_path: str):
        """Renders a Jinja2 template and writes it to the target path."""
        target_path = self.root / output_rel_path
        
        # UI Folder Guard (Safety check to prevent ghost UI assets)
        if output_rel_path.startswith("ui/") or output_rel_path == "ui":
            logger.debug(f"🛡️ Skipped unauthorized UI asset: {output_rel_path}")
            return

        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            # Handle template lookup by filename only (since paths are in FileSystemLoader)
            tpl_file = os.path.basename(tpl_path)
            template = self.env.get_template(tpl_file)
            rendered_content = template.render(**self.ctx)
            
            target_path.write_text(rendered_content, encoding="utf-8")
            logger.debug(f"📝 Rendered: {output_rel_path}")
            
        except Exception as e:
            logger.error(f"❌ Template Error [{tpl_path}]: {str(e)}")
            # Fallback: create empty file to avoid breaking the build structure
            if not target_path.exists(): 
                target_path.touch()
                logger.warning(f"⚠️ Created empty fallback file: {output_rel_path}")

    def run(self, blueprint: dict, manifest_rules: list):
        """
        Executes the physical build sequence.
        Modified to align with 'init_strategy' for __init__.py creation.
        """
        if not blueprint: 
            logger.warning("⚠️ No blueprint provided to Generator.")
            blueprint = {}
            
        self.root.mkdir(parents=True, exist_ok=True)
        logger.info("🛠️ Building project filesystem...")

        # 1. Folder & Package Scaffolding
        # Folders are plain dirs; Packages are Python packages (with __init__.py)
        folders_to_create = (blueprint.get("folders", []) + blueprint.get("packages", []))
        
        # Pull the init_strategy map from the context (the DNA of the project structure)
        init_strategy = self.ctx.get("init_strategy", {})

        for folder in folders_to_create:
            if not folder or folder == "none" or folder.lower() == "ui":
                continue
            
            target = self.root / folder
            target.mkdir(parents=True, exist_ok=True)
            
            # Logic: __init__.py is created if it's in the 'packages' list 
            # OR if the init_strategy (from interactive/CLI mode) marks it True.
            should_init = folder in blueprint.get("packages", []) or init_strategy.get(folder, False)
            
            if should_init:
                init_file = target / "__init__.py"
                if not init_file.exists():
                    init_file.touch()
                    logger.debug(f"🐍 Initialized package: {folder}")
            else:
                logger.debug(f"📁 Folder created: {folder}")

        # 2. File Rendering from Manifest
        if manifest_rules:
            logger.info(f"📄 Rendering {len(manifest_rules)} files from manifest...")
            for rule in manifest_rules:
                self._render_and_write(rule["source"], rule["target"])

        # 3. Static Asset Handling (Specific to non-DRF Django projects)
        self._handle_static_assets()
        
        logger.info("🏁 Physical generation phase complete.")
        return True

    def _handle_static_assets(self):
        """Copies or renders static assets if the framework requires them."""
        # Only Standard Django needs special static handling from the 'common' directory
        if self.fw != "django" or self.is_drf: 
            return 
            
        src_static = self.common_dir / "static"
        if not src_static.exists(): 
            logger.warning("⚠️ Source static folder missing in common/ directory.")
            return

        target_base = self.root / self.app_name / "static"
        logger.info(f"🖼️ Syncing static assets to {self.app_name}/static...")

        for root_path, _, files in os.walk(src_static):
            for file in files:
                source_file = Path(root_path) / file
                rel_path = source_file.relative_to(src_static)
                
                if file.endswith(".tpl"):
                    clean_name = str(rel_path).replace(".tpl", "")
                    # Calculate path relative to project root for the renderer
                    rel_to_root = str((target_base / clean_name).relative_to(self.root))
                    self._render_and_write(file, rel_to_root)
                else:
                    target_file = target_base / rel_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, target_file)
                    logger.debug(f"📂 Copied static asset: {rel_path}")