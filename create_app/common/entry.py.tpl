"""
🚀 {{project_name}} - {{fw_name | upper}} ENGINE
Powered by: {{app_name}} v{{version}}
"""

import os
import sys
from pathlib import Path

# --- 1. FRAMEWORK & UI CONFIGURATION ---
{% if fw_name == 'flask' %}
from flask import Flask, render_template, jsonify
app = Flask(__name__, template_folder="{{ui_folder}}")

{% elif fw_name == 'fastapi' %}
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
app = FastAPI(title="{{project_name}}")
if Path("./static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

{% elif fw_name == 'django' %}
from django.core.management import execute_from_command_line
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{project_name}}.settings')

{% elif fw_name == 'bottle' %}
from bottle import Bottle, template, static_file
app = Bottle()

@app.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root='./static')

{% elif fw_name == 'sanic' %}
from sanic import Sanic, response
app = Sanic("{{project_name}}")
if Path("./static").exists():
    app.static("/static", "./static")

{% elif fw_name == 'tornado' %}
import tornado.web
import tornado.ioloop
import asyncio
{% endif %}

# --- 2. UNIVERSAL UI ROUTE (Serving index.html) ---
{% if fw_name == 'flask' %}
@app.route("/")
def home():
    return render_template("index.html", project_name="{{project_name}}", fw_name="{{fw_name}}")

{% elif fw_name == 'fastapi' %}
@app.get("/", response_class=HTMLResponse)
async def home():
    idx_path = Path("{{ui_folder}}/index.html")
    return idx_path.read_text() if idx_path.exists() else "Index not found"

{% elif fw_name == 'bottle' %}
@app.route("/")
def home():
    return template("{{ui_folder}}/index.html", project_name="{{project_name}}", fw_name="{{fw_name}}")

{% elif fw_name == 'sanic' %}
@app.get("/")
async def home(request):
    idx_path = Path("{{ui_folder}}/index.html")
    return response.html(idx_path.read_text()) if idx_path.exists() else response.text("Index not found")

{% elif fw_name == 'tornado' %}
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", project_name="{{project_name}}", fw_name="{{fw_name}}")

{% elif fw_name == 'django' %}
# Django routes are managed via urls.py and views.py
{% endif %}

# --- 3. DYNAMIC HEALTH CHECK ---
{% if fw_name == 'fastapi' %}
@app.get("/health")
async def health():
    return {"status": "online", "framework": "fastapi"}

{% elif fw_name == 'flask' %}
@app.route("/health")
def health():
    return jsonify({"status": "online", "framework": "flask"})

{% elif fw_name == 'bottle' %}
@app.route("/health")
def health():
    return {"status": "online", "framework": "bottle"}

{% elif fw_name == 'sanic' %}
@app.get("/health")
async def health(request):
    return response.json({"status": "online", "framework": "sanic"})

{% elif fw_name == 'tornado' %}
class HealthHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"status": "online", "framework": "tornado"})
{% endif %}

# --- 4. RUNTIME SERVER ORCHESTRATION ---
if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = {{port if (port and port != 'na') else 8000}}
    
    print(f"\n🔥 {{app_name}} v{{version}}")
    print(f"🚀 Framework: {{fw_name}} | Server Strategy: {{server}}")
    print(f"🌐 URL: http://{HOST}:{PORT}\n")

{% if fw_name == 'django' %}
    execute_from_command_line([sys.argv[0], "runserver", f"{HOST}:{PORT}"])

{% elif fw_name == 'fastapi' or fw_name == 'sanic' %}
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)

{% elif fw_name == 'tornado' %}
    tornado_app = tornado.web.Application([
        (r"/", MainHandler),
        (r"/health", HealthHandler),
    ], template_path="{{ui_folder}}", static_path="static")
    tornado_app.listen(PORT)
    tornado.ioloop.IOLoop.current().start()

{% elif server == 'waitress' %}
    from waitress import serve
    serve(app, host=HOST, port=PORT)

{% elif fw_name == 'flask' %}
    app.run(host=HOST, port=PORT, debug=True)

{% elif fw_name == 'bottle' %}
    app.run(host=HOST, port=PORT, debug=True)

{% else %}
    print("No native runner found. Please use a production WSGI/ASGI server.")
{% endif %}