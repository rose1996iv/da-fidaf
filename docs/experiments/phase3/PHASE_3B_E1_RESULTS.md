# DA-FIDAF Phase 3B — E1 Results (IID vs. Non-IID Federated Learning)

- **Execution Scope:** Authorized Phase 3B Non-DP baseline (`dp_enabled = False`, `secure_aggregation_active = False`), `K = 10` simulated logical gateways (`sim_gw_01..10`), `8` communication rounds, `5` independent seeds `[42, 101, 202, 303, 404]`.
- **Artifacts:** `I:\Projects\da-fidaf-runs\phase3b\e1\` and `e1_master_summary.json` (`70` total runs: `35` on W1 + `35` on W3; `0` failed runs).
- **IEEE Figures:** `I:\Projects\da-fidaf-runs\figures\phase3b\fig_E1_01_convergence.*`, `fig_E1_02_f1_comparison.*`.

> [!IMPORTANT]
> **Overlapping Window Disclosure:** W1 (`Shards 22+23`, `stride=15`, `89,269` rows) is a chronological subset of W3 (`Shards 8–23`, `stride=80`, `191,738` rows). Results are reported and analyzed strictly separately and are NEVER pooled as independent datasets. With `n = 5` seeds, bootstrap 95% CIs reflect limited sample size and must be interpreted cautiously.

---

## 1. Window W1 Results (`Shards 22+23`, `300s` Embargo)

**Verified Split Counts:** Train `62,488` (`15,270` benign / `47,218` attack: `xss`, `ransomware`, `backdoor`); Val `13,303` (`747` benign / `12,556` attack); Test `13,253` (`1,811` benign / `11,442` attack: `backdoor`, `mitm`). All splits exceed the `>= 500`/class floor (`disc_embargo = 224`, `disc_active = 1`).

| Configuration | Cal Macro-F1 (Mean ± SD, 95% CI) | Fixed 0.50 F1 | ROC-AUC | PR-AUC | Cal FPR | Cal FNR | Per-Seed Cal Macro-F1 `[42,101,202,303,404]` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `iid_fedavg` | `0.7017 ± 0.0124` `[0.6926, 0.7108]` | `0.5097 ± 0.0007` | `0.3189` | `0.7497` | `0.7037` | `0.0003` | `[0.6992, 0.6842, 0.7136, 0.7136, 0.6978]` |
| `label_skew_a05_fedavg` | `0.6962 ± 0.0347` `[0.6651, 0.7225]` | `0.4832 ± 0.0125` | `0.3072` | `0.7471` | `0.7107` | `0.0003` | `[0.7070, 0.7016, 0.7374, 0.6936, 0.6416]` |
| `label_skew_a01_fedavg` | `0.6999 ± 0.0385` `[0.6709, 0.7294]` | `0.4911 ± 0.0374` | `0.3011` | `0.7462` | `0.7010` | `0.0016` | `[0.7358, 0.6984, 0.6578, 0.7415, 0.6661]` |
| `quantity_skew_fedavg` | `0.7102 ± 0.0204` `[0.6946, 0.7258]` | `0.5194 ± 0.0083` | `0.3399` | `0.7545` | `0.6893` | `0.0004` | `[0.6888, 0.7208, 0.6872, 0.7271, 0.7268]` |
| `combined_fedavg` | `0.7185 ± 0.0245` `[0.7003, 0.7382]` | `0.4998 ± 0.0167` | `0.3480` | `0.7566` | `0.6740` | `0.0009` | `[0.6889, 0.7290, 0.7148, 0.7060, 0.7539]` |
| `label_skew_a05_fedprox` | `0.6957 ± 0.0204` `[0.6834, 0.7140]` | `0.4780 ± 0.0047` | `0.2938` | `0.7441` | `0.7125` | `0.0003` | `[0.6914, 0.6795, 0.7312, 0.6860, 0.6903]` |
| `label_skew_a01_fedprox` | `0.6859 ± 0.0391` `[0.6589, 0.7190]` | `0.4876 ± 0.0336` | `0.2899` | `0.7438` | `0.7248` | `0.0008` | `[0.7023, 0.6659, 0.6517, 0.7470, 0.6627]` |

- **Paired Tests (W1, `n=5`):**
  - FedProx vs. FedAvg (`alpha=0.5`): `mean_diff = -0.0005`, `d_z = -0.019`, 95% CI `[-0.0166, +0.0249]` (no significant difference; FedProx lowered seed SD from `0.0347` to `0.0204`).
  - FedProx vs. FedAvg (`alpha=0.1`): `mean_diff = -0.0140`, `d_z = -0.785`, 95% CI `[-0.0274, -0.0004]`.
  - Non-IID (`alpha=0.1`) vs. IID: `mean_diff = -0.0018`, `d_z = -0.045`, 95% CI `[-0.0326, +0.0276]`.
- **Critical Scientific Finding on W1:** Validation-only threshold calibration improved Macro-F1 by **`+0.19` to `+0.22`** over fixed `0.50` across all 7 configurations (`~0.70` vs `~0.50`). However, W1 `ROC-AUC` is `0.29–0.35` (`< 0.50`) because Train is dominated by `xss` (`32,607` flows with large HTTP payloads), whereas Val and Test contain `backdoor` + `mitm` flows with inverted linear feature slopes relative to `normal`. This demonstrates a genuine cross-campaign linear representation bottleneck on chronological ToN-IoT.

---

## 2. Window W3 Results (`Shards 8–23`, `300s` Embargo, Overlapping Larger Window)

**Verified Split Counts:** Train `147,355` (`3,043` benign / `144,312` attack: `scanning`, `dos`, `injection`, `ddos`, `password`); Val `33,693` (`625` benign / `33,068` attack: `password`, `xss`); Test `10,547` (`3,261` benign / `7,286` attack: `ransomware`, `backdoor`, `mitm` — 100% novel attack families vs. Train).

| Configuration | Cal Macro-F1 (Mean ± SD, 95% CI) | Fixed 0.50 F1 | ROC-AUC | PR-AUC | Cal FPR | Cal FNR | Per-Seed Cal Macro-F1 `[42,101,202,303,404]` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `iid_fedavg` | `0.4142 ± 0.0078` `[0.4086, 0.4203]` | `0.4163 ± 0.0072` | `0.8369` | `0.8382` | `0.9947` | `0.0000` | `[0.4216, 0.4086, 0.4086, 0.4239, 0.4086]` |
| `label_skew_a05_fedavg` | `0.4177 ± 0.0084` `[0.4116, 0.4239]` | `0.4086 ± 0.0001` | `0.8308` | `0.8331` | `0.9914` | `0.0000` | `[0.4086, 0.4239, 0.4239, 0.4239, 0.4086]` |
| `label_skew_a01_fedavg` | `0.7184 ± 0.1760` `[0.5563, 0.8212]` | `0.4227 ± 0.0317` | `0.6895` | `0.7345` | `0.4558` | `0.0813` | `[0.7773, 0.7780, 0.8504, 0.4086, 0.7776]` |
| `quantity_skew_fedavg` | `0.4086 ± 0.0000` `[0.4086, 0.4086]` | `0.4222 ± 0.0040` | `0.8450` | `0.8467` | `1.0000` | `0.0000` | `[0.4086, 0.4086, 0.4086, 0.4086, 0.4086]` |
| `combined_fedavg` | `0.4152 ± 0.0078` `[0.4092, 0.4211]` | `0.4116 ± 0.0068` | `0.8310` | `0.8328` | `0.9937` | `0.0000` | `[0.4242, 0.4232, 0.4086, 0.4115, 0.4086]` |
| `label_skew_a05_fedprox` | `0.4183 ± 0.0082` `[0.4120, 0.4243]` | `0.4086 ± 0.0000` | `0.8197` | `0.8238` | `0.9908` | `0.0000` | `[0.4102, 0.4248, 0.4242, 0.4239, 0.4086]` |
| `label_skew_a01_fedprox` | `0.7045 ± 0.1654` `[0.5562, 0.7794]` | `0.4116 ± 0.0068` | `0.6471` | `0.7050` | `0.4892` | `0.0811` | `[0.7775, 0.7776, 0.7806, 0.4086, 0.7780]` |

- **Critical Scientific Finding on W3:** Despite strong ranking performance on 100% unseen Test attack families (`ROC-AUC = 0.831–0.845`, `PR-AUC = 0.833–0.847` for IID/Qty/LS-0.5), `Cal Macro-F1` collapsed to `0.414` (`FPR = 0.995`) because Train (`97.9%` attack) and Val (`98.1%` attack, `xss/password`) produced an aggressive threshold $\tau^*_{\text{val}}$ that miscalibrated on Test (`69.1%` attack, `ransomware/backdoor`). Under extreme `label_skew` ($\alpha=0.1$), higher score dispersion across clients allowed Val calibration to find a better operating point on 4 of 5 seeds (`Macro-F1 = 0.718 ± 0.176`), though with higher variance and lower ranking AUC (`0.690`).
