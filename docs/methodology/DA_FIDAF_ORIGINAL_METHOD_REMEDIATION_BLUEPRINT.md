# DA-FIDAF — Original Methodology Remediation Blueprint

> [!IMPORTANT]
> **Governance Gate:** This blueprint is a **planning document ONLY**. Per Phase 3B.2 safety controls, **DO NOT implement any step below without explicit user authorization** AND without first ingesting the original approved research proposal document to confirm Category A requirements.

---

## Stage 0 — Authoritative Proposal Ingestion (Mandatory Prerequisite)
- **Action:** User provides the original approved DA-FIDAF research proposal (PDF, DOCX, or LaTeX) into an immutable reference location (e.g., `docs/proposal/` or external reference path).
- **Exit Criterion:** Populate Category A citations (exact section, page, equation, figure) across `DA_FIDAF_ORIGINAL_METHODOLOGY_SPECIFICATION.md` and re-evaluate alignment from `INSUFFICIENT SOURCE EVIDENCE` to `ALIGNED` / `PARTIALLY ALIGNED` / `NOT ALIGNED`.

## Stage 1 — Model Expressivity & Feature Engineering (Addresses `GAP-02`)
- **Action:** Confirm proposal IDS backbone (e.g., PyTorch MLP / 1D-CNN / Tabular ResNet) behind existing `ModelInterface`; include categorical protocol/service/conn_state encodings fitted strictly on Train; evaluate on W1 (`xss -> backdoor`) to verify whether non-linear capacity resolves W1 `ROC-AUC = 0.32`.
- **Governance:** Any new dependencies (`torch`, `numpy`, `scikit-learn`) require explicit approval to update `pyproject.toml` and `uv.lock`.

## Stage 2 — Drift-Compensated Multi-Round Attribution (Addresses `GAP-03`)
- **Action:** Replace naive single-round `val_loss_delta` thresholding (empirically falsified in Phase 3B.2 E3 v2) with a drift-aware, multi-round attribution mechanism (e.g., comparing client loss deltas *after* covariate-shift reweighting or tracking client update trajectories across $k \ge 3$ rounds) and re-validate E3 + closed-loop E6 targeting `FAR < 0.10` under benign covariate shift.

## Stage 3 — Multi-Dataset Execution & E5 Ontology Alignment (Addresses `GAP-05`)
- **Action:** Run E1/E4/E6 on CICIoT2023 and Edge-IIoTset independently; author and formally approve `configs/datasets/label_taxonomy.yaml` (`verified_for_e5 = true`) + semantic feature alignment before unblocking E5.

## Stage 4 — Independent Privacy Track & Statistical Expansion (Addresses `GAP-04`, `GAP-06`, `GAP-07`)
- **Action:** Authorize dedicated simulation-grade RDP DP-utility sweeps (explicitly disclosing CSPRNG replacement if deployment DP is targeted) and/or Bonawitz SecAgg implementation if required by the original proposal; expand seed replication to `n = 10` for exact Student-$t$ ($df = 9$) statistical power; add adaptive Byzantine attacks (ALIE/Min-Max) and multi-round E2 adaptation evaluation.
