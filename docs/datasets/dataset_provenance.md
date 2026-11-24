# Dataset Provenance and Integrity

DA-FIDAF enforces verified provenance before any dataset file enters an experiment pipeline (`src/dafidaf/data/provenance.py`).

---

## 1. Version-Controlled Provenance Manifests

Three lightweight JSON manifests verified during Phase 1 are tracked in `manifests/`:

| Manifest File | Purpose | Size |
| --- | --- | ---: |
| `manifests/dataset_inventory.json` | File inventory, archive integrity outcomes (`7z l`), row/label counts | `126,080` bytes |
| `manifests/ton_iot_temporal_audit.json` | Per-day timestamp ranges and attack-family campaign distributions | `15,689` bytes |
| `manifests/ton_iot_drift_analysis.json` | Feature-level drift statistics across ToN-IoT capture windows | `25,094` bytes |

---

## 2. Known Source Integrity Issues (Documented, Never Repaired In-Place)

- **Duplicate ToN-IoT Shards:** `Network_dataset_15.csv` and `Network_dataset_16.csv` are duplicates; Shard `16` is excluded in all Phase 3B / 3B.2 splits.
- **Damaged Archives & Raw PCAPs:** Damaged archives identified in [Phase 1 Report 02](../dataset/phase1/02_ARCHIVE_INTEGRITY_REPORT.md) and raw PCAP/PCAPNG collections (Reports 18–22) remain strictly external, read-only, and excluded from Git.
- **Original Dataset Sources:** Cite the respective dataset creators (ToN-IoT — Moustafa et al., UNSW Canberra; CICIoT2023 — Neto et al., Canadian Institute for Cybersecurity; Edge-IIoTset — Ferrag et al.) when publishing results. See [Citation Policy](../references/citation_policy.md).
