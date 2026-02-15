from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from config.settings import settings

def main():
    # Use settings for configuration
    with Configurator() as config:
        
        # 1. Include your route definitions (from routes.py)
        config.include(".routes") # Added dot for relative import if inside a package
        
        # 2. Scan for @view_config decorators in your views folder
        # Note: 'views' must be a package (must have an __init__.py)
        config.scan("views")

        app = config.make_wsgi_app()

    # 3. Use host/port from your settings object
    server = make_server(settings.host, settings.port, app)

    print(f"🚀 Pyramid running on http://{settings.host}:{settings.port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server... 🛑")


if __name__ == "__main__":
    main()