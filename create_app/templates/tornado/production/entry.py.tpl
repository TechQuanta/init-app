import tornado.ioloop
import tornado.web

from routes import register_routes
from config.settings import settings


def make_app():
    return tornado.web.Application(
        register_routes(),
        debug=settings.debug,
        template_path="templates",   # ✅ IMPORTANT 🔥
        static_path="static",        # ✅ IMPORTANT 🔥
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(settings.port, address=settings.host)

    print(f"🚀 Tornado running → http://{settings.host}:{settings.port}")

    tornado.ioloop.IOLoop.current().start()
