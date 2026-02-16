"""
🚀 {{project_name}} – Flask Application
Generated using py-create
"""

from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)


@app.route("/")
def home():


    return render_template(
        "index.html",

        # ✅ Variables your template expects 😈🔥
        project_name="{{project_name}}",
        framework="Flask",
        structure="{{structure}}",
        app_name="{{app_name}}",
    )


@app.route("/health")
def health_check():
    return jsonify(status="OK")


if __name__ == "__main__":

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "True") == "True"

    print(f"\n🚀 Starting {{project_name}}...")
    print(f"🌐 Running on http://{host}:{port}\n")

    app.run(
        host=host,
        port=port,
        debug=debug,
    )
