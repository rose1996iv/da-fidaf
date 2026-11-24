# DA-FIDAF Phase 3A — ToN-IoT Dataset Integrity Report

**Audit Mode:** Strictly read-only inspection of local ToN-IoT files under `DAFIDAF_DATA_ROOT` (`I:\IoT`). Zero files modified, extracted, repaired, or downloaded.

---

## 1. Discovered Dataset Inventory

| Dataset Family | Discovered Relative Path under `I:\IoT\IoT Datasets\` | File Count | Size (Bytes) | Status |
| --- | --- | --- | --- | --- |
| **Train-Test Network CSV** | `Train_Test_datasets\Train_Test_Network_dataset\train_test_network.csv` | 1 | `29,902,775` | VERIFIED (Read-Only) |
| **Processed Network Shards** | `Processed_datasets\Processed_Network_dataset\Network_dataset_1.csv` .. `23.csv` | 23 | `51.7 MB` – `165.8 MB` each | VERIFIED (Read-Only) |
| **Ground-Truth Network Shards** | `SecuityEvents_GroundTruth_datasets\SecurityEvents_Network_datasets\GroundTruth_Network_1..18.csv` (note source typo `SecuityEvents`) | 17 unique (shard 16 excluded) | `1,005,205,730` (17 shards) | VERIFIED (Shard 16 duplicate confirmed) |

---

## 2. `train_test_network.csv` Full Integrity Audit

- **Size:** `29,902,775` bytes | **SHA-256:** `26ddc513552de36de6428b2e578efaed2b57504c716dfba847cc0109a64e1974`
- **Dimensions:** `211,043` data rows × `44` columns (`label` and `type` present; **`ts` ABSENT**).
- **Label Distribution (Full File):**
  - Binary: `1` (attack) = `161,043` (`76.31%`), `0` (normal) = `50,000` (`23.69%`).
  - Multi-class `type`: `normal` (`50,000`), `backdoor` (`20,000`), `ddos` (`20,000`), `dos` (`20,000`), `injection` (`20,000`), `password` (`20,000`), `ransomware` (`20,000`), `scanning` (`20,000`), `xss` (`20,000`), `mitm` (`1,043`).
- **CRITICAL DISCOVERY — Strict Class-Grouped Row Ordering:**
  - The first `5,000` rows of `train_test_network.csv` are **100% single-class `backdoor`** (`binary=1: 5,000`, `benign=0: 0`).
  - **Operational Impact for Phase 3:** Never use head-truncated `--max-rows` sampling on `train_test_network.csv`. Any experiment using `train_test_network.csv` must load all `211,043` rows (or use a stratified sampler) to avoid single-class truncation.
- **Adapter Compatibility (`TonIoTNetworkAdapter`, bounded 5,000 rows):**
  - `10` numeric features loaded cleanly (`duration`, `src_bytes`, `dst_bytes`, `missed_bytes`, `src_pkts`, `src_ip_bytes`, `dst_pkts`, `dst_ip_bytes`, `http_request_body_len`, `http_response_body_len`).
  - `has_timestamps = False`, `inf_sanitized = 0`, `dropped_invalid_ts = 0`, `dropped_invalid_label = 0`, `missing = 0` across all 10 features, `exact_duplicates = 3,966 / 5,000` (identical numeric flow vectors).

---

## 3. `Processed_Network_dataset` Bounded Shard Audit

All 23 shards share a `46`-column schema including `ts` (Unix epoch seconds) and `type`. Representative 50,000-row bounded scans:

| Shard | Size (Bytes) | Cols | Sampled Rows | UTC Timestamp Span (Sampled) | Invalid `ts` | Observed `type` Distribution |
| --- | --- | --- | --- | --- | --- | --- |
| `Network_dataset_1.csv` | `146,725,605` | 46 | 50,000 | `2019-04-02T09:45:58Z` .. `2019-04-03T01:35:36Z` | 0 | `normal: 50,000` |
| `Network_dataset_14.csv` | `153,329,384` | 46 | 50,000 | `2019-04-25T19:59:08Z` .. `2019-04-25T20:05:06Z` | 0 | `ddos: 49,992`, `normal: 8` |
| `Network_dataset_15.csv` | `153,194,923` | 46 | 50,000 | `2019-04-25T22:06:21Z` .. `2019-04-25T22:12:51Z` | 0 | `ddos: 49,971`, `normal: 29` |
| `Network_dataset_22.csv` | `153,268,181` | 46 | 50,000 | `2019-04-27T11:06:41Z` .. `2019-04-27T11:16:05Z` | 0 | `xss: 49,395`, `normal: 605` |
| `Network_dataset_23.csv` | `51,705,634` | 46 | 50,000 | `2019-04-28T21:05:32Z` .. `2019-04-28T23:04:44Z` | 0 | `backdoor: 47,778`, `normal: 2,222` |

- `Network_dataset_23.csv` full SHA-256: `e89c54673961c2b260265cdd3f6c50355369f8a80e63c31999df04b0a757f213`.
- **Single-Shard Class Imbalance Warning:** Individual attack shards are heavily attack-dominated (`95.6%` to `99.98%` attack), whereas Shard 1 is `100%` benign. Full Phase 3 chronological E2/E3/E4 runs must use multi-shard chronological windows rather than a single shard prefix.

---

## 4. `GroundTruth_Network_1–18` Provenance Audit

- **Schema (`7` columns):** `['ts', 'src_ip', 'src_port', 'dst_ip', 'dst_port', 'proto', 'type']`.
- **Duplicate Shard 16 Confirmed:** `SHA-256(GroundTruth_Network_15.csv) == SHA-256(GroundTruth_Network_16.csv) == True` (both `58,467,300` bytes).
- **Usable Shards:** `17` unique files (`1–15, 17–18`), total `1,005,205,730` bytes.
