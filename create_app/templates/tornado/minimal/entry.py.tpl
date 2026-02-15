import os
import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # ✅ Jinja will now replace these with the actual strings
        self.render(
            "index.html",
            project_name="{{ project_name }}",
            structure="{{ structure }}",
            framework="{{ framework }}"
        )


class HealthHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"status": "OK"})


def make_app():
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/health", HealthHandler),
        ],
        template_path="templates",
        static_path="static",
        debug=True,
    )


if __name__ == "__main__":
    app = make_app()

    # These come from your context['port'] and context['host']
    port = int(os.getenv("PORT", {{ port }}))
    host = os.getenv("HOST", "{{ host }}")

    app.listen(port, address=host)

    print(f"🚀 Tornado server running → http://{host}:{port}")

    tornado.ioloop.IOLoop.current().start()