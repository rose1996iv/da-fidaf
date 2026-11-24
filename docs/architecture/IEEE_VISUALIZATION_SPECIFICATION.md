# DA-FIDAF — IEEE Publication-Quality Visualization Specification

## 1. Visual & Typographic Standards (`src/dafidaf/visualization/ieee_plots.py`)

All DA-FIDAF figures are generated programmatically with Matplotlib (`apply_ieee_style()`) adhering to IEEE Transactions standards:

| Parameter | Standard |
| --- | --- |
| Single-column width | `3.5 in` (`IEEE_SINGLE_COL_IN`) |
| Double-column width | `7.16 in` (`IEEE_DOUBLE_COL_IN`) |
| Typography | Serif (`Times New Roman`, fallback `DejaVu Serif`), `8–10 pt`, TrueType embedding (`pdf.fonttype=42`, `ps.fonttype=42`) |
| Color & Grayscale Safety | Colorblind-safe Okabe-Ito palette paired with distinct markers, line styles, and bar hatches |
| Canvas | White background, top/right spines removed, restrained dashed grid (`alpha=0.6`, `lw=0.5`), zero 3D/gradients |
| Output Formats | Vector `.pdf`, vector `.eps`, raster `.png` at `>= 300 DPI` |
| Artifact Containment | Stored strictly outside Git under `I:\Projects\da-fidaf-runs\figures\` (in-repo writes rejected by `export_ieee_figure`) |

---

## 2. Required Per-Figure Deliverables

Every exported figure stem (e.g., `fig_E1_02_f1_comparison`) produces:
1. `<stem>.pdf` — Vector IEEE PDF
2. `<stem>.eps` — Vector EPS
3. `<stem>.png` — `>= 300 DPI` PNG preview
4. `<stem>_data.csv` & `<stem>_data.json` — Exact measured source values plotted
5. `<stem>_caption.txt` — IEEE-style figure caption
6. `<stem>_metadata.json` — Experiment ID, config hashes, run IDs, seeds, sample/client counts, data source, generation timestamp, and artifact SHA-256 hashes
7. Reproducible Python plotting script stored alongside outputs.

---

## 3. Research Integrity Rules

- Only measured values read directly from experiment `run_report.json` outputs are plotted; no fabricated or manually altered numbers.
- Uncertainty is displayed via mean ± SD (or 95% CI when $n \ge 3$ seeds).
- Synthetic smoke-test or synthetic drift interventions are explicitly labeled and visually distinguished (hatches + legend + caption) from real-dataset measurements.
- Failed runs and unfavorable outcomes (e.g., Non-IID collapse on `seed=101`) are never omitted.
