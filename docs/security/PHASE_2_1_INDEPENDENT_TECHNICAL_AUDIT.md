# DA-FIDAF Phase 2.1 — Independent Technical Audit and Research Validation Review

**Audit Scope:** Full read-only source code, configuration, documentation, and mathematical verification of DA-FIDAF Phase 2 (`src/dafidaf/`, `configs/experiments/`, `tests/`, `docs/`).

**Audit Posture:** Independent verification; zero production code modified; all findings empirically reproduced via isolated probes.

---

## 1. Executive Verdict

Phase 2 delivered a clean, modular, zero-new-dependency Python 3.12 research codebase (`38/38` tests passing, zero Gitleaks findings, exact Stage 7 Git baseline preserved). However, an independent line-by-line audit of the actual implementation against its mathematical claims, research methodology, and documentation uncovered **1 CRITICAL**, **6 HIGH**, **8 MEDIUM**, **4 LOW**, and **3 INFORMATIONAL** findings.

Most critically:
1. **`run_experiment_from_yaml` (`src/dafidaf/orchestration/runner.py`) never executes on real datasets** — it silently ignores dataset, grid, drift, poisoning, and ablation YAML fields and unconditionally runs the synthetic toy generator.
2. **`PrivacyAccountant` (`src/dafidaf/privacy/mechanisms.py`) is mathematically invalid outside $\epsilon \le 1$ and omits $\delta$ composition across rounds**, classifying the privacy layer as **Option B (Partial DP implementation requiring remediation before claiming formal DP)**.
3. **A single `NaN` Byzantine client update completely destroys `fedavg`, `krum`, and `multi_krum`**, returning `[nan, nan]`.
4. **`DriftAttackAttributor` is blind to positive-cosine `scaled_update` Byzantine attacks** (classifying a 10x norm explosion as `uncertain_insufficient_evidence`).
5. **The `1.0000` Macro-F1 / ROC-AUC / PR-AUC achieved in synthetic E2E is an artifact of an overly separable Gaussian toy generator ($D_M = 5.004\sigma$, theoretical Bayes accuracy `99.38%`)**, not evidence of IDS effectiveness.

### Final Dimension Verdicts (No Forced Global PASS)

| Dimension | Verdict | Justification |
| --- | --- | --- |
| **Code Correctness** | **CONDITIONAL** | Core modules are clean and pass 38 tests, but edge-case bugs exist in `chronological_split`, `aggregation.py`, `simulators.py`, and `metrics.py`. |
| **Data Engineering Reliability** | **CONDITIONAL** | Core `flow_extract_v1` packet logic and `TrainOnlyPreprocessor` work, but PCAPNG/ZIP container parsing is absent, `embargo=0` disables active-flow exclusion, and missing `ts`/labels silently coerce to `0.0`/attack. |
| **Federated Learning Correctness** | **CONDITIONAL** | FedAvg/FedProx math and `n >= 2f + 3` are sound, but `NaN`/`Inf` updates break Krum/Multi-Krum/FedAvg, and DP clipping in `FederatedTrainer` silently neutralizes Byzantine scaling attacks. |
| **Privacy Assurance** | **HOLD** | **Option B (Partial DP):** Theorem A.1 used outside $\epsilon \le 1$, $\delta$ not composed across rounds, local vs. central DP sensitivity conflated. Secure Aggregation is honestly inactive (`False`). |
| **Drift & Attack Attribution Validity** | **CONDITIONAL** | Zero ground-truth leakage confirmed; PSI/JSD math exact. However, `scaled_update` (10x) is missed (`uncertain`), `random_update` is non-deterministic across processes (`PYTHONHASHSEED`), and `val_loss_delta` documented in spec is absent. |
| **Evaluation Reliability** | **CONDITIONAL** | ROC-AUC tie handling is exact, but PR-AUC is tie-order dependent (`1.0` vs `0.4167`), `paired_effect_size_and_ci` returns `0.0` for constant nonzero improvement, and `n=2` bootstrap CI is marked `statistically_valid=True`. |
| **Security Posture** | **CONDITIONAL** | Zero secrets/leaks, `yaml.safe_load` used, Stage 7 preserved; however, CLI `validate-dataset` omits `allowed_root` (bypassing path-traversal protection) and `runner.py` has 1-second `run_id` collision risk. |
| **Phase 3 Readiness** | **HOLD** | Blocked until P0/P1 items are fixed: real-dataset YAML execution path, `NaN`/`Inf` aggregation sanitization, DP accountant correction, `PYTHONHASHSEED` fix, and CLI path-traversal enforcement. |

---

## 2. Workstream A Findings — Data Engineering

### [A-1] HIGH — `flow_extract.py` Lacks PCAPNG / libpcap / ZIP-Stream Reader Claimed in Docs
- **File & Function:** `src/dafidaf/data/flow_extract.py` (`extract_flows_v1`, lines 81–278) vs. `docs/architecture/DATA_PIPELINE_SPECIFICATION.md`
- **Technical Issue:** `extract_flows_v1` accepts only pre-parsed `(ts_us, packet_index, orig_len, raw_sll_bytes)` tuples. Neither a PCAPNG block reader, a classic libpcap reader, nor a non-extracting ZIP stream reader is implemented in `flow_extract.py`. Additionally, `DATA_PIPELINE_SPECIFICATION.md` documents `15.0s`/`120.0s` timeouts whereas `FlowExtractConfig` uses `120s`/`600s` (matching Phase 1G).
- **Evidence:** Direct inspection of `flow_extract.py` (no `zipfile` import or PCAPNG block parsing). Isolated Probe 8 verified that the core SLL (113) packet-to-flow logic (`0x0003` drop, non-initial fragment drop, bidirectional 5-tuple canonicalization, 120s idle timeout, 1-packet IAT `None`, order determinism) matches Phase 1G fixtures.
- **Research Impact:** Raw PCAPNG flows from `normal_pcaps.zip` cannot be extracted by the production module without adding the container reader.
- **Remediation:** Implement a bounded, read-only PCAPNG/libpcap ZIP-stream packet iterator feeding `extract_flows_v1` (with incomplete trailing block handling) and align `DATA_PIPELINE_SPECIFICATION.md` timeouts to `120s`/`600s`.
- **Required Regression Test:** Fixture test reading synthetic PCAPNG + truncated trailing block bytes directly from an in-memory `zipfile.ZipFile` stream.

### [A-2] HIGH — `chronological_split` Silently Disables Active-Flow Exclusion When `embargo_seconds == 0`
- **File & Function:** `src/dafidaf/data/partitioning.py` (`chronological_split`, lines 109 & 116)
- **Technical Issue:** `if cfg.exclude_active_end_time and (ts + dur) >= val_floor and cfg.embargo_seconds > 0:` disables active-flow exclusion whenever `embargo_seconds == 0.0`.
- **Reproduction (Probe 1):** `ts = [0, 10, ..., 190]`, `durs[13] = 50.0` (starts at `t=130`, ends at `t=180` inside Val) with `TemporalSplitConfig(embargo_seconds=0.0, exclude_active_end_time=True)` -> `13 in res.train_indices == True`, `discarded_active_endtime == 0`.
- **Research Impact:** Sensitivity ablations testing `embargo_seconds=0` suffer silent temporal flow leakage across split boundaries.
- **Remediation:** Remove `and cfg.embargo_seconds > 0` and exclude when `(ts + dur) > t_tr_end` (for Train) and `(ts + dur) > t_va_end` (for Val) whenever `exclude_active_end_time` is `True`.
- **Required Regression Test:** Assert flow `13` in Probe 1 is excluded (`discarded_active_endtime == 1`) when `embargo_seconds == 0.0`.

### [A-3] MEDIUM — Corrupted/Missing Timestamps Coerced to `0.0` and Blank Labels Coerced to Attack (`1`)
- **File & Function:** `src/dafidaf/data/adapters.py` (`TonIoTNetworkAdapter.load`, lines 172–180) and `src/dafidaf/data/schemas.py` (`LabelOntology.to_binary`, lines 39–41)
- **Technical Issue:** Missing/unparseable `ts` silently becomes `0.0` (epoch 1970, forcing a potentially Test-period row into Train). Blank/corrupted `type`/`Label` strings not in `benign_tokens` silently map to `1` (attack).
- **Research Impact:** Silent temporal leakage of corrupted rows into Train and false-positive label corruption.
- **Remediation:** Drop and count rows with missing/invalid `ts` or blank labels (incrementing explicit `dropped_invalid_ts` / `dropped_invalid_label` counters in `LoadedDataset`).
- **Required Regression Test:** CSV fixture with blank `ts` and blank `type` verifying rows are dropped and counted rather than mapped to `ts=0.0` / `label=1`.

### [A-4] MEDIUM — `TrainOnlyPreprocessor` Lacks Documented Re-Fit Guard and Treats `±inf` as Finite
- **File & Function:** `src/dafidaf/data/preprocessing.py` (`fit`, `transform`, lines 44–128)
- **Technical Issue:** `DATA_PIPELINE_SPECIFICATION.md` claims `TrainOnlyPreprocessor` raises `RuntimeError` if re-fitted on `val`/`test`, but `fit()` accepts no split tag and silently overwrites `_state`. Also `is_miss = raw is None or math.isnan(raw)` does not catch `±inf`, clipping `±inf` to `±20.0` instead of imputing.
- **Remediation:** Add `split_name: str = "train"` validation (rejecting non-train splits) and use `not math.isfinite(raw)` for missing/invalid detection.
- **Required Regression Test:** Test `fit(..., split_name="test")` raises `RuntimeError` and `transform([[float("inf")]])` imputes via `fill_values`.

### [A-5] LOW — `flow_extract_v1` IPv6 Extension Headers & `chronological_split` Empty-Split Edge Case
- **File & Function:** `src/dafidaf/data/flow_extract.py` (line 183) & `src/dafidaf/data/partitioning.py` (lines 93–124)
- **Technical Issue:** IPv6 parsing checks `l3[6]` directly without walking extension headers (Hop-by-Hop/Routing/DestOpts). In `chronological_split`, if `embargo_seconds` exceeds the validation time span, `val_idx` silently becomes empty.
- **Remediation:** Add bounded IPv6 extension-header walking (or explicit counter for unsupported extension headers) and raise `ValueError` if `train_idx`, `val_idx`, or `test_idx` is empty.
- **Required Regression Test:** Unit tests for IPv6 extension-header counting and oversized embargo error handling.

---

## 3. Workstream B Findings — Federated Learning

### [B-1] HIGH — `NaN` / `Inf` Client Updates Completely Poison `fedavg`, `krum`, and `multi_krum`
- **File & Function:** `src/dafidaf/federated/aggregation.py` (`_validate_updates`, lines 23–30)
- **Technical Issue:** `_validate_updates` checks list emptiness and dimension only, never `math.isfinite(v)`. Because Python Timsort comparisons with `NaN` always return `False`, a single Byzantine client sending `NaN` breaks Krum/Multi-Krum distance sorting.
- **Reproduction (Probe 2 & 2B):** With 6 honest clients `(0.1+0.01i, 0.2)` and 1 `NaN` Byzantine client placed first in `updates`:
  - `fedavg` -> `[nan, nan]`
  - `krum(num_byzantine=1)` -> **`[nan, nan]`**
  - `multi_krum(num_byzantine=1)` -> **`[nan, nan]`**
- **Research Impact:** Trivially defeats Byzantine-robust aggregation in E4 if a malicious client sends non-finite gradients.
- **Remediation:** Reject or quarantine any `ClientUpdate` containing non-finite (`NaN`/`Inf`) parameters in `_validate_updates` (or filter non-finite updates before aggregation with explicit telemetry).
- **Required Regression Test:** Assert `fedavg`, `coordinate_median`, `trimmed_mean`, `krum`, and `multi_krum` never output `NaN`/`Inf` regardless of client ordering.

### [B-2] HIGH — `FederatedTrainer` Applies DP Clipping *After* `update_hook`, Silently Neutralizing Byzantine Scaling Attacks
- **File & Function:** `src/dafidaf/federated/trainer.py` (`FederatedTrainer.run`, lines 104–112)
- **Technical Issue:** `update_hook` (used for Byzantine injection) runs on line 105, and `add_gaussian_dp_noise` (which clips L2 norm to `max_grad_norm`) runs on lines 106–112 for every client. Under local DP, a malicious Byzantine client would not obey honest client-side clipping; under central DP, server-side clipping is a defense, not an implicit side effect of the hook order.
- **Research Impact:** E4/E6 experiments combining DP and `scaled_update` / `model_replacement` Byzantine attacks will silently clip malicious updates unless the threat model (server-side clipping vs. client-side DP) is made explicit.
- **Remediation:** Separate `dp_mode` (`"server_clip_then_noise"` vs `"client_local_dp"` where malicious hooks execute after local DP) and log `clipped_clients` telemetry.
- **Required Regression Test:** Verify Byzantine `scaled_update` norm is preserved under `"client_local_dp"` and explicitly logged as clipped under `"server_clip_then_noise"`.

### [B-3] MEDIUM — `aggregation.py` Edge Cases (`num_samples=0` Weighting & `num_byzantine < 0`)
- **File & Function:** `src/dafidaf/federated/aggregation.py` (`fedavg` line 36, `multi_krum` line 91)
- **Technical Issue:** `fedavg` uses `max(1, u.num_samples)` (giving a 0-sample client positive weight). `multi_krum` does not reject `num_byzantine < 0`.
- **Remediation:** Reject `num_samples <= 0` in `_validate_updates` and `num_byzantine < 0` in `multi_krum`.
- **Required Regression Test:** Unit tests asserting `AggregationError` for `num_samples=0` and `num_byzantine=-1`.

### [B-4] LOW — `SimulatedClient.train_round` Hardcodes `n_features = len(global_params) - 1` and Non-Atomic Checkpointing
- **File & Function:** `src/dafidaf/federated/client.py` (line 64) and `src/dafidaf/federated/trainer.py` (lines 156–163)
- **Technical Issue:** `len(global_params) - 1` assumes a single-layer linear model with 1 bias scalar, incompatible with Phase 3 multi-layer neural `ModelInterface` models. Checkpoints write directly via `write_text` (non-atomic) without metadata (`n_features`, `config`, `seed`) or a `load_checkpoint` helper.
- **Remediation:** Pass `n_features` explicitly or clone `model` via `ModelInterface`, and write checkpoints atomically (`tmp` -> `os.replace`) with full metadata.

---

## 4. Workstream C Findings — Drift, Adversarial Simulation & Attribution

### [C-1] HIGH — `DriftAttackAttributor` Is Blind to Positive-Cosine `scaled_update` Byzantine Attacks
- **File & Function:** `src/dafidaf/attribution/engine.py` (`DriftAttackAttributor.attribute_round`, lines 114–131)
- **Technical Issue:** Rule 2 (`malicious_model_update`) requires `is_norm_extreme and cos_sim < cfg.cosine_benign_min and not has_feat_drift`. A Byzantine `scaled_update` attack ($\tilde{\Delta} = 10 \cdot \Delta$) has `cos_sim ≈ +1.0 >= 0.10`, so it bypasses all malicious rules and lands in `uncertain_insufficient_evidence`.
- **Reproduction (Probe 4):** 8 honest updates `(0.1, 0.1, 0.1, 0.1)` + 1 `scaled_update` `(1.0, 1.0, 1.0, 1.0)` (`norm_ratio = 10.0`, `cos = 1.0`) -> verdict = **`uncertain_insufficient_evidence`** (missed detection).
- **Research Impact:** E3/E4 attribution recall drops to `0.0` on scaling attacks (which are explicitly listed in `e4_byzantine_robust_agg.yaml`).
- **Remediation:** Add a high-confidence norm-explosion threshold (e.g., `norm_ratio >= cfg.norm_ratio_severe_threshold` such as `6.0` with `not has_feat_drift`, or Z-score/MAD on log-norms across the cohort) so extreme scaling attacks are flagged even when cosine-aligned, without triggering false positives on moderate non-IID norm variance.
- **Required Regression Test:** Probe 4 test asserting 10x `scaled_update` is classified as `malicious_model_update` while honest Dirichlet($\alpha=0.5$) clients keep `FAR == 0.0`.

### [C-2] HIGH — Non-Deterministic Seeding Across Processes in `apply_byzantine_update`
- **File & Function:** `src/dafidaf/attacks/simulators.py` (`apply_byzantine_update`, line 88)
- **Technical Issue:** `rng = random.Random(config.seed + round_id * 97 + hash(update.client_id) % 1000)` uses Python's built-in `hash(str)`, which is salted per process via `PYTHONHASHSEED`.
- **Reproduction (Probe 5):** Identical call with `seed=42` returned `(-1.2248, -0.1186, -0.8791)` under `PYTHONHASHSEED=1` and `(-1.0738, 1.0764, -0.7353)` under `PYTHONHASHSEED=2` (`Identical across processes?: False`).
- **Research Impact:** Breaks cross-run reproducibility for `random_update` Byzantine experiments in E4.
- **Remediation:** Replace `hash(update.client_id)` with deterministic `int.from_bytes(hashlib.blake2b(update.client_id.encode(), digest_size=4).digest(), "big")`.
- **Required Regression Test:** Subprocess test asserting identical `random_update` output under `PYTHONHASHSEED=1` and `PYTHONHASHSEED=2`.

### [C-3] MEDIUM — Documentation-to-Code Drift in Attribution & Page-Hinkley
- **File & Function:** `src/dafidaf/attribution/engine.py`, `src/dafidaf/drift/core.py` (`PageHinkleyDetector`) vs. `docs/architecture/DRIFT_AND_ATTACK_ATTRIBUTION_SPECIFICATION.md`
- **Technical Issue:** The specification documents `val_loss_delta` / `val_loss_poison_delta` in `AttributionEvidence` and an `alpha` parameter in `PageHinkleyDetector`, neither of which exists in code. Additionally, `PageHinkleyDetector` lacks a `reset()` method (once triggered, it stays permanently triggered on recurring drift).
- **Remediation:** Add `PageHinkleyDetector.reset()` and either implement optional server-side `val_loss_delta` probing or remove it from the specification.

### [C-4] INFORMATIONAL — Verified Strengths in Workstream C
- `DriftAttackAttributor.attribute_round()` has **zero access** to hidden attack labels or `malicious_clients` (strict detector/ground-truth separation verified).
- `apply_data_poisoning` and `apply_synthetic_drift` operate strictly on deep-copied in-memory lists; source arrays and disk datasets are never mutated.
- `FeatureDriftDetector` PSI and JSD (in bits) formulas are mathematically exact.

---

## 5. Workstream D Findings — Evaluation & Orchestration

### [D-1] CRITICAL — `run_experiment_from_yaml` Ignores Real Datasets and Experiment Grids, Always Running Synthetic Data
- **File & Function:** `src/dafidaf/orchestration/runner.py` (`run_experiment_from_yaml`, lines 257–275)
- **Technical Issue:** After checking the E5 HOLD gate, `run_experiment_from_yaml` unconditionally calls `run_synthetic_e2e_experiment(...)`, silently ignoring `datasets`, `seeds_multi_run`, `partition_grid`, `dirichlet_alphas`, `drift_interventions`, `poisoning_simulations`, `byzantine`, `ablations`, and `temporal_protocol` defined in `e1`–`e6` YAML configs.
- **Research Impact:** Running `python -m dafidaf.orchestration.cli run-experiment --config configs/experiments/e1_iid_vs_noniid.yaml` produces synthetic toy results while tagging the output `"experiment_id": "E1"`, creating a severe risk of misreporting synthetic runs as ToN-IoT results.
- **Remediation:** Implement a real-dataset experiment dispatcher (using `TonIoTNetworkAdapter`, `CICIoT2023Adapter`, `EdgeIIoTsetAdapter` + `seeds_multi_run` + configured grids) and explicitly tag synthetic runs with `"data_source": "SYNTHETIC_TOY_GENERATOR"` while refusing to run real-dataset YAMLs on synthetic data unless `--synthetic-smoke-test` is explicitly passed.
- **Required Regression Test:** Assert `run_experiment_from_yaml` loads the specified dataset adapter (or fails cleanly when dataset path is missing) and never silently substitutes synthetic data.

### [D-2] MEDIUM — PR-AUC Computation Is Order-Dependent on Tied Prediction Scores
- **File & Function:** `src/dafidaf/evaluation/metrics.py` (`_compute_pr_auc`, lines 56–74)
- **Technical Issue:** `_compute_pr_auc` iterates one sample at a time after `sorted(..., reverse=True)` without grouping tied scores.
- **Reproduction (Probe 6):** For identical constant scores `[0.5, 0.5, 0.5, 0.5]`, `y_true=[1, 1, 0, 0]` yields `pr_auc = 1.0`, whereas `y_true=[0, 0, 1, 1]` yields `pr_auc = 0.416667` (expected: `0.500000` for both!).
- **Remediation:** Group consecutive tied scores into a single threshold step before updating `tp`, `fp`, `rec`, and `prec` (matching `sklearn.metrics.average_precision_score` step-function semantics).
- **Required Regression Test:** Assert `_compute_pr_auc([1,1,0,0], [0.5]*4) == _compute_pr_auc([0,0,1,1], [0.5]*4) == 0.5`.

### [D-3] MEDIUM — `paired_effect_size_and_ci` Returns `0.0` for Constant Nonzero Improvement & `n=2` Bootstrap CI Overclaims Validity
- **File & Function:** `src/dafidaf/evaluation/metrics.py` (`summarize_multi_seed` lines 187–216, `paired_effect_size_and_ci` lines 219–241)
- **Reproduction (Probe 6):**
  - `paired_effect_size_and_ci([0.8, 0.8, 0.8], [0.9, 0.9, 0.9])` returns `{"mean_diff": 0.1, "cohens_d_paired": 0.0, ...}` because `sd == 0.0` falls back to `0.0` instead of `None`/`inf`.
  - `summarize_multi_seed([0.80, 0.90])` marks `statistically_valid = True` even though percentile bootstrap on `n = 2` has only 4 possible resamples (~50% actual coverage, not 95%).
- **Remediation:** Return `None` (undefined/infinite) for `cohens_d_paired` when `sd <= 1e-12 and abs(md) > 1e-12`; require `n >= 3` (ideally `n >= 5` for bootstrap, or use Student-$t$ CI for small $n \ge 3$) before setting `statistically_valid = True`.
- **Required Regression Test:** Unit tests for constant nonzero paired diff and `n=2` returning `statistically_valid=False`.

### [D-4] MEDIUM — CLI Flag & Artifact Naming Mismatches vs. `EXPERIMENT_EXECUTION_GUIDE.md`
- **File & Function:** `src/dafidaf/orchestration/cli.py` vs. `docs/experiments/EXPERIMENT_EXECUTION_GUIDE.md`
- **Technical Issue:** Guide documents `inspect-schema --dataset ton_iot`, `validate-dataset --dataset ton_iot`, and output files `summary.json`/`round_history.json`/`config_snapshot.json`. Actual CLI uses `inspect-schema` (no flags), `validate-dataset --family edge_iiot --csv <path>`, and writes `run_report.json` + `run_report.sha256`.
- **Remediation:** Synchronize CLI flags and documentation so every documented command executes verbatim.

---

## 6. Privacy Assurance Assessment

### Classification: **Option B — Partial DP Implementation Requiring Validation & Mathematical Remediation**

Do **NOT** claim formal $(\epsilon, \delta)$-Differential Privacy from the current implementation.

### [P-1] HIGH — Invalid Gaussian Mechanism Domain ($\epsilon > 1$) and Missing $\delta$ Composition
- **File & Function:** `src/dafidaf/privacy/mechanisms.py` (`PrivacyAccountant.step`, lines 73–83; `summary`, lines 85–99)
- **Technical Issue:**
  1. Uses classical Dwork & Roth Theorem A.1 (`eps_round = sqrt(2 * ln(1.25 / delta)) / sigma`), which is **mathematically valid ONLY when $\epsilon_{\text{round}} \le 1.0$** ($\sigma \ge 4.845$ at $\delta = 10^{-5}$). At `sigma = 0.5` (Probe 3), `eps_round = 9.69 >> 1.0` — outside the theorem's domain.
  2. Basic composition of $T$ $(\epsilon, \delta)$-DP rounds yields **$(T\epsilon, T\delta)$**, not $(T\epsilon, \delta)$. `summary()` composes $\epsilon$ across $T=5$ rounds (`48.448`) while reporting uncomposed `delta = 1e-5` instead of `5e-5`.
  3. Does not validate `0 < delta < 1` (`delta=0` raises `ZeroDivisionError`; `delta >= 1.25` raises `ValueError`).
  4. Conflates per-client local Gaussian noise (`trainer.py` line 107) with central FedAvg sensitivity (where sample-weighted averaging $w_i = n_i / N$ changes L2 sensitivity per client).
  5. Uses non-cryptographic `random.Random` (Mersenne Twister) — acceptable for **reproducible simulation** only, must be disclosed as `simulation_only_prng`.
  6. `FEDERATED_LEARNING_SPECIFICATION.md` inaccurately describes `PrivacyAccountant` as "RDP-style" whereas code implements basic composition.
- **Remediation:** Implement exact Analytic Gaussian Mechanism (Balle & Wang 2018) or Rényi Differential Privacy (RDP) accounting (Mironov 2017) with explicit `delta` validation, proper composition (both $\epsilon$ and $\delta$), explicit local-vs-central DP mode, and `simulation_only_prng: True` disclosure.
- **Required Regression Test:** Verify `PrivacyAccountant` rejects invalid `delta`, composes `delta` (or uses exact RDP-to-$(\epsilon,\delta)$ conversion), and matches reference RDP values across $\sigma \in \{0.5, 1.0, 2.0, 5.0\}$.

### Secure Aggregation Verification: **PASS (Honest Disclosure)**
- `SecureAggregationInterface` is an abstract base class with `SecureAggregationNotImplementedError`.
- `PrivacyAccountant.summary()` explicitly emits `"secure_aggregation_active": False`.
- No code or telemetry misrepresents Secure Aggregation as active.

---

## 7. Security Findings

### [S-1] HIGH — CLI `validate-dataset` Bypasses Path-Traversal Guard
- **File & Function:** `src/dafidaf/orchestration/cli.py` (lines 57–59)
- **Technical Issue:** Calls `adapters[args.family].load(Path(args.csv), max_rows=args.max_rows, compute_sha256=False)` without passing `allowed_root=load_config().paths.dataset_root.path`, neutralizing `_validate_safe_path()`'s root containment check.
- **Remediation:** Pass `allowed_root=load_config().paths.dataset_root.path` in `cli.py` (with explicit error if `dataset_root` is unconfigured).
- **Required Regression Test:** CLI test passing a CSV path outside `DAFIDAF_DATA_ROOT` asserting `DatasetAdapterError` / non-zero exit.

### [S-2] MEDIUM — Non-Validated YAML Root Type & 1-Second `run_id` Directory Collision
- **File & Function:** `src/dafidaf/orchestration/runner.py` (lines 217–224, 261–262)
- **Technical Issue:** Empty or non-mapping YAML causes unhandled `AttributeError` on `cfg.get(...)`. Running two experiments with the same seed within 1 second crashes on `run_dir.mkdir(exist_ok=False)`.
- **Remediation:** Validate `isinstance(cfg, dict)` (raising `ValueError`) and include microsecond or short UUID suffix in `run_id`.

### [S-3] INFORMATIONAL — Verified Security Controls
- Zero `eval`/`exec`/`pickle`/`yaml.load` calls in `src/dafidaf/`.
- Zero hardcoded host drive letters in `src/dafidaf/` (verified by `test_no_hardcoded_drive_letters_in_source_code`).
- Zero secrets leaked (`gitleaks dir` and `gitleaks git --staged` both `0` leaks).
- Stage 7 Git baseline (`22` staged files, `84,102` bytes, `0` commits, `0` remotes) 100% intact.

---

## 8. Research Validity Assessment

### Why Did Synthetic E2E Achieve `1.0000` Across All Classification Metrics?
In `generate_synthetic_iot_dataset()` (`runner.py` lines 59–65), classes `y=1` and `y=0` are drawn from isotropic Gaussians with means `+1.6` and `-1.0` ($\Delta\mu = 2.6$) and $\sigma = 0.9$ across 3 independent features:
$$D_M = \sqrt{3} \cdot \frac{2.6}{0.9} \approx 5.0037\sigma \implies \text{Bayes Error} = \Phi(-D_M / 2) \approx 0.00618 \quad (99.38\% \text{ Bayes accuracy})$$
On `n_test = 151`, expected errors are `< 1` sample, so **any linear classifier trivially achieves `1.0` Macro-F1 / ROC-AUC / PR-AUC**.

- **Conclusion:** The synthetic E2E pipeline is a valid **software integration smoke test** (proving modules connect end-to-end without crashing), **NOT** a realistic benchmark or research evidence.
- **Additional Research Validity Gaps:**
  - `uncertain_rate = 0.40` (4 of 10 clients abstained) even on clean synthetic data; threshold calibration on real non-IID ToN-IoT traffic is required before E3/E4 claims.
  - `e6_ablation_overhead.yaml` has `status: PASS` while `e1`–`e4` have `status: CONDITIONAL`, yet none have been executed on real datasets (all should be `CONDITIONAL` until real runs execute).

---

## 9. Prioritized Remediation Summary

See the companion [PHASE_2_1_REMEDIATION_PLAN.md](file:///I:/Projects/da-fidaf/docs/architecture/PHASE_2_1_REMEDIATION_PLAN.md) for the exact step-by-step P0/P1/P2/P3 plan and regression test matrix.

---

## 10. Phase 3 Readiness Decision

**Decision: `HOLD` (Blocked Pending Phase 2.2 Remediation Sprint)**

Phase 3 real-dataset experiments (E1–E4, E6) MUST NOT start until the following **6 P0/P1 blockers** are resolved and regression-tested:
1. **[D-1] CRITICAL:** Wire real-dataset execution and multi-seed/grid dispatch into `run_experiment_from_yaml` (never silently fall back to synthetic data).
2. **[P-1] HIGH:** Fix `PrivacyAccountant` (RDP / Analytic Gaussian mechanism + $\delta$ validation/composition + local-vs-central DP clarity) and fix `FederatedTrainer` DP-vs-Byzantine ordering **[B-2]**.
3. **[B-1] HIGH:** Reject/quarantine `NaN`/`Inf` client updates in `aggregation.py` before Krum/Multi-Krum/FedAvg.
4. **[C-1] HIGH:** Fix `DriftAttackAttributor` blind spot to positive-cosine `scaled_update` Byzantine attacks.
5. **[C-2] HIGH:** Replace `hash(update.client_id)` with deterministic `blake2b` in `apply_byzantine_update`.
6. **[A-2] & [S-1] HIGH:** Fix `chronological_split` active-flow exclusion when `embargo_seconds == 0`, and enforce `allowed_root` in `cli.py validate-dataset`.
