from fastapi import FastAPI
import os

app = FastAPI()


@app.get("/")
async def home():
    return {
        "message": "Welcome to {{project_name}} 🚀",
        "framework": "FastAPI",
        "status": "Running"
    }


@app.get("/health")
async def health_check():
    return {"status": "OK"}
