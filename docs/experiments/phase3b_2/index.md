# Phase 3B.2 — Targeted Remediation & Evidence Integration

**Verdict:** **`CONDITIONAL PASS`** (`60` new LF-canonical runs under `<DAFIDAF_RUNS_ROOT>/phase3b_2/`; `0` original Phase 3B artifacts modified; `0` E5/DP executions).

---

## Workstream Outcomes

- **Workstream A (E1 W1 Inversion):** Diagnosed `8/8` active flow-volume feature sign inversions between W1 Train (`xss`, `Train AUC = 0.9339`) and W1 Test (`backdoor`, `Test AUC = 0.3208`).
- **Workstream B (E3 v2 `client_val_loss_delta`):** **Negative net remediation — DO NOT DEPLOY AS DEFAULT.** Broke W3 `data_poisoning` blind spot (`0.000 -> 0.400` recall) but regressed FAR across all arms (`0.400–0.575`) and falsely flagged `4–8/15` benign-drifted clients.
- **Workstream C (E6 Genuine Closed-Loop Ablation):** Code-isolated `attribution_filter` verified (`0` calls vs. `24.8–27.2` client-rounds quarantined); selected metric gains observed under `sign_flip`, alongside transparent disclosure of honest-client over-quarantine (`41%–45%` vs. `20%` attackers).
- **Workstream D (Statistical Reanalysis):** `9` paired comparisons at `n=5` seeds changed from significant (bootstrap) to **non-significant** under exact Student-$t$ ($df=4$).
- **Workstream E (Revised IEEE Figures):** `5` revised/new IEEE figure sets (`36` files) generated in `<DAFIDAF_RUNS_ROOT>/phase3b_2/figures/`; lightweight preview PNG copies included in [Results Figures](../../results/figures/FIGURE_CATALOG.md).
- **Workstream F (Canonical SHA-256 Manifest):** `578` files hashed (`470/470` original Phase 3B LF-verified intact; `60/60` Phase 3B.2 raw-byte LF-verified `100%`).

---

## Phase 3B.2 Reports

- [Remediation Report](../phase3/PHASE_3B_2_REMEDIATION_REPORT.md)
- [E1 W1 Domain-Shift Diagnostics](../phase3/PHASE_3B_2_E1_DOMAIN_SHIFT_DIAGNOSTICS.md)
- [E3 Attribution Improvement](../phase3/PHASE_3B_2_E3_ATTRIBUTION_IMPROVEMENT.md)
- [E6 Genuine Ablation Validation](../phase3/PHASE_3B_2_E6_ABLATION_VALIDATION.md)
- [Statistical Reanalysis](../phase3/PHASE_3B_2_STATISTICAL_REANALYSIS.md)
- [Publication Asset Revision](../phase3/PHASE_3B_2_PUBLICATION_ASSET_REVISION.md)
- [Integrity Manifest Report](../phase3/PHASE_3B_2_INTEGRITY_MANIFEST_REPORT.md)
- [Independent Technical Review](../phase3/PHASE_3B_2_INDEPENDENT_REVIEW.md)
