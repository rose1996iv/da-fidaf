# DA-FIDAF Phase 3B.2 — E3 Attribution Improvement Evaluation (Workstream B)

- **Design:** Added leak-free server-side clean-validation loss probing (`client_val_loss_delta` evaluated strictly on balanced clean Validation subset `n = 1,000`, zero Test access, zero hidden attack labels) to `DriftAttackAttributor.attribute_round()` (`src/dafidaf/attribution/engine.py`).
- **Artifacts:** `40` new LF-canonical runs under `I:\Projects\da-fidaf-runs\phase3b_2\runs\e3_v2\` (sample run IDs: `20261124T083209_605909Z_e3v2_w1_label_flip_seed42_1c070f`, `20261124T083340_548193Z_e3v2_w3_data_poisoning_seed42_062dd6`); revised figure `fig_E3_02_attribution_v2.pdf`.

---

## 1. Measured Comparison: E3 v1 (Original Phase 3B) vs. E3 v2 (`val_loss_delta`, `n = 5` Seeds)

| Window & Arm | v1 Recall -> v2 Recall | v1 FAR -> v2 FAR | v2 Uncertain | v2 Pooled CM (`TP, FP, FN, TN`) | Benign-Drifted (`15` inst) Flagged Malicious |
| --- | --- | --- | --- | --- | --- |
| **W1 `label_flip`** | `0.300 -> 0.000` | `0.200 -> 0.575` | `0.400` | `0, 23, 10, 17` | `8 / 15` |
| **W1 `data_poisoning`** | `0.300 -> 0.200` | `0.275 -> 0.475` | `0.440` | `2, 19, 8, 21` | `6 / 15` |
| **W1 `backdoor`** | `0.100 -> 0.000` | `0.200 -> 0.525` | `0.420` | `0, 21, 10, 19` | `8 / 15` |
| **W1 `byzantine_sign_flip`** | `0.600 -> 0.300` | `0.275 -> 0.400` | `0.300` | `3, 16, 7, 24` | `4 / 15` |
| **W3 `label_flip`** | `0.800 -> 0.000` | `0.425 -> 0.575` | `0.420` | `0, 23, 10, 17` | `6 / 15` |
| **W3 `data_poisoning`** | **`0.000 -> 0.400`** | `0.225 -> 0.500` | `0.280` | **`4, 20, 6, 20`** | `5 / 15` |
| **W3 `backdoor`** | `0.800 -> 0.200` | `0.275 -> 0.525` | `0.360` | `2, 21, 8, 19` | `5 / 15` |
| **W3 `byzantine_sign_flip`** | `0.800 -> 0.300` | `0.350 -> 0.525` | `0.240` | `3, 21, 7, 19` | `5 / 15` |

---

## 2. Honest Scientific Verdict: **NEGATIVE NET REMEDIATION (DO NOT DEPLOY AS DEFAULT)**

1. **Targeted Hypothesis Partially Confirmed:** Clean-validation loss probing successfully broke the W3 `data_poisoning` `0.00` blind spot (`Recall: 0.000 -> 0.400`, `4 / 10` feature-noise poisoned clients detected despite elevated PSI).
2. **Severe Unintended Regression Observed:** Overall `FAR` worsened across every single arm (`0.400–0.575`), `4–8 / 15` benign-drifted clients were falsely flagged as `malicious_data_poisoning` (because benign covariate shift ALSO increases loss on an unadapted stationary Validation probe!), and `has_val_benign` suppressed valid angular detections on `label_flip`, `backdoor`, and `sign_flip`.
3. **Conclusion:** Naive single-round `val_loss_delta` thresholding is **empirically falsified** as a benign-drift-safe discriminator on real Non-IID ToN-IoT data. Future attribution research must separate covariate-shift loss increases from label-boundary corruption (e.g., via drift-compensated loss or multi-round client trajectories).
