# 🚀 init-app

### Production-Ready Python Backend Bootstrapper

<div align="center" >
<img width="750" height="350" alt="image" src="https://github.com/user-attachments/assets/167cf853-24f4-4c55-af40-b4a41ac31b2a" />

</div>
<img width="1525" height="221" alt="image" src="https://github.com/user-attachments/assets/ac565776-55a8-4aad-a87f-e5f6ba873933" />

<img width="338" height="105" alt="image" src="https://github.com/user-attachments/assets/8d9c36f1-8d7d-403e-a5d2-684b7b9ad716" />


**init-app** is a professional CLI tool that scaffolds clean, structured, production-ready Python backend applications in seconds.

No boilerplate.
No manual setup.
Just clean architecture — instantly.

Supports:

* Django
* FastAPI
* Flask
* Falcon
* Tornado
* Sanic
* Pyramid
* Bottle

---

## Installation

```bash
pip install init-app
```

Verify:

```bash
init-app --version
```

---

## Interactive Mode

```bash
init-app
```

Keyboard-driven interface:

* ↑ ↓ Arrow navigation
* Enter to select
* Clean colored UI
* Guided project setup

<img width="1271" height="270" alt="image" src="https://github.com/user-attachments/assets/b2757298-9940-435b-9db0-f905e12cb5d1" />

<img width="1271" height="270" alt="image" src="https://github.com/user-attachments/assets/01362429-c202-4481-8aa4-9197591faa01" />


---

## Command Usage

```bash
init-app create [options]
init-app doctor
init-app list
init-app --version
```

---

## Options (Non-Interactive Mode)

```bash
init-app create -n myapp -f flask --venv
```

### Flags Overview

| Flag | Long Option   | Description                | Example         |
| ---- | ------------- | -------------------------- | --------------- |
| `-n` | `--name`      | Project name               | `-n myapp`      |
| `-f` | `--framework` | Target framework           | `-f flask`      |
| `-s` | `--structure` | Project structure          | `-s Production` |
| `-l` | `--location`  | Output directory           | `-l ./`         |
| `-d` | `--database`  | Database type              | `-d postgresql` |
| —    | `--venv`      | Create virtual environment | `--venv`        |

---

## Available Commands

| Command     | Purpose                   |
| ----------- | ------------------------- |
| `create`    | Generate new project      |
| `doctor`    | Validate environment      |
| `list`      | Show supported frameworks |
| `--version` | Show installed version    |

---

## Database Support

| Database   | Dependency Resolution | Config Template |
| ---------- | --------------------- | --------------- |
| PostgreSQL | ✔                     | ✔               |
| MySQL      | ✔                     | ✔               |
| SQLite     | ✔                     | ✔               |

---

## What Gets Generated

* Structured project layout
* Framework entrypoint
* `.env` configuration
* `requirements.txt`
* Logging setup
* Test scaffolding
* Database integration (optional)
* Virtual environment (optional)

Example structure:

```text
project/
├── app.py
├── requirements.txt
├── .env
├── logs/
├── routes/
├── services/
├── models/
└── tests/
```

Structure adapts automatically based on framework selection.

---

## Processing Experience

Clean spinner feedback during generation.




<img width="1007" height="306" alt="image" src="https://github.com/user-attachments/assets/89beb2ef-68ac-47ab-988a-9df142e76bd3" />



<img width="1007" height="506" alt="image" src="https://github.com/user-attachments/assets/e8ae64c8-b82b-4649-beaa-bbd173f91450" />


---

## Environment Check

```bash
init-app doctor
```

Confirms:

* Python version
* CLI installation
* System readiness

---

## Production Focus

init-app generates projects that are:

* Structured
* Predictable
* Deployment-ready
* Framework-correct
* Cleanly separated

---

## Version

```bash
init-app --version
```

---

init-app is built for engineers who value structure, speed, and production standards.

If you want, I can now:

* Add PyPI & GitHub badges
* Add your actual terminal screenshot placeholders
* Add your real processing GIF embed section
* Create a premium GitHub landing layout

Ready to make this release elite.

**Full Changelog**: https://github.com/TechQuanta/py-create/commits/v0.2.0