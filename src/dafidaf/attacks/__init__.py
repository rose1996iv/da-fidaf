"""Workstream C: Controlled poisoning and Byzantine client attack simulators."""

from dafidaf.attacks.simulators import (
    ByzantineConfig,
    PoisoningConfig,
    apply_byzantine_update,
    apply_data_poisoning,
)

__all__ = [
    "ByzantineConfig",
    "PoisoningConfig",
    "apply_byzantine_update",
    "apply_data_poisoning",
]
