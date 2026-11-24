# DA-FIDAF — Phase 3B IEEE Figure & Table Standard

## 1. Mandatory Output Pipeline (`src/dafidaf/visualization/ieee_plots.py`)

Every Phase 3B experiment (E1–E4, E6) MUST export all figures strictly outside the Git repository under:
`I:\Projects\da-fidaf-runs\figures\phase3b\`

Each figure stem produces **7 mandatory deliverables**:
1. `<stem>.pdf` — Vector IEEE PDF (`pdf.fonttype=42`, TrueType fonts embedded)
2. `<stem>.eps` — Vector EPS (`ps.fonttype=42`, where supported by backend)
3. `<stem>.png` — Raster preview at **`>= 300 DPI`**
4. `<stem>_data.csv` & `<stem>_data.json` — Exact measured source values from `run_report.json`
5. `<stem>_caption.txt` — IEEE-style self-contained caption (dataset, window, `K`, `n` seeds, uncertainty definition)
6. `<stem>_metadata.json` — Experiment ID, config hashes, run IDs, seeds, sample/client counts, data source, generation UTC timestamp, and SHA-256 of every exported artifact
7. Reproducible Python plotting script stored alongside the figures.

---

## 2. Planned Phase 3B Figure Registry

| Experiment | Figure Stem | Layout | Content |
| --- | --- | --- | --- |
| **E1** | `fig_E1_01_convergence` | Single (`3.5 in`) | Per-round Val BCE loss (mean ± SD, `n=5`) for IID vs. Non-IID (FedAvg vs. FedProx) |
| **E1** | `fig_E1_02_f1_comparison` | Double (`7.16 in`) | Macro-F1, ROC-AUC, PR-AUC, FPR across partition regimes & $\tau^*_{\text{val}}$ calibration |
| **E2** | `fig_E2_01_drift_timeline` | Double (`7.16 in`) | Chronological PSI/Page-Hinkley trajectory (natural vs. labeled synthetic gradual/abrupt/recurring) |
| **E2** | `fig_E2_02_adaptation_forgetting` | Single (`3.5 in`) | Recovery Macro-F1 vs. `forgetting_delta` across Static / Fine-Tune / Regularized / Replay |
| **E3** | `fig_E3_01_attribution_tradeoff` | Single (`3.5 in`) | FAR vs. Malicious Recall & `uncertain_rate` across drift vs. poisoning arms |
| **E4** | `fig_E4_01_byzantine_robustness` | Double (`7.16 in`) | Macro-F1 across 5 aggregators × 5 Byzantine attack types (`n=5` seeds, mean ± 95% CI) |
| **E6** | `fig_E6_01_ablation_overhead` | Double (`7.16 in`) | Component ablation Macro-F1 vs. communication bytes / wall time & conditional RDP $\epsilon$-utility curve |

---

## 3. Visual & Research Integrity Rules

- **Typography & Style:** Serif (`Times New Roman`, fallback `DejaVu Serif`), `8–10 pt`, white background, top/right spines removed, restrained dashed grid, Okabe-Ito colorblind-safe palette + distinct grayscale markers/linestyles/hatches, zero 3D or decorative gradients.
- **No Fabricated Data or Invalid CIs:** Only measured `run_report.json` values may be plotted. Never plot CIs for $n < 3$ seeds. Never plot synthetic smoke-test data as final research figures.
- **IEEE Table Standard:** Every LaTeX/Markdown table reports `mean ± SD` (`n=5`), bolds best statistically supported value, includes exact `n_val`/`n_test` benign & attack counts, and explicitly footnotes `E5: HOLD`, `DP: simulation-grade RDP`, and `SecAgg: inactive`.
