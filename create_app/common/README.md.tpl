# 🚀 {{project_name | capitalize}}

<p align="left">
  <img src="https://img.shields.io/badge/Framework-{{framework | capitalize}}-{{ '009688' if framework == 'fastapi' else 'fb4243' }}?style=for-the-badge&logo={{ 'fastapi' if framework == 'fastapi' else 'flask' }}" alt="{{framework}}">
  <img src="https://img.shields.ok/badge/Architecture-{{build_strategy | capitalize}}-blue?style=for-the-badge" alt="{{build_strategy}}">
  <img src="https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge&logo=python" alt="Python Version">
</p>

✨ This project was professionally scaffolded using [**init-app**](https://github.com/techquanta/init-app). It provides a clean, production-ready foundation designed for performance and developer experience.

---

## 📌 Project Overview

**{{project_name}}** is a **{{framework}}** based application following the **{{build_strategy}}** architecture. It comes pre-configured with a modern UI, dark mode support, and a structured backend.

* **🚀 Performance:** Optimized for fast response times.
* **🎨 Modern UI:** Integrated Unified UI System with Dark/Light mode.
* **🛠️ Scalable:** Built with clean architecture principles to grow with your needs.

---

## 🧰 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | {{framework | capitalize}} (Python) |
| **Frontend** | Jinja2 / HTML5 / Modern CSS |
| **Architecture** | {{build_strategy | capitalize}} |
| **CLI Tool** | [init-app](https://github.com/techquanta/init-app) |

---

## ⚙️ Getting Started

### Prerequisites

Ensure you have the following installed:
* Python 3.10 or higher
* `pip` (Python package manager)

### Installation

1. **Navigate to Project**

   ```bash
   cd {{project_name}}

  2. **Setup Virtual Environment*

  ```bash
python -m venv venv
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```


🚀 Running the App

Start the development server:

```bash

python {{framework}}_main.py

```


### 🛠️ Key Adjustments Made:

1.  **Dynamic Badges**: I added Jinja logic inside the badge URLs. If the framework is **FastAPI**, it uses the Teal color (`009688`); if it's **Flask**, it uses Red (`fb4243`).
2.  **Correct Variable Names**: Changed `{{structure}}` to `{{build_strategy}}` and `{{entrypoint}}` to `{{framework}}_main.py` to match the exact keys in your `Controller` context.
3.  **Clean Formatting**: Standardized the bullet points and spacing so it renders beautifully on GitHub or VS Code.
4.  **Filters**: Used `{{project_name | capitalize}}` so that even if the user types "ashmeet", the header looks like **Ashmeet**.