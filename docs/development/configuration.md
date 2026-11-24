# Configuration Guide

DA-FIDAF avoids hardcoded machine-specific paths in source code by resolving storage roots via Git-ignored environment variables (`.env`) or local YAML configuration (`configs/paths.local.yaml`).

---

## 1. Machine-Local Environment File (`.env`)

Copy `.env.example` to `.env` (already Git-ignored via `.gitignore`) and configure external directories outside the repository:

```dotenv
DAFIDAF_DATA_ROOT=<ABSOLUTE_PATH_TO_READONLY_IOT_DATASETS>
DAFIDAF_RUNS_ROOT=<ABSOLUTE_PATH_TO_EXTERNAL_EXPERIMENT_RUNS>
DAFIDAF_SEVENZIP_EXE=<OPTIONAL_PATH_TO_7Z_EXECUTABLE>
```

Alternative YAML override: copy `configs/paths.example.yaml` to `configs/paths.local.yaml` (Git-ignored).

---

## 2. Verify Configuration Read-Only (`dafidaf doctor`)

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.venv\Scripts\python.exe -m dafidaf doctor
```

Expected exit code: `0` when all configured external roots exist on disk (strictly read-only; never creates directories or prints unrelated environment variables).

---

## 3. Experiment YAML Configurations (`configs/experiments/`)

| Config File | Experiment | Status |
| --- | --- | --- |
| `configs/experiments/e1_iid_vs_noniid.yaml` | E1 — IID vs. Non-IID Heterogeneity | `CONDITIONAL` (Executed on ToN-IoT) |
| `configs/experiments/e2_concept_drift.yaml` | E2 — Concept Drift & Replay | `CONDITIONAL` (Executed with synthetic drift) |
| `configs/experiments/e3_benign_drift_vs_poisoning.yaml` | E3 — Benign Drift vs. Poisoning Attribution | `CONDITIONAL` (v1 & v2 evaluated) |
| `configs/experiments/e4_byzantine_robust_agg.yaml` | E4 — Byzantine-Robust Aggregation | `CONDITIONAL` (Executed on ToN-IoT) |
| `configs/experiments/e5_cross_dataset_hold.yaml` | E5 — Cross-Dataset Generalization | **`HOLD`** (Fails closed by design) |
| `configs/experiments/e6_ablation_overhead.yaml` | E6 — Ablation & Overhead | `CONDITIONAL` (Closed-loop verified in 3B.2) |
