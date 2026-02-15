import tornado.ioloop
import tornado.web

from config.settings import settings
from routes import register_routes


def make_app():
    return tornado.web.Application(
        register_routes(),
        debug=settings.debug,
        template_path="templates",
        static_path="static",
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(settings.port, address=settings.host)

    print(f"🚀 Server running → http://{settings.host}:{settings.port}")

    tornado.ioloop.IOLoop.current().start()
