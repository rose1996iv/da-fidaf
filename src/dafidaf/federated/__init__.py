"""Workstream B: Framework-independent federated learning orchestration."""

from dafidaf.federated.aggregation import (
    AggregationError,
    aggregate_updates,
    coordinate_median,
    fedavg,
    krum,
    multi_krum,
    trimmed_mean,
)
from dafidaf.federated.client import ClientUpdate, SimulatedClient
from dafidaf.federated.trainer import FederatedConfig, FederatedTrainer, RoundResult

__all__ = [
    "AggregationError",
    "ClientUpdate",
    "FederatedConfig",
    "FederatedTrainer",
    "RoundResult",
    "SimulatedClient",
    "aggregate_updates",
    "coordinate_median",
    "fedavg",
    "krum",
    "multi_krum",
    "trimmed_mean",
]
