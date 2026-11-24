# DA-FIDAF — Data Pipeline Specification

## 1. Design Principles

The DA-FIDAF data pipeline (`src/dafidaf/data/`) enforces the leakage, provenance, and archive-safety rules established during Phase 1A–1I:

1. **Strict Read-Only Access**: All adapters read exclusively from `DAFIDAF_DATA_ROOT` without extracting, renaming, modifying, or repairing any dataset file or archive.
2. **Path-Traversal Guard**: Every file path resolved by an adapter is canonicalized and verified to reside within the configured dataset root.
3. **No Identifier Leakage**: Network identifiers (`src_ip`, `dst_ip`, raw timestamps `ts`) are excluded from numeric model features.
4. **Fit-on-Train-Only Preprocessing**: Imputation medians/means and feature standardization statistics are computed exclusively on the Train split.
5. **Fail-Closed Cross-Dataset Gate**: Attempting to run cross-dataset E5 experiments raises `E5OntologyBlockedError` unless an approved ontology mapping is explicitly supplied.

---

## 2. Dataset Adapters (`src/dafidaf/data/adapters.py`)

| Adapter | Target Dataset Family | Primary Role | Sanitization |
| --- | --- | --- | --- |
| `TonIoTNetworkAdapter` | ToN-IoT `Processed_Network_dataset` (`Network_dataset_1..23.csv`) | Primary chronological FL benchmark (E1–E4, E6) | Parses `ts` epoch, strips IPs, replaces `inf`/`-inf`/`NaN`, maps binary & multi-class `type` |
| `CICIoT2023Adapter` | CICIoT2023 CSV files | Secondary high-volume benchmark / future E5 | Replaces `inf`/`NaN`, normalizes attack family labels |
| `EdgeIIoTsetAdapter` | Edge-IIoTset CSV files | Secondary IoT/IIoT benchmark / future E5 | Strips network identifiers, normalizes `Attack_type` |

---

## 3. Flow Extraction (`src/dafidaf/data/flow_extract.py` — `flow_extract_v1`)

Implements the Phase 1G validated specification for streaming PCAPNG files directly from `normal_pcaps.zip` without archive extraction:

- **Link-Layer Support**: `LINKTYPE_LINUX_SLL (113)` with 16-byte cooked-capture header parsing.
- **Explicit Exclusion Counters**: Tracks and excludes `0x0003` (`ETH_P_ALL` non-IP/cooked control frames), ARP (`0x0806`), non-IPv4/IPv6 frames, malformed/truncated trailing records, and IP fragments.
- **Bidirectional Canonical 5-Tuple**: Normalizes `(src_ip, src_port, dst_ip, dst_port, proto)` by lexicographic endpoint ordering so forward and reverse packets aggregate into a single flow record.
- **Timeouts**: Deterministic inactive (idle) timeout (`120s` default) and active timeout (`600s` default) with explicit flush at end-of-stream (matching Phase 1G).
- **Provenance Sidecar**: Records archive SHA-256, member name, parser version (`flow_extract_v1`), and per-category packet disposition counts.

---

## 4. Temporal Splitting, Deduplication & FL Partitioning (`src/dafidaf/data/partitioning.py`)

### 4.1 Chronological Split (`chronological_split`)
- Sorts records strictly by timestamp `ts`.
- Default ratios: **70% Train / 15% Validation / 15% Test**.
- **Boundary Buffer Gap**: Configurable gap (`300s` or `900s`) between Train→Val and Val→Test boundaries; records falling inside the buffer window are excluded and counted.
- **Active-Flow Exclusion**: Any flow whose interval `[ts, ts + duration]` crosses a split boundary is excluded to eliminate temporal flow leakage.

### 4.2 Flow Deduplication (`deduplicate_event_flows`)
- Computes deterministic event-level flow fingerprints (canonical 5-tuple + quantized start timestamp + packet/byte counts) to suppress duplicate observations caused by overlapping capture streams.

### 4.3 Federated Client Partitioning (`partition_fl_clients`)
- Executed **strictly inside the Train split** so Validation and Test remain clean global evaluation sets.
- All generated clients receive synthetic gateway IDs (`sim_gw_00`, `sim_gw_01`, ...) because Phase 1 proved real hardware gateway identity is absent in ToN-IoT CSVs.
- Supported regimes:
  - `iid`: Uniform stratified shuffle across clients.
  - `label_skew`: Dirichlet allocation (`alpha`, e.g., `0.5` or `0.1`).
  - `feature_skew`: Deterministic feature-quantile / cluster assignment.
  - `quantity_skew`: Power-law / Dirichlet sample count imbalance.
  - `combined`: Joint label + quantity heterogeneity.

---

## 5. Preprocessing (`src/dafidaf/data/preprocessing.py`)

`TrainOnlyPreprocessor`:
- `fit(x_train)`: Computes per-feature finite median (imputation) and mean/std (with zero-variance floor `1e-8`).
- `transform(x)`: Applies frozen Train statistics to Train, Val, or Test.
- Raises `RuntimeError` if `transform()` is called before `fit()` or if an attempt is made to re-fit on a split tagged as `val` or `test`.
