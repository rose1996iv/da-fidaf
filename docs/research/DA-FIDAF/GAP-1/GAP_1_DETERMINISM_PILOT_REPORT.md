# DA-FIDAF GAP-1 — Determinism Pilot Verification Report (`VER-3`, Gate 1)

**Document Status:** `COMPLETED — GATE 1 PILOT PASSED (AWAITING GATE 2 REVIEW)`  
**Date:** `2026-11-28`  
**Recommendation:** **`PASS`** *(Recommend proceeding to Gate 2 review; confirmatory `320`-run suite remains **NOT AUTHORIZED** until explicit separate Gate 2 approval)*  
**Governing Protocol:** [EXP_GAP_1_Protocol_v5_0.md](EXP_GAP_1_Protocol_v5_0.md) (`SHA-256: 0ee5dbd15e2116ab0294bcd7d5f8a715837a97aa99cd761e024645f6e7899ad2`)  
**Readiness Plan:** [GAP_1_DETERMINISM_PILOT_READINESS_AND_EXECUTION_PLAN.md](GAP_1_DETERMINISM_PILOT_READINESS_AND_EXECUTION_PLAN.md) (`SHA-256: cf88a1dc969f041681242194105eccbe54043719428ba202b45b233f80f51603`)  
**Confirmatory Exclusion Notice:** Both pilot runs (`run_A`, `run_B`) carry `"is_pilot_excluded_from_confirmatory": true`, are isolated under `stage_b4_exp_gap1_e2_mlp\pilot_determinism_check\`, and are **permanently excluded** from the `320`-run confirmatory suite and all statistical hypothesis tests.

---

## 1. Files Created / Modified Under Gate 1 Authorization

| File Path | Action | Verified SHA-256 | Scope / Isolation Check |
|---|---|---|---|
| `I:\Projects\da-fidaf-runs\phase4_phd_execution\compact_mlp_continual.py` | Created | `29f490f7126eb4f3aef71f8c29f8e2fae37d9a51ca2a45bdaf3c58cef34b916c` | Isolated shared `CompactMLP` continual-adaptation library (read-only imports from `common_phase4`, `stage_a2`, `stage_b2_b3`, `dafidaf.drift.core`) |
| `I:\Projects\da-fidaf-runs\phase4_phd_execution\stage_b4_exp_gap1_e2_mlp.py` | Created | `61bd307a05f477c7747a69102672a22f5855842dad86f696eba687f1e256291e` | Isolated Gate 1 pilot runner (`--mode {pilot}` ONLY; confirmatory execution hard-blocked) |
| `I:\Projects\da-fidaf\docs\research\DA-FIDAF\GAP-1\GAP_1_DETERMINISM_PILOT_REPORT.md` | Created | *(recorded in `README.md` after save)* | Inside authorized `docs/research/DA-FIDAF/GAP-1/` directory |
| `I:\Projects\da-fidaf\docs\research\DA-FIDAF\GAP-1\README.md` | Updated | *(verified post-save)* | Documentation index updated with pilot report entry |

Zero modifications were made to `I:\IoT\`, `I:\Projects\da-fidaf\src\`, `I:\Projects\da-fidaf\configs\`, tracked repository files, prior Phase 3B / Phase 4 outputs, or frozen evidence ledgers.

---

## 2. Exact Commands, Run Identifiers & Runtime Environment

### 2.1 Commands Executed (Exit Code `0` on All Commands)

```powershell
python -m py_compile "I:\Projects\da-fidaf-runs\phase4_phd_execution\compact_mlp_continual.py" "I:\Projects\da-fidaf-runs\phase4_phd_execution\stage_b4_exp_gap1_e2_mlp.py"
python "I:\Projects\da-fidaf-runs\phase4_phd_execution\stage_b4_exp_gap1_e2_mlp.py" --help
$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
python "I:\Projects\da-fidaf-runs\phase4_phd_execution\stage_b4_exp_gap1_e2_mlp.py" --mode pilot
```

- CLI scope verification (`--help`) confirmed `--mode {pilot}` is the sole accepted mode (zero additional seeds, schedules, arms, windows, or confirmatory runs launchable).

### 2.2 Run Identifiers & Wall Times

- **`pilot_run_A`:** `20261127T184936_871960Z_gap1_pilot_run_A_w1_abrupt_covariate_drift_gated_replay_seed42_dfd877`
  - `base_train_wall_seconds = 9.1274s`, `total_adaptation_wall_seconds = 4.2868s`
- **`pilot_run_B`:** `20261127T184952_155180Z_gap1_pilot_run_B_w1_abrupt_covariate_drift_gated_replay_seed42_606bb9`
  - `base_train_wall_seconds = 5.5188s`, `total_adaptation_wall_seconds = 3.8967s`
- **Confirmatory runs executed:** `0`

### 2.3 Verified Software & Hardware Environment (`independently verified`)

| Field | Verified Value |
|---|---|
| Platform / OS | `Windows-11-10.0.26300-SP0` (desktop workstation — not physical IoT hardware) |
| Python | `3.12.10` |
| PyTorch / CUDA | `2.6.0+cu124` on `NVIDIA GeForce GTX 1650` (`device = cuda`) |
| NumPy / SciPy / scikit-learn | `2.4.2` / `1.17.1` / `1.8.0` |
| Determinism Flags | `CUBLAS_WORKSPACE_CONFIG=":4096:8"`, `cudnn.benchmark=False`, `cudnn.deterministic=True`, `torch.use_deterministic_algorithms(True, warn_only=False)` |

---

## 3. Protocol, Source & Output SHA-256 Integrity Table (`independently verified`)

| Artifact | Path | Verified SHA-256 |
|---|---|---|
| Protocol `v5.0` | `docs/research/DA-FIDAF/GAP-1/EXP_GAP_1_Protocol_v5_0.md` | `0ee5dbd15e2116ab0294bcd7d5f8a715837a97aa99cd761e024645f6e7899ad2` |
| Stage A4-Fix Frozen Ledger | `phase4_phd_execution/stage_a4_evidence_freeze/Stage_A4_Fix_Evidence_Freeze_and_Claim_Ledger.md` | `47f28614879b019f075cdfcc4e586998ad59588f584af11b6e6073bd5f6a7335` |
| Unified Cross-Stage Ledger | `phase4_phd_execution/unified_cross_stage_freeze/DA_FIDAF_Unified_Cross_Stage_Evidence_and_Claim_Ledger.md` | `f51eddcea12928c6ab465bd12a21e9c22f99b59a55d3a36a9cda210c09810d4f` |
| `run_A/run_report.json` | `stage_b4_exp_gap1_e2_mlp/pilot_determinism_check/run_A/run_report.json` | `0e330fd5a4c29cb3a94e2d28ef233ba43f60588575855ae7e27c1512ef61633a` |
| `run_B/run_report.json` | `stage_b4_exp_gap1_e2_mlp/pilot_determinism_check/run_B/run_report.json` | `0a5762a3e02bdd73f650e32ab4d5414bd0a8ea7ca2a78b89ec76b7de19e92bf7` |
| `run_A` & `run_B` `model_theta_0.npy` | `pilot_determinism_check/run_{A,B}/model_theta_0.npy` | `7cab365a6d124653dbd9551059cced42876386bd936560de6c732ad47e19a348` **(identical)** |
| `run_A` & `run_B` `model_theta_10.npy` | `pilot_determinism_check/run_{A,B}/model_theta_10.npy` | `03c259a08029925f8231b1c5b8b0fa24d8876b31da12e8c620725e1d164ac214` **(identical)** |
| `run_A` & `run_B` `prior_audit_probs.npy` | `pilot_determinism_check/run_{A,B}/prior_audit_probs.npy` | `8245211e8ed3c9dfefc903a364f073b22676496889ec4d5894da4514b3fc05f0` **(identical)** |
| `run_A` & `run_B` `pre_adapt_probs.npz` | `pilot_determinism_check/run_{A,B}/pre_adapt_probs.npz` | `ae2e1bf94f0e9fcd3c66f13f8581ace55b630256907a30c6b521e2e3c96fe667` **(identical)** |
| `determinism_diff_report.json` | `stage_b4_exp_gap1_e2_mlp/pilot_determinism_check/determinism_diff_report.json` | `e84a0ac9f8560b171ac885020afdf739d2f1c6d4df2f7050540f759cf95bfdca` |
| `pilot_manifest.json` | `stage_b4_exp_gap1_e2_mlp/pilot_determinism_check/pilot_manifest.json` | `a0f2785389d233c7c0d2ef55e7130d978a8858d91746b4b7565772e34d42c3c0` *(sidecar verified)* |

All `4/4` `.sha256` sidecars (`run_A/run_report.json.sha256`, `run_B/run_report.json.sha256`, `determinism_diff_report.json.sha256`, `pilot_manifest.json.sha256`) passed independent raw-byte verification.

---

## 4. `run_A` vs. `run_B` Determinism Comparison & Criterion Pass/Fail (`independently verified`)

| Pilot Criterion (Readiness Plan §4.1) | Observed Diff (`run_A` vs. `run_B`) | Threshold | Result |
|---|---:|---:|---|
| Base model parameters $\theta_0$ (`3,073` `float64` values) | **`0.000e+00`** (bit-identical `.npy`) | `<= 1e-6` | **PASS** |
| Final model parameters $\theta_{10}$ (`3,073` `float64` values) | **`0.000e+00`** (bit-identical `.npy`) | `<= 1e-6` | **PASS** |
| Per-round prequential probability vectors $\hat{p}_{R1..R10}$ (all `10` rounds) | **`0.000e+00`** on every round `R1..R10` | `<= 1e-6` | **PASS** |
| Final `D_prior_audit` probability vector $\hat{p}_{\text{audit}}$ (`9,373` values) | **`0.000e+00`** (bit-identical `.npy`) | `<= 1e-6` | **PASS** |
| Normalized `run_report.json` numeric leaves (`0` violations) | **`0.000e+00`** (`0` violations) | `<= 1e-6` | **PASS** |
| Discrete control-flow & integrity fields (`adaptation_rounds=[4..10]`, `quorum_met`, per-client triggers/participation/PH resets, `total_federation_adapt_steps=560`, `total_adaptation_comm_bytes=1,720,880`, `split_integrity`) | **`0` mismatches** (`100%` identical) | Exact (`0`) | **PASS** |
| `X_test` isolation & raw-array immutability assertions | `x_test_used_for_psi_cal_or_adapt=False`, `source_arrays_immutable=True`, `psi_ref_labels_accessed=False` | Exact (`True`/`False`) | **PASS** |
| Strict PyTorch CUDA determinism (`warn_only=False`, `CUBLAS_WORKSPACE_CONFIG=:4096:8`) | Zero unsupported-op errors; exact `0.0` reproducibility on `GTX 1650` | Zero errors | **PASS** |

*Excluded non-deterministic JSON metadata keys (explicitly documented):* `run_id`, `pilot_slot` (`"run_A"` vs. `"run_B"`), `generated_utc`, `base_train_wall_seconds`, `adapt_wall_seconds`, `total_adaptation_wall_seconds`.

---

## 5. Non-Confirmatory Runtime & Behavioral Diagnostics (`run_A == run_B`, Single Seed `42`)

> **Evidence Status:** `independently verified` as single-seed pilot runtime diagnostics (`exploratory` / non-confirmatory; excluded from confirmatory inference).

### 5.1 Base Model $M_0$ & Untouched `X_test` Static Audit

- **Base $M_0$ (`10` FL rounds on `D_fl_train`, `K=10` pure `Dir(0.5)`, `tau_val_frozen = 0.95` calibrated strictly on `D_val_cal`):**
  - `D_val_cal` Macro-F1 = `0.994685`; `D_prior_audit` BCE = `0.158576`, Macro-F1 = `0.892530`.
  - Untouched `X_test` (`M_0`): `Macro-F1@tau_val = 0.983043`, `Macro-F1@0.50 = 0.965374`, `ROC-AUC = 0.992743`, `ECE = 0.027560`.
- **Final $M_{10}$ on Untouched `X_test` (static audit only):**
  - `Macro-F1@tau_val = 0.986195`, `Macro-F1@0.50 = 0.981826`, `ROC-AUC = 0.995520`, `ECE = 0.008772`.
- **Reservoirs (`seed=42`, `W1`):** All `10/10` clients had `N_k >= 1,072` (`10/10` `exact_proportional` at `cap = 500`, `0` single-class on `seed=42`, `0` empty/undersized).

### 5.2 Per-Round Prequential Trajectory (`ToN-IoT W1`, `abrupt_covariate`, `drift_gated_replay`, `seed=42`)

| Round | $I(t)$ | Mean Shift $\Delta\mu_t$ | `pre_adapt` F1 (`tau`/`0.50`) | `pre_adapt` AUC / BCE | Clients `PSI` / `PH` / `Any` | Quorum / Adapted | `post_adapt` F1 (diag) | Cumul. Prior Forgetting $\Delta\mathcal{L}$ | Prior Audit F1 |
|---:|---:|---:|---|---:|---|---|---:|---:|---:|
| `R1` | `0.00` | `-0.0134` | `0.9880` / `0.9555` | `1.0000` / `0.0356` | `1 / 0 / 1` | `No / No` | `0.9880` | `+0.000000` | `0.8925` |
| `R2` | `0.00` | `+0.0006` | `0.9941` / `0.9754` | `1.0000` / `0.0225` | `1 / 0 / 1` | `No / No` | `0.9941` | `+0.000000` | `0.8925` |
| `R3` | `0.00` | `+0.0213` | `0.9939` / `0.9814` | `1.0000` / `0.0216` | `0 / 0 / 0` | `No / No` | `0.9939` | `+0.000000` | `0.8925` |
| `R4` | `1.00` | `+1.4771` | **`0.0397`** / `0.0304` | `0.2608` / `1.9218` | **`10 / 10 / 10`** | **`Yes / Yes`** | `0.7934` | `+0.017224` | `0.8891` |
| `R5` | `1.00` | `+1.5199` | `0.7995` / `0.4855` | `0.6745` / `0.2338` | `10 / 0 / 10` | `Yes / Yes` | `0.9113` | `+0.011408` | `0.8841` |
| `R6` | `1.00` | `+1.5212` | `0.8866` / `0.6998` | `0.7298` / `0.1531` | `10 / 0 / 10` | `Yes / Yes` | `0.8409` | `+0.024972` | `0.8666` |
| `R7` | `1.00` | `+1.4856` | `0.8208` / `0.7272` | `0.7387` / `0.1787` | `10 / 0 / 10` | `Yes / Yes` | `0.8866` | `+0.039664` | `0.8211` |
| `R8` | `1.00` | `+1.5329` | **`0.9555`** / `0.8409` | `0.9386` / `0.0867` | `10 / 0 / 10` | `Yes / Yes` | `0.9191` | `+0.027284` | `0.8663` |
| `R9` | `1.00` | `+1.5306` | `0.8780` / `0.7884` | `0.8388` / `0.1378` | `10 / 0 / 10` | `Yes / Yes` | `0.9033` | `+0.038249` | `0.8264` |
| `R10` | `1.00` | `+1.4572` | `0.9191` / `0.7272` | `0.9765` / `0.1147` | `10 / 0 / 10` | `Yes / Yes` | `0.9268` | `+0.048752` | `0.8143` |

- **Key Runtime Findings (Single-Seed Diagnostic Only):**
  1. **Quorum & Live PH Pre-Onset Protection (`R1..R3`):** Isolated `1/10` client PSI noise on `R1` and `R2` was cleanly blocked by `q_min = 3` (`0/3` fleet false alarms), and live `PageHinkleyDetector` fired `0/30` pre-onset false alarms (`R3` actively armed at `min_samples = 3`).
  2. **Genuine Abrupt Drift Impact & Recovery:** `abrupt_covariate` (`s = 1.5`) dropped `pre_adapt` Macro-F1 from `0.9920` (`R1..R3` mean) to `0.0397` at `R4`, immediately triggered `10/10` PSI **and** `10/10` PH, and achieved primary prequential recovery (`>= 0.9424`) at `R8` (`0.9555`; `recovery_time_from_drop = 4` rounds; `mean_r5_r10_pre_adapt_macro_f1 = 0.876604`; `final_prior_audit_forgetting_delta = +0.048752`).
  3. **Compute & Communication Accounting:** `7` adapted rounds (`R4..R10`), `70` client adaptations, `560` federation gradient steps, `35,840` sample presentations, `1,720,880` bytes total (`12,292 B` × `20` up+down × `7` rounds).

---

## 6. Warnings, Minor Deviations & Limitations

1. **Zero errors or warnings** were emitted by Python, PyTorch (`warn_only=False`), CUDA, or any data/split assertion.
2. **Minor JSON exclusion key addition:** Added `"pilot_slot"` (`"run_A"` vs. `"run_B"`) to `EXCLUDED_JSON_KEYS` alongside the Readiness Plan's `"run_id"`, `"generated_utc"`, and `"*_wall_seconds"` keys, as it is strictly the slot identifier distinguishing the two pilot folders.
3. **Minor telemetry field naming polish (for Gate 2 confirmatory implementation):** In `compact_mlp_continual.py`, the summary keys `all_rounds_client_*_far` / `all_rounds_fleet_quorum_far` record overall trigger rates across `R1..R10` (which equal FAR only on `stable_control`, whereas on drifted schedules they include true post-onset triggers). Recommend renaming those keys to `all_rounds_*_trigger_rate` (while keeping `stable_control` FAR explicitly computed in the confirmatory aggregator) if Gate 2 is approved.
4. **Strict Limitations (What This Pilot Does NOT Verify):**
   - Single seed (`42`), single window (`W1`), single schedule (`abrupt_covariate`), single arm (`drift_gated_replay`) — provides **zero** confirmatory comparison against `static`, `fine_tune`, or `unconditional_replay`, and **zero** live `W3` or `stable_control` `R4..R10` `PH` FAR evidence (those will be measured only in the Gate 2 confirmatory run).
   - Desktop `GTX 1650` timing (`~13s` per full clean-slate run) does not represent physical IoT edge hardware.

---

## 7. Post-Execution Repository & Frozen-Ledger Isolation Check

*(Re-verified independently immediately after pilot completion — see final verification output.)*
- `I:\Projects\da-fidaf` remains on branch `main`, `HEAD = da1b5fc69f4d172dea72b6afc74a4257ba36f048`, `0` tracked files modified.
- Both frozen ledgers (`Stage_A4_Fix_Evidence_Freeze_and_Claim_Ledger.md` `47f28614...`, `DA_FIDAF_Unified_Cross_Stage_Evidence_and_Claim_Ledger.md` `f51eddce...`) and `EXP_GAP_1_Protocol_v5_0.md` (`0ee5dbd1...`) remain bit-identical.
- `stage_b4_exp_gap1_e2_mlp\runs\` does **not** exist (`0` confirmatory runs executed).

---

## 8. Final Recommendation

**`PASS`**

**Rationale:** Every Gate 1 Determinism Pilot criterion passed with **bit-for-bit `0.000e+00` agreement** across `theta_0`, `theta_10`, all `10` rounds of prequential probabilities, `D_prior_audit` probabilities, and normalized JSON reports, with `0` discrete control-flow mismatches, zero CUDA determinism warnings under `warn_only=False`, clean pre-onset quorum protection (`0/3` fleet FA; `0/30` live PH FA), and verified non-trivial abrupt-drift impact and recovery on `CompactMLP`.

**Next Step (Stopped — Awaiting Explicit Gate 2 Approval):** Do **not** launch the `320`-run confirmatory suite until the user reviews this report and explicitly authorizes **Gate 2** (adding the `--mode confirmatory` execution path and running `20` base FL models + `320` confirmatory trajectories + paired Student-$t$ / exact Wilcoxon / Holm-Bonferroni analysis).
