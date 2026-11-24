# DA-FIDAF — Phase 2 Module Status Matrix

## 1. Package & Module Status

| Workstream | Module Path | Status | Verification | Notes |
| --- | --- | --- | --- | --- |
| A — Data | `src/dafidaf/data/schemas.py` | PASS | Unit + Integration | Enforces `E5OntologyBlockedError` (E5 HOLD) |
| A — Data | `src/dafidaf/data/adapters.py` | PASS | Unit | ToN-IoT, CICIoT2023, Edge-IIoTset read-only adapters |
| A — Data | `src/dafidaf/data/preprocessing.py` | PASS | Unit + Integration | Fit-on-Train-only preprocessor with leakage guard |
| A — Data | `src/dafidaf/data/flow_extract.py` | PASS | Unit | `flow_extract_v1` for SLL (113), `0x0003` exclusion |
| A — Data | `src/dafidaf/data/partitioning.py` | PASS | Unit + Integration | 70/15/15 temporal split + buffer + active-flow exclusion |
| A — Data | `src/dafidaf/data/provenance.py` | PASS | Unit + Integration | Deterministic SHA-256 and `RunProvenance` metadata |
| B — FL/Privacy | `src/dafidaf/models/logistic.py` | PASS | Unit + Integration | Pure-Python `LinearLogisticIDS` (FedAvg + FedProx) |
| B — FL/Privacy | `src/dafidaf/privacy/mechanisms.py` | CONDITIONAL | Unit + Integration | L2 clip + Gaussian DP PASS; SecAgg interface only (`active=False`) |
| B — FL/Privacy | `src/dafidaf/federated/client.py` | PASS | Unit + Integration | `SimulatedClient` enforcing `sim_` client prefix |
| B — FL/Privacy | `src/dafidaf/federated/aggregation.py` | PASS | Unit + Integration | FedAvg, Median, Trimmed Mean, Krum, Multi-Krum |
| B — FL/Privacy | `src/dafidaf/federated/trainer.py` | PASS | Unit + Integration | Multi-round FL trainer with DP and attack hooks |
| C — Drift/Attr | `src/dafidaf/drift/core.py` | PASS | Unit + Integration | Synthetic drift, PSI/JSD, Page-Hinkley, ContinualAdapter |
| C — Drift/Attr | `src/dafidaf/attacks/simulators.py` | PASS | Unit + Integration | In-memory data poisoning & Byzantine update attacks |
| C — Drift/Attr | `src/dafidaf/attribution/engine.py` | PASS | Unit + Integration | Multi-signal Drift vs. Attack attribution engine |
| D — Eval/Orch | `src/dafidaf/evaluation/metrics.py` | PASS | Unit + Integration | Macro-F1, PR/ROC-AUC, FPR/FNR, FAR, paired CI |
| D — Eval/Orch | `src/dafidaf/orchestration/runner.py` | PASS | Unit + Integration | Synthetic E2E & YAML experiment runner with E5 gate |
| D — Eval/Orch | `src/dafidaf/orchestration/cli.py` | PASS | CLI + Integration | Phase 2 CLI (`python -m dafidaf.orchestration.cli`) |

---

## 2. Experiment Configuration Readiness (E1–E6)

| ID | Config File | Implementation Status | Real-Dataset Execution Status | Gate / Blocker |
| --- | --- | --- | --- | --- |
| E1 | `configs/experiments/e1_iid_vs_noniid.yaml` | PASS (Code + Config Ready) | NOT YET RUN | None — ready for Phase 3 execution |
| E2 | `configs/experiments/e2_concept_drift.yaml` | PASS (Code + Config Ready) | NOT YET RUN | None — ready for Phase 3 execution |
| E3 | `configs/experiments/e3_benign_drift_vs_poisoning.yaml` | PASS (Code + Config Ready) | NOT YET RUN | None — ready for Phase 3 execution |
| E4 | `configs/experiments/e4_byzantine_robust_agg.yaml` | PASS (Code + Config Ready) | NOT YET RUN | None — ready for Phase 3 execution |
| E5 | `configs/experiments/e5_cross_dataset_hold.yaml` | HOLD (Gate Enforced) | BLOCKED / HOLD | Cross-dataset feature & attack ontology alignment required |
| E6 | `configs/experiments/e6_ablation_overhead.yaml` | PASS (Code + Config Ready) | NOT YET RUN | None — ready for Phase 3 execution |

---

## 3. Explicit Non-Implemented / Deferred Items

- **Cryptographic Secure Aggregation**: `SecureAggregationInterface` is an interface and threat-model specification only (`secure_aggregation_active: False`). Full Bonawitz/SecAgg+ cryptographic masking is `NOT IMPLEMENTED` in Phase 2.
- **Deep Neural Network Backbones (PyTorch)**: Deferred to Phase 3 so Phase 2 maintains zero changes to `pyproject.toml` and `uv.lock`. `ModelInterface` is designed to accept drop-in neural backbones.
- **Cross-Dataset Ontology Harmonization (E5)**: Explicitly `HOLD` per Phase 1I decision; blocked at runtime by `E5OntologyBlockedError`.
