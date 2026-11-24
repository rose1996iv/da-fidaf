# Attribution-Guided, Risk-Aware Robust Aggregation

- **Implementation Modules:** `src/dafidaf/federated/aggregation.py`, `src/dafidaf/federated/trainer.py`
- **Related Reports:** [Phase 3B E4 Results](../experiments/phase3/PHASE_3B_E4_RESULTS.md), [Phase 3B.2 E6 Ablation Validation](../experiments/phase3/PHASE_3B_2_E6_ABLATION_VALIDATION.md)

---

## 1. Draft Risk-Aware Action Policy vs. Current Implementation

The latest draft architecture diagrams define four graduated aggregation responses derived from Drift–Attack Attribution verdicts:

| Attribution Verdict | Draft Policy Action | Current Codebase Support |
| --- | --- | --- |
| `Benign Drift` | **Accept** (and trigger drift adaptation feedback) | Implemented (accepted into aggregation) |
| `Uncertain` | **Downweight** or **Hold** for multi-round verification | **Not yet implemented** (currently accepted unless flagged `malicious_*`) |
| `Malicious` | **Quarantine** (exclude from aggregation round) | **Implemented in Phase 3B.2** via `FederatedTrainer` `attribution_filter` hook |

---

## 2. Implemented Robust Aggregators (`aggregation.py`)

- `FedAvg` (sample-weighted mean baseline)
- `FedProx` (proximal local objective + weighted averaging)
- `Coordinate Median`
- `Trimmed Mean`
- `Multi-Krum`

---

## 3. Closed-Loop Quarantine Validation (Phase 3B.2 Workstream C)

Code-level isolation was verified by `test_genuine_attribution_ablation_code_isolation` and `20` matched-seed live runs (`FedAvg`, `sign_flip` attack with `f=2/10` compromised clients, `n=5` seeds):

| Window & Variant | Cal Macro-F1 (Mean ± SD) | ROC-AUC (Mean ± SD) | Mean Quarantined Client-Rounds |
| --- | ---: | ---: | ---: |
| **W1 `full_dafidaf_closed_loop`** | `0.7493 ± 0.097` | `0.4320 ± 0.341` | `27.2 / 60` (`45.3%`) |
| **W1 `without_attribution_genuine`** | `0.6256 ± 0.202` | `0.3646 ± 0.268` | `0.0 / 60` (`0.0%`) |
| **W3 `full_dafidaf_closed_loop`** | `0.4200 ± 0.008` | `0.8257 ± 0.015` | `24.8 / 60` (`41.3%`) |
| **W3 `without_attribution_genuine`** | `0.5380 ± 0.175` | `0.6294 ± 0.222` | `0.0 / 60` (`0.0%`) |

!!! warning "Benign-Client Over-Quarantine & Statistical Power Caveats"
    1. **Over-Quarantine:** While both true attackers (`sim_gw_01`, `sim_gw_02`) were excluded, `2–3` honest Non-IID clients were also falsely quarantined per round (`41%–45%` total quarantine rate vs. `20%` true attacker rate).
    2. **Statistical Significance (`n=5`):** Under exact paired Student-$t$ ($df=4$), the W3 ROC-AUC gain (`+0.1963`, 95% CI `[-0.0726, +0.4653]`) is **not statistically significant**, flipping from the anti-conservative bootstrap CI (`[+0.0262, +0.3643]`).
    3. **Adaptive Adversaries:** Adaptive Byzantine attacks (ALIE, Min-Max) have not yet been evaluated (`GAP-07`).
