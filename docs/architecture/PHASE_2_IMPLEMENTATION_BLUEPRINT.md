# DA-FIDAF — Phase 2 Implementation Blueprint

- **Blueprint Version:** `1.0.0`
- **Status:** Planning blueprint only (no Phase 2 production code implemented yet).
- **Evidence Basis:** Phase 1 reports `01`–`24` under `docs/dataset/phase1/` and `docs/architecture/PORTABLE_ARCHITECTURE.md`.
- **Architectural Constraints:** Portable `pathlib.Path` via `dafidaf.config.load_config()`, Python `3.12.10` (`uv.lock`), zero hardcoded drive letters, read-only `DAFIDAF_DATA_ROOT`, outputs written strictly to `DAFIDAF_RUNS_ROOT`, train-only preprocessing fit, and deterministic YAML experiment configs.

---

## 1. Recommended Implementation Order & Module Architecture

Build strictly bottom-up in **10 modular stages** under `src/dafidaf/`, verifying each stage with unit tests before advancing:

```text
src/dafidaf/
├── datasets/          # Stage 1: Dataset adapters (ToN-IoT, CICIoT2023, Edge-IIoTset)
├── preprocessing/     # Stage 2: flow_extract_v1 + train-only scalers/imputers/encoders
│                      # Stage 3: Chronological split + 300s/900s + (ts+dur) embargo
├── federation/        # Stage 4: Logical FL client partitioner (IID, Dir, feature/qty skew)
│                      # Stage 7: Federated training loop (FedAvg baseline + telemetry)
│                      # Stage 8: Robust aggregation (Krum, TrimmedMean, CoordMedian, etc.)
├── interventions/     # Stage 5: Controlled synthetic drift (Protocol C)
│                      # Stage 6: Poisoning & Byzantine client simulators (E3/E4)
├── attribution/       # Stage 9: Drift-vs-attack attribution & benign-shift quarantine guard
└── evaluation/        # Stage 10: Metrics, confusion matrices, overhead & JSON run reports
```

---

## 2. Ten-Component Blueprint: Dependencies, Acceptance Criteria & Required Tests

| Order | Component | Dependencies | Evidence Ref | Acceptance Criteria | Required Tests (`tests/unit/` & `tests/integration/`) |
| :-: | :--- | :--- | :--- | :--- | :--- |
| **1** | **Dataset Adapters** (`src/dafidaf/datasets/`) | `dafidaf.paths`, `dafidaf.config`, `manifests/dataset_inventory.json` | `01`, `03`, `04`, `07` | Read-only streaming loaders for ToN-IoT (`Processed_Network_dataset`, `train_test_network.csv`), CICIoT2023 (`MERGED_CSV`), and Edge-IIoTset (`ML-EdgeIIoT`); explicit drop of IPs, ports, corrupted `frame.time`, `inf`, and complementary target column; SHA-256 verification hook. | Schema validation, identifier-drop assertion, `inf`/missing sanitization, SHA-256 mismatch error, zero writes to `DAFIDAF_DATA_ROOT`. |
| **2** | **Packet-to-Flow Extraction** (`src/dafidaf/preprocessing/flow_extract.py`) | Component 1 (optional PCAP baseline) | `19`, `20`, `21`, `22` | Productionize `flow_extract_v1`: `LINKTYPE_LINUX_SLL (113)` for PCAPNG + classic PCAP; explicit `0x0003`/ARP/fragment/EOF-tail drop counters; canonical bidirectional 5-tuple; `120s`/`600s` timeouts; Stream A/B separation; provenance sidecar JSON. | Bit-for-bit determinism test, `0x0003` exclusion test, EOF-truncated record test, UDP `null` TCP-flag & 1-pkt `null` IAT tests. |
| **3** | **Temporal Partitioning** (`src/dafidaf/preprocessing/splits.py`) | Component 1 | `10`, `12`, `16`, `23` | Chronological `70/15/15` and Protocol A/B time-boundary splitters with configurable embargo (`300s` default, `900s` option) + `ts + duration` active-flow exclusion; event-level deduplication `(stream_id, ts, 5tuple, hash)` preserving legitimate recurring flows; train-only preprocessor fit/transform API. | Zero future-to-past timestamp leakage, active-flow boundary exclusion test, train-only scaler fit test (mutating test data does not alter scaler params). |
| **4** | **Federated Client Partitioning** (`src/dafidaf/federation/partitioner.py`) | Component 3 | `06`, `23` | Deterministic seeded (`seed`) logical gateway partitioners applied **strictly inside Train**: IID, Dirichlet `Dir(alpha)` label-skew, feature-skew, log-normal quantity-skew, and combined heterogeneity; metadata explicitly flags `partition_type: simulated_logical_gateway`. | Reproducibility across seeds, non-empty client floor, `max(client_train_ts) < val_start_ts` assertion. |
| **5** | **Drift Simulation** (`src/dafidaf/interventions/drift.py`) | Component 3, 4 | `13`, `17`, `23` | Protocol C synthetic gradual and recurring drift generators (feature shift, prior shift, class-emergence schedule) parameterized strictly by YAML (`mechanism`, `onset_round`, `duration`, `severity`, `seed`) without mutating raw data. | Exact onset/severity verification, seed determinism, zero mutation of natural baseline tensors. |
| **6** | **Poisoning & Byzantine Simulation** (`src/dafidaf/interventions/attacks.py`) | Component 4 | `08`, `17`, `23` | Seeded client-side attacks: label-flip, targeted backdoor, gradient sign-flip, Gaussian noise, and model-replacement scaling with configurable malicious client fraction and round schedule. | Exact malicious-client isolation, zero contamination of benign clients, seed reproducibility. |
| **7** | **Federated Training Engine** (`src/dafidaf/federation/trainer.py`) | Components 1, 3, 4 | `08`, `23` | Reproducible FL round loop (`FedAvg` baseline) logging per-round wall-clock time, parameter bytes communicated, memory, and per-client metrics; writes immutable run artifacts to `DAFIDAF_RUNS_ROOT`. | Smoke convergence on synthetic tabular toy data, deterministic weight hash with fixed seed, zero writes inside Git repo. |
| **8** | **Robust Aggregation** (`src/dafidaf/federation/aggregators.py`) | Component 6, 7 | `08`, `23` | Modular aggregators (`FedAvg`, `CoordinateMedian`, `TrimmedMean`, `Krum`/`MultiKrum`, plus DA-FIDAF adaptive weighting) behind a common typed interface. | Breakdown-point unit tests verifying Byzantine outlier rejection vs `FedAvg` corruption. |
| **9** | **Drift–Attack Attribution** (`src/dafidaf/attribution/`) | Components 5, 6, 7, 8 | `16`, `17`, `23` | Client-update divergence and distribution-shift diagnostics distinguishing benign shifted clients (Period B / synthetic benign shift) from malicious poisoned clients without falsely quarantining benign drift. | Controlled synthetic separation test (benign-shifted client FPR vs poisoned client TPR). |
| **10** | **Evaluation & Reporting** (`src/dafidaf/evaluation/`) | Components 7, 8, 9 | `08`, `23`, `24` | Unified metrics (Macro-F1, PR-AUC, FPR, unseen-attack recall, benign false-quarantine rate, compute/comm overhead), sanitized `run_metadata.json` (Git SHA, `uv.lock` hash, dataset SHA-256, seeds, confounding tags), and Markdown summary tables. | Metric calculation unit tests, zero-secret/zero-absolute-path check on exported JSON reports. |

---

## 3. Dependency & Environment Governance for Phase 2

- **New ML/Data Dependencies (Deferred Until Authorized):** Adding `numpy`, `pandas`, `scikit-learn`, `scipy`, or `torch` must be proposed explicitly in `pyproject.toml`, locked via `uv lock`, and verified via `uv sync --locked --dev` on Python `3.12.10`.
- **E5 Gate:** Cross-dataset experiment E5 remains **HOLD** until `configs/datasets/label_taxonomy.yaml` and a semantic feature-alignment specification are approved (`04`, `24`).
- **Pre-Phase-2 Git Checkpoint:** Recommended to commit the audited Stage 7 baseline (`22` staged files) and Phase 1 documentation (`docs/dataset/phase1/01..24`, `manifests/*.json`) before beginning Phase 2 code commits.
