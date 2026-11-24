# DA-FIDAF Portable Architecture

This document defines the portable storage, configuration, and cross-platform execution design implemented in Stage 3 of the DA-FIDAF research framework.

## 1. Repository vs. Dataset Storage Separation

DA-FIDAF strictly separates **version-controlled research code** from **external dataset storage**:

- **Git repository (source code, configs, manifests, docs, tests):** Lightweight, portable, and hosted in a private GitHub repository.
- **External dataset storage (`DAFIDAF_DATA_ROOT`):** Resides on a separate directory, drive, or mount point outside the Git repository. Raw archives, packet captures (`.pcap`/`.pcapng`), extracted CSVs, and large intermediate datasets are never placed inside the Git working tree.

The repository and dataset root do not need to share the same drive letter, filesystem, or mount hierarchy.

## 2. Configuration Precedence

Path resolution in `src/dafidaf/paths.py` and `src/dafidaf/config.py` uses typed Python `dataclasses`, `pathlib.Path`, `PyYAML`, and `python-dotenv` with strict, deterministic precedence (highest to lowest):

1. **Process environment variables** (`DAFIDAF_DATA_ROOT`, `DAFIDAF_RUNS_ROOT`, `DAFIDAF_SEVENZIP_EXE`)
2. **Machine-local `.env` file** at repository root (Git-ignored; parsed via `dotenv_values()` without mutating process `os.environ`)
3. **Machine-local YAML file** at `configs/paths.local.yaml` (Git-ignored)
4. **Tracked example template** at `configs/paths.example.yaml` (placeholders such as `<SET_VIA_ENV_OR_LOCAL_CONFIG>` are treated as unconfigured)
5. **Safe repository-relative defaults** (for repository-local paths such as `manifests/` and `runs/`)

Only explicitly allowlisted `DAFIDAF_*` keys are read; unrelated environment variables, tokens, and credentials are ignored and never printed in diagnostic output.

## 3. Windows and Linux Portability

- All path manipulation uses `pathlib.Path` (with Windows drive-letter and UNC awareness via `PureWindowsPath`).
- Zero machine-specific absolute paths or drive letters appear in tracked source code or tracked configuration files.
- `.gitattributes` enforces LF (`\n`) line endings across code, YAML, JSON, and Markdown files.
- External tools such as 7-Zip and Gitleaks are discovered dynamically (via `DAFIDAF_SEVENZIP_EXE`, `PATH`, or Windows WinGet shim fallback) rather than assuming OS-specific install paths.

## 4. Dataset Immutability

- Raw datasets under `DAFIDAF_DATA_ROOT` are strictly read-only.
- Configuration loading and `python -m dafidaf doctor` never create directories, never modify files, and never scan dataset contents.
- Future preprocessing pipelines must write derived outputs to a separate processed directory rather than mutating raw dataset files.

## 5. External Experiment Output Strategy

- Experiment outputs, logs, and checkpoints default to `DAFIDAF_RUNS_ROOT` (which may point to a fast external drive or scratch volume) or the Git-ignored local `runs/` fallback.
- Only lightweight, sanitized experiment metadata and validation summaries are promoted into tracked directories (`manifests/`, `docs/`).

## 6. Configuring a Second Computer Without Editing Tracked Code

To run DA-FIDAF on another Windows or Linux machine:

1. Clone the private repository.
2. Attach or mount the dataset storage at any path (for example, `E:\Datasets\IoT` on Windows or `/mnt/iot-datasets` on Linux).
3. Copy `.env.example` to `.env` (or `configs/paths.example.yaml` to `configs/paths.local.yaml`) and set `DAFIDAF_DATA_ROOT`, `DAFIDAF_RUNS_ROOT`, and optionally `DAFIDAF_SEVENZIP_EXE`.
4. Run `python -m dafidaf doctor` to verify Python `3.12.*`, repository state, configured paths, and security tooling with zero changes to tracked files.
