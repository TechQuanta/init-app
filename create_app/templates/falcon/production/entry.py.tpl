import falcon
from wsgiref import simple_server

from config.settings import settings
from routes import register_routes


def create_app():
    app = falcon.App()

    register_routes(app)

    return app


app = create_app()


if __name__ == "__main__":
    print(f"🚀 Server running on http://{settings.host}:{settings.port}")

    with simple_server.make_server(settings.host, settings.port, app) as httpd:
        httpd.serve_forever()
