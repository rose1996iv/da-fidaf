"""Workstream D: Experiment orchestration, synthetic E2E validation, and CLI."""

from dafidaf.orchestration.runner import (
    SyntheticE2EResult,
    generate_synthetic_iot_dataset,
    run_experiment_from_yaml,
    run_synthetic_e2e_experiment,
)

__all__ = [
    "SyntheticE2EResult",
    "generate_synthetic_iot_dataset",
    "run_experiment_from_yaml",
    "run_synthetic_e2e_experiment",
]
