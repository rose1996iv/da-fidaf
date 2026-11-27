# DA-FIDAF GAP-1 — Final Confirmatory Experiment Report (`EXP-GAP-1`, Gate 2)

**Document Status:** `COMPLETED — AWAITING INDEPENDENT POST-CONFIRMATORY AUDIT`  
**Date:** `2026-11-28`  
**Execution Gate:** Gate 2 Authorized under **Option B-Hybrid** (`compact_mlp_continual.py` preserved `100%` byte-identical to Gate 1 audited hash `29f490f7...`; `stage_b4_exp_gap1_master_summary.json` and this report use clean `all_rounds_*_trigger_rate` and `stable_control_*_far` labels).  
**Governing Anchors (All Verified Unchanged):**
- Protocol `v5.0`: [EXP_GAP_1_Protocol_v5_0.md](EXP_GAP_1_Protocol_v5_0.md) (`0ee5dbd15e2116ab0294bcd7d5f8a715837a97aa99cd761e024645f6e7899ad2`)
- Gate 1 Pilot Report (`PASS`): [GAP_1_DETERMINISM_PILOT_REPORT.md](GAP_1_DETERMINISM_PILOT_REPORT.md) (`cbd335405b91ad62821b8a443c66d53e2335891e854d77a975300523573c4ce9`)
- Post-Pilot Audit (`9/9 PASS`): [GAP_1_POST_PILOT_AUDIT_REPORT.md](GAP_1_POST_PILOT_AUDIT_REPORT.md) (`aaf15b19d115129a749299d160b5fc5a8b9e8f51f61a3d956951a2f98395b9bd`)
- Gate 2 Readiness Report: [GAP_1_GATE_2_READINESS_REPORT.md](GAP_1_GATE_2_READINESS_REPORT.md) (`5d2e7e39763e061b7116eeb1400846b2566c18fc203cb43d5b52f7233cd980c2`)
- **Governance Hold Notice:** Cross-stage evidence ledgers have **NOT** been updated, and `EXP-GAP-2` / `EXP-GAP-3` have **NOT** started, pending an independent read-only Post-Confirmatory Audit.

---

## 1. Execution Summary, Environment & Provenance

- **Command Executed (Exit Code `0`):**
  ```powershell
  $env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
  python "I:\Projects\da-fidaf-runs\phase4_phd_execution\stage_b4_exp_gap1_e2_mlp.py" --mode confirmatory
  ```
- **Run Accounting:** `20` base FL `CompactMLP` models (`2 windows × 10 seeds`) + **`320` confirmatory trajectory runs** (`2 windows × 4 schedules × 4 arms × 10 seeds`; `160` on `W1`, `160` on `W3`). The `2` Gate 1 determinism-pilot runs under `pilot_determinism_check/` remain preserved untouched and **strictly excluded** from all `320` confirmatory runs and statistical tests.
- **Runtime Environment (Desktop Workstation — Not Physical IoT Hardware):** `Windows-11-10.0.26300-SP0`, Python `3.12.10`, PyTorch `2.6.0+cu124`, `NVIDIA GeForce GTX 1650` (`cuda`), NumPy `2.4.2`, SciPy `1.17.1`, scikit-learn `1.8.0`; `CUBLAS_WORKSPACE_CONFIG=":4096:8"`, `cudnn.benchmark=False`, `cudnn.deterministic=True`, `torch.use_deterministic_algorithms(True, warn_only=False)`.
- **Total Wall Time:** `1,106.0s` (`18.43` min; `W1`: `464.4s`, `W3`: `641.5s`).
- **Scope Disclosures:** `NON_DP_BASELINE_ONLY` (`dp_enabled = False`, `secure_aggregation_active = False`), `K = 10` simulated logical gateways, `byzantine_clients = 0`, `is_synthetic_intervention = True`, **`ToN-IoT W1` (`89,269`) is a strict chronological subset of `W3` (`191,738`) — kept strictly separate and never pooled**, `X_test` `100%` untouched for PSI/calibration/adaptation, `E5` cross-dataset transfer remains on **`HOLD`**.

### 1.1 Verified Runtime Split Counts (Recorded per Gate 2 Requirement #5)

| Window (`W1 ⊂ W3`) | `X_train` Total | `D_fl_train` (85%) | `D_prior_audit` (15%) | `X_val` Total | `D_val_cal` (20%) | `D_val_psi_ref` (20%, `X`-only) | Stream `S_1..S_10` (60%) | Untouched `X_test` |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| **`ToN-IoT W1`** (`d=11`) | `62,488` | **`53,114`** | **`9,374`** | `13,303` | `2,660` | `2,661` | `7,982` (`[799×2, 798×8]`) | `13,253` |
| **`ToN-IoT W3`** (`d=10`) | `147,355` | **`125,251`** | **`22,104`** | `33,693` | `6,738` | `6,739` | `20,216` (`[2022×6, 2021×4]`) | `10,547` |

*(Note: `StratifiedShuffleSplit(test_size=0.15)` uses `ceil(0.15 * N)`, producing exact verified `D_fl_train / D_prior_audit` counts `53,114 / 9,374` on `W1` and `125,251 / 22,104` on `W3`; frozen `v5.0` protocol text was not modified.)*

---

## 2. Schedule Validation & Hard Abort Gates (`100% PASS`)

| Validation / Abort Gate | `ToN-IoT W1` | `ToN-IoT W3` | Status |
|---|---:|---:|---|
| `NaN`/`Inf`, split-overlap, reservoir `< 32`, stream-guard, or `X_test` access errors | `0` | `0` | **PASS** |
| Single-class reservoirs permitted & logged per `RD-3` (`min |B_k|`) | `3 / 100` (`min=38`) | `5 / 100` (`min=36`) | **PASS** |
| `gradual_covariate` continuous ramp monotonicity (`R4 < R5 < R6 < R7`) | `10 / 10` seeds | `10 / 10` seeds | **PASS** |
| `abrupt_covariate` `R4` `10/10`-client PSI recall | `10 / 10` seeds | `10 / 10` seeds | **PASS** |
| `recurring_covariate` `ON` (`R4,5,8,9`) / `OFF` (`R6,7,10`) quorum `q_min=3` | `40/40` / `1/30` (`3.3%`) | `40/40` / `0/30` (`0.0%`) | **PASS** |
| `stable_control` `drift_gated_replay` combined (`PSI or PH`) fleet FAR (`<= 10%`) | **`4 / 100` (`4.0%`)** | **`0 / 100` (`0.0%`)** | **PASS** |
| `stable_control` `fine_tune` combined (`PSI or PH`) fleet FAR (`<= 10%`) | **`4 / 100` (`4.0%`)** | **`0 / 100` (`0.0%`)** | **PASS** |
| `abrupt_covariate` `static` prequential drop (`n_no_drop < 10`) | `0 / 10` `no_drop` (`10/10` dropped) | `1 / 10` `no_drop` (`9/10` dropped) | **PASS** |

---

## 3. Pre-Registered Confirmatory Statistical Results (`20` Holm-Bonferroni Tests, `n = 10`, `df = 9`)

Overall confirmatory breakdown across the `20` pre-registered comparisons (`10` on `W1`, `10` on `W3`): **`8 CONFIRMATORY_HOLM`**, **`4 EXPLORATORY_RAW_ONLY`**, **`8 NS`**.

### 3.1 `ToN-IoT W1` Confirmatory Families (`7 / 10 CONFIRMATORY_HOLM`, `3 / 10 EXPLORATORY_RAW_ONLY`)

| Family (`m`) | Schedule | Metric | Treatment vs. Baseline | Base Mean ± SD | Treat Mean ± SD | Mean Diff (`95%` $t$-CI) | Cohen's $d_z$ | Raw $p$ | Holm $p$ | Exact Wilcoxon $p$ (`nz`) | Tier |
|---|---|---|---|---:|---:|---|---:|---:|---:|---:|---|
| `F1_W1` (`3`) | `gradual_covariate` | `mean_r5_r10_pre_adapt_macro_f1` | `drift_gated_replay` vs. `static` | `0.0771 ± 0.1101` | `0.7771 ± 0.1566` | **`+0.7000`** `[+0.5656, +0.8343]` | `+3.726` | `9.00e-7` | **`2.70e-6`** | `0.00195` (`10`) | **`CONFIRMATORY_HOLM`** |
| `F1_W1` (`3`) | `abrupt_covariate` | `mean_r5_r10_pre_adapt_macro_f1` | `drift_gated_replay` vs. `static` | `0.0943 ± 0.1669` | `0.7841 ± 0.1711` | **`+0.6898`** `[+0.5171, +0.8626]` | `+2.856` | `8.30e-6` | **`1.66e-5`** | `0.00195` (`10`) | **`CONFIRMATORY_HOLM`** |
| `F1_W1` (`3`) | `recurring_covariate` | `mean_r5_r10_pre_adapt_macro_f1` | `drift_gated_replay` vs. `static` | `0.5406 ± 0.0814` | `0.8539 ± 0.0971` | **`+0.3133`** `[+0.2202, +0.4063]` | `+2.409` | `3.27e-5` | **`3.27e-5`** | `0.00195` (`10`) | **`CONFIRMATORY_HOLM`** |
| `F2_W1` (`3`) | `gradual_covariate` | `final_prior_audit_forgetting_delta` | `drift_gated_replay` vs. `fine_tune` | `+1.1329 ± 0.2842` | `+0.0445 ± 0.0190` | **`-1.0883`** `[-1.2994, -0.8773]` | `-3.689` | `9.80e-7` | **`2.94e-6`** | `0.00195` (`10`) | **`CONFIRMATORY_HOLM`** |
| `F2_W1` (`3`) | `abrupt_covariate` | `final_prior_audit_forgetting_delta` | `drift_gated_replay` vs. `fine_tune` | `+1.0785 ± 0.2993` | `+0.0468 ± 0.0253` | **`-1.0317`** `[-1.2568, -0.8065]` | `-3.278` | `2.65e-6` | **`5.30e-6`** | `0.00195` (`10`) | **`CONFIRMATORY_HOLM`** |
| `F2_W1` (`3`) | `recurring_covariate` | `final_prior_audit_forgetting_delta` | `drift_gated_replay` vs. `fine_tune` | `+0.2978 ± 0.1643` | `+0.0396 ± 0.0165` | **`-0.2582`** `[-0.3760, -0.1405]` | `-1.569` | `0.00078` | **`0.00078`** | `0.00195` (`10`) | **`CONFIRMATORY_HOLM`** |
| `F3_W1` (`4`) | `stable_control` | `total_federation_adapt_steps` | `drift_gated_replay` vs. `unconditional_replay` | `560.0 ± 0.0` | `10.4 ± 18.9` | **`-549.6`** `[-563.1, -536.1]` | `-29.118` | `<1e-8` | **`<1e-8`** | `0.00195` (`10`) | **`CONFIRMATORY_HOLM`** |
| `F3_W1` (`4`) | `stable_control` | `final_prior_audit_forgetting_delta` | `drift_gated_replay` vs. `unconditional_replay` | `+0.0267 ± 0.0215` | `+0.0065 ± 0.0105` | `-0.0202` `[-0.0367, -0.0037]` | `-0.876` | `0.02176` | `0.05007` | `0.01953` (`10`) | `EXPLORATORY_RAW_ONLY` |
| `F3_W1` (`4`) | `stable_control` | `mean_r4_r10_pre_adapt_macro_f1` | `drift_gated_replay` vs. `unconditional_replay` | `0.9945 ± 0.0020` | `0.9914 ± 0.0051` | `-0.0031` `[-0.0058, -0.0004]` | `-0.815` | `0.02990` | `0.05007` | `0.05469` (`9`) | `EXPLORATORY_RAW_ONLY` |
| `F3_W1` (`4`) | `recurring_covariate` | `final_prior_audit_forgetting_delta` | `drift_gated_replay` vs. `unconditional_replay` | `+0.0290 ± 0.0184` | `+0.0396 ± 0.0165` | `+0.0106` `[+0.0024, +0.0188]` | `+0.927` | `0.01669` | `0.05007` | `0.02734` (`10`) | `EXPLORATORY_RAW_ONLY` |

### 3.2 `ToN-IoT W3` Confirmatory Families (`1 / 10 CONFIRMATORY_HOLM`, `1 / 10 EXPLORATORY_RAW_ONLY`, `8 / 10 NS`)

| Family (`m`) | Schedule | Metric | Treatment vs. Baseline | Base Mean ± SD | Treat Mean ± SD | Mean Diff (`95%` $t$-CI) | Cohen's $d_z$ | Raw $p$ | Holm $p$ | Exact Wilcoxon $p$ (`nz`) | Tier |
|---|---|---|---|---:|---:|---|---:|---:|---:|---:|---|
| `F1_W3` (`3`) | `gradual_covariate` | `mean_r5_r10_pre_adapt_macro_f1` | `drift_gated_replay` vs. `static` | `0.5179 ± 0.0220` | `0.5351 ± 0.0302` | `+0.0172` `[-0.0041, +0.0385]` | `+0.577` | `0.10134` | `0.20269` | `0.03906` (`9`) | `NS` |
| `F1_W3` (`3`) | `abrupt_covariate` | `mean_r5_r10_pre_adapt_macro_f1` | `drift_gated_replay` vs. `static` | `0.5132 ± 0.0190` | `0.5279 ± 0.0252` | `+0.0147` `[-0.0007, +0.0300]` | `+0.684` | `0.05890` | `0.17670` | `0.03125` (`7`) | `NS` |
| `F1_W3` (`3`) | `recurring_covariate` | `mean_r5_r10_pre_adapt_macro_f1` | `drift_gated_replay` vs. `static` | `0.6082 ± 0.0498` | `0.6072 ± 0.0276` | `-0.0010` `[-0.0304, +0.0284]` | `-0.024` | `0.94106` | `0.94106` | `0.32227` (`10`) | `NS` |
| `F2_W3` (`3`) | `gradual_covariate` | `final_prior_audit_forgetting_delta` | `drift_gated_replay` vs. `fine_tune` | `+0.1024 ± 0.1496` | `+0.0186 ± 0.0350` | `-0.0838` `[-0.1835, +0.0159]` | `-0.602` | `0.08954` | `0.17908` | `0.06445` (`10`) | `NS` |
| `F2_W3` (`3`) | `abrupt_covariate` | `final_prior_audit_forgetting_delta` | `drift_gated_replay` vs. `fine_tune` | `+0.0906 ± 0.1302` | `+0.0185 ± 0.0257` | `-0.0721` `[-0.1591, +0.0150]` | `-0.592` | `0.09386` | `0.17908` | `0.08398` (`10`) | `NS` |
| `F2_W3` (`3`) | `recurring_covariate` | `final_prior_audit_forgetting_delta` | `drift_gated_replay` vs. `fine_tune` | `+0.0210 ± 0.0488` | `+0.0015 ± 0.0398` | `-0.0194` `[-0.0352, -0.0037]` | `-0.883` | `0.02092` | `0.06277` | `0.01953` (`10`) | `EXPLORATORY_RAW_ONLY` |
| `F3_W3` (`4`) | `stable_control` | `total_federation_adapt_steps` | `drift_gated_replay` vs. `unconditional_replay` | `560.0 ± 0.0` | `0.0 ± 0.0` | **`-560.0`** `[-560.0, -560.0]` | `None` *(0 var)* | `<1e-8` | **`<1e-8`** | `0.00195` (`10`) | **`CONFIRMATORY_HOLM`** |
| `F3_W3` (`4`) | `stable_control` | `mean_r4_r10_pre_adapt_macro_f1` | `drift_gated_replay` vs. `unconditional_replay` | `0.7124 ± 0.0522` | `0.7089 ± 0.0896` | `-0.0034` `[-0.0451, +0.0383]` | `-0.059` | `0.85587` | `1.00000` | `0.69531` (`10`) | `NS` |
| `F3_W3` (`4`) | `stable_control` | `final_prior_audit_forgetting_delta` | `drift_gated_replay` vs. `unconditional_replay` | `+0.0050 ± 0.0339` | `+0.0000 ± 0.0000` | `-0.0050` `[-0.0293, +0.0192]` | `-0.148` | `0.65157` | `1.00000` | `0.08398` (`10`) | `NS` |
| `F3_W3` (`4`) | `recurring_covariate` | `final_prior_audit_forgetting_delta` | `drift_gated_replay` vs. `unconditional_replay` | `+0.0052 ± 0.0336` | `+0.0015 ± 0.0398` | `-0.0037` `[-0.0117, +0.0044]` | `-0.325` | `0.33069` | `0.99207` | `0.49219` (`10`) | `NS` |

---

## 4. Per-Arm Summary, Compute Fairness, Recovery & `stable_control` FAR

### 4.1 `ToN-IoT W1` (`Base M_0`: `val_cal F1 = 0.9894`, `prior_audit BCE = 0.1662`, `untouched X_test F1 = 0.9773`, `AUC = 0.9927`)

| Schedule | Arm | `R5–R10` `pre_adapt` F1 | Prior Forgetting $\Delta\mathcal{L}$ | Fed Steps / Comm (MB) | Primary Recovery (`rec / nodrop / notrec`; mean $t$) | Untouched `X_test` `M_10` F1 |
|---|---|---:|---:|---:|---|---:|
| `stable_control` | `static` | `0.9893 ± 0.0090` | `+0.0000` | `0.0` / `0.00` | `0 / 10 / 0` (`—`) | `0.9773` |
| `stable_control` | `fine_tune` | `0.9921 ± 0.0048` | `+0.0415 ± 0.0853` | `10.4` / `0.07` | `0 / 10 / 0` (`—`) | `0.9812` |
| `stable_control` | `unconditional_replay` | `0.9954 ± 0.0018` | `+0.0267 ± 0.0215` | `560.0` / `1.72` | `0 / 10 / 0` (`—`) | `0.9828` |
| `stable_control` | `drift_gated_replay` | `0.9919 ± 0.0049` | `+0.0065 ± 0.0105` | `10.4` / `0.07` | `0 / 10 / 0` (`—`) | `0.9809` |
| `gradual_covariate` | `static` | `0.0771 ± 0.1101` | `+0.0000` | `0.0` / `0.00` | `0 / 0 / 10` (`—`) | `0.9773` |
| `gradual_covariate` | `fine_tune` | `0.8353 ± 0.0927` | `+1.1329 ± 0.2842` | `562.4` / `1.74` | `10 / 0 / 0` (`3.60 rd`) | `0.9645` |
| `gradual_covariate` | `unconditional_replay` | `0.7791 ± 0.1566` | `+0.0446 ± 0.0189` | `560.0` / `1.72` | `8 / 0 / 2` (`4.75 rd`) | `0.8902` |
| `gradual_covariate` | `drift_gated_replay` | `0.7771 ± 0.1566` | `+0.0445 ± 0.0190` | `562.4` / `1.74` | `8 / 0 / 2` (`4.75 rd`) | `0.8904` |
| `abrupt_covariate` | `static` | `0.0943 ± 0.1669` | `+0.0000` | `0.0` / `0.00` | `0 / 0 / 10` (`—`) | `0.9773` |
| `abrupt_covariate` | `fine_tune` | `0.8388 ± 0.1252` | `+1.0785 ± 0.2993` | `562.4` / `1.74` | `10 / 0 / 0` (`3.80 rd`) | `0.9727` |
| `abrupt_covariate` | `unconditional_replay` | `0.7844 ± 0.1713` | `+0.0470 ± 0.0251` | `560.0` / `1.72` | `8 / 0 / 2` (`4.88 rd`) | `0.8948` |
| `abrupt_covariate` | `drift_gated_replay` | `0.7841 ± 0.1711` | `+0.0468 ± 0.0253` | `562.4` / `1.74` | `8 / 0 / 2` (`4.88 rd`) | `0.8948` |
| `recurring_covariate` | `static` | `0.5406 ± 0.0814` | `+0.0000` | `0.0` / `0.00` | `10 / 0 / 0` (`2.00 rd`) | `0.9773` |
| `recurring_covariate` | `fine_tune` | `0.8714 ± 0.0844` | `+0.2978 ± 0.1643` | `324.8` / `1.02` | `10 / 0 / 0` (`2.00 rd`) | `0.9750` |
| `recurring_covariate` | `unconditional_replay` | `0.8162 ± 0.0817` | `+0.0290 ± 0.0184` | `560.0` / `1.72` | `10 / 0 / 0` (`2.00 rd`) | `0.9806` |
| `recurring_covariate` | `drift_gated_replay` | `0.8539 ± 0.0971` | `+0.0396 ± 0.0165` | `324.8` / `1.02` | `10 / 0 / 0` (`2.00 rd`) | `0.9818` |

*`W1` `stable_control_*_far` (`drift_gated_replay` / `fine_tune`)*: `client_psi_far = 83/1000` (`8.3%`), `client_ph_far = 13/1000` (`1.3%`), `client_any_far = 95/1000` (`9.5%`), **`fleet_quorum_far = 4/100` (`4.0%`)** (vs. `static` passive monitor `cPH = 23/1000`, `fleetQ3 = 5/100`).

### 4.2 `ToN-IoT W3` (`Base M_0`: `val_cal F1 = 0.7194`, `prior_audit BCE = 0.0624`, `untouched X_test F1 = 0.7116`, `AUC = 0.9418`)

| Schedule | Arm | `R5–R10` `pre_adapt` F1 | Prior Forgetting $\Delta\mathcal{L}$ | Fed Steps / Comm (MB) | Primary Recovery (`rec / nodrop / notrec`; mean $t$) | Untouched `X_test` `M_10` F1 |
|---|---|---:|---:|---:|---|---:|
| `stable_control` | `static` / `fine_tune` / `drift_gated_replay` | `0.7107 ± 0.0884` | `+0.0000` | `0.0` / `0.00` | `7 / 3 / 0` (`1.43 rd`) | `0.7116` |
| `stable_control` | `unconditional_replay` | `0.7147 ± 0.0452` | `+0.0050 ± 0.0339` | `560.0` / `1.69` | `8 / 2 / 0` (`1.75 rd`) | `0.8034` |
| `gradual_covariate` | `static` | `0.5179 ± 0.0220` | `+0.0000` | `0.0` / `0.00` | `0 / 1 / 9` (`—`) | `0.7116` |
| `gradual_covariate` | `fine_tune` | `0.5511 ± 0.0477` | `+0.1024 ± 0.1496` | `560.0` / `1.69` | `2 / 1 / 7` (`6.00 rd`) | `0.8015` |
| `gradual_covariate` | `unconditional_replay` / `drift_gated_replay` | `0.5351 ± 0.0302` | `+0.0186 ± 0.0350` | `560.0` / `1.69` | `0 / 1 / 9` (`—`) | `0.7927` |
| `abrupt_covariate` | `static` | `0.5132 ± 0.0190` | `+0.0000` | `0.0` / `0.00` | `0 / 1 / 9` (`—`) | `0.7116` |
| `abrupt_covariate` | `fine_tune` | `0.5462 ± 0.0478` | `+0.0906 ± 0.1302` | `560.0` / `1.69` | `3 / 1 / 6` (`5.00 rd`) | `0.7847` |
| `abrupt_covariate` | `unconditional_replay` / `drift_gated_replay` | `0.5279 ± 0.0252` | `+0.0185 ± 0.0257` | `560.0` / `1.69` | `0 / 1 / 9` (`—`) | `0.7816` |
| `recurring_covariate` | `static` | `0.6082 ± 0.0498` | `+0.0000` | `0.0` / `0.00` | `9 / 1 / 0` (`2.67 rd`) | `0.7116` |
| `recurring_covariate` | `fine_tune` | `0.5953 ± 0.0405` | `+0.0210 ± 0.0488` | `320.0` / `0.96` | `8 / 1 / 1` (`2.38 rd`) | `0.7650` |
| `recurring_covariate` | `unconditional_replay` | `0.6083 ± 0.0262` | `+0.0052 ± 0.0336` | `560.0` / `1.69` | `8 / 1 / 1` (`3.13 rd`) | `0.7877` |
| `recurring_covariate` | `drift_gated_replay` | `0.6072 ± 0.0276` | `+0.0015 ± 0.0398` | `320.0` / `0.96` | `8 / 1 / 1` (`3.13 rd`) | `0.7704` |

*`W3` `stable_control_*_far` (`drift_gated_replay` / `fine_tune` / `static`)*: `client_psi_far = 2/1000` (`0.2%`), `client_ph_far = 11/1000` (`1.1%`), `client_any_far = 13/1000` (`1.3%`), **`fleet_quorum_far = 0/100` (`0.0%`)**.

---

## 5. Scientific Interpretation, Compute-Fairness & Honest Limitations

1. **Strong Holm-Confirmatory `C3` Proof on `ToN-IoT W1` (`7 / 10 CONFIRMATORY_HOLM`):**
   - **Drift Recovery (`F1_W1`, `3/3`):** `drift_gated_replay` rescues `CompactMLP` from covariate-drift collapse (`+0.700` gradual, `+0.690` abrupt, `+0.313` recurring Macro-F1 vs. `static`, all `p_Holm <= 3.27e-5`, unanimous `10/10` Wilcoxon `p = 0.00195`).
   - **Catastrophic-Forgetting Protection (`F2_W1`, `3/3`, strictly compute-matched):** At identical federation step budgets (`562.4` gradual/abrupt, `324.8` recurring), `drift_gated_replay` reduces unseen prior-distribution BCE forgetting by **`86.7%–96.1%`** versus `fine_tune` (`+0.040–0.047` vs. `+0.298–1.133`, all `p_Holm <= 0.00078`, `10/10` Wilcoxon), trading a modest exploratory `-0.018` to `-0.058` drifted Macro-F1 difference for dramatic prior stability.
   - **Policy-Cost Protection (`F3_W1`, `1/4` confirmatory + `3/4` exploratory raw):** On `stable_control`, drift gating eliminates **`98.1%`** of unnecessary adaptation steps (`10.4` vs. `560.0`, `p_Holm < 1e-8`) and communication (`0.07` vs. `1.72 MB`), and on `recurring_covariate` eliminates **`42.0%`** of steps (`324.8` vs. `560.0`, exploratory Wilcoxon `p = 0.00195`) while achieving directionally higher `R5–R10` Macro-F1 (`+0.038`).
2. **Honest Extreme-Imbalance Regime Boundary on `ToN-IoT W3` (`1 / 10 CONFIRMATORY_HOLM`, `8 / 10 NS`):**
   - Drift gating achieves **`0/100` (`0.0%`) fleet FAR** and **`100.0%` compute/comm savings** on `stable_control` (`0.0` vs. `560.0` steps, `p_Holm < 1e-8`, `CONFIRMATORY_HOLM`) plus `42.9%` step savings on `recurring_covariate` (`320.0` vs. `560.0`).
   - However, because `W3 X_val` is `98.15%` attack (`~37` benign / `1,985` attack per round, only `~2–6` benign rows/client/round) and `W3 D_fl_train` is `97.93%` attack, `8` mini-batch steps with proportional `98%`-attack replay and frozen `tau_val` yield only small directional Macro-F1 recovery (`+0.015–0.017`, `NS` under parametric Holm, exploratory Wilcoxon `p = 0.031–0.039`) and directional forgetting reduction (`-0.019` to `-0.084`, `NS` under Holm due to high `fine_tune` variance). This establishes a clear **minority-class scarcity boundary** for proportional replay under `53:1` imbalance.
3. **Claims `EXP-GAP-1` Cannot Support (Preserved Scope Boundaries):** Natural chronological or conditional concept drift, `C1` attribution, `C2` 4-tier response, `E6` closed-loop ablation, formal DP, Secure Aggregation, physical IoT gateway latency/energy, logit distillation, or `E5` cross-dataset transfer (`HOLD`).

---

## 6. Output Artifact Hashes & Preservation Status

| Artifact | Path | Verified SHA-256 |
|---|---|---|
| Master Summary JSON | `stage_b4_exp_gap1_e2_mlp/stage_b4_exp_gap1_master_summary.json` | `10c659e888c5b78feff3afa7f41b735cb43f026498cf5e1c1bc6d95eb8e07075` |
| Paired Stats & Holm CSV | `stage_b4_exp_gap1_e2_mlp/stage_b4_exp_gap1_paired_stats_holm.csv` | `9bc76a438b1d09ff031347e7e95af8a3b2fc8df3f4ec171acff4f7dfa2b1b162` |
| Schedule Validation JSON | `stage_b4_exp_gap1_e2_mlp/stage_b4_exp_gap1_schedule_validation.json` | `649d0ac0b3ebb2d7da92cafba498b774965205c025e9fea6ef411416f4977888` |
| Confirmatory Manifest JSON | `stage_b4_exp_gap1_e2_mlp/stage_b4_exp_gap1_manifest.json` | `301556fd5f4e48e5243b05a106cfc9dab36b9e9bc24006b0abf36536b372385d` |
| Unchanged `compact_mlp_continual.py` | `phase4_phd_execution/compact_mlp_continual.py` | `29f490f7126eb4f3aef71f8c29f8e2fae37d9a51ca2a45bdaf3c58cef34b916c` **(byte-identical to Gate 1)** |
| Updated `stage_b4_exp_gap1_e2_mlp.py` | `phase4_phd_execution/stage_b4_exp_gap1_e2_mlp.py` | `fd44f09d731aed6f043542196facbead3e88dba93a7508ebf4cd656b29ac7010` |
| Unchanged Protocol `v5.0` | `docs/research/DA-FIDAF/GAP-1/EXP_GAP_1_Protocol_v5_0.md` | `0ee5dbd15e2116ab0294bcd7d5f8a715837a97aa99cd761e024645f6e7899ad2` |
| Unchanged Frozen Ledgers | `Stage_A4_Fix_...` / `DA_FIDAF_Unified_...` | `47f28614...` / `f51eddce...` |

**Next Step (Stopped):** Awaiting separate user authorization for the **Independent Post-Confirmatory Audit** (do not update cross-stage ledgers or begin `EXP-GAP-2`/`EXP-GAP-3` until audited and approved).
