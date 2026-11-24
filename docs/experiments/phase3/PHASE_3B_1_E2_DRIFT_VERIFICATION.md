# DA-FIDAF Phase 3B.1 — E2 Independent Drift & Continual Adaptation Verification

- **Scope:** All `60` standalone E2 drift-arm `run_report.json` files (`30` W1 + `30` W3) plus the `20` embargo sensitivity records (`300s`/`900s`) stored in `e2_master_summary.json`.

---

## Finding [AUD-03A] — MEDIUM: E2 Standalone Artifact Count (`60` Directories vs. `80` Expected Runs)

- **Finding ID:** `AUD-03A` | **Severity:** `MEDIUM`
- **Evidence File:** `I:\Projects\da-fidaf-runs\phase3b\e2\` & `e2_master_summary.json`
- **Run IDs:** All `60` E2 drift-arm run IDs verified; `20` embargo sensitivity runs (`embargo_300s` & `embargo_900s` × `5` seeds × `2` windows) had no individual `run_report.json` or `.sha256` files.
- **Verification Method:** Recursive filesystem inventory of `phase3b\e2\`.
- **Original Reported vs. Independently Recalculated:** Reported `80` E2 runs (`40` W1 + `40` W3); recalculated `60` standalone `run_report.json` files + `20` summary-embedded embargo runs.
- **Scientific Implication:** Metrics exist in `e2_master_summary.json`, but auditability/checksum provenance is weaker for the 20 embargo runs.
- **Recommended Action:** Emit standalone `run_report.json` + `.sha256` artifacts for embargo sensitivity runs in Phase 4.

---

## Finding [AUD-03B] — MEDIUM: Round-8 Covariate Schedule Equivalence & One-Sided Page-Hinkley Behavior on W1

- **Finding ID:** `AUD-03B` | **Severity:** `MEDIUM`
- **Evidence File:** `e2_w1_gradual_covariate_seed42`, `e2_w1_recurring_covariate_seed42`, `e2_w1_abrupt_conditional_drift_seed42`, `e2_w3_abrupt_conditional_drift_seed42`
- **Verification Method:** Inspected raw 8-round `psi_trajectory` and `loss_trajectory` arrays directly from raw JSON files.
- **Key Verified Facts:**
  1. **Zero-Round Detection (`delay_psi = 0`) Is Genuine, Not Pre-Triggered:**
     - `W1 gradual_covariate` `seed=42` `psi_traj`: `[0.0, 0.0, 12.434, 12.434, 12.434, 12.434, 12.434, 12.434]`.
     - `W1 recurring_covariate` `seed=42` `psi_traj`: `[0.0, 0.0, 12.434, 12.434, 0.0, 0.0, 12.434, 12.434]`.
     - Pre-onset rounds `1..2` had `PSI = 0.0` (`0` false alarms across all `60` runs); detection fired cleanly at `round 3` (first post-onset observation).
  2. **Why `abrupt`, `gradual`, and `recurring` Had Identical Round-8 Macro-F1 (`0.4779` Static / `0.5507` Replay):**
     - Adaptation was evaluated only at `round 8`, where `abrupt`, `gradual` (`onset=3, dur=4`), and `recurring` (`onset=3, period=2` -> rounds 7–8 ON) all had exact `intensity = 1.0` and identical RNG seed `seed + 8`.
  3. **Why Page-Hinkley Missed W1 `abrupt_conditional_drift` (`delay_ph = None`) but Caught W3 (`delay_ph = 0`):**
     - W1 `loss_traj`: `[0.5772, 0.5772, 0.5549, 0.5304, 0.5364, 0.5506, 0.5591, 0.5372]` — because the W1 linear model was already inverted on Val, flipping labels on `row[0] > 0` *reduced* BCE loss (`0.577 -> 0.530`), and `PageHinkleyDetector` only monitors upward loss increases.
     - W3 `loss_traj`: `[0.1557, 0.1557, 1.2712, 1.3272, 1.2727, 1.2036, 1.2683, 1.1969]` — loss jumped `+1.116` at round 3, triggering `PageHinkley` immediately (`delay = 0`).
  4. **Four-Way Drift Distinction Verified:**
     - **Covariate Shift ($P_t(X)$):** Measured by PSI/JSD (`delay = 0`); does NOT prove conditional drift.
     - **Label/Prior Shift ($P_t(Y)$):** Tested separately (`abrupt_prior_shift`); PSI stayed `None`.
     - **Conditional Concept Drift ($P_t(Y|X)$):** Tested separately (`abrupt_conditional_drift`); caught by Page-Hinkley on W3 where PSI was blind.
     - **Capture/Environment Shift (Period A → B):** Excluded from W1 and W3 (both operate strictly inside continuous Period B); never claimed as organic drift.
- **Recommended Action:** Evaluate E2 continual adaptation at intermediate rounds (`R3..R8`) so gradual/recurring trajectories diverge in adaptation metrics, and support two-sided/metric-drop sequential monitoring alongside upward loss Page-Hinkley.
