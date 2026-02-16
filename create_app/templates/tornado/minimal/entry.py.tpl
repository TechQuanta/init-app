import os
import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")   # ✅ UI Rendering 🔥


class HealthHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"status": "OK"})


def make_app():
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/health", HealthHandler),
        ],
        template_path="templates",   # ✅ CRITICAL 🔥
        static_path="static",        # ✅ CRITICAL 🔥
        debug=True,
    )


if __name__ == "__main__":
    app = make_app()

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")

    app.listen(port, address=host)

    print(f"🚀 Tornado server running → http://{host}:{port}")

    tornado.ioloop.IOLoop.current().start()
