# DA-FIDAF Phase 3B.1 — Independent IEEE Figure Audit

- **Scope:** All `6` Phase 3B figure sets (`43` files) under `I:\Projects\da-fidaf-runs\figures\phase3b\`. Original figures were NOT modified during this audit.

---

## 1. Artifact Integrity, DPI & Format Verification

| Figure Stem | PDF SHA-256 | EPS SHA-256 | PNG SHA-256 | PNG DPI & Dimensions | CSV / JSON Rows | Metadata `run_ids` | Metadata `n_samples` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `fig_E1_01_convergence` | **PASS** | **PASS** | **PASS** | `300.0 × 300.0` (`2126×740 px`) | `64` / `64` | `40` (exact for 4 plotted cfgs) | `89269` *(W1 only!)* |
| `fig_E1_02_f1_comparison` | **PASS** | **PASS** | **PASS** | `300.0 × 300.0` (`2127×798 px`) | `42` / `42` | **`40`** *(should be `70`!)* | `89269` *(W1 only!)* |
| `fig_E2_01_drift_timeline` | **PASS** | **PASS** | **PASS** | `300.0 × 300.0` (`2126×768 px`) | `12` / `12` | `60` *(W1+W3; plot shows W1)* | `89269` *(W1 only!)* |
| `fig_E3_01_attribution_tradeoff` | **PASS** | **PASS** | **PASS** | `300.0 × 300.0` (`2127×768 px`) | `24` / `24` | `40` (exact) | `89269` *(W1 only!)* |
| `fig_E4_01_byzantine_robustness` | **PASS** | **PASS** | **PASS** | `300.0 × 300.0` (`2127×798 px`) | `50` / `50` | `250` (exact) | `89269` *(W1 only!)* |
| `fig_E6_01_ablation_overhead` | **PASS** | **PASS** | **PASS** | `300.0 × 300.0` (`2126×768 px`) | `10` / `10` | `50` (exact) | `89269` *(W1 only!)* |

- **Plotted Values vs. Raw Reports (`PASS`):** Every plotted mean and SD in `*_data.csv` / `*_data.json` matches the independently recomputed raw `run_report.json` values (`0` failed or missing runs silently excluded).
- **Layout, Typography & Grayscale Compliance (`PASS`):** All 6 figures use double-column `7.16 in` layout (`~2126 px` at `300 DPI`), serif typography, `pdf.fonttype=42`, colorblind-safe Okabe-Ito palette with distinct hatches/markers/linestyles, and white backgrounds.

---

## Finding [AUD-06] — MEDIUM: Figure Provenance Metadata Omissions (`fig_E1_02` `run_ids` & Dual-Window `n_samples`)

- **Finding ID:** `AUD-06` | **Severity:** `MEDIUM` (Metadata Provenance)
- **Evidence File:** `I:\Projects\da-fidaf-runs\figures\phase3b\plot_phase3b_ieee_figures.py` & `*_metadata.json`
- **Verification Method:** Audited all `6` `*_metadata.json` files against plotted datasets and raw run counts.
- **Exact Discrepancies Found:**
  1. `fig_E1_02_f1_comparison_metadata.json` reused `rids` from `fig_E1_01` (`40` runs for 4 configs) even though `fig_E1_02` plots all **`7` configurations × `5` seeds × `2` windows = `70` runs**.
  2. All five dual-window figures (`fig_E1_01`, `fig_E1_02`, `fig_E3_01`, `fig_E4_01`, `fig_E6_01`) set `n_samples = 89269` (W1 count only), omitting W3's `191,738` rows from the structured metadata field (though captions name both W1 and W3).
  3. `fig_E2_01_drift_timeline_metadata.json` lists `60` `run_ids` (both W1 and W3, matching `_data.csv`), whereas the rendered two-panel plot displays W1 only (caption correctly states W1).
- **Scientific Implication:** Plotted numbers and visual graphics are accurate, but automated provenance consumers reading `*_metadata.json` would undercount E1 runs on `fig_E1_02` and miss W3's sample size.
- **Recommended Action:** Update `plot_phase3b_ieee_figures.py` (when authorized to regenerate figures) to collect all `70` E1 `run_ids` for `fig_E1_02`, record per-window sample counts (`W1: 89,269; W3: 191,738`), and restrict `fig_E2_01` `run_ids` to the `30` W1 runs plotted (or add a W3 panel).
