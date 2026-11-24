# 21 — SLL Protocol Semantics, Packet Parsing Validation & Flow Feature Reliability Audit (DA-FIDAF Phase 1F)

- **Audit Timestamp (UTC):** `2026-11-24T04:24:30Z`
- **Target Archive:** `I:\IoT\IoT Datasets\Raw_datasets\network_data\normal_pcaps.zip` (`SHA-256: fbefb9c1179be30a0771c646b729324c5723afce642b8994ef28c7337c64878d`)
- **Sample Scope:** `250,000` packets (`50,000` deterministic prefix packets each from `normal_1.pcap`, `normal_6.pcap`, `normal_13.pcap`, `normal_IoT_2.pcap`, `normal_IoT_3.pcap`), read directly from the uncompressed Store ZIP with zero disk extraction.
- **Final Verdict:** **CONDITIONAL** *(All standard `IPv4`, `IPv6`, `TCP`, `UDP`, and `ARP` packets parsed with `0` header/length/fragmentation errors across `250,000` packets; however, `66.72%–83.27%` of packets in `normal_1`, `normal_6`, and `normal_13` are SLL `0x0003` (`ETH_P_ALL`) outgoing raw-socket frames with non-RFC IPv4 headers (`version=0`), requiring mandatory explicit filtering in the preprocessing pipeline.)*

---

## 1. Executive Summary

1. **`0x0003` Root Cause Solved (VERIFIED):** Every single `0x0003` packet inspected (`116,460` packets across `normal_1`, `normal_6`, and `normal_13`; `0` in `normal_IoT_2/3`) has a **valid 16-byte `LINKTYPE_LINUX_SLL (113)` header** with `pkt_type = 4` (`PACKET_OUTGOING`), `arphrd = 1` (`ARPHRD_ETHER`), `ll_len = 6`, and `protocol = 0x0003` (`ETH_P_ALL`). Its L3 payload (`pkt[16:]`) is a **non-RFC synthetic raw-socket IPv4-like frame** whose version/IHL byte cycles `0x00..0x0f` (`version = 0`, not `4`), with fixed IP ID `0x04d2` (`1234`), `TTL = 127`, `proto = 6`, and `192.168.1.x -> 192.168.1.y` addresses.
2. **Standard Protocol Parsing is Clean (VERIFIED):** Across all `250,000` sampled packets, `100%` of SLL headers (`250,000 / 250,000`), `IPv4` (`126,420`), `IPv6` (`901`), `ARP` (`6,219`), `TCP` (`118,191`), `UDP` (`3,486`), `TCPv6` (`324`), and `UDPv6` (`122`) parsed with **`0` truncated headers, `0` invalid lengths, and `0` fragmentation errors**.
3. **Cross-Capture Bias Warning (VERIFIED):** Stream A (`normal_1`, `normal_6`, `normal_13`) is `66.7%–83.3%` `0x0003` raw-socket traffic, while Stream B (`normal_IoT_2`, `normal_IoT_3`) is `93.8%–95.6%` standard IPv4 + `4.4%–6.2%` ARP (`0.0%` `0x0003`). Any shared pipeline must explicitly filter `0x0003` frames and log drop counts.

---

## 2. SLL Protocol Field (`0x0003`) Investigation (VERIFIED)

- **SLL Header Layout (`16` bytes, big-endian):** `[pkt_type:2][arphrd:2][ll_addr_len:2][ll_addr:8][protocol:2]`.
- **Observed `0x0003` Sample (`normal_13.pcap`, `cap_len = 349`):**
  - `sll_hdr`: `0004 0001 0006 a491b11e58a8 f6f7 0003` -> `PACKET_OUTGOING (4)`, `ARPHRD_ETHER (1)`, `ll_len = 6`, `ETH_P_ALL (0x0003)`.
  - `l3[0:20]`: `0f00 014d 04d2 0000 7f06 e84a c0a80137 c0a80107` -> Byte `0` = `0x0f` (`version = 0`, invalid IPv4!), `len = 0x014d = 333` (`349 - 16`), `IP_ID = 1234`, `TTL = 127`, `proto = 6`, `src = 192.168.1.55`, `dst = 192.168.1.7`.
- **Conclusion:** Valid SLL records carrying **non-RFC / synthetic raw-socket frames** (`ETH_P_ALL`, `version = 0`). They must **not** be treated as valid IPv4/IPv6/ARP packets and must be explicitly segregated/dropped with audited counters before IP flow construction.

---

## 3. Packet Parser Validation Matrix (`n = 50,000` per Capture — VERIFIED)

| Capture (`normal_pcaps/...`) | SLL Valid | `0x0003` (`ETH_P_ALL`) | IPv4 Valid | IPv6 Valid | ARP Valid | TCP / UDP Valid | Frag / Trunc / Invalid | Unique 5-Tuple Flows (Bidir / Unidir) |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- | ---: | :--- |
| `normal_1.pcap` | `50,000` | `33,361` (`66.72%`) | `15,954` | `482` | `203` | `14,406` / `207` (+`363` v6) | `0` / `0` / `0` | `78` (`64` / `14`) |
| `normal_6.pcap` | `50,000` | `41,636` (`83.27%`) | `7,516` | `363` | `485` | `5,382` / `483` (+`67` v6) | `0` / `0` / `0` | `187` (`72` / `115`) |
| `normal_13.pcap` | `50,000` | `41,463` (`82.93%`) | `8,245` | `56` | `236` | `6,451` / `179` (+`16` v6) | `0` / `0` / `0` | `67` (`47` / `20`) |
| `normal_IoT_2.pcap` | `50,000` | `0` (`0.00%`) | `47,812` | `0` | `2,188` | `46,664` / `1,103` | `0` / `0` / `0` | `430` (`139` / `291`) |
| `normal_IoT_3.pcap` | `50,000` | `0` (`0.00%`) | `46,893` | `0` | `3,107` | `45,288` / `1,514` | `0` / `0` / `0` | `716` (`218` / `498`) |

---

## 4. Flow Construction Reliability

- **Deterministic Bidirectional Canonical Key:** For valid IPv4/IPv6 TCP and UDP packets (excluding non-initial IP fragments with `frag_offset > 0` where transport ports are absent), define endpoint `E1 = (src_ip, src_port)` and `E2 = (dst_ip, dst_port)`. Canonical key = `(min(E1, E2), max(E1, E2), l4_proto)`; forward direction = first observed packet's `(src_ip, src_port)` (or lexicographical `E1 <= E2` when order-independent).
- **Port & Protocol Discipline:** Never invent ports for ICMP/IGMP/ARP/non-initial fragments (`port = null`); never assert application protocol identity solely from port numbers (report `dst_port` as a numeric transport attribute only, or run explicit L7 dissection).
- **Ordering & Timeouts:** Stable-sort by microsecond timestamp before flow assembly (handling the `0.030%` OOO packets verified in Phase 1D); enforce explicit idle timeout (`60s` or `120s`) and active timeout (`300s` or `600s`) so long-lived MQTT sessions do not span split boundaries.

---

## 5. Flow Feature Reliability Matrix

| Feature | Classification | Evidence & Leakage / Bias Notes |
| :--- | :--- | :--- |
| **Duration, Total/Fwd/Bwd Packets, Total Bytes** | **Reliably extractable** | Microsecond timestamps & `orig_len`/`cap_len` verified (`0` truncated complete packets). |
| **Packet-Size & Inter-Arrival-Time (IAT) Stats** | **Reliably extractable** | Valid once `0x0003` frames are dropped and packets are timestamp-sorted per flow. |
| **TCP Flags & L4 Protocol (`TCP`/`UDP`/`ICMP`)** | **Reliably extractable** | `100%` of sampled TCP/UDP headers valid (`0` invalid `doff`). |
| **Flow Direction (Fwd vs. Bwd)** | **Conditionally extractable** | Reliable when flow start (TCP SYN) is observed; ambiguous for mid-stream flows at file boundaries. |
| **Service Port (`src_port`, `dst_port`)** | **Conditionally extractable** | High host/session memorization risk; strip ephemeral `src_port` and avoid inferring L7 solely from port. |
| **Application-Layer Features (HTTP/DNS/MQTT/TLS)** | **Unavailable or unreliable** | TLS (`443`) is encrypted; L7 dissection requires reassembled TCP streams and cannot be assumed complete. |
| **IPs, MACs, Raw Timestamps, SLL `pkt_type`** | **Exclude from ML features** | Direct identifier/capture-vantage leakage (`pkt_type` distribution differs sharply between Stream A and Stream B). |

---

## 6. Cross-Capture Comparability

- **Before Filtering `0x0003`:** **NOT COMPARABLE** — Stream A (`normal_1`, `normal_6`, `normal_13`) contains `66.7%–83.3%` synthetic `0x0003` frames vs `0.0%` in Stream B (`normal_IoT_2`, `normal_IoT_3`).
- **After Filtering `0x0003` & Excluding `ARP`:** **CONDITIONALLY COMPARABLE** for standard IPv4 TCP/UDP flow features (`normal_1..13` also include `0.1%–1.0%` IPv6, whereas `normal_IoT_2/3` are `100%` IPv4+ARP). Capture-source bias remains possible because `normal_IoT_2/3` have `6x–10x` higher unique 5-tuple density per 50k packets (`430–716` vs `67–187`).

---

## 7. Proposed Reproducible Preprocessing Specification (`flow_extract_v1`)

1. **Supported Inputs:** `PCAPNG v1.0` and classic `libpcap v2.4` with `LINKTYPE_LINUX_SLL (113)` (explicitly reject unknown linktypes).
2. **Protocol Rules:** Accept `0x0800` (IPv4) and `0x86DD` (IPv6) with valid version/IHL/length; drop and count `0x0003` (`ETH_P_ALL`), `0x0806` (ARP), and unsupported EtherTypes.
3. **Malformed & EOF Handling:** Drop single EOF-truncated trailing record in `normal_IoT_2/3`; log exact dropped byte count and record offset; fail closed on mid-file corruption.
4. **Fragments:** Log and drop non-initial fragments (`frag_offset > 0` or IPv6 Next Header `44`) from 5-tuple TCP/UDP flows unless reassembly is enabled.
5. **Flow Key & Timeouts:** Canonical bidirectional 5-tuple `(min(E1, E2), max(E1, E2), l4_proto)`; idle timeout `120s`, active timeout `600s`; stable-sort packets by `(ts_us, member_idx, pkt_idx)`.
6. **Overlap Control:** Keep Stream A (`normal_1..13`) and Stream B (`normal_IoT_2..3`) separated by default; apply Phase 1E cross-vantage deduplication only if merging is explicitly justified.
7. **Missing Values & Provenance:** Record `null` for non-TCP flags; fit all scalers/imputers strictly on Train; emit JSON provenance sidecar recording archive SHA-256, drop counters (`0x0003`, EOF, fragments), timeout config, and software versions.

---

## 8. E1–E6 Reassessment, Limitations & Final Verdict

- **E1–E6 Reassessment:** No change to Phase 1C/1E verdicts (`E1: CONDITIONAL`, `E2: CONDITIONAL`, `E3: CONDITIONAL`, `E4: CONDITIONAL`, `E5: HOLD`, `E6: PASS`). All captures in `normal_pcaps.zip` remain Period A (`Apr 2–4`) normal-only traffic with simulated FL client partitioning.
- **Limitations:** Audit sampled `50,000` prefix packets per capture (`250,000` total); full 31.3M-packet `0x0003` prevalence and TCP reassembly completeness were not executed.
- **Final Verdict:** **CONDITIONAL** — Standard IPv4/IPv6/TCP/UDP flow extraction is verified reliable **only** when the preprocessing specification explicitly drops and logs SLL `0x0003` raw-socket frames and EOF-truncated trailing records.
