# DA-FIDAF GAP-1 — Independent Read-Only Post-Confirmatory Audit Report (`EXP-GAP-1`)

**Audit Verdict:** **`PASS`** *(Zero blocking discrepancies across all 7 independent audit requirements; 5 non-blocking empirical/documentation observations logged in §6)*  
**Document Status:** `COMPLETED — READ-ONLY AUDIT PASSED`  
**Audit Date:** `2026-11-28`  
**Audit Mode & Strict Boundary:** **Strictly read-only independent audit.** Zero training runs, pilots, confirmatory executions, or retries were launched. Zero modifications were made to code, `EXP_GAP_1_Protocol_v5_0.md`, datasets, `runs/` outputs, manifests, Gate 1 pilot artifacts, frozen evidence ledgers, or Git-tracked files.  
**Governance Hold Notice:** Cross-stage evidence ledgers have **NOT** been updated, and `EXP-GAP-2` / `EXP-GAP-3` have **NOT** started; both remain blocked pending explicit separate user authorization.

---

## 1. Executive Summary & Requirement-by-Requirement Audit Matrix

| Req # | Audit Requirement | Independent Verification Scope & Result | Status |
|---|---|---|---|
| **Req 1** | Run completeness, uniqueness, assignment & `20` base-model linkage | `320 / 320` expected `(window × schedule × arm × seed)` cells present (`160 W1 + 160 W3`), `0` missing, `0` duplicates; all `20` `(window, seed)` base FL `CompactMLP` models verified **bit-identically linked** (`base_model_m0` excl. wall time, `split_integrity`, `partition_metadata`) across all `16` `(schedule × arm)` trajectories each. | **PASS** |
| **Req 2** | Artifact hashes, sidecars & manifest references | **`328 / 328`** `.sha256` sidecars under `stage_b4_exp_gap1_e2_mlp/` verified raw-byte (`320` run reports + `4` confirmatory top-level artifacts + `4` Gate 1 pilot sidecars); all `320` manifest `run_report_sha256` entries + `3` output hashes + `6` preflight hashes matched `100%` (`0` mismatches). | **PASS** |
| **Req 3** | Independent recomputation of paired stats, exact Wilcoxon & Holm-Bonferroni | Recomputed all **`20` primary Holm** (`F1_W1 m=3`, `F2_W1 m=3`, `F3_W1 m=4`, `F1_W3 m=3`, `F2_W3 m=3`, `F3_W3 m=4`) + **`46` exploratory** comparisons directly from raw `runs/<run_id>/run_report.json` against both `master_summary.json` and `paired_stats_holm.csv`: `max_stat_err = 5.00e-7` (6-decimal rounding), `max_holm_err = 1.39e-8`, **`0` tier mismatches**. | **PASS** |
| **Req 4** | Verified `W1`/`W3` split counts, `W1 ⊂ W3` separation & round/row integrity | Verified exact split counts across all `160 W1` (`53,114/9,374` Train, `2,660/2,661/7,982` Val, `13,253` Test) and `160 W3` (`125,251/22,104` Train, `6,738/6,739/20,216` Val, `10,547` Test) runs; `W1` and `W3` never pooled; recomputed `R4..R10`, `R5..R10`, and `final_prior_audit_forgetting_delta` directly from per-round `rounds[]` (`max_err = 5.00e-7`); verified `3,200` rounds / `32,000` client-rounds step, weight, PH-reset, and `unconditional_replay` `R1..R3` freeze invariants. | **PASS** |
| **Req 5** | Abort gates, missing values, retries, exclusions & pre-onset deviations | `all_abort_gates_passed = True`; `0` `NaN`/`Inf` floats across all `320` JSON trees; `0` retries; `2` Gate 1 pilot runs excluded (`is_pilot_excluded_from_confirmatory == False` and `"pilot_slot" not in r` for all `320` runs); `8` pre-onset `R3` quorum events traced deterministically to `W1 seed=202 R3` (`3`-client PSI FA, expected stochastic behavior under `<= 10%` FAR gate). | **PASS** |
| **Req 6** | Audit of `GAP_1_FINAL_EXPERIMENT_REPORT.md` headline claims & tiering | Line-by-line check confirmed every reported table value, percentage, CI, $p$-value, Wilcoxon $p$, FAR count, and split count matches underlying verified data; strict separation preserved across **`8 CONFIRMATORY_HOLM`**, **`4 EXPLORATORY_RAW_ONLY`**, **`8 NS`**, and `46` exploratory tests; `0` overclaims. | **PASS** |
| **Req 7** | Preservation & isolation of Gate 1 pilot, code, protocol, frozen ledgers & Git | All `12` Gate 1 pilot files (`run_A`, `run_B`, `.npy`/`.npz`, `determinism_diff_report.json`, `pilot_manifest.json`), `compact_mlp_continual.py`, `EXP_GAP_1_Protocol_v5_0.md`, both frozen ledgers, and Git `HEAD` (`da1b5fc69f4d172dea72b6afc74a4257ba36f048`, `0` modified tracked files) independently verified unchanged. | **PASS** |

---

## 2. Inspected Artifacts & Independently Verified SHA-256 Registry

| Category | Artifact Path | Size (B) | Independently Verified SHA-256 | Match |
|---|---|---:|---|---|
| **Confirmatory Output** | `stage_b4_exp_gap1_e2_mlp/stage_b4_exp_gap1_master_summary.json` | — | `10c659e888c5b78feff3afa7f41b735cb43f026498cf5e1c1bc6d95eb8e07075` | **EXACT** |
| **Confirmatory Output** | `stage_b4_exp_gap1_e2_mlp/stage_b4_exp_gap1_paired_stats_holm.csv` | `49,653` | `9bc76a438b1d09ff031347e7e95af8a3b2fc8df3f4ec171acff4f7dfa2b1b162` | **EXACT** |
| **Confirmatory Output** | `stage_b4_exp_gap1_e2_mlp/stage_b4_exp_gap1_schedule_validation.json` | — | `649d0ac0b3ebb2d7da92cafba498b774965205c025e9fea6ef411416f4977888` | **EXACT** |
| **Confirmatory Output** | `stage_b4_exp_gap1_e2_mlp/stage_b4_exp_gap1_manifest.json` | — | `301556fd5f4e48e5243b05a106cfc9dab36b9e9bc24006b0abf36536b372385d` | **EXACT** |
| **Confirmatory Runs** | `stage_b4_exp_gap1_e2_mlp/runs/<run_id>/run_report.json` (`320` files + `320` `.sha256`) | `320` files | `320 / 320` raw-byte sidecar + manifest hash matches (`0` mismatches) | **EXACT** |
| **Implementation** | `phase4_phd_execution/compact_mlp_continual.py` | `48,477` | `29f490f7126eb4f3aef71f8c29f8e2fae37d9a51ca2a45bdaf3c58cef34b916c` | **EXACT (Gate 1)** |
| **Implementation** | `phase4_phd_execution/stage_b4_exp_gap1_e2_mlp.py` | — | `fd44f09d731aed6f043542196facbead3e88dba93a7508ebf4cd656b29ac7010` | **EXACT (Gate 2)** |
| **Gate 1 Pilot** | `pilot_determinism_check/pilot_manifest.json` | `2,487` | `a0f2785389d2f864c20460d1383c515208a2ed242033e9c5e5778377f012151b` | **EXACT** |
| **Gate 1 Pilot** | `pilot_determinism_check/determinism_diff_report.json` | `1,786` | `e84a0ac9f8560b171ac885020afdf739d2f1c6d4df2f7050540f759cf95bfdca` | **EXACT** |
| **Gate 1 Pilot** | `pilot_determinism_check/run_A/run_report.json` & `run_B/run_report.json` | `107,304` / `107,303` | `0e330fd5a4c29cb3...61633a` / `0a5762a3e02bdd73...19e92bf7` | **EXACT** |
| **Gate 1 Pilot** | `pilot_determinism_check/run_{A,B}/{model_theta_0,model_theta_10,prior_audit_probs}.npy` & `pre_adapt_probs.npz` | `8` binary files | Bit-identical `run_A == run_B` (`7cab365a...`, `03c259a0...`, `ae2e1bf9...`, `8245211e...`) | **EXACT** |
| **Protocol & Docs** | [`EXP_GAP_1_Protocol_v5_0.md`](EXP_GAP_1_Protocol_v5_0.md) *(repo + external mirror)* | `29,619` | `0ee5dbd15e2116ab0294bcd7d5f8a715837a97aa99cd761e024645f6e7899ad2` | **EXACT** |
| **Protocol & Docs** | [`GAP_1_FINAL_EXPERIMENT_REPORT.md`](GAP_1_FINAL_EXPERIMENT_REPORT.md) | `20,854` | `5ecd61238596d5cf6c1967753a0d6f6aa9024a6a92b5f56b1feea0c2a6c0946f` | **EXACT** |
| **Protocol & Docs** | [`GAP_1_GATE_2_READINESS_REPORT.md`](GAP_1_GATE_2_READINESS_REPORT.md) | `11,027` | `5d2e7e39763e061b7116eeb1400846b2566c18fc203cb43d5b52f7233cd980c2` | **EXACT** |
| **Protocol & Docs** | [`GAP_1_POST_PILOT_AUDIT_REPORT.md`](GAP_1_POST_PILOT_AUDIT_REPORT.md) | `12,902` | `aaf15b19d115129a749299d160b5fc5a8b9e8f51f61a3d956951a2f98395b9bd` | **EXACT** |
| **Frozen Ledgers** | `stage_a4_evidence_freeze/Stage_A4_Fix_Evidence_Freeze_and_Claim_Ledger.md` | — | `47f28614879b019f075cdfcc4e586998ad59588f584af11b6e6073bd5f6a7335` | **EXACT** |
| **Frozen Ledgers** | `unified_cross_stage_freeze/DA_FIDAF_Unified_Cross_Stage_Evidence_and_Claim_Ledger.md` | — | `f51eddcea12928c6ab465bd12a21e9c22f99b59a55d3a36a9cda210c09810d4f` | **EXACT** |
| **Git State** | `I:\Projects\da-fidaf` (`main`) | — | `HEAD = da1b5fc69f4d172dea72b6afc74a4257ba36f048`, `0` modified tracked files | **EXACT** |

---

## 3. Independent Verification of Run Completeness, Linkage & Protocol Invariants (Req 1, 2, 4, 5)

### 3.1 Run Matrix, `20` Base Models & Exclusion Checks
- **Completeness & Uniqueness:** Scanning `runs/*/run_report.json` returned exactly **`320`** unique `run_id` directories mapping `1-to-1` onto the full Cartesian grid `2 windows (W1, W3) × 4 schedules (stable_control, gradual_covariate, abrupt_covariate, recurring_covariate) × 4 arms (static, fine_tune, unconditional_replay, drift_gated_replay) × 10 seeds (42, 101, 202, 303, 404, 505, 606, 707, 808, 909)`. Zero missing cells, zero duplicate cells, zero retries.
- **Base-Model Linkage (`20 × 16`):** Grouping all `320` runs by `(window_id, seed)` verified that all `16` `(schedule × arm)` trajectories sharing a `(window_id, seed)` pair have **identical** `base_model_m0` metrics (excluding wall time), `split_integrity` records, and `partition_metadata` (client shard counts and reservoir allocations).
- **Pilot Isolation:** Every single one of the `320` confirmatory `run_report.json` files has `is_pilot_excluded_from_confirmatory == False` and omits `"pilot_slot"`. The `2` Gate 1 pilot runs reside exclusively inside `pilot_determinism_check/` and appear nowhere in `runs/`, `stage_b4_exp_gap1_manifest.json` (`total_confirmatory_runs = 320`, `pilot_runs_excluded_count = 2`), or any statistical calculation.

### 3.2 Verified Split Counts, Data Isolation & Per-Round Algorithmic Invariants
- **Verified Runtime Split Counts (`StratifiedShuffleSplit(0.15)` `ceil` behavior confirmed across all `320` runs):**
  - `ToN-IoT W1` (`160/160` runs, `12,292 B` model): `X_train = 62,488` → `D_fl_train = 53,114`, `D_prior_audit = 9,374`; `X_val = 13,303` → `D_val_cal = 2,660`, `D_val_psi_ref = 2,661`, stream `S_1..S_10 = 7,982` (`[799×2, 798×8]`); untouched `X_test = 13,253`.
  - `ToN-IoT W3` (`160/160` runs, `12,036 B` model): `X_train = 147,355` → `D_fl_train = 125,251`, `D_prior_audit = 22,104`; `X_val = 33,693` → `D_val_cal = 6,738`, `D_val_psi_ref = 6,739`, stream `S_1..S_10 = 20,216` (`[2022×6, 2021×4]`); untouched `X_test = 10,547`.
- **Integrity Flags (`320 / 320` runs):** `disjoint_assertion_passed == True`, `psi_ref_labels_accessed == False`, `x_test_used_for_psi_cal_or_adapt == False`, `source_arrays_immutable == True`, `dp_enabled == False`, `secure_aggregation_active == False`, `byzantine_clients == 0`, `0` `NaN`/`Inf` values anywhere in any JSON tree.
- **Trajectory Summary Recomputation from Raw Rounds (`320` runs, `3,200` rounds, `32,000` client-rounds):**
  - Recomputing `mean_r4_r10_pre_adapt_macro_f1` (mean of rounds `R4..R10`), `mean_r5_r10_pre_adapt_macro_f1` (mean of rounds `R5..R10`), and `final_prior_audit_forgetting_delta` (`R10` cumulative forgetting delta) directly from `rounds[]` yielded **`max_abs_err = 5.00e-7`** (strictly 6-decimal serialization rounding).
  - Across all `32,000` client-rounds: participating clients executed exactly `8` optimizer steps (`512` sample presentations) and non-participating clients executed `0` steps (`0` presentations); aggregation weights summed to `1.000000` on every adapting round; `ph_reset_after_adapt == participated_in_adapt` held `100%`; communication bytes matched exact model byte size × active upload/download counts; and `unconditional_replay` remained strictly frozen (`0` adaptations) on `R1..R3` (`100%` compliance with `D4`/`RD-5`).

### 3.3 Exact Audit of Pre-Onset (`R1..R3`), Recurring-`OFF` (`R6, R7, R10`) & `stable_control` Quorum Events
Independent inspection of all `3,200` rounds accounted for **100%** of every non-drift quorum event across the entire `320`-run suite:
1. **Pre-Onset (`R1..R3`) Quorum Events (`8` total across `320` runs):** All `8` originated from a single deterministic event — **`ToN-IoT W1`, `seed=202`, `R3`** — where `3/10` clients exceeded the PSI threshold (`3` PSI, `0` PH), meeting `q_min = 3` and executing `3 × 8 = 24` federation steps. Because `R1..R3` has `drift_intensity = 0.0` across all four schedules, this exact event occurred identically in `stable_control`, `gradual_covariate`, `abrupt_covariate`, and `recurring_covariate` for both `fine_tune` and `drift_gated_replay`, accounting for the exact `+2.4` mean steps (`24 / 10`) on `W1` `gradual`/`abrupt` (`562.4` vs. `560.0`). Zero pre-onset triggers occurred on `W3`.
2. **`recurring_covariate` `OFF`-Round (`R6, R7, R10`) Quorum Events (`2` total across both gated arms = `1/30` = `3.3%` per arm on `W1`, `0/30` on `W3`):** Originated solely from **`W1`, `seed=505`, `R6`** (`3` PSI, `0` PH → `24` steps), identically in `fine_tune` and `drift_gated_replay`. Together with `seed=202 R3`, this accounts for exact `W1` `recurring_covariate` mean federation steps: `320.0 + (24 + 24)/10 = 324.8`.
3. **`stable_control` Quorum False-Alarm Events (`4/100` = `4.0%` per gated arm on `W1`; `0/100` = `0.0%` on `W3`):** Identical across `fine_tune` and `drift_gated_replay` on `W1`:
   - `seed=202, R3`: `3` clients (`3` PSI, `0` PH) → `24` steps
   - `seed=505, R5`: `4` clients (`2` PSI, `2` PH) → `32` steps
   - `seed=505, R6`: `3` clients (`3` PSI, `0` PH) → `24` steps
   - `seed=909, R9`: `3` clients (`1` PSI, `2` PH) → `24` steps
   - Total = `104` steps across `10` seeds → exact mean **`10.4`** steps (`0.0` on `W3`), comfortably within the `<= 10%` fleet FAR abort gate.

---

## 4. Independent Statistical & Holm-Bonferroni Recomputation (Req 3)

Recomputing all **`66` paired comparisons** (`20` primary Holm + `46` exploratory) directly from raw `runs/<run_id>/run_report.json` via two-sided paired Student-$t$ (`df = 9`), exact two-sided Wilcoxon signed-rank (`zero_method="wilcox"`, `method="exact"`), and step-down Holm-Bonferroni (`m` per family verified against `EXP_GAP_1_Protocol_v5_0.md` §10.2) matched both `stage_b4_exp_gap1_master_summary.json` and `stage_b4_exp_gap1_paired_stats_holm.csv` with:
- **`max_stat_err = 5.00e-7`** (mean, SD, mean diff, CI bounds, $t$-stat, Cohen's $d_z$, raw $p$, Wilcoxon $p$ — pure 6-decimal rounding)
- **`max_holm_err = 1.39e-8`**
- **`tier_mismatches = 0 / 66`**

### 4.1 Multiplicity Families, Denominators & Step-Down Verification (`20` Primary Tests)

| Window | Family | Approved `m` | Verified `m` | `n_pairs` / `df` | `CONFIRMATORY_HOLM` | `EXPLORATORY_RAW_ONLY` | `NS` | Step-Down Audit Note |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `ToN-IoT W1` | `F1_W1` | `3` | `3` | `10` / `9` | **`3`** | `0` | `0` | All `p_Holm <= 3.27e-5`; unanimous `10/10` Wilcoxon (`0.00195`). |
| `ToN-IoT W1` | `F2_W1` | `3` | `3` | `10` / `9` | **`3`** | `0` | `0` | All `p_Holm <= 0.00078`; unanimous `10/10` Wilcoxon (`0.00195`). |
| `ToN-IoT W1` | `F3_W1` | `4` | `4` | `10` / `9` | **`1`** | **`3`** | `0` | Rank-1 (`steps`) `p_Holm < 1e-8`; rank-2 (`recurring` forgetting) raw `p = 0.01669077 × 3 = 0.05007231 > 0.05`, correctly clamping ranks 3 & 4 to `p_Holm = 0.05007231` (`EXPLORATORY_RAW_ONLY`). |
| `ToN-IoT W3` | `F1_W3` | `3` | `3` | `10` / `9` | `0` | `0` | **`3`** | Parametric `p_Holm >= 0.17670` (`NS`); directional Wilcoxon `0.031–0.039` properly left non-confirmatory. |
| `ToN-IoT W3` | `F2_W3` | `3` | `3` | `10` / `9` | `0` | **`1`** | **`2`** | `recurring` forgetting raw `p = 0.02092 × 3 = 0.06277` (`EXPLORATORY_RAW_ONLY`); `gradual`/`abrupt` `p_Holm = 0.17908` (`NS`). |
| `ToN-IoT W3` | `F3_W3` | `4` | `4` | `10` / `9` | **`1`** | `0` | **`3`** | `stable_control` steps `-560.0` (`0` var, `p_Holm < 1e-8`, Wilcoxon `0.00195`); remaining `3` endpoints `p_Holm >= 0.992` (`NS`). |
| **Total** | **6 families** | **`20`** | **`20`** | `10` / `9` | **`8`** | **`4`** | **`8`** | **100% match to pre-registered family structure & denominators.** |

- **Exploratory Tier Check (`46` comparisons):** All `46` exploratory tests carry `is_primary_holm = False`, `family = "exploratory_not_in_primary_holm"`, blank `family_m` / `holm_p`, and `tier = "EXPLORATORY_NOT_IN_PRIMARY_HOLM"`. None were promoted into primary Holm families.

---

## 5. Audit of `GAP_1_FINAL_EXPERIMENT_REPORT.md` Conclusions & Claim Boundaries (Req 6)

Line-by-line verification of [`GAP_1_FINAL_EXPERIMENT_REPORT.md`](GAP_1_FINAL_EXPERIMENT_REPORT.md) against raw recomputed data confirmed **`0` numerical errors and `0` claim-tier violations**:
- **Exact Quantitative Fidelity:** Every single cell in §1.1 (verified split counts), §2 (schedule validation & abort gates), §3.1–§3.2 (`20` primary Holm rows), §4.1–§4.2 (`32` per-schedule/per-arm rows + `stable_control_*_far` counts), and §5 derived percentages (`86.7%–96.1%` `W1` forgetting reduction; `98.1%` / `42.0%` `W1` and `100.0%` / `42.9%` `W3` step reductions; `W3` `98.15%` Val / `97.93%` Train attack rates) matched independently recomputed values to every printed digit.
- **Strict Evidence Tiering:** Headline claims cleanly separate **`8 CONFIRMATORY_HOLM`** findings (`7/10` on `W1`, `1/10` on `W3`) from **`4 EXPLORATORY_RAW_ONLY`** (`3` on `F3_W1` at `p_Holm = 0.05007`, `1` on `F2_W3` at `p_Holm = 0.06277`), **`8 NS`** (all on `W3`), and exploratory comparisons (`fine_tune` drifted F1 trade-off `-0.018` to `-0.058`, `recurring` step savings, `W3` directional Wilcoxon `p = 0.031–0.039`).
- **Scope & Honesty Boundaries Preserved:** `W1 ⊂ W3` non-pooling, `X_test` untouched for PSI/calibration/adaptation, `NON_DP_BASELINE_ONLY`, `secure_aggregation_active = False`, `K = 10` simulated gateways on desktop `GTX 1650`, synthetic covariate-shift interventions, `E5: HOLD`, and the honest `W3` `53:1` minority-class scarcity boundary are all stated unambiguously.

---

## 6. Non-Blocking Observations & Empirical Caveats (Informational Only)

None of the following observations invalidate any result or block audit passage; they are logged explicitly for thesis-grade traceability:

1. **Single Pre-Onset Quorum Event (`W1 seed=202 R3`):** As detailed in §3.3, `3/10` clients triggered PSI on clean round `R3` (`24` steps), adding `+2.4` mean steps to `W1` drifted gated arms (`562.4` vs. `560.0`). This is expected stochastic detector behavior well within the `<= 10%` fleet FAR gate (`4/100 = 4.0%`).
2. **Narrow Step-Down Holm Miss on `F3_W1` (`p_Holm = 0.05007231`):** All three non-step `F3_W1` endpoints had raw $p \in [0.0167, 0.0299]$ but missed Holm `0.05` by `7.23e-5` due to rank-2 `0.01669077 × 3 = 0.05007231`. Any future ledger/manuscript citation MUST preserve their `EXPLORATORY_RAW_ONLY` classification.
3. **`ToN-IoT W3` Extreme Imbalance Boundary (`98.15%` Attack on `X_val`):** Parametric `F1_W3` and `F2_W3` are `NS` under Holm (`1/10` confirmatory on `W3`, solely `stable_control` step savings). Manuscript framing must present `W3` honestly as a minority-class scarcity boundary rather than pooling with `W1`.
4. **Option B-Hybrid Key Naming Convention:** Per approved Gate 2 Option B-Hybrid, `compact_mlp_continual.py` stayed `100%` byte-identical to Gate 1 (so per-run JSONs retain legacy `all_rounds_*_far` keys), while `stage_b4_exp_gap1_master_summary.json` and `GAP_1_FINAL_EXPERIMENT_REPORT.md` expose clean `all_rounds_*_trigger_rate` and `stable_control_*_far` labels.
5. **Minor Historical Typo in Gate 1 Report Only (Already Resolved in Post-Pilot Audit):** As previously recorded in [`GAP_1_POST_PILOT_AUDIT_REPORT.md`](GAP_1_POST_PILOT_AUDIT_REPORT.md), the Gate 1 report (`GAP_1_DETERMINISM_PILOT_REPORT.md` §3) contained a transcription typo in the `pilot_manifest.json` hash, and frozen `v5.0` text rounded `StratifiedShuffleSplit(0.15)` by `1` row (`53,115/9,373` vs. verified `53,114/9,374` on `W1`; `125,252/22,103` vs. verified `125,251/22,104` on `W3`). All Gate 2 outputs, manifests, and reports record the exact verified runtime counts and true `pilot_manifest.json` hash (`a0f2785389d2f864c20460d1383c515208a2ed242033e9c5e5778377f012151b`).

---

## 7. Final Audit Verdict & Remaining Authorization Gates

- **Final Independent Post-Confirmatory Audit Verdict:** **`PASS`** *(7 / 7 requirements passed; zero blocking discrepancies).*
- **Current Authorized Stop Point:** `EXP-GAP-1` confirmatory execution and independent audit are complete and verified.
- **Blocked Pending Separate Explicit User Authorization:**
  1. **Cross-Stage Ledger Integration Gate:** Creating/updating any unified cross-stage claim ledger (while preserving frozen pre-GAP-1 ledger snapshots immutable) with the audited `EXP-GAP-1` (`E2` + `C3`) evidence (`8 CONFIRMATORY_HOLM`, `4 EXPLORATORY_RAW_ONLY`, `8 NS`, strict `W1`/`W3` separation).
  2. **Next-Gap Gate (`EXP-GAP-2` / `EXP-GAP-3`):** Protocol authoring and execution for `C1` attribution fidelity or `C2` 4-tier response latency/telemetry.
