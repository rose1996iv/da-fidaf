"""Unit tests for IEEE publication-quality visualization guards and metadata contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

from dafidaf.visualization.ieee_plots import (
    IEEE_DOUBLE_COL_IN,
    IEEE_SINGLE_COL_IN,
    FigureMetadata,
    export_ieee_figure,
)


def test_ieee_constants_and_export_guards(tmp_path: Path) -> None:
    assert IEEE_SINGLE_COL_IN == 3.5
    assert IEEE_DOUBLE_COL_IN == 7.16

    meta = FigureMetadata(
        figure_stem="fig_test",
        experiment_id="E1",
        config_hashes=("abc123",),
        run_ids=("run_1",),
        seeds=(42,),
        n_clients=6,
        n_samples=100,
        data_source="REAL_DATASET_TON_IOT_PILOT",
        is_synthetic_diagnostic=False,
        conditions="test",
        generated_utc="2026-11-24T00:00:00Z",
        plotting_script="test.py",
    )

    with pytest.raises(ValueError, match="dpi >= 300"):
        export_ieee_figure(
            None,
            stem="fig_test",
            output_dir=tmp_path,
            source_rows=[{"a": 1}],
            caption="cap",
            metadata=meta,
            dpi=150,
        )

    with pytest.raises(ValueError, match="without measured source_rows"):
        export_ieee_figure(
            None,
            stem="fig_test",
            output_dir=tmp_path,
            source_rows=[],
            caption="cap",
            metadata=meta,
            dpi=300,
        )

    with pytest.raises(ValueError, match="Refusing to write figures inside Git repository"):
        export_ieee_figure(
            None,
            stem="fig_test",
            output_dir=tmp_path / "inside",
            source_rows=[{"a": 1}],
            caption="cap",
            metadata=meta,
            dpi=300,
            repo_root=tmp_path,
        )
