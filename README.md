# MyBudget

MyBudget is a simple personal finance manager with a FastAPI backend and a NiceGUI web UI. It tracks accounts, bills, budgets, transactions, income, categories, and settings.

## Features
- FastAPI REST API with SQLite defaults (SQLModel/SQLAlchemy)
- NiceGUI frontend (`run_ui.py`) consuming the API
- Accounts, bills, budgets, transactions, income, and categories management
- Settings for currency/format/timezone and pruning
- Built-in docs endpoints: Swagger, ReDoc, user and developer guides
- Sample data loader for quick demos
- Idempotent bootstrap script for initial setup
- Automated releases with release-please

## Requirements
- Python 3.12+ (recommended)
- pip

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd MyBudget
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Bootstrap with defaults (categories and settings)
./scripts/setup.sh
```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the API
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- Default base URL: `http://localhost:8000` (override with `API_URL` env var).
- Docs:
  - Swagger UI: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`
  - Docs list JSON: `http://localhost:8000/docs/list`
  - Rendered guides: `/docs/user`, `/docs/developer`

## Run the UI
```bash
python run_ui.py
```
- Serves NiceGUI on `http://localhost:8080`.
- The UI uses the API URL from the `API_URL` environment variable (falls back to `http://localhost:8000`). Ensure the API is running and reachable.

## Load Sample Data (optional)
```bash
python scripts/load_sample_data.py
```

## Tests
```bash
pytest
```

## Project Layout
- `main.py` — FastAPI application entrypoint and router includes.
- `run_ui.py` — starts the NiceGUI frontend.
- `app/models` — SQLModel models and database setup.
- `app/routers` — FastAPI routers (accounts, bills, budgets, transactions, settings, income, categories, docs).
- `app/ui` — NiceGUI components and modules.
- `documentation/USER.md`, `documentation/DEVELOPER.md` — user and developer guides.
- `scripts/` — helper scripts (sample data, setup).
- `tests/` — pytest suite.
