# DA-FIDAF Phase 3B.1 — Independent Statistical Reanalysis

- **Unit of Analysis Verified (`PASS`):** Independent experimental seed (`n = 5` deterministic seeds `[42, 101, 202, 303, 404]`). Individual rounds, clients, and flow samples were NEVER treated as independent seeds.
- **W1 $\subset$ W3 Non-Pooling Verified (`PASS`):** W1 (`Shards 22+23`, `Apr 27–29`, `stride=15`) is contained inside W3 (`Shards 8–23`, `Apr 24–29`, `stride=80`). Every statistical summary and paired test keeps W1 and W3 strictly separate; no independent cross-dataset validation is claimed.
- **Raw-to-Summary Numeric Agreement (`PASS`):** Independent recalculation of all E1 means and sample SDs ($n-1$) directly from raw `run_report.json` files matched `e1_master_summary.json` with **`max_abs_diff = 0.0`**.

---

## Finding [AUD-07A] — LOW: Percentile Bootstrap CIs Are Narrower Than Exact Student-$t$ ($df=4$) CIs at `n = 5`

- **Finding ID:** `AUD-07A` | **Severity:** `LOW` (Statistical Conservatism)
- **Evidence File:** `I:\Projects\da-fidaf-runs\phase3b_audit\PHASE_3B_1_EVIDENCE_MANIFEST.json` (`statistical_reanalysis`)
- **Verification Method:** Recomputed exact Student-$t$ 95% CIs ($\bar{x} \pm t_{0.975, 4} \cdot s/\sqrt{5}$, with $t_{0.975, 4} = 2.776445$) directly from raw per-seed Macro-F1 values and compared against the published percentile bootstrap 95% CIs (`n_boot = 500`).

### E1 Independent Reanalysis Table (Calibrated Macro-F1, `n = 5` Seeds)

| Window & Config | Recalc Mean ± SD | Published Bootstrap 95% CI | Exact Student-$t$ ($df=4$) 95% CI | Width Ratio ($t_4$ / Boot) |
| --- | --- | --- | --- | --- |
| **W1 `iid_fedavg`** | `0.7017 ± 0.0124` | `[0.6926, 0.7108]` | `[0.6863, 0.7171]` | `1.69x` |
| **W1 `label_skew_a05_fedavg`** | `0.6962 ± 0.0347` | `[0.6651, 0.7225]` | `[0.6531, 0.7394]` | `1.50x` |
| **W1 `label_skew_a01_fedavg`** | `0.6999 ± 0.0385` | `[0.6709, 0.7294]` | `[0.6521, 0.7477]` | `1.63x` |
| **W1 `quantity_skew_fedavg`** | `0.7102 ± 0.0204` | `[0.6946, 0.7258]` | `[0.6849, 0.7354]` | `1.62x` |
| **W1 `combined_fedavg`** | `0.7185 ± 0.0245` | `[0.7003, 0.7382]` | `[0.6881, 0.7490]` | `1.61x` |
| **W1 `label_skew_a05_fedprox`** | `0.6957 ± 0.0204` | `[0.6834, 0.7140]` | `[0.6704, 0.7211]` | `1.66x` |
| **W1 `label_skew_a01_fedprox`** | `0.6859 ± 0.0391` | `[0.6589, 0.7190]` | `[0.6374, 0.7344]` | `1.62x` |
| **W3 `iid_fedavg`** | `0.4142 ± 0.0078` | `[0.4086, 0.4203]` | `[0.4046, 0.4239]` | `1.64x` |
| **W3 `label_skew_a01_fedavg`** | `0.7184 ± 0.1760` | `[0.5563, 0.8212]` | `[0.4998, 0.9370]` | `1.65x` |
| **W3 `label_skew_a01_fedprox`** | `0.7045 ± 0.1654` | `[0.5562, 0.7794]` | `[0.4991, 0.9099]` | `1.84x` |

- **Scientific Implication:** At small sample size `n = 5`, percentile bootstrap CIs systematically underestimate tail uncertainty by ~`1.5x–1.8x` compared to Student-$t$ ($df = 4$). For instance, W1 `FedProx vs FedAvg (alpha=0.1)` (`mean_diff = -0.0140`, `d_z = -0.785`) had a bootstrap CI barely excluding zero `[-0.0274, -0.0004]`, whereas its exact Student-$t$ CI `[-0.0361, +0.0081]` **includes zero** (not statistically significant at $\alpha = 0.05$)!
- **Recommended Action:** Report exact Student-$t$ ($df = n - 1$) 95% CIs (or expand to `n >= 10` seeds) for final manuscript claims and avoid asserting statistical significance when $t$-CIs cross zero.
