# DA-FIDAF

**Status:** Under active PhD research development (Stage 2 repository scaffolding).

## Overview & Research Purpose

**DA-FIDAF** is a PhD research framework for secure, adaptive, and reproducible intrusion detection and defense in heterogeneous Internet of Things (IoT) networks.

### Research Scope

- Heterogeneous IoT environments and multi-dataset evaluation
- Federated Learning (FL) under Non-IID client distributions
- Concept drift detection and continual adaptation
- Adversarial threats and Byzantine/poisoning resilience
- Robust aggregation mechanisms
- Privacy-preserving collaborative learning

## Core Architectural Principles

### Dataset Separation

Raw datasets, extracted archives, packet captures (PCAP/PCAPNG), large tabular exports, and heavy intermediate artifacts **remain permanently outside this Git repository** on external or separate storage. Original dataset files are treated as immutable. Only lightweight manifests, schemas, provenance records (verified post-inspection), and documentation are version-controlled.

### Portability

This repository is designed to run cleanly across Windows and Linux machines without hardcoded drive letters or machine-specific absolute paths. Machine-local storage roots and tool locations are supplied via Git-ignored environment variables (`.env`) or local configuration (`configs/paths.local.yaml`).

### Reproducibility Target

- **Python version:** `3.12.*` (pinned via `.python-version`)
- **Dependency management:** `uv` with `pyproject.toml` and `uv.lock` *(planned — Stage 4)*
- **Security hygiene:** Gitleaks secret scanning and automated pre-commit/pre-push checks *(planned — Stage 6)*

## Setup and Execution

- **Stage 3 (Implemented):** Portable core package (`src/dafidaf/`) with `pathlib`-based path resolution, typed configuration loading (`dataclasses`, `PyYAML`, `python-dotenv`), and read-only diagnostics via `python -m dafidaf doctor` (requires `PYTHONPATH=src` until the isolated `uv` environment is created in Stage 4).
- **Stage 4 (Planned):** Reproducible Python `3.12.10` environment (`uv.lock` and project-local `.venv`)
- **Stage 5 (Planned):** Machine-local `.env` configuration (Git-ignored)
- **Stage 6 (Planned):** Gitleaks, `pre-commit`, `pre-push`, and portability verification
- **Stage 7 (Planned):** Private GitHub repository connection (manual/authorized push)
- **Stage 8+ (Planned):** Dataset integrity validation and research experiments

See [docs/architecture/PORTABLE_ARCHITECTURE.md](docs/architecture/PORTABLE_ARCHITECTURE.md), [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md), and [docs/REPOSITORY_POLICY.md](docs/REPOSITORY_POLICY.md) for architecture details, current status, and governance rules.
