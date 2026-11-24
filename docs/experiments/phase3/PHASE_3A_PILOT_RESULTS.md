# DA-FIDAF Phase 3A — Bounded Real-Data Pilot Results (E1 & E2)

> [!IMPORTANT]
> **Pilot Scope Disclosure:** All runs below are small, bounded engineering pilots (`15,000` rows of `Network_dataset_23.csv`, `6` simulated logical gateway clients, `5` FL rounds) saved externally under `I:\Projects\da-fidaf-runs`. These results **validate pipeline execution only** and MUST NOT be cited as full research efficacy evidence.

---

## 1. E1 Pilot — IID vs. Non-IID (`label_skew`, Dirichlet $\alpha=0.5$)

- **Dataset:** `Network_dataset_23.csv` (`15,000` rows; SHA-256 `e89c54673961c2b260265cdd3f6c50355369f8a80e63c31999df04b0a757f213`)
- **Chronological Split:** `train=10,503` (`425` benign, `10,078` attack), `val=150` (`15` benign, `135` attack), `test=173` (`3` benign, `170` attack)
- **FL Setup:** `6` simulated clients (`sim_gw_01..06`), `5` rounds, `local_epochs=1`, `batch_size=64`, `lr=0.05`, `FedAvg`, `2` seeds (`42`, `101`).

### Summary Table

| Strategy | Seed | Run ID (in `I:\Projects\da-fidaf-runs`) | Config Hash | Macro-F1 | PR-AUC | ROC-AUC | FPR | FNR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `iid` | 42 | `20261124T063040_430883Z_phase3a_e1_iid_seed42_7e7666` | `21f72de81b63f4bc` | `0.747076` | `1.000000` | `1.000000` | `0.666667` | `0.000000` |
| `iid` | 101 | `20261124T063040_703422Z_phase3a_e1_iid_seed101_417a46` | `35b715faa99526c8` | `0.747076` | `1.000000` | `1.000000` | `0.666667` | `0.000000` |
| `label_skew` | 42 | `20261124T063040_985904Z_phase3a_e1_label_skew_seed42_5dcbe5` | `5f9863851a5a7b75` | `0.747076` | `1.000000` | `1.000000` | `0.666667` | `0.000000` |
| `label_skew` | 101 | `20261124T063041_266599Z_phase3a_e1_label_skew_seed101_90c735` | `a1324f63f7b5f8b5` | `0.495627` | `0.979890` | `0.674510` | `1.000000` | `0.000000` |

### Client-Level Sample & Label Distributions

- **IID (`seed=42` & `seed=101`):** `sim_gw_01..04`: `1,751` (`71` benign / `1,680` attack); `sim_gw_05`: `1,750` (`71` / `1,679`); `sim_gw_06`: `1,749` (`70` / `1,679`).
- **Non-IID `label_skew` (`seed=42`):** `sim_gw_01`: `5,871` (`122`/`5,749`), `sim_gw_02`: `911` (`0`/`911`), `sim_gw_03`: `1,486` (`186`/`1,300`), `sim_gw_04`: `32` (`1`/`31`), `sim_gw_05`: `1,706` (`3`/`1,703`), `sim_gw_06`: `497` (`113`/`384`).
- **Non-IID `label_skew` (`seed=101`):** `sim_gw_01`: `6,591` (`9`/`6,582`), `sim_gw_02`: `433` (`109`/`324`), `sim_gw_03`: `105` (`71`/`34`), `sim_gw_04`: `719` (`169`/`550`), `sim_gw_05`: `58` (`52`/`6`), `sim_gw_06`: `2,597` (`15`/`2,582`).

### Observations & Limitations
- Unlike the synthetic toy benchmark (`macro_f1 = 1.0`), real ToN-IoT immediately surfaced severe class imbalance (`95.9%` attack) causing high FPR (`0.6667`–`1.0`) at the default `0.5` probability threshold, and genuine Non-IID collapse (`macro_f1 = 0.4956`, `roc_auc = 0.6745` at `seed=101`).
- Because the 15k-row pilot Test split contained only `3` benign flows, FPR estimates have high quantization variance (`1/3` steps) and are not statistically meaningful for publication.

---

## 2. E2 Pilot — Natural Chronological Drift vs. Controlled Synthetic Drift

### 2.1 Natural Drift Measurements (Zero Synthetic Intervention)

| Comparison | Mean PSI | Max PSI | Mean JSD (bits) | Detected (`PSI >= 0.25`) | Interpretation |
| --- | --- | --- | --- | --- | --- |
| `Network_dataset_23.csv` Train -> Val (chronological) | `0.029480` | `0.233838` | `0.005195` | `False` | Stationary within 36-minute shard |
| `Network_dataset_23.csv` Train -> Test (chronological) | `0.007753` | `0.077528` | `0.001383` | `False` | Stationary within 36-minute shard |
| Period A (`Network_dataset_1.csv` normal) -> Period B (`Network_dataset_23.csv` normal) | `1.924537` | `10.364964` | — | `True` | Large natural shift **confounded by 18-day capture gap** (Phase 1C) |

### 2.2 Controlled Synthetic Drift Interventions (`is_synthetic=True`, Applied to Real Val Window)

| Schedule | Run ID (in `I:\Projects\da-fidaf-runs`) | Synthetic Max PSI | Detected | Pre-Adapt Loss | Post-Adapt Loss (`replay`) | Forgetting Delta |
| --- | --- | --- | --- | --- | --- | --- |
| `abrupt` (`severity=1.5`, `round=5`) | `20261124T063041_393734Z_phase3a_e2_abrupt_seed42_f4114d` | `7.3114` | `True` | `0.3981` | `0.3044` | `-0.037704` |
| `gradual` (`severity=1.5`, `onset=3`, `dur=3`, `round=5`) | `20261124T063041_416735Z_phase3a_e2_gradual_seed42_be98db` | `7.3114` | `True` | `0.3981` | `0.3044` | `-0.037704` |

- **Note:** `abrupt` and `gradual` reached identical intensity (`1.0`) at `round_id = 5` (`onset=3, duration=3`). Synthetic drift is explicitly tagged `is_synthetic=True` and is NOT interpreted as naturally occurring drift.
