# DA-FIDAF Phase 3A.1 — E1 Pilot Diagnostic Audit

**Audited Artifacts (`I:\Projects\da-fidaf-runs`):**
- `20261124T063040_430883Z_phase3a_e1_iid_seed42_7e7666`
- `20261124T063040_703422Z_phase3a_e1_iid_seed101_417a46`
- `20261124T063040_985904Z_phase3a_e1_label_skew_seed42_5dcbe5`
- `20261124T063041_266599Z_phase3a_e1_label_skew_seed101_90c735`

**Diagnostic Figures:** `I:\Projects\da-fidaf-runs\figures\phase3a_diagnostics\fig_E1_01..04_*`

---

## 1. Exact Confusion Matrices & Class-Wise Metrics (Test `n = 173`: `3` Benign, `170` Attack)

Positive class = `1` (attack), decision threshold = `0.50` (unmodified pilot outputs):

| Run | TN | FP | FN | TP | Cls 0 (P / R / F1) | Cls 1 (P / R / F1) | Macro-F1 | ROC-AUC | PR-AUC | FPR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IID (`seed=42`) | 1 | 2 | 0 | 170 | `1.000 / 0.333 / 0.500` | `0.988 / 1.000 / 0.994` | `0.7471` | `1.0000` | `1.0000` | `0.6667` |
| IID (`seed=101`) | 1 | 2 | 0 | 170 | `1.000 / 0.333 / 0.500` | `0.988 / 1.000 / 0.994` | `0.7471` | `1.0000` | `1.0000` | `0.6667` |
| Non-IID (`seed=42`) | 1 | 2 | 0 | 170 | `1.000 / 0.333 / 0.500` | `0.988 / 1.000 / 0.994` | `0.7471` | `1.0000` | `1.0000` | `0.6667` |
| Non-IID (`seed=101`) | 0 | 3 | 0 | 170 | `0.000 / 0.000 / 0.000` | `0.983 / 1.000 / 0.991` | `0.4956` | `0.6745` | `0.9799` | `1.0000` |

---

## 2. Root-Cause Findings

### 2.1 Why IID Seed 42, IID Seed 101, and Non-IID Seed 42 Have Identical Macro-F1 (`0.747076`)
- The three models learned **distinct** weight vectors and predicted probabilities:
  - IID (`seed=42`): benign probs `[0.42828, 0.62542, 0.74174]`, attack range `[0.76061, 0.85300]`
  - IID (`seed=101`): benign probs `[0.36229, 0.56285, 0.68705]`, attack range `[0.70529, 0.85509]`
  - Non-IID (`seed=42`): benign probs `[0.44508, 0.68874, 0.81758]`, attack range `[0.84125, 0.92391]`
- Because the pilot Test split contains only **`n_benign = 3`** flows, and strictly **1 of 3** benign flows fell below `0.50` in all three runs, the discrete confusion matrix quantized identically to `(TN=1, FP=2, FN=0, TP=170)` -> Class 0 F1 = `0.5000`, Class 1 F1 = `0.994152`, Macro-F1 = `0.747076`.

### 2.2 Why IID FPR Is `0.6667` Despite `ROC-AUC = 1.0000`
- The models achieved **perfect rank separation** (`max(benign_prob) < min(attack_prob)` in all three runs; optimal midpoint `0.751`, `0.696`, `0.829`).
- However, the `95.9%` attack training prior (`10,078` attack vs. `425` benign) shifted the logistic intercept upward, pushing 2 of 3 benign flows above the uncalibrated default threshold `0.50`.
- **Phase 3B Implication:** Evaluate both threshold-free metrics (`ROC-AUC`, `PR-AUC`) and validation-calibrated thresholds (selected strictly on Validation split, never Test), alongside balanced multi-shard windows.

### 2.3 Why Non-IID `label_skew` Seed 101 Collapses (`Macro-F1 = 0.4956`, `ROC-AUC = 0.6745`, `FPR = 1.0`)
- Under Dirichlet($\alpha=0.5$, `seed=101`), `sim_gw_01` received `6,591` flows (`9` benign, `6,582` attack = `99.86%` attack) and `sim_gw_06` received `2,597` flows (`15` benign, `2,582` attack = `99.42%` attack), representing **`87.5%`** of total FedAvg sample weight.
- Benign-rich clients (`sim_gw_03`: `71/105`, `sim_gw_05`: `52/58`) carried only `1.55%` combined weight.
- Sample-weighted FedAvg collapsed onto majority-attack predictions (`benign_probs = [0.8904, 0.9350, 0.9527]` overlapping `attack_probs = [0.9370, 0.9536]`), proving genuine Non-IID vulnerability in FedAvg and motivating FedProx / balanced weighting in Phase 3B.

### 2.4 Reproducibility Verification
- Re-executing all 4 pilot setups in memory reproduced the exact `run_report.json` metrics (`macro_f1`, `roc_auc`, `pr_auc`, `fpr`, `fnr`, `final_val_loss`) to 6 decimal places.
