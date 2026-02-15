from sanic import Sanic
from sanic.response import json

from config.settings import settings
from routes import register_routes


def create_app():
    app = Sanic("{{project_name}}")

    register_routes(app)

    return app


app = create_app()


if __name__ == "__main__":
    print(f"🚀 Server running on http://{settings.host}:{settings.port}")

    app.run(
        host=settings.host,
        port=settings.port,
        debug=settings.debug,
    )
