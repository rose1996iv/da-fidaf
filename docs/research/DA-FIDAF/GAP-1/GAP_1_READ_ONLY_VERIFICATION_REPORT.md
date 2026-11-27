# DA-FIDAF GAP-1 — Read-Only Verification Report (`VER-1` & `VER-2`, Phase C)

**Document Status:** `COMPLETED — READ-ONLY VERIFICATION PASSED`  
**Date:** `2026-11-28`  
**Protocol Verified:** [EXP_GAP_1_Protocol_v5_0.md](EXP_GAP_1_Protocol_v5_0.md) (`SHA-256: 0ee5dbd15e2116ab0294bcd7d5f8a715837a97aa99cd761e024645f6e7899ad2`)  
**Scope:** Strictly read-only data-partition, replay-reservoir (`VER-1`), and deterministic stream / clean PSI false-alarm (`VER-2`) verification across `SEEDS_10` on `ToN-IoT W1` and `ToN-IoT W3`. Zero models trained; zero pilots launched; zero datasets, configs, or frozen ledgers modified.

---

## 1. Exact Inputs, Source File Hashes & Execution Context

- **Source Modules Invoked (Read-Only, Unchanged SHA-256s Confirmed on `2026-11-28`):**
  - `I:\Projects\da-fidaf-runs\phase4_phd_execution\common_phase4.py` (`86f01f7e920f1760063757985f4ecfc3ec852ceaef6600e230f3307997aa91ea`) — `load_ton_iot_window`, `partition_clients_np`.
  - `I:\Projects\da-fidaf-runs\scripts\phase3b\common_phase3b.py` (`96b4e0d6d1576ba082e28cb4446ca49efde022ab1db3c8c25303c59c0f44d9c6`) — `load_strided_window`.
  - `I:\Projects\da-fidaf\src\dafidaf\drift\core.py` (`74f18fdd045c7a7b27ef91d8b13df5e0b03e9d1cc11c92c93db175d9f78cae3a`) — `FeatureDriftDetector(psi_threshold=0.25, n_bins=5)`.
- **Parameters:**
  - Windows (strictly separate; `W1 ⊂ W3`, never pooled): `ToN-IoT W1` (`89,269` rows: `62,488 / 13,303 / 13,253`, `d=11`) and `ToN-IoT W3` (`191,738` rows: `147,355 / 33,693 / 10,547`, `d=10`).
  - Seeds: `SEEDS_10 = (42, 101, 202, 303, 404, 505, 606, 707, 808, 909)`.
  - Federation & Detector Constants: `K = 10`, `alpha = 0.5`, `cap = 500`, `p_min = 0.06`, `q_min = 3`, `n_bins = 5`, `psi_threshold = 0.25`, `T = 10`, `onset_round = 4`, `severity = 1.5`.
- **Execution Record:** Single read-only Python verification script (`task-536`, exit code `0`, zero file writes) piped via stdin against live `I:\IoT` shards through `load_ton_iot_window()`. All source modules and frozen ledgers re-hashed unchanged after execution.

---

## 2. `VER-1` Results — Replay-Reservoir Feasibility (`200` Client Reservoirs)

**Evidence Status:** `independently verified` (read-only partition & reservoir check only; does **not** validate model training).

| Check (`10` seeds × `10` clients = `100` per window) | `ToN-IoT W1` | `ToN-IoT W3` | Gate Outcome |
|---|---:|---:|---|
| Raw `X_train`/`y_train`/`X_val`/`y_val`/`X_test`/`y_test` SHA-256 unchanged | `True` | `True` | **PASS** |
| Reservoir determinism (`2×` repeated construction exact array match) | `True` (`100/100`) | `True` (`100/100`) | **PASS** |
| Reservoir disjointness from `D_prior_audit` (`0` index overlap) | `True` (`100/100`) | `True` (`100/100`) | **PASS** |
| Client `D_fl_train[k]` size (`min / max`) | `38 / 21,409` | `36 / 91,860` | **PASS** |
| Reservoir `\|B_k\|` size (`min / max`) | **`38`** `/ 500` | **`36`** `/ 500` | **PASS (`>= 32`)** |
| Empty (`\|B_k\| == 0`) / Undersized (`\|B_k\| < 32`) | **`0 / 0`** | **`0 / 0`** | **PASS** |
| `exact_proportional` (`N_k > 500`, both classes, `raw_m0 >= 1`) | `86 / 100` | `79 / 100` | Logged |
| `below_or_eq_cap_all_kept` (`32 <= N_k <= 500`, all eligible kept) | `7 / 100` | `6 / 100` *(incl. `1` single-class: `seed=42, k=7`)* | Logged (`RD-2`) |
| `min1_benign_floor_applied` (`N_k > 500, n0 >= 1, floor=0 -> m0=1`) | `4 / 100` | `11 / 100` | Logged (`RD-2`) |
| `single_class_attack_only` (`N_k > 500, n0=0`) | `1 / 100` | `4 / 100` | Logged (`RD-3`) |
| `single_class_benign_only` (`N_k > 500, n1=0`) | `2 / 100` | `0 / 100` | Logged (`RD-3`) |
| **Total single-class reservoirs (`RD-3` permitted, `0` oversampling)** | **`3 / 100`** | **`5 / 100`** (`4` at `cap=500` + `1` at `N_k=74`) | **PASS (`RD-3`)** |

**Exact Single-Class Client Enumeration (`8 / 200` Total):**
- `W1`: `(seed=202, k=4: N=530, 0b/530a -> B=0b/500a)`, `(seed=606, k=4: N=2459, 2459b/0a -> B=500b/0a)`, `(seed=707, k=6: N=2555, 2555b/0a -> B=500b/0a)`.
- `W3`: `(seed=42, k=7: N=74, 0b/74a -> B=0b/74a)`, `(seed=303, k=2: N=77023, 0b/77023a -> B=0b/500a)`, `(seed=303, k=7: N=843, 0b/843a -> B=0b/500a)`, `(seed=505, k=8: N=6480, 0b/6480a -> B=0b/500a)`, `(seed=808, k=6: N=17621, 0b/17621a -> B=0b/500a)`.

---

## 3. `VER-2` Results — Deterministic `SeedSequence` Streams & Clean PSI FAR (`2,000` Client-Rounds / `200` Fleet-Rounds)

**Evidence Status:** `independently verified` (read-only stream generation & covariate PSI check only; does **not** measure live Page-Hinkley FAR or model accuracy).

| Check (`p_min=0.06`, `q_min=3`, `n_bins=5`, `psi_thr=0.25`) | `ToN-IoT W1` | `ToN-IoT W3` | Gate Outcome |
|---|---:|---:|---|
| Determinism (`2×` exact index array match across ref & `S_1..S_10`) | `True` | `True` | **PASS** |
| Pairwise disjointness (`D_val_cal`, `D_val_psi_ref`, `S_1..S_10`, `X_test` untouched) | `True` | `True` | **PASS** |
| `D_val_psi_ref` per-client `min (total / benign / attack)` | `161 / 9 / 150` | `403 / 7 / 396` | **PASS** |
| `S_1..S_10` per-client `min (total / benign / attack)` | `47 / 2 / 45` | `121 / 2 / 119` | **PASS** |
| Empty stream clients / Guard failures (`n < 30` or missing class) | **`0 / 0`** | **`0 / 0`** | **PASS** |
| `stable_control` Client-level PSI FAR (`1,000` client-rounds) | `76 / 1,000` (`7.60% ± 3.34%` SD) | `2 / 1,000` (`0.20% ± 0.42%` SD) | Reported (`RD-5`) |
| `stable_control` Client PSI FA counts per seed (of `100`) | `[5, 3, 11, 5, 6, 12, 12, 5, 7, 10]` | `[0, 0, 0, 0, 0, 1, 0, 0, 0, 1]` | Reported |
| `stable_control` Fleet-level Quorum FAR (`q_min=3`, `100` rounds) | **`4 / 100`** (`4.00% ± 5.16%` SD) | **`0 / 100`** (`0.00% ± 0.00%` SD) | **PASS (`< 10%`)** |
| `stable_control` Fleet `q_min=3` FA counts per seed (of `10`) | `[0, 0, 1, 1, 0, 1, 1, 0, 0, 0]` | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]` | Reported |
| Diagnostic comparator: Fleet FAR at `q_min=2` (not used) | `19 / 100` (`19.0%`) | `0 / 100` (`0.0%`) | Confirms `q_min=3` |
| `gradual_covariate` `R4` (`0.25`) client PSI recall | `100 / 100` (`100%`) | `100 / 100` (`100%`) | **PASS** |
| `abrupt_covariate` `R4` (`1.00`) client PSI recall | `100 / 100` (`100%`) | `100 / 100` (`100%`) | **PASS** |
| `gradual_covariate` continuous ramp monotonicity (`R4 < R5 < R6 < R7`) | `10 / 10` seeds | `10 / 10` seeds | **PASS** |
| `recurring_covariate` `ON` (`R4,5,8,9`) quorum `q_min=3` rate | `40 / 40` (`100%`) | `40 / 40` (`100%`) | **PASS** |
| `recurring_covariate` `OFF` (`R6,7,10`) quorum `q_min=3` FA rate | `2 / 30` (`6.67%`) | `0 / 30` (`0.00%`) | **PASS (`< 10%`)** |

---

## 4. Evidence-Status Separation & Strict Verification Limitations

| Property | Evidence Status | Notes |
|---|---|---|
| `W1` & `W3` split sizes, `W1 ⊂ W3` overlap, `E5: HOLD` | `supported by existing frozen evidence` & `independently verified` | Re-verified live via `load_ton_iot_window()` and Unified Ledger `U-D0-01`–`U-D0-03`. |
| `VER-1` reservoir sizes (`>= 36`), disjointness, determinism, `8/200` single-class counts | `independently verified` | Verified across `200` reservoirs in `task-536`. |
| `VER-2` `SeedSequence` stream guards (`0` fails), clean PSI FAR (`4.0%` W1, `0.0%` W3), drifted PSI recall (`100%`), ramp monotonicity (`10/10`) | `independently verified` | Verified across `2,000` client-rounds in `task-536`. |
| Live Page-Hinkley (`PH`) loss-stream FAR on `stable_control` | **`unverified` (requires model execution)** | Clean PSI FAR is **NOT** live PH FAR; `PH` depends on live `CompactMLP` BCE losses. |
| Live `CompactMLP` `static` Macro-F1 drop below `0.95 * pre_drift` on `abrupt_covariate` | **`unverified` (requires model execution)** | Cannot be inferred from PSI recall alone. |
| `VER-3` CUDA deterministic tolerance (`max_abs_diff <= 1e-6`) across repeated `CompactMLP` runs | **`unverified` (requires Determinism Pilot)** | Must be tested explicitly in authorized `2`-run Determinism Pilot. |
| `C1` attribution, `C2` 4-tier response, `E6` ablation, DP, SecAgg, physical hardware latency, `E5` transfer | **`out of scope`** | Excluded from `EXP-GAP-1` by design. |
