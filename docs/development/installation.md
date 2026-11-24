# Installation and Environment Setup

DA-FIDAF targets **Python `3.12.*`** (pinned to `3.12.10` in `.python-version`) and manages reproducible core and developer dependencies with **`uv`** (`pyproject.toml`, `uv.lock`).

---

## 1. Core Framework Installation (`uv`)

```powershell
# Verify Python 3.12 and uv availability
python --version
uv --version

# Create project-local .venv and install locked runtime + dev dependencies
uv sync
```

Core runtime dependencies (`pyproject.toml`):

- `pyyaml>=6.0`
- `python-dotenv>=1.0`

Development dependencies (`[dependency-groups].dev`):

- `pytest>=8.0`
- `ruff>=0.8`
- `pre-commit>=4.0`

---

## 2. Documentation Website Dependencies (Separate Environment Recommended)

MkDocs Material is intentionally **excluded** from `pyproject.toml` so runtime experiment dependencies remain minimal. To build or preview the documentation website locally, install `requirements-docs.txt` into a separate documentation virtual environment (do **not** install globally):

```powershell
# Create an isolated documentation environment (example outside tracked files)
python -m venv .venv-docs
.venv-docs\Scripts\python.exe -m pip install -r requirements-docs.txt

# Validate strict build or serve locally
.venv-docs\Scripts\mkdocs.exe build --clean
.venv-docs\Scripts\mkdocs.exe serve
```

> **Note:** On Linux/macOS, substitute `.venv-docs/bin/python` and `.venv-docs/bin/mkdocs`. Do not commit `.venv-docs/` or `site/`.

---

## 3. Security Tooling (Gitleaks)

Install Gitleaks v8 (`>= 8.30.1`) via your OS package manager (e.g., `winget install Gitleaks.Gitleaks` on Windows) to run repository secret scans locally.
