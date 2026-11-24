"""Isolated in-memory poisoning and Byzantine client simulators (never mutate raw datasets)."""

from __future__ import annotations

import hashlib
import random
from collections.abc import Sequence
from dataclasses import dataclass

from dafidaf.federated.client import ClientUpdate


@dataclass(frozen=True, slots=True)
class PoisoningConfig:
    """Configuration for controlled in-memory data poisoning."""

    attack_type: str  # "label_flip", "data_poisoning", "backdoor"
    poison_fraction: float = 0.3
    affected_clients: tuple[str, ...] = ("sim_gw_01",)
    backdoor_trigger_value: float = 5.0
    backdoor_target_label: int = 0
    noise_std: float = 3.0
    seed: int = 42
    is_simulated: bool = True


def apply_data_poisoning(
    x_rows: Sequence[Sequence[float]],
    y_rows: Sequence[int],
    config: PoisoningConfig,
) -> tuple[list[list[float]], list[int], dict[str, object]]:
    """Return poisoned in-memory copies without altering input sequences."""
    x_out = [list(r) for r in x_rows]
    y_out = [int(y) for y in y_rows]
    n = len(x_out)
    rng = random.Random(config.seed)
    n_target = int(round(n * max(0.0, min(1.0, config.poison_fraction))))
    idxs = rng.sample(range(n), n_target) if n_target > 0 else []

    if config.attack_type == "label_flip":
        for i in idxs:
            y_out[i] = 1 - y_out[i]
    elif config.attack_type == "data_poisoning":
        for i in idxs:
            for j in range(len(x_out[i])):
                x_out[i][j] += rng.gauss(0.0, config.noise_std)
    elif config.attack_type == "backdoor":
        for i in idxs:
            if len(x_out[i]) >= 2:
                x_out[i][0] = config.backdoor_trigger_value
                x_out[i][1] = config.backdoor_trigger_value
            y_out[i] = config.backdoor_target_label
    else:
        raise ValueError(f"Unsupported poisoning attack_type: '{config.attack_type}'")

    meta: dict[str, object] = {
        "is_simulated": True,
        "attack_type": config.attack_type,
        "poisoned_samples": len(idxs),
        "total_samples": n,
        "affected_clients": list(config.affected_clients),
    }
    return x_out, y_out, meta


@dataclass(frozen=True, slots=True)
class ByzantineConfig:
    """Configuration for simulated Byzantine client model-update attacks."""

    attack_type: str  # "sign_flip", "scaled_update", "random_update", "model_replacement"
    malicious_clients: tuple[str, ...] = ("sim_gw_01", "sim_gw_02")
    scale_factor: float = 10.0
    random_std: float = 2.0
    active_from_round: int = 1
    seed: int = 42
    is_simulated: bool = True


def apply_byzantine_update(
    round_id: int,
    update: ClientUpdate,
    config: ByzantineConfig,
) -> ClientUpdate:
    """Transform a malicious simulated client's update according to ByzantineConfig."""
    if round_id < config.active_from_round or update.client_id not in config.malicious_clients:
        return update

    d = len(update.delta_params)
    cid_hash = int.from_bytes(
        hashlib.blake2b(update.client_id.encode("utf-8"), digest_size=4).digest(),
        "big",
    )
    rng = random.Random(config.seed + round_id * 97 + (cid_hash % 100_000))

    if config.attack_type == "sign_flip":
        corrupted = tuple(-config.scale_factor * v for v in update.delta_params)
    elif config.attack_type == "scaled_update":
        corrupted = tuple(config.scale_factor * v for v in update.delta_params)
    elif config.attack_type == "random_update":
        corrupted = tuple(rng.gauss(0.0, config.random_std) for _ in range(d))
    elif config.attack_type == "model_replacement":
        corrupted = tuple(-config.scale_factor * (v + 0.5) for v in update.delta_params)
    else:
        raise ValueError(f"Unsupported Byzantine attack_type: '{config.attack_type}'")

    return ClientUpdate(
        client_id=update.client_id,
        is_simulated=True,
        num_samples=update.num_samples,
        delta_params=corrupted,
        train_loss=update.train_loss,
        val_loss=update.val_loss,
        bytes_sent=update.bytes_sent,
    )
