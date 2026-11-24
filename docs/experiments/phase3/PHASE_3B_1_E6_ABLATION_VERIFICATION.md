# DA-FIDAF Phase 3B.1 — E6 Independent Ablation & Systems Overhead Verification

- **Scope:** All `50` E6 raw `run_report.json` files (`25` W1 + `25` W3; `5` ablation variants × `5` seeds; Non-DP baseline ONLY).
- **CM-to-Metric & Non-DP Verification:** `0 / 50` CM-to-metric discrepancies; `dp_enabled == False` and `secure_aggregation_active == False` verified in `50 / 50` raw JSONs.

---

## Finding [AUD-05] — MEDIUM: `without_attribution` Is a No-Op on Utility & `without_drift_detection` Aliases `without_continual_adaptation`

- **Finding ID:** `AUD-05` | **Severity:** `MEDIUM` (Ablation Design Limitation)
- **Evidence File:** `I:\Projects\da-fidaf-runs\scripts\phase3b\run_phase3b_e3_e4_e6.py` (lines 285–355) & `I:\Projects\da-fidaf-runs\phase3b\e6\*`
- **Verification Method:** Audited ablation branching code and compared per-seed `test_metrics_val_calibrated` across all `5` ablations.
- **Original Reported vs. Independently Verified Values:**
  - `full_dafidaf` vs. `without_attribution`: Identical Macro-F1 on every seed (`0.6629 ± 0.0828` W1; `0.4245 ± 0.0016` W3). Why? `attributor.attribute_round()` is invoked *after* `trainer.run()` solely for logging, without quarantining or down-weighting attributed clients during aggregation!
  - `without_drift_detection` vs. `without_continual_adaptation`: Identical Macro-F1 on every seed (`0.5631 ± 0.0507` W1; `0.5520 ± 0.1838` W3). Why? Because continual adaptation is nested inside `if abl != "without_drift_detection":`, removing drift detection also suppresses adaptation.
- **Scientific Implication:** E6 validly measures the impact of **robust aggregation** (`without_robust_aggregation`: W3 F1 drops `0.4245 -> 0.3649`, SD rises `66x`) and the **combined drift-detection + continual-adaptation loop** (W1 F1 drops `0.6629 -> 0.5631`), but it does **NOT** yet measure closed-loop attribution-driven quarantine utility.
- **Recommended Action:** Wire `DriftAttackAttributor` decisions into round-level client weighting/quarantine in Phase 4 and test an unconditional-adaptation arm to separate drift detection from continual adaptation.

---

## Systems Overhead & Hardware Measurement Audit

- **Communication Bytes Verified:** `1,920 B/round` (`11,520 B` total, W1: 12 float64 params × 8 B × 10 clients × 2 directions) and `1,760 B/round` (`10,560 B` total, W3: 11 float64 params — W3 has 0 missing-value indicators because `W3` had 0 missing features!).
- **Model Size Verified:** `96 bytes` (W1, 12 float64) / `88 bytes` (W3, 11 float64).
- **Timing & Memory Methodology Caveat:** Wall-clock time (`15.0s` W1, `35.0s` W3), inference latency (`6.1–7.8 ms / 1k` flows), and `tracemalloc` peak memory (`13.53 MB` W1, `30.87 MB` W3) were measured on a single desktop Windows Python 3.12 host without dedicated warm-up isolation or hardware energy profiling. **These simulated-gateway timings MUST NOT be generalized to physical resource-constrained IoT hardware (e.g., Raspberry Pi / ESP32 / ARM Cortex-M).**
