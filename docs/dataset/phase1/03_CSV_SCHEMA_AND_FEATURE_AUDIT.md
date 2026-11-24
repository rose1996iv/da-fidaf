# 03 — CSV Schema and Feature Audit (DA-FIDAF Phase 1 Part A)

- **Audit Timestamp (UTC):** `2026-11-24T03:20:51Z`
- **Method:** Streaming Python `csv.reader` inspection across **18 representative CSVs** spanning all 3 dataset families. Files `<= 100 MiB` underwent full streaming row/label counts + 5,000-row quality sampling; larger files underwent bounded 5,000-row sampling without loading into RAM.

## 1. Audited CSV Summary Table (VERIFIED)

| Family | Relative Path | Size (B) | Scan Mode | Rows | Cols | Dups (5k) | Missing / Inf (5k) | SHA-256 |
| :--- | :--- | ---: | :--- | ---: | ---: | ---: | :--- | :--- |
| CICIoT2023 | `CIC_IOT_Dataset2023/MERGED_CSV/Merged01.csv` | `147,115,614` | Sample 5k | `null` | `40` | `26` | `0` / `0` | `8b43d655...792fe` |
| CICIoT2023 | `CIC_IOT_Dataset2023/CSV/Benign_Final/BenignTraffic.pcap.csv` | `75,100,977` | Full | `362,361` | `39` | `0` | `0` / `0` | `f0ee40b6...19ee6` |
| CICIoT2023 | `CIC_IOT_Dataset2023/CSV/DDoS-SYN_Flood/DDoS-SYN_Flood.pcap.csv` | `51,108,638` | Full | `266,024` | `39` | `188` | `0` / `0` | `d91942c5...b9ff3` |
| CICIoT2023 | `CIC_IOT_Dataset2023/CSV/Mirai-greeth_flood/Mirai-greeth_flood.pcap.csv` | `6,743,677` | Full | `33,597` | `39` | `3` | `0` / `0` | `d8b068a4...42eb6` |
| CICIoT2023 | `CIC_IOT_Dataset2023/CSV/DNS_Spoofing/DNS_Spoofing.pcap.csv` | `36,833,637` | Full | `178,898` | `39` | `0` | `0` / `0` | `8658a591...81cc0` |
| ToN-IoT | `IoT Datasets/Train_Test_datasets/Train_Test_Network_dataset/train_test_network.csv` | `29,902,775` | Full | `211,043` | `44` | `287` | `0` / `0` | `26ddc513...e1974` |
| ToN-IoT | `IoT Datasets/Train_Test_datasets/Train_Test_IoT_dataset/Train_Test_IoT_Fridge.csv` | `1,678,744` | Full | `39,944` | `6` | `9` | `0` / `0` | `56377a00...e3149` |
| ToN-IoT | `IoT Datasets/Train_Test_datasets/Train_Test_Linux_dataset/Train_Test_Linux_process.csv` | `4,900,281` | Full | `90,112` | `16` | `2,498` | `0` / `0` | `63a878f9...3f7e` |
| ToN-IoT | `IoT Datasets/Train_Test_datasets/Train_Test_Windows_dataset/Train_Test_Windows_10.csv` | `21,769,739` | Full | `21,104` | `126` | `0` | 11 cols / `0` | `85f08276...2703a8` |
| ToN-IoT | `IoT Datasets/Processed_datasets/Processed_Network_dataset/Network_dataset_1.csv` | `146,725,605` | Sample 5k | `null` | `46` | `0` | `0` / `0` | `37ea5238...c0448` |
| ToN-IoT | `IoT Datasets/Processed_datasets/Processed_IoT_dataset/IoT_Fridge.csv` | `24,965,618` | Full | `587,076` | `6` | `733` | `0` / `0` | `e5c7fd42...36272` |
| ToN-IoT | `IoT Datasets/SecuityEvents_GroundTruth_datasets/SecurityEvents_IoT_datasets/GroundTruth_IoT_Fridge.csv` | `2,599,764` | Full | `63,449` | `4` | `0` | `0` / `0` | `e9c3e2b9...3c1c6` |
| Edge-IIoTset | `Edge_IIoT Dataset/.../Selected dataset for ML and DL/ML-EdgeIIoT-dataset.csv` | `82,184,390` | Full | `157,800` | `63` | `814` | `0` / `0` | `53101fad...4c3c1a` |
| Edge-IIoTset | `Edge_IIoT Dataset/.../Selected dataset for ML and DL/DNN-EdgeIIoT-dataset.csv` | `1,217,413,981` | Sample 5k | `null` | `63` | `0` | `0` / `0` | `null` (`>200 MiB`) |
| Edge-IIoTset | `Edge_IIoT Dataset/.../Attack traffic/MITM_attack.csv` | `329,947` | Full | `1,229` | `63` | `819` | `0` / `0` | `c4fd9f0d...fd498` |
| Edge-IIoTset | `Edge_IIoT Dataset/.../Attack traffic/Port_Scanning_attack.csv` | `7,335,171` | Full | `22,564` | `63` | `0` | `0` / `0` | `26f7f094...793ad` |
| Edge-IIoTset | `Edge_IIoT Dataset/.../Normal traffic/Modbus/Modbus.csv` | `67,899,662` | Full | `159,502` | `63` | `453` | `0` / `15` (`tcp.options`) | `6ae11be7...9c37a` |
| Edge-IIoTset | `Edge_IIoT Dataset/.../Normal traffic/Temperature_and_Humidity/Temperature_and_Humidity.csv` | `922,587,674` | Sample 5k | `null` | `63` | `0` | `0` / `0` | `null` (`>200 MiB`) |

*(Full 64-character SHA-256 digests are recorded in `manifests/dataset_inventory.json`.)*

## 2. Key Schema & Data-Quality Findings (VERIFIED)

1. **CICIoT2023 Schema Split (39 vs. 40 columns):**
   - `MERGED_CSV/Merged01.csv` has **40 columns** (39 numeric flow/packet-summary features + `Label`).
   - Per-class files under `CSV/<Class>/*.pcap.csv` have **39 columns** and **omit the `Label` column** (label exists only in folder/filename).
   - Zero missing/Inf values in audited samples; low-to-moderate exact duplicates (`26/5000` in `Merged01.csv`, `188/5000` in `DDoS-SYN_Flood.pcap.csv`).
2. **ToN-IoT Schema Divergence Between Processed and Train/Test Network CSVs:**
   - `Processed_Network_dataset/Network_dataset_1.csv` has **46 columns** (includes `ts` and `http_referrer`).
   - `train_test_network.csv` has **44 columns** — **`ts` and `http_referrer` were dropped**, and `287/5000` exact duplicates appear in the first 5,000 rows (`29` columns are constant in the first 5,000 rows due to contiguous class/protocol ordering!).
   - `Train_Test_Linux_process.csv` exhibits **50.0% exact duplication** (`2,498 / 5,000` rows) in the sampled prefix.
   - `Train_Test_Windows_10.csv` (126 columns) contains missing values across 11 `Process_IO` / `Process_pct` columns and 25 constant columns in the sample.
3. **Edge-IIoTset Uniform 63-Column Schema with Severe Column-Value Anomalies:**
   - All 6 audited Edge-IIoTset CSVs share the exact same **63-column** packet-dissection schema (`frame.time`, `ip.src_host`, `ip.dst_host`, ARP/ICMP/HTTP/TCP/UDP/DNS/MQTT/ModbusTCP fields, `Attack_label`, `Attack_type`).
   - **VERIFIED DATA QUALITY DEFECTS:**
     - `Modbus.csv`: `frame.time` contains **IPv4 addresses** (`192.168.0.128`, `192.168.0.1`), and `tcp.options` contains **`inf` values** (`15` in the first 5,000 rows).
     - `ML-EdgeIIoT-dataset.csv`: `frame.time` contains `'6.0'` in the sampled prefix; **`814 / 5,000` (16.3%) exact duplicate rows**; `33` constant columns in the sampled prefix.
     - `MITM_attack.csv`: **`819 / 1,229` (66.6%) exact duplicate rows**; `frame.time` contains `'0.0'`/`'6.0'`.
4. **Cross-Dataset Feature Incompatibility (VERIFIED):**
   - CICIoT2023 features are **aggregated flow/window statistics** (`Header_Length`, `Rate`, `Tot sum`, `IAT`, `Variance`).
   - ToN-IoT network features are **Zeek/Bro connection-level logs** (`duration`, `src_bytes`, `dst_bytes`, `conn_state`, `dns_*`, `ssl_*`, `http_*`).
   - Edge-IIoTset features are **Wireshark/TShark packet-level header fields** (`tcp.ack`, `tcp.seq`, `mqtt.topic`, `mbtcp.trans_id`).
   - **Conclusion:** Zero naive column-name merging is scientifically valid across these three corpora.
