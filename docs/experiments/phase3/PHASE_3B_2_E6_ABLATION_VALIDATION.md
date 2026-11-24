# DA-FIDAF Phase 3B.2 — E6 Genuine Attribution Ablation Validation (Workstream C)

- **Code Change:** Added closed-loop `attribution_filter` hook and `quarantined_attributed_clients` telemetry to `FederatedTrainer` (`src/dafidaf/federated/trainer.py`). Verified by unit test `test_genuine_attribution_ablation_code_isolation` (`tests/unit/test_phase3b_2_remediation.py`).
- **Artifacts:** `20` matched-seed runs (`10` W1 + `10` W3; `5` seeds `[42, 101, 202, 303, 404]`; `FedAvg` under `sign_flip` attack `f=2/10`) under `I:\Projects\da-fidaf-runs\phase3b_2\runs\e6_v2\` (sample run IDs: `20261124T083521_956901Z_e6v2_w1_full_dafidaf_closed_loop_seed42_78b4a4`, `20261124T083644_236706Z_e6v2_w1_without_attribution_genuine_seed42_0ebd8f`, `20261124T083829_133583Z_e6v2_w3_full_dafidaf_closed_loop_seed42_9a9e4e`, `20261124T084142_146699Z_e6v2_w3_without_attribution_genuine_seed42_5fb774`).

---

## 1. Code-Level Isolation Verification

| Verification Check | `full_dafidaf_closed_loop` | `without_attribution_genuine` |
| --- | --- | --- |
| `attribution_calls_executed` (per 6-round run) | `6` | **`0`** |
| `quarantined_attributed_clients` (mean across 60 client-rounds) | `27.2` (W1) / `24.8` (W3) | **`0.0`** (W1 & W3) |
| Alters aggregated model parameters? | **YES** (verified in unit test & live runs) | **NO** |

---

## 2. Measured Ablation Outcomes (`n = 5` Matched Seeds)

| Window & Variant | Cal Macro-F1 (Mean ± SD) | ROC-AUC (Mean ± SD) | Mean Quarantined Client-Rounds | Wall Time (s) |
| --- | --- | --- | --- | --- |
| **W1 `full_dafidaf_closed_loop`** | **`0.7493 ± 0.097`** | **`0.4320 ± 0.341`** | `27.2 / 60` (`45.3%`) | `16.54` |
| **W1 `without_attribution_genuine`** | `0.6256 ± 0.202` | `0.3646 ± 0.268` | `0.0 / 60` (`0.0%`) | `16.03` |
| **W3 `full_dafidaf_closed_loop`** | `0.4200 ± 0.008` | **`0.8257 ± 0.015`** | `24.8 / 60` (`41.3%`) | `38.11` |
| **W3 `without_attribution_genuine`** | `0.5380 ± 0.175` | `0.6294 ± 0.222` | `0.0 / 60` (`0.0%`) | `36.25` |

- **Paired Tests (`full_closed_loop` vs `without_attribution_genuine`, `n = 5`):**
  - W1 Macro-F1: `mean_diff = +0.1237` (`d_z = +0.505`), Student-$t$ 95% CI `[-0.1806, +0.4280]` (not significant at `n=5`).
  - W3 ROC-AUC: `mean_diff = +0.1963` (`d_z = +0.907`), Bootstrap 95% CI `[+0.0262, +0.3643]` (significant) vs. **Student-$t$ ($df=4$) 95% CI `[-0.0726, +0.4653]` (NOT significant — conclusion changed!)**.
- **Critical Over-Quarantine Disclosure:** Inspecting `quarantined_per_round` (e.g., W1 seed 42 rounds 3–6: `['sim_gw_01', 'sim_gw_02', 'sim_gw_04', 'sim_gw_07', 'sim_gw_10']`) confirms that while both true attackers (`sim_gw_01`, `sim_gw_02`) were excluded, `2–3` honest Non-IID clients were also falsely quarantined every round (`41%–45%` total quarantine rate vs `20%` attacker rate).
