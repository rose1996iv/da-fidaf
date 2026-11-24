# DA-FIDAF — Repository Discovery and Inventory

- **Discovery Date (UTC):** `2026-11-24`
- **Repository Root:** `da-fidaf`
- **Pre-Preparation Footprint (excluding `.git/` and `.venv/`):** `151` files (`873,465` bytes / `0.83 MiB`; `0` files `> 1 MiB`)
- **Python Environment:** Python `3.12.10` (`.venv/`), managed with `uv` (`pyproject.toml`, `uv.lock`); `ruff` and `pytest` (`57` tests) installed; `mkdocs` / `mkdocs-material` not installed locally (declared separately in `requirements-docs.txt`).

---

## 1. Existing Repository Layout (Pre-Preparation Baseline)

| Area | Location | Count | Notes |
| --- | --- | ---: | --- |
| Root configuration & policy | `.env.example`, `.gitattributes`, `.gitignore`, `.gitleaks.toml`, `.pre-commit-config.yaml`, `.python-version`, `pyproject.toml`, `uv.lock`, `README.md` | 9 | All 9 are part of the 22 frozen Stage 7 staged files. |
| Git-ignored local environment | `.env` | 1 | Contains only `DAFIDAF_DATA_ROOT`, `DAFIDAF_RUNS_ROOT`, `DAFIDAF_SEVENZIP_EXE`; verified ignored by `.gitignore:7`. |
| Experiment configs | `configs/experiments/e1..e6*.yaml`, `configs/paths.example.yaml` | 7 | YAML specifications for E1–E6 (`e5_cross_dataset_hold.yaml` enforces `HOLD`). |
| Source code (`src/dafidaf/`) | `attacks/`, `attribution/`, `data/`, `drift/`, `evaluation/`, `federated/`, `models/`, `orchestration/`, `privacy/`, `visualization/`, plus core modules (`cli.py`, `config.py`, `paths.py`, `repo_guard.py`) | 34 | Established module paths preserved verbatim; zero refactoring during preparation. |
| Test suite (`tests/`) | `tests/unit/` (9 files) + `tests/integration/test_phase2_end_to_end.py` | 10 | `57` passing tests (`pytest`); synthetic fixtures only. |
| Lightweight manifests | `manifests/dataset_inventory.json`, `manifests/ton_iot_drift_analysis.json`, `manifests/ton_iot_temporal_audit.json` | 3 | Verified metadata/checksums (`166,863` bytes combined); no raw datasets. |
| Architecture & Phase 2 docs | `docs/architecture/` | 12 | Blueprint, specs, Phase 2 / 2.1 / 2.2 reports, IEEE plot spec, portable architecture. |
| Dataset & Phase 1 / 3 docs | `docs/dataset/phase1/` (24 reports), `docs/dataset/phase3/` (3 reports), `docs/dataset/PHASE_1_TRANSITION_READINESS.md` | 28 | Complete ToN-IoT, CICIoT2023, and Edge-IIoTset audit trail. |
| Experiment & Phase 3A/3B/3B.2 docs | `docs/experiments/EXPERIMENT_EXECUTION_GUIDE.md`, `docs/experiments/phase3/` (31 reports) | 32 | Pilot, Phase 3B, Phase 3B.1 audit, and Phase 3B.2 remediation reports. |
| Methodology alignment docs | `docs/methodology/` | 8 | Source inventory, specification, traceability, gap register, blueprint, verdict (`INSUFFICIENT SOURCE EVIDENCE`). |
| Security & governance docs | `docs/security/` (5 reports), `docs/PROJECT_STATUS.md`, `docs/REPOSITORY_POLICY.md` | 7 | Security reviews, Non-DP scope disclosure, repository policy. |
| GitHub directory | `.github/workflows/` (empty directory) | 0 | Ready for least-privilege CI workflows and issue/PR templates. |

---

## 2. Existing Documentation Reused Without Duplication

All 87 pre-existing documentation files under `docs/` are preserved at their original locations without altering historical conclusions:

- **Phase 1 Dataset Audits:** `docs/dataset/phase1/01_*.md` through `24_*.md` and `docs/dataset/PHASE_1_TRANSITION_READINESS.md`.
- **Phase 2 Architecture & Remediation:** `docs/architecture/PHASE_2_*.md`, `DATA_PIPELINE_SPECIFICATION.md`, `FEDERATED_LEARNING_SPECIFICATION.md`, `DRIFT_AND_ATTACK_ATTRIBUTION_SPECIFICATION.md`, `EVALUATION_PROTOCOL.md`, `IEEE_VISUALIZATION_SPECIFICATION.md`, `PORTABLE_ARCHITECTURE.md`.
- **Phase 3A, 3B, 3B.1, 3B.2 Reports:** `docs/dataset/phase3/PHASE_3*.md`, `docs/experiments/phase3/PHASE_3*.md`, `docs/experiments/EXPERIMENT_EXECUTION_GUIDE.md`.
- **Methodology Alignment Audit:** All 8 reports under `docs/methodology/`.
- **Security & Privacy Disclosures:** All 5 reports under `docs/security/`.

---

## 3. Gaps Identified & Additions Implemented in Preparation

| Category | Missing Pre-Preparation | Added During Preparation |
| --- | --- | --- |
| Documentation Website | No `mkdocs.yml`, no `docs/index.md`, no `requirements-docs.txt` | Created MkDocs Material configuration, `docs/index.md`, and `requirements-docs.txt`. |
| Structured Research Docs | No `docs/research/`, `docs/datasets/`, `docs/results/`, `docs/development/`, `docs/references/` hubs | Added concise hub pages linking directly to authoritative Phase 1–3B.2 reports without duplicating raw reports. |
| Visual Assets & Diagrams | `0` image/diagram files in repo; two draft architecture diagrams not present locally | Created `FIG-01`–`FIG-10` catalogs (`docs/architecture/figures/` and `docs/results/figures/`); copied 5 verified Phase 3B.2 preview PNGs (`522 KB`) into `docs/results/figures/`; flagged `FIG-01`–`FIG-09` as pending researcher diagram upload. |
| Root README & Ignore Updates | `README.md`, `.gitignore`, `.gitattributes` frozen in Stage 7 staged index | Created drop-in proposed replacements under `docs/repository/proposed_staged_updates/` pending authorization. |
| GitHub Metadata & CI | Missing `CITATION.cff`, `CHANGELOG.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue/PR templates, CI workflows | Created all standard GitHub metadata, issue/PR templates, label specification, and 3 least-privilege GitHub Actions workflows. |
| Repository Audit Reports | Missing baseline, security audit, release readiness, and publication checklist reports | Created full audit suite under `docs/repository/`. |

---

## 4. Assets That Must Permanently Remain External to Git

| External Asset Category | Typical Storage Location | Policy |
| --- | --- | --- |
| Raw & processed IoT datasets (ToN-IoT, CICIoT2023, Edge-IIoTset), PCAP/PCAPNG, damaged archives | `<DAFIDAF_DATA_ROOT>` (read-only external volume) | Never commit, copy, extract into repo, or modify. |
| Raw experiment run directories (`470` Phase 3B + `60` Phase 3B.2 + Phase 3A runs), checkpoints, master JSONs | `<DAFIDAF_RUNS_ROOT>` | Reference via run IDs, manifests, and SHA-256 checksums only. |
| Publication vector PDF/EPS bundles and raw plotting data CSVs | `<DAFIDAF_RUNS_ROOT>/figures/` & `<DAFIDAF_RUNS_ROOT>/phase3b_2/figures/` | Keep canonical originals external; only lightweight documentation PNG copies (`< 200 KB` each) reside in `docs/results/figures/`. |
| Machine-local environment & path overrides | `.env`, `configs/paths.local.yaml` | Strictly Git-ignored; never stage or commit. |
| Local virtual environments & caches | `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `site/` | Strictly Git-ignored. |
