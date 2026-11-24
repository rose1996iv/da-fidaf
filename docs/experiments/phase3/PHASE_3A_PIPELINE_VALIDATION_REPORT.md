# DA-FIDAF Phase 3A — Real-Data Pipeline Validation Report

## 1. End-to-End Pipeline Verification Scope

Validated the full Phase 2.2 remediated pipeline strictly on real ToN-IoT records (`Network_dataset_23.csv`, bounded `15,000` rows, `allowed_root = I:\IoT`):

`TonIoTNetworkAdapter` -> `Schema Validation` -> `chronological_split` (70/15/15 + 300s embargo + active-flow exclusion) -> `TrainOnlyPreprocessor` -> `partition_fl_clients` (`sim_gw_01..06`).

---

## 2. Live CLI Adapter Validation (`dafidaf.orchestration.cli validate-dataset`)

| Target CSV | Exit Code | Rows Loaded | Features | `has_timestamps` | `inf_sanitized` | `dropped_invalid_ts` | `dropped_invalid_label` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `train_test_network.csv` (`--max-rows 500`) | `0` | 500 | 10 | `false` | 0 | 0 | 0 |
| `Network_dataset_23.csv` (`--max-rows 500`) | `0` | 500 | 10 | `true` | 0 | 0 | 0 |

- Path-traversal containment (`allowed_root = DAFIDAF_DATA_ROOT`) enforced automatically by CLI.
- Zero silent fallback to synthetic data occurred.

---

## 3. Temporal Split, Leakage Prevention & Preprocessing Isolation

Tested on `Network_dataset_23.csv` (`15,000` rows; SHA-256 `e89c54673961c2b260265cdd3f6c50355369f8a80e63c31999df04b0a757f213`; timestamps `1556485532.0` .. `1556487686.0`, span `2,154.0s`):

| Verification Check | Observed Result | Status |
| --- | --- | --- |
| Split sizes (`70/15/15`, `embargo=300s`, `exclude_active_end_time=True`) | `train=10,503`, `val=150`, `test=173` (`discarded_embargo=4,174`, `discarded_active_endtime=0`) | **PASS** (note high embargo discard rate on short 36-min window) |
| Causal gap Train -> Val | `300.0s` (`>= 300.0s`) | **PASS** |
| Causal gap Val -> Test | `300.0s` (`>= 300.0s`) | **PASS** |
| `TrainOnlyPreprocessor` state immutability | `pre.state` identical before and after `transform(x_val)` and `transform(x_test)` | **PASS** |
| Client partition reproducibility (`seed=42`, `label_skew`) | Exact index-for-index match across repeated calls | **PASS** |
| Simulated gateway disclosure | `partition_type == "simulated_logical_gateway"`, all IDs prefixed `sim_gw_` | **PASS** |
| No Val/Test contamination in FL clients | `max(train_ts) < split.val_start_ts` enforced by `partition_fl_clients` | **PASS** |

---

## 4. Discovered Real-Data Pipeline Constraints for Phase 3

1. **Short-Window Embargo Attrition:** On a 36-minute (`2,154s`) prefix of `Network_dataset_23.csv`, two 300s embargoes discard `4,174` rows (`27.8%`), leaving only `150` Val and `173` Test rows (with only `3` benign Test rows). Full Phase 3 chronological runs must span multi-hour / multi-shard windows so Val and Test contain sufficient benign and attack support.
2. **Class-Grouped `train_test_network.csv`:** Head-truncating `train_test_network.csv` via `--max-rows` yields 100% `backdoor` rows. Full Phase 3 E1/E4 runs on `train_test_network.csv` must load the complete `211,043` rows.
3. **High Feature-Vector Duplication:** `exact_duplicates` is high (`3,966/5,000` in `train_test_network.csv`, `4,258/5,000` in `Network_dataset_23.csv`) due to identical 10-feature numeric signatures across flows; `deduplicate_event_flows` keys on `(stream_id, ts, feature_hash)` to preserve legitimate recurring flows at distinct timestamps while suppressing exact event duplicates.
