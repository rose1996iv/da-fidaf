# 18 — ToN-IoT `normal_pcaps.zip` Forensic & Integrity Review (DA-FIDAF)

- **Audit Timestamp (UTC):** `2026-11-24T03:51:09Z` – `2026-11-24T03:53:52Z`
- **Target Archive:** `I:\IoT\IoT Datasets\Raw_datasets\network_data\normal_pcaps.zip`
- **Executive Verdict:** **CONDITIONAL** *(Structurally valid Zip64 archive with intact central directory, verified full SHA-256, and valid in-memory PCAPNG headers across 10/15 sampled members; full 15.62 GiB `7z t` per-member CRC verification was deferred due to archive size, and upstream official UNSW checksums remain unverified.)*

---

## 1. Basic File Metadata & Stability (VERIFIED)

| Attribute | Verified Value |
| :--- | :--- |
| **Exact Path** | `I:\IoT\IoT Datasets\Raw_datasets\network_data\normal_pcaps.zip` |
| **Existence** | `True` |
| **Size** | `16,769,348,890` bytes (`15.6177 GiB` / `16.77 GB`) |
| **Created (UTC)** | `2026-11-24T03:44:48Z` |
| **Modified (UTC)** | `2026-11-24T03:44:48Z` |
| **ZIP Magic Bytes (First 16 B)** | `504b03041400080800002013785d0000` (`PK\x03\x04`, Zip64, `Method = Store`) |
| **Full Streaming SHA-256** | `fbefb9c1179be30a0771c646b729324c5723afce642b8994ef28c7337c64878d` (`162.59s`) |
| **Stability During Inspection** | **STABLE** (`size_bytes` and `modified_utc` identical across Snapshot 1 and Snapshot 2) |

---

## 2. ZIP Structural Inspection (VERIFIED)

- **7-Zip Listing Command:** `"C:\Program Files\7-Zip\7z.exe" l -slt "I:\IoT\IoT Datasets\Raw_datasets\network_data\normal_pcaps.zip"`
  - **Exit Code:** `0` (`0.09s`) | **Errors / Warnings:** `0`
  - **Archive Format:** `zip` (`64-bit = +`, `Characteristics = Zip64`, `Method = Store`)
- **Python `zipfile.ZipFile` Central Directory:** `central_dir_ok = True`
- **Archive Structure Summary:**
  - **Entry Count:** `15` files (`0` explicit directory entries; all under prefix `normal_pcaps/`)
  - **Total Compressed / Uncompressed Size:** `16,769,345,992` B / `16,769,345,992` B (`15.6177 GiB`)
  - **Compression Ratio:** `1.0000` (stored uncompressed)
  - **Encrypted Entries:** `0`
  - **Nested Archives:** `0`
  - **Duplicate Member Names:** `0`
  - **Suspicious Paths (`..` traversal / absolute paths):** `0`
- **Full CRC Test (`7z t`):** **Skipped** (`15.62 GiB > 10 GiB` safety threshold to avoid uncontrolled long-running I/O). Because the archive is stored uncompressed and its full SHA-256 completed cleanly (`exit 0`), a bounded `7z t` can be executed later only if full per-member CRC validation is explicitly required before extraction.

---

## 3. PCAP / PCAPNG Inventory & In-Memory Header Verification (VERIFIED)

- **File Extension Counts:** `15` `.pcap` files, `0` `.pcapng` filenames, `0` other file types.
- **CRITICAL FORMAT FINDING (VERIFIED via in-memory 40-byte header read; zero bytes written to disk):**
  - All `10` sampled members (`normal_1.pcap`–`normal_6.pcap`, `normal_10.pcap`–`normal_13.pcap`) begin with magic bytes **`0a0d0d0a`** — proving they are **`PCAPNG` (Section Header Block)** files despite carrying the `.pcap` filename extension.
  - The remaining `5` members (`normal_7`–`normal_9`, `normal_IoT_2`, `normal_IoT_3`) were not header-sampled (**UNVERIFIED** format, **INFERRED** likely PCAPNG).

| Member Path | Compressed / Uncompressed Size (Bytes) | CRC32 | Sampled Header Format |
| :--- | ---: | :--- | :--- |
| `normal_pcaps/normal_1.pcap` | `1,177,084,172` | `60883818` | **PCAPNG** (`0a0d0d0a`) |
| `normal_pcaps/normal_2.pcap` | `1,151,429,180` | `86d365b8` | **PCAPNG** (`0a0d0d0a`) |
| `normal_pcaps/normal_3.pcap` | `1,102,597,380` | `352d9262` | **PCAPNG** (`0a0d0d0a`) |
| `normal_pcaps/normal_4.pcap` | `1,112,341,756` | `be541073` | **PCAPNG** (`0a0d0d0a`) |
| `normal_pcaps/normal_5.pcap` | `1,077,665,172` | `1115d6da` | **PCAPNG** (`0a0d0d0a`) |
| `normal_pcaps/normal_6.pcap` | `1,075,817,348` | `421f80bb` | **PCAPNG** (`0a0d0d0a`) |
| `normal_pcaps/normal_7.pcap` | `1,110,516,324` | `62636594` | Unsampled |
| `normal_pcaps/normal_8.pcap` | `1,262,737,092` | `b4177121` | Unsampled |
| `normal_pcaps/normal_9.pcap` | `1,150,733,220` | `89bfb221` | Unsampled |
| `normal_pcaps/normal_10.pcap` | `1,122,702,904` | `fcfed059` | **PCAPNG** (`0a0d0d0a`) |
| `normal_pcaps/normal_11.pcap` | `1,118,684,220` | `feba7c2a` | **PCAPNG** (`0a0d0d0a`) |
| `normal_pcaps/normal_12.pcap` | `1,119,176,788` | `90a3317d` | **PCAPNG** (`0a0d0d0a`) |
| `normal_pcaps/normal_13.pcap` | `1,065,001,940` | `13274940` | **PCAPNG** (`0a0d0d0a`) |
| `normal_pcaps/normal_IoT_2.pcap` | `1,056,194,560` | `15e9e43e` | Unsampled |
| `normal_pcaps/normal_IoT_3.pcap` | `1,066,663,936` | `2166ec27` | Unsampled |

*(Note: `normal_IoT_1.pcap` is absent from the member list; completeness against the official UNSW release manifest is **UNVERIFIED**.)*

---

## 4. Comparison with Previous Damaged Archive (`normal_attack_pcaps.zip`)

| Attribute | `normal_pcaps.zip` (New) | `normal_attack_pcaps.zip` (Previous HOLD) |
| :--- | :--- | :--- |
| **Size** | `16,769,348,890` B (`15.62 GiB`) | `20,639,112,059` B (`19.22 GiB`) |
| **Modified (UTC)** | `2026-11-24T03:44:48Z` | `2026-11-22T22:55:43Z` |
| **Header Bytes (First 16 B)** | `504b03041400080800002013785d0000` | `504b0304140008080000209e765d0000` |
| **Central Directory / `7z l`** | Valid (`exit 0`, 15 members) | Truncated / Missing (`exit 2`) |
| **SHA-256** | `fbefb9c1179be30a0771c646b729324c5723afce642b8994ef28c7337c64878d` | Skipped (20.64 GB, size-distinct & corrupt) |

**Classification:** **Completely different file** (differs by `3.87 GB`, distinct timestamps, distinct header bytes, valid Zip64 central directory, normal-only naming scope). `normal_attack_pcaps.zip` remains untouched on **HOLD**.

---

## 5. DA-FIDAF Research Suitability & Limitations

- **Normal Traffic Availability:** **PROMISING (CONDITIONAL)** — Provides `15.62 GiB` of structurally readable PCAPNG captures labelled by filename as normal traffic (`normal_1..13`, `normal_IoT_2..3`).
- **Packet-to-Flow Conversion Required:** **YES** — Raw PCAPNG captures require deterministic flow extraction (e.g., Zeek/Bro matching ToN-IoT `Processed_Network_dataset` 44/46-feature semantics) before tabular ML/FL modeling. Tooling must explicitly support **PCAPNG** (`0a0d0d0a`).
- **Timestamps, Gateway IDs & Ground-Truth Alignment:** **UNVERIFIED** — Packet-level capture timestamps, IP/MAC topology, whether traffic is strictly attack-free, and temporal overlap with `Processed_Network_dataset` (`Apr 2–4` vs `Apr 23–29`) cannot be asserted without bounded PCAPNG block/packet-header inspection.
- **Limitations:** Full `7z t` per-member CRC check not yet run; upstream UNSW release manifest/SHA-256 not yet reconciled; `normal_IoT_1.pcap` absent.

---

## 6. Recommended Next Step

1. Keep `normal_pcaps.zip` read-only and **do not update `manifests/dataset_inventory.json`** until you decide whether to run a scheduled `7z t` CRC check and/or bounded PCAPNG `Interface Description Block` + first/last `Enhanced Packet Block` timestamp audit (in-memory, no extraction) to confirm exact capture dates and alignment with Period A (`Apr 2–4`).
2. Retain `normal_attack_pcaps.zip` and `network_data.zip` on **HOLD**.
