"""
🚀 {{project_name}} – Bottle Application
Generated using py-create
"""

from bottle import Bottle
import os
from dotenv import load_dotenv

from config.settings import settings
from routes import register_routes

# ✅ Load env
load_dotenv()


def create_app():
    app = Bottle()

    # ✅ Register routes
    register_routes(app)

    return app


app = create_app()


if __name__ == "__main__":

    print(f"\n🚀 Starting {{project_name}}...")
    print(f"🌐 Running on http://{settings.host}:{settings.port}\n")

    app.run(
        host=settings.host,
        port=settings.port,
        debug=settings.debug,
        reloader=settings.debug
    )
