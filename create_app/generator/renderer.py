import re
from pathlib import Path
from create_app.ui.logger import logger

# 📁 Define the absolute path to the templates directory
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

def render_template(template_name, output_path, context, raw=False, raw_print=False):
    """
    ✨ Robust Engine: Renders templates using Regex.
    Handles variations in spacing ({{ key }}) and avoids Regex escape errors 
    in ASCII art or paths using lambda replacements.
    """
    template_file = TEMPLATE_DIR / template_name
    logger.info(f"🎨 Rendering template: {template_name}")

    if not template_file.exists():
        logger.error(f"❌ Template file not found: {template_file}")
        raise FileNotFoundError(f"❌ Template missing: {template_name}")

    try:
        content = template_file.read_text(encoding="utf-8")

        # 🔄 SMART INJECTION
        for key, value in context.items():
            # Matches {{key}}, {{ key }}, etc.
            pattern = r"\{\{\s*" + re.escape(str(key)) + r"\s*\}\}"
            replacement = str(value)
            
            if re.search(pattern, content):
                logger.debug(f"  -> Injecting '{key}' into {template_name}")
                
                # ✅ FIX: Using lambda m: replacement treats the value as literal text.
                # This prevents 'bad escape \S' errors when templates contain backslashes.
                content = re.sub(pattern, lambda m: replacement, content)

        # 🛡️ Quality Check: Detect unreplaced placeholders
        leftover = re.findall(r"\{\{\s*(.*?)\s*\}\}", content)
        if leftover:
            logger.warning(f"⚠️  Unreplaced placeholders in {template_name}: {set(leftover)}")

        # --- Output Modes ---

        # 🛠️ Mode 1: Return raw string (Used for dashboard/terminal messages)
        if raw:
            return content

        # 📺 Mode 2: Print to terminal
        if raw_print:
            print(content)
            return

        # 💾 Mode 3: Write to destination file
        if output_path:
            dest_path = Path(output_path)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_text(content, encoding="utf-8")
            return f"✅ Created: {dest_path.name}"
            
    except Exception as e:
        logger.error(f"💥 Failed to render template {template_name}", exc_info=True)
        raise e