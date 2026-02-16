"""
🚀 {{project_name}} – Bottle Application
Generated using py-create
"""

from bottle import Bottle, static_file, template
from dotenv import load_dotenv
import os

from config.settings import settings
from routes import register_routes

# ✅ Load env
load_dotenv()


def create_app():
    app = Bottle()

    # ✅ Static File Handler 😈🔥
    @app.route('/static/<filepath:path>')
    def serve_static(filepath):
        return static_file(filepath, root='./static')

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
