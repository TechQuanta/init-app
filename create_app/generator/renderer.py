from pathlib import Path

# 🟢 Custom Logger Import
from create_app.ui.logger import logger

# 📁 Define the absolute path to the templates directory
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

def render_template(template_name, output_path, context, raw=False, raw_print=False):
    """
    ✨ Core Engine: Renders templates by mapping context keys to placeholders.
    Supports file output, raw string return, or direct terminal printing.
    """
    
    template_file = TEMPLATE_DIR / template_name
    logger.info(f"🎨 Rendering template: {template_name}")

    # 🔍 Ensure the template exists before processing
    if not template_file.exists():
        logger.error(f"❌ Template file not found: {template_file}")
        raise FileNotFoundError(f"❌ Template missing: {template_name}")

    try:
        content = template_file.read_text(encoding="utf-8")
        original_size = len(content)

        # 🔄 Replace placeholders: {{key}} -> value
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in content:
                logger.debug(f"  -> Replacing {placeholder} with '{value}'")
                content = content.replace(placeholder, str(value))

        # 🛡️ Quality Check: Detect unreplaced placeholders
        if "{{" in content and "}}" in content:
            import re
            missing = re.findall(r"\{\{(.*?)\}\}", content)
            logger.warning(f"⚠️  Unreplaced placeholders found in {template_name}: {set(missing)}")

        # 🛠️ Mode 1: Return content as a string
        if raw:
            logger.info(f"✅ Returned raw content for {template_name}")
            return content

        # 📺 Mode 2: Print content to terminal
        if raw_print:
            logger.info(f"📺 Preview mode triggered for {template_name}")
            print(f"\n--- Preview: {template_name} ---")
            print(content)
            print("-" * (14 + len(template_name)) + "\n")
            return

        # 💾 Mode 3: Write to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"💾 Writing rendered file to: {output_path.absolute()}")
        output_path.write_text(content, encoding="utf-8")
        
        return f"✅ Created: {output_path.name}"

    except Exception as e:
        logger.error(f"💥 Failed to render template {template_name}", exc_info=True)
        raise e