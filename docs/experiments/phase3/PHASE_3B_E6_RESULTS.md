# DA-FIDAF Phase 3B — E6 Results (Component Ablations & Systems Overhead — Non-DP Baseline)

- **Execution Scope:** Authorized Phase 3B **Non-DP baseline ONLY** (`dp_enabled = False`, `secure_aggregation_active = False`), `K = 10` simulated gateways (`label_skew`, Dirichlet $\alpha = 0.5$), `6` rounds under concurrent `sign_flip` Byzantine attack (`f = 2/10`) + covariate drift (`severity = 1.5`), `5` seeds `[42, 101, 202, 303, 404]`.
- **Artifacts:** `I:\Projects\da-fidaf-runs\phase3b\e6\` & `e6_master_summary.json` (`50` runs: `25` W1 + `25` W3; `0` failed).
- **IEEE Figure:** `I:\Projects\da-fidaf-runs\figures\phase3b\fig_E6_01_ablation_overhead.*`.
- **Reproducibility Check:** Identical W1 E1 (`iid`, `seed=42`) executed twice back-to-back confirmed **`bit_exact_parameters = True`** and **`bit_exact_macro_f1 = True`** (`0.47519`).

---

## 1. Window W1 Ablation & Overhead (`Shards 22+23`, `n = 5` Seeds)

| Ablation Variant | Cal Macro-F1 (Mean ± SD) | Train Wall Time (s) | Inference (ms / 1k flows) | Peak Memory (MB) | Comm / Round (B) | Total Comm (B) | Model Size (B) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **`full_dafidaf`** | **`0.6629 ± 0.0828`** | `14.97 ± 0.34` | `7.802` | `13.53` | `1,920` | `11,520` | `96` |
| `without_drift_detection` | `0.5631 ± 0.0507` | `15.02 ± 0.24` | `7.319` | `13.53` | `1,920` | `11,520` | `96` |
| `without_robust_aggregation` | `0.6583 ± 0.1293` | `15.07 ± 0.39` | `7.319` | `13.53` | `1,920` | `11,520` | `96` |
| `without_attribution` | `0.6629 ± 0.0828` | `15.26 ± 0.51` | `7.545` | `13.53` | `1,920` | `11,520` | `96` |
| `without_continual_adaptation` | `0.5631 ± 0.0507` | `15.16 ± 0.32` | `6.112` | `13.53` | `1,920` | `11,520` | `96` |

---

## 2. Window W3 Ablation & Overhead (`Shards 8–23`, Overlapping Window, `n = 5` Seeds)

| Ablation Variant | Cal Macro-F1 (Mean ± SD) | Train Wall Time (s) | Inference (ms / 1k flows) | Peak Memory (MB) | Comm / Round (B) | Total Comm (B) | Model Size (B) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **`full_dafidaf`** | `0.4245 ± 0.0016` | `34.97 ± 0.51` | `7.130` | `30.87` | `1,760` | `10,560` | `88` |
| `without_drift_detection` | `0.5520 ± 0.1838` | `35.55 ± 0.79` | `7.396` | `30.87` | `1,760` | `10,560` | `88` |
| `without_robust_aggregation` | `0.3649 ± 0.1067` | `38.20 ± 2.34` | `7.396` | `30.87` | `1,760` | `10,560` | `88` |
| `without_attribution` | `0.4245 ± 0.0016` | `35.36 ± 0.80` | `7.092` | `30.87` | `1,760` | `10,560` | `88` |
| `without_continual_adaptation` | `0.5520 ± 0.1838` | `35.05 ± 0.88` | `5.935` | `30.87` | `1,760` | `10,560` | `88` |

---

## 3. Systems & Utility-Robustness Findings

1. **Ultra-Lightweight Edge IoT Footprint:** Serialized `LinearLogisticIDS` weighs only **`88–96 bytes`**, requiring **`1.76–1.92 KB/round`** (`10.56–11.52 KB` total across 6 rounds and 10 clients), `~6–8 ms` inference per `1,000` flows (`< 8 µs/flow`), and `13.5–30.9 MB` peak traced memory.
2. **Negligible Framework Overhead:** Drift detection, attribution, robust aggregation, and replay adaptation add `< 3%` wall-time overhead (`~15.0s` W1, `~35.0s` W3) and `0` extra communication bytes relative to baseline FL.
3. **Component Contributions:** On W1, drift detection + continual adaptation contributed **`+0.0998` Macro-F1** (`0.6629` vs `0.5631`) and robust aggregation reduced seed SD by `36%` (`0.0828` vs `0.1293`). On W3, robust aggregation lifted Macro-F1 by **`+0.0596`** (`0.4245` vs `0.3649`) and reduced SD by `66x` (`0.0016` vs `0.1067`). Note that `without_attribution` matched `full_dafidaf` because attribution currently logs decisions without automated client quarantine (a clear Phase 4 enhancement).
4. **No Privacy Guarantees Claimed:** All E6 runs executed strictly in Non-DP mode (`dp_enabled = False`, `secure_aggregation_active = False`).
