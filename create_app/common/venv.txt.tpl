{% if venv_enabled in [True, 'yes', 'y', 'true'] %}
Environment manager: {{ env_manager|default('venv') }}

Activate the project environment:

source .venv/bin/activate   (Linux / macOS)
.venv\Scripts\activate      (Windows)
{% else %}
Environment setup skipped.

Install requirements in your active environment before running the app:

python -m pip install -r requirements.txt
{% endif %}
