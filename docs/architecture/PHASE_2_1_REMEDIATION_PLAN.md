# DA-FIDAF Phase 2.1 — Prioritized Remediation Plan (Phase 2.2 Sprint)

This plan sequences every finding from [PHASE_2_1_INDEPENDENT_TECHNICAL_AUDIT.md](file:///I:/Projects/da-fidaf/docs/security/PHASE_2_1_INDEPENDENT_TECHNICAL_AUDIT.md) into concrete, testable engineering tasks required to unblock **Phase 3 (Real-Dataset Experiments E1–E4, E6)**.

---

## Priority Tiers & Exit Gate

- **P0 (CRITICAL — Immediate Phase 3 Blocker):** Must be fixed before running any real-dataset experiment.
- **P1 (HIGH — Phase 3 Blocker):** Must be fixed before publishing or trusting FL, DP, Byzantine, or attribution metrics.
- **P2 (MEDIUM — Pre-Benchmark Quality):** Should be fixed in the same Phase 2.2 sprint before multi-seed sweeps.
- **P3 (LOW — Architecture Polish):** Can be completed in Phase 2.2 or early Phase 3.

**Phase 3 Unblock Gate:** All **P0 + P1** items fixed, all new regression tests passing, `ruff check` + `pytest` + `gitleaks` + `repo_guard` exit `0`, and Stage 7 Git baseline preserved.

---

## P0 — Critical Blockers

### 1. [D-1] Implement Real-Dataset Execution Path in `run_experiment_from_yaml`
- **Target:** `src/dafidaf/orchestration/runner.py` (`run_experiment_from_yaml`)
- **Action:**
  - Parse `datasets.primary`, `seeds_multi_run`, `temporal_protocol`, `federation`, `drift_interventions`, `poisoning_simulations`, `byzantine`, and `ablations` from YAML.
  - Load real CSVs via `TonIoTNetworkAdapter` / `CICIoT2023Adapter` / `EdgeIIoTsetAdapter` bounded to `DAFIDAF_DATA_ROOT`.
  - Never silently substitute `generate_synthetic_iot_dataset()` when running a real-dataset YAML; require an explicit `--synthetic-smoke-test` flag for synthetic runs and stamp `"data_source": "SYNTHETIC_TOY_GENERATOR"` in synthetic outputs.
  - Validate `isinstance(cfg, dict)` before calling `cfg.get(...)` (also fixes **[S-2]** YAML validation).
- **Regression Test:** `test_run_experiment_from_yaml_refuses_silent_synthetic_fallback` & `test_run_experiment_from_yaml_loads_real_adapter_fixture`.

---

## P1 — High Blockers

### 2. [B-1] Sanitize Non-Finite (`NaN`/`Inf`) Updates in All Aggregators
- **Target:** `src/dafidaf/federated/aggregation.py` (`_validate_updates`)
- **Action:**
  - Validate `all(math.isfinite(v) for v in u.delta_params)` for every `ClientUpdate`.
  - Either raise `AggregationError` (strict mode) or filter out non-finite updates before aggregation (returning filtered client IDs in telemetry) so `fedavg`, `coordinate_median`, `trimmed_mean`, `krum`, and `multi_krum` can never output `NaN`/`Inf`.
- **Regression Test:** `test_nan_and_inf_byzantine_updates_never_poison_krum_or_median` (testing `NaN` at index `0` and index `-1`).

### 3. [P-1] Replace Invalid Gaussian Theorem A.1 Formula with Exact RDP Accounting
- **Target:** `src/dafidaf/privacy/mechanisms.py` (`DPConfig`, `PrivacyAccountant`)
- **Action:**
  - Validate `0.0 < delta < 1.0`, `max_grad_norm > 0.0`, `noise_multiplier >= 0.0`.
  - Implement Rényi Differential Privacy (RDP) Gaussian mechanism accounting across orders $\alpha \in \{2, \dots, 64\}$ with exact additive RDP composition across rounds and standard RDP-to-$(\epsilon, \delta)$ conversion (valid for all $\sigma > 0$, not restricted to $\epsilon \le 1$).
  - Explicitly record `dp_scope` (`"local_per_client"` vs `"central_aggregate"`), `prng_mode: "simulation_only_mersenne_twister"`, and `secure_aggregation_active: False`.
- **Regression Test:** `test_rdp_accountant_valid_at_sigma_0_5_and_rejects_invalid_delta`.

### 4. [B-2] Decouple DP Clipping Order from Byzantine `update_hook`
- **Target:** `src/dafidaf/federated/trainer.py` (`FederatedTrainer.run`)
- **Action:**
  - Make DP placement explicit via `DPConfig.mode` (`"server_side_clip_and_noise"` vs `"client_side_local_dp"`).
  - Under `"client_side_local_dp"`, apply DP to honest client updates *before* invoking the Byzantine `update_hook` so malicious clients are not artificially forced to obey honest client-side clipping.
- **Regression Test:** `test_byzantine_scaling_preserved_under_client_local_dp`.

### 5. [C-1] Close `DriftAttackAttributor` Blind Spot to Positive-Cosine `scaled_update` Attacks
- **Target:** `src/dafidaf/attribution/engine.py` (`AttributionConfig`, `DriftAttackAttributor.attribute_round`)
- **Action:**
  - Add `norm_ratio_severe_threshold: float = 6.0` (or cohort MAD-based norm outlier check) so extreme norm explosions without corroborating feature drift (`not has_feat_drift`) are classified as `malicious_model_update` even when `cos_sim >= cosine_benign_min`.
  - Calibrate thresholds against both Dirichlet($\alpha=0.5$) non-IID honest clients and `scaled_update` attacks.
- **Regression Test:** `test_attributor_detects_10x_positive_cosine_scaled_update_with_zero_far`.

### 6. [C-2] Eliminate `PYTHONHASHSEED` Non-Determinism in `apply_byzantine_update`
- **Target:** `src/dafidaf/attacks/simulators.py` (`apply_byzantine_update`, line 88)
- **Action:** Replace `hash(update.client_id)` with deterministic `int.from_bytes(hashlib.blake2b(update.client_id.encode("utf-8"), digest_size=4).digest(), "big")`.
- **Regression Test:** Subprocess test confirming identical `random_update` output under `PYTHONHASHSEED=1` and `PYTHONHASHSEED=2`.

### 7. [A-2] Fix `chronological_split` Active-Flow Exclusion When `embargo_seconds == 0`
- **Target:** `src/dafidaf/data/partitioning.py` (`chronological_split`, lines 109 & 116)
- **Action:** Remove `and cfg.embargo_seconds > 0`; enforce `(ts + dur) > t_tr_end` (for Train) and `(ts + dur) > t_va_end` (for Val) whenever `exclude_active_end_time=True`.
- **Regression Test:** `test_active_flow_exclusion_enforced_when_embargo_is_zero`.

### 8. [S-1] Enforce `allowed_root` Path-Traversal Guard in CLI `validate-dataset`
- **Target:** `src/dafidaf/orchestration/cli.py` (`main`, lines 51–59)
- **Action:** Pass `allowed_root=load_config().paths.dataset_root.path` to `adapters[args.family].load(...)`.
- **Regression Test:** `test_cli_validate_dataset_blocks_path_outside_dataset_root`.

### 9. [A-1] Implement Read-Only PCAPNG/libpcap ZIP-Stream Reader for `flow_extract_v1`
- **Target:** `src/dafidaf/data/flow_extract.py`
- **Action:** Add a streaming PCAPNG/libpcap reader supporting `zipfile.ZipFile.open()` (no disk extraction) with explicit incomplete-trailing-block counting, feeding `extract_flows_v1`. Update `DATA_PIPELINE_SPECIFICATION.md` timeouts to `120s`/`600s`.
- **Regression Test:** `test_flow_extract_v1_reads_pcapng_from_zip_stream_and_handles_truncated_tail`.

---

## P2 — Medium Quality & Metric Fixes

| ID | File | Fix | Regression Test |
| --- | --- | --- | --- |
| **[D-2]** | `src/dafidaf/evaluation/metrics.py` | Group tied scores at each threshold in `_compute_pr_auc` | `test_pr_auc_invariant_to_tie_ordering` |
| **[D-3]** | `src/dafidaf/evaluation/metrics.py` | Return `None` for `cohens_d_paired` when `sd==0` & `md!=0`; require `n >= 3` for `statistically_valid` | `test_paired_effect_constant_diff_and_n2_ci_flag` |
| **[A-3]** | `src/dafidaf/data/adapters.py`, `schemas.py` | Drop & count rows with missing `ts` or blank labels instead of coercing to `0.0` / `1` | `test_adapter_drops_invalid_ts_and_blank_labels` |
| **[A-4]** | `src/dafidaf/data/preprocessing.py` | Add `split_name` guard against val/test re-fit; treat `±inf` via `not math.isfinite()` | `test_preprocessor_rejects_test_refit_and_sanitizes_inf` |
| **[B-3]** | `src/dafidaf/federated/aggregation.py` | Reject `num_samples <= 0` and `num_byzantine < 0` with `AggregationError` | `test_aggregator_rejects_zero_samples_and_negative_f` |
| **[C-3]** | `src/dafidaf/drift/core.py` & docs | Add `PageHinkleyDetector.reset()` and synchronize `DRIFT_AND_ATTACK_ATTRIBUTION_SPECIFICATION.md` | `test_page_hinkley_reset_for_recurring_drift` |
| **[S-2]** | `src/dafidaf/orchestration/runner.py` | Add microsecond/UUID suffix to `run_id` to eliminate 1-second collisions | `test_concurrent_same_second_runs_do_not_collide` |
| **[D-4]** | `docs/experiments/EXPERIMENT_EXECUTION_GUIDE.md` & `configs/experiments/e6_ablation_overhead.yaml` | Synchronize CLI flags/filenames with `cli.py` and set `e6` status to `CONDITIONAL` until real runs execute | CLI doc smoke check |

---

## P3 — Low / Phase 3 Architecture Polish

- **[A-5]** Add bounded IPv6 extension-header handling in `flow_extract.py` and empty-split validation in `chronological_split`.
- **[B-4]** Decouple `SimulatedClient.train_round` from `len(global_params) - 1` so multi-layer PyTorch models plug cleanly into `ModelInterface`; add atomic checkpoint writes and `load_checkpoint`.
- Add a harder, realistic non-linear synthetic benchmark generator (e.g., overlapping distributions $D_M \approx 1.5\sigma$ + class imbalance `95:5`) alongside the smoke-test generator so synthetic tests exercise non-trivial F1/PR-AUC/FPR regimes.
