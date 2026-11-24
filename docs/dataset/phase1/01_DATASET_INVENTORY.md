# 01 — Dataset Inventory Report (DA-FIDAF Phase 1 Part A)

- **Audit Timestamp (UTC):** `2026-11-24T03:20:51Z`
- **Audit Scope:** Strictly read-only recursive metadata inventory across `CIC_IOT_Dataset2023`, `IoT Datasets` (ToN-IoT), and `Edge_IIoT Dataset` (+ `Edge_IIoT Dataset.zip`) under the configured dataset root.
- **Evidence Standard:** All counts, byte sizes, and timestamps below are **VERIFIED** directly via Python `os.walk` / `Path.stat()`. Reconciled against **HISTORICAL** reports in `_dataset_audit/`.

## 1. Cross-Family Summary (VERIFIED)

| Dataset Family | Relative Root | Total Files | Total Dirs | Total Size | CSV Files | CSV Size | Archives (`.zip`) | Release Completeness |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| **CICIoT2023** | `CIC_IOT_Dataset2023` | `375` | `36` | `21,376,281,949` B (`19.91 GiB`) | `372` | `16.99 GiB` | `2` | **UNVERIFIED** |
| **ToN-IoT** | `IoT Datasets` | `2,662` | `287` | `116,098,831,555` B (`108.13 GiB`) | `800` | `11.37 GiB` | `18` | **HOLD** (2 corrupt 20 GB ZIPs) |
| **Edge-IIoTset** | `Edge_IIoT Dataset` + `.zip` | `53` | `14` | `12,995,420,309` B (`12.10 GiB`) | `26` | `8.42 GiB` | `1` | **UNVERIFIED** |
| **Total** | — | **`3,090`** | **`337`** | **`150,470,533,813` B (`140.14 GiB`)** | **`1,198`** | **`36.78 GiB`** | **`21`** | — |

## 2. Classification Breakdown (Raw vs. Processed vs. Train/Test vs. Ground Truth)

### A. CICIoT2023 (`CIC_IOT_Dataset2023`) — VERIFIED
- **Extensions:** `.csv` (`372`), `.zip` (`2`), `.pdf` (`1`).
- **Classifications:**
  - `archive` (`2`): `CSV.zip` (`1,430,268,604` B, `2026-11-17T17:28:06Z`), `MERGED_CSV.zip` (`1,702,032,816` B, `2026-11-17T17:42:38Z`).
  - `extracted_tabular` (`310`): Per-class CSVs under `CSV/<Attack_or_Benign>/` (34 class subdirectories) + `1` PDF.
  - `processed_merged` (`63`): Pre-merged CSV shards under `MERGED_CSV/Merged01.csv` .. `Merged63.csv`.
- **Reconciliation with Historical Audit:** Matches **HISTORICAL** report `04_DATASET_STATUS_REPORT.md` (which counted 744 CSV schema records including both extracted and in-ZIP CSVs). No raw PCAPs are present locally (**VERIFIED**).

### B. ToN-IoT (`IoT Datasets`) — VERIFIED
- **Extensions:** `.log` (`1,226`), `.csv` (`800`), `.txt` (`554`), `.blg` (`28`), `.zip` (`18`), `.docx` (`11`), `.pdf` (`10`), `.xlsx` (`8`), `.bst` (`6`), `.vsdx` (`1`).
- **Classifications:**
  - `archive` (`18`): `Train_Test_datasets.zip`, `SecuityEvents_GroundTruth_datasets.zip`, `network_data.zip` (**HOLD**), `Raw_datasets/network_data/normal_attack_pcaps.zip` (**HOLD**), `Raw_datasets/telemtry_data.zip`, `Raw_datasets/windows_data.zip`, `Raw_datasets/Linux_data.zip`, `Raw_datasets/network_data/Network_dataset_Bro.zip`, `normal_Bro.zip`, and 9 per-attack Bro ZIPs.
  - `raw` (`1,242`) & `raw_or_per_class` (`1,261`): Zeek/Bro `.log` files, Windows `.blg` performance logs, `.txt` raw telemetry/host logs under `Raw_datasets/`.
  - `processed` (`38`): `Processed_datasets/` (`Processed_Network_dataset/`, `Processed_IoT_dataset/`, Linux/Windows processed CSVs).
  - `train_test_or_selected` (`13`): `Train_Test_datasets/` including `Train_Test_Network_dataset/train_test_network.csv` (`29,902,775` B, `2026-11-15T13:23:00Z`), `Train_Test_IoT_dataset/`, `Train_Test_Linux_dataset/`, and `Train_Test_Windows_dataset/`.
  - `ground_truth` (`30`): `SecuityEvents_GroundTruth_datasets/` (note upstream typo `SecuityEvents`).
  - `metadata_stats` (`60`): `Description_stats_datasets/`.

### C. Edge-IIoTset (`Edge_IIoT Dataset` + `Edge_IIoT Dataset.zip`) — VERIFIED
- **Extensions:** `.csv` (`26`), `.pcap` (`24`), `.zip` (`1`), `.pdf` (`1`), `.txt` (`1`).
- **Classifications:**
  - `archive` (`1`): `Edge_IIoT Dataset.zip` (`1,746,605,436` B, `2026-11-19T04:54:31Z`).
  - `train_test_or_selected` (`2`): `Selected dataset for ML and DL/ML-EdgeIIoT-dataset.csv` (`82,184,390` B, `2022-03-18T09:28:36Z`) and `DNN-EdgeIIoT-dataset.csv` (`1,217,413,981` B, `2022-03-18T09:27:18Z`).
  - `raw` (`24` PCAPs) & `raw_or_per_class` (`24` CSVs): `Attack traffic/` (14 attack types with paired `.pcap` and `.csv`) and `Normal traffic/` (10 sensor subdirectories: `Distance`, `Flame_Sensor`, `Heart_Rate`, `IR_Receiver`, `Modbus`, `phValue`, `Soil_Moisture`, `Sound_Sensor`, `Temperature_and_Humidity`, `Water_Level`).

## 3. Limitations
- Official upstream publisher manifests (CIC, UNSW, IEEE DataPort) have not yet been cross-checked (**UNVERIFIED**).
- Coexisting archived and extracted representations create potential disk redundancy; both are preserved read-only per policy.
