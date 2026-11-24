# Phase 3B — Full-Scale Experiments & Phase 3B.1 Independent Audit

Phase 3B executed `490` authorized Non-DP runs (`470` standalone `run_report.json` + `20` embedded E2 embargo sensitivity runs) across E1, E2, E3, E4, and E6 on overlapping ToN-IoT windows W1 and W3 (`K=10` simulated logical gateways, `n=5` seeds `[42, 101, 202, 303, 404]`). Experiment E5 was explicitly excluded (`HOLD`), and DP / Secure Aggregation were disabled.

Phase 3B.1 then independently recomputed raw metrics from disk, identifying 6 material audit findings (CRLF/LF checksum mismatch, W1 score inversion, E3 W3 `data_poisoning` blind spot, log-only E6 `without_attribution`, `n=5` bootstrap vs. Student-$t$ discrepancy, and `fig_E1_02`/`fig_E2_01` metadata discrepancies) that motivated Phase 3B.2.

---

## Phase 3B Design & Execution Reports

- [Phase 3B Dataset Selection & Split Plan](../../dataset/phase3/PHASE_3B_DATASET_SELECTION_AND_SPLIT_PLAN.md)
- [Phase 3B Experiment Design](../phase3/PHASE_3B_EXPERIMENT_DESIGN.md)
- [Phase 3B Final Experiment Protocol](../phase3/PHASE_3B_FINAL_EXPERIMENT_PROTOCOL.md)
- [Phase 3B Statistical Analysis Plan](../phase3/PHASE_3B_STATISTICAL_ANALYSIS_PLAN.md)
- [Phase 3B Figure & Table Standard](../phase3/PHASE_3B_FIGURE_AND_TABLE_STANDARD.md)
- [Phase 3B Execution Report](../phase3/PHASE_3B_EXECUTION_REPORT.md)
- [E1 Results](../phase3/PHASE_3B_E1_RESULTS.md) · [E2 Results](../phase3/PHASE_3B_E2_RESULTS.md) · [E3 Results](../phase3/PHASE_3B_E3_RESULTS.md) · [E4 Results](../phase3/PHASE_3B_E4_RESULTS.md) · [E6 Results](../phase3/PHASE_3B_E6_RESULTS.md)

## Phase 3B.1 Independent Audit Reports

- [Independent Audit Report](../phase3/PHASE_3B_1_INDEPENDENT_AUDIT_REPORT.md)
- [E1 Metric Verification](../phase3/PHASE_3B_1_E1_METRIC_VERIFICATION.md) · [E2 Drift Verification](../phase3/PHASE_3B_1_E2_DRIFT_VERIFICATION.md) · [E3 Attribution Verification](../phase3/PHASE_3B_1_E3_ATTRIBUTION_VERIFICATION.md) · [E4 Byzantine Verification](../phase3/PHASE_3B_1_E4_BYZANTINE_VERIFICATION.md) · [E6 Ablation Verification](../phase3/PHASE_3B_1_E6_ABLATION_VERIFICATION.md)
- [Figure Audit](../phase3/PHASE_3B_1_FIGURE_AUDIT.md) · [Statistical Reanalysis](../phase3/PHASE_3B_1_STATISTICAL_REANALYSIS.md) · [Reproducibility Report](../phase3/PHASE_3B_1_REPRODUCIBILITY_REPORT.md)
