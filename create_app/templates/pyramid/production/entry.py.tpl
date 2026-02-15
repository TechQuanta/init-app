from wsgiref.simple_server import make_server
from pyramid.config import Configurator

from config.settings import settings


def main():
    with Configurator() as config:

        config.include("routes")
        config.scan("views")

        app = config.make_wsgi_app()

    server = make_server(settings.host, settings.port, app)

    print(f"🚀 Pyramid running on http://{settings.host}:{settings.port}")

    server.serve_forever()


if __name__ == "__main__":
    main()
