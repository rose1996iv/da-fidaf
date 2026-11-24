# 22 — `flow_extract_v1` Prototype Validation & Feature Distribution Audit (DA-FIDAF Phase 1G)

- **Audit Timestamp (UTC):** `2026-11-24T04:35:21Z`
- **Prototype Version:** `flow_extract_v1.0-proto` (isolated scratch script; production `src/dafidaf/` untouched)
- **Source Archive:** `I:\IoT\IoT Datasets\Raw_datasets\network_data\normal_pcaps.zip` (`SHA-256: fbefb9c1179be30a0771c646b729324c5723afce642b8994ef28c7337c64878d`)
- **Final Verdict:** **PASS (Prototype Validated) / CONDITIONAL (For Full-Scale Conversion)** *(The isolated `flow_extract_v1` prototype executed cleanly in `11.94s` over `1,000,000` bounded packets with bit-for-bit determinism, explicit `0x0003` drop counters, and causal flow assembly; full-scale deployment remains conditional on formal `src/dafidaf/` integration approval and explicit Stream A vs. Stream B separation.)*

---

## 1. Executive Summary

- **Prototype Verification (VERIFIED):** Executed `flow_extract_v1.0-proto` directly over uncompressed Store ZIP streams (`0` bytes extracted to disk) on `200,000` deterministic prefix packets from each of `5` captures (`1,000,000` packets total).
- **Determinism (VERIFIED):** Two independent executions on `normal_1.pcap` produced **bit-for-bit identical** canonical flow outputs (`SHA-256: 00e0da08cbabb00c267da8b69d33a19f4e277964618d10ab882bf2b8781140f7`).
- **Timeout Sensitivity (VERIFIED):** Raising idle timeout from `120s` to `600s` reduces flow count by `2.9%–6.5%` and increases mean flow duration by `+56%` to `+78%`, while median duration stays nearly constant (`0.0s–0.0135s`).
- **Cross-Capture Separation (VERIFIED):** Even after filtering `0x0003`, Stream B (`normal_IoT_2/3`) diverges sharply from Stream A (`normal_1`) (`duration_s` `PSI = 4.30–4.38`, `JSD = 0.40–0.41`) due to capture-vantage and single-packet UDP flow density (`62.9%` 1-packet flows vs `9.6%`), confirming capture-source bias rather than natural concept drift.

---

## 2. Prototype Architecture (`flow_extract_v1.0-proto`)

- **Isolation:** Implemented strictly outside `src/dafidaf/` (no production code or `uv.lock` changes).
- **Pipeline Stages:**
  1. Direct non-extracting reader supporting both `PCAPNG v1.0` (`normal_1/6/13`) and classic `libpcap v2.4` (`normal_IoT_2/3`), dropping EOF-truncated trailing records safely.
  2. Deterministic stable-sort by `(ts_us, original_packet_index)` — strictly causal (zero future lookahead in flow assembly).
  3. `LINKTYPE_LINUX_SLL (113)` parser with explicit drop counters for `0x0003` (`ETH_P_ALL`), `ARP`, non-TCP/UDP, and non-initial IPv4/IPv6 fragments.
  4. Canonical bidirectional 5-tuple `(min(E1, E2), max(E1, E2), l4_proto)` with forward direction anchored to the first observed packet of each flow.
  5. Configurable idle/active timeout eviction emitting deterministic canonical JSON/tabular flow records with archive SHA-256 and preprocessing version provenance.

---

## 3. Sample Methodology

- **Selection:** Deterministic bounded prefix (`packet_index 0..199,999`, `n = 200,000` per capture; `1,000,000` packets total) across `normal_1.pcap`, `normal_6.pcap`, `normal_13.pcap`, `normal_IoT_2.pcap`, and `normal_IoT_3.pcap`.
- **Caveat:** Sampled prefix windows (~15–100 minutes per file) validate prototype mechanics and relative sensitivity only; they are **not** full-archive population statistics.

---

## 4. Flow Extraction Validation & Packet Accounting (VERIFIED)

| Capture (`200,000` Input Pkts) | `0x0003` Dropped | Accepted TCP/UDP Pkts | Flows (`120s`) | TCP / UDP Flows (`120s`) | Structural `null`: `iat_mean_s` | Structural `null`: `tcp_*_cnt` |
| :--- | ---: | ---: | ---: | :--- | ---: | ---: |
| `normal_1.pcap` | `134,124` (`67.1%`) | `59,064` (`29.5%`) | `293` | `25` / `268` | `28` (`9.6%`) | `268` (`91.5%`) |
| `normal_6.pcap` | `165,833` (`82.9%`) | `24,790` (`12.4%`) | `897` | `28` / `869` | `382` (`42.6%`) | `869` (`96.9%`) |
| `normal_13.pcap` | `165,653` (`82.8%`) | `26,516` (`13.3%`) | `356` | `17` / `339` | `187` (`52.5%`) | `339` (`95.2%`) |
| `normal_IoT_2.pcap` | `0` (`0.0%`) | `192,642` (`96.3%`) | `1,536` | `45` / `1,491` | `966` (`62.9%`) | `1,491` (`97.1%`) |
| `normal_IoT_3.pcap` | `0` (`0.0%`) | `192,502` (`96.3%`) | `1,783` | `107` / `1,676` | `1,121` (`62.9%`) | `1,676` (`94.0%`) |

---

## 5. Feature Reliability Results

- **Reliably Extracted (0 unexpected missingness):** `duration_s` (s), `tot_pkts`, `fwd_pkts`, `bwd_pkts` (count), `tot_bytes`, `fwd_bytes`, `bwd_bytes` (bytes), `pkt_len_{min,mean,max,std}` (bytes), `protocol` (`6`/`17`), `src_port`, `dst_port` (numeric transport ports only; no L7 protocol inferred).
- **Conditionally Defined (explicit `null`, never silently zero-filled):**
  - `iat_{mean,max,std}_s` (s): `null` for all 1-packet flows (`9.6%–62.9%` of flows).
  - `tcp_{syn,ack,fin,rst,psh}_cnt`: `null` for all UDP flows (`91.5%–97.1%` of flows by count).
- **Application-Layer Features:** Intentionally omitted (not invented).

---

## 6. Timeout Sensitivity Analysis (`120s` vs. `600s` Idle Timeout — VERIFIED)

| Capture | Flows `120s -> 600s` | Mean Dur `120s -> 600s` | Median Dur `120s -> 600s` | Median Pkts `120s -> 600s` | Long-Lived (`>60s`) `120s -> 600s` |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `normal_1.pcap` | `293 -> 274` (`-6.5%`) | `26.47s -> 47.13s` (`+78.1%`) | `0.0135s -> 0.0132s` | `3.0 -> 2.0` | `6.48% -> 8.03%` |
| `normal_6.pcap` | `897 -> 871` (`-2.9%`) | `11.63s -> 19.93s` (`+71.3%`) | `0.0003s -> 0.0003s` | `2.0 -> 2.0` | `2.79% -> 2.76%` |
| `normal_13.pcap` | `356 -> 343` (`-3.7%`) | `17.91s -> 28.08s` (`+56.8%`) | `0.0s -> 0.0s` | `1.0 -> 1.0` | `2.53% -> 3.79%` |
| `normal_IoT_2.pcap` | `1,536 -> 1,468` (`-4.4%`) | `26.76s -> 41.68s` (`+55.7%`) | `0.0s -> 0.0s` | `1.0 -> 1.0` | `2.47% -> 2.45%` |
| `normal_IoT_3.pcap` | `1,783 -> 1,712` (`-4.0%`) | `19.01s -> 33.42s` (`+75.8%`) | `0.0s -> 0.0s` | `1.0 -> 1.0` | `1.63% -> 1.99%` |

**Interpretation:** `120s` vs `600s` substantially shifts mean flow duration (`+56%–+78%`) by merging persistent TCP/MQTT sessions across idle gaps while leaving short-flow medians stable. Timeout selection must be recorded as an explicit hyperparameter in experiment configs, not treated as universally optimal.

---

## 7. Cross-Capture Distribution Audit (vs. `normal_1.pcap` at `120s` — VERIFIED)

| Comparison Capture | `duration_s` (PSI / JSD / SMD) | `tot_pkts` (PSI / JSD / SMD) | `tot_bytes` (PSI / JSD / SMD) | `pkt_len_mean` (PSI / JSD / SMD) |
| :--- | :--- | :--- | :--- | :--- |
| `normal_6.pcap` (Stream A) | `1.080` / `0.183` / `-0.108` | `0.876` / `0.148` / `-0.113` | `1.184` / `0.195` / `-0.114` | `1.332` / `0.209` / `-0.418` |
| `normal_13.pcap` (Stream A) | `1.292` / `0.210` / `-0.062` | `1.124` / `0.186` / `-0.083` | `1.362` / `0.221` / `-0.089` | `1.183` / `0.194` / `-0.491` |
| `normal_IoT_2.pcap` (Stream B) | **`4.382`** / `0.413` / `+0.002` | **`2.064`** / `0.312` / `-0.049` | **`2.137`** / `0.327` / `-0.045` | **`2.579`** / `0.366` / `-0.581` |
| `normal_IoT_3.pcap` (Stream B) | **`4.296`** / `0.397` / `-0.054` | **`2.195`** / `0.319` / `-0.061` | **`1.976`** / `0.307` / `-0.058` | **`2.263`** / `0.331` / `+0.020` |

**Attribution:** Large Stream A vs. Stream B divergences reflect **capture-vantage differences** (different 1-packet UDP/DNS share and 5-tuple density), **not** natural concept drift.

---

## 8. Leakage & Reproducibility Checks (VERIFIED)

- **Zero train/test contamination & zero evaluation-set fitting:** All PSI/JSD/SMD bin edges and `std` values were fitted strictly on reference capture `normal_1.pcap`; no model training occurred.
- **Strictly causal flow assembly:** Flows evict purely on past-to-current packet timestamps (`ts_us - last_ts > idle_us`).
- **Bit-for-bit determinism:** Verified across repeated runs (`SHA-256: 00e0da08cbabb00c267da8b69d33a19f4e277964618d10ab882bf2b8781140f7`).
- **Provenance:** Source archive SHA-256 (`fbefb9c1179be30a0771c646b729324c5723afce642b8994ef28c7337c64878d`) and `flow_extract_v1.0-proto` recorded explicitly.

---

## 9. Limitations & Final Verdict

- **Limitations:** Bounded to `200,000` prefix packets per file (`1,000,000` total); TCP stream reassembly and full-archive conversion were intentionally not executed; Period B (`Apr 23–29`) raw PCAPs remain unavailable (`normal_attack_pcaps.zip` on **HOLD**).
- **Final Verdict:** **CONDITIONAL** — `flow_extract_v1` prototype is **verified deterministic and structurally sound** on bounded samples, ready for optional production integration into `src/dafidaf/` only upon explicit approval and with Stream A / Stream B kept separated.
