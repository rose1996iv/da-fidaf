# 05 — Temporal Provenance and Concept-Drift Feasibility (DA-FIDAF Phase 1 Part A)

- **Audit Timestamp (UTC):** `2026-11-24T03:20:51Z`
- **Methodological Rule:** Never use row order or filename order as a proxy for time. Temporal concept drift (E2/E3) requires verified capture/event timestamps and chronological provenance.

## 1. Per-Dataset Timestamp Evidence (VERIFIED)

### A. CICIoT2023 — **VERIFIED ABSENT (NOT SUPPORTED FOR E2)**
- **Observed Columns:** 39/40 flow/packet summary features. The only column matching a time-related token is `Time_To_Live` (`63.36`, `64.0`, `110.5`), which is **IPv4 TTL**, not a timestamp, and `IAT` (inter-arrival time delta, not absolute wall-clock time).
- **Verdict:** No event or capture timestamp exists in CICIoT2023 CSVs. **NOT SUPPORTED** for natural temporal concept drift.

### B. ToN-IoT — **VERIFIED PARTIAL (CONDITIONAL)**
- **`Train_Test_datasets/Train_Test_Network_dataset/train_test_network.csv`:** **NO `ts` column** (44 columns; `ts` was stripped during train/test creation). **Cannot support E2 on its own.**
- **`Train_Test_Linux_dataset/Train_Test_Linux_process.csv` & `Train_Test_Windows_dataset/Train_Test_Windows_10.csv`:** **No wall-clock timestamp column** (only OS performance/scheduling counters).
- **`Processed_datasets/Processed_Network_dataset/Network_dataset_1.csv`:** **HAS `ts`** (46 columns) — Unix epoch seconds observed: `1554198358`–`1554198362` (`2019-04-02T09:45:58Z` – `09:46:02Z`, **VERIFIED**).
- **`Processed_datasets/Processed_IoT_dataset/IoT_Fridge.csv` & `Train_Test_IoT_Fridge.csv`:** **HAS `date` and `time`** — observed `31-Mar-19 12:36:52..56` (`Processed`) and `25-Apr-19 19:19:40..55` (`Train_Test`, **VERIFIED**).
- **`SecuityEvents_GroundTruth_datasets/.../GroundTruth_IoT_Fridge.csv`:** **HAS `ts` and `time`** — Unix epoch seconds observed: `1556203753`–`1556205392` (`2019-04-25T14:49:13Z` – `15:16:32Z`, **VERIFIED**).
- **Verdict:** ToN-IoT `Processed_Network_dataset` + `Processed_IoT_dataset` + `SecuityEvents_GroundTruth_datasets` are the **only locally verified candidates with real wall-clock timestamps**, but full multi-file chronological span, timezone consistency (UTC vs local AEST/AEDT in `date`/`time` vs `ts`), and event alignment across all shards remain **UNVERIFIED** (Phase 1B prerequisite).

### C. Edge-IIoTset — **VERIFIED CORRUPTED / INCOMPLETE (HOLD)**
- Direct inspection of `frame.time` across 6 audited CSVs revealed **three distinct formatting/corruption defects**:
  1. `ML-EdgeIIoT-dataset.csv` and `MITM_attack.csv`: `frame.time` contains numeric values `'6.0'` / `'0.0'` (**corrupted — not a timestamp**).
  2. `Normal traffic/Modbus/Modbus.csv`: `frame.time` contains **IPv4 addresses** (`'192.168.0.128'`, `'192.168.0.1'`) — **column shift / corruption**.
  3. `DNN-EdgeIIoT-dataset.csv`, `Port_Scanning_attack.csv`, and `Temperature_and_Humidity.csv`: `frame.time` contains `'2021 11:44:10.081753000'` and `'2021 16:03:29.475073000'` — **missing calendar month and day** (year + time-of-day only, preventing unambiguous multi-day chronological ordering).
- **Verdict:** Edge-IIoTset CSV `frame.time` **cannot be used for temporal ordering or drift claims** (**HOLD**). Authentic capture timestamps exist only inside the 24 raw `.pcap` files (**INFERRED**; PCAP headers were not parsed in Part A).

## 2. Concept-Drift Suitability Summary

- **Natural Temporal Concept Drift (E2):** **HOLD** globally until Phase 1B verifies complete chronological coverage, monotonicity, timezone alignment, and attack-window evolution across ToN-IoT `Processed_Network_dataset` / `Processed_IoT_dataset` shards.
- **Controlled/Synthetic Drift (if adopted later):** Must be explicitly distinguished from natural temporal drift and never misrepresented as real-world chronological drift.
