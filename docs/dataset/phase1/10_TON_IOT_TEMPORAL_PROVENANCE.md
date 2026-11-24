# 10 — ToN-IoT Temporal Provenance Audit (DA-FIDAF Phase 1B)

- **Audit Timestamp (UTC):** `2026-11-24T03:38:32Z`
- **Scope:** Full read-only streaming inspection of all **23** `Processed_Network_dataset/*.csv` files (`22,339,021` rows), all **30** `SecuityEvents_GroundTruth_datasets/**/*.csv` files, and `Train_Test_Network_dataset/train_test_network.csv`.

## 1. Candidate Timestamp Validation Matrix (VERIFIED)

| Dataset Component | Column | Format / Type | Valid Rows | Invalid / Missing | Min UTC | Max UTC | Duplicate `ts` Rows | Ordering (`ooo`) | Provenance Meaning |
| :--- | :--- | :--- | ---: | ---: | :--- | :--- | ---: | ---: | :--- |
| `Processed_Network_dataset` (23 CSVs) | `ts` | Unix epoch seconds (int) | `22,339,021` | `0` / `0` (`0.0%`) | `2019-04-02T09:45:58Z` | `2019-04-29T14:45:56Z` | `21,946,388` (`392,633` unique `ts`) | `21` out-of-order (`0.000094%`) | Zeek/Bro network connection capture start time (UTC) |
| `Train_Test_Network_dataset` (1 CSV) | `None` | Absent (`ts` stripped) | `0` | `0` / `211,043` (`100%`) | `null` | `null` | `null` | `null` | **No timestamp provenance** |
| `GroundTruth_Network_1..18` (18 CSVs) | `ts` | Unix epoch seconds (int) | `17,801,188` (raw; `1M` dup shard) | `0` / `0` | `2019-04-23T12:10:10Z` | `2019-04-29T14:45:29Z` | High (same-second bursts) | Nearly monotonic | Attack-event network capture timestamp (UTC) |
| `GroundTruth_IoT_*` (7 CSVs) | `ts`, `time` | Unix epoch + local `HH:MM:SS` | `405,037` | `0` / `0` | `2019-04-24T03:20:29Z` | `2019-04-29T14:45:29Z` | Moderate | Nearly monotonic | **`time` lags UTC `ts` by `-25,200` s (`UTC-7`/PDT)** |

## 2. Verified Daily Chronology of `Processed_Network_dataset` (22,339,021 Rows)

| UTC Date | Normal | Attack Classes & Exact Row Counts | Temporal Regime |
| :--- | ---: | :--- | :--- |
| `2019-04-02` | `43,377` | *(none)* | Pure normal baseline |
| `2019-04-03` | `121,945` | *(none)* | Pure normal baseline |
| `2019-04-04` | `35,576` | *(none)* | Pure normal baseline |
| **`2019-04-05` – `2019-04-22`** | **`0`** | **`0` (18-day capture gap)** | **Missing / No capture** |
| `2019-04-23` | `22,476` | `scanning`: `3,733,109` | Staged campaign Day 1 |
| `2019-04-24` | `89,324` | `scanning`: `3,407,052`; `dos`: `2,184,823` | Staged campaign Day 2 |
| `2019-04-25` | `81,742` | `dos`: `1,190,505`; `injection`: `452,659`; `ddos`: `3,504,493` | Staged campaign Day 3 |
| `2019-04-26` | `91,576` | `ddos`: `2,660,515`; `password`: `1,169,187` | Staged campaign Day 4 |
| `2019-04-27` | `48,578` | `password`: `549,381`; `xss`: `2,108,944` | Staged campaign Day 5 |
| `2019-04-28` | `231,561` | `ransomware`: `72,805`; `backdoor`: `273,545` | Staged campaign Day 6 |
| `2019-04-29` | `30,225` | `backdoor`: `234,571`; `mitm`: `1,052` | Staged campaign Day 7 |

## 3. Key Temporal Provenance Conclusions (VERIFIED)

1. **High-Integrity Unix Timestamps in `Processed_Network_dataset`:** `100.00%` of `22,339,021` rows carry valid integer Unix epoch timestamps (`0` missing, `0` invalid), chaining contiguously across shards `Network_dataset_1.csv` through `Network_dataset_23.csv` with only `21` minor out-of-order transitions (`0.000094%`).
2. **Staged Campaign Schedule, Not Continuous Organic Drift:** Attacks are introduced sequentially in disjoint 1–2 day windows after an **18-day capture gap** (`Apr 5–22`). Each attack class is non-recurring.
3. **High Same-Second Multiplicity:** `22,339,021` flows map to `392,633` unique seconds (~`56.9` flows/second average; up to `>1,500` flows/second during `scanning` shards `3` and `5`).
4. **Timezone Caution:** In `GroundTruth_IoT_*`, the string `time` column differs from UTC `ts` by `-25,200` seconds (`UTC-7`). All DA-FIDAF pipelines must key strictly on numeric Unix epoch `ts` (UTC).
