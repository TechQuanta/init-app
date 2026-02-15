from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def render_template(template_path, output_path, context, raw=False, raw_print=False):

    template_file = TEMPLATE_DIR / template_path

    if not template_file.exists():
        raise FileNotFoundError(f"Template not found → {template_path}")

    content = template_file.read_text()

    for key, value in context.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))

    if raw:
        return content

    if raw_print:
        print(content)
        return

    output_path.write_text(content)
