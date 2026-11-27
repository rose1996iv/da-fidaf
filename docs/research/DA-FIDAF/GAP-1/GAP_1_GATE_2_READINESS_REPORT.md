# DA-FIDAF GAP-1 — Gate 2 Readiness Report (Read-Only Review)

**Status:** **`READY FOR EXPLICIT GATE 2 USER AUTHORIZATION`** *(with 1 lightweight schema-naming preference to confirm; zero blocking methodological or technical defects)*  
**Date:** `2026-11-28`  
**Review Mode:** Strict read-only readiness check. Zero code, protocol files, configs, datasets, pilot artifacts, tracked repository files, or frozen evidence ledgers were modified; zero experiments or confirmatory runs were executed.  
**Governing Anchors (All Independently Verified Unchanged):**
- Protocol `v5.0`: [EXP_GAP_1_Protocol_v5_0.md](EXP_GAP_1_Protocol_v5_0.md) (`0ee5dbd15e2116ab0294bcd7d5f8a715837a97aa99cd761e024645f6e7899ad2`)
- Gate 1 Pilot Report: [GAP_1_DETERMINISM_PILOT_REPORT.md](GAP_1_DETERMINISM_PILOT_REPORT.md) (`cbd335405b91ad62821b8a443c66d53e2335891e854d77a975300523573c4ce9`, Verdict: `PASS`)
- Post-Pilot Audit: [GAP_1_POST_PILOT_AUDIT_REPORT.md](GAP_1_POST_PILOT_AUDIT_REPORT.md) (`aaf15b19d115129a749299d160b5fc5a8b9e8f51f61a3d956951a2f98395b9bd`, `9/9` criteria `PASS`)
- Readiness Plan: [GAP_1_DETERMINISM_PILOT_READINESS_AND_EXECUTION_PLAN.md](GAP_1_DETERMINISM_PILOT_READINESS_AND_EXECUTION_PLAN.md) (`cf88a1dc969f041681242194105eccbe54043719428ba202b45b233f80f51603`)
- Audited Pilot Code: `compact_mlp_continual.py` (`29f490f7...`), `stage_b4_exp_gap1_e2_mlp.py` (`61bd307a...`)

---

## 1. Verification of the 320-Run Confirmatory Matrix, Statistical Plan & Expected Outputs

### 1.1 Confirmatory Run Matrix (`independently verified` against `v5.0`)

| Dimension | Specification | Count |
|---|---|---:|
| Chronological ToN-IoT windows (`W1 ⊂ W3`, strictly separate, never pooled) | `ToN-IoT W1` (`d=11`, `3,073` params), `ToN-IoT W3` (`d=10`, `3,009` params) | `2` |
| Synthetic drift schedules (`T = 10`, `onset_round = 4`, `s = 1.5`) | `stable_control`, `gradual_covariate`, `abrupt_covariate`, `recurring_covariate` | `4` |
| Adaptation arms (`K = 10`, `Dir(0.5)`, `q_min = 3`, `8 × 64 = 512` presentations) | `static`, drift-gated `fine_tune`, `unconditional_replay` (`R4..R10`), `drift_gated_replay` | `4` |
| Matched random seeds (`SEEDS_10`, `df = 9`) | `(42, 101, 202, 303, 404, 505, 606, 707, 808, 909)` | `10` |
| **Base FL `CompactMLP` Models ($M_0$)** | Reused bit-identically across all `16` `(schedule × arm)` trajectories per `(window, seed)` | **`20`** |
| **Confirmatory Trajectory Runs** | `2 windows × 4 schedules × 4 arms × 10 seeds` (each with unique `run_id` UUID) | **`320`** |
| **Excluded Gate 1 Pilot Runs** | Preserved untouched in `pilot_determinism_check/`; permanently excluded from confirmatory totals & stats | **`2`** *(excluded)* |

- **Empirically Calibrated Runtime Estimate (`GTX 1650`, `torch 2.6.0+cu124`):** Based on actual measured Gate 1 `W1` timing (`~5.5s` base FL $M_0$, `~3.9s` per `7`-adaptation trajectory) and `W3`'s `2.36×` larger `D_fl_train` / `2.53×` larger stream blocks (with `80` `static` and `~40` `stable` gated runs doing `0` adaptations), total wall time is estimated at **`~12–22 minutes`** (revising v3.0's pre-pilot estimate of `3.5–7.5 min`).

### 1.2 Pre-Registered Paired Comparisons & Statistical Tests (`20` Primary Holm Tests = `10` per Window)

All confirmatory tests are matched-seed (`n = 10`, `df = 9`) and computed **strictly separately** for `W1` and `W3` using `common_phase4.paired_student_t` (exact two-sided $p$, 95% $t$-CI, Cohen's $d_z$, zero-variance guard) + `common_phase4.apply_holm_bonferroni` ($\alpha = 0.05$) + exact two-sided Wilcoxon signed-rank (`scipy.stats.wilcoxon(..., method="exact", zero_method="wilcox")`, reporting `n_nonzero` and exact $p_{\text{wilcoxon}}$):

| Family | Window Scope | `m` per Window | Treatment vs. Baseline | Primary Endpoint | Schedules |
|---|---|---:|---|---|---|
| **`F1`** | Separate `W1`, `W3` | `3` | `drift_gated_replay` vs. `static` | `mean_r5_r10_pre_adapt_macro_f1` | `gradual`, `abrupt`, `recurring` |
| **`F2`** | Separate `W1`, `W3` | `3` | `drift_gated_replay` vs. `fine_tune` | `final_prior_audit_forgetting_delta` | `gradual`, `abrupt`, `recurring` |
| **`F3`** | Separate `W1`, `W3` | `4` | `drift_gated_replay` vs. `unconditional_replay` | `mean_r4_r10_pre_adapt_macro_f1` (`stable`), `final_prior_audit_forgetting_delta` (`stable`, `recurring`), `total_federation_adapt_steps` (`stable`) | `stable_control`, `recurring_covariate` |

- All other contrasts (`fine_tune` vs. `static`, `drift_gated_replay` vs. `fine_tune` on Macro-F1, per-round `R1..R10`, untouched `X_test` `M_0`/`M_10`, `ROC-AUC`, `ECE`, `Brier`, `post_adapt_same_batch_diagnostic`) are explicitly labeled `exploratory_not_in_primary_holm`.

### 1.3 Expected Confirmatory Outputs (Isolated Under `stage_b4_exp_gap1_e2_mlp\`)

- `pilot_determinism_check\` — preserved `100%` untouched.
- `runs\<run_id>\run_report.json` + `.sha256` (`320` confirmatory runs, `"is_pilot_excluded_from_confirmatory": false`).
- `stage_b4_exp_gap1_master_summary.json` + `.sha256` (separate `W1` & `W3` blocks, per-round & trajectory aggregates, client/fleet `stable_control` FAR, compute-fairness tables, untouched `X_test` static audit).
- `stage_b4_exp_gap1_paired_stats_holm.csv` + `.sha256` (`20` primary Holm rows + labeled exploratory rows).
- `stage_b4_exp_gap1_schedule_validation.json` + `.sha256` (all schedule, guard, and immutability gates across `320` runs).
- `stage_b4_exp_gap1_manifest.json` + `.sha256` (code/protocol/ledger/output SHA-256s + Git `HEAD`).
- Post-run report inside `docs/`: `docs/research/DA-FIDAF/GAP-1/GAP_1_FINAL_EXPERIMENT_REPORT.md` + `README.md` update.

---

## 2. Explicit Resolution of the Three Review Items for Gate 2

### Item 1 — Split Count Clarification (`53,115/9,373` vs. `53,114/9,374`)

- **Exact Finding (`independently verified` via read-only `StratifiedShuffleSplit` check on both `W1` and `W3`):**
  - First, note that this 1-row difference is in the **`X_train` (`D_fl_train` / `D_prior_audit`)** 85/15 split — **NOT in `X_val`**, whose 3-way splits match `v5.0` to the exact row on both windows!
  - Specifically, scikit-learn's `StratifiedShuffleSplit(test_size=0.15)` computes `math.ceil(0.15 * N)` rather than `math.floor(0.15 * N)`:

| Window | Split | `v5.0` Text (`floor`) | Verified `StratifiedShuffleSplit` (`ceil`) | Sum Verified |
|---|---|---:|---:|---:|
| **`W1`** | `X_train (62,488)` → `D_fl_train / D_prior_audit` | `53,115 / 9,373` | **`53,114 / 9,374`** (`-1 / +1`) | `62,488` (exact) |
| **`W1`** | `X_val (13,303)` → `D_val_cal / D_val_psi_ref / S_1..S_10` | `2,660 / 2,661 / 7,982` | **`2,660 / 2,661 / 7,982`** (`0` diff; `[799×2, 798×8]`) | `13,303` (exact) |
| **`W3`** | `X_train (147,355)` → `D_fl_train / D_prior_audit` | `125,252 / 22,103` | **`125,251 / 22,104`** (`-1 / +1`) | `147,355` (exact) |
| **`W3`** | `X_val (33,693)` → `D_val_cal / D_val_psi_ref / S_1..S_10` | `6,738 / 6,739 / 20,216` | **`6,738 / 6,739 / 20,216`** (`0` diff; `[2022×6, 2021×4]`) | `33,693` (exact) |

- **Resolution:** **No code change and no rewrite of `v5.0` needed.** Documented here as an authoritative 1-row `StratifiedShuffleSplit` `ceil` note; all Gate 2 outputs and reports will cite exact runtime counts (`53,114 / 9,374` on `W1`; `125,251 / 22,104` on `W3`).

### Item 2 — Handling of `pilot_slot` in Confirmatory Outputs

- **Resolution:** **Omit `pilot_slot` from confirmatory `run_report.json` outputs.** `pilot_slot` (`"run_A"` / `"run_B"`) is exclusively a Gate 1 determinism-pilot metadata field; confirmatory runs are identified by `run_id`, `window_id`, `schedule_arm`, `adaptation_arm`, `seed`, and `"is_pilot_excluded_from_confirmatory": false`. Gate 1 pilot files remain untouched.

### Item 3 — Telemetry Key Naming (`all_rounds_*_far` vs. `all_rounds_*_trigger_rate`)

| Option | Effect on `compact_mlp_continual.py` | Effect on Output Clarity | Recommendation |
|---|---|---|---|
| **Option B-Hybrid *(Recommended)*** | Keeps `compact_mlp_continual.py` **`100%` byte-identical** (`SHA-256: 29f490f7...`) to the Gate 1 audited pilot module (zero code churn in core logic). | Per-run JSON keeps pilot-identical keys (`all_rounds_*_far`), while `stage_b4_exp_gap1_master_summary.json` & final report expose clean **`all_rounds_*_trigger_rate`** (all schedules) and **`stable_control_*_far`** (`stable_control` only). | **Recommended** — preserves exact Gate 1 audited library hash while preventing misleading FAR labels in summaries. |
| **Option A** | Edits 4 key names inside `compact_mlp_continual.py` (`all_rounds_*_far` → `all_rounds_*_trigger_rate`), changing its SHA-256 relative to `pilot_manifest.json` (zero algorithmic/numeric change). | Per-run JSON and master summary both use `all_rounds_*_trigger_rate`. | Acceptable if clean per-run key naming is preferred over keeping `compact_mlp_continual.py` byte-identical. |

---

## 3. Code Changes & Runtime Gates Required Upon Gate 2 Authorization

- **Protocol / Addendum Needed?** **No** — `EXP_GAP_1_Protocol_v5_0.md` stays locked and untouched; this readiness report records the 1-row `StratifiedShuffleSplit` `ceil` clarification and `SeedSequence` tag `404` traceability note (`DISCREPANCY-1` & `DISCREPANCY-2` from Post-Pilot Audit).
- **Sole Authorized Code Edit Upon Gate 2 Approval:**
  - Extend `I:\Projects\da-fidaf-runs\phase4_phd_execution\stage_b4_exp_gap1_e2_mlp.py` to add `--mode confirmatory` (verifying `pilot_manifest.json` `overall_determinism_pass == True`, enforcing fail-closed empty `runs/` guard, caching the `20` base FL models per `(window, seed)`, running all `320` trajectories with `CUBLAS_WORKSPACE_CONFIG=:4096:8` + `warn_only=False`, computing Holm `F1`/`F2`/`F3` + exact Wilcoxon + exploratory stats, and writing canonical LF JSON/CSV + `.sha256` sidecars).
  - `compact_mlp_continual.py` stays byte-identical under Option B-Hybrid (or updates only the 4 summary key names under Option A).
- **Hard Runtime Abort Gates Preserved for Confirmatory Suite:**
  1. Any `NaN`/`Inf` in parameters, logits, gradients, or BCE loss.
  2. Any split-overlap, reservoir `< 32`, stream-guard, or `X_test` access assertion failure.
  3. `stable_control` combined (`PSI or PH`) fleet quorum FAR `> 10%` of rounds across `10` seeds on either `W1` or `W3` (live `PH` FAR across `R4..R10` on `stable_control` remains unverified until confirmatory execution!).
  4. `static` showing `no_drop` across all `10` seeds on `abrupt_covariate` on either `W1` or `W3`.

---

## 4. Final Gate 2 Readiness Determination

**`READY FOR EXPLICIT GATE 2 USER AUTHORIZATION`**

- **Remaining Blockers:** **Zero** methodological or data-integrity blockers. Only (1) explicit user authorization for **Gate 2** (`--mode confirmatory`, `20` base models + `320` trajectories) and (2) confirmation of telemetry key preference (**Option B-Hybrid** [keep `compact_mlp_continual.py` byte-identical, use `trigger_rate`/`stable_control_far` in master summary] vs. **Option A** [rename keys inside `compact_mlp_continual.py`]) are needed before proceeding.
