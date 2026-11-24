# DA-FIDAF Phase 3B.1 — E1 Independent Metric Verification & W1 ROC-AUC Diagnosis

- **Scope:** All `70` E1 raw `run_report.json` files (`35` W1 + `35` W3) + saved seed-42 model checkpoint (`I:\Projects\da-fidaf-runs\phase3b\checkpoints\e1_W1_iid_fedavg_seed42\checkpoint_round_008.json`).
- **CM-to-Metric Recalculation (`70/70` runs, fixed `0.50` & Val-calibrated):** `0` discrepancies (`max_abs_diff <= 1e-6` across Accuracy, Precision, Recall, Specificity, F1, Macro-F1, FPR, FNR). `0.0` mean mismatch between raw files and `e1_master_summary.json`.

---

## Finding [AUD-02] — HIGH: Root-Cause Diagnosis of W1 `ROC-AUC = 0.3208` vs. `Calibrated Macro-F1 = 0.6992`

- **Finding ID:** `AUD-02` | **Severity:** `HIGH` (Scientific Interpretation Risk)
- **Evidence File:** `I:\Projects\da-fidaf-runs\phase3b\checkpoints\e1_W1_iid_fedavg_seed42\checkpoint_round_008.json` & `e1_w1_iid_fedavg` seed `42` `run_report.json`
- **Verification Method:** Loaded the untouched round-8 weights directly into `LinearLogisticIDS`, computed raw probabilities on W1 Val (`n=13,303`) and Test (`n=13,253`), and independently recomputed ROC-AUC, inverted-score ROC-AUC, Macro-F1, and class-conditional score quantiles.
- **Original Reported vs. Independently Recalculated Values (`e1_W1_iid_fedavg`, `seed=42`):**
  - `test_roc_auc`: Reported `0.320810` | Recalculated **`0.320810`** (exact match)
  - `test_cal_macro_f1` ($\tau^*_{\text{val}} = 0.625$): Reported `0.699189` | Recalculated **`0.699189`** (exact match)
  - Inverted-score `ROC-AUC(1 - p)`: **`0.679190`** (`= 1.0 - 0.320810`)

### Seven-Point Diagnostic Checklist

1. **Positive-class definition & label encoding:** Verified consistent across Train, Val, and Test: `0 = normal/benign`, `1 = attack` (`TON_IOT_LABEL_ONTOLOGY.to_binary`).
2. **Score semantics:** `LinearLogisticIDS.predict_proba()` returns $P(y = 1 \mid x)$ (attack probability). Learned weights: `src_bytes = +0.4908`, `dst_pkts = +0.8452`, `dst_ip_bytes = -0.5755`, `bias = +0.9349`.
3. **ROC-AUC score direction:** Verified correct (higher score = predicted attack). No sign flip or code bug occurred.
4. **Train/Val/Test encoding consistency:** Verified identical `TonIoTNetworkAdapter` / `TON_IOT_LABEL_ONTOLOGY` encoding across all splits.
5. **Validation-only threshold calibration:** Verified `tau_val = 0.625` was computed strictly via `calibrate_threshold_on_val(w1.y_val, val_scores)` without touching `y_test`.
6. **Zero Test leakage:** Verified `y_test` and `x_test` never influenced training, aggregation, or threshold selection.
7. **Exact mathematical explanation of `AUC = 0.3208` + `Macro-F1 = 0.6992`:**
   - **Test Attack (`backdoor`, `n=11,442`) score quantiles `[0%, 25%, 50%, 75%, 100%]`:** `[0.61692, 0.64051, 0.64051, 0.64052, 1.00000]` (`mean = 0.64145`).
   - **Test Benign (`normal`, `n=1,811`) score quantiles `[0%, 25%, 50%, 75%, 100%]`:** `[0.00151, 0.61734, 0.80443, 0.94367, 1.00000]` (`mean = 0.76885`).
   - Because Train is dominated by `xss` (`32,607` high-byte/packet flows), the linear model assigns *higher* attack probability to normal traffic (`median = 0.8044`) than to low-volume `backdoor` flows (`median = 0.6405`), causing `67.9%` of `(benign, attack)` pairs to be misranked (`ROC-AUC = 0.3208`).
   - Simultaneously, because `29.21%` of benign flows fall in the lower tail `< 0.625` while `99.97%` of attack flows sit tightly at `0.6405 >= 0.625`, the Validation-selected threshold `0.625` yields `TN = 29.21%` (`FPR = 0.7079`), `Recall = 99.97%`, Class-0 F1 `≈ 0.45`, Class-1 F1 `≈ 0.95` -> `Macro-F1 = 0.6992`.

- **Scientific Implication:** The W1 linear model ranks worse than random (`AUC = 0.32`) under campaign-disjoint `xss -> backdoor` transfer. Reporting W1 `Macro-F1 = 0.70` alone without `ROC-AUC = 0.32` and `FPR = 0.70` would be misleading. Original measurements are preserved unmodified.
- **Recommended Action:** Always co-report `ROC-AUC`, `FPR`, and Class-0 F1 alongside `Macro-F1`; introduce non-linear neural backbones (`ModelInterface`) in Phase 4 to test whether non-linear boundaries overcome campaign-disjoint linear inversion.
