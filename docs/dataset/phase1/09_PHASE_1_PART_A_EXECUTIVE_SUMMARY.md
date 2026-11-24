# 09 — Phase 1 Part A Executive Summary (DA-FIDAF)

- **Audit Timestamp (UTC):** `2026-11-24T03:20:51Z`
- **Overall Phase 1 Part A Status:** **COMPLETED (Read-Only Evidence Audit)**
- **Machine-Readable Manifest:** `manifests/dataset_inventory.json`

## 1. Key Verified Findings

1. **Corpus Scale (VERIFIED):** `3,090` files (`140.14 GiB`) across three IoT cybersecurity families:
   - **CICIoT2023:** `375` files (`19.91 GiB`), `372` CSVs, `2` intact ZIPs (`CSV.zip`, `MERGED_CSV.zip`).
   - **ToN-IoT:** `2,662` files (`108.13 GiB`), `800` CSVs, `18` ZIPs (`16` intact, **`2` truncated/HOLD**).
   - **Edge-IIoTset:** `53` files (`12.10 GiB`), `26` CSVs, `24` PCAPs, `1` intact ZIP (`Edge_IIoT Dataset.zip`).
2. **Archive Integrity (VERIFIED):**
   - `19 / 21` archives passed non-extracting inspection (`7z` exit `0` + Python `zipfile` central-directory OK). Full `7z t` CRC checks and actual SHA-256 digests were computed for feasible archives (`<= 500 MiB` CRC / `<= 200 MiB` SHA-256).
   - **`2 / 21` archives remain on HOLD:** `IoT Datasets/network_data.zip` (`20.25 GB`) and `IoT Datasets/Raw_datasets/network_data/normal_attack_pcaps.zip` (`20.64 GB`) both fail with missing central directory / `Unexpected end of archive` (`7z` exit `2`).
3. **Critical Schema, Quality & Temporal Discoveries (VERIFIED):**
   - **CICIoT2023:** `MERGED_CSV` has `40` cols (with `Label`); per-class `CSV/` files have `39` cols (no `Label` column). **Zero wall-clock timestamps** and **zero gateway/device IDs**.
   - **ToN-IoT:** `train_test_network.csv` (`211,043` rows, `44` cols, SHA-256 verified) **dropped `ts`**; whereas `Processed_Network_dataset/Network_dataset_1.csv` (`46` cols) **retains `ts`** (Unix epoch `2019-04-02`). `Train_Test_Linux_process.csv` has **50% exact duplicates** in its first 5,000 rows.
   - **Edge-IIoTset:** `ML-EdgeIIoT-dataset.csv` (`157,800` rows, `63` cols, SHA-256 verified) has **16.3% duplicates** in its first 5,000 rows and corrupted `frame.time` (`'6.0'`). `Modbus.csv` has **IP addresses in `frame.time`** and `inf` in `tcp.options`. `DNN-EdgeIIoT-dataset.csv` has `frame.time` **missing month and day** (`2021 11:44:10...`).
   - **Gateway IDs:** **None** of the three datasets contain genuine gateway identifiers; FL client partitions must be explicitly declared as **simulated logical gateways**.
4. **Historical Audit Reconciliation:** Findings align with and extend the 8 **HISTORICAL** reports in `I:\IoT\_dataset_audit\` by adding actual SHA-256 digests, verified full-file row/class counts, and newly discovered column-corruption defects in Edge-IIoTset `frame.time` / `tcp.options` and ToN-IoT `ts` omission in `train_test_network.csv`.

## 2. Dataset Readiness & Critical Blockers

- **Ready for Controlled Baseline Preprocessing (after deduplication & ID stripping):** CICIoT2023 `MERGED_CSV`, ToN-IoT `train_test_network.csv`, Edge-IIoTset `ML-EdgeIIoT-dataset.csv`.
- **Critical Blockers:**
  1. Two truncated 20 GB ToN-IoT network archives (**HOLD**).
  2. Temporal provenance gap across CICIoT2023 (absent) and Edge-IIoTset CSVs (corrupted/incomplete) -> blocks E2/E3 until ToN-IoT `Processed_*` chronology is fully audited in Phase 1B.
  3. Cross-dataset schema incompatibility -> blocks E5 until semantic feature & label contracts are defined.

## 3. Recommended Next Actions (Phase 1 Part B)

1. **Temporal Alignment Audit (Phase 1B):** Stream-verify `min(ts)`/`max(ts)`, timezone alignment, and class-vs-time evolution across all ToN-IoT `Processed_Network_dataset` and `Processed_IoT_dataset` shards + `SecuityEvents_GroundTruth_datasets`.
2. **Official Manifest Reconciliation:** Cross-check local archive sizes/hashes against official CIC, UNSW, and IEEE DataPort release manifests (no downloads until reconciled).
3. **Author Versioned Contracts:** Define `configs/datasets/label_taxonomy.yaml` and per-dataset feature-drop lists (identifiers, corrupted `frame.time`, complementary targets) before any Phase 2 preprocessing begins.
