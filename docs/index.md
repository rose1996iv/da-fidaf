# DA-FIDAF — Drift-Aware Federated Intrusion Detection and Attribution Framework

**Research Status:** `Active PhD Research — Experimental Validation and Development`

> **A robust, privacy-preserving, and continually adaptive federated intrusion detection framework for heterogeneous IoT/IIoT networks under Non-IID data, concept drift, and adversarial threats.**

!!! warning "Mandatory Research Status & Scope Disclosures"
    - **Phase 3B.2 Remediation Verdict:** **Conditional Pass** — engineering, integrity, statistical, and closed-loop ablation goals succeeded, while the experimental `E3 v2` attribution variant (`client_val_loss_delta`) produced a net false-alarm regression and is **not approved as default**.
    - **Original Methodology Alignment:** **Insufficient Source Evidence** — the original approved PhD proposal document has not yet been located in the workspace; the two latest draft architecture diagrams are treated strictly as draft-level evidence.
    - **Model Architecture Disclosure:** The current codebase implements a baseline linear classifier (`LinearLogisticIDS`); the `1D-CNN / TCN` local IDS depicted in Draft Diagram 2 has **not** yet been implemented or experimentally validated.
    - **Privacy & Cross-Dataset Boundaries:** Phase 3B and Phase 3B.2 executed **Non-DP baselines only** (`dp_enabled=False`, `secure_aggregation_active=False`). Experiment **E5** (cross-dataset generalization) remains on **`HOLD`** and has **not** been executed.
    - **Dataset & Client Boundaries:** ToN-IoT windows **W1** (Shards 22–23) and **W3** (Shards 8–23) **overlap** ($\text{W1} \subset \text{W3}$) and are never independent validation sets. Clients (`K=10`) are **simulated logical gateways**, not physical edge deployments.

---

## Research Progress Overview

| Research Phase | Scope | Current Status | Primary Reference |
| --- | --- | --- | --- |
| **Phase 1** | Multi-dataset inventory, archive integrity, schema, temporal provenance (24 reports) | Completed | [Phase 1 Readiness Gate](dataset/phase1/24_PHASE_1_RESEARCH_READINESS_GATE.md) |
| **Phase 2 / 2.1 / 2.2** | Modular Python framework, independent technical audit, security remediation | Completed | [Phase 2.2 Acceptance Gate](architecture/PHASE_2_2_ACCEPTANCE_GATE_REPORT.md) |
| **Phase 3A / 3A.1** | Real-dataset pilot validation and diagnostic audit on ToN-IoT | Completed | [Phase 3A Pilot Overview](experiments/phase3a/index.md) |
| **Phase 3B / 3B.1** | Full-scale E1, E2, E3, E4, E6 Non-DP experiments (`490` runs) & independent audit | Completed & Audited | [Phase 3B Overview](experiments/phase3b/index.md) |
| **Phase 3B.2** | Targeted remediation (`60` new runs), statistical reanalysis, IEEE figure revision | **Conditional Pass** | [Phase 3B.2 Overview](experiments/phase3b_2/index.md) |
| **Methodology Alignment** | Verification against original approved PhD research proposal | **Insufficient Source Evidence** | [Alignment Verdict](methodology/DA_FIDAF_METHODOLOGY_ALIGNMENT_VERDICT.md) |
| **Phase 4** | Proposal-aligned architecture (`1D-CNN / TCN`), DP/SecAgg, E5 unblocking | **Not Authorized / Pending** | [Remediation Blueprint](methodology/DA_FIDAF_ORIGINAL_METHOD_REMEDIATION_BLUEPRINT.md) |

---

## Navigation Map

- **Research Framing:** [Research Overview](research/research_overview.md), [Problem Statement](research/problem_statement.md), [Objectives](research/research_objectives.md), [Questions](research/research_questions.md), [Scope & Limitations](research/scope_and_limitations.md).
- **Architecture:** [System Architecture](architecture/system_architecture.md), [Local IDS](architecture/local_ids.md), [Attribution Engine](architecture/attribution_engine.md), [Risk-Aware Aggregation](architecture/risk_aware_aggregation.md), [Figure Catalog](architecture/figures/FIGURE_CATALOG.md).
- **Datasets & Protocol:** [Dataset Inventory](datasets/dataset_inventory.md), [Data Governance](datasets/data_governance.md), [Experimental Protocol](experiments/experimental_protocol.md).
- **Verified Results & Caveats:** [Results Overview](results/results_overview.md), [Limitations](results/limitations.md), [Results Figures](results/figures/FIGURE_CATALOG.md).
- **Developer & Reproducibility Guides:** [Installation](development/installation.md), [Configuration](development/configuration.md), [Running Experiments](development/running_experiments.md), [Testing](development/testing.md).
- **Repository Governance:** [Git Baseline Preservation](repository/GIT_BASELINE_PRESERVATION_REPORT.md), [Security Audit](repository/REPOSITORY_SECURITY_AUDIT.md), [Release Readiness](repository/REPOSITORY_RELEASE_READINESS.md).
