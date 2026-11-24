# DA-FIDAF Phase 3A.1 — E2 Pilot Diagnostic Audit

**Audited Artifacts (`I:\Projects\da-fidaf-runs`):**
- `20261124T063041_393734Z_phase3a_e2_abrupt_seed42_f4114d`
- `20261124T063041_416735Z_phase3a_e2_gradual_seed42_be98db`

**Diagnostic Figures:** `I:\Projects\da-fidaf-runs\figures\phase3a_diagnostics\fig_E2_01_drift_timeline.*`, `fig_E2_02_replay_adaptation.*`

---

## 1. Strict Three-Way Separation of Drift Evidence

| Category | Measured Window / Intervention | Observed Max PSI | Detected (`>= 0.25`) | Scientific Interpretation |
| --- | --- | --- | --- | --- |
| **1. Natural Temporal Distribution** | `Network_dataset_23.csv` Train -> Val (`300s` gap) | `0.233838` (`duration`) | `False` | Stationary within 36-minute window (`9/10` features `<= 0.0305`) |
| **1. Natural Temporal Distribution** | `Network_dataset_23.csv` Train -> Test (`300s` gap) | `0.077528` (`duration`) | `False` | Stationary within 36-minute window (`9/10` features `<= 0.000002`) |
| **2. Capture-Confounded Cross-Shard** | Period A (`Shard 1` normal) -> Period B (`Shard 23` normal) | `10.364964` | `True` | **CONFOUNDED by 18-day gap (Apr 5–22) & capture changes** — NOT proof of organic benign concept drift |
| **3. Controlled Synthetic Intervention** | `abrupt` (`onset=3, severity=1.5, is_synthetic=True`) | `R1-2: 0.234`, `R3: 8.116`, `R4: 8.154`, `R5: 7.311` | `True` (from R3) | Step-function synthetic covariate shift verified |
| **3. Controlled Synthetic Intervention** | `gradual` (`onset=3, dur=3, severity=1.5, is_synthetic=True`) | `R1-2: 0.234`, `R3: 2.844`, `R4: 5.568`, `R5: 7.311` | `True` (from R3) | Linearly ramping synthetic covariate shift verified |

---

## 2. Diagnostic Findings

1. **Timestamp Provenance:** `Network_dataset_23.csv` has valid Unix epoch timestamps (`0` invalid `ts`), supporting genuine within-window chronological ordering. However, a 15k-row prefix spans only `36 minutes` (`2,154s`), which is too short to observe natural multi-day attack emergence and fails under `900s` embargo.
2. **Per-Feature PSI & False-Positive Check:** Within-shard natural PSI was concentrated entirely in `duration` (`0.2338` Val, `0.0775` Test), staying cleanly below the `0.25` threshold (`0` false positives). Note that `0.2338` is close to `0.25`; Phase 3B should evaluate threshold sensitivity (`0.20, 0.25, 0.35`) and multi-round persistence (Page-Hinkley) to guard against single-window false alarms.
3. **Why Abrupt & Gradual Matched at Round 5:** At `onset_round = 3, duration_rounds = 3`, gradual intensity is `min(1.0, (round - 3 + 1) / 3)`, reaching `0.333` (R3, PSI `2.844`), `0.667` (R4, PSI `5.568`), and `1.000` (R5, PSI `7.311`), matching abrupt at R5. Phase 3B E2 must log per-round PSI trajectories and detection latency across all rounds.
4. **Replay Adaptation & Forgetting:** Under synthetic covariate shift (`R5`), `ContinualAdapter(strategy="replay", epochs=2, lr=0.05)` reduced drifted validation BCE loss from `0.3981` to `0.3044` (`-23.5%`) while improving prior-replay BCE loss (`forgetting_delta = -0.0377`, zero catastrophic forgetting).
