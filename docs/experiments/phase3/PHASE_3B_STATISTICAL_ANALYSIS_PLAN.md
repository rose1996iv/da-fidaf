# DA-FIDAF — Phase 3B Statistical Analysis Plan

## 1. Replication & Randomization Design

- **Independent Seeds:** Every condition in E1–E4 and E6 executes across **`n = 5` independent deterministic seeds**: `[42, 101, 202, 303, 404]`.
- **Paired Design:** Baseline and DA-FIDAF variants share identical seed-indexed client partitions, model initializations, and attack/drift schedules, enabling **paired within-seed comparisons** that eliminate partition-draw variance.
- **Statistical Validity Guard:** Per `src/dafidaf/evaluation/metrics.py`, confidence intervals are computed ONLY when $n \ge 3$ (target $n = 5$). Runs with $n < 3$ report individual seed values only (`statistically_valid = False`).

---

## 2. Primary & Secondary Metrics

| Domain | Primary Metrics | Secondary / Diagnostic Metrics |
| --- | --- | --- |
| **IDS Classification (E1, E2, E4, E6)** | Macro-F1 (at $\tau^*_{\text{val}}$ and `0.50`), PR-AUC, ROC-AUC | Class-0 & Class-1 Precision/Recall/F1, FPR, FNR, Confusion Matrix |
| **Drift & Adaptation (E2)** | Detection Delay (rounds), Recovery Macro-F1, `forgetting_delta` | False Alarm Rate (stable control), per-round Max PSI & JSD |
| **Attribution (E3, E4)** | False Attribution Rate (FAR), Malicious Recall, Malicious Precision | `uncertain_rate`, per-verdict confusion counts |
| **Systems & Privacy (E6)** | Total Communication Bytes, Round Wall Time (s), Peak Memory (MB) | Exact RDP $\epsilon_{\text{upper}}(\delta=10^{-5})$ (simulation-grade) |

---

## 3. Inferential Comparison Methods

1. **Summary Statistics (`summarize_multi_seed`):** Report `mean`, `std` (unbiased $n-1$), `min`, `max`, and **95% percentile bootstrap CI** (`n_boot = 2000` for final Phase 3B reporting).
2. **Paired Treatment vs. Baseline (`paired_effect_size_and_ci`):**
   - Paired mean difference $\bar{d} = \frac{1}{n}\sum_{i=1}^n (y_{\text{treat}, i} - y_{\text{base}, i})$.
   - Paired Cohen's $d_z = \bar{d} / s_d$ (explicitly reported as `None`/undefined when $s_d = 0$ and $\bar{d} \neq 0$).
   - 95% paired bootstrap CI on $\bar{d}$; practical + statistical superiority requires CI excluding `0.0` AND $|\bar{d}| \ge 0.01$ Macro-F1.
3. **Non-Overclaiming Rules:**
   - Never hide failed seeds or unfavorable collapses (e.g., Non-IID FedAvg degradation).
   - Report exact sample counts (`n_train`, `n_val`, `n_test`, benign/attack split counts) alongside every metric table.
   - Clearly separate natural real-data measurements from labeled synthetic interventions.
