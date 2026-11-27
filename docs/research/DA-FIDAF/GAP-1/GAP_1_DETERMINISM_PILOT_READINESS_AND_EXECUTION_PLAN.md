# DA-FIDAF GAP-1 — Determinism Pilot Readiness Review & Proposed Execution Plan (Phase D)

**Document Status:** `PROPOSED PLAN — NOT AUTHORIZED TO EXECUTE`  
**Date:** `2026-11-28`  
**Governing Protocol:** [EXP_GAP_1_Protocol_v5_0.md](EXP_GAP_1_Protocol_v5_0.md) (`SHA-256: 0ee5dbd15e2116ab0294bcd7d5f8a715837a97aa99cd761e024645f6e7899ad2`)  
**Scope:** Complete execution-readiness checklist and proposed isolated implementation/pilot plan for the `2`-run excluded Determinism Pilot (`VER-3`). Neither code creation nor pilot execution is authorized by this document.

---

## 1. Readiness Checklist

| Readiness Area | Requirement | Current State | Evidence Status |
|---|---|---|---|
| Protocol completeness | All `D1`–`D6` and `RD-1`–`RD-5` locked with unambiguous operational formulas | **COMPLETE** in `EXP_GAP_1_Protocol_v5_0.md` | `independently verified` |
| Reservoir feasibility (`VER-1`) | `200/200` reservoirs `>= 32`, `0` empty, deterministic, disjoint, single-class reconciled | **PASSED** (`min |B_k| = 38` W1 / `36` W3; `8/200` single-class per `RD-3`) | `independently verified` |
| Stream & clean PSI FAR (`VER-2`) | `2,000/2,000` client-rounds pass guards; `X_test` untouched; clean fleet FAR `< 10%` | **PASSED** (`4.0%` W1, `0.0%` W3; `100/100` drifted recall; `10/10` ramp) | `independently verified` |
| Frozen artifact integrity | `HEAD = da1b5fc6...`, Stage A4-Fix & Unified ledgers unchanged | **PASSED** (SHA-256 verified `2026-11-28`) | `independently verified` |
| Implementation code | `compact_mlp_continual.py` and `stage_b4_exp_gap1_e2_mlp.py` | **NOT CREATED** (blocked pending explicit authorization) | `unverified` |
| Determinism Pilot (`VER-3`) | `2` identical repeated runs (`<= 1e-6` tensors/probs/metrics; exact control-flow) | **NOT EXECUTED** (blocked pending explicit authorization) | `unverified` |
| Confirmatory `320`-run suite | `2 windows × 4 schedules × 4 arms × 10 seeds` + Holm/Wilcoxon | **BLOCKED** (requires separate approval *after* Pilot review) | `unverified` |

---

## 2. Proposed Implementation Scope (Only Upon Explicit Authorization)

### 2.1 Files to Be Created (Strictly Isolated Outside Git `src/` and Frozen Directories)

| Planned File | Role | Touches Existing Code / Frozen Artifacts? |
|---|---|---|
| `I:\Projects\da-fidaf-runs\phase4_phd_execution\compact_mlp_continual.py` | Reusable `CompactMLP` continual-adaptation module (shared cleanly with planned `EXP-GAP-2`): `SeedSequence` stream/ref partitioner, `RD-2`/`RD-3` reservoir builder, `RD-1` shuffled-cycle CRN batch sampler, deterministic PyTorch step trainer (`AdamW`, seeded `Dropout(0.10)`), 5-phase client-local `PSI`/`PH` federated state machine (`q_min=3`), participating-only stream-weighted `FedAvg`, and `D_prior_audit` BCE forgetting evaluator. | **NO** (imports `common_phase4.py`, `stage_a2_nonlinear_and_personalization.py`, and `dafidaf.drift.core` strictly read-only). |
| `I:\Projects\da-fidaf-runs\phase4_phd_execution\stage_b4_exp_gap1_e2_mlp.py` | Dedicated runner with `--mode pilot` (runs ONLY the `2` excluded determinism-pilot runs and exits) and `--mode confirmatory` (refuses to run unless `--pilot-verified` manifest exists and target `runs/` is empty). | **NO** (fail-closed against non-empty target directory; zero writes to `I:\Projects\da-fidaf\src\`, `configs\`, `I:\IoT\`, or frozen ledgers). |
| `I:\Projects\da-fidaf\docs\research\DA-FIDAF\GAP-1\GAP_1_DETERMINISM_PILOT_REPORT.md` | Post-pilot verification report saved inside `docs/` per Master Documentation Rule (created only after pilot completes). | **NO** (updates `docs/research/DA-FIDAF/GAP-1/README.md` only). |

*Portability Note (`AUD-06`):* Both new `.py` scripts live in `I:\Projects\da-fidaf-runs\phase4_phd_execution\` (matching Stages `A1`–`B3`), keeping `I:\Projects\da-fidaf\src\` untouched; internal path defaults will use `pathlib.Path(__file__).resolve().parent` with env overrides so they remain portable if ever migrated into `src/`.

---

## 3. Exact Determinism Pilot Configuration & Runs (`--mode pilot`)

- **Runs Executed:** Exactly **`2`** independent, sequential, identical repeated executions (`pilot_run_A`, `pilot_run_B`) initialized from scratch (fresh model weights, fresh `SeedSequence`/`torch.Generator` state, fresh data split & stream materialization).
- **Exact Configuration:**
  - Dataset Window: **`ToN-IoT W1`** (`embargo_seconds = 300.0`, `d = 11`, `CompactMLP` `3,073` params / `12,292 B` FP32).
  - Schedule: **`abrupt_covariate`** (`T = 10`, `onset_round = 4`, `severity = 1.5`, `is_synthetic = True`).
  - Adaptation Arm: **`drift_gated_replay`** (`N_adapt_steps = 8`, `batch_size = 64` [`32` curr + `32` rep], `AdamW(lr=2e-3, wd=1e-4)`, `cap = 500`, `q_min = 3`, `p_min = 0.06`, `n_bins = 5`, `psi_threshold = 0.25`, `PH(delta=0.005, threshold=0.10, min_samples=3)`).
  - Seed: **`42`**.
  - Runtime Environment Flags: `CUBLAS_WORKSPACE_CONFIG=:4096:8`, `torch.backends.cudnn.benchmark = False`, `torch.backends.cudnn.deterministic = True`, `torch.use_deterministic_algorithms(True, warn_only=False)` (explicit per-step `torch.manual_seed` / `torch.cuda.manual_seed_all` to lock `Dropout(0.10)`).
  - Estimated Wall Time: `~10–25s` total on `NVIDIA GeForce GTX 1650` (including one-time `W1` load).
- **Exclusion Rule:** Both pilot outputs carry `"is_pilot_excluded_from_confirmatory": true`, are written strictly under `stage_b4_exp_gap1_e2_mlp\pilot_determinism_check\run_A\` and `run_B\`, and are **permanently excluded** from the `320`-run confirmatory count and all statistical tests.

---

## 4. Deterministic Comparison Criteria, Required Metrics & Failure Conditions

### 4.1 Exact Comparison Criteria (`pilot_run_A` vs. `pilot_run_B`)

| Compared Output | Tolerance | Pass Condition |
|---|---|---|
| Base & final global parameter vectors ($\theta_0, \theta_{10}$, `float64`) | `<= 1e-6` | `max_abs_diff <= 1e-6` |
| Prequential probability vectors ($\hat{p}_{1..10}$ on $S_{1..10}$) & $\hat{p}_{\text{audit}}$ on `D_prior_audit` | `<= 1e-6` | `max_abs_diff <= 1e-6` |
| All numeric metrics & detector values (`pre_adapt_primary`, `forgetting`, `local_psi_max`, `local_pre_bce`, `local_ph_stat`, `update_l2_norm`, `trajectory_summary`) | `<= 1e-6` | `max_abs_diff <= 1e-6` |
| Discrete control-flow & integrity fields (`adaptation_rounds`, `quorum_met`, per-client triggers/participation/PH resets, `total_federation_adapt_steps`, `total_adaptation_comm_bytes`, split hashes) | **`0` (exact)** | `100%` identical |
| Normalized `run_report.json` diff (excluding only `run_id`, `generated_utc`, `*_wall_seconds`) | `<= 1e-6` / exact | Zero numeric violations, zero discrete mismatches |

### 4.2 Required Pilot Diagnostic Metrics (Logged, Non-Confirmatory)
- Base $M_0$ performance on `D_val_cal`, `D_prior_audit`, and untouched `X_test` (`macro_f1_tau_val`, `macro_f1_fixed050`, `roc_auc`, `ece`, `brier`).
- Per-round `R1..R10` `pre_adapt_primary` metrics, `final_prior_audit_forgetting_delta`, `recovery_pre_adapt_primary`, separate client/fleet `PSI` and `PH` trigger histories (giving first empirical read on live `PH` behavior on `R1..R3` pre-onset!), and exact `total_federation_adapt_steps` / `comm_bytes`.
- `X_test` untouched verification assertion (`x_test_used_for_psi_cal_or_adapt == False`).

### 4.3 Hard Fail-Closed Abort Conditions
Abort immediately (exit non-zero, launch `0` confirmatory runs, report root cause) if **any** occurs:
1. Any `NaN`/`Inf` in weights, gradients, logits, or BCE loss.
2. Any split-overlap, reservoir-size (`< 32`), stream-guard (`n < 30` or missing class), or `X_test` contamination assertion failure.
3. Any discrete control-flow mismatch OR `max_abs_diff > 1e-6` between `run_A` and `run_B`.
4. `torch.use_deterministic_algorithms(True, warn_only=False)` raises an unsupported-op error on CUDA (triggers explicit investigation & decision: switch pilot/confirmatory to deterministic CPU or investigate specific op before re-running).

---

## 5. Expected Outputs, Rollback & Isolation Plan

- **Expected Pilot Outputs (under `I:\Projects\da-fidaf-runs\phase4_phd_execution\stage_b4_exp_gap1_e2_mlp\pilot_determinism_check\`):**
  - `run_A\run_report.json` + `.sha256`, `run_A\model_theta_0.npy`, `run_A\model_theta_10.npy`
  - `run_B\run_report.json` + `.sha256`, `run_B\model_theta_0.npy`, `run_B\model_theta_10.npy`
  - `determinism_diff_report.json` + `.sha256`
  - `pilot_manifest.json` + `.sha256` (exact SHA-256s of `compact_mlp_continual.py`, `stage_b4_exp_gap1_e2_mlp.py`, `EXP_GAP_1_Protocol_v5_0.md`, frozen ledgers, and `HEAD`).
- **Expected Documentation Output:** `I:\Projects\da-fidaf\docs\research\DA-FIDAF\GAP-1\GAP_1_DETERMINISM_PILOT_REPORT.md` + updated `README.md`.
- **Rollback / Isolation Plan:** Because zero existing files, frozen ledgers, datasets, or `src/` files are modified, full rollback of a failed or aborted pilot requires only removing the newly created isolated `pilot_determinism_check\` folder (or preserving it as an archived failure trace alongside a new timestamped attempt) and reverting/revising the isolated `compact_mlp_continual.py` / `stage_b4_exp_gap1_e2_mlp.py` scripts. Existing Stages `A1`–`B3`, `A4-Fix`, and `I:\Projects\da-fidaf\src\` remain `100%` unaffected.

---

## 6. Risks & Remaining Unverified Runtime Questions

| Risk / Question | Current Status | Mitigation in Pilot / Confirmatory Plan |
|---|---|---|
| **R1: CUDA determinism on `GTX 1650`** (`LayerNorm`, `GELU`, `Dropout`, `AdamW`) | `unverified` | Tested first in `VER-3` with `warn_only=False` + `CUBLAS_WORKSPACE_CONFIG=:4096:8`; deterministic CPU fallback option documented if CUDA op fails `<= 1e-6`. |
| **R2: Live Page-Hinkley (`PH`) FAR on `stable_control`** | `unverified` | `VER-2` verified PSI FAR only; pilot logs live `PH` loss trajectory on `R1..R3`, and confirmatory `stable_control` monitors combined `PSI or PH` fleet FAR against the `< 10%` abort gate. |
| **R3: `CompactMLP` `static` drop magnitude on `abrupt_covariate` (`s=1.5`)** | `unverified` | Pilot verifies whether `M_0` actually drops below `0.95 * pre_drift` at `R4` before committing to `320` confirmatory runs (no silent severity tuning if `no_drop` occurs). |
| **R4: Small benign count per round in `X_val` (`~45` W1 / `~37` W3)** | `independently verified` (trade-off accepted via `RD-4`) | Mitigated by `n = 10` seeds (`370–450` benign evaluations/round across seeds) and exact Wilcoxon companion tests. |

---

## 7. Explicit Two-Stage User Approval Gate

Execution remains **STOPPED** until explicit user authorization is granted in two strictly separated gates:

1. **Gate 1 — Determinism Pilot Authorization (Next Step Requested):**
   User explicitly authorizes: (a) creating isolated `compact_mlp_continual.py` and `stage_b4_exp_gap1_e2_mlp.py` under `I:\Projects\da-fidaf-runs\phase4_phd_execution\`, and (b) running **ONLY** `--mode pilot` (`2` excluded runs of `(W1, abrupt_covariate, drift_gated_replay, seed=42)`), then stopping and reporting `GAP_1_DETERMINISM_PILOT_REPORT.md` in `docs/research/DA-FIDAF/GAP-1/`.
2. **Gate 2 — Confirmatory Suite Authorization (Locked Until Gate 1 Passes Review):**
   Only **after** the user reviews and approves `GAP_1_DETERMINISM_PILOT_REPORT.md` may `--mode confirmatory` (`20` base FL models + `320` confirmatory trajectory runs) be authorized.
