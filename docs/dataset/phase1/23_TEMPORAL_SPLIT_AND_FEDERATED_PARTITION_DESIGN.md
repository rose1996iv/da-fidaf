# 23 — Temporal Split, Flow Leakage & Federated Client Partition Design (DA-FIDAF Phase 1H)

- **Audit Timestamp (UTC):** `2026-11-24T04:57:31Z`
- **Primary Evidence Basis:** Phase 1A–1G reports (`01`, `10`, `12`, `14`, `17`, `20`, `21`, `22`) plus direct read-only quantitative validation on ToN-IoT `Processed_Network_dataset` (`Network_dataset_1.csv` Period A normal `n = 200,898`; `Network_dataset_23.csv` campaign `n = 339,021`).
- **Final Verdict:** **PASS (Protocol Design Validated) / CONDITIONAL (For Execution Pending Phase 2 Pipeline Implementation)** *(Reproducible chronological split, embargo + active-flow end-time exclusion, capture-stream stratification, and seeded logical FL client partitioning are quantitatively validated with zero temporal leakage; execution remains conditional on formal Phase 2 preprocessing implementation and explicit simulated-gateway disclosure.)*

---

## 1. Executive Summary

- **Flow Identity & Legitimate Recurrence (VERIFIED):** In Period A normal traffic (`n = 200,898`), **`99.25%`** of chronological test rows share identical 7-feature vectors with earlier training rows at **distinct timestamps** (legitimate periodic IoT/DNS traffic). Removing flows solely on matching feature vectors would destroy authentic IoT periodicity; deduplication must therefore be keyed on deterministic **event-level flow identity** `(stream_id, ts_start_us, canonical_5tuple, flow_feature_hash)`.
- **Embargo + Active-Flow End-Time Validation (VERIFIED):** On a `70/15/15` chronological split, a **`300s` (5-min) embargo + `ts + duration` active-flow exclusion** retains **`99.681%`** of Period A normal records (`620` embargo + `20` active-flow discarded) and **`98.774%`** of Shard 23 campaign records (`4,153` embargo + `3` active-flow discarded), eliminating boundary-straddling sessions with minimal data loss.
- **Zero-Leakage Federated Partitioning (VERIFIED):** Applying `K = 10` logical gateway partitioning **strictly inside the chronological training partition** (`seed = 42`) guarantees `max(client_train_ts) < val_start_ts` (`zero_temporal_leakage = True`).
- **Capture-Source Stratification (VERIFIED):** Stream A (`normal_1..13`, `67%–83%` `0x0003`) and Stream B (`normal_IoT_2..3`, `0%` `0x0003`, `PSI = 4.30–4.38` on `duration_s`) must **never** be mixed as a single homogeneous baseline.

---

## 2. Flow-Level Leakage Analysis & Deterministic Flow Identity

| Leakage Vector | Root Cause | Mandatory Control |
| :--- | :--- | :--- |
| **Identical flows across temporal partitions** | Exact duplicate records in same/adjacent seconds (e.g., `5.7%` in `train_test_network.csv`, `16.3%` in `ML-EdgeIIoT`). | Deduplicate by `(stream_id, ts_start_us, canonical_5tuple, feature_hash)` before splitting; enforce `max(ts_train) + embargo <= min(ts_val)`. |
| **Bidirectional flow duplication** | Splitting forward `(A->B)` and reverse `(B->A)` into separate records. | Canonicalize 5-tuple as `(min(E1, E2), max(E1, E2), l4_proto)` before flow aggregation. |
| **Overlapping capture streams** | Stream A (`normal_1..13`) and Stream B (`normal_IoT_2..3`) share `24.7%–29.1%` L3 payloads across overlapping hours. | Keep Stream A and Stream B in separate experimental strata; never mix across Train and Test. |
| **Long-lived flows crossing boundaries** | Flows starting in Train (`ts <= t_end`) whose `ts + duration` extends into Val/Test (`1.29% > 60s` in Period A). | Enforce **active-flow end-time exclusion**: drop any Train/Val flow where `ts + duration >= next_split_start_ts`. |
| **Legitimate recurring feature vectors** | Periodic IoT telemetry/DNS produces identical feature vectors at distinct timestamps (`99.25%` in Period A Test). | **RETAIN** recurring flows with distinct `ts`; never collapse globally by feature vector alone. |

---

## 3. Temporal Split Protocol & 4. Embargo Sensitivity (VERIFIED)

Chronological ordering is applied **only** to datasets with verified wall-clock timestamps (`ToN-IoT Processed_Network_dataset`, `normal_pcaps.zip`). Timestamps are **never** fabricated for CICIoT2023 (absent), `train_test_network.csv` (`ts` stripped), or Edge-IIoTset CSVs (`frame.time` corrupted/incomplete).

### Quantitative 70/15/15 Split & Embargo Validation (VERIFIED)

| Dataset Shard & Configuration | Train | Val | Test | Discarded (Embargo) | Discarded (`ts+dur`) | Retained (%) | Test Recurring Feature Match |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Period A Normal (`n = 200,898`)** — `0s` | `140,628` | `30,137` | `30,133` | `0` | `0` | `100.000%` | `99.25%` |
| **Period A Normal** — `300s` embargo | `140,628` | `29,837` | `29,813` | `620` | `0` | `99.691%` | `99.25%` |
| **Period A Normal** — `300s` + `ts+dur` | `140,622` | `29,823` | `29,813` | `620` | `20` | **`99.681%`** | `99.25%` |
| **Period A Normal** — `900s` + `ts+dur` | `140,622` | `29,105` | `29,116` | `2,037` | `18` | `98.977%` | `99.24%` |
| **Shard 23 Campaign (`n = 339,021`)** — `0s` | `237,314` | `50,858` | `50,849` | `0` | `0` | `100.000%` | `66.87%` |
| **Shard 23 Campaign** — `300s` + `ts+dur` | `237,312` | `48,770` | `48,783` | `4,153` | `3` | **`98.774%`** | `65.47%` |
| **Shard 23 Campaign** — `900s` + `ts+dur` | `237,312` | `44,537` | `44,567` | `12,603` | `2` | `96.282%` | `62.23%` |

- **Recommended Default:** **`300s` (5-min) embargo + `ts + duration` active-flow end-time exclusion** (retains `98.8%–99.7%` of records while eliminating boundary-crossing sessions; `900s` optional for high-conservatism sensitivity runs).
- **Three Supported Temporal Regimes:** (A) Stable normal baseline (`Apr 2–4`), (B) Natural abrupt novel-attack emergence (`Apr 2–24` -> `Apr 25–29`, binary & unseen-class evaluation), (C) Explicitly labeled controlled synthetic drift (gradual/recurring).

---

## 5. Logical Federated Client Partition Design (Simulated Gateways)

Because **no dataset provides genuine physical gateway IDs**, all FL partitions are explicitly classified as **simulated logical gateways** (`K` clients, fixed `seed`, partitioned **strictly after** temporal splitting so `max(client_train_ts) < val_start_ts`):

1. **IID Partition:** Stratified uniform random assignment across `K` clients (`seed = 42`; verified on Shard 23: `K = 10` client sizes `[23,731 .. 23,733]`).
2. **Label-Skew Non-IID:** Symmetric Dirichlet `Dir(alpha)` per class (`alpha in {0.5, 0.1}`, fixed `seed`, minimum-samples floor to prevent empty clients).
3. **Feature-Distribution-Skew Non-IID:** Deterministic cluster/quantile assignment (e.g., partitioning by protocol/traffic-rate strata or k-means on **Train-only** standardized features).
4. **Quantity-Skew Non-IID:** Log-normal client sample allocation (`sigma = 0.8`, verified on Shard 23: `[6,870 .. 47,682]`).
5. **Combined Heterogeneity:** Joint `Dir(alpha)` label skew + log-normal quantity skew + optional cross-silo environment assignment (CICIoT2023 / ToN-IoT / Edge-IIoTset silos in E5).

---

## 6. Capture-Source Confounding Recommendation (`normal_pcaps.zip`)

- **Verified Asymmetry:** Stream A (`normal_1..13`) vs. Stream B (`normal_IoT_2..3`) differ drastically in `0x0003` prevalence (`67%–83%` vs `0%`), flow yield per 200k packets (`293–897` vs `1,536–1,783`), 1-packet UDP share (`9.6%–52.5%` vs `62.9%`), and flow-feature distributions (`duration_s` `PSI = 4.30–4.38`).
- **Mandatory Policy:** **Keep Stream A and Stream B as separate experimental strata** (Option 1) and run primary single-stream FL partitions within one comparable stream (Option 3). Use both streams together **only** as an explicitly labeled confounded robustness stress test (Option 4) — never interpret Stream A vs. Stream B divergence as natural concept drift.

---

## 7. Preprocessing & Leakage Controls

1. **Temporal split FIRST**, before any learned transformation or client partitioning.
2. **Train-only fitting:** Imputers, scalers (`RobustScaler`/`StandardScaler`), categorical encoders, and feature selectors fit **exclusively on Train** (or per-client local Train in FL).
3. **Label encoding & unknown attack handling:** Map unseen attack classes in global chronological test windows cleanly to binary `attack = 1` (and `unknown_attack` bucket for open-set evaluation); never leak test class vocabularies into training encoders.
4. **Fixed hyperparameters & provenance:** Lock `idle_timeout_s` (`120s` default; `600s` ablation), `embargo_s` (`300s` default), `seed`, input SHA-256, and `flow_extract_v1` version in versioned YAML experiment configs.

---

## 8. E1–E6 Experimental Protocol Matrix

| Exp | Datasets / Sources | Partition Unit & Client Strategy | Train / Val / Test Policy | Drift / Attack Intervention | Key Metrics | Known Confounders |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- |
| **E1** | CICIoT2023 `MERGED_CSV`, ToN-IoT `train_test_network.csv`, Edge-IIoTset `ML-EdgeIIoT` | Simulated logical gateways (`K=10`); IID vs `Dir(0.5/0.1)` + qty skew | Deduplicated, ID-stripped stratified `70/15/15` (non-temporal benchmarks) | None (baseline heterogeneity) | Macro-F1, PR-AUC, FPR, client-variance | Simulated clients; heavy raw duplication |
| **E2** | ToN-IoT `Processed_Network_dataset` (Protocols A/B/C) | Simulated logical gateways within Train window | Global chronological (`300s` + `ts+dur` embargo) + Protocol C synthetic | Natural abrupt attack emergence + synthetic gradual/recurring | Pre- vs post-drift Macro-F1, binary recall, FPR, recovery rounds | 18-day gap; 295x `src_ip` & 73x `http` shift in Period B |
| **E3** | ToN-IoT `Processed_Network_dataset` (Period A + Period B normal) | Simulated logical gateways; subset benign-shifted vs poisoned | Chronological (`300s` + `ts+dur`); Period B normal for benign-shift stress | Confounded benign shift vs seeded FL poisoning (label-flip/scaling) | Benign false-quarantine rate, poisoning detection TPR/FPR, clean F1 | Period B normal shift is capture-confounded; poisoning is simulated |
| **E4** | CICIoT2023, ToN-IoT, Edge-IIoTset | Simulated logical gateways (`10%–30%` Byzantine fraction) | Same as E1 (`70/15/15`, train-only fit) | Seeded Byzantine attacks (sign-flip, noise, model replacement) | Robust-agg F1 vs `FedAvg`, attack success rate | Simulated FL adversary |
| **E5** | CICIoT2023 + ToN-IoT + Edge-IIoTset (**HOLD** pending ontology) | Cross-environment silos (1 dataset family = 1 silo) | Leave-one-dataset-out / cross-silo transfer | Cross-domain feature/label shift | Binary & coarse-class Macro-F1, domain-gap drop | Heterogeneous feature spaces (flow vs Zeek vs packet headers) |
| **E6** | Manageable verified baselines (`train_test_network`, `ML-EdgeIIoT`, `Merged01`) | Simulated logical gateways (`K=10`) | Fixed seeds across ablations | Component ablations (drift detector, robust agg, privacy) | Wall-clock time/round, bytes sent/round, memory, F1 delta | Hardware-dependent timing (logged in run JSON) |

---

## 9. Limitations, Unresolved Decisions & Final Verdict

- **Unresolved Decisions Before Phase 2 Coding:** (1) Approve `configs/datasets/label_taxonomy.yaml` for E5 coarse label alignment; (2) Decide whether to integrate `flow_extract_v1` into `src/dafidaf/` or use verified ToN-IoT `Processed_Network_dataset` CSVs as primary Phase 2 input; (3) Finalize `K` clients and `Dir(alpha)` grid in `configs/experiments/`.
- **Final Verdict:** **CONDITIONAL** — The Phase 1H temporal split, embargo (`300s` + `ts + duration`), deduplication, and simulated FL partitioning protocol is quantitatively validated and ready for Phase 2 implementation once the above configuration decisions are locked.
