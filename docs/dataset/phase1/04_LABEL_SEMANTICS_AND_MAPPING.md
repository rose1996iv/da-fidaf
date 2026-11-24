# 04 — Label Semantics and Mapping Feasibility (DA-FIDAF Phase 1 Part A)

- **Audit Timestamp (UTC):** `2026-11-24T03:20:51Z`
- **Policy:** Never merge datasets solely on matching class names or column names without a versioned semantic ontology.

## 1. Verified Label Taxonomies

### A. CICIoT2023 — VERIFIED
- **Encoding:** Single string column `Label` in `MERGED_CSV/*.csv`; **implicit directory/filename label** in `CSV/<Class>/*.pcap.csv`.
- **Observed Classes (`28` distinct values in 5,000-row sample of `Merged01.csv`; `34` subdirectories in `CSV/`):**
  - Benign: `BENIGN`
  - DDoS (12+ subtypes): `DDOS-ICMP_FLOOD`, `DDOS-UDP_FLOOD`, `DDOS-TCP_FLOOD`, `DDOS-RSTFINFLOOD`, `DDOS-PSHACK_FLOOD`, `DDOS-SYN_FLOOD`, `DDOS-SYNONYMOUSIP_FLOOD`, `DDOS-ICMP_FRAGMENTATION`, `DDOS-ACK_FRAGMENTATION`, `DDOS-UDP_FRAGMENTATION`, `DDOS-SLOWLORIS`, `DDOS-HTTP_FLOOD`
  - DoS: `DOS-UDP_FLOOD`, `DOS-TCP_FLOOD`, `DOS-SYN_FLOOD`, `DOS-HTTP_FLOOD`
  - Botnet/Mirai: `MIRAI-GREETH_FLOOD`, `MIRAI-UDPPLAIN`, `MIRAI-GREIP_FLOOD`
  - Recon/MITM/Web/Other: `VULNERABILITYSCAN`, `MITM-ARPSPOOFING`, `DNS_SPOOFING`, `RECON-HOSTDISCOVERY`, `RECON-PORTSCAN`, `RECON-OSSCAN`, `BACKDOOR_MALWARE`, `XSS`, plus `BrowserHijacking`, `CommandInjection`, `DictionaryBruteForce`, `SqlInjection`, `Uploading_Attack` directories.

### B. ToN-IoT (`train_test_network.csv`, Full Scan: `211,043` rows) — VERIFIED
- **Encoding:** Binary `label` (`0`: `50,000` normal; `1`: `161,043` attack) + multi-class `type` (**10 classes**):
  - `normal` (`50,000`), `backdoor` (`20,000`), `ddos` (`20,000`), `dos` (`20,000`), `injection` (`20,000`), `password` (`20,000`), `ransomware` (`20,000`), `scanning` (`20,000`), `xss` (`20,000`), `mitm` (`1,043`).
- **Sub-corpus variation:** `Train_Test_IoT_Fridge.csv` has **7** `type` classes (`39,944` rows; omits `dos`, `scanning`, `mitm`); `Train_Test_Linux_process.csv` and `Train_Test_Windows_10.csv` each have **8** `type` classes.

### C. Edge-IIoTset (`ML-EdgeIIoT-dataset.csv`, Full Scan: `157,800` rows) — VERIFIED
- **Encoding:** Binary `Attack_label` (`0`: `24,301` normal; `1`: `133,499` attack) + multi-class `Attack_type` (**15 classes**):
  - `Normal` (`24,301`), `DDoS_UDP` (`14,498`), `DDoS_ICMP` (`14,090`), `Ransomware` (`10,925`), `DDoS_HTTP` (`10,561`), `SQL_injection` (`10,311`), `Uploading` (`10,269`), `DDoS_TCP` (`10,247`), `Backdoor` (`10,195`), `Vulnerability_scanner` (`10,076`), `Port_Scanning` (`10,071`), `XSS` (`10,052`), `Password` (`9,989`), `MITM` (`1,214`), `Fingerprinting` (`1,001`).

## 2. Semantic Equivalence vs. Incompatibility Matrix (INFERRED from VERIFIED Labels)

| Canonical Coarse Category | CICIoT2023 | ToN-IoT (`type`) | Edge-IIoTset (`Attack_type`) | Semantic Alignment Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Benign / Normal** | `BENIGN` | `normal` | `Normal` | Direct binary equivalence (`0` vs `1`), but background environments differ fundamentally. |
| **DDoS / DoS** | 16 distinct DDoS/DoS + 3 Mirai flood classes | `ddos`, `dos` | `DDoS_UDP`, `DDoS_ICMP`, `DDoS_HTTP`, `DDoS_TCP` | Granularity mismatch: ToN-IoT collapses protocols; Edge-IIoTset has no separate `DoS` class; CICIoT2023 separates Mirai floods. |
| **Recon / Scanning** | `RECON-PORTSCAN`, `RECON-OSSCAN`, `RECON-HOSTDISCOVERY`, `VULNERABILITYSCAN` | `scanning` | `Port_Scanning`, `Vulnerability_scanner`, `Fingerprinting` | Many-to-one mapping required; `Fingerprinting` ~ `RECON-OSSCAN` (INFERRED). |
| **Web / Injection** | `XSS`, `SqlInjection`, `CommandInjection`, `Uploading_Attack`, `BrowserHijacking` | `xss`, `injection` | `XSS`, `SQL_injection`, `Uploading` | ToN-IoT `injection` is broader than Edge-IIoTset `SQL_injection`. |
| **MITM / Spoofing** | `MITM-ARPSPOOFING`, `DNS_SPOOFING` | `mitm` | `MITM` | Severe class imbalance in both ToN-IoT (`1,043`) and Edge-IIoTset (`1,214`). |
| **Credential / Password** | `DictionaryBruteForce` | `password` | `Password` | Broadly alignable after verifying protocol context. |
| **Malware / Backdoor / Ransomware** | `BACKDOOR_MALWARE` (no Ransomware) | `backdoor`, `ransomware` | `Backdoor`, `Ransomware` | CICIoT2023 lacks a `Ransomware` class (partial taxonomy gap). |

## 3. Mapping Feasibility Verdict
- **Binary (`Benign` vs `Attack`) mapping:** **FEASIBLE** across all three families (with domain-shift caveats).
- **Coarse 6–7 family multi-class mapping:** **CONDITIONAL** — requires a versioned YAML ontology contract (`configs/datasets/label_taxonomy.yaml`) explicitly documenting many-to-one collapses and missing classes (`Ransomware` absent in CICIoT2023; `DoS`/`Mirai` absent in Edge-IIoTset).
- **Fine-grained 1-to-1 cross-dataset mapping:** **NOT SUPPORTED** due to incompatible attack granularities.
