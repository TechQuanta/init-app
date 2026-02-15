import os
import json
import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({
            "message": "Welcome to {{project_name}} 🚀",
            "framework": "Tornado",
            "status": "Running"
        }))


class HealthHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({"status": "OK"}))


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/health", HealthHandler),
    ])


if __name__ == "__main__":
    app = make_app()

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")

    app.listen(port, address=host)

    print(f"🚀 Tornado server running on http://{host}:{port}")

    tornado.ioloop.IOLoop.current().start()
