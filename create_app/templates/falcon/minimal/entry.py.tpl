import os
import json
import falcon
from wsgiref.simple_server import make_server

class HomeResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = "application/json"
        resp.text = json.dumps({
            "message": "Welcome to {{project_name}} 🚀",
            "framework": "Falcon",
            "structure": "{{structure}}",
            "status": "Running"
        })


class HealthResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = "application/json"
        resp.text = json.dumps({"status": "OK"})


# ✅ Initialize Falcon App
app = falcon.App()

# ✅ Routes
app.add_route("/", HomeResource())
app.add_route("/health", HealthResource())


# ✅ Dev Server Entry Point
if __name__ == "__main__":
    # Get configuration from environment or defaults
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))

    print(f"\n🚀 Starting {{project_name}} (Falcon)...")
    print(f"🌐 Running on http://{host}:{port}\n")

    try:
        with make_server(host, port, app) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user.")