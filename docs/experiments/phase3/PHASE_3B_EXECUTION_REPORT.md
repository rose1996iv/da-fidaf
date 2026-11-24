# DA-FIDAF — Phase 3B Master Execution Report

- **Authorization Scope:** Full-scale Phase 3B execution on **W1 (`Shards 22+23`, primary)** and **W3 (`Shards 8–23`, overlapping larger window)** across **E1, E2, E3, E4, and E6**; **Non-DP baseline only**; **E5 explicitly excluded (`HOLD`)**.
- **Final Phase 3B Status:** **`CONDITIONAL PASS`** (All `490` authorized real-dataset runs completed with `0` failures, `6` IEEE publication figure sets generated, bit-exact reproducibility verified, Stage 7 Git baseline preserved; conditional due to authorized Non-DP scope, excluded E5, W1 $\subset$ W3 overlap, and documented linear-model / single-round-attribution limitations on real ToN-IoT).

---

## 1. Execution Ledger (Completed vs. Failed Runs)

| Experiment | Window W1 Runs | Window W3 Runs | Failed Runs | Master Artifact Path (`I:\Projects\da-fidaf-runs\phase3b\`) | Report |
| --- | --- | --- | --- | --- | --- |
| **E1** (IID vs. Non-IID) | `35` (`7` cfgs × `5` seeds) | `35` (`7` cfgs × `5` seeds) | `0` | `e1/` & `e1_master_summary.json` | [PHASE_3B_E1_RESULTS.md](file:///I:/Projects/da-fidaf/docs/experiments/phase3/PHASE_3B_E1_RESULTS.md) |
| **E2** (Concept Drift) | `40` (`10` emb + `30` arms) | `40` (`10` emb + `30` arms) | `0` | `e2/` & `e2_master_summary.json` | [PHASE_3B_E2_RESULTS.md](file:///I:/Projects/da-fidaf/docs/experiments/phase3/PHASE_3B_E2_RESULTS.md) |
| **E3** (Attribution) | `20` (`4` arms × `5` seeds) | `20` (`4` arms × `5` seeds) | `0` | `e3/` & `e3_master_summary.json` | [PHASE_3B_E3_RESULTS.md](file:///I:/Projects/da-fidaf/docs/experiments/phase3/PHASE_3B_E3_RESULTS.md) |
| **E4** (Byzantine) | `125` (`5` atk × `5` agg × `5` s) | `125` (`5` atk × `5` agg × `5` s) | `0` | `e4/` & `e4_master_summary.json` | [PHASE_3B_E4_RESULTS.md](file:///I:/Projects/da-fidaf/docs/experiments/phase3/PHASE_3B_E4_RESULTS.md) |
| **E5** (Cross-Dataset) | `0` (NOT AUTHORIZED) | `0` (NOT AUTHORIZED) | N/A | Excluded (`HOLD`) | — |
| **E6** (Ablation/Overhead) | `25` (`5` abl × `5` seeds) | `25` (`5` abl × `5` seeds) | `0` | `e6/` & `e6_master_summary.json` | [PHASE_3B_E6_RESULTS.md](file:///I:/Projects/da-fidaf/docs/experiments/phase3/PHASE_3B_E6_RESULTS.md) |
| **Total** | **`245`** | **`245`** | **`0`** | **`490` total real-data runs + bit-exact reproducibility check** | — |

---

## 2. Window Integrity & Non-Pooling Verification

- **W1 (`Shards 22+23`, `stride=15`, `89,269` rows, `300s`):** Train `62,488` (`15,270` benign / `47,218` attack); Val `13,303` (`747` / `12,556`); Test `13,253` (`1,811` / `11,442`). All splits exceed `>= 500`/class floor under both `300s` and `900s` embargo.
- **W3 (`Shards 8–23`, `stride=80`, `191,738` rows, `300s`):** Train `147,355` (`3,043` benign / `144,312` attack); Val `33,693` (`625` / `33,068`); Test `10,547` (`3,261` / `7,286`). All splits exceed `>= 500`/class floor under both `300s` and `900s` embargo.
- **Overlap Disclosure:** W1 is a chronological subset of W3; no metrics or statistical tests ever pooled W1 and W3.

---

## 3. IEEE Publication Figure Inventory (`I:\Projects\da-fidaf-runs\figures\phase3b\`)

Generated via [plot_phase3b_ieee_figures.py](file:///I:/Projects/da-fidaf-runs/figures/phase3b/plot_phase3b_ieee_figures.py) (each stem includes `.pdf`, `.eps`, `300 DPI .png`, `_data.csv`, `_data.json`, `_caption.txt`, and `_metadata.json`):
1. `fig_E1_01_convergence` — Per-round validation BCE loss (W1 & W3, mean ± SD, `n=5`)
2. `fig_E1_02_f1_comparison` — Calibrated vs. fixed `0.50` Macro-F1 & ROC-AUC across 7 E1 configs
3. `fig_E2_01_drift_timeline` — Static vs. Replay drift recovery & catastrophic forgetting comparison
4. `fig_E3_01_attribution_tradeoff` — Malicious Recall, FAR, and Uncertain Rate across E3 arms
5. `fig_E4_01_byzantine_robustness` — `5` Byzantine attacks × `5` aggregators matrix (W1 & W3)
6. `fig_E6_01_ablation_overhead` — Component ablation utility & wall-time overhead (Non-DP)

---

## 4. Synthesis of Scientific Findings & Remaining Limitations

1. **Real ToN-IoT Domain Shift Exposes Linear Model Limits (E1):** Validation-only threshold calibration lifted W1 Macro-F1 by `+0.19` (`0.51 → 0.70`), and W3 achieved strong ranking (`ROC-AUC = 0.837–0.845`) on 100% unseen Test attack families, but disjoint attack campaigns exposed linear slope inversion (W1 `AUC ≈ 0.32`) and threshold transfer shift (W3 `FPR ≈ 0.99`).
2. **Dual Drift Detection & Replay Adaptation Validated (E2):** `0%` false alarms on stable controls, `0`-round PSI detection on covariate shifts, `0`-round Page-Hinkley detection on W3 conditional concept drift (where PSI was blind), and zero catastrophic forgetting under `replay` on W1 (`-0.020` vs `+0.187` for `fine_tune`).
3. **Attribution Realism Under Non-IID (E3):** Strong recall (`0.80`) on W3 `label_flip`/`backdoor`/`sign_flip`, while exposing real-world Non-IID FAR (`0.20–0.43`) and a feature-noise poisoning blind spot (`0.00` recall on W3 `data_poisoning`).
4. **Byzantine Defense & `NaN` Quarantine (E4 & E6):** `100%` of `NaN` Byzantine updates quarantined (`10/10` per run); Multi-Krum & Trimmed Mean lifted W3 `ROC-AUC` by `+0.167` (`sign_flip`) to `+0.269` (`model_replacement`) over FedAvg; lightweight edge footprint (`88–96 B` model, `< 2 KB/round`, `< 8 ms/1k` inference).
5. **Scope Exclusions Retained:** Non-DP baseline only (`dp_enabled = False`, `secure_aggregation_active = False`); **E5 remains `HOLD`**. See [PHASE_3B_NON_DP_SCOPE_AND_LIMITATIONS.md](file:///I:/Projects/da-fidaf/docs/security/PHASE_3B_NON_DP_SCOPE_AND_LIMITATIONS.md).
