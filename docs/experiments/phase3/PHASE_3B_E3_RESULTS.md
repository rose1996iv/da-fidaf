# DA-FIDAF Phase 3B — E3 Results (Benign Drift vs. Poisoning Attribution)

- **Execution Scope:** Authorized Phase 3B Non-DP baseline (`dp_enabled = False`), `K = 10` simulated logical gateways (`label_skew`, Dirichlet $\alpha = 0.5$), `6` rounds, `5` seeds `[42, 101, 202, 303, 404]`.
- **Threat Setup:** `20%` compromised (`sim_gw_01`, `sim_gw_02`, active throughout training for data poisoning or from round 2 for Byzantine sign-flip) concurrently with `30%` benign-drifted clients (`sim_gw_03..05` receiving labeled synthetic covariate shift, `severity = 1.8`).
- **Detector Isolation Verified:** `DriftAttackAttributor.attribute_round()` received ONLY client updates and per-client feature PSI — **zero hidden attack labels** were passed to the model or attributor.
- **Artifacts:** `I:\Projects\da-fidaf-runs\phase3b\e3\` & `e3_master_summary.json` (`40` runs: `20` W1 + `20` W3; `0` failed).
- **IEEE Figure:** `I:\Projects\da-fidaf-runs\figures\phase3b\fig_E3_01_attribution_tradeoff.*`.

---

## 1. Window W1 Attribution Results (`Shards 22+23`, `n = 5` Seeds)

| Intervention Arm | Malicious Precision | Malicious Recall | Malicious F1 | False Attribution Rate (FAR) | Uncertain Rate | Test Cal Macro-F1 |
| --- | --- | --- | --- | --- | --- | --- |
| `label_flip` (`30%`) | `0.267 ± 0.253` | `0.300 ± 0.274` | `0.280 ± 0.259` | `0.200 ± 0.112` | `0.520` | `0.6088` |
| `data_poisoning` (`30%`) | `0.217 ± 0.217` | `0.300 ± 0.274` | `0.247 ± 0.233` | `0.275 ± 0.105` | `0.480` | `0.5681` |
| `backdoor` (`20%`) | `0.100 ± 0.224` | `0.100 ± 0.224` | `0.100 ± 0.224` | `0.200 ± 0.112` | `0.520` | `0.6464` |
| `byzantine_sign_flip` (`-8x`) | `0.330 ± 0.211` | `0.600 ± 0.418` | `0.414 ± 0.262` | `0.275 ± 0.105` | `0.460` | `0.6101` |

---

## 2. Window W3 Attribution Results (`Shards 8–23`, Overlapping Window, `n = 5` Seeds)

| Intervention Arm | Malicious Precision | Malicious Recall | Malicious F1 | False Attribution Rate (FAR) | Uncertain Rate | Test Cal Macro-F1 |
| --- | --- | --- | --- | --- | --- | --- |
| `label_flip` (`30%`) | `0.357 ± 0.139` | **`0.800 ± 0.274`** | `0.470 ± 0.141` | `0.425 ± 0.244` | `0.320` | `0.4379` |
| `data_poisoning` (`30%`) | `0.000 ± 0.000` | `0.000 ± 0.000` | `0.000 ± 0.000` | `0.225 ± 0.205` | `0.440` | `0.4744` |
| `backdoor` (`20%`) | `0.557 ± 0.289` | **`0.800 ± 0.274`** | **`0.582 ± 0.148`** | `0.275 ± 0.271` | `0.400` | `0.4211` |
| `byzantine_sign_flip` (`-8x`) | `0.507 ± 0.299` | **`0.800 ± 0.274`** | `0.536 ± 0.125` | `0.350 ± 0.324` | `0.300` | `0.5290` |

---

## 3. Honest Research Findings & Attribution Limitations

1. **Strong Recall on W3 Label-Flip / Backdoor / Sign-Flip (`0.800`):** On W3, the attributor achieved `80%` recall on `label_flip`, `backdoor`, and `byzantine_sign_flip` without any access to hidden attack labels.
2. **Feature-Noise Poisoning Blind Spot (`data_poisoning`):** Feature-noise poisoning (`sigma = 3.0`) elevates per-client `feature_psi >= 0.25`, causing the attributor's `not has_feat_drift` guard to treat noisy poisoned clients as benign covariate shift (`Recall = 0.000` on W3, `0.300` on W1).
3. **Non-IID False Attribution Pressure (`FAR = 0.20–0.43`, `Uncertain = 0.30–0.52`):** Unlike the clean synthetic E2E test (`FAR = 0.0`), real ToN-IoT Dirichlet($\alpha=0.5$) non-IID heterogeneity induces high honest gradient dispersion, causing `20%–42.5%` false attribution and `30%–52%` abstention (`uncertain_insufficient_evidence`). This empirically demonstrates that single-round cohort-median heuristics require multi-round temporal smoothing and server-side validation loss probing in future iterations.
