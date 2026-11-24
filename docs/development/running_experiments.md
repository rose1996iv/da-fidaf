# Running Experiments and Reproducing Results

For the complete Phase 2 CLI reference, see [Experiment Execution Guide](../experiments/EXPERIMENT_EXECUTION_GUIDE.md).

---

## 1. Synthetic End-to-End Smoke Test (No External Dataset Required)

Explicitly tagged `SYNTHETIC_TOY_GENERATOR` (never reported as real-world evidence):

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.venv\Scripts\python.exe -m dafidaf.orchestration.cli run-e2e-synthetic --seed 42 --save
```

---

## 2. Validating External Dataset Files (Read-Only, Root-Contained)

```powershell
.venv\Scripts\python.exe -m dafidaf.orchestration.cli validate-dataset `
  --family ton_iot `
  --csv "<DAFIDAF_DATA_ROOT>\...\Network_dataset_1.csv" `
  --max-rows 500
```

Paths outside `DAFIDAF_DATA_ROOT` are automatically rejected.

---

## 3. Running Configured Real-Dataset Experiments

```powershell
.venv\Scripts\python.exe -m dafidaf.orchestration.cli run-experiment `
  --config configs/experiments/e1_iid_vs_noniid.yaml `
  --dataset-csv "<DAFIDAF_DATA_ROOT>\...\train_test_network.csv" `
  --multi-seed `
  --save
```

- **Standard Phase 3B / 3B.2 Seed Set (`n=5`):** `[42, 101, 202, 303, 404]`.
- **Expected Outputs (`<DAFIDAF_RUNS_ROOT>/<timestamp>_<exp>_seed<seed>_<nonce>/`):**
  - `run_report.json` (LF-canonical UTF-8 JSON)
  - `run_report.sha256` (raw-byte SHA-256 checksum matching `run_report.json` on disk)
- **E5 Safety Gate:** Passing `e5_cross_dataset_hold.yaml` intentionally raises `E5OntologyBlockedError` because cross-dataset E5 remains on `HOLD`.
- **Privacy Disclosure:** Current experiment configs execute **Non-DP baselines only** (`dp_enabled=False`, `secure_aggregation_active=False`).

---

## 4. Phase 3B & Phase 3B.2 Full-Scale Reproduction Notes

Full-scale Phase 3B (`490` runs) and Phase 3B.2 (`60` targeted remediation runs) orchestration and IEEE figure plotting scripts are archived alongside external run outputs under `<DAFIDAF_RUNS_ROOT>/scripts/` and `<DAFIDAF_RUNS_ROOT>/phase3b_2/`. Verify artifact integrity against `<DAFIDAF_RUNS_ROOT>/phase3b_2/canonical_sha256_manifest.json` (`578` hashed files).
