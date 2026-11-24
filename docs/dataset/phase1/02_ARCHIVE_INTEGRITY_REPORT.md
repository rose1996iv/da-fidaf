# 02 — Archive Integrity Report (DA-FIDAF Phase 1 Part A)

- **Audit Timestamp (UTC):** `2026-11-24T03:20:51Z`
- **Tools Used:** `7-Zip 26.06 (x64)` (non-extracting `7z t` for archives `<= 500 MiB`; non-extracting `7z l` for intact archives `> 500 MiB`; `7z l -slt` verified in Stage 8 for damaged archives) + Python `3.12.10` `zipfile.ZipFile` central-directory inspection + `hashlib.sha256` (`<= 200 MiB` threshold).
- **Safety Guarantee:** Zero archives were extracted, repaired, renamed, overwritten, or redownloaded.

## 1. Archive Integrity Matrix (21 Archives — VERIFIED)

| Family | Relative Path | Size (Bytes) | `zipfile` CD | Members | 7-Zip Command | Exit | SHA-256 Status | Status |
| :--- | :--- | ---: | :---: | ---: | :--- | :-: | :--- | :---: |
| CICIoT2023 | `CIC_IOT_Dataset2023/CSV.zip` | `1,430,268,604` | OK | `345` | `7z l` | `0` | Skipped (`>200 MiB`) | **VERIFIED** (CD) |
| CICIoT2023 | `CIC_IOT_Dataset2023/MERGED_CSV.zip` | `1,702,032,816` | OK | `64` | `7z l` | `0` | Skipped (`>200 MiB`) | **VERIFIED** (CD) |
| ToN-IoT | `IoT Datasets/Train_Test_datasets.zip` | `89,920,530` | OK | `13` | `7z t` | `0` | **Calculated** | **VERIFIED** (CRC+SHA) |
| ToN-IoT | `IoT Datasets/SecuityEvents_GroundTruth_datasets.zip` | `1,100,052,492` | OK | `30` | `7z l` | `0` | Skipped (`>200 MiB`) | **VERIFIED** (CD) |
| ToN-IoT | `IoT Datasets/Raw_datasets/telemtry_data.zip` | `609,529,266` | OK | `168` | `7z l` | `0` | Skipped (`>200 MiB`) | **VERIFIED** (CD) |
| ToN-IoT | `IoT Datasets/Raw_datasets/windows_data.zip` | `2,699,360,346` | OK | `56` | `7z l` | `0` | Skipped (`>200 MiB`) | **VERIFIED** (CD) |
| ToN-IoT | `IoT Datasets/Raw_datasets/Linux_data.zip` | `8,291,849,575` | OK | `325` | `7z l` | `0` | Skipped (`>200 MiB`) | **VERIFIED** (CD) |
| ToN-IoT | `IoT Datasets/Raw_datasets/network_data/Network_dataset_Bro.zip` | `9,395,263,700` | OK | `928` | `7z l` | `0` | Skipped (`>200 MiB`) | **VERIFIED** (CD) |
| ToN-IoT | `IoT Datasets/Raw_datasets/network_data/normal_Bro.zip` | `57,727,497` | OK | `190` | `7z t` | `0` | **Calculated** | **VERIFIED** (CRC+SHA) |
| ToN-IoT | `.../normal_attack_Bro/normal_backdoor.zip` | `169,397,566` | OK | `19` | `7z t` | `0` | **Calculated** | **VERIFIED** (CRC+SHA) |
| ToN-IoT | `.../normal_attack_Bro/normal_runsomware.zip` | `66,054,162` | OK | `19` | `7z t` | `0` | **Calculated** | **VERIFIED** (CRC+SHA) |
| ToN-IoT | `.../normal_attack_Bro/normal_injection.zip` | `502,321,456` | OK | `62` | `7z t` | `0` | Skipped (`>200 MiB`) | **VERIFIED** (CRC) |
| ToN-IoT | `.../normal_attack_Bro/normal_DoS.zip` | `806,745,013` | OK | `75` | `7z l` | `0` | Skipped (`>200 MiB`) | **VERIFIED** (CD) |
| ToN-IoT | `.../normal_attack_Bro/normal_MITM.zip` | `1,059,642,347` | OK | `64` | `7z l` | `0` | Skipped (`>200 MiB`) | **VERIFIED** (CD) |
| ToN-IoT | `.../normal_attack_Bro/normal_password.zip` | `1,271,199,596` | OK | `72` | `7z l` | `0` | Skipped (`>200 MiB`) | **VERIFIED** (CD) |
| ToN-IoT | `.../normal_attack_Bro/normal_scanning.zip` | `1,328,508,853` | OK | `160` | `7z l` | `0` | Skipped (`>200 MiB`) | **VERIFIED** (CD) |
| ToN-IoT | `.../normal_attack_Bro/normal_DDoS.zip` | `1,846,775,243` | OK | `146` | `7z l` | `0` | Skipped (`>200 MiB`) | **VERIFIED** (CD) |
| ToN-IoT | `.../normal_attack_Bro/normal_XSS.zip` | `2,286,796,257` | OK | `121` | `7z l` | `0` | Skipped (`>200 MiB`) | **VERIFIED** (CD) |
| ToN-IoT | `IoT Datasets/network_data.zip` | `20,251,216,829` | **FAIL** | `null` | `7z l -slt` | `2` | Skipped (**HOLD**) | **HOLD** |
| ToN-IoT | `IoT Datasets/Raw_datasets/network_data/normal_attack_pcaps.zip` | `20,639,112,059` | **FAIL** | `null` | `7z l -slt` | `2` | Skipped (**HOLD**) | **HOLD** |
| Edge-IIoTset | `Edge_IIoT Dataset.zip` | `1,746,605,436` | OK | `52` | `7z l` | `0` | Skipped (`>200 MiB`) | **VERIFIED** (CD) |

## 2. Calculated Archive SHA-256 Checksums (VERIFIED)

| Relative Path | SHA-256 |
| :--- | :--- |
| `IoT Datasets/Train_Test_datasets.zip` | `18714adad9027a8e8155829f300b5c8e84ddb2bb5f54c09d84fd0a095c6951f6` |
| `IoT Datasets/Raw_datasets/network_data/normal_Bro.zip` | `8a7fa5ec159934740a520c2226adbe1ef49e08d1a363bcad88001f85b21ec159` |
| `.../normal_attack_Bro/normal_backdoor.zip` | `672e0d77cb6e474e0e4ca5e7b208635ef0309ea54d291a486e6b71cc1caeb7fd` |
| `.../normal_attack_Bro/normal_runsomware.zip` | `8b470b5ced3e7ecced25722073b670c5cbd90a62f54be2c4dcd2567f9027d7e9` |

*(No SHA-256 values were fabricated for archives exceeding the 200 MiB threshold; those are explicitly recorded as `null` in `manifests/dataset_inventory.json`.)*

## 3. Unreadable / HOLD Archives (VERIFIED)

1. **`IoT Datasets/network_data.zip`** (`20,251,216,829` B, `18.86 GiB`) — Python `zipfile.ZipFile` failed with `BadZipFile: File is not a zip file`; `7z l -slt` exited with code `2` (`ERRORS: Unexpected end of archive`, `Characteristics = Local`).
2. **`IoT Datasets/Raw_datasets/network_data/normal_attack_pcaps.zip`** (`20,639,112,059` B, `19.22 GiB`) — Python `zipfile.ZipFile` failed with `BadZipFile: File is not a zip file`; `7z l -slt` exited with code `2` (`ERRORS: Unexpected end of archive`, `Characteristics = Local`).

**Disposition:** Both archives remain strictly on **HOLD** and must be excluded from automated pipelines until officially reacquired or formally excluded from scope. Note that `Raw_datasets/network_data/Network_dataset_Bro.zip` (`9.40 GB`, `928` members) and its per-attack Bro ZIPs **did** pass central-directory inspection (**VERIFIED**).
