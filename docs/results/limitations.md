# Results Limitations, Negative Findings, and Statistical Caveats

Every claim derived from Phase 3A, Phase 3B, and Phase 3B.2 artifacts must carry the following empirically verified caveats:

1. **W1 Score Inversion (E1):** W1 achieved `Test ROC-AUC = 0.320810` despite `Train ROC-AUC = 0.933945` because `8/8` active flow-volume features inverted polarity between `xss`-heavy Train and `backdoor`-heavy Test. Scores were never flipped post-hoc.
2. **E3 v2 Attribution Regression (Workstream B):** Adding single-round `client_val_loss_delta` probing broke the W3 `data_poisoning` blind spot (`0.000 -> 0.400`), but regressed FAR to `0.400–0.575`, falsely flagged `4–8/15` benign-drifted clients, and reduced recall on `label_flip` (`0.80 -> 0.00`), `backdoor` (`0.80 -> 0.20`), and `sign_flip` (`0.80 -> 0.30`). **It must not be used as the default attribution policy.**
3. **E6 Closed-Loop Over-Quarantine (Workstream C):** Although `full_dafidaf_closed_loop` excluded both true attackers (`sim_gw_01`, `sim_gw_02`), it also quarantined `2–3` honest Non-IID clients per round (`24.8–27.2 / 60` client-rounds = `41.3%–45.3%` vs. `20%` true attackers).
4. **Statistical Reanalysis — 9 Flipped Verdicts (Workstream D):** At `n=5` seeds, percentile bootstrap CIs are anti-conservative. Switching to exact two-sided paired Student-$t$ ($df=4, t_{0.975,4}=2.776445$) flipped **9 comparisons** from "significant" to **non-significant**, including `E1_W1_fedprox_vs_fedavg_a01_f1`, `E1_W3_fedprox_vs_fedavg_a05_f1`, `E4_W3_mkrum_vs_fedavg_signflip_auc`, and `E6_W3_closedloop_vs_noattr_auc`.
5. **Overlapping Windows (`W1 ⊂ W3`):** W1 (`Shards 22+23`) is strictly contained within W3 (`Shards 8–23`). They are not independent datasets or independent validation splits.
6. **Simulated Logical Gateways:** `K=10` partitions emulate heterogeneous gateways in software; desktop Python 3.12 runtimes (`15–38s`) do not represent embedded IoT/IIoT hardware latency or power budgets.
7. **Non-DP Only & Unexecuted E5:** Zero Differential Privacy or Secure Aggregation experiments ran in Phase 3B / 3B.2. Experiment E5 remains on `HOLD`.
8. **Linear IDS vs. Draft `1D-CNN / TCN`:** Current results reflect `LinearLogisticIDS`, not the `1D-CNN / TCN` depicted in Draft Diagram 2.
9. **Missing Original Proposal (`GAP-01`):** Methodology alignment remains `INSUFFICIENT SOURCE EVIDENCE` until the original approved PhD research proposal is provided.

For full statistical tables, see [Phase 3B.2 Statistical Reanalysis](../experiments/phase3/PHASE_3B_2_STATISTICAL_REANALYSIS.md) and [Phase 3B.2 Independent Review](../experiments/phase3/PHASE_3B_2_INDEPENDENT_REVIEW.md).
