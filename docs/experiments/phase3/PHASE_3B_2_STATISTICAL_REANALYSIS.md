# DA-FIDAF Phase 3B.2 — Paired Statistical Reanalysis (Workstream D)

- **Method:** Independent matched-seed paired analysis (`n = 5` seeds `[42, 101, 202, 303, 404]`; unit of analysis = independent seed ONLY). Compares exact two-sided **95% Student-$t$ CI ($df = 4, t_{0.975, 4} = 2.776445$)** against **5,000-resample paired percentile bootstrap 95% CI** and Cohen's $d_z$.
- **Evidence File:** `I:\Projects\da-fidaf-runs\phase3b_2\PHASE_3B_2_EVIDENCE_MANIFEST.json` (`workstream_d_statistical_reanalysis`).

---

## Comparisons Whose Statistical Significance Conclusion Changed (`9` Total)

Every comparison below appeared "statistically significant" under `n = 5` percentile bootstrap (CI excluding `0`), yet **FAILED statistical significance under exact Student-$t$ ($df = 4$)** (CI crossing `0`):

| Comparison ID | Base Mean | Treat Mean | Paired Diff ± SD | Cohen's $d_z$ | Bootstrap 95% CI (`5000`) | Exact Student-$t$ 95% CI (`df=4`) | Verdict Shift |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `E1_W1_fedprox_vs_fedavg_a01_f1` | `0.6999` | `0.6859` | `-0.0140 ± 0.0178` | `-0.785` | `[-0.0276, -0.0004]` | `[-0.0361, +0.0082]` | Sig -> **NS** |
| `E1_W3_fedprox_vs_fedavg_a05_f1` | `0.4177` | `0.4183` | `+0.0006 ± 0.0007` | `+0.824` | `[+0.0001, +0.0012]` | `[-0.0003, +0.0015]` | Sig -> **NS** |
| `E4_W3_mkrum_vs_fedavg_signflip_auc` | `0.6294` | `0.7963` | `+0.1669 ± 0.2011` | `+0.830` | `[+0.0146, +0.3193]` | `[-0.0827, +0.4166]` | Sig -> **NS** |
| `E6_W3_closedloop_vs_noattr_auc` | `0.6294` | `0.8257` | `+0.1963 ± 0.2166` | `+0.907` | `[+0.0262, +0.3643]` | `[-0.0726, +0.4653]` | Sig -> **NS** |
| `E3_W1_data_poisoning_v2_vs_v1_far` | `0.2750` | `0.4750` | `+0.2000 ± 0.1677` | `+1.193` | `[+0.1250, +0.3500]` | `[-0.0082, +0.4082]` | Sig -> **NS** |
| `E3_W1_label_flip_v2_vs_v1_recall` | `0.3000` | `0.0000` | `-0.3000 ± 0.2739` | `-1.095` | `[-0.5000, -0.1000]` | `[-0.6400, +0.0400]` | Sig -> **NS** |
| `E3_W1_byzantine_sign_flip_v2_vs_v1_recall` | `0.6000` | `0.3000` | `-0.3000 ± 0.2739` | `-1.095` | `[-0.5000, -0.1000]` | `[-0.6400, +0.0400]` | Sig -> **NS** |
| `E3_W3_backdoor_v2_vs_v1_far` | `0.2750` | `0.5250` | `+0.2500 ± 0.2500` | `+1.000` | `[+0.0250, +0.4250]` | `[-0.0604, +0.5604]` | Sig -> **NS** |
| `E3_W3_byzantine_sign_flip_v2_vs_v1_recall` | `0.8000` | `0.3000` | `-0.5000 ± 0.5000` | `-1.000` | `[-0.9000, -0.1000]` | `[-1.1208, +0.1208]` | Sig -> **NS** |

- **Mandatory Reporting Rule:** With `n = 5` seeds, percentile bootstrap CIs are anti-conservative. All publication tables must treat **exact Student-$t$ ($df = 4$)** as primary and bootstrap as supplementary, avoiding claims of statistical significance where $t_4$ CIs include zero.
