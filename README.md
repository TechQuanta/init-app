# 🌌 [init-app](https://pypi.org/project/init-app/)

This is the "Source of Truth" document for your engine. I’ve designed this `COMMANDLINE.md` to look professional, high-tech, and crystal clear, exposing every feature from the **Architect** logic to the **Infrastructure Forge**.

---
<div align="center" >
<img width="750" height="350" alt="image" src="https://github.com/user-attachments/assets/7b78c8eb-c14d-4f97-aa2c-f3677b845132" />
</div>
<img width="500" height="221" alt="image" src="https://github.com/user-attachments/assets/a5977fc8-78c8-4226-902a-4511a7eb1fe2" /> <img width="500" height="221" alt="image" src="https://github.com/user-attachments/assets/cab5ba61-62e5-4407-ae42-2fd5dfc06b31" />

<img width="571" height="517" alt="image" src="https://github.com/user-attachments/assets/dc9a31af-6e72-4396-89bd-cd22940a49fe" /> <img width="400" height="236" alt="image" src="https://github.com/user-attachments/assets/6b7a6992-4172-4178-aa7d-961d2180181c" /> <img width="252" height="236" alt="image" src="https://github.com/user-attachments/assets/71d28576-42c7-4f3f-8c53-1599d8105e75" /> <img width="252" height="236" alt="image" src="https://github.com/user-attachments/assets/99fb4345-2e1d-4594-b7f6-96360542b260" /> <img width="252" height="236" alt="image" src="https://github.com/user-attachments/assets/4a1d5a74-fe58-4a92-b632-bed4fd3e3f2c" /> <img width="252" height="236" alt="image" src="https://github.com/user-attachments/assets/bef658ad-b15f-4a4a-9813-7040aae3015f" /> <img width="252" height="236" alt="image" src="https://github.com/user-attachments/assets/fa9e6caf-c76c-4cba-ae50-cc3cdd949365" />






**Version:** `1.0.0`

**Engineer:** `Ashmeet Singh`

This document outlines the full capabilities of the Project Engine. The engine supports two primary flows: **Interactive UI** (Menu-driven) and **Headless CLI** (Flag-driven).

---

## 🕹️ 1. Build Strategies

The engine behaves differently based on the `-t` (type) flag:

| Strategy | Behavior |
| --- | --- |
| `auto_config` | **Zero-Config.** Uses smart defaults for the chosen framework. Best for rapid prototyping. |
| `standard` | **The Balanced Build.** Generates common folder structures (routes, models, schemas). |
| `production` | **Enterprise Ready.** Includes full infrastructure suites (Docker, K8s) and strict folder separation. |
| `custom` | **Total Control.** Enables manual folder selection and individual `__init__.py` configuration. |

---

## 🛠️ 2. CLI Flag Reference

Use these flags to bypass menus and automate your workflow.

### Core Identity

* `name`: The name of your project folder.
* `-f, --framework`: `fastapi`, `flask`, `django`, `others`.
* `-s, --server`: Specify the runner (e.g., `uvicorn`, `gunicorn`, `hypercorn`).
* `-t, --type`: The build strategy (`auto_config`, `standard`, `production`, `custom`).

### Architecture & Packages (Custom Mode)

* `--folders`: Manually define every directory to be created.
* `--packages`: Define which of those folders should be Python packages (adds `__init__.py`).

### Data & Environment

* `--db`: Set the database engine (`sqlite`, `postgres`, `mysql`, `mongodb`).
* `--venv`: Enable virtual environment creation (`y` or `n`).

### Infrastructure Forge

* `--docker`: `dockerfile`, `docker-compose`, `.dockerignore`.
* `--github`: `main.yml`, `ci.yml`, `cd.yml`.
* `--k8s`: `deployment.yml`, `service.yml`, `ingress.yml`.
* `--jenkins`: `Jenkinsfile`.

---

## 🚀 3. Usage Examples

### A. The "Speed Demon" (Auto-Config)

Builds a FastAPI project with SQLite and a VENV instantly.

```bash
init-app quick_api -f fastapi -t auto_config --venv y

```

### B. The "Full Stack Pro" (Production)

Builds a Django + Postgres app with Docker and GitHub Actions.

```bash
init-app pro_backend -f django -t production --db postgres --docker dockerfile docker-compose --github main.yml

```

### C. The "Architect" (Deep Customization)

The most powerful command. Manually define folders and only make `src` and `app` Python packages.

```bash
init-app bespoke_engine -f fastapi -t custom \
  --folders src app docs tests logs \
  --packages src app \
  --db mongodb --venv y

```

---

## 🧠 4. Internal Logic & Features

### 🐍 Selective Package Initialization

Unlike standard generators that put `__init__.py` everywhere, this engine uses an `init_strategy` map. It only converts a folder into a Python package if explicitly told to or if the framework requires it.

### 💉 Snippet Injection (Django)

When building Django, the engine performs "surgical" regex injections:

* **Settings Patching**: Automatically adds your App to `INSTALLED_APPS`.
* **Security Injection**: Moves `SECRET_KEY` to environment variable logic.
* **DRF Integration**: If DRF is detected, it injects the `REST_FRAMEWORK` configuration block automatically.

### 🛡️ UI Folder Guard

The engine contains a security layer that prevents any template rendering from writing into the `ui/` directory, protecting the engine's core interface assets during a project build.

---

## 🏗️ 5. Directory Structure Example (Production)

<img width="500" height="552" alt="image" src="https://github.com/user-attachments/assets/75f44825-f486-40df-9100-015be74d9877" />

<img width="400" height="452" alt="image" src="https://github.com/user-attachments/assets/7dfda372-7ecf-4b3b-9d88-765c4ddc04c7" />


# **Contributors are welcome to this to enhance the optimisation of this repository**
