import uvicorn
from fastapi import FastAPI

from config.settings import settings
from routes import register_routes


def create_app() -> FastAPI:
    app = FastAPI(
        title="{{project_name}} API",
        debug=settings.debug,
    )

    register_routes(app)

    return app


app = create_app()


if __name__ == "__main__":
    print(f"🚀 Server running on http://{settings.host}:{settings.port}")

    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
