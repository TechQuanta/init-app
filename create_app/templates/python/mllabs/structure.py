import sys
from pathlib import Path
from create_app.generator.renderer import render_template

TEMPLATE_DIR = Path(__file__).parent

def load_dependencies():
    """Returns a modern ML & Big Data stack."""
    deps = [
        "numpy",
        "pandas",
        "scikit-learn",
        "matplotlib",
        "tensorflow",      # Deep Learning 🧠
        "pyhive[hive]",    # Big Data / SQL 🐝
        "thrift",
        "thrift-sasl",
        "mlflow",          # Experiment Tracking
        "python-dotenv",
        "notebook"         # Jupyter Lab/Notebook
    ]
    return "\n".join(deps)

def generate(project_root: Path, context: dict):
    """
    Modern ML & Data Engineering Lab Generator 🧪🤖
    Optimized for Deep Learning (TensorFlow) and Big Data (PyHive).
    """
    project_name = context["project_name"]
    project_root.mkdir(parents=True, exist_ok=True)

    # 1. ✅ Industry Standard Folder Structure
    folders = [
        "data/raw",         # Raw SQL dumps / CSVs
        "data/processed",   # Scaled/Encoded data for TF
        "notebooks",        # Research & EDA
        "src/data",         # PyHive ingestion scripts
        "src/models",       # TensorFlow model architectures
        "models/checkpoints", # Saved .h5 or SavedModel formats
        "config",           # Hyperparameters & DB configs
    ]
    
    for folder in folders:
        (project_root / folder).mkdir(parents=True, exist_ok=True)
        (project_root / folder / ".gitkeep").touch()

    # 2. ✅ Create PyHive Data Ingestion Script
    (project_root / "src" / "data" / "fetch_data.py").write_text("""
from pyhive import hive
import pandas as pd

def get_data(query):
    # Example Hive connection
    # Note: Requires sasl and thrift system libs
    conn = hive.Connection(host="localhost", port=10000, username="ashmeet")
    return pd.read_sql(query, conn)

if __name__ == "__main__":
    print("🐝 PyHive client initialized...")
""")

    # 3. ✅ Create TensorFlow Training Script
    (project_root / "src" / "models" / "train.py").write_text("""
import tensorflow as tf
from tensorflow.keras import layers
import mlflow.tensorflow

def build_model():
    model = tf.keras.Sequential([
        layers.Dense(64, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy')
    return model

if __name__ == "__main__":
    mlflow.tensorflow.autolog() # 🔥 Auto-track TF experiments
    model = build_model()
    print("🧠 TensorFlow Model built and MLflow autologging enabled.")
""")

    # 4. ✅ Modern pyproject.toml
    (project_root / "pyproject.toml").write_text(f"""
[project]
name = "{project_name}"
version = "0.1.0"
description = "Deep Learning & Big Data Lab"
requires-python = ">=3.9"
dependencies = [
    "tensorflow>=2.10.0",
    "pyhive[hive]",
    "pandas",
    "mlflow"
]
""".strip() + "\n")

    # 5. ✅ Common Files
    context.update({
        "dependencies": load_dependencies(),
        "entrypoint": "src/models/train.py"
    })

    render_template("common/README.md.tpl", project_root / "README.md", context)
    render_template("common/requirements.txt.tpl", project_root / "requirements.txt", context)
    
    # 🛡️ Guard for Pytest: Ensure these exist in /templates/common/
    render_template("common/gitignore.tpl", project_root / ".gitignore", context)

    return project_root