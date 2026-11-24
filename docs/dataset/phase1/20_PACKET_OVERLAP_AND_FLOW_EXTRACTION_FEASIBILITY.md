# 20 — Packet Overlap, Duplicate Detection & Flow Extraction Feasibility Audit (DA-FIDAF Phase 1E)

- **Audit Timestamp (UTC):** `2026-11-24T04:12:40Z`
- **Target Archive:** `I:\IoT\IoT Datasets\Raw_datasets\network_data\normal_pcaps.zip` (`SHA-256: fbefb9c1179be30a0771c646b729324c5723afce642b8994ef28c7337c64878d`)
- **Reference Reports:** `18_TON_IOT_NORMAL_PCAP_ARCHIVE_REVIEW.md`, `19_TON_IOT_PCAPNG_METADATA_AND_TIMELINE_AUDIT.md`
- **Final Verdict:** **CONDITIONAL** *(Packet-level overlap, trailing-record bounds, and `LINKTYPE_LINUX_SLL (113)` IPv4/IPv6/TCP/UDP flow extraction are all verified directly from archive streams without disk extraction; however, `normal_IoT_2/3` share `24.7%–29.1%` L3 payload overlap with `normal_1..13` across distinct capture points, `normal_1..13` contain `66.8%–82.6%` non-IPv4/IPv6 `0x0003` SLL frames, and no genuine gateway identifiers exist.)*

---

## 1. Executive Summary

- **`normal_13.pcap` vs. `normal_6..12.pcap` Mystery Resolved (VERIFIED):** Hourly packet bucketing of all `1,918,446` packets in `normal_13.pcap` proved **zero packets** between `2019-04-03T09:00Z` and `2019-04-04T05:59Z` (`Apr 3 06:00Z`: `137,130`; `07:00Z`: `666,458`; `08:00Z`: `100,424` ending before `08:09:45Z`; then `Apr 4 06:00Z`: `503,683`; `07:00Z`: `510,751`). **`normal_13.pcap` has `0` overlapping packets with `normal_6.pcap`** — it is a two-segment remainder file bridging the `normal_5`–`normal_6` gap and extending past `normal_12`.
- **`normal_IoT_2/3` vs. `normal_1..13` Cross-Capture Overlap (VERIFIED):** Bounded 15-minute overlap windows showed **`0` exact microsecond+full-byte duplicates (`0.0%`)**, but **`24.72%` (`3,832` L3 hashes)** overlap between `normal_IoT_2.pcap` and `normal_6.pcap` and **`29.12%` (`9,619` L3 hashes)** overlap between `normal_IoT_3.pcap` and `normal_1.pcap` — proving two distinct capture vantage points observing partially overlapping network traffic.
- **Capture Completeness (VERIFIED):** Both `normal_IoT_2.pcap` (`2,639,871` valid packets) and `normal_IoT_3.pcap` (`2,728,860` valid packets) are **`99.99996%` valid**, each ending with exactly **1** incomplete trailing packet record.
- **Flow Extraction Feasibility (VERIFIED):** `LINKTYPE_LINUX_SLL (113)` supports IPv4, IPv6, TCP/UDP bidirectional 5-tuples, packet/byte counters, durations, and well-known service ports (`1883` MQTT, `53` DNS, `443` HTTPS, `80` HTTP, `123` NTP), **but** `normal_1..13` contain `66.8%–82.6%` SLL protocol `0x0003` frames that must be explicitly filtered/handled.

---

## 2. Packet Duplicate Analysis (Bounded 15-Minute Overlap Windows — VERIFIED)

Fingerprints compared: (1) **Exact duplicate** = `(ts_us, cap_len, orig_len, blake2b_96(full_pkt))`; (2) **L3 payload match** = `blake2b_96(pkt[16:])` (stripping the 16-byte SLL link header to detect identical IP packets captured at different vantage points/clocks); (3) **Ambiguous match** = identical `(ts_us, cap_len, orig_len)` with different packet bytes.

| Capture Pair & 15-Min Window (UTC) | Pkts A / B | Unique Exact A / B | Internal Exact Dups | Exact Duplicate Overlap | L3 Payload Hash Overlap | Ambiguous (`ts+len`, diff bytes) |
| :--- | :--- | :--- | :--- | ---: | ---: | ---: |
| `normal_13.pcap` vs `normal_6.pcap` (`Apr 3 08:09:45–08:24:45`) | `0` / `100,000` | `0` / `100,000` | `0` / `0` | **`0`** (`0.0%`) | **`0`** (`0.0%`) | `0` |
| `normal_IoT_2.pcap` vs `normal_6.pcap` (`Apr 3 08:09:45–08:24:45`) | `21,574` / `100,000` | `21,574` / `100,000` | `0` / `0` | **`0`** (`0.0%`) | **`3,832`** (`24.716%`) | `1` |
| `normal_IoT_3.pcap` vs `normal_1.pcap` (`Apr 2 15:52:04–16:07:04`) | `70,941` / `100,000` | `70,941` / `100,000` | `0` / `0` | **`0`** (`0.0%`) | **`9,619`** (`29.123%`) | `0` |

**Limitations:** Bounded to 15-minute windows (`<= 100,000` packets/file) to avoid multi-GB RAM expansion. L3 hash overlap can include legitimate repeated payloads (e.g., identical MQTT keepalives/TCP retransmissions) in addition to dual-captured packets; full cross-capture deduplication requires IP-ID + TCP-seq + bounded clock-skew (`|dt| <= delta`) correlation.

---

## 3. Capture Completeness (`normal_IoT_2.pcap` & `normal_IoT_3.pcap` — VERIFIED)

| Member | Valid Complete Packets | Incomplete Trailing Records | Trailing Record Timestamp (UTC) | Expected `cap_len` / `orig_len` | Available Payload / Missing Bytes | Recommendation |
| :--- | ---: | ---: | :--- | ---: | ---: | :--- |
| `normal_IoT_2.pcap` | `2,639,871` (`99.99996%`) | `1` (`67` B tail) | `2019-04-04T07:50:11.328547Z` | `76` / `76` B | `51` B / `25` B missing | **Exclude trailing incomplete record only** |
| `normal_IoT_3.pcap` | `2,728,860` (`99.99996%`) | `1` (`187` B tail) | `2019-04-03T08:08:28.473816Z` | `447` / `447` B | `171` B / `276` B missing | **Exclude trailing incomplete record only** |

**Disposition:** Do **not** quarantine `normal_IoT_2.pcap` or `normal_IoT_3.pcap`. Both files contain >`2.6M` structurally valid packets each and require only standard EOF-truncated-record drop during read-only parsing (source archive untouched).

---

## 4. `LINKTYPE_LINUX_SLL (113)` Flow Extraction Feasibility (25,000-Packet Samples — VERIFIED)

| Member (25k Sample) | IPv4 | IPv6 | ARP | SLL `0x0003` (Non-IP) | TCP / UDP / ICMP | Unique Src/Dst IPs | Unique SLL MACs | Bidir 5-Tuples | Top Service Ports |
| :--- | ---: | ---: | ---: | ---: | :--- | :--- | ---: | ---: | :--- |
| `normal_1.pcap` | `7,798` (`31.2%`) | `393` (`1.6%`) | `108` | **`16,701` (`66.8%`)** | `7,299` / `148` / `670` | `39` / `49` | `23` | `64` | `1883` (`786`), `53` (`112`), `443` (`57`), `80` (`17`) |
| `normal_13.pcap` | `4,154` (`16.6%`) | `45` (`0.2%`) | `146` | **`20,655` (`82.6%`)** | `3,204` / `132` / `826` | `26` / `40` | `25` | `59` | `1883` (`847`), `53` (`86`), `443` (`28`) |
| `normal_IoT_2.pcap` | `23,713` (`94.9%`) | `0` | `1,287` | `0` (`0.0%`) | `23,041` / `645` / `0` | `18` / `12` | `12` | `256` | `1883` (`7,314`), `53` (`260`), `443` (`92`), `123` (`12`) |
| `normal_IoT_3.pcap` | `23,493` (`94.0%`) | `0` | `1,507` | `0` (`0.0%`) | `22,703` / `738` / `22` | `19` / `12` | `11` | `365` | `1883` (`7,748`), `53` (`416`), `443` (`54`), `80` (`17`) |

- **Supported Features (VERIFIED):** IPv4 & IPv6 L3 headers, TCP/UDP bidirectional 5-tuples, microsecond flow timestamps & durations, packet/byte counters, TCP flags, and port-indicated service hints (`MQTT 1883`, `DNS 53`, `HTTPS 443`, `HTTP 80`, `NTP 123`).
- **Unavailable / Unreliable Features:** Physical Ethernet destination MAC (stripped by `LINUX_SLL`), interface names (`None`), encrypted TLS (`443`) application payloads, and L3/L4 flow semantics on the `66.8%–82.6%` `0x0003` non-IP frames in `normal_1..13`.

---

## 5. Proposed Reproducible Deduplication Protocol

1. **Stream Separation First (Primary Defense):** Never merge Stream A (`normal_1..13`, PCAPNG) and Stream B (`normal_IoT_2..3`, classic PCAP) into a single flat packet stream before flow extraction; treat them as **two separate capture vantage streams** unless cross-stream deduplication is explicitly required.
2. **Deterministic Ordering:** Within each stream, parse valid records only (dropping the 1 EOF-truncated record in `normal_IoT_2/3`) and stable-sort by `(ts_us, member_index, packet_index)`.
3. **Packet-Category Distinction:**
   - **Exact capture duplicate:** Identical `(ts_us, cap_len, orig_len, blake2b_96(full_pkt))` -> drop duplicate.
   - **Cross-vantage overlapping observation:** Identical `(L3_5tuple, IPv4_ID, TCP_seq_or_UDP_checksum, blake2b_96(L3_payload))` with `|dt| <= 50 ms` across Stream A & Stream B -> retain canonical Stream A (or Stream B) observation and log match.
   - **TCP Retransmission / Legitimate Repeated Packet:** Same L3 payload with `|dt| > 50 ms` OR distinct IPv4 ID / TCP flags -> **RETAIN** (never drop retransmissions or periodic MQTT telemetry solely because payload bytes match).
   - **Ambiguous match:** Identical `(ts_us, cap_len, orig_len)` with different packet bytes -> **RETAIN both** and increment ambiguity counter.

---

## 6. Gateway Partition Limitations & E1–E6 Implications

- **Gateway / Client Partitioning:** Capture filenames (`normal_1..13` vs `normal_IoT_2..3`) **cannot** be treated as independent physical gateways (`normal_1..13` are 2M-packet `editcap` splits of one stream, and `normal_IoT_2..3` overlap Stream A by `24.7%–29.1%` L3 payloads with only `11–25` unique SLL MACs). Any FL client partition derived from these captures must be explicitly classified as **simulated logical clients**.
- **E1–E6 Implications:**
  - **E1 / E4 / E6:** `normal_pcaps.zip` is **not required** for tabular FL baselines (already covered by verified CSVs), but provides optional raw Period A normal-traffic re-extraction provenance.
  - **E2 / E3 / E5:** Does **not** alter Phase 1C verdicts (`E2: CONDITIONAL`, `E3: CONDITIONAL`, `E5: HOLD`) because all 15 captures cover only Period A (`Apr 2–4`) normal traffic with zero Period B (`Apr 23–29`) coverage.

---

## 7. Final Verdict

**CONDITIONAL** — Both streams inside `normal_pcaps.zip` are structurally usable for read-only Period A flow extraction once parsers support mixed PCAPNG/classic-PCAP formats, filter `0x0003` SLL frames, drop the single EOF-truncated record in `normal_IoT_2/3`, and keep Stream A (`normal_1..13`) and Stream B (`normal_IoT_2..3`) separated or cross-vantage deduplicated.
