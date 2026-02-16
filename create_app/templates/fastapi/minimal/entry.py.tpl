import os
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="{{project_name}}")


@app.get("/")
async def home():
    return {
        "message": "Welcome to {{project_name}} 🚀",
        "framework": "FastAPI",
        "structure": "{{structure}}",
        "status": "Running"
    }


@app.get("/health")
async def health_check():
    return {"status": "OK"}


# ✅ This is the missing piece that makes it "run"
if __name__ == "__main__":
    # Pull config from .env or use defaults
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    
    print(f"\n🚀 Starting {{project_name}} on FastAPI...")
    
    uvicorn.run(
        "app:app", 
        host=host, 
        port=port, 
        reload=True  # Enables auto-reload for development
    )