# DA-FIDAF Phase 3B.1 — E4 Independent Byzantine Robustness Verification

- **Scope:** All `250` E4 raw `run_report.json` files (`125` W1 + `125` W3; `5` attacks × `5` aggregators × `5` seeds × `2` windows).
- **Equivalence Audit (`PASS`):** Code inspection of `run_phase3b_e3_e4_e6.py` lines 166–181 confirms `clients_by_seed[seed]` is pre-built once per seed and shared identically across all 5 aggregators (`fedavg`, `median`, `trimmed_mean`, `krum`, `multi_krum`), with identical `f = 2` compromised clients (`20%` of `K = 10`, satisfying $n \ge 2f + 3$). Note: `FedProx` (`proximal_mu > 0`) was **not** configured in E4 (matching `e4_byzantine_robust_agg.yaml`, where `FedProx` is tested in E1 only).

---

## 1. Independent Verification Summary

- **CM-to-Metric Accuracy:** `0 / 250` discrepancies between raw confusion matrices and reported Macro-F1 / FPR / FNR.
- **Aggregation Failures:** `0` crashes or `NaN` parameter outputs across all `250` runs.
- **`NaN` Quarantine Verified (`50 / 50` `nan_poison` runs):** Every `nan_poison` run reported `rejected_nonfinite_total == 10` (`2` malicious clients × `5` active attack rounds `2..6`). **Audit Caveat:** Input sanitization (`NaN`/`Inf` quarantine) is a basic defensive hygiene control and MUST NOT be equated with resistance to subtle, finite adaptive Byzantine attacks (e.g., ALIE or inner-product manipulation).

---

## 2. Key Verified Findings (Window-Separated)

1. **W3 Ranking Protection Verified:** Under `sign_flip` and `model_replacement` on W3, unprotected `FedAvg` dropped to `ROC-AUC = 0.629` and `0.573`, respectively, whereas `Multi-Krum` maintained `0.796` (`+0.167` under `sign_flip`) and `Trimmed Mean` maintained `0.842` (`+0.269` under `model_replacement`). Note that Val-calibrated `Macro-F1` differences on W3 had wide `n=5` CIs crossing `0` (`Trimmed Mean vs FedAvg: +0.014, 95% CI [-0.198, +0.188]`) due to W3 Val→Test calibration shift, so ranking `ROC-AUC` is the cleaner signal of Byzantine defense on W3.
2. **W1 `model_replacement` FedAvg Anomaly (`0.971` Macro-F1 / `0.962` AUC) Verified Authentic:** Recalculation confirms `FedAvg` jumped to `0.971` solely because `model_replacement` negated the inverted W1 `xss`-trained weights (`AUC = 0.319`), accidentally matching Test `backdoor`. All 4 robust aggregators successfully rejected the replacement update and remained tightly bounded (`SD = 0.013–0.058`, vs FedAvg `SD = 0.202` under `sign_flip`).
3. **Limitation:** Adaptive attacks targeting Krum/Trimmed-Mean specifically (e.g., Little Is Enough / Min-Max / Min-Sum) were not part of the Phase 3B attack grid and remain future work.
