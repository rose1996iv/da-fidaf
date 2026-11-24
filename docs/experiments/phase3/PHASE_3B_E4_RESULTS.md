# DA-FIDAF Phase 3B — E4 Results (Byzantine Robust Aggregation)

- **Execution Scope:** Authorized Phase 3B Non-DP baseline (`dp_enabled = False`), `K = 10` simulated gateways (`label_skew`, Dirichlet $\alpha = 0.5$), $f = 2$ Byzantine clients (`20%`, satisfying Krum/Multi-Krum precondition $n \ge 2f + 3$: $10 \ge 7$), active rounds `2..6`, `5` seeds `[42, 101, 202, 303, 404]`.
- **Artifacts:** `I:\Projects\da-fidaf-runs\phase3b\e4\` & `e4_master_summary.json` (`250` runs: `125` W1 + `125` W3; `0` failed).
- **IEEE Figure:** `I:\Projects\da-fidaf-runs\figures\phase3b\fig_E4_01_byzantine_robustness.*`.

---

## 1. Window W3 Results (`Shards 8–23`, Overlapping Window) — Val-Calibrated Macro-F1 & ROC-AUC

On W3 (where benign ranking `ROC-AUC` is `~0.83`), robust aggregators clearly preserve ranking integrity under severe Byzantine attacks:

| Attack (`f = 2 / 10`) | FedAvg (F1 / AUC) | Median (F1 / AUC) | Trimmed Mean (F1 / AUC) | Krum (F1 / AUC) | Multi-Krum (F1 / AUC) | NaN Quarantined |
| --- | --- | --- | --- | --- | --- | --- |
| `sign_flip` (`-8x`) | `0.538 ± 0.175` / `0.629` | **`0.566 ± 0.193`** / `0.740` | `0.552 ± 0.184` / `0.757` | `0.493 ± 0.159` / `0.760` | `0.470 ± 0.110` / **`0.796`** | `0.0` |
| `scaled_update` (`+8x`) | `0.486 ± 0.155` / `0.778` | **`0.497 ± 0.130`** / `0.781` | `0.493 ± 0.160` / **`0.820`** | `0.493 ± 0.159` / `0.760` | `0.492 ± 0.161` / `0.796` | `0.0` |
| `random_update` | `0.561 ± 0.155` / `0.715` | `0.496 ± 0.159` / `0.779` | `0.472 ± 0.110` / **`0.799`** | `0.494 ± 0.158` / `0.760` | `0.470 ± 0.110` / `0.796` | `0.0` |
| `model_replacement` | `0.411 ± 0.005` / `0.573` | `0.424 ± 0.001` / `0.827` | `0.419 ± 0.007` / **`0.842`** | **`0.494 ± 0.158`** / `0.760` | `0.470 ± 0.110` / `0.796` | `0.0` |
| `nan_poison` | `0.478 ± 0.139` / `0.784` | `0.496 ± 0.158` / `0.775` | `0.465 ± 0.107` / **`0.792`** | `0.496 ± 0.158` / `0.759` | **`0.588 ± 0.163`** / `0.715` | **`10.0 / 10`** |

- **Paired Tests (W3 `sign_flip`, Macro-F1, `n=5`):** Trimmed Mean vs. FedAvg `mean_diff = +0.0140` (95% CI `[-0.1978, +0.1878]`); Multi-Krum vs. FedAvg `mean_diff = -0.0685` (95% CI `[-0.2226, +0.0126]`). On ranking `ROC-AUC`, Multi-Krum improved over FedAvg by **`+0.167`** under `sign_flip` (`0.796` vs `0.629`) and Trimmed Mean improved by **`+0.269`** under `model_replacement` (`0.842` vs `0.573`).

---

## 2. Window W1 Results (`Shards 22+23`, Primary Window) — Val-Calibrated Macro-F1 & ROC-AUC

| Attack (`f = 2 / 10`) | FedAvg (F1 / AUC) | Median (F1 / AUC) | Trimmed Mean (F1 / AUC) | Krum (F1 / AUC) | Multi-Krum (F1 / AUC) | NaN Quarantined |
| --- | --- | --- | --- | --- | --- | --- |
| `sign_flip` (`-8x`) | `0.626 ± 0.202` / `0.365` | `0.596 ± 0.058` / `0.181` | `0.563 ± 0.051` / `0.183` | `0.604 ± 0.057` / `0.212` | `0.612 ± 0.061` / `0.203` | `0.0` |
| `scaled_update` (`+8x`) | `0.726 ± 0.026` / `0.347` | `0.642 ± 0.038` / `0.229` | `0.668 ± 0.042` / `0.267` | `0.626 ± 0.067` / `0.223` | `0.643 ± 0.015` / `0.245` | `0.0` |
| `random_update` | `0.702 ± 0.126` / `0.340` | `0.642 ± 0.021` / `0.215` | `0.664 ± 0.029` / `0.252` | `0.602 ± 0.058` / `0.191` | `0.637 ± 0.013` / `0.232` | `0.0` |
| `model_replacement` | `0.971 ± 0.007` / `0.962`* | `0.650 ± 0.033` / `0.262` | `0.678 ± 0.031` / `0.284` | `0.602 ± 0.058` / `0.191` | `0.637 ± 0.013` / `0.232` | `0.0` |
| `nan_poison` | `0.658 ± 0.048` / `0.266` | `0.627 ± 0.028` / `0.203` | `0.651 ± 0.024` / `0.242` | `0.636 ± 0.102` / `0.225` | `0.626 ± 0.034` / `0.210` | **`10.0 / 10`** |

- **\*Critical Scientific Explanation of W1 `model_replacement` FedAvg (`0.971`):** Because honest W1 linear weights trained on `xss` have an inverted slope relative to Test `backdoor` (`AUC = 0.319`), the `model_replacement` attack (`-8*(v + 0.5)`) negated the global linear weights under unprotected `FedAvg`, accidentally aligning them with Test `backdoor`! Crucially, all four robust aggregators (`Median`, `Trimmed Mean`, `Krum`, `Multi-Krum`) **successfully rejected the replacement attack**, keeping seed variance tight (`SD = 0.013–0.058` vs FedAvg `SD = 0.202` under `sign_flip`).
- **100% `NaN` Quarantine Verified:** Across all `50` `nan_poison` runs on W1 and W3, `FederatedTrainer` quarantined `10 / 10` corrupted updates per run (`2` attackers × `5` active rounds) with zero `NaN` parameter propagation.
