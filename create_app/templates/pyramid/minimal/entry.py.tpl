from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
import json


def home(request):
    return Response(
        json.dumps({
            "message": "Welcome to {{project_name}} 🚀",
            "framework": "Pyramid",
            "status": "Running"
        }),
        content_type="application/json",
    )


def health_check(request):
    return Response(
        json.dumps({"status": "OK"}),
        content_type="application/json",
    )


if __name__ == "__main__":

    with Configurator() as config:
        config.add_route("home", "/")
        config.add_route("health", "/health")

        config.add_view(home, route_name="home")
        config.add_view(health_check, route_name="health")

        app = config.make_wsgi_app()

    server = make_server("127.0.0.1", 8000, app)

    print("🚀 Pyramid server running on http://127.0.0.1:8000")

    server.serve_forever()
