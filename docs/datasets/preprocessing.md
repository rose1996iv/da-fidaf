# Preprocessing and Leakage-Control Pipeline

- **Implementation Modules:** `src/dafidaf/data/adapters.py`, `src/dafidaf/data/schemas.py`, `src/dafidaf/data/preprocessing.py`, `src/dafidaf/data/partitioning.py`
- **Engineering Spec:** [Data Pipeline Specification](../architecture/DATA_PIPELINE_SPECIFICATION.md)

---

## 1. Mandatory Leakage Controls

1. **Strict Chronological Splitting with Embargoes:** Chronological ordering uses validated numeric `ts` timestamps (unparseable/missing timestamps are rejected rather than coerced to epoch `0.0`, remediated in Phase 2.2) with `300s` or `900s` boundary embargoes and active-flow exclusion across split boundaries.
2. **Train-Only Preprocessing (`TrainOnlyPreprocessor`):** Median imputation and robust feature scaling are fitted strictly on training partitions and applied read-only to validation and test partitions.
3. **Zero Test Leakage in Threshold Calibration & Probing:** Decision threshold calibration (`val_calibrated_threshold`) and experimental Phase 3B.2 `client_val_loss_delta` probing use held-out **Validation** data only; Test splits are never accessed during training, attribution, or threshold selection.
4. **Root-Contained Read-Only Access:** `validate-dataset` and `run-experiment` reject any dataset path outside `DAFIDAF_DATA_ROOT` and never mutate source files.

---

## 2. Verified Active Numeric Features (ToN-IoT)

Phase 3B / 3B.2 binary IDS experiments operate on the 10 canonical ToN-IoT numeric flow features (`duration`, `src_bytes`, `dst_bytes`, `missed_bytes`, `src_pkts`, `src_ip_bytes`, `dst_pkts`, `dst_ip_bytes`, `http_request_body_len`, `http_response_body_len`), excluding identifier/leakage columns (IP addresses, ports, raw timestamps, and attack-type strings).
