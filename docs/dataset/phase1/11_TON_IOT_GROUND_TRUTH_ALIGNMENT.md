# 11 — ToN-IoT Ground-Truth Alignment Audit (DA-FIDAF Phase 1B)

- **Audit Timestamp (UTC):** `2026-11-24T03:38:32Z`
- **Scope:** Full streaming inspection of all **30** CSVs under `SecuityEvents_GroundTruth_datasets/` cross-checked against the `392,633` unique integer timestamps of `Processed_Network_dataset`.

## 1. Ground-Truth Inventory & Timestamp Overlap (VERIFIED)

| Ground-Truth Sub-Corpus | Files | Total Rows | Schema | UTC Range | Exact `ts` Overlap with `Processed_Network_dataset` |
| :--- | ---: | ---: | :--- | :--- | :--- |
| `SecurityEvents_Network_datasets` (`GroundTruth_Network_1..18`) | `18` | `17,801,188` *(1M dup)* | `['ts', 'src_ip', 'src_port', 'dst_ip', 'dst_port', 'proto', 'type']` | `2019-04-23T12:10:10Z` – `2019-04-29T14:45:29Z` | **`100.0%`** across all 18 files |
| `SecurityEvents_IoT_datasets` (7 sensor files) | `7` | `405,037` | `['ts', 'data', 'time', 'type']` | `2019-04-24T03:20:29Z` – `2019-04-29T14:45:29Z` | **`99.56% – 100.0%`** |
| `SecurityEvents_Linux_datasets` (disk/mem/proc) | `3` | `813,624` | `['ts', 'PID', 'type']` | `2019-04-23T13:04:19Z` – `2019-04-29T14:45:29Z` | **`99.68% – 100.0%`** |
| `SecurityEvents_Windows_datasets` (Win7/Win10) | `2` | `17,084` | `['ts', 'type']` | `2019-04-23T13:16:26Z` – `2019-04-29T14:33:31Z` | **`98.61% – 100.0%`** |

## 2. Critical Verified Finding: Bit-for-Bit Duplicate Ground-Truth Shard

- **`GroundTruth_Network_15.csv`** (`1,000,000` rows, `2019-04-27T00:06:17Z..07:26:35Z`):
  - SHA-256: `d1d4cb491cb6edda3523f7424d24ea1afd4496a933e60b3ec357286f7f0f542f`
- **`GroundTruth_Network_16.csv`** (`1,000,000` rows, `2019-04-27T00:06:17Z..07:26:35Z`):
  - SHA-256: `d1d4cb491cb6edda3523f7424d24ea1afd4496a933e60b3ec357286f7f0f542f`
- **Result (VERIFIED):** `GroundTruth_Network_15.csv` and `GroundTruth_Network_16.csv` are **exact byte-for-byte duplicates** (`1,000,000` duplicated ground-truth rows). Any downstream audit or join must deduplicate by shard SHA-256 before counting events.

## 3. Alignment Feasibility & Leakage Assessment

1. **Network Ground-Truth Join Key (VERIFIED):** `GroundTruth_Network_*` shares the exact 6-tuple `['ts', 'src_ip', 'src_port', 'dst_ip', 'dst_port', 'proto']` plus `type` with `Processed_Network_dataset`. Joining on `ts` alone is **ambiguous** due to ~`56.9` flows/second average multiplicity; full 6-tuple matching is required.
2. **No Extra Labels Needed — Direct Leakage Warning (VERIFIED):** `Processed_Network_dataset` already carries `label` and `type`. Using `GroundTruth_Network_*` columns (or counts of matching ground-truth events) as model input features would introduce **direct target leakage** and is strictly prohibited.
3. **Cross-Source Event Boundaries (VERIFIED):** Ground-truth timestamps span `2019-04-23`–`2019-04-29` only (matching the attack campaign window) and contain **zero** records during the `2019-04-02`–`2019-04-04` pure normal baseline.
4. **IoT/Host-to-Network Alignment:** `GroundTruth_IoT_*`, `GroundTruth_Linux_*`, and `GroundTruth_Windows_*` lack network 5-tuples (`src_ip`/`dst_ip`/ports); they align with network traffic only at coarse second-level `ts` windows (not 1-to-1 flow attribution).
