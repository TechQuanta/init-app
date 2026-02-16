from flask import Flask
from config.settings import settings
from routes import register_routes
from extensions.init_extensions import init_extensions


def create_app():
    """
    Flask Application Factory 😈🔥
    """

    app = Flask(__name__)

    app.config["DEBUG"] = settings.debug

    init_extensions(app)
    register_routes(app)

    return app


if __name__ == "__main__":
    app = create_app()

    app.run(
        host=settings.host,
        port=settings.port,
        debug=settings.debug,
    )
