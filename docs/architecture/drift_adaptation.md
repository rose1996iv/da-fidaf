# Drift Monitoring and Continual Adaptation

- **Implementation Module:** `src/dafidaf/drift/core.py`
- **Related Reports:** [Phase 3B E2 Results](../experiments/phase3/PHASE_3B_E2_RESULTS.md), [Phase 3B.1 E2 Drift Verification](../experiments/phase3/PHASE_3B_1_E2_DRIFT_VERIFICATION.md)

---

## 1. Local Drift Monitoring

- Computes feature distribution shift (Population Stability Index, Kolmogorov–Smirnov statistics) and streaming change detection (Page–Hinkley test) to raise local drift flags without sharing raw client data.
- In the draft framework architecture, local drift monitoring informs both local adaptation and server-side multi-evidence attribution so benign distribution shifts are distinguished from poisoning attacks.

---

## 2. Continual Adaptation & Replay Mechanism

- Uses bounded class-balanced replay buffers (`src/dafidaf/drift/core.py`) to retain historical normal and attack patterns while adapting to new traffic distributions.
- **Experiment E2 Summary:** Evaluated controlled synthetic gradual and abrupt drift interventions (`is_synthetic=True`) on ToN-IoT W1 and W3 under `300s` and `900s` chronological embargoes (`30` plotted W1 runs in `fig_E2_01_drift_timeline_rev2`).

---

## 3. Known Limitations

- Real ToN-IoT benign drift across capture periods is confounded with capture-vantage and campaign timing (documented in Phase 1 Reports 14–17); therefore, E2 uses explicitly labeled controlled synthetic drift interventions (`is_synthetic=True`) layered over real ToN-IoT splits.
- Phase 3B E2 evaluated post-drift adaptation at round 8 only, limiting full multi-round recovery trajectory characterization (`GAP-07`).
- The `20` embargo sensitivity runs in Phase 3B were embedded in master summaries rather than standalone `run_report.json` files (documented in [Phase 3B.1 Independent Audit](../experiments/phase3/PHASE_3B_1_INDEPENDENT_AUDIT_REPORT.md)).
