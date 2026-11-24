# DA-FIDAF — Experiment Execution Guide

## 1. Prerequisites

Ensure your local `.env` (Git-ignored, based on `.env.example`) sets:
- `DAFIDAF_DATA_ROOT` — Read-only external IoT dataset directory
- `DAFIDAF_RUNS_ROOT` — External experiment output directory (outside the Git repository)

Verify environment health before running experiments:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.venv\Scripts\python.exe -m dafidaf doctor
```

Expected result: exit code `0` with all configured paths verified.

---

## 2. Phase 2 CLI Commands (`python -m dafidaf.orchestration.cli`)

The Phase 2 orchestration CLI is intentionally hosted in `src/dafidaf/orchestration/cli.py` (preserving the Stage 7 `src/dafidaf/cli.py`).

### 2.1 Inspect Canonical ToN-IoT Schema
```powershell
.venv\Scripts\python.exe -m dafidaf.orchestration.cli inspect-schema
```

### 2.2 Validate Local Dataset Files (Read-Only, Root-Contained)
```powershell
.venv\Scripts\python.exe -m dafidaf.orchestration.cli validate-dataset --family ton_iot --csv "<DAFIDAF_DATA_ROOT>\...\Network_dataset_1.csv" --max-rows 500
```
Supported `--family` values: `ton_iot`, `ciciot2023`, `edge_iiot`, `edge_iiotset`. Paths outside `DAFIDAF_DATA_ROOT` are rejected.

### 2.3 Run Deterministic Synthetic End-to-End Smoke Test
Runs Workstreams A -> B -> C -> D on a synthetic toy dataset (explicitly tagged `SYNTHETIC_TOY_GENERATOR`; not real-world evidence) and saves JSON artifacts to `DAFIDAF_RUNS_ROOT`:

```powershell
.venv\Scripts\python.exe -m dafidaf.orchestration.cli run-e2e-synthetic --seed 42 --save
```

### 2.4 Run a Configured Experiment YAML
Real-dataset execution requires `--dataset-csv` (contained within `DAFIDAF_DATA_ROOT`) and never silently falls back to synthetic data:

```powershell
.venv\Scripts\python.exe -m dafidaf.orchestration.cli run-experiment --config configs/experiments/e1_iid_vs_noniid.yaml --dataset-csv "<DAFIDAF_DATA_ROOT>\...\train_test_network.csv" --multi-seed --save
```

To run an explicit synthetic smoke test with a YAML config:
```powershell
.venv\Scripts\python.exe -m dafidaf.orchestration.cli run-experiment --config configs/experiments/e1_iid_vs_noniid.yaml --synthetic-smoke-test --save
```

Available experiment configs under `configs/experiments/`:
- `e1_iid_vs_noniid.yaml`
- `e2_concept_drift.yaml`
- `e3_benign_drift_vs_poisoning.yaml`
- `e4_byzantine_robust_agg.yaml`
- `e5_cross_dataset_hold.yaml` (fails closed with `E5OntologyBlockedError` because E5 is `HOLD`)
- `e6_ablation_overhead.yaml`

---

## 3. Output Artifacts Layout

When `--save` is passed, a unique microsecond-and-nonce-stamped run directory is created under `DAFIDAF_RUNS_ROOT` (preventing accidental overwrites):

```
<DAFIDAF_RUNS_ROOT>/<YYYYMMDDTHHMMSS_ffffffZ>_<experiment>_seed<seed>_<nonce>/
├── run_report.json       # Metrics, attribution summary, privacy accounting, provenance
└── run_report.sha256     # SHA-256 integrity checksum of run_report.json
```

---

## 4. Verification & Test Suite

Run the full lint and test suite (38 tests across unit + integration):

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.venv\Scripts\ruff.exe check src tests --no-cache
.venv\Scripts\python.exe -m pytest -v -p no:cacheprovider tests
```
