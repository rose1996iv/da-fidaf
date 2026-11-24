# DA-FIDAF Architecture and Research Figure Catalog (`FIG-01` – `FIG-10`)

!!! warning "Original Draft Architecture Diagrams Not Present in Repository"
    A complete inventory of `da-fidaf` and adjacent workspaces confirmed **zero** original architecture diagram image files (`.svg`, `.png`, `.pdf`, `.drawio`, `.vsdx`, `.pptx`) currently reside in the repository.
    Per strict scientific integrity rules, **no missing diagrams were fabricated, redrawn, or silently replaced**. The researcher must copy the original approved or draft diagram files into `docs/architecture/figures/` using the canonical identifiers below.

---

## Master Figure Registry (`FIG-01` – `FIG-10`)

| Figure ID | Title | Version | Research Component | Provenance / Source | Target Formats | Verification Status |
| --- | --- | --- | --- | --- | --- | --- |
| `FIG-01_overall_da_fidaf_architecture` | Overall DA-FIDAF Framework Architecture (Draft Diagram 1 & 2) | Draft v0 | End-to-end system | Researcher-supplied draft architecture diagrams (not yet copied into repo) | `.svg`, `.pdf`, `.png` | **PENDING — Researcher upload required** (Draft evidence only; not supervisor-approved) |
| `FIG-02_federated_learning_workflow` | Heterogeneous Federated Learning Round Workflow | Pending | Federated Learning | Pending approved diagram source | `.svg`, `.pdf`, `.png` | **PENDING — Researcher upload required** |
| `FIG-03_local_ids_architecture` | Local IDS Architecture (`1D-CNN / TCN` Draft vs. `LinearLogisticIDS` Baseline) | Draft v0 | Local IDS | Draft Diagram 2 depicts `1D-CNN / TCN`; current implementation is linear baseline | `.svg`, `.pdf`, `.png` | **PENDING — Researcher upload required** (Implementation alignment unverified) |
| `FIG-04_multi_evidence_attribution` | Multi-Evidence Update Analysis Pipeline | Draft v0 | Attribution Engine | Draft architecture diagrams (geometry, shift, model behavior, history) | `.svg`, `.pdf`, `.png` | **PENDING — Researcher upload required** |
| `FIG-05_drift_attack_decision` | Drift–Attack Decision Matrix (`Benign Drift` / `Uncertain` / `Malicious`) | Draft v0 | Attribution Engine | Draft architecture diagrams | `.svg`, `.pdf`, `.png` | **PENDING — Researcher upload required** |
| `FIG-06_risk_aware_aggregation` | Attribution-Guided Risk-Aware Robust Aggregation (`Accept` / `Downweight` / `Hold` / `Quarantine`) | Draft v0 | Robust Aggregation | Draft architecture diagrams | `.svg`, `.pdf`, `.png` | **PENDING — Researcher upload required** |
| `FIG-07_continual_adaptation_feedback` | Drift Detection & Continual Adaptation Feedback Loop | Draft v0 | Drift Adaptation | Draft architecture diagrams | `.svg`, `.pdf`, `.png` | **PENDING — Researcher upload required** |
| `FIG-08_experimental_workflow` | E1–E6 Experimental Pipeline & Provenance Architecture | Pending | Experiments | Pending diagram export from Phase 3B protocol | `.svg`, `.pdf`, `.png` | **PENDING — Researcher upload required** |
| `FIG-09_dataset_temporal_partitioning` | ToN-IoT Chronological Windows (W1 $\subset$ W3) & Embargo Splits | Pending | Datasets | Pending diagram export from Phase 3B split plan | `.svg`, `.pdf`, `.png` | **PENDING — Researcher upload required** |
| `FIG-10_phase3b2_results` | Phase 3B.2 Measured Experimental Results Suite (5 Verified IEEE Figures) | Rev. 2 (`2026-11-24`) | Experimental Results | Measured from `phase3b` & `phase3b_2` `run_report.json` via `plot_phase3b_2_revised_figures.py` | `.png` (docs copies in `docs/results/figures/`); canonical `.pdf`, `.eps`, `.png`, `.csv`, `.json` external | **VERIFIED — Measured Results** (see [Results Figure Catalog](../../results/figures/FIGURE_CATALOG.md)) |

---

## Metadata Standard for Future Uploaded Figures

Every diagram added to `docs/architecture/figures/` must record:

1. **Figure ID** (`FIG-XX_<slug>`)
2. **Title & Version** (explicitly distinguish `Draft` vs. `Supervisor-Approved` vs. `Measured`)
3. **Description & Research Component**
4. **Provenance / Source** (original authoring tool or plotting script + manifest SHA-256)
5. **Caption & Accessible Alt Text**
6. **File Formats** (`.svg` for docs, `.pdf`/`.eps` for publication, `.png` for GitHub previews)
7. **Verification Status** (never label draft diagrams as final approved architecture or verified implementation)
