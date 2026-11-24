# 07 — Data Leakage and Preprocessing Risk Audit (DA-FIDAF Phase 1 Part A)

- **Audit Timestamp (UTC):** `2026-11-24T03:20:51Z`
- **Methodological Rule:** Fit all scalers, imputers, encoders, and feature selectors **strictly on training partitions**. Never alter original dataset files or pre-existing splits.

## 1. Verified Leakage & Data-Quality Risks

| Risk Category | Severity | Verified Evidence | Mandatory Mitigation |
| :--- | :---: | :--- | :--- |
| **Identifier / IP Memorization Leakage** | **CRITICAL** | `train_test_network.csv` exposes `src_ip`, `dst_ip`, `src_port`, `dst_port` (only `3` unique `src_ip` in first 5k rows); `ML-EdgeIIoT-dataset.csv` exposes `ip.src_host`, `ip.dst_host`, `arp.*`, `tcp.srcport`, `tcp.dstport` (`7` unique `ip.src_host` in first 5k rows); `MITM_attack.csv` has `1` constant `ip.dst_host`. | **Drop all IP, MAC, ARP address, ephemeral port, PID, and raw host identifier columns** from model input features before training (retain only in external audit/split metadata if needed for group-aware splitting). |
| **Exact Duplicate Row Leakage** | **CRITICAL** | **VERIFIED** exact duplicates in bounded samples: `Train_Test_Linux_process.csv` (`2,498 / 5,000` = **50.0%**), `MITM_attack.csv` (`819 / 1,229` = **66.6%**), `ML-EdgeIIoT-dataset.csv` (`814 / 5,000` = **16.3%**), `IoT_Fridge.csv` (`733 / 5,000` = **14.7%**), `Modbus.csv` (`453 / 5,000` = **9.1%**), `train_test_network.csv` (`287 / 5,000` = **5.7%**), `DDoS-SYN_Flood.pcap.csv` (`188 / 5,000` = **3.8%**). | Deduplicate **before** train/val/test and FL client splitting (in a derived processed copy), or enforce group-disjoint splits so identical records never straddle train and test. |
| **Coexisting Redundant Representations** | **HIGH** | CICIoT2023 has both `CSV/` (per-class) and `MERGED_CSV/` (merged); ToN-IoT has `Processed_datasets/` and `Train_Test_datasets/`; Edge-IIoTset has `Attack/Normal traffic/` and `Selected dataset for ML and DL/`. | Never mix records from `Processed_*` and `Train_Test_*` or `CSV/` and `MERGED_CSV/` in the same experiment; pin exact input file paths and SHA-256 digests per experiment config. |
| **Corrupted / Shifted Timestamp & Inf Values** | **HIGH** | Edge-IIoTset `Modbus.csv` has IP addresses in `frame.time` and `15` `inf` values in `tcp.options`; `ML-EdgeIIoT-dataset.csv` has `'6.0'` in `frame.time`. | Drop `frame.time` from Edge-IIoTset ML features; explicitly sanitize `+/-inf` and missing values (`Train_Test_Windows_10.csv` has missing values across 11 columns) using train-only imputer statistics. |
| **Contiguous Class Ordering** | **HIGH** | In `train_test_network.csv` (`29` constant cols in first 5k rows), `Network_dataset_1.csv` (`5,000/5,000` normal), and `DNN-EdgeIIoT-dataset.csv` (`5,000/5,000` normal), rows are block-ordered by class/capture. | Never take prefix slices as representative samples or naive unstratified splits; use deterministic seeded stratified or chronological-block splits. |
| **Target / Label-Derived Feature Leakage** | **MEDIUM** | ToN-IoT and Edge-IIoTset each include **both** binary (`label` / `Attack_label`) and multi-class (`type` / `Attack_type`) columns in the same CSV. | Explicitly drop the complementary target column (`label` when predicting `type`, and vice versa) inside the validated data loader. |

## 2. Train-Only Preprocessing Contract

Every future DA-FIDAF preprocessing pipeline (`src/dafidaf/preprocessing/`) must enforce:
1. **Split first** (after exact deduplication on feature vectors, using fixed random seeds or verified temporal cutpoints).
2. **Fit strictly on training split (or per-client local training data in FL):** `StandardScaler` / `RobustScaler`, `SimpleImputer`, categorical encoders (`OneHotEncoder` / `OrdinalEncoder` with unknown-category handling), and variance/feature selectors.
3. **Transform validation and test splits** using frozen training parameters only.
4. **Never write back** to `I:\IoT`; store derived artifacts under a versioned derived directory referencing input SHA-256 hashes.
