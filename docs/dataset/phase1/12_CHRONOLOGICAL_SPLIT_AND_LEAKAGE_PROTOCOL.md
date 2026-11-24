# 12 — Chronological Split and Leakage-Free Protocol (DA-FIDAF Phase 1B)

- **Audit Timestamp (UTC):** `2026-11-24T03:38:32Z`
- **Scope:** Design specification only (no actual experiment splits or derived files created in Phase 1B).

## 1. Why Naive Splits Fail on ToN-IoT (VERIFIED)

1. **`train_test_network.csv` Cannot Support Chronological Splits:** `ts` is absent (`100%` missing).
2. **Global Chronological Split Yields Zero-Shot Unseen Attacks:** Because attack classes occur in disjoint 1–2 day windows (`scanning` Apr 23–24, `dos` Apr 24–25, `injection` Apr 25, `ddos` Apr 25–26, `password` Apr 26–27, `xss` Apr 27, `ransomware` Apr 28, `backdoor` Apr 28–29, `mitm` Apr 29), a single global time cutoff separates unseen attack classes into Test.
3. **Shard Boundary Overlap:** Adjacent `Processed_Network_dataset` shards share identical boundary timestamps (e.g., Shard 1 ends and Shard 2 begins at `2019-04-23T13:23:00Z`). Splitting by shard index without boundary guards leaks same-second bursts.

## 2. Defensible Chronological Split Protocols

### Protocol A — Global Chronological Novel-Attack Drift Split (For E2 Binary / Continual Adaptation)
- **Source:** `Processed_Network_dataset` (`Network_dataset_1..23`), stable-sorted by `ts` (resolving the `21` minor out-of-order rows).
- **Pre-split Hygiene:** Exact feature-level deduplication within identical `ts` windows; drop `src_ip`, `dst_ip`, `src_port`, `dst_port`, and complementary target column.
- **Proposed Time Boundaries (UTC):**
  - **Baseline / Initial Train:** `2019-04-02T09:45:58Z` – `2019-04-24T23:59:59Z` (`normal` + `scanning` + early `dos`).
  - **Embargo Buffer:** Exclude exact boundary second(s) between adjacent splits (minimum `60` seconds gap).
  - **Validation / Adaptation Window 1:** `2019-04-25T00:01:00Z` – `2019-04-26T23:59:59Z` (`normal` + `dos` + `injection` + `ddos` + `password`).
  - **Test / Drift Window 2 (Abrupt Unseen Attacks):** `2019-04-27T00:01:00Z` – `2019-04-29T14:45:56Z` (`normal` + `password` + `xss` + `ransomware` + `backdoor` + `mitm`).
- **Evaluation:** Binary intrusion detection (`label`: `0` vs `1`) and continual drift adaptation metrics (never claiming closed-set multi-class accuracy on unseen classes).

### Protocol B — Per-Class Chronological Split (For Closed-Set Multi-Class Supervised Evaluation)
- **Source:** `Processed_Network_dataset` (deduplicated, identifier-stripped).
- **Method:** Within **each** of the 10 classes (`normal` + 9 attacks), sort strictly by `ts` and partition into chronological `70% Train / 15% Val / 15% Test` segments, enforcing **strict timestamp disjointness** (`max(ts_train) < min(ts_val)` and `max(ts_val) < min(ts_test)`) so no same-second burst straddles a boundary.
- **Limitation:** Must be explicitly documented as *per-class chronological* (not global future forecasting), because global calendar windows are class-disjoint.

## 3. Mandatory Leakage Controls (All Protocols)
- **Zero future-to-past leakage:** Scalers, imputers, encoders, and feature selectors fit **exclusively on Train** (or per-client local Train in FL).
- **Zero ground-truth leakage:** `SecuityEvents_GroundTruth_datasets` is used solely for external provenance verification, never joined as input features.
- **Deterministic sampling:** Because `Processed_Network_dataset` has `22.34M` rows, any downsampling for manageable FL experiments must be stratified by `(time_bucket, class)` with explicit logged random seeds (`seed` recorded in `configs/experiments/*.yaml`).
