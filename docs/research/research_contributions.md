# Research Contributions (Verified vs. Planned)

To maintain strict scientific honesty, contributions are separated into **already verified engineering/empirical artifacts** and **planned PhD research contributions** not yet completed.

---

## 1. Verified Engineering & Empirical Contributions (Phases 1–3B.2)

1. **Leakage-Controlled IoT Dataset Integrity & Temporal Audit:** 24 Phase 1 reports plus Phase 3A/3B split audits documenting ToN-IoT duplicate shards (`15`/`16`), chronological campaign confounding, active-flow exclusion, and embargo feasibility.
2. **Portable, Auditable Experimental Framework:** Modular Python 3.12 framework (`src/dafidaf/`) with train-only preprocessing, root-contained read-only dataset access, LF-canonical raw-byte SHA-256 run provenance (`canonical_sha256_manifest.json`), and `57` automated unit/integration tests.
3. **Diagnostic Proof of Linear IDS Feature Polarity Inversion under Campaign Shift (Workstream A):** Empirical demonstration on ToN-IoT W1 (`seed=42` checkpoint) that `8/8` active flow-volume features invert sign between `xss`-heavy training and `backdoor`-heavy testing (`Train AUC = 0.9339 -> Test AUC = 0.3208`), establishing a quantitative justification for non-linear local IDS models.
4. **Honest Empirical Falsification of Naive Clean-Validation Loss Probing under Benign Drift (Workstream B):** Demonstration that adding single-round `client_val_loss_delta` improves W3 `data_poisoning` recall (`0.00 -> 0.40`) while causing unacceptable FAR degradation (`0.400–0.575`) because benign covariate shift also elevates stationary validation loss.
5. **Verified Code-Isolated Closed-Loop Attribution Ablation (Workstream C):** Replacement of log-only ablation with a tested `attribution_filter` hook showing genuine closed-loop impact alongside transparent measurement of honest-client over-quarantine (`41%–45%` client-rounds).
6. **Small-Sample Paired Statistical Discipline (Workstream D):** Demonstration that `9` paired comparisons at `n=5` seeds change significance verdict between percentile bootstrap and exact Student-$t$ ($df=4$), establishing Student-$t$ as primary for publication reporting.

---

## 2. Planned Contributions (Not Yet Completed or Verified)

- Implementation and validation of the `1D-CNN / TCN` local IDS architecture depicted in Draft Diagram 2.
- Drift-compensated, multi-round attribution separating benign covariate shift from label/feature poisoning at low FAR and low honest-client over-quarantine.
- Graduated risk-aware aggregation (`Accept` / `Downweight` / `Hold` / `Quarantine`) beyond binary quarantine.
- Formal Differential Privacy (with cryptographic PRNG) and Secure Aggregation evaluation.
- Multi-dataset and cross-dataset generalization (CICIoT2023, Edge-IIoTset, and E5 once unblocked).
- Alignment sign-off against the original approved PhD research proposal.
