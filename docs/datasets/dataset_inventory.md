# Dataset Inventory

All raw and processed IoT datasets remain **permanently outside this Git repository** under the read-only external directory configured via `DAFIDAF_DATA_ROOT`. Only verified lightweight metadata manifests (`manifests/*.json`) and Phase 1 / Phase 3 audit reports are version-controlled.

---

## 1. Audited Dataset Families

| Dataset Family | Experimental Status in DA-FIDAF | Key Findings from Phase 1 / Phase 3 Audits | Primary Audit Report |
| --- | --- | --- | --- |
| **ToN-IoT (Network)** | **Primary Evaluated Dataset** (Phase 3A, 3B, 3B.2) | `23` shards in `Processed_Network_dataset`; Shards `15` and `16` are exact duplicates (excluded); strong chronological campaign-day confounding across Apr 24–29, 2019. | [Phase 3A.1 Consolidation](../dataset/phase3/PHASE_3A_1_DATASET_CONSOLIDATION.md) |
| **CICIoT2023** | Audited Only (**Not Yet Executed** in E1–E6) | `MERGED_CSV` lacks true wall-clock timestamps (`Time_To_Live` is IP TTL, not timestamp); unsuitable for real chronological drift without separate flow extraction. | [Phase 1 Report 05](../dataset/phase1/05_TEMPORAL_PROVENANCE_AND_DRIFT_FEASIBILITY.md) |
| **Edge-IIoTset** | Audited Only (**Not Yet Executed** in E1–E6) | Multi-class tabular IoT/IIoT traffic audited in Phase 1; cross-dataset alignment with ToN-IoT and CICIoT2023 requires formal ontology validation (`E5` on `HOLD`). | [Phase 1 Report 04](../dataset/phase1/04_LABEL_SEMANTICS_AND_MAPPING.md) |

---

## 2. Evaluated ToN-IoT Windows (Phase 3B & Phase 3B.2)

| Window ID | Shards Included | Total Evaluated Rows | Overlap Relationship | Embargo Checks |
| --- | --- | ---: | --- | --- |
| **W1** | Shards `22 + 23` | `89,269` | **Strict subset of W3 ($\text{W1} \subset \text{W3}$)** | `300s` & `900s` verified |
| **W3** | Shards `8–23` (excluding duplicate shard `16`) | `191,738` | **Superset containing W1** | `300s` & `900s` verified |

!!! danger "Non-Independence Rule"
    **W1 and W3 overlap.** They must **never** be pooled or presented as independent datasets or independent validation sets.

See [Phase 3B Dataset Selection and Split Plan](../dataset/phase3/PHASE_3B_DATASET_SELECTION_AND_SPLIT_PLAN.md) and the 24 Phase 1 reports under `docs/dataset/phase1/`.
