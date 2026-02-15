from bottle import route, run, response
import os


@route("/")
def home():
    response.content_type = "application/json"
    return {
        "message": "Welcome to {{project_name}} 🚀",
        "framework": "Bottle",
        "status": "Running"
    }


@route("/health")
def health_check():
    response.content_type = "application/json"
    return {"status": "OK"}


if __name__ == "__main__":
    run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8080)),
        debug=os.getenv("DEBUG", "True") == "True"
    )
