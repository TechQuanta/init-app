from flask import Flask, jsonify
import os

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify(
        message="Welcome to {{project_name}} 🚀",
        framework="Flask",
        status="Running"
    )


@app.route("/health")
def health_check():
    return jsonify(status="OK")


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("DEBUG", "True") == "True"
    )
