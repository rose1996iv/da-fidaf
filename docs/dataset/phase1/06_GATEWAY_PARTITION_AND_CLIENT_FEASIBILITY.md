# 06 — Gateway Partition and FL Client Feasibility (DA-FIDAF Phase 1 Part A)

- **Audit Timestamp (UTC):** `2026-11-24T03:20:51Z`
- **Methodological Requirement:** Federated Learning client unit is the IoT gateway. Logical/emulated gateway partitions are permitted only when genuine gateway identifiers are unavailable and **must be explicitly reported as simulated**.

## 1. Identifier Evidence Across All Three Families (VERIFIED)

| Dataset Family | Genuine `gateway_id`? | Observed Host / Device / Network Identifiers | Cardinality in 5,000-Row Sample | Genuine Gateway Partitioning? |
| :--- | :---: | :--- | :--- | :---: |
| **CICIoT2023** | **No** | None (only `IPv` protocol indicator; no IP, MAC, gateway, or device ID) | N/A | **NOT SUPPORTED** (Simulated only) |
| **ToN-IoT (Network)** | **No** | `src_ip`, `dst_ip`, `src_port`, `dst_port` | `train_test_network.csv`: `3` unique `src_ip`, `5` unique `dst_ip`; `Network_dataset_1.csv`: `16` unique `src_ip`, `15` unique `dst_ip` | **NOT SUPPORTED** (IP-grouped or Dirichlet simulated clients only) |
| **ToN-IoT (IoT Telemetry)** | **No** | File-level separation by 7 IoT device types (`Fridge`, `Garage_Door`, `GPS_Tracker`, `Modbus`, `Motion_Light`, `Thermostat`, `Weather`) | 1 device type per file; **heterogeneous feature schemas across devices** | **PARTIAL / NON-UNIFORM** (different feature spaces per sensor) |
| **Edge-IIoTset** | **No** | `ip.src_host`, `ip.dst_host`, `arp.src.proto_ipv4`, `arp.dst.proto_ipv4`; 10 sensor folders under `Normal traffic/` | `ML-EdgeIIoT-dataset.csv`: `7` unique `ip.src_host`, `7` unique `ip.dst_host`; `MITM_attack.csv`: `1` unique `ip.dst_host` | **NOT SUPPORTED** (Simulated only) |

## 2. Scientific Implications for DA-FIDAF

1. **No Genuine Gateway IDs Exist Locally (VERIFIED):** None of the three locally audited datasets provides an explicit, verified gateway identifier mapping multi-device subnetworks to physical IoT gateways. This independently confirms the **HISTORICAL** finding in `_dataset_audit/06_DAFIDAF_EXPERIMENT_SUITABILITY.md`.
2. **Low IP Cardinality Prevents Naive IP-as-Gateway Partitioning (VERIFIED):**
   - In `train_test_network.csv` (first 5,000 rows), only `3` unique `src_ip` values appear; in `ML-EdgeIIoT-dataset.csv` (first 5,000 rows), only `7` unique `ip.src_host` values appear.
   - In `Edge-IIoTset`, `Normal traffic/` is organized by 10 IoT sensor types while `Attack traffic/` is organized by 14 attack types (not per-gateway capture).
3. **Mandatory Simulation Protocol (INFERRED):**
   - For E1, E4, and E6, federated clients must be constructed using **explicitly documented, seed-controlled simulated logical gateway partitions** (e.g., Dirichlet label-skew `Dir(alpha)` for Non-IID vs. stratified IID, or documented cross-silo partitioning where each dataset family acts as an independent environment silo in E5).
   - Every publication table, experiment config, and PhD methodology section must explicitly state that gateway partitions on CICIoT2023, ToN-IoT, and Edge-IIoTset are **simulated logical gateways**, never claiming physical gateway provenance.
