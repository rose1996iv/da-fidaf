# DA-FIDAF System Architecture

!!! warning "Draft Architecture vs. Current Implementation"
    This page documents **both** (1) the latest **draft-level conceptual architecture** described in the researcher's two draft framework diagrams (treated strictly as draft evidence, **not** proof of supervisor approval or completed implementation), and (2) the **currently verified codebase implementation** under `src/dafidaf/`.

---

## 1. Draft Framework Pipeline vs. Verified Implementation Status

| Draft Architecture Stage | Draft Framework Description | Current Codebase Module | Verification Status |
| --- | --- | --- | --- |
| **1. Heterogeneous IoT/IIoT Clients** | Distributed heterogeneous IoT/IIoT gateways | `src/dafidaf/data/partitioning.py` (`K=10` simulated logical gateways) | **Simulated Only** (not physical gateways) |
| **2. Local Data Preparation & IDS Training** | Train-only preprocessing + local `1D-CNN / TCN` IDS (Draft Diagram 2) | `src/dafidaf/data/preprocessing.py` + `src/dafidaf/models/logistic.py` (`LinearLogisticIDS`) | **Partial / Divergent** (`1D-CNN / TCN` NOT implemented) |
| **3. Local Drift Monitoring** | Client-side covariate & performance drift monitoring | `src/dafidaf/drift/core.py` (PSI / KS / Page-Hinkley) | **Implemented (Baseline)** |
| **4. Multi-Evidence Update Analysis** | Update geometry + distribution-shift evidence + model behavior + historical client behavior | `src/dafidaf/attribution/engine.py` | **Partial / Experimental** (`val_loss_delta` v2 regressed FAR) |
| **5. Drift–Attack Attribution** | `Benign Drift` / `Uncertain` / `Malicious` classification | `src/dafidaf/attribution/engine.py` (`DriftAttackAttributor`) | **Implemented (Baseline — High FAR under Benign Drift)** |
| **6. Risk-Aware Decision Actions** | Graduated `Accept` / `Downweight` / `Hold` / `Quarantine` | `src/dafidaf/federated/trainer.py` (`attribution_filter`, binary quarantine only) | **Partial** (`Downweight`/`Hold` not yet implemented) |
| **7. Attribution-Guided Robust Aggregation** | Risk-aware robust aggregation (`FedAvg`, `Median`, `Trimmed Mean`, `Multi-Krum`, `FedProx`) | `src/dafidaf/federated/aggregation.py` | **Implemented (Non-DP Baseline)** |
| **8. Drift Adaptation & Feedback** | Continual adaptation, replay, and feedback loop | `src/dafidaf/drift/core.py` (replay buffer) | **Implemented (Baseline)** |
| **9. Global IDS Distribution & Edge Monitoring** | Broadcast updated global IDS model to gateways for local inference | `src/dafidaf/federated/trainer.py` & `src/dafidaf/evaluation/metrics.py` | **Simulated Evaluation Only** |
| **10. Privacy Mechanisms** | Differential Privacy / Secure Aggregation | `src/dafidaf/privacy/mechanisms.py` (prototype DP, non-crypto PRNG; SecAgg unimplemented) | **Not Executed in Phase 3B / 3B.2** |

---

## 2. Conceptual Data-Flow Reference

The two latest draft architecture diagram files are **not currently stored in this repository** (`docs/architecture/figures/`). Once the researcher copies the original approved/draft diagram files into `docs/architecture/figures/`, they will be linked directly here under `FIG-01_overall_da_fidaf_architecture` (see [Architecture Figure Catalog](figures/FIGURE_CATALOG.md)).

For existing low-level engineering specifications implemented in Phases 2–2.2, refer to:

- [Portable Architecture](PORTABLE_ARCHITECTURE.md)
- [Data Pipeline Specification](DATA_PIPELINE_SPECIFICATION.md)
- [Federated Learning Specification](FEDERATED_LEARNING_SPECIFICATION.md)
- [Drift & Attack Attribution Specification](DRIFT_AND_ATTACK_ATTRIBUTION_SPECIFICATION.md)
- [Evaluation Protocol](EVALUATION_PROTOCOL.md)
- [Architecture Alignment Audit](../methodology/DA_FIDAF_ARCHITECTURE_ALIGNMENT_AUDIT.md)
