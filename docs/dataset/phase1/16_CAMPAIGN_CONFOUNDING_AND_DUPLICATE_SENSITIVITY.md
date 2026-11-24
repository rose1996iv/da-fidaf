# 16 — Campaign Confounding and Duplicate Sensitivity Audit (DA-FIDAF Phase 1C)

- **Audit Timestamp (UTC):** `2026-11-24T03:46:13Z`
- **Core Question:** Can the observed Period A vs. Period B normal-traffic shift be attributed purely to benign environmental evolution, or is it confounded by capture/campaign conditions and duplication?

## 1. Capture & Campaign Confounding Evidence (VERIFIED)

| Confounding Dimension | Period A (`Apr 2–4`) | Period B (`Apr 23–29`) | Overlap / Change | Confounding Impact |
| :--- | ---: | ---: | :--- | :--- |
| **Unique `src_ip`** | `79` | `23,298` | Only `17` shared (**295x explosion**) | **SEVERE** — source host population changed drastically |
| **Unique `dst_ip`** | `879` | `5,655` | `454` shared (**6.4x increase**) | **HIGH** — destination topology expanded |
| **`service == http`** | `279` (`0.14%`) | `61,032` (`10.25%`) | **73x increase in share** | **SEVERE** — HTTP traffic surged during campaign days |
| **`service == '-'` (unspecified)** | `148,525` (`73.93%`) | `363,255` (`61.00%`) | `-12.93` percentage points | **MODERATE** |
| **`proto == icmp`** | `6,871` (`3.42%`) | `6,211` (`1.04%`) | `-2.38` percentage points | **MODERATE** (`tcp` `56.6%->57.6%`, `udp` `40.0%->41.4%`) |
| **18-Day Capture Gap** | Ends `Apr 4` | Starts `Apr 23` | `18` days missing (`0` rows) | **HIGH** — discontinuous testbed state |

**Confounding Verdict (VERIFIED):** The available ToN-IoT data **cannot** separate pure benign environmental drift from testbed/capture-composition and campaign-context confounding. The 295x jump in unique `src_ip` (`79` -> `23,298` with only `17` shared) and 73x jump in `http` service share prove that Period B normal traffic comes from a substantially altered host/service mix during active attack campaigns.

## 2. Duplicate & Ground-Truth Alignment Sensitivity (VERIFIED)

- **Exact Feature-Row Duplication:**
  - Period A: `200,898` -> `27,441` unique feature rows (**86.3% repetition**).
  - Period B: `595,482` -> `272,165` unique feature rows (**54.3% repetition**).
- **Sensitivity of Drift Metrics to Deduplication:**
  - **Robust shifts (persist or grow after dedup):** `src_pkts` (`PSI 1.567 -> 1.617`), `src_ip_bytes` (`0.691 -> 0.968`), `duration` (`0.503 -> 0.470`), `dst_bytes` (`0.187 -> 0.199`).
  - **Duplicate-inflated shifts (drop >50% after dedup):** `dst_pkts` (`0.461 -> 0.181`), `dst_ip_bytes` (`0.363 -> 0.162`).
  - **Duplicate-masked shift (grows >10x after dedup):** `src_bytes` (`0.0095 -> 0.1323`).
- **Ground-Truth Composite-Key Verification:**
  - Excluded bit-for-bit duplicate shard `GroundTruth_Network_16.csv` (`SHA-256` identical to `15.csv`).
  - Across all `16,801,188` unique-shard ground-truth attack rows, **`0` rows** matched any Period A (`173,535` unique 6-tuples) or Period B (`428,291` unique 6-tuples) normal 6-tuple (**0% conflicting labels**).
  - Many-to-one 6-tuple collisions within normal traffic (`18,423` keys in Period A; `30,244` keys in Period B) confirm same-second repeated flows exist and require group/dedup-aware splitting.

## 3. Embargo Duration Sensitivity (VERIFIED)

| Flow Duration Threshold | Period A Normal Rows (`n=200,898`) | Period B Normal Rows (`n=595,482`) | Assessment |
| :--- | ---: | ---: | :--- |
| `duration > 60s` (1 min) | `2,597` (`1.293%`) | `2,637` (`0.443%`) | Leaves >1% of baseline flows able to straddle boundary |
| `duration > 300s` (5 min) | `980` (`0.488%`) | `266` (`0.045%`) | Reduces straddling flows by `62%` (A) / `90%` (B) |
| `duration > 900s` (15 min) | `410` (`0.204%`) | `169` (`0.028%`) | Strong practical reduction; residual long-lived sessions remain |

**Recommendation:** Replace the preliminary `60s` embargo with a **`5-minute (300s)` or `15-minute (900s)` embargo** AND explicitly filter boundary-crossing sessions where `ts_train + duration_train >= min_ts_eval`. No fixed time gap alone guarantees zero leakage.
