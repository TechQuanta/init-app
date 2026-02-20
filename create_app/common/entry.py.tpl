"""
🚀 {{project_name}} - {{fw_name | upper}} ENGINE
Powered by: {{app_name}} v{{version}}
"""

import os
import sys
from pathlib import Path
{% if fw_name in ['fastapi', 'sanic', 'tornado'] %}
import asyncio
{% endif %}

# --- 1. FRAMEWORK & UI CONFIGURATION ---
{% if fw_name == 'flask' %}
from flask import Flask, render_template, jsonify
app = Flask(__name__)
# Flask looks in 'templates/' by default

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
# Bottle UI handler
@app.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root='./static')

{% elif fw_name == 'sanic' %}
from sanic import Sanic, response
app = Sanic("{{project_name}}")
app.static("/static", "./static")

{% elif fw_name == 'tornado' %}
import tornado.web
import tornado.ioloop
{% endif %}

# --- 2. UNIVERSAL UI ROUTE (Serving index.html) ---
{% if fw_name == 'flask' %}
@app.route("/")
def home():
    return render_template("index.html", project_name="{{project_name}}", fw_name="{{fw_name}}")

{% elif fw_name == 'fastapi' %}
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("{{ui_folder}}/index.html") as f:
        return f.read()

{% elif fw_name == 'bottle' %}
@app.route("/")
def home():
    return template("{{ui_folder}}/index.html", project_name="{{project_name}}", fw_name="{{fw_name}}")

{% elif fw_name == 'sanic' %}
@app.get("/")
async def home(request):
    with open("{{ui_folder}}/index.html") as f:
        return response.html(f.read())

{% elif fw_name == 'tornado' %}
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", project_name="{{project_name}}", fw_name="{{fw_name}}")

{% elif fw_name == 'django' %}
# Django routes are handled in {{app_name}}/urls.py
{% endif %}

# --- 3. DYNAMIC HEALTH CHECK ---
{% if fw_name != 'django' %}
@app.get("/health") if hasattr(app, 'get') else (app.route("/health") if hasattr(app, 'route') else None)
{% if fw_name in ['fastapi', 'sanic'] %}
async def health():
    return {"status": "online", "framework": "{{fw_name}}"}
{% else %}
def health():
    return {"status": "online", "framework": "{{fw_name}}"}
{% endif %}
{% else %}
def health():
    return {"status": "online", "framework": "django"}
{% endif %}

# --- 4. RUNTIME SERVER ORCHESTRATION ---
if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = {{port if port != 'na' else 8000}}
    
    print(f"\n🔥 {{app_name}} v{{version}}")
    print(f"🚀 Framework: {{fw_name}} | Server: {{server}}")
    print(f"🌐 UI URL: http://{HOST}:{PORT}\n")

{% if fw_name == 'django' %}
    execute_from_command_line([sys.argv[0], "runserver", f"{HOST}:{PORT}"])

{% elif server == 'uvicorn' or fw_name in ['fastapi', 'sanic'] %}
    import uvicorn
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)

{% elif server == 'gunicorn' %}
    os.system(f"gunicorn -w 4 -b {HOST}:{PORT} app:app")

{% elif server == 'waitress' %}
    from waitress import serve
    serve(app, host=HOST, port=PORT)

{% else %}
    # Native Dev Servers
    {% if fw_name == 'flask' %}
    app.run(host=HOST, port=PORT, debug=True)
    {% elif fw_name == 'bottle' %}
    app.run(host=HOST, port=PORT, debug=True)
    {% elif fw_name == 'tornado' %}
    tornado_app = tornado.web.Application([
        (r"/", MainHandler),
    ], template_path="{{ui_folder}}", static_path="static")
    tornado_app.listen(PORT)
    tornado.ioloop.IOLoop.current().start()
    {% endif %}
{% endif %}