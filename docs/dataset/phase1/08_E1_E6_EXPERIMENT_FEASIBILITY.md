# 08 — E1–E6 Experiment Feasibility Matrix (DA-FIDAF Phase 1 Part A)

- **Audit Timestamp (UTC):** `2026-11-24T03:20:51Z`
- **Classifications:** `PASS`, `CONDITIONAL`, `HOLD`, `NOT SUPPORTED` (evidence-based; zero fabricated dataset properties).

## 1. Updated Feasibility Matrix

| Exp | Research Question | Status | Verified Local Evidence | Blockers & Mandatory Prerequisites |
| :-: | :--- | :---: | :--- | :--- |
| **E1** | **IID vs. Non-IID Federated Learning** | **CONDITIONAL** | Verified multi-class tabular datasets: CICIoT2023 `MERGED_CSV` (40 cols), ToN-IoT `train_test_network.csv` (`211,043` rows, 10 classes), Edge-IIoTset `ML-EdgeIIoT-dataset.csv` (`157,800` rows, 15 classes). | 1. Explicitly document FL clients as **simulated logical gateways** (Dirichlet/shard Non-IID vs IID).<br>2. Deduplicate and strip IP/port/corrupted `frame.time` columns.<br>3. Lock train-only preprocessing and fixed seeds. |
| **E2** | **Stable vs. Gradual / Abrupt Concept Drift** | **HOLD** | CICIoT2023: **no timestamps** (`NOT SUPPORTED`). ToN-IoT `train_test_network.csv`: **`ts` stripped**. Edge-IIoTset `frame.time`: **corrupted/incomplete**. Only ToN-IoT `Processed_Network_dataset` (`ts` Unix epoch), `Processed_IoT_dataset` (`date`/`time`), and `GroundTruth_*` (`ts`) have real wall-clock timestamps. | 1. Phase 1B full chronological span, monotonicity, and timezone alignment audit of ToN-IoT `Processed_*` + `GroundTruth_*`.<br>2. Decide whether to reacquire/exclude the 2 truncated 20 GB ToN-IoT archives or add a verified temporal IoT benchmark. |
| **E3** | **Benign Concept Drift vs. Poisoning Attacks** | **HOLD** | Clean labelled baselines exist across all 3 families, but no native poisoning ground truth exists and natural drift prerequisite (E2) is on **HOLD**. | 1. Resolve E2 temporal drift baseline first.<br>2. Author versioned, seed-controlled poisoning injection protocol (label-flip / backdoor / scaling) strictly in derived experiment code, never mutating raw data. |
| **E4** | **Adaptive vs. Byzantine / Malicious Clients** | **CONDITIONAL** | Verified labelled datasets (CICIoT2023, ToN-IoT, Edge-IIoTset) support FL simulation with seeded Byzantine client behaviors (sign-flip, Gaussian noise, model-replacement, label-flip). | 1. Resolve E1 deduplication, identifier stripping, and simulated-client partitioning.<br>2. Lock formal Byzantine threat model and robust aggregation configs (`FedAvg`, `Krum`, `TrimmedMean`, `Median`, etc.). |
| **E5** | **Cross-Dataset / Cross-Environment Generalization** | **HOLD** | All 3 families exist locally, **but** schemas are semantically incompatible (CICIoT2023: 39 flow stats; ToN-IoT: 44/46 Zeek conn logs; Edge-IIoTset: 63 packet headers) and label taxonomies have granularity/coverage gaps. | 1. Define versioned semantic feature contract (or cross-domain transfer/representation alignment protocol — never naive column merging).<br>2. Define versioned coarse label ontology (`configs/datasets/label_taxonomy.yaml`). |
| **E6** | **Ablations & Computation / Communication Overhead** | **PASS** | Manageable verified baselines (`train_test_network.csv` 28.5 MiB, `ML-EdgeIIoT-dataset.csv` 78.4 MiB, CICIoT2023 `MERGED_CSV` shards) enable controlled round-by-round timing, parameter-byte, and ablation measurement. | Record hardware metadata, FL round/client counts, seeds, compression/aggregation settings, and run metadata JSON under `DAFIDAF_RUNS_ROOT`. |

## 2. Summary Verdict
- **PASS:** `E6` (`1 / 6`)
- **CONDITIONAL:** `E1`, `E4` (`2 / 6` — unblocked as soon as Phase 1B data-cleaning & partitioning contracts are locked)
- **HOLD:** `E2`, `E3`, `E5` (`3 / 6` — require temporal provenance verification on ToN-IoT `Processed_*` and semantic cross-dataset mapping before execution)
