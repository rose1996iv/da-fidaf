# Testing, Linting, and Security Verification

All automated verification commands are strictly read-only and run without raw datasets.

---

## 1. Lint & Unit/Integration Test Suite (`57` Tests)

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.venv\Scripts\ruff.exe check src tests --no-cache
.venv\Scripts\python.exe -m pytest -v -p no:cacheprovider tests
```

Test coverage (`tests/`):

- `tests/unit/test_config_and_paths.py` — Portable path resolution and YAML/dotenv precedence.
- `tests/unit/test_doctor_cli.py` — Read-only `dafidaf doctor` and secret non-leakage guarantees.
- `tests/unit/test_repo_guard.py` — Size, extension, whitespace, and EOF guardrails.
- `tests/unit/test_workstream_a_data.py` — Schema, chronological splitting, and train-only preprocessing.
- `tests/unit/test_workstream_b_federated.py` — Federated clients, trainers, and robust aggregators.
- `tests/unit/test_workstream_c_drift_attacks_attribution.py` — Drift detectors, attack simulators, and attribution.
- `tests/unit/test_phase2_2_remediation.py` — Audit remediation regressions (E5 `HOLD`, strict timestamps, nonce uniqueness).
- `tests/unit/test_phase3b_2_remediation.py` — LF-canonical raw-byte SHA-256, leak-free `val_loss_delta`, and closed-loop `attribution_filter` code isolation.
- `tests/unit/test_visualization_ieee.py` — IEEE figure styling and external-root containment.
- `tests/integration/test_phase2_end_to_end.py` — Deterministic synthetic end-to-end pipeline.

---

## 2. Repository Hygiene & Secret Scans

```powershell
# Repository guard (10 MiB limit, blocked dataset/secret extensions, trailing whitespace, EOF newline)
.venv\Scripts\python.exe -m dafidaf.repo_guard check-files <files...>

# Gitleaks secret scans
gitleaks dir --redact --config .gitleaks.toml .
gitleaks git --staged --redact --config .gitleaks.toml .
```

Pre-commit and pre-push hook specifications live in `.pre-commit-config.yaml`.
