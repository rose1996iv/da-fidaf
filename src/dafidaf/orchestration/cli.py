"""Phase 2 CLI (`python -m dafidaf.orchestration.cli`) preserving Stage 7 `cli.py`."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from dafidaf.config import load_config
from dafidaf.data.adapters import (
    CICIoT2023Adapter,
    DatasetAdapterError,
    EdgeIIoTsetAdapter,
    TonIoTNetworkAdapter,
)
from dafidaf.data.schemas import TON_IOT_NUMERIC_FEATURES
from dafidaf.orchestration.runner import run_experiment_from_yaml, run_synthetic_e2e_experiment


def _require_dataset_root() -> Path:
    cfg = load_config()
    root = cfg.paths.dataset_root.path
    if root is None:
        raise DatasetAdapterError(
            "DAFIDAF_DATA_ROOT is not configured; refusing uncontained dataset path access."
        )
    return root


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m dafidaf.orchestration.cli",
        description="DA-FIDAF Phase 2 data, federation, and evaluation CLI.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("inspect-schema", help="Print canonical ToN-IoT numeric feature metadata.")

    val_p = sub.add_parser("validate-dataset", help="Bounded read-only adapter check on a CSV.")
    val_p.add_argument(
        "--family",
        choices=("ton_iot", "ciciot2023", "edge_iiot", "edge_iiotset"),
        required=True,
    )
    val_p.add_argument("--csv", required=True)
    val_p.add_argument("--max-rows", type=int, default=500)

    e2e_p = sub.add_parser("run-e2e-synthetic", help="Run Gate D synthetic end-to-end smoke test.")
    e2e_p.add_argument("--seed", type=int, default=42)
    e2e_p.add_argument("--save", action="store_true", help="Write report to DAFIDAF_RUNS_ROOT.")

    exp_p = sub.add_parser("run-experiment", help="Run a versioned YAML experiment configuration.")
    exp_p.add_argument("--config", required=True)
    exp_p.add_argument(
        "--dataset-csv",
        default=None,
        help="Path to real dataset CSV (must reside inside DAFIDAF_DATA_ROOT).",
    )
    exp_p.add_argument("--max-rows", type=int, default=None)
    exp_p.add_argument("--multi-seed", action="store_true")
    exp_p.add_argument(
        "--synthetic-smoke-test",
        action="store_true",
        help="Explicitly run synthetic toy smoke test instead of real dataset.",
    )
    exp_p.add_argument("--save", action="store_true")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "inspect-schema":
        out = [
            {"name": f.name, "dtype": f.dtype, "unit": f.unit, "missing_policy": f.missing_policy}
            for f in TON_IOT_NUMERIC_FEATURES
        ]
        sys.stdout.write(json.dumps(out, indent=2) + "\n")
        return 0

    if args.command == "validate-dataset":
        allowed_root = _require_dataset_root()
        adapters = {
            "ton_iot": TonIoTNetworkAdapter(),
            "ciciot2023": CICIoT2023Adapter(),
            "edge_iiot": EdgeIIoTsetAdapter(),
            "edge_iiotset": EdgeIIoTsetAdapter(),
        }
        ds = adapters[args.family].load(
            Path(args.csv),
            max_rows=args.max_rows,
            allowed_root=allowed_root,
            compute_sha256=False,
        )
        summary = {
            "dataset_id": ds.dataset_id,
            "rows_loaded": len(ds.features),
            "feature_count": len(ds.feature_names),
            "has_timestamps": ds.timestamps is not None,
            "inf_sanitized": ds.inf_sanitized_count,
            "exact_duplicates": ds.exact_duplicate_count,
            "dropped_invalid_ts": ds.dropped_invalid_ts,
            "dropped_invalid_label": ds.dropped_invalid_label,
        }
        sys.stdout.write(json.dumps(summary, indent=2) + "\n")
        return 0

    if args.command == "run-e2e-synthetic":
        runs_root: Path | None = None
        if args.save:
            cfg = load_config()
            runs_root = cfg.paths.experiment_runs_dir.path
        res = run_synthetic_e2e_experiment(runs_root=runs_root, seed=args.seed)
        sys.stdout.write(
            json.dumps(
                {
                    "run_id": res.run_id,
                    "data_source": "SYNTHETIC_TOY_GENERATOR",
                    "test_metrics": res.test_metrics,
                    "attribution_metrics": res.attribution_metrics,
                    "drift_detected": res.drift_detected,
                },
                indent=2,
            )
            + "\n"
        )
        return 0

    if args.command == "run-experiment":
        runs_root = load_config().paths.experiment_runs_dir.path if args.save else None
        allowed_root = None if args.synthetic_smoke_test else _require_dataset_root()
        out = run_experiment_from_yaml(
            Path(args.config),
            runs_root=runs_root,
            dataset_csv=Path(args.dataset_csv) if args.dataset_csv else None,
            allowed_root=allowed_root,
            max_rows=args.max_rows,
            multi_seed=args.multi_seed,
            synthetic_smoke_test=args.synthetic_smoke_test,
        )
        sys.stdout.write(json.dumps(out, indent=2) + "\n")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
