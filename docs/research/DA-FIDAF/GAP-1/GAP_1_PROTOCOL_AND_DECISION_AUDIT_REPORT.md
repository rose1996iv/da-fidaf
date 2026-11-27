# DA-FIDAF GAP-1 — Protocol & Decision Audit Report (Phase B)

**Document Status:** `COMPLETED — AUDIT PASSED (NO METHODOLOGICAL CONTRADICTIONS)`  
**Date:** `2026-11-28`  
**Audited Protocol:** [EXP_GAP_1_Protocol_v5_0.md](EXP_GAP_1_Protocol_v5_0.md) (`SHA-256: 0ee5dbd15e2116ab0294bcd7d5f8a715837a97aa99cd761e024645f6e7899ad2`)  
**Scope:** Line-by-line verification of `RD-1` through `RD-5`, operational definitions, internal consistency across `v1.0`–`v5.0`, alignment with frozen evidence ledgers, and maintenance of the authoritative decision log.

---

## 1. Operational Verification Matrix (`RD-1` – `RD-5`)

| Decision / Requirement | Location in `v5.0` | Operational Completeness Check | Audit Result |
|---|---|---|---|
| **`RD-1`: Shuffled-cycle adaptation sampling** | §1 (L14), §5.1 (L133–L150) | Exact `N_adapt_steps = 8`, `batch_size = 64` (`512` presentations), `drop_last = False`, independent without-replacement pass shuffles (`n_passes = ceil(total_need / n)`), cycle restart behavior, and sub-batch wraparound (`|S_{t,k}| < 64` padded seamlessly from Pass `1`) all explicitly defined. | **PASS** (`independently verified`) |
| **`RD-1`: Current-stream CRN + separate replay RNG** | §5.1 (L147–L150) | Current-stream passes use `SeedSequence([seed, WINDOW_ID, SCHEDULE_ID, 0, 401, t, k, p])` (`ARM_TAG = 0` CRN across comparable arms); replay passes use separate stream `tag = 402` (`[seed, WINDOW_ID, SCHEDULE_ID, 0, 402, t, k, p]`); concatenated `[curr_32; rep_32]` shuffled per step via `tag = 403`. | **PASS** (`independently verified`) |
| **`RD-2`: Proportional stratified replay reservoir (`B_k`)** | §1 (L15), §4.4 (L115–L124) | Constructed from `D_fl_train[k]` only; `cap = 500` maximum (all `N_k` kept if `N_k <= 500`); proportional formula `m_k0 = max(1, min(N_k0, floor(500 * N_k0 / N_k)))`, `m_k1 = 500 - m_k0` with symmetric clamp; deterministic without-replacement `SeedSequence([seed, WINDOW_ID, 301, k, c])` (`c=0` then `c=1`); frozen across rounds & arms; zero oversampling; shortfalls explicitly logged. | **PASS** (`independently verified`) |
| **`RD-3`: Single-class / incomplete-class reservoirs** | §1 (L16), §4.4 (L119, L125–L127) | Permitted without oversampling or client exclusion; exact class coverage `(N_k0, N_k1, m_k0, m_k1, is_single_class_reservoir)` logged; reconciled with `|B_k| >= 32` size guard (`0/200` failures in `VER-1`; all `8` single-class clients have `|B_k| >= 74`); `pos_weight[k] = 1.0` fallback matches `stage_a2_nonlinear_and_personalization.py` L263. | **PASS** (`independently verified`) |
| **`RD-4`: Deterministic validation partitioning & `X_test` isolation** | §1 (L17), §4.2 (L85–L100) | `X_val` split via `StratifiedShuffleSplit(0.60, seed)` → `StratifiedShuffleSplit(0.50, seed+1)` → `StratifiedKFold(10, shuffle=True, seed+2)` into disjoint `20% D_val_cal`, `20% D_val_psi_ref` (`X` only), and `60% S_1..S_10`. `X_test` `100%` untouched by PSI, calibration, adaptation, and protocol selection. `W1 ⊂ W3` strictly separate. | **PASS** (`independently verified`) |
| **`RD-5`: `p_min`, `q_min`, `n_bins`, PSI threshold & guards** | §1 (L18), §4.3 (L102–L113), §5.2 (L152–L161) | `p_min = 0.06` (`p_eff = 0.40 * p_raw + 0.06`), `q_min = 3` of `K = 10`, `n_bins = 5` (preserved from v4.0), `psi_threshold = 0.25`, `eps = 1e-6`, dedicated per-`(split_tag, round_slot, class)` `SeedSequence` (`tags 201/202/203`, `c=0` then `c=1`), `argmax` remainder allocation, fail-closed guards `len >= 30, n_0 >= 1, n_1 >= 1`. | **PASS** (`independently verified`) |

---

## 2. Cross-Version & Ledger Consistency Audit

1. **Alignment with Unified Cross-Stage Ledger (`U-D0-01`–`U-D0-04`, `U-A1-03`):**
   - `W1` (`89,269`) and `W3` (`191,738`) counts, `W1 ⊂ W3` non-pooling rule, exclusion of timestamp-less datasets (`CICIoT2023`, `Edge-IIoTset`, `ToN-IoT train_test_network.csv`), `E5: HOLD` status, `Non-DP` / `secure_aggregation_active: False` scope, and simulated logical gateway disclosure (`K = 10`, desktop `GTX 1650`) match the frozen ledger `100%` (`supported by existing frozen evidence`).
2. **Non-Blocking Subtle Observations Documented Explicitly (Zero Silent Edits Made):**
   - **OBS-B1 (`min1_benign_floor_applied` in `RD-2`):** For `4/100` (`W1`) and `11/100` (`W3`) clients with $N_k > 500$, $N_{k,0} \ge 1$, and benign proportion $< 0.2\%$ ($\lfloor 500 \cdot N_{k,0}/N_k \rfloor = 0$), v5.0 sets $m_{k,0} = 1$ (retaining `1` real benign sample without replacement; `0` oversampling) rather than rounding benign down to `0`. This honors `RD-2` ("preserving each client's original class proportions as closely as feasible", zero oversampling) and is explicitly logged under `allocation_notes`.
   - **OBS-B2 (`W3` single-class overlap count in v5.0 §7.1):** On `W3`, `(seed=42, client=7: 0b/74a)` is simultaneously `< 500` (`below_or_eq_cap_all_kept = 6`) AND single-class (`n_single_class_clients = 5` = `4` at `cap=500` + `1` at `N_k=74`). Total across the four mutually exclusive `allocation_notes` buckets is `79 + 6 + 11 + 4 = 100`. Clarified in `GAP_1_READ_ONLY_VERIFICATION_REPORT.md`.
   - **OBS-B3 (`v5.0` §5.1 L150 `fine_tune` step-shuffle):** Concatenated `[curr_32; rep_32]` is permuted via `tag 403` for replay arms, while `fine_tune`'s `64`-sample slice already comes from independently shuffled passes (`tag 401`) and stays in cyclic order. Unambiguous as written.
   - **OBS-B4 (External governance header inside byte-identical v5.0 copy):** Line 6 of `EXP_GAP_1_Protocol_v5_0.md` references the original pre-consolidation folder `I:\Projects\da-fidaf-runs\phase4_phd_execution\exp_gap1_protocol\` because `docs/research/DA-FIDAF/GAP-1/EXP_GAP_1_Protocol_v5_0.md` is intentionally kept byte-identical (`SHA-256: 0ee5dbd1...`) to preserve hash continuity. Noted in `README.md`.
   - **OBS-B5 (`CompactMLP` Dropout RNG during adaptation):** `CompactMLP` (`common_phase4.py` L516) includes `nn.Dropout(0.10)`. During implementation (when authorized), `set_all_seeds(...)` / `torch.Generator` seeding per `(seed, round, client, step)` must explicitly seed PyTorch's CUDA/CPU RNG before each adaptation call so `Dropout(0.10)` is deterministic across repeated runs; flagged explicitly in the Phase D Readiness Plan.

---

## 3. Authoritative GAP-1 Decision Log (`D1`–`D6`, `RD-1`–`RD-5`)

| ID | Decision Summary | Locked Value | Approval Status | Supersedes |
|---|---|---|---|---|
| **D1** | Stream horizon & onset | `T = 10`, `onset_round = 4`, `gradual D = 4`, `recurring D = 2` | Locked (User) | Phase 3B.3 `T=8, onset=3` |
| **D2** | Drift schedules included | `stable_control`, `gradual_covariate`, `abrupt_covariate`, `recurring_covariate` only | Locked (User) | Optional `natural` / `conditional` arms |
| **D3** | Base client heterogeneity | Non-IID class-wise `Dirichlet(alpha = 0.5)`, `K = 10` | Locked (User) | YAML `iid` baseline |
| **D4** | Client-local federated adaptation | `local_psi or local_ph`, `q_min = 3`, pre-training quorum gate, participating-only stream-weighted `FedAvg`, `PH` reset strictly on participating clients, `cooldown = 0` | Locked (User) | Phase 3B.3 centralized adapter; v2.0 `q_min = 2` |
| **D5** | Comparators & compute accounting | 4 arms (`static`, drift-gated `fine_tune`, `unconditional_replay` `R4..R10`, `drift_gated_replay`); no regularized arm; compute-matched (`fine_tune` vs. `drift_gated_replay`) vs. natural policy-cost (`unconditional_replay`) | Locked (User) | Optional `regularized` arm |
| **D6** | Seeds & statistical power | `SEEDS_10 = (42, 101, 202, 303, 404, 505, 606, 707, 808, 909)` (`df = 9`), paired Student-$t$ + exact Wilcoxon + pre-registered Holm (`F1`/`F2`/`F3`); `2` pilot runs excluded | Locked (User) | Phase 4 `SEEDS_5` |
| **RD-1** | Batch sampler & CRN | Shuffled-cycle (`Option 1A`), `drop_last = False`, `8` steps × `64`, CRN `tag 401` (`ARM_TAG = 0`), separate replay `tag 402`, concat perm `tag 403` | Locked (User) | v4.0 open `Option 1A` vs. `1B` |
| **RD-2** | Replay reservoir allocation | Proportional stratified, `cap = 500` max, without replacement (`tag 301`), frozen across rounds/arms, zero oversampling | Locked (User) | v4.0 open proportional vs. 50/50 |
| **RD-3** | Single-class reservoirs | Permitted using only available class(es); zero oversampling; zero client exclusion; explicit class-coverage logging | Locked (User) | v4.0 open Option 3A vs. 3B |
| **RD-4** | Validation split & `X_test` isolation | `X_val` → `20% D_val_cal` / `20% D_val_psi_ref` (`X` only) / `60% S_1..S_10`; `X_test` `100%` untouched; `W1 ⊂ W3` separate | Locked (User) | v2.0 `20% X_test` PSI ref |
| **RD-5** | Stream floor, quorum & bins | `p_min = 0.06`, `q_min = 3`, `n_bins = 5` (`psi_threshold = 0.25`, `eps = 1e-6`), `SeedSequence` tags `201/202/203` | Locked (User) | v3.0 scalar-seed stream RNG |

**Methodological Ambiguities Blocking Safe Progress:** **None.** Every core methodological decision (`D1`–`D6`, `RD-1`–`RD-5`) is unambiguously locked and consistent.
