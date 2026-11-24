"""IEEE publication-quality Matplotlib visualization framework for DA-FIDAF.

Design & Integrity Guarantees:
- Supports IEEE single-column (3.5 in) and double-column (7.16 in) layouts.
- Uses serif typography (Times New Roman preferred) at 8-10 pt, white backgrounds,
  restrained gridlines, colorblind-safe Okabe-Ito palette, and grayscale-distinct
  markers, linestyles, and bar hatches.
- Exports vector PDF, EPS, >=300 DPI PNG preview, source CSV/JSON, IEEE caption,
  and provenance metadata JSON strictly outside the Git repository.
- Never fabricates, interpolates, or alters measured experimental results.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

IEEE_SINGLE_COL_IN = 3.5
IEEE_DOUBLE_COL_IN = 7.16

# Colorblind-friendly Okabe-Ito palette (with high luminance contrast for grayscale)
OKABE_ITO_PALETTE: tuple[str, ...] = (
    "#0072B2",  # Blue
    "#D55E00",  # Vermilion
    "#009E73",  # Bluish green
    "#CC79A7",  # Reddish purple
    "#E69F00",  # Orange
    "#56B4E9",  # Sky blue
    "#000000",  # Black
)
IEEE_LINESTYLES: tuple[str, ...] = ("-", "--", "-.", ":", (0, (3, 1, 1, 1)))
IEEE_MARKERS: tuple[str, ...] = ("o", "s", "^", "D", "v", "P")
IEEE_HATCHES: tuple[str, ...] = ("", "//", "\\\\", "xx", "..", "++")


@dataclass(frozen=True, slots=True)
class FigureMetadata:
    """Provenance and integrity metadata recorded alongside every IEEE figure."""

    figure_stem: str
    experiment_id: str
    config_hashes: tuple[str, ...]
    run_ids: tuple[str, ...]
    seeds: tuple[int, ...]
    n_clients: int | None
    n_samples: int | None
    data_source: str  # e.g. "REAL_DATASET_TON_IOT_PILOT" or "SYNTHETIC_DIAGNOSTIC"
    is_synthetic_diagnostic: bool
    conditions: str
    generated_utc: str
    plotting_script: str
    dpi: int = 300
    layout: str = "single_column_3.5in"


def _require_matplotlib() -> tuple[Any, Any]:
    try:
        import matplotlib
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError(
            "Matplotlib is required to render IEEE figures. Run plotting with a Python "
            "environment that provides matplotlib (e.g., system Python 3.12 or a plotting venv)."
        ) from exc
    matplotlib.use("Agg")
    return matplotlib, plt


def apply_ieee_style() -> None:
    """Configure Matplotlib rcParams for IEEE publication-quality serif figures."""
    matplotlib, _ = _require_matplotlib()
    matplotlib.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif", "serif"],
            "font.size": 9,
            "axes.titlesize": 9,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.edgecolor": "#222222",
            "axes.linewidth": 0.7,
            "axes.grid": True,
            "grid.color": "#CCCCCC",
            "grid.linestyle": "--",
            "grid.linewidth": 0.5,
            "grid.alpha": 0.6,
            "lines.linewidth": 1.3,
            "lines.markersize": 4.5,
            "pdf.fonttype": 42,  # TrueType embedding for IEEE PDF compliance
            "ps.fonttype": 42,
        }
    )


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def export_ieee_figure(
    fig: Any,
    *,
    stem: str,
    output_dir: Path,
    source_rows: Sequence[dict[str, object]],
    caption: str,
    metadata: FigureMetadata,
    dpi: int = 300,
    repo_root: Path | None = None,
) -> dict[str, object]:
    """Export PDF, EPS, >=300 DPI PNG, source CSV/JSON, caption, and metadata JSON.

    Refuses to write inside `repo_root` if provided, enforcing external artifact storage.
    """
    if dpi < 300:
        raise ValueError(f"IEEE PNG preview requires dpi >= 300; got {dpi}.")
    if not source_rows:
        raise ValueError("Cannot export figure without measured source_rows.")
    out = output_dir.resolve()
    if repo_root is not None:
        try:
            out.relative_to(repo_root.resolve())
            raise ValueError(
                f"Refusing to write figures inside Git repository '{repo_root}': '{out}'"
            )
        except ValueError as exc:
            if "Refusing to write figures" in str(exc):
                raise

    out.mkdir(parents=True, exist_ok=True)
    pdf_path = out / f"{stem}.pdf"
    eps_path = out / f"{stem}.eps"
    png_path = out / f"{stem}.png"
    csv_path = out / f"{stem}_data.csv"
    json_path = out / f"{stem}_data.json"
    cap_path = out / f"{stem}_caption.txt"
    meta_path = out / f"{stem}_metadata.json"

    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    fig.savefig(png_path, format="png", dpi=dpi, bbox_inches="tight")
    eps_exported = True
    try:
        fig.savefig(eps_path, format="eps", bbox_inches="tight")
    except Exception:
        eps_exported = False

    # Write exact measured source CSV & JSON
    fieldnames = list(source_rows[0].keys())
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in source_rows:
            writer.writerow(row)
    json_path.write_text(json.dumps(list(source_rows), indent=2) + "\n", encoding="utf-8")
    cap_path.write_text(caption.strip() + "\n", encoding="utf-8")

    artifacts: dict[str, object] = {
        "pdf": {"path": str(pdf_path), "sha256": _sha256_file(pdf_path)},
        "eps": (
            {"path": str(eps_path), "sha256": _sha256_file(eps_path)} if eps_exported else None
        ),
        "png": {"path": str(png_path), "sha256": _sha256_file(png_path), "dpi": dpi},
        "data_csv": str(csv_path),
        "data_json": str(json_path),
        "caption_txt": str(cap_path),
    }
    meta_payload = {
        **asdict(metadata),
        "artifacts": artifacts,
    }
    meta_path.write_text(json.dumps(meta_payload, indent=2) + "\n", encoding="utf-8")
    return meta_payload


def plot_e1_f1_comparison(
    run_reports: Sequence[dict[str, object]],
    *,
    output_dir: Path,
    stem: str = "fig_E1_02_f1_comparison",
    plotting_script: str = "dafidaf.visualization.ieee_plots",
    repo_root: Path | None = None,
    double_column: bool = False,
) -> dict[str, object]:
    """Plot IEEE-compliant E1 Macro-F1 & ROC-AUC comparison with mean +/- SD error bars."""
    apply_ieee_style()
    _, plt = _require_matplotlib()

    by_strat: dict[str, list[dict[str, object]]] = {}
    for rep in run_reports:
        strat = str(rep["strategy"])
        by_strat.setdefault(strat, []).append(rep)

    strategies = sorted(by_strat.keys())
    metrics = ("macro_f1", "roc_auc", "pr_auc")
    metric_labels = ("Macro-F1", "ROC-AUC", "PR-AUC")

    source_rows: list[dict[str, object]] = []
    means: dict[str, list[float]] = {s: [] for s in strategies}
    stds: dict[str, list[float]] = {s: [] for s in strategies}
    run_ids: list[str] = []
    cfg_hashes: list[str] = []
    seeds_set: set[int] = set()

    for s in strategies:
        reps = by_strat[s]
        for r in reps:
            run_ids.append(str(r.get("run_id", "")))
            if r.get("config_sha256_prefix"):
                cfg_hashes.append(str(r["config_sha256_prefix"]))
            if r.get("seed") is not None:
                seeds_set.add(int(r["seed"]))  # type: ignore[arg-type]
        for mk in metrics:
            vals = [float(r["test_metrics"][mk]) for r in reps]  # type: ignore[index]
            mu = sum(vals) / len(vals)
            sd = (
                (sum((v - mu) ** 2 for v in vals) / (len(vals) - 1)) ** 0.5
                if len(vals) > 1
                else 0.0
            )
            means[s].append(mu)
            stds[s].append(sd)
            source_rows.append(
                {
                    "strategy": s,
                    "metric": mk,
                    "n_seeds": len(vals),
                    "mean": round(mu, 6),
                    "std": round(sd, 6),
                    "values": json.dumps(vals),
                }
            )

    width_in = IEEE_DOUBLE_COL_IN if double_column else IEEE_SINGLE_COL_IN
    fig, ax = plt.subplots(figsize=(width_in, 2.45))

    x_pos = list(range(len(metrics)))
    bar_w = 0.72 / max(1, len(strategies))
    for idx, s in enumerate(strategies):
        offsets = [x + (idx - (len(strategies) - 1) / 2.0) * bar_w for x in x_pos]
        ax.bar(
            offsets,
            means[s],
            width=bar_w * 0.92,
            yerr=stds[s],
            capsize=3,
            color=OKABE_ITO_PALETTE[idx % len(OKABE_ITO_PALETTE)],
            edgecolor="#222222",
            linewidth=0.6,
            hatch=IEEE_HATCHES[idx % len(IEEE_HATCHES)],
            label=s.replace("_", " ").upper(),
            error_kw={"elinewidth": 0.9, "ecolor": "#111111"},
        )

    ax.set_xticks(x_pos)
    ax.set_xticklabels(metric_labels)
    ax.set_ylim(0.0, 1.08)
    ax.set_ylabel("Score (0–1)")
    ax.set_xlabel("Evaluation Metric (Chronological Test Split)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=True, facecolor="white", edgecolor="#CCCCCC", loc="lower right")
    fig.tight_layout()

    seeds_sorted = tuple(sorted(seeds_set))
    caption = (
        f"Fig. E1-02 (Phase 3A Pilot Diagnostic): Comparison of IID vs. Non-IID (label skew) "
        f"federated intrusion detection on ToN-IoT Network_dataset_23.csv (bounded 15,000-row "
        f"chronological pilot; 6 simulated clients, 5 FL rounds, FedAvg, {len(seeds_sorted)} "
        f"seeds={list(seeds_sorted)}). Bars show mean across seeds; error bars indicate +/- 1 SD. "
        f"Pilot diagnostic only; test split contains 173 flows (3 benign, 170 attack)."
    )
    meta = FigureMetadata(
        figure_stem=stem,
        experiment_id="E1_PILOT",
        config_hashes=tuple(sorted(set(cfg_hashes))),
        run_ids=tuple(run_ids),
        seeds=seeds_sorted,
        n_clients=6,
        n_samples=15000,
        data_source="REAL_DATASET_TON_IOT_PILOT",
        is_synthetic_diagnostic=False,
        conditions="ToN-IoT Network_dataset_23.csv (15k rows), 6 sim clients, 5 rounds, FedAvg",
        generated_utc=datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        plotting_script=plotting_script,
        dpi=300,
        layout="double_column_7.16in" if double_column else "single_column_3.5in",
    )
    res = export_ieee_figure(
        fig,
        stem=stem,
        output_dir=output_dir,
        source_rows=source_rows,
        caption=caption,
        metadata=meta,
        dpi=300,
        repo_root=repo_root,
    )
    plt.close(fig)
    return res


def plot_e2_drift_comparison(
    drift_rows: Sequence[dict[str, object]],
    *,
    run_ids: Sequence[str],
    output_dir: Path,
    stem: str = "fig_E2_01_drift_timeline",
    plotting_script: str = "dafidaf.visualization.ieee_plots",
    repo_root: Path | None = None,
    double_column: bool = False,
) -> dict[str, object]:
    """Plot IEEE-compliant E2 PSI drift magnitudes distinguishing natural vs. synthetic shifts."""
    apply_ieee_style()
    _, plt = _require_matplotlib()

    labels = [str(r["regime"]) for r in drift_rows]
    psi_vals = [float(r["max_psi"]) for r in drift_rows]
    is_synth = [bool(r["is_synthetic"]) for r in drift_rows]

    width_in = IEEE_DOUBLE_COL_IN if double_column else IEEE_SINGLE_COL_IN
    fig, ax = plt.subplots(figsize=(width_in, 2.55))

    y_pos = list(range(len(labels)))
    colors = [OKABE_ITO_PALETTE[1] if s else OKABE_ITO_PALETTE[0] for s in is_synth]
    hatches = ["//" if s else "" for s in is_synth]

    for y, val, col, hat, syn in zip(y_pos, psi_vals, colors, hatches, is_synth, strict=True):
        ax.barh(
            y,
            val,
            height=0.58,
            color=col,
            edgecolor="#222222",
            linewidth=0.6,
            hatch=hat,
            label=("Synthetic Intervention" if syn else "Natural ToN-IoT Observation"),
        )

    ax.axvline(0.25, color="#000000", linestyle="--", linewidth=1.0, label="PSI Threshold (0.25)")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Maximum Feature PSI")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Deduplicate legend entries cleanly
    handles, leg_labels = ax.get_legend_handles_labels()
    seen: dict[str, Any] = {}
    for h, lbl in zip(handles, leg_labels, strict=True):
        seen.setdefault(lbl, h)
    ax.legend(
        list(seen.values()),
        list(seen.keys()),
        frameon=True,
        facecolor="white",
        edgecolor="#CCCCCC",
        loc="lower right",
        fontsize=7.5,
    )
    fig.tight_layout()

    caption = (
        "Fig. E2-01 (Phase 3A Pilot Diagnostic): Maximum feature Population Stability Index (PSI) "
        "across natural ToN-IoT chronological windows (Network_dataset_23.csv Train->Val and "
        "Train->Test), cross-period benign shift (Period A Shard 1 vs. Period B Shard 23, "
        "18-day capture-confounded), and controlled synthetic covariate shift interventions "
        "(abrupt/gradual, severity=1.5, is_synthetic=True). Dashed line marks PSI=0.25 threshold."
    )
    meta = FigureMetadata(
        figure_stem=stem,
        experiment_id="E2_PILOT",
        config_hashes=(),
        run_ids=tuple(run_ids),
        seeds=(42,),
        n_clients=6,
        n_samples=15000,
        data_source="REAL_DATASET_TON_IOT_PILOT_PLUS_LABELED_SYNTHETIC_INTERVENTION",
        is_synthetic_diagnostic=False,
        conditions="Natural chronological vs. confounded Period A->B vs. synthetic covariate shift",
        generated_utc=datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        plotting_script=plotting_script,
        dpi=300,
        layout="double_column_7.16in" if double_column else "single_column_3.5in",
    )
    res = export_ieee_figure(
        fig,
        stem=stem,
        output_dir=output_dir,
        source_rows=drift_rows,
        caption=caption,
        metadata=meta,
        dpi=300,
        repo_root=repo_root,
    )
    plt.close(fig)
    return res
