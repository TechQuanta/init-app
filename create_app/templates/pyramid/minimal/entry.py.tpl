import json
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

def home(request):
    # ✅ We encode the string to utf-8 bytes to prevent the Charset TypeError
    body_content = json.dumps({
        "message": "Welcome to {{project_name}} 🚀",
        "framework": "Pyramid",
        "status": "Running"
    })
    
    return Response(
        body=body_content.encode('utf-8'), 
        content_type="application/json",
        charset='UTF-8'
    )


def health_check(request):
    body_content = json.dumps({"status": "OK"})
    
    return Response(
        body=body_content.encode('utf-8'),
        content_type="application/json",
        charset='UTF-8'
    )


if __name__ == "__main__":
    # Setup the Pyramid Configurator
    with Configurator() as config:
        config.add_route("home", "/")
        config.add_route("health", "/health")

        config.add_view(home, route_name="home")
        config.add_view(health_check, route_name="health")

        app = config.make_wsgi_app()

    # Define Server Settings
    host = "127.0.0.1"
    port = 8000

    # Start the WSGI Server
    print(f"🚀 Pyramid server running on http://{host}:{port}")
    
    server = make_server(host, port, app)
    server.serve_forever()