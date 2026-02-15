import falcon
import json


class HomeResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = "application/json"
        resp.text = json.dumps({
            "message": "Welcome to {{project_name}} 🚀",
            "framework": "Falcon",
            "status": "Running"
        })


class HealthResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = "application/json"
        resp.text = json.dumps({"status": "OK"})


app = falcon.App()

app.add_route("/", HomeResource())
app.add_route("/health", HealthResource())
