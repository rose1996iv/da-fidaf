# DA-FIDAF GAP-1 — Independent Post-Pilot Audit Report (Read-Only)

**Audit Status:** **`AUDIT PASSED — PILOT CONCLUSION INDEPENDENTLY SUPPORTED; GATE 2 READY FOR USER REVIEW`**  
**Date:** `2026-11-28`  
**Audit Mode:** **Strict Read-Only Audit.** **No experiment, pilot, training run, or rerun was executed during this audit.** Zero implementation code, configuration files, datasets, pilot outputs, tracked Git files, or frozen evidence ledgers were modified.  
**Authorization Boundary:** This audit verifies Gate 1 only. **Gate 2 (`320`-run confirmatory suite) is NOT authorized** and remains blocked pending explicit separate user approval.

---

## 1. Inspected Artifacts & Independently Verified SHA-256 Hashes

All hashes below were independently computed directly from live on-disk files on `2026-11-28` (zero hashes copied from reports without recomputation):

| Artifact | Path | Bytes | Independently Verified SHA-256 | Cross-Check vs. Manifest / Sidecars |
|---|---|---:|---|---|
| GAP-1 Protocol `v5.0` | `docs/research/DA-FIDAF/GAP-1/EXP_GAP_1_Protocol_v5_0.md` | `29,619` | `0ee5dbd15e2116ab0294bcd7d5f8a715837a97aa99cd761e024645f6e7899ad2` | Exact match |
| Pilot Readiness Plan | `docs/research/DA-FIDAF/GAP-1/GAP_1_DETERMINISM_PILOT_READINESS_AND_EXECUTION_PLAN.md` | `11,343` | `cf88a1dc969f041681242194105eccbe54043719428ba202b45b233f80f51603` | Exact match |
| Gate 1 Pilot Report | `docs/research/DA-FIDAF/GAP-1/GAP_1_DETERMINISM_PILOT_REPORT.md` | `15,109` | `cbd335405b91ad62821b8a443c66d53e2335891e854d77a975300523573c4ce9` | Exact match |
| GAP-1 Index (pre-update) | `docs/research/DA-FIDAF/GAP-1/README.md` | `6,093` | `62a9685925ba2a8d044345799d771e968d904d3d23ffb6f1a0a053b2d835cc6d` | Verified prior to audit update |
| Continual Library | `phase4_phd_execution/compact_mlp_continual.py` | `48,477` | `29f490f7126eb4f3aef71f8c29f8e2fae37d9a51ca2a45bdaf3c58cef34b916c` | Matches `pilot_manifest.json` |
| Gate 1 Pilot Runner | `phase4_phd_execution/stage_b4_exp_gap1_e2_mlp.py` | `18,635` | `61bd307a05f477c7747a69102672a22f5855842dad86f696eba687f1e256291e` | Matches `pilot_manifest.json` |
| Frozen Stage A4-Fix Ledger | `phase4_phd_execution/stage_a4_evidence_freeze/Stage_A4_Fix_Evidence_Freeze_and_Claim_Ledger.md` | `45,530` | `47f28614879b019f075cdfcc4e586998ad59588f584af11b6e6073bd5f6a7335` | Unchanged (immutable) |
| Frozen Unified Ledger | `phase4_phd_execution/unified_cross_stage_freeze/DA_FIDAF_Unified_Cross_Stage_Evidence_and_Claim_Ledger.md` | `65,619` | `f51eddcea12928c6ab465bd12a21e9c22f99b59a55d3a36a9cda210c09810d4f` | Unchanged (immutable) |
| Diff Report | `stage_b4_exp_gap1_e2_mlp/pilot_determinism_check/determinism_diff_report.json` | `1,786` | `e84a0ac9f8560b171ac885020afdf739d2f1c6d4df2f7050540f759cf95bfdca` | Sidecar + manifest match |
| Pilot Manifest | `stage_b4_exp_gap1_e2_mlp/pilot_determinism_check/pilot_manifest.json` | `2,487` | `a0f2785389d233c7c0d2ef55e7130d978a8858d91746b4b7565772e34d42c3c0` | Sidecar match |
| `run_A/run_report.json` | `pilot_determinism_check/run_A/run_report.json` | `107,304` | `0e330fd5a4c29cb3a94e2d28ef233ba43f60588575855ae7e27c1512ef61633a` | Sidecar + manifest match |
| `run_B/run_report.json` | `pilot_determinism_check/run_B/run_report.json` | `107,303` | `0a5762a3e02bdd73f650e32ab4d5414bd0a8ea7ca2a78b89ec76b7de19e92bf7` | Sidecar + manifest match |
| `run_A` & `run_B` `model_theta_0.npy` | `pilot_determinism_check/run_{A,B}/model_theta_0.npy` | `24,712` | `7cab365a6d124653dbd9551059cced42876386bd936560de6c732ad47e19a348` | Byte-identical across `A`/`B` |
| `run_A` & `run_B` `model_theta_10.npy` | `pilot_determinism_check/run_{A,B}/model_theta_10.npy` | `24,712` | `03c259a08029925f8231b1c5b8b0fa24d8876b31da12e8c620725e1d164ac214` | Byte-identical across `A`/`B` |
| `run_A` & `run_B` `prior_audit_probs.npy` | `pilot_determinism_check/run_{A,B}/prior_audit_probs.npy` | `75,120` | `8245211e8ed3c9dfefc903a364f073b22676496889ec4d5894da4514b3fc05f0` | Byte-identical across `A`/`B` |
| `run_A` & `run_B` `pre_adapt_probs.npz` | `pilot_determinism_check/run_{A,B}/pre_adapt_probs.npz` | `66,240` | `ae2e1bf94f0e9fcd3c66f13f8581ace55b630256907a30c6b521e2e3c96fe667` | Byte-identical across `A`/`B` |

All `4/4` `.sha256` sidecars and all `16/16` hashes recorded in `pilot_manifest.json` matched live disk files `100%`.

---

## 2. Independent Checks Performed & Raw Recomputation Results

1. **Scope & Non-Expansion Audit (`independently verified`):**
   - `stage_b4_exp_gap1_e2_mlp` contains solely `['pilot_determinism_check']`; `stage_b4_exp_gap1_e2_mlp\runs\` does **not** exist (`0` confirmatory runs launched).
   - `pilot_determinism_check` contains solely `run_A`, `run_B`, `determinism_diff_report.json` (+ `.sha256`), and `pilot_manifest.json` (+ `.sha256`).
   - Both `run_A/run_report.json` and `run_B/run_report.json` confirm exact locked configuration (`window_id = "W1"`, `schedule_arm = "abrupt_covariate"`, `adaptation_arm = "drift_gated_replay"`, `seed = 42`, `is_pilot_excluded_from_confirmatory = True`, `dp_enabled = False`, `secure_aggregation_active = False`, `byzantine_clients = 0`, `x_test_used_for_psi_cal_or_adapt = False`, `psi_ref_labels_accessed = False`).
   - Static inspection of `stage_b4_exp_gap1_e2_mlp.py` confirms CLI `choices=("pilot",)` hard-blocks confirmatory execution, and `compact_mlp_continual.py` enforces `torch.use_deterministic_algorithms(True, warn_only=False)`.
2. **Independent Raw Tensor & Probability Recomputation (`independently verified`):**
   - `model_theta_0.npy`: shape `(3073,)`, `float64`, all finite, `max_abs_diff = 0.000e+00`, `bytes_eq = True`.
   - `model_theta_10.npy`: shape `(3073,)`, `float64`, all finite, `max_abs_diff = 0.000e+00`, `bytes_eq = True`, non-trivial update magnitude $\|\theta_{10} - \theta_0\|_2 = 0.961542$ (confirms adaptation genuinely updated weights).
   - `prior_audit_probs.npy`: shape `(9374,)`, `float64`, finite, bounded in `[0, 1]`, `max_abs_diff = 0.000e+00`, `bytes_eq = True`.
   - `pre_adapt_probs.npz`: exact keys `R1..R10`, `7,982` total rows (`R1=799, R2=799, R3..R10=798`), `float64`, finite, bounded in `[0, 1]`, `max_abs_diff = 0.000e+00` on every round, `all_bytes_eq = True`.
3. **Independent Recursive JSON Diff Across All `816` Numeric Leaves (`independently verified`):**
   - Using Readiness Plan's original `5` excluded keys (`run_id`, `generated_utc`, `base_train_wall_seconds`, `adapt_wall_seconds`, `total_adaptation_wall_seconds`): `max_num_diff = 0.000e+00`, sole discrete diff = `[('pilot_slot', 'run_A', 'run_B')]`.
   - Adding `"pilot_slot"` (`6` excluded keys): `max_num_diff = 0.000e+00`, `discrete_diffs = []` (`0` mismatches).
4. **Split-Sum & Disjointness Arithmetic (`independently verified`):**
   - `d_fl_train_n (53,114) + d_prior_audit_n (9,374) = 62,488` (exact `W1 Train`).
   - `d_val_cal_n (2,660) + d_val_psi_ref_n (2,661) + stream_total_n (7,982) = 13,303` (exact `W1 Val`).
   - `x_test_n = 13,253` (exact `W1 Test`, `x_test_used_for_psi_cal_or_adapt = False`).
5. **Report Framing, Repository & Documentation Audit (`independently verified`):**
   - `GAP_1_DETERMINISM_PILOT_REPORT.md` explicitly labels single-seed runtime diagnostics as `non-confirmatory` / `exploratory`, separates determinism verification from model-performance evidence, enumerates what the pilot does NOT verify (§6), and confirms Gate 2 is `NOT AUTHORIZED`.
   - `I:\Projects\da-fidaf` is on `main`, `HEAD = da1b5fc69f4d172dea72b6afc74a4257ba36f048`, `0` modified tracked files; all GAP-1 Markdown files live under `docs/research/DA-FIDAF/GAP-1/`; `12/12` relative links verified (`0` broken).

---

## 3. Criterion-by-Criterion Audit Assessment

| # | Audit Criterion | Assessment | Independent Evidence Basis |
|---|---|---|---|
| 1 | Pilot stayed strictly within authorized Gate 1 scope (`W1`, `abrupt_covariate`, `drift_gated_replay`, `seed=42`, `run_A`/`run_B` only) | **PASS** | Verified via directory tree, both `run_report.json` configs, `pilot_manifest.json`, and CLI `choices=("pilot",)`. |
| 2 | Parameter determinism ($\theta_0, \theta_{10} \le 10^{-6}$) | **PASS** | Recomputed directly from `.npy`: `0.000e+00` (`bytes_eq=True`, $\|\theta_{10}-\theta_0\|_2=0.961542$). |
| 3 | Prediction probability determinism ($\hat{p}_{R1..R10}, \hat{p}_{\text{audit}} \le 10^{-6}$) | **PASS** | Recomputed directly from `.npz`/`.npy`: `0.000e+00` across `7,982 + 9,374` values (`bytes_eq=True`). |
| 4 | JSON numeric (`<= 1e-6`) & discrete control-flow (`0` mismatches) determinism | **PASS** | Independent recursive diff over `816` float leaves = `0.000e+00`; `0` discrete diffs (excluding slot/time/ID keys). |
| 5 | Single-seed diagnostics clearly labeled non-confirmatory & separated from determinism evidence | **PASS** | Verified in `GAP_1_DETERMINISM_PILOT_REPORT.md` header, §5 banner, and §6 limitations. |
| 6 | Zero confirmatory runs launched | **PASS** | `stage_b4_exp_gap1_e2_mlp\runs\` does not exist; `confirmatory_runs_executed = 0`. |
| 7 | Repository isolation & frozen-ledger integrity preserved | **PASS** | `HEAD = da1b5fc6...`, `0` tracked diffs, both frozen ledgers and v5.0 hashes unchanged. |
| 8 | Docs location (`docs/research/DA-FIDAF/GAP-1/`), `README.md` currency, and valid links | **PASS** | All GAP-1 `.md` files reside inside authorized dir; `12/12` links verified (`0` broken). |
| 9 | Raw-artifact SHA-256 & sidecar integrity | **PASS** | `4/4` `.sha256` sidecars and `16/16` manifest hashes independently matched live disk. |

---

## 4. Minor Discrepancies, Limitations & Missing Evidence (Non-Blocking)

1. **DISCREPANCY-1 (1-Row `ceil` vs. `floor` Text Count in v5.0 & Pilot Report — Non-Blocking):**
   - `EXP_GAP_1_Protocol_v5_0.md` (§4.2 L90, §6.1 L175) and `GAP_1_DETERMINISM_PILOT_REPORT.md` (§4 row 4) state `D_fl_train = 53,115` / `D_prior_audit = 9,373` (`floor(0.15 * 62,488)`), whereas scikit-learn's `StratifiedShuffleSplit(test_size=0.15)` computes `ceil(0.15 * 62,488) = 9,374`, yielding actual verified sizes **`D_fl_train = 53,114` and `D_prior_audit = 9,374`** (`53,114 + 9,374 = 62,488`, verified in `prior_audit_probs.npy` shape `(9374,)`). Zero impact on disjointness or determinism; Gate 2 reports should cite actual `53,114 / 9,374` (and verify exact `W3` `StratifiedShuffleSplit(0.15)` `ceil` count at runtime).
2. **DISCREPANCY-2 (`SeedSequence` Tag `404` Traceability — Non-Blocking):**
   - `compact_mlp_continual.py` uses `SeedSequence([seed, win_id, sched_id, 0, 404, round_id, client_k, s])` to seed PyTorch/CUDA `Dropout(0.10)` deterministically per adaptation step (implementing `OBS-B5` and Readiness Plan §3 L46). Tag `404` is not explicitly listed in v5.0 §5.1 text (which lists `401/402/403`); documented here for full code-to-protocol traceability.
3. **NOTE-3 (`pilot_slot` Excluded Key & `all_rounds_*_far` Key Naming — Non-Blocking):**
   - Both were already transparently disclosed in `GAP_1_DETERMINISM_PILOT_REPORT.md` §4 & §6; independent diff confirmed `pilot_slot` was the sole extra discrete field differing between `run_A` and `run_B`. Renaming `all_rounds_*_far` to `all_rounds_*_trigger_rate` is recommended if Gate 2 implementation is authorized (preserving Gate 1 pilot files untouched).
4. **Limitations / Evidence Still Missing Until Gate 2:**
   - Determinism is independently verified on `W1`, `abrupt_covariate`, `drift_gated_replay`, `seed=42` only. Live `W3` trajectories, live `stable_control` `R4..R10` Page-Hinkley FAR across `10` seeds, and all confirmatory arm comparisons (`static` vs. `fine_tune` vs. `unconditional_replay` vs. `drift_gated_replay`) remain **unverified** until Gate 2 is authorized and completed.

---

## 5. Independent Audit Conclusion & Gate 2 Readiness

- **Is the Gate 1 Pilot `PASS` conclusion independently supported?** **YES.** Every determinism, scope, isolation, and integrity criterion was independently reproduced from raw `.npy`, `.npz`, `.json`, `.sha256`, and Git state with `0.000e+00` numeric diff and `0` control-flow mismatches.
- **Is Gate 2 ready for user review?** **YES** (subject to acknowledging minor documentation notes `DISCREPANCY-1`–`NOTE-3`).
- **Remaining Approval Gates (Execution Stopped):**
  1. **Gate 2 Authorization (Required Before Any Code Change or Run):** Explicit user approval to extend `stage_b4_exp_gap1_e2_mlp.py` with `--mode confirmatory` (applying the optional `all_rounds_*_trigger_rate` key-name polish if desired, keeping `pilot_determinism_check/` untouched) and execute the `320`-run confirmatory suite (`20` base FL models + `320` trajectories + paired Student-$t$ / exact Wilcoxon / Holm-Bonferroni `F1`/`F2`/`F3` + `GAP_1_FINAL_EXPERIMENT_REPORT.md`).
  2. **Separate Post-Confirmatory Audit & Ledger Integration Gate:** Independent audit of the `320` confirmatory outputs before updating any cross-stage evidence ledger or proceeding to `EXP-GAP-2` / `EXP-GAP-3`.
