import os
import shutil
from pathlib import Path
import create_app.constants as const 

# 🟢 Using your existing Generator/Bundler logic
from create_app.initializer.generator import Generator
from create_app.framework.bundler import Bundler
from create_app.logger import logger

def generate_auto(project_root: Path, context: dict):
    """
    AUTO-CONFIGURE ENGINE (v2.1)
    - Replaces Nucleus with Generator logic.
    - Forces 'Production' level infrastructure.
    - Injects EVERY infrastructure suite automatically (Full-Stack Auto-Build).
    """
    fw_slug = context.get('fw_name', 'fastapi').lower()
    
    # 1. Initialize the Bundler to resolve dependencies and rules
    # We force 'production' strategy here because auto_config is a "Full-Stack Max" build
    context['build strategy'] = 'production'
    
    logger.info(f"🤖 Auto-Config Triggered: {fw_slug.upper()} Full-Stack sequence started.")
    
    bundler = Bundler(project_root, context)
    build_data = bundler.execute()
    
    # 2. Initialize the Generator worker
    # Using your Generator class which handles rendered writes and init_strategy
    worker = Generator(project_root, build_data['ctx'])
    blueprint = build_data['blueprint']

    # 3. Create Physical Architecture (Folders & Packages)
    # worker.run handles the folder creation and __init__.py logic
    worker.run(blueprint=blueprint, manifest_rules=[])

    # 4. AUTO-INJECT ALL SUITES
    # We compile a massive manifest of every single asset defined in constants.py
    auto_manifest = []
    
    all_suites = {
        "docker": const.DOCKER_SUITE,
        "jenkins": const.JENKINS_SUITE,
        "kubernetes": const.K8S_FILES,
        "github": const.GITHUB_SUITE,
        "community": const.COMMUNITY_CORE,
        "db": getattr(const, 'DB_STRUCTURE', []),
        "pkg": getattr(const, 'PACKAGE_FILES', []),
        "global": getattr(const, 'GLOBAL_DEFAULTS', [])
    }

    for suite_name, files in all_suites.items():
        if not files:
            continue
            
        for filename in files:
            # Cleanup naming for target output
            clean_name = filename.replace('.tpl', '')
            
            # Smart Target Path Logic
            if suite_name == "github":
                target_path = f".github/workflows/{os.path.basename(clean_name)}"
            elif suite_name in ["docker", "jenkins", "kubernetes"] and "/" not in clean_name:
                # Group infra files into subdirectories for a cleaner root
                target_path = f"{suite_name}/{clean_name}"
            else:
                # Standard files or those with pre-defined paths
                target_path = clean_name
                
            auto_manifest.append({
                "source": filename if filename.endswith('.tpl') else f"{filename}.tpl",
                "target": target_path
            })

    # 5. Framework Entry Point Logic
    if fw_slug != "django":
        # Ensure a main entry point exists for non-Django projects
        auto_manifest.append({"source": "app.py.tpl", "target": "app.py"})
        # Sync dependencies list for requirements.txt
        auto_manifest.append({"source": "requirements.txt.tpl", "target": "requirements.txt"})

    # 6. Execute Physical Generation
    # We leverage the worker's internal rendering engine to process the auto-manifest
    logger.info(f"📦 Auto-Injecting {len(auto_manifest)} infrastructure files...")
    for rule in auto_manifest:
        worker._render_and_write(rule["source"], rule["target"])

    return project_root