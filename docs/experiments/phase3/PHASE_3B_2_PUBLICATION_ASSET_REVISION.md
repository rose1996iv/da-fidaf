# DA-FIDAF Phase 3B.2 — Publication Asset Revision Report (Workstream E)

- **Revision Output Directory:** `I:\Projects\da-fidaf-runs\phase3b_2\figures\` (`36` files: `5` IEEE figure sets × `7` deliverables + `plot_phase3b_2_revised_figures.py`).
- **Original Figure Preservation:** Original Phase 3B figures under `I:\Projects\da-fidaf-runs\figures\phase3b\` (`43` files) remain **100% untouched**.

---

## Revised & New IEEE Figure Inventory (`300 DPI` PNG + Vector PDF + Vector EPS + CSV/JSON + Caption + Metadata)

| Figure Stem | Type | Audit Issue Remediated / Content | Metadata Verified |
| --- | --- | --- | --- |
| `fig_E1_02_f1_comparison_rev2` | Revised | Fixed `run_ids` from `40` -> exact **`70`** E1 runs; explicitly itemized W1 (`89,269`) and W3 (`191,738`) | `70` run IDs, PDF/EPS/PNG SHA-256 verified |
| `fig_E2_01_drift_timeline_rev2` | Revised | Aligned `run_ids` to exact **`30`** plotted W1 runs (removing unplotted W3 IDs) | `30` run IDs, PDF/EPS/PNG SHA-256 verified |
| `fig_E1_03_w1_domain_shift` | New | Workstream A per-split/per-class probability mean & IQR explaining W1 `ROC-AUC = 0.3208` | Checkpoint provenance recorded |
| `fig_E3_02_attribution_v2` | New | Workstream B honest comparison of E3 v1 vs. v2 Recall & FAR on W1 and W3 | `40` v2 run IDs recorded |
| `fig_E6_02_genuine_ablation` | New | Workstream C closed-loop quarantine vs. zero-call `without_attribution_genuine` | `20` v2 run IDs recorded |
