# DA-FIDAF — Phase 3B.2 Targeted Remediation Report

- **Evidence Manifest:** `I:\Projects\da-fidaf-runs\phase3b_2\PHASE_3B_2_EVIDENCE_MANIFEST.json` (`60` new targeted runs: `40` E3 v2 + `20` E6 genuine ablation; `0` failures; `0` original Phase 3B outputs modified).
- **Canonical Checksum Manifest:** `I:\Projects\da-fidaf-runs\phase3b_2\canonical_sha256_manifest.json` (`578` total files hashed).
- **Revised IEEE Publication Assets:** `I:\Projects\da-fidaf-runs\phase3b_2\figures\` (`36` files; original `figures\phase3b\` preserved untouched).
- **Final Phase 3B.2 Verdict:** **`CONDITIONAL PASS`** *(Workstreams A, C, D, E, and F succeeded with verifiable evidence; Workstream B proved `val_loss_delta` detects W3 feature-noise poisoning `0.00 -> 0.40` but failed to improve net FAR/Recall, which is reported transparently as a negative remediation result rather than concealed. Phase 4 is NOT started automatically.)*

---

## Workstream Summary

| Workstream | Objective | Outcome | Primary Evidence |
| --- | --- | --- | --- |
| **A — E1 W1 Inversion** | Diagnose W1 `ROC-AUC = 0.3208` without altering scores | **RESOLVED (Diagnosed)** | `8/10` numeric features invert sign between Train (`xss`, `Train AUC=0.9339`) and Test (`backdoor`, `Test AUC=0.3208`) |
| **B — E3 Attribution v2** | Evaluate leak-free `client_val_loss_delta` probing | **PARTIAL / NEGATIVE NET RESULT** | W3 `data_poisoning` Recall `0.00 -> 0.40`, but FAR rose `0.20–0.43 -> 0.40–0.58` due to benign-drift Val-loss sensitivity |
| **C — E6 Genuine Ablation** | Replace log-only `without_attribution` with real quarantine | **RESOLVED (Verified)** | `0` calls / `0` quarantined in `without_attribution` vs `24.8–27.2` client-rounds quarantined in `full_closed_loop` (+0.124 W1 F1, +0.196 W3 AUC; benign over-quarantine disclosed) |
| **D — Statistical Reanalysis** | Paired Student-$t$ ($df=4$) + 5,000-bootstrap CIs | **RESOLVED** | `9` comparisons changed significance verdict between bootstrap and exact $t_4$ |
| **E — IEEE Figure Revision** | Fix `fig_E1_02` `run_ids=70` & dual-window `n_samples` | **RESOLVED** | `5` revised/new figure sets (`36` files) in `phase3b_2\figures\` |
| **F — Checksum Protocol** | Canonical raw-byte SHA-256 manifest + LF fix in `runner.py` | **RESOLVED** | `470/470` orig LF-verified; `60/60` Phase 3B.2 raw-byte LF-verified (`100%`) |
