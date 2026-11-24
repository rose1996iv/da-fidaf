# 24 — Phase 1 Research Dataset Selection & Experimental Readiness Gate (DA-FIDAF Phase 1I)

- **Gate Date (UTC):** `2026-11-24T05:05:00Z`
- **Evidence Corpus:** Phase 1 reports `01`–`23` under `docs/dataset/phase1/` and manifests `dataset_inventory.json`, `ton_iot_temporal_audit.json`, `ton_iot_drift_analysis.json`.
- **Gate Scope:** Formal dataset selection, frozen preprocessing specification, threats to validity, and Phase 2 readiness verdicts (no production code implemented; no datasets modified).

---

## 1. Research Dataset Selection

| Dataset Family | Role | Integrity | Label Quality | Temporal Provenance | Gateway IDs | Cross-Env Suitability | Eligible Experiments |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ToN-IoT** (`Processed_Network_dataset` + `train_test_network.csv`) | **Primary** | CSVs & `Train_Test_datasets.zip` **VERIFIED**; 2 raw 20 GB ZIPs **HOLD** (`02`) | Clean (`0` GT 6-tuple conflicts across `16.8M` rows; `14`) | **VERIFIED** in `Processed_Network_dataset` (`22.34M` rows, `Apr 2–4` + `Apr 23–29`, 18-day gap; `10`); absent in `train_test_network.csv` (`05`) | None (simulated; `06`) | High (Zeek conn schema; requires semantic ontology for E5) | **E1, E2, E3, E4, E6** (`E5` HOLD) |
| **CICIoT2023** (`MERGED_CSV`) | **Supporting** | `CSV.zip` & `MERGED_CSV.zip` CD **VERIFIED** (`02`) | `40`-col `MERGED_CSV` has `Label` (28+ classes); `39`-col `CSV/` omits `Label` (`03`, `04`) | **ABSENT** (`Time_To_Live` is IP TTL; `05`) | None (simulated; `06`) | Moderate (aggregated flow stats; no `Ransomware` class; `04`) | **E1, E4, E6** (`E2/E3` NOT SUPPORTED; `E5` HOLD) |
| **Edge-IIoTset** (`ML-EdgeIIoT-dataset.csv` / `DNN-EdgeIIoT-dataset.csv`) | **Supporting** | `Edge_IIoT Dataset.zip` CD **VERIFIED**; `ML-EdgeIIoT` SHA-256 **VERIFIED** (`02`, `03`) | `15` classes (`Attack_label`, `Attack_type`); heavy duplication (`16.3%` in `ML-EdgeIIoT`, `66.6%` in `MITM`; `03`, `07`) | **CORRUPTED / INCOMPLETE** (`frame.time` = `'6.0'`, IPs in `Modbus.csv`, missing month/day in `DNN`; `05`) | None (simulated; `06`) | Moderate (63 packet-header cols; requires `frame.time`/IP/`inf` sanitization; `03`, `07`) | **E1, E4, E6** (`E2/E3` HOLD; `E5` HOLD) |
| **ToN-IoT `normal_pcaps.zip`** | **Conditional** | Zip64 CD OK, SHA-256 **VERIFIED**, `31.29M` pkts walked (`18`, `19`); full `7z t` deferred | Normal-only by filename & Period A dates (`Apr 2–4`); **no attack labels** (`19`) | **VERIFIED** Period A (`2019-04-02T09:45:58Z` – `2019-04-04T07:50:10Z`; `19`) | None (`LINUX_SLL`, `if_name=None`; `19`, `20`) | Low alone (normal-only; Stream A `67%–83%` `0x0003` vs Stream B `0%`; `21`) | Optional Period A raw baseline & `flow_extract_v1` validation only |
| **ToN-IoT `network_data.zip` & `normal_attack_pcaps.zip`** | **Excluded / HOLD** | **CORRUPT / TRUNCATED** (`7z l -slt` exit `2`, missing central directory; `02`) | Unusable | Unusable | Unusable | Excluded | **None (Quarantined)** |

---

## 2. ToN-IoT Source Selection & Eligibility Separation

- **CSV-Derived Experiments (`Processed_Network_dataset` & `train_test_network.csv`):** Primary source for E1, E2, E3, E4, and E6. Use `Processed_Network_dataset` (retains `ts`) for all temporal protocols (E2/E3) and `train_test_network.csv` (`211,043` rows, SHA-256 verified) for fast non-temporal baselines (E1/E4/E6). Never mix `Processed_*` and `Train_Test_*` in the same split (`07`).
- **Network Ground-Truth Files (`GroundTruth_Network_1..18`):** Provenance verification **only** (`100%` `ts` overlap, `0` label conflicts with normal 6-tuples; `11`, `14`). **Exclude `GroundTruth_Network_16.csv`** (bit-for-bit duplicate of `15.csv`, SHA-256 `d1d4cb49...542f`; `11`). Never join GT columns as model features (`11`).
- **PCAP-Derived Normal Baseline (`normal_pcaps.zip`):** Eligible **only** as an optional raw Period A normal baseline (`Apr 2–4`) using `flow_extract_v1`. **Cannot** support packet-level attack attribution or Period B evaluation (`0%` overlap with `Apr 23–29` ground truth; `19`). **Stream A (`normal_1..13`) and Stream B (`normal_IoT_2..3`) must remain separate strata** (`20`, `22`, `23`).
- **Damaged Archives (`network_data.zip`, `normal_attack_pcaps.zip`):** Permanently **HOLD / Excluded** unless officially reacquired and checksum-verified (`02`).

---

## 3. Consolidated E1–E6 Readiness Matrix (Natural vs. Synthetic Distinguished)

| Exp | Dataset Source | Split & Client Strategy | Intervention (Natural vs. Synthetic) | Evaluation Metrics | Confounders | Status | Outstanding Prerequisites |
| :-: | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **E1** | ToN-IoT `train_test_network`, CICIoT2023 `MERGED_CSV`, Edge-IIoTset `ML-EdgeIIoT` | Deduped stratified `70/15/15`; simulated `K=10` (IID vs `Dir(0.5/0.1)` + qty skew) (`23`) | Natural class distributions + **simulated** FL client partitions | Macro-F1, PR-AUC, FPR, client variance | Simulated gateways; raw duplication (`07`) | **CONDITIONAL** | Phase 2 dataset adapters & partitioner |
| **E2** | ToN-IoT `Processed_Network_dataset` (Protocols A/B/C) | Global chronological (`300s` + `ts+dur` embargo); simulated clients inside Train (`23`) | **Natural** abrupt novel-attack emergence + **synthetic** gradual/recurring drift (`17`) | Pre/post-drift Macro-F1, binary recall, FPR, recovery rounds | 18-day gap; 295x `src_ip` & 73x `http` shift (`16`) | **CONDITIONAL** | Phase 2 temporal splitter & synthetic drift module |
| **E3** | ToN-IoT `Processed_Network_dataset` (Period A + Period B normal) | Chronological (`300s` + `ts+dur`); benign-shifted vs poisoned clients (`23`) | **Natural (confounded)** Period B benign shift vs **simulated** FL poisoning (`17`) | Benign false-quarantine rate, poisoning TPR/FPR, clean F1 | Period B capture confounding; simulated poisoning (`16`, `17`) | **CONDITIONAL** | Phase 2 poisoning simulator & attribution module |
| **E4** | ToN-IoT, CICIoT2023, Edge-IIoTset | Same as E1; `10%–30%` Byzantine client fraction (`23`) | **Simulated** Byzantine attacks (sign-flip, noise, model replacement) | Robust-agg Macro-F1 vs `FedAvg`, ASR | Simulated FL adversary | **CONDITIONAL** | Phase 2 Byzantine simulator & robust aggregators |
| **E5** | CICIoT2023 + ToN-IoT + Edge-IIoTset | Cross-environment silos (1 dataset = 1 silo) (`23`) | **Natural** cross-dataset domain & taxonomy shift | Binary & coarse Macro-F1, domain-gap delta | Incompatible feature spaces (`03`, `04`) | **HOLD** | Versioned semantic feature & label ontology (`configs/datasets/label_taxonomy.yaml`) |
| **E6** | Verified manageable baselines (`train_test_network`, `ML-EdgeIIoT`, `Merged01`) | Simulated `K=10` logical gateways, fixed seeds (`23`) | Component ablations | Round wall-time, bytes/round, RAM, F1 delta | Hardware variance (logged in run JSON) | **PASS** | Ready for Phase 2 implementation |

---

## 4. Frozen `flow_extract_v1` Preprocessing Specification (`21`, `22`, `23`)

- **Frozen Decisions:**
  1. **Linktype & Containers:** `LINKTYPE_LINUX_SLL (113)` across `PCAPNG v1.0` and classic `libpcap v2.4`.
  2. **SLL `0x0003` & Non-IP Handling:** Explicitly drop and count `0x0003` (`ETH_P_ALL`, non-RFC `version=0` raw-socket frames), `ARP`, and unsupported EtherTypes (`21`).
  3. **Invalid / EOF Handling:** Drop single EOF-truncated trailing record in `normal_IoT_2/3` (`20`); drop non-initial IPv4/IPv6 fragments from 5-tuple TCP/UDP flows (`21`).
  4. **Flow Identity & Canonicalization:** Deterministic event identity `(stream_id, ts_start_us, canonical_5tuple, feature_hash)`; canonical bidirectional key `(min(E1, E2), max(E1, E2), l4_proto)` (`21`, `23`).
  5. **Missing-Value Semantics:** Explicit `null` for `iat_*` on 1-packet flows and `tcp_*` flags on UDP flows; never silently zero-fill (`22`).
  6. **Stream Separation:** Keep Stream A (`normal_1..13`) and Stream B (`normal_IoT_2..3`) strictly separated (`22`, `23`).
  7. **Temporal Split & Leakage Controls:** Chronological split **before** learned transformations or client partitioning; **`300s` embargo + `ts + duration` active-flow exclusion**; train-only fitting for all scalers, imputers, encoders, and selectors; strip all IPs, MACs, raw timestamps, and complementary targets (`07`, `23`).
  8. **Provenance:** Emit JSON sidecar recording archive SHA-256, `flow_extract_v1` version, drop counters, timeout config, and random seeds (`22`).
- **Provisional Decisions (To Lock in Phase 2 Configs):**
  - Default `idle_timeout_s` (`120s` baseline vs `600s` ablation; `22`).
  - Optional `900s` embargo sensitivity sweep (`23`).
  - Whether full-archive conversion of `normal_pcaps.zip` is needed beyond CSV baselines.

---

## 5. Research Limitations & Threats to Validity

| # | Limitation / Threat | Evidence Ref | Mandatory Mitigation / Explicit Disclosure |
| :-: | :--- | :--- | :--- |
| 1 | Missing genuine physical gateway IDs | `06`, `19`, `20` | Explicitly label all FL clients as **simulated logical gateways**. |
| 2 | Simulated FL clients & adversaries | `06`, `08`, `23` | Version all Dirichlet/quantity/Byzantine seeds and threat models in YAML. |
| 3 | Period B capture/campaign confounding (295x `src_ip`, 73x `http`) | `16` | Disclose explicitly in E2/E3; never claim unconfounded organic benign drift. |
| 4 | Limited natural drift (18-day gap; non-recurring attacks) | `10`, `13`, `17` | Pair natural abrupt emergence (Protocol B) with explicitly labeled synthetic drift (Protocol C). |
| 5 | Synthetic drift / poisoning assumptions | `13`, `17` | Keep natural-data metrics strictly separate from synthetic-intervention metrics. |
| 6 | Duplicate GT shard (`GroundTruth_Network_15 == 16`) | `11` | Deduplicate by shard SHA-256; use GT for provenance only, never as features. |
| 7 | Cross-dataset semantic incompatibility | `03`, `04` | Hold E5 until versioned feature/label ontology is approved; never merge on raw column names. |
| 8 | PCAP archive limitations (Period A only; `0x0003`; 2 corrupt 20 GB ZIPs) | `02`, `19`, `21` | Quarantine corrupt archives; filter `0x0003`; keep Stream A/B stratified. |
| 9 | Sample-based PCAP validation (`50k`–`200k` pkts/file) | `21`, `22` | Report sample bounds transparently; do not generalize prefix stats as full-archive totals. |
| 10 | Legitimate recurring IoT patterns (`99.25%` feature-sig match) | `23` | Deduplicate by event-level `(ts, 5-tuple, hash)`, never collapsing distinct timestamps. |

---

## 6. Final Phase 1 Gate Decisions

| Gate Dimension | Decision | Rationale |
| :--- | :---: | :--- |
| **Research Dataset Readiness** | **CONDITIONAL** | Intact ToN-IoT, CICIoT2023, Edge-IIoTset CSVs and `normal_pcaps.zip` verified; 2 corrupt 20 GB ToN-IoT archives remain on HOLD and upstream official manifests are unverified. |
| **E1–E6 Readiness** | **CONDITIONAL** | `E6: PASS`; `E1, E2, E3, E4: CONDITIONAL` (unblocked for Phase 2 coding); `E5: HOLD` pending semantic feature/label ontology. |
| **Preprocessing Readiness** | **PASS** | `flow_extract_v1` prototype validated deterministic (`22`); `300s + ts+dur` embargo and train-only leakage controls quantitatively verified (`23`). |
| **Phase 2 Implementation Readiness** | **CONDITIONAL (GO FOR MODULES 1–10 ON CSV BASELINES)** | Ready to begin Phase 2 software engineering under `src/dafidaf/` with E5 ontology and damaged 20 GB archives explicitly gated. |
