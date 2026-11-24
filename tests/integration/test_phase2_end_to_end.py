"""Gate D integration tests: synthetic E2E DA-FIDAF pipeline, YAML configs, E5 HOLD gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dafidaf.data.schemas import E5OntologyBlockedError
from dafidaf.evaluation import paired_effect_size_and_ci, summarize_multi_seed
from dafidaf.orchestration import run_experiment_from_yaml, run_synthetic_e2e_experiment


def test_synthetic_end_to_end_pipeline_gate_d(tmp_path: Path) -> None:
    res = run_synthetic_e2e_experiment(
        runs_root=tmp_path,
        seed=42,
        n_clients=10,
        rounds=4,
        aggregation="trimmed_mean",
        partition_strategy="label_skew",
    )
    assert res.run_dir is not None
    report_path = Path(res.run_dir) / "run_report.json"
    sha_path = Path(res.run_dir) / "run_report.sha256"
    assert report_path.is_file() and sha_path.is_file()

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["test_metrics"]["macro_f1"] > 0.70
    assert payload["drift_detected"] is True
    assert payload["attribution_metrics"]["malicious_recall"] >= 0.5
    assert payload["attribution_metrics"]["false_attribution_rate"] == 0.0
    assert payload["provenance"]["client_partition_type"] == "simulated_logical_gateway"
    assert payload["total_comm_bytes"] > 0


def test_e5_yaml_enforces_hold_gate() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    e5_cfg = repo_root / "configs" / "experiments" / "e5_cross_dataset_hold.yaml"
    with pytest.raises(E5OntologyBlockedError):
        run_experiment_from_yaml(e5_cfg)


def test_multi_seed_statistics_refuses_single_seed_ci() -> None:
    s1 = summarize_multi_seed([0.85])
    assert s1.statistically_valid is False and s1.ci95_low is None

    s3 = summarize_multi_seed([0.84, 0.86, 0.88])
    assert s3.statistically_valid is True
    assert s3.ci95_low is not None and s3.ci95_high is not None

    eff = paired_effect_size_and_ci([0.70, 0.72, 0.71], [0.85, 0.87, 0.86])
    assert eff["mean_diff"] is not None and eff["mean_diff"] > 0.1
