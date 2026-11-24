"""Gate B unit tests: models, FedAvg, FedProx, robust aggregators, trainer, privacy."""

from __future__ import annotations

from pathlib import Path

import pytest

from dafidaf.federated import (
    AggregationError,
    ClientUpdate,
    FederatedConfig,
    FederatedTrainer,
    SimulatedClient,
    aggregate_updates,
)
from dafidaf.models import LinearLogisticIDS
from dafidaf.privacy import DPConfig, PrivacyAccountant, add_gaussian_dp_noise, clip_update_l2


def test_simulated_client_requires_sim_prefix() -> None:
    with pytest.raises(ValueError, match="sim_"):
        SimulatedClient("gw_01", [[0.0, 1.0]], [0])


def test_aggregators_and_byzantine_rejection() -> None:
    honest = [
        ClientUpdate(f"sim_gw_{i:02d}", True, 100, (0.1, -0.1, 0.05), 0.3, None, 24)
        for i in range(1, 8)
    ]
    byz = ClientUpdate("sim_gw_08", True, 100, (-50.0, 50.0, -50.0), 2.0, None, 24)
    all_u = honest + [byz]

    med = aggregate_updates(all_u, method="median")
    tmean = aggregate_updates(all_u, method="trimmed_mean", trim_ratio=0.2)
    mkrum = aggregate_updates(all_u, method="multi_krum", num_byzantine=1)
    assert abs(med[0] - 0.1) < 1e-6
    assert abs(tmean[0] - 0.1) < 1e-6
    assert abs(mkrum[0] - 0.1) < 1e-6

    with pytest.raises(AggregationError):
        aggregate_updates(all_u[:4], method="krum", num_byzantine=1)


def test_fedavg_and_fedprox_deterministic_with_checkpointing(tmp_path: Path) -> None:
    x_pos = [[2.0, 2.0, 1.0]] * 15
    x_neg = [[-2.0, -2.0, -1.0]] * 15
    clients = [
        SimulatedClient(f"sim_gw_{i:02d}", x_pos + x_neg, [1] * 15 + [0] * 15) for i in range(1, 5)
    ]

    m1 = LinearLogisticIDS(3, seed=42)
    m2 = LinearLogisticIDS(3, seed=42)
    cfg = FederatedConfig(rounds=3, local_epochs=2, lr=0.1, proximal_mu=0.05, seed=42)

    t1 = FederatedTrainer(m1, clients, cfg, checkpoint_dir=tmp_path / "ckpts")
    t2 = FederatedTrainer(m2, clients, cfg)
    h1 = t1.run(x_val=x_pos + x_neg, y_val=[1] * 15 + [0] * 15)
    t2.run(x_val=x_pos + x_neg, y_val=[1] * 15 + [0] * 15)

    assert m1.get_parameters() == m2.get_parameters()
    assert h1[-1].mean_train_loss < h1[0].mean_train_loss
    assert (tmp_path / "ckpts" / "checkpoint_round_003.json").is_file()


def test_dp_clipping_and_accountant() -> None:
    clipped, orig_norm = clip_update_l2([3.0, 4.0], max_norm=1.0)
    assert abs(orig_norm - 5.0) < 1e-6
    assert abs((clipped[0] ** 2 + clipped[1] ** 2) ** 0.5 - 1.0) < 1e-6

    noisy1 = add_gaussian_dp_noise([0.5, 0.5], max_norm=1.0, noise_multiplier=1.0, seed=42)
    noisy2 = add_gaussian_dp_noise([0.5, 0.5], max_norm=1.0, noise_multiplier=1.0, seed=42)
    assert noisy1 == noisy2

    acc = PrivacyAccountant(DPConfig(enabled=True, max_grad_norm=1.0, noise_multiplier=1.2))
    eps = acc.step()
    assert eps > 0.0
    assert acc.summary()["secure_aggregation_active"] is False
