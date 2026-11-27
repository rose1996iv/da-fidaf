# DA-FIDAF `EXP-GAP-1` Protocol — v5.0 (`CompactMLP` Drift & Continual Adaptation: `E2` + `C3`)

**Document Version:** `v5.0` (supersedes draft revisions `v1.0`–`v4.0`)  
**Date:** `2026-11-27`  
**Status:** `READY FOR DETERMINISM PILOT REVIEW` *(Not approved for execution; implementation, determinism pilot, and confirmatory runs remain blocked pending explicit user authorization)*  
**Governance Boundary:** Strictly isolated protocol documentation under `I:\Projects\da-fidaf-runs\phase4_phd_execution\exp_gap1_protocol\`. Zero code, configuration files, datasets (`I:\IoT`), Git repository files (`I:\Projects\da-fidaf`), experiment outputs, or frozen evidence ledgers were modified.

---

## 1. Authoritative User Decisions Locked (`RD-1` – `RD-5`)

| Decision ID | Topic | Locked Authoritative Specification | Rationale & Operational Impact |
|---|---|---|---|
| **`RD-1`** | Local Adaptation Batch Sampling & CRN | **Shuffled-cycle sampling** (`Option 1A`), `drop_last = False`, exact `N_adapt_steps = 8`, exact `batch_size = 64` (`512` sample presentations per adapted client-round); **Common Random Numbers (CRN)** (`ARM_TAG = 0`) for current-stream draw order across comparable arms (`fine_tune`, `drift_gated_replay`, `unconditional_replay`); separate deterministic `SeedSequence` stream (`tag = 402`) for replay samples. | Eliminates with-replacement variance asymmetry when `47 <= |S_{t,k}| < 64` on `W1` (`fine_tune` batch = `64` vs. `replay` current half = `32`), guarantees balanced coverage of all local samples across `8` steps, and reduces paired variance between `fine_tune` and `drift_gated_replay`. |
| **`RD-2`** | Replay-Reservoir Allocation (`B_k`) | **Client-proportional stratified allocation** from `D_fl_train[k]`, **maximum cap `500`** (retaining all `N_k` samples if `N_k <= 500`), deterministic seeded without-replacement sampling (`SeedSequence` `tag = 301`), membership **frozen** across all `10` rounds and both replay arms, **zero silent oversampling**, explicit shortfall logging (`below_or_eq_cap_all_kept`, `min1_benign_floor_applied`, `single_class_*`). | Preserves each gateway's true local training prior $P_k(Y)$ without distorting calibration or manufacturing synthetic duplicates; `VER-1` verified `200/200` reservoirs have `|B_k| >= 36 >= 32`. |
| **`RD-3`** | Single-Class / Incomplete-Class Reservoirs | A client reservoir `B_k` may contain **only the class(es) actually present** in `D_fl_train[k]`. **Never oversample** to manufacture missing classes; **never silently exclude clients** or alter pure `Dir(0.5)` base partitioning; explicitly record class coverage (`N_{k,0}, N_{k,1}, m_{k,0}, m_{k,1}, is_single_class_reservoir`) and any feasibility failure. | Reconciles pure `Dir(0.5)` base FL heterogeneity with replay memory: `VER-1` verified `3/100` single-class reservoirs on `W1` and `5/100` on `W3`, all with `|B_k| >= 74 >= 32` (`0` conflicts with the `|B_k| >= 32` size guard). |
| **`RD-4`** | Validation Partition & `X_test` Isolation | Partition `X_val` into 3 strictly disjoint stratified sets: **`D_val_cal` (`20%`)**, **`D_val_psi_ref` (`20%`, features `X` only)**, and **stream pool (`60%`)** split into `10` disjoint blocks `S_1..S_10`. **`X_test` stays `100%` untouched** for PSI, calibration, adaptation, and protocol selection (reserved solely for uncontaminated static `M_0`/`M_10` audit). Keep `W1` and `W3` strictly separate (`W1 ⊂ W3`, never pooled). | Eliminates all test-feature contamination (`U1`) while resolving `W3`'s verified natural `Val -> Test` shift (`max_psi = 6.01`). `VER-2` verified `100%` determinism and pairwise disjointness across all `10` seeds on both windows. |
| **`RD-5`** | Stream Floor, Quorum & `n_bins` | Lock **`p_min = 0.06`** simplex floor (`p_eff = 0.40 * p_raw + 0.06`), **`q_min = 3`** of `K = 10` (`>= 30%` fleet quorum), and preserve v4.0 **`n_bins = 5`** (`psi_threshold = 0.25`, `eps = 1e-6`). | Verified read-only in `VER-2` under exact v4.0/v5.0 `SeedSequence` streams: `0` empty clients, `0` guard failures (`min_n = 47` W1 / `121` W3; `min_benign = 2`), clean fleet PSI FAR **`4.0%` (`4/100`) on `W1`** and **`0.0%` (`0/100`) on `W3`**, and **`100/100`** client detection at `gradual@0.25` and `abrupt@1.0`. |

---

## 2. Scope, Verified Asset Anchors & Planned Isolation

### 2.1 Existing Read-Only Source & Evidence Anchors Inspected

| Asset | Exact Local Path | Verification Basis |
|---|---|---|
| Production repo `HEAD` | `I:\Projects\da-fidaf` | Verified via `git rev-parse HEAD` = `da1b5fc69f4d172dea72b6afc74a4257ba36f048`; zero tracked modifications (`??` only on two pre-existing untracked docs under `docs/repository/`). |
| Drift core (`FeatureDriftDetector`, `PageHinkleyDetector`, `DriftSpec`) | `I:\Projects\da-fidaf\src\dafidaf\drift\core.py` (L14–L207) | Inspected directly; `FeatureDriftDetector(psi_threshold=0.25, n_bins=5)` executed in `VER-2`. |
| Phase 3B chronological loader (`load_strided_window`) | `I:\Projects\da-fidaf-runs\scripts\phase3b\common_phase3b.py` (L76–L224) | Inspected directly; invoked via `load_ton_iot_window` in `VER-1`/`VER-2`. |
| Phase 4 shared library (`load_ton_iot_window`, `CompactMLP`, `partition_clients_np`, `aggregate_np`, `paired_student_t`, `apply_holm_bonferroni`) | `I:\Projects\da-fidaf-runs\phase4_phd_execution\common_phase4.py` | Inspected directly; `load_ton_iot_window` and `partition_clients_np` executed in `VER-1`/`VER-2`. |
| Stage A2 trainer (`train_torch_local`, `pos_weight` fallback) | `I:\Projects\da-fidaf-runs\phase4_phd_execution\stage_a2_nonlinear_and_personalization.py` (L62–L110, L258–L264) | Inspected directly; confirms single-class `pos_weight = 1.0` fallback. |
| Stage B2/B3 BCE helper (`eval_bce_np`) | `I:\Projects\da-fidaf-runs\phase4_phd_execution\stage_b2_b3_adaptive_byzantine_and_v3_attribution.py` (L182–L184) | Inspected directly; defines `[1e-6, 1-1e-6]` clipped unweighted BCE. |
| Frozen Stage A4-Fix Ledger (immutable) | `I:\Projects\da-fidaf-runs\phase4_phd_execution\stage_a4_evidence_freeze\Stage_A4_Fix_Evidence_Freeze_and_Claim_Ledger.md` | SHA-256 verified unchanged: `47f28614879b019f075cdfcc4e586998ad59588f584af11b6e6073bd5f6a7335`. |
| Frozen Unified Cross-Stage Ledger (immutable) | `I:\Projects\da-fidaf-runs\phase4_phd_execution\unified_cross_stage_freeze\DA_FIDAF_Unified_Cross_Stage_Evidence_and_Claim_Ledger.md` | Inspected (D0–D5, `U-D0-01`–`U-D0-04`, `U-A1-03`); SHA-256 verified unchanged: `f51eddcea12928c6ab465bd12a21e9c22f99b59a55d3a36a9cda210c09810d4f`. |

### 2.2 Planned New Isolated Files (Not Yet Created — Blocked Pending Approval)

- Shared continual-adaptation helper (reused by `EXP-GAP-2`): `I:\Projects\da-fidaf-runs\phase4_phd_execution\compact_mlp_continual.py`
- Dedicated `EXP-GAP-1` runner: `I:\Projects\da-fidaf-runs\phase4_phd_execution\stage_b4_exp_gap1_e2_mlp.py`
- Isolated output directory (does not yet exist; fail-closed non-overwrite guard): `I:\Projects\da-fidaf-runs\phase4_phd_execution\stage_b4_exp_gap1_e2_mlp\`

---

## 3. Drift Schedules: Generation & Validation

### 3.1 Four Core Schedules (`T = 10`, `onset_round = 4`, `is_synthetic = True`)

| Schedule Arm | `SCHEDULE_ID` | Mechanism | Onset $r_0$ | Duration $D$ | Severity $s$ | Per-Round Intensity $I(t)$ (`R1..R10`) |
|---|---:|---|---:|---:|---:|---|
| `stable_control` | `0` | `none` (`s = 0.0`) | `99` | `—` | `0.0` | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]` |
| `gradual_covariate` | `1` | `covariate_shift` | `4` | `4` | `1.5` | `[0, 0, 0, 0.25, 0.50, 0.75, 1.00, 1.00, 1.00, 1.00]` |
| `abrupt_covariate` | `2` | `covariate_shift` | `4` | `—` | `1.5` | `[0, 0, 0, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00]` |
| `recurring_covariate` | `3` | `covariate_shift` | `4` | `2` | `1.5` | `[0, 0, 0, 1.00, 1.00, 0.00, 0.00, 1.00, 1.00, 0.00]` |

*Excluded schedules:* `natural_chronological`, `abrupt_conditional_drift`, and `abrupt_prior_shift`.

### 3.2 Exact Covariate Shift Formula & Schedule Validation Gates

For round $t \in \{1..10\}$, client $k \in \{0..9\}$, sample $x_i \in S_{t,k}$, and shifted features $j \in \{0, 1, 2\}$ (`duration`, `src_bytes`, `dst_bytes`):
$$x_{i,j}^{(t)} = x_{i,j} + s \cdot I(t) + \varepsilon_{i,j,t}, \qquad \varepsilon_{i,j,t} \sim \mathcal{N}\!\left(0,\; (0.1\, I(t))^2\right)$$
computed in `float64` from an unmutated copy of $X_{t,k}$ using `np.random.default_rng(np.random.SeedSequence([seed, WINDOW_ID, SCHEDULE_ID, 501, t, k]))` and cast to `float32` for `CompactMLP`, with labels $y_i$ untouched.

**Mandatory Validation Assertions:**
1. Zero perturbation for $t \in \{1, 2, 3\}$ and all `stable_control` rounds ($\max |x^{(t)} - x| = 0$, $\sum \mathbb{I}(y^{(t)} \neq y) = 0$).
2. Strict monotonic ramp of mean continuous feature shift $\Delta\mu_t = \frac{1}{3}\sum_{j=0}^{2}(\bar{x}_{t,j} - \bar{x}_{\text{ref},j})$ across `R4 < R5 < R6 < R7` (`gradual_covariate`) — independently verified `10/10` seeds on both `W1` and `W3` in `VER-2`.
3. `100%` client PSI detection at `R4` (`gradual_covariate` and `abrupt_covariate`) — verified `100/100` on both `W1` and `W3` in `VER-2`.
4. `recurring_covariate` quorum alignment on `ON` (`R4, R5, R8, R9`) vs. `OFF` (`R6, R7, R10`) rounds — verified `40/40` `ON` and `2/30` (`W1`) / `0/30` (`W3`) `OFF` FA in `VER-2`.
5. Pre- and post-execution SHA-256 invariance of raw loaded `X_train`, `y_train`, `X_val`, `y_val`, `X_test`, `y_test` arrays — verified `True` in `VER-1`/`VER-2`.

---

## 4. Dataset Splits, Stream Partitioning & Replay Reservoirs (`RD-2`, `RD-3`, `RD-4`, `RD-5`)

### 4.1 Verified Dataset Splits & Window Separation (`W1 ⊂ W3`)

| Window (`WINDOW_ID`) | `Train` (`N` / benign / attack) | `Val` (`N` / benign / attack) | `Test` (`N` / benign / attack) | `d` | `CompactMLP` Params / FP32 Bytes |
|---|---|---|---|---:|---:|
| **`ToN-IoT W1`** (`1`) | `62,488` (`15,270` / `47,218`; `75.56%` atk) | `13,303` (`747` / `12,556`; `94.38%` atk) | `13,253` (`1,811` / `11,442`; `86.34%` atk) | `11` | `3,073` / `12,292 B` |
| **`ToN-IoT W3`** (`3`) | `147,355` (`3,043` / `144,312`; `97.93%` atk) | `33,693` (`625` / `33,068`; `98.15%` atk) | `10,547` (`3,261` / `7,286`; `69.08%` atk) | `10` | `3,009` / `12,036 B` |

- `W1` is a strict chronological subset of `W3` (`W1 ⊂ W3`); **never pooled**.
- Excluded datasets: `CICIoT2023`, `Edge-IIoTset`, `ToN-IoT train_test_network.csv` (absent/invalid wall-clock timestamps); `E5` remains `HELD`.

### 4.2 Role-Separated Disjoint Partitioning (`RD-4`)

Per `(window, seed)`:
1. **`X_train` → `D_fl_train` (`85%`) + `D_prior_audit` (`15%`):**
   `StratifiedShuffleSplit(n_splits=1, test_size=0.15, random_state=seed)`.
   - `W1`: `D_fl_train = 53,115` (`12,980` benign), `D_prior_audit = 9,373` (`2,290` benign).
   - `W3`: `D_fl_train = 125,252` (`2,587` benign), `D_prior_audit = 22,103` (`456` benign).
2. **`X_val` → `D_val_cal` (`20%`) + `D_val_psi_ref` (`20%`) + `S_1..S_10` (`60%`):**
   - Split A: `StratifiedShuffleSplit(n_splits=1, test_size=0.60, random_state=seed)` → `tmp_val (40%)`, `stream_pool (60%)`.
   - Split B: `StratifiedShuffleSplit(n_splits=1, test_size=0.50, random_state=seed + 1)` on `tmp_val` → `D_val_cal (20%)`, `D_val_psi_ref (20%)`.
   - Split C: `StratifiedKFold(n_splits=10, shuffle=True, random_state=seed + 2)` on `stream_pool` → `10` disjoint blocks `S_1..S_10`.
   - `D_val_cal`: frozen threshold $\tau_{\text{val}}$ calibration on `M_0` only (`W1: 2,660`, `W3: 6,738`).
   - `D_val_psi_ref`: **features `X` only** (zero label access), static PSI baseline fit once before `R1` (`W1: 2,661`, `W3: 6,739`).
   - `S_1..S_10`: prequential test-then-adapt stream (`W1: ~799/rd`, `W3: ~2,022/rd`).
3. **`X_test` (`100%` untouched):** Zero usage for PSI, calibration, adaptation, or protocol selection; reserved strictly for uncontaminated static `M_0` and `M_10` generalization audit.
4. **Runtime Assertions:** Pairwise disjointness across `D_fl_train`, `D_prior_audit`, `D_val_cal`, `D_val_psi_ref`, `S_1..S_10`, and `X_test`, plus `psi_ref_labels_accessed == False`.

### 4.3 Unambiguous `SeedSequence` Client Partitioning (`RD-5`)

- **Base FL Training (`D_fl_train`):** Pure unmodified class-wise `Dirichlet(alpha=0.5)` via `partition_clients_np(y_fl_train, n_clients=10, strategy="label_skew", alpha=0.5, seed=seed)`.
- **Stream & PSI-Reference Partitioning (`D_val_psi_ref` and `S_1..S_10`):**
  - Fixed canonical class iteration order: **`c = 0` (benign), then `c = 1` (attack)**.
  - Dedicated per-class proportion RNG: `rng_prop(c) = np.random.default_rng(np.random.SeedSequence([seed, WINDOW_ID, 201, c]))` → `p_raw = rng_prop(c).dirichlet(np.full(10, 0.5))`.
  - Simplex floor (`p_min = 0.06`, `K = 10`): $p^{(c)} = 0.40\, p^{(c,\text{raw})} + 0.06$.
  - Dedicated per-`(split_tag, round_slot, class)` shuffle RNG (`split_tag = 202, round_slot = 0` for `D_val_psi_ref`; `split_tag = 203, round_slot = t ∈ {1..10}` for `S_t`):
    `rng_shuf(c) = np.random.default_rng(np.random.SeedSequence([seed, WINDOW_ID, split_tag, round_slot, c]))`.
  - Shuffle ascending `idx_c = np.where(y == c)[0]` in-place; allocate `counts = np.floor(p[c] * len(idx_c)).astype(np.int64)`; assign remainder `len(idx_c) - int(counts.sum())` to `int(np.argmax(p[c]))` (deterministic lowest-index tie-break); slice contiguously to `k = 0..9`; merge and sort each client's indices ascending.
  - **Fail-Closed Stream Guards:** Assert `len(bucket[k]) >= 30`, `n_benign[k] >= 1`, `n_attack[k] >= 1` for every `(seed, round, client)` in `D_val_psi_ref` and `S_1..S_10` (`VER-2`: `0` failures across `2,000` stream client-rounds and `200` ref client-slots).
  - **Local PSI Fit:** Each client $k$ fits `FeatureDriftDetector(psi_threshold=0.25, n_bins=5)` strictly on `X_val_psi_ref[ref_parts[k]]` (`n_bins = 5` preserved exactly from v4.0).

### 4.4 Replay-Reservoir Construction (`B_k`, `RD-2` + `RD-3`)

1. **Source & Maximum Cap:** Constructed strictly from `D_fl_train[k]` (`cap = 500` maximum, never oversampled):
   - If $N_k = |D_{\text{fl\_train}, k}| \le 500$: retain **all** eligible samples (`B_k = sorted(D_fl_train[k])`; logged as `below_or_eq_cap_all_kept`).
   - If $N_k > 500$ and single-class ($N_{k,0} = 0$ or $N_{k,1} = 0$, permitted per `RD-3`): sample `500` indices strictly without replacement from the sole available class (`single_class_attack_only` or `single_class_benign_only`; `is_single_class_reservoir = True`; zero oversampling; zero client exclusion).
   - If $N_k > 500$ and both classes present ($N_{k,0} \ge 1, N_{k,1} \ge 1$): proportional stratified targets:
     $$m_{k,0} = \max\!\left(1,\; \min\!\left(N_{k,0},\; \left\lfloor 500 \cdot \frac{N_{k,0}}{N_k} \right\rfloor\right)\right), \qquad m_{k,1} = 500 - m_{k,0}$$
     (clamping $m_{k,1} = N_{k,1}$ and reallocating $m_{k,0} = \min(N_{k,0}, 500 - m_{k,1})$ if $m_{k,1} > N_{k,1}$). When $\lfloor 500 \cdot N_{k,0}/N_k \rfloor = 0$ with $N_{k,0} \ge 1$, keeping `m_{k,0} = 1` real sample without replacement is logged as `min1_benign_floor_applied`.
2. **Sampling Order & Deterministic RNG:** Iterate `c = 0`, then `c = 1`. For each class with $m_{k,c} > 0$, instantiate `rng_res = np.random.default_rng(np.random.SeedSequence([seed, WINDOW_ID, 301, k, c]))` and draw `m_{k,c}` indices without replacement from sorted class-$c$ indices in `D_fl_train[k]`. Concatenate and sort ascending.
3. **Frozen Membership & Disjointness:** Built once per `(window, seed, client)` and frozen across all `10` rounds, `4` schedules, and both replay arms. Runtime `assert` confirms `0` overlap with `D_prior_audit`, `D_val_cal`, `D_val_psi_ref`, `S_1..S_10`, and `X_test`.
4. **Reconciled Feasibility Guard (`RD-3` + `VER-1`):**
   - **Hard fail-closed size guard:** Abort if any client has `|B_k| == 0` or `|B_k| < 32` (`VER-1` verified `0 / 200` failures; `min |B_k| = 38` on `W1`, `36` on `W3`).
   - **Single-class reservoirs permitted & explicitly logged (`RD-3`):** `VER-1` found `3/100` single-class reservoirs on `W1` (`|B_k| = 500`) and `5/100` on `W3` (`|B_k| ∈ {74, 500}`). No conflict exists with `|B_k| >= 32`. Frozen base `pos_weight[k]` follows Stage A2's exact rule (`min(10.0, max(0.1, n_neg/n_pos))` if both classes exist in `D_fl_train[k]`, else `1.0`).

---

## 5. Exact Local Adaptation Sampler (`RD-1`), Federated State Machine & Compute Accounting

### 5.1 Deterministic Shuffled-Cycle Sampler with CRN (`RD-1`)

Every adapted client-round in `fine_tune`, `drift_gated_replay`, and `unconditional_replay` executes **exact `N_adapt_steps = 8`** `AdamW(lr=2e-3, weight_decay=1e-4)` optimizer steps (`clip_grad_norm_(5.0)`, frozen `pos_weight[k]`) with **exact `batch_size = 64`** (`512` sample presentations per adapted client-round) and **`drop_last = False`**:

1. **Budget split per step ($s \in \{0..7\}$):**
   - `fine_tune`: `req_curr = 64`, `req_rep = 0` (`total_curr = 512`, `total_rep = 0`).
   - `drift_gated_replay` & `unconditional_replay`: `req_curr = 32`, `req_rep = 32` (`total_curr = 256`, `total_rep = 256`).
2. **Shuffled-Cycle Stream (`build_cyclic_indices(pool, total_need, base_seed_tuple)`):**
   - Compute `n_passes = ceil(total_need / len(pool))`.
   - For each pass `p = 0, 1, ..., n_passes - 1`: instantiate `rng_p = np.random.default_rng(np.random.SeedSequence([*base_seed_tuple, p]))` and shuffle `pool` **without replacement** (`rng_p.permutation(pool)`).
   - Concatenate passes `0 .. n_passes - 1` and slice `[:total_need]`.
   - **Cycle restart behavior:** Every restart begins a fresh independent permutation of the full pool without replacement; no trailing samples are dropped (`drop_last = False`).
   - **Sub-batch behavior (`|S_{t,k}| < 64` in `fine_tune`, e.g., `min_n = 47` on `W1`):** Pass `0` yields all `n` unique samples without replacement, immediately padded by the first `64 - n` samples of independently shuffled Pass `1` to complete Step `0`'s `64`-sample batch. Every sample appears `1–2×` within Step `0` and `floor(512/n)` or `ceil(512/n)` times across all `8` steps.
3. **Exact RNG Derivation (CRN on Current Stream + Separate Replay Stream):**
   - `WINDOW_ID = {"W1": 1, "W3": 3}`, `SCHEDULE_ID ∈ {0, 1, 2, 3}`, `ARM_ID = {"static": 0, "fine_tune": 1, "unconditional_replay": 2, "drift_gated_replay": 3}`.
   - **Current-stream pass `p` (CRN — shared across arms via `ARM_TAG = 0`):** `SeedSequence([seed, WINDOW_ID, SCHEDULE_ID, 0, 401, t, k, p])`.
   - **Replay-buffer pass `p` (separate deterministic stream, `tag = 402`):** `SeedSequence([seed, WINDOW_ID, SCHEDULE_ID, 0, 402, t, k, p])` (identically coupled between `drift_gated_replay` and `unconditional_replay` when both adapt on the same `(seed, t, k)`).
   - **Per-step mini-batch shuffle (`s ∈ {0..7}`):** `SeedSequence([seed, WINDOW_ID, SCHEDULE_ID, 0, 403, t, k, s])` permutes the `64`-sample concatenated `[curr_32; rep_32]` batch (and `fine_tune`'s `64`-sample slice stays in cyclic order).

### 5.2 Deterministic 5-Phase Federated Round State Machine (`R1..R10`, `q_min = 3`, `cooldown = 0`)

1. **Phase 1 (Prequential Evaluation):** All `K = 10` clients hold $M_{t-1}$; evaluate fleet prequential metrics on unseen $S_t$ at frozen $\tau_{\text{val}}$ and fixed `0.50`; each client computes $\ell_{t,k}^{\text{pre}} = \text{BCE}(M_{t-1}, S_{t,k})$.
2. **Phase 2 (Local Drift Signals — Logged in All 4 Arms):** `local_psi_triggered[k] = (det_k.detect(X_{t,k}).max_psi >= 0.25)`; `local_ph_triggered[k] = ph_k.update(local_pre_bce[k])` (`PageHinkleyDetector(delta=0.005, threshold=0.10, min_samples=3)`); `local_triggered[k] = local_psi_triggered[k] or local_ph_triggered[k]`; $\mathcal{A}_t = \{k : \text{local\_triggered}[k]\}$.
3. **Phase 3 (Quorum Gate `q_min = 3`):** For gated arms (`fine_tune`, `drift_gated_replay`), `quorum_met = (|A_t| >= 3)`. If `quorum_met == False`, **zero** clients perform local training (`0` steps, `0` B, $M_t = M_{t-1}$, no candidate updates computed/retained/discarded, `PH_k` NOT reset).
4. **Phase 4 (Per-Arm Execution & Aggregation):**
   - `static`: never adapts (`0` steps, `0` B, `PH_k` never resets).
   - `fine_tune` & `drift_gated_replay`: when `quorum_met == True`, **only** $k \in \mathcal{A}_t$ execute `8` steps (`64` curr vs. `32` curr + `32` rep) and upload $\Delta\theta_{t,k}$; non-triggered clients $k \notin \mathcal{A}_t$ execute `0` steps and upload `0` B. Server aggregates strictly over $\mathcal{A}_t$ with stream-size weights $w_{t,k} = |S_{t,k}| / \sum_{j \in \mathcal{A}_t} |S_{t,j}|$, updates $\theta_t = \theta_{t-1} + \sum_{k \in \mathcal{A}_t} w_{t,k}\,\Delta\theta_{t,k}$, and broadcasts $M_t$ to all `10` clients.
   - `unconditional_replay`: freezes `R1..R3` (`0` steps, `0` B, preserving bit-identical pre-drift baseline across all 4 arms); on `R4..R10`, all `K = 10` clients execute `8` steps (`32` curr + `32` rep), aggregate over all `10` clients via stream-size weights, and download $M_t$.
5. **Phase 5 (`PH_k` Reset & Re-Arming):** Whenever `adapted_this_round == True`, call `ph_k.reset()` **strictly on participating clients** (re-arming after `3` subsequent rounds via `min_samples = 3`). Non-participating clients keep `PH_k` active. Static `PSI_k` never resets. Simultaneous `PSI + PH` triggers execute a single `8`-step adaptation pass.

### 5.3 Compute-Fairness Accounting

- `drift_gated_replay` vs. `fine_tune`: **Compute-matched** (`8` steps / `512` presentations per adapted client-round; identical gating policy; exact `delta_fed_steps` logged if `PH_k` trajectories diverge).
- `drift_gated_replay` vs. `unconditional_replay`: **Per-step matched, intentionally natural policy-cost comparison** (`unconditional_replay` expends fixed `560` federation steps / `35,840` presentations across `R4..R10` on every schedule vs. gated `~0–20` on `stable_control`, `~320` on `recurring`, `~560` on `abrupt`/`gradual`). Exact `total_federation_adapt_steps`, `total_federation_sample_presentations`, and `total_adaptation_comm_bytes` are co-reported on all tables.
- Clean-federation boundary: `byzantine_clients = 0`; zero `C1` attribution or `C2` 4-tier response telemetry (owned by `EXP-GAP-2` / `EXP-GAP-3`).

---

## 6. Primary Metrics, `final_prior_audit_forgetting_delta`, Statistical Plan & Determinism Pilot

### 6.1 `final_prior_audit_forgetting_delta`

- **Metric Basis:** Unweighted binary cross-entropy (BCE) loss (`eval_bce_np`, probability clipping `[1e-6, 1 - 1e-6]`) evaluated on the synchronized **global** model over fixed unseen `D_prior_audit` (`9,373` rows `W1`; `22,103` rows `W3`).
- **Formula:**
  $$\mathcal{L}_{\text{prior}}(M) = -\frac{1}{N_{\text{audit}}} \sum_{i=1}^{N_{\text{audit}}} \Big[ y_i \ln \hat{p}_i(M) + (1 - y_i)\ln\!\big(1 - \hat{p}_i(M)\big) \Big], \qquad \hat{p}_i(M) = \operatorname{clip}\!\big(\sigma(f_M(x_i)),\, 10^{-6},\, 1 - 10^{-6}\big)$$
  $$\text{final\_prior\_audit\_forgetting\_delta} = \mathcal{L}_{\text{prior}}(M_{10}) - \mathcal{L}_{\text{prior}}(M_0)$$
- **Sign Convention:** `> 0` = **more catastrophic forgetting (worse)**; `= 0` = no change (`0.0` for `static`); `< 0` = backward transfer / improvement (better).
- **Aggregation:** No per-client aggregation (global model metric); summarized across `SEEDS_10` by `mean`, sample `SD` (`ddof=1`), `median`, `min`, `max`, and tested via matched-seed paired Student-$t$ (`df = 9`) + exact two-sided Wilcoxon signed-rank + Holm-Bonferroni.

### 6.2 Seeds, Run Ledger & Pre-Registered Holm-Bonferroni Families

- **Seeds:** `SEEDS_10 = (42, 101, 202, 303, 404, 505, 606, 707, 808, 909)` (`n = 10`, `df = 9`).
- **Confirmatory Runs (Not Authorized Yet):** `20` base FL `CompactMLP` models (`2 windows × 10 seeds`) + `320` confirmatory trajectory runs (`2 windows × 4 schedules × 4 arms × 10 seeds`).
- **Pre-Registered Holm Families (Separate per Window `W1`/`W3`, $\alpha = 0.05$):**
  - **`F1` (`m = 3`):** `drift_gated_replay` vs. `static` on `mean_r5_r10_pre_adapt_macro_f1` (`gradual`, `abrupt`, `recurring`).
  - **`F2` (`m = 3`):** `drift_gated_replay` vs. `fine_tune` on `final_prior_audit_forgetting_delta` (`gradual`, `abrupt`, `recurring`).
  - **`F3` (`m = 4`):** `drift_gated_replay` vs. `unconditional_replay` on `stable_control` (`mean_r4_r10_pre_adapt_macro_f1`, `final_prior_audit_forgetting_delta`, `total_federation_adapt_steps`) and `recurring_covariate` (`final_prior_audit_forgetting_delta`).
- **Stable-Control FAR Reporting:** Mandatory client-level (`client_psi_far`, `client_ph_far`, `client_any_far`) AND fleet-level (`fleet_quorum_far`).

### 6.3 Determinism Pilot Specification (`VER-3` — Not Executed Yet)

- **Design:** Two independent, sequential, identical repeated executions (`pilot_run_A`, `pilot_run_B`) of **`(ToN-IoT W1, abrupt_covariate, drift_gated_replay, seed=42)`** from clean initial state, written exclusively to `stage_b4_exp_gap1_e2_mlp/pilot_determinism_check/run_A/` and `run_B/` (`"is_pilot_excluded_from_confirmatory": true`).
- **Compared Outputs:** (1) flattened `float64` $\theta_0$ and $\theta_{10}$ (`max_abs_diff <= 1e-6`); (2) per-round prequential probability vectors $\hat{p}_{1..10}$ and $\hat{p}_{\text{audit}}$ (`<= 1e-6`); (3) all floating-point metrics and detector stats (`<= 1e-6`); (4) exact equality (`tolerance = 0`) on all discrete control-flow flags (`adaptation_rounds`, `quorum_met`, triggers, participation, PH resets, federation steps, comm bytes, split hashes); (5) normalized `run_report.json` diff excluding only `run_id`, `generated_utc`, and `*_wall_seconds`.
- **Fail-Closed Policy:** Any discrete mismatch or `max_abs_diff > 1e-6` immediately aborts (`0` confirmatory runs launched), triggers root-cause investigation (e.g., CUDA kernel determinism / `CUBLAS_WORKSPACE_CONFIG=:4096:8` / CPU fallback), and requires protocol revision & re-approval.
- **Exclusion Guarantee:** Strictly excluded from the `320` confirmatory runs, master summaries, and all statistical tests.

---

## 7. Independently Verified Read-Only Evidence (`VER-1` & `VER-2`)

### 7.1 `VER-1`: Reservoir Feasibility Across All `SEEDS_10` (`200` Client Reservoirs)

| Metric (10 seeds × 10 clients = 100/window) | `ToN-IoT W1` (Independently Verified) | `ToN-IoT W3` (Independently Verified) |
|---|---:|---:|
| Deterministic (`2×` exact array match) | `True` (`100/100`) | `True` (`100/100`) |
| Disjoint from `D_prior_audit` | `True` (`100/100`) | `True` (`100/100`) |
| `min / max` client `D_fl_train[k]` size | `38` / `21,409` | `36` / `91,860` |
| `min / max` reservoir `\|B_k\|` size | **`38`** / `500` | **`36`** / `500` |
| Empty (`\|B_k\| == 0`) / Undersized (`\|B_k\| < 32`) | **`0`** / **`0`** | **`0`** / **`0`** |
| Below cap (`32 <= \|B_k\| < 500`, all eligible kept) | `7 / 100` | `6 / 100` |
| `min1_benign_floor_applied` (`raw_m0=0, n0>=1 -> m0=1`) | `4 / 100` | `11 / 100` |
| Single-class reservoirs (`RD-3` permitted, `0` oversampling) | **`3 / 100`**: `(202, k=4: 0b/500a)`, `(606, k=4: 500b/0a)`, `(707, k=6: 500b/0a)` | **`5 / 100`** (all attack-only): `(42, k=7: 0b/74a)`, `(303, k=2: 0b/500a)`, `(303, k=7: 0b/500a)`, `(505, k=8: 0b/500a)`, `(808, k=6: 0b/500a)` |

### 7.2 `VER-2`: Deterministic `SeedSequence` Stream & Clean-FAR Verification (`2,000` Client-Rounds / `200` Fleet-Rounds)

| Metric (`p_min=0.06`, `n_bins=5`, `q_min=3`, `psi_thr=0.25`) | `ToN-IoT W1` (Independently Verified) | `ToN-IoT W3` (Independently Verified) |
|---|---:|---:|
| Deterministic (`2×` exact match) & Disjoint `X_val` 3-way + blocks | `True` / `True` | `True` / `True` |
| Source arrays immutable (`pre == post` SHA-256) | `True` | `True` |
| `D_val_psi_ref` per-client `min (total / benign / attack)` | `161 / 9 / 150` | `403 / 7 / 396` |
| `S_1..S_10` per-client `min (total / benign / attack)` | `47 / 2 / 45` | `121 / 2 / 119` |
| Empty clients / Guard failures (`n < 30` or missing class) | **`0`** / **`0`** | **`0`** / **`0`** |
| `stable_control` Client-level PSI FAR (`1,000` client-rounds) | `76 / 1,000` (`7.60% ± 3.34%` SD; seeds: `[5,3,11,5,6,12,12,5,7,10]`) | `2 / 1,000` (`0.20% ± 0.42%` SD; seeds: `[0,0,0,0,0,1,0,0,0,1]`) |
| `stable_control` Fleet-level Quorum FAR (`q_min=3`, `100` rounds) | **`4 / 100`** (`4.00% ± 5.16%` SD; seeds: `[0,0,1,1,0,1,1,0,0,0]`) | **`0 / 100`** (`0.00% ± 0.00%` SD; seeds: `[0,0,0,0,0,0,0,0,0,0]`) |
| Diagnostic: Fleet FAR if `q_min=2` had been used | `19 / 100` (`19.0%`) | `0 / 100` (`0.0%`) |
| `gradual_covariate` `R4` (`0.25`) / `abrupt` `R4` (`1.0`) client recall | `100 / 100` / `100 / 100` | `100 / 100` / `100 / 100` |
| `gradual_covariate` continuous ramp monotonicity (`R4<R5<R6<R7`) | `10 / 10` seeds | `10 / 10` seeds |
| `recurring_covariate` `ON` (`R4,5,8,9`) / `OFF` (`R6,7,10`) `q_min=3` | `40 / 40` (`100%`) / `2 / 30` (`6.67%`) | `40 / 40` (`100%`) / `0 / 30` (`0.00%`) |

**Verification Limitations:** `VER-1` and `VER-2` are strictly read-only data/detector checks with zero model training; live Page-Hinkley (`PH`) loss-stream FAR, live `CompactMLP` `static` accuracy drop on `abrupt_covariate`, and CUDA deterministic tolerance (`<= 1e-6`) remain unverified until the determinism pilot (`VER-3`) is authorized.

---

## 8. Claim-Scope Boundaries (Unchanged from v4.0)

`EXP-GAP-1` can support controlled synthetic covariate-drift recovery (`F1`), unbiased prior-audit forgetting mitigation (`F2`), and client-local drift-gating protection/savings (`F3`) on binary `CompactMLP` over ToN-IoT `W1` & `W3` (`W1 ⊂ W3`, non-pooled, simulated logical gateways, Non-DP, non-SecAgg). It **cannot** support natural or conditional drift, `C1` attribution, `C2` 4-tier response, `E6` closed-loop ablation, formal DP, Secure Aggregation, physical IoT gateway timing/energy, logit distillation, or `E5` cross-dataset transfer.
