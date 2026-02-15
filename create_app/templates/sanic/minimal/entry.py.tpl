from sanic import Sanic
from sanic.response import json
import os

app = Sanic("{{project_name}}")


@app.get("/")
async def home(request):
    return json({
        "message": "Welcome to {{project_name}} 🚀",
        "framework": "Sanic",
        "status": "Running"
    })


@app.get("/health")
async def health_check(request):
    return json({"status": "OK"})


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        debug=os.getenv("DEBUG", "True") == "True"
    )
