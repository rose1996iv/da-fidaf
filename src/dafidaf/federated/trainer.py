"""Round-based Federated Learning orchestration with checkpointing and privacy hooks."""

from __future__ import annotations

import json
import os
import random
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from dafidaf.federated.aggregation import aggregate_updates, filter_finite_updates
from dafidaf.federated.client import ClientUpdate, SimulatedClient
from dafidaf.models.logistic import LinearLogisticIDS, ModelInterface
from dafidaf.privacy.mechanisms import (
    DPConfig,
    PrivacyAccountant,
    add_gaussian_dp_noise,
    clip_update_l2,
)


@dataclass(frozen=True, slots=True)
class FederatedConfig:
    """Reproducible FL training configuration."""

    rounds: int = 10
    local_epochs: int = 2
    batch_size: int = 32
    lr: float = 0.05
    l2_reg: float = 1e-4
    proximal_mu: float = 0.0  # > 0 enables FedProx
    participation_rate: float = 1.0
    aggregation: str = "fedavg"
    trim_ratio: float = 0.2
    num_byzantine: int = 1
    seed: int = 42
    dp: DPConfig = DPConfig()


@dataclass(frozen=True, slots=True)
class RoundResult:
    """Per-round telemetry and evaluation summary."""

    round_id: int
    participating_clients: tuple[str, ...]
    mean_train_loss: float
    global_val_loss: float | None
    total_bytes_communicated: int
    elapsed_seconds: float
    client_updates: tuple[ClientUpdate, ...]
    rejected_nonfinite_clients: tuple[str, ...] = ()
    quarantined_attributed_clients: tuple[str, ...] = ()


UpdateTransform = Callable[[int, ClientUpdate], ClientUpdate]
AttributionFilter = Callable[
    [int, Sequence[float], Sequence[ClientUpdate]], tuple[list[ClientUpdate], list[str]]
]


class FederatedTrainer:
    """Framework-independent FL round coordinator (never touches test set during training)."""

    def __init__(
        self,
        model: ModelInterface,
        clients: Sequence[SimulatedClient],
        config: FederatedConfig | None = None,
        *,
        update_hook: UpdateTransform | None = None,
        attribution_filter: AttributionFilter | None = None,
        checkpoint_dir: Path | None = None,
    ) -> None:
        if not clients:
            raise ValueError("FederatedTrainer requires at least one simulated client.")
        self.model = model
        self.clients = list(clients)
        self.config = config or FederatedConfig()
        self.update_hook = update_hook
        self.attribution_filter = attribution_filter
        self.checkpoint_dir = checkpoint_dir
        self.accountant = PrivacyAccountant(self.config.dp)
        self.history: list[RoundResult] = []

    def run(
        self,
        *,
        x_val: Sequence[Sequence[float]] | None = None,
        y_val: Sequence[int] | None = None,
    ) -> list[RoundResult]:
        cfg = self.config
        rng = random.Random(cfg.seed)
        n_select = max(1, int(round(len(self.clients) * cfg.participation_rate)))

        for r_id in range(1, cfg.rounds + 1):
            t0 = time.monotonic()
            selected = (
                list(self.clients)
                if n_select >= len(self.clients)
                else rng.sample(self.clients, n_select)
            )
            global_params = self.model.get_parameters()
            updates: list[ClientUpdate] = []

            for c_idx, client in enumerate(selected):
                upd = client.train_round(
                    global_params,
                    epochs=cfg.local_epochs,
                    batch_size=cfg.batch_size,
                    lr=cfg.lr,
                    l2_reg=cfg.l2_reg,
                    proximal_mu=cfg.proximal_mu,
                    seed=cfg.seed + r_id * 1000 + c_idx,
                )
                # Under local_per_client DP, honest clients clip & add noise locally BEFORE
                # any adversarial/Byzantine update_hook acts (malicious clients need not obey DP).
                if cfg.dp.enabled and cfg.dp.dp_scope == "local_per_client":
                    noisy = add_gaussian_dp_noise(
                        upd.delta_params,
                        max_norm=cfg.dp.max_grad_norm,
                        noise_multiplier=cfg.dp.noise_multiplier,
                        seed=cfg.seed + r_id * 10000 + c_idx,
                    )
                    upd = ClientUpdate(
                        client_id=upd.client_id,
                        is_simulated=upd.is_simulated,
                        num_samples=upd.num_samples,
                        delta_params=tuple(noisy),
                        train_loss=upd.train_loss,
                        val_loss=upd.val_loss,
                        bytes_sent=upd.bytes_sent,
                    )
                if self.update_hook is not None:
                    upd = self.update_hook(r_id, upd)
                updates.append(upd)

            finite_updates, rejected_ids = filter_finite_updates(updates)
            quarantined_ids: list[str] = []
            agg_inputs = finite_updates
            if self.attribution_filter is not None and finite_updates:
                filtered_updates, quarantined_ids = self.attribution_filter(
                    r_id, global_params, finite_updates
                )
                if filtered_updates:
                    agg_inputs = filtered_updates

            # Under central_aggregate DP, server clips finite updates to C, aggregates,
            # and adds Gaussian noise scaled to the aggregate sensitivity (C * max_w).
            if cfg.dp.enabled and cfg.dp.dp_scope == "central_aggregate":
                clipped_inputs: list[ClientUpdate] = []
                for u in agg_inputs:
                    clipped_delta, _ = clip_update_l2(u.delta_params, cfg.dp.max_grad_norm)
                    clipped_inputs.append(
                        ClientUpdate(
                            client_id=u.client_id,
                            is_simulated=u.is_simulated,
                            num_samples=u.num_samples,
                            delta_params=tuple(clipped_delta),
                            train_loss=u.train_loss,
                            val_loss=u.val_loss,
                            bytes_sent=u.bytes_sent,
                        )
                    )
                agg_inputs = clipped_inputs

            agg_delta = aggregate_updates(
                agg_inputs,
                method=cfg.aggregation,
                trim_ratio=cfg.trim_ratio,
                num_byzantine=cfg.num_byzantine,
            )
            if (
                cfg.dp.enabled
                and cfg.dp.dp_scope == "central_aggregate"
                and cfg.dp.noise_multiplier > 0.0
            ):
                if cfg.aggregation == "fedavg":
                    total_n = sum(u.num_samples for u in agg_inputs)
                    max_w = max(u.num_samples / total_n for u in agg_inputs)
                else:
                    max_w = 1.0
                central_sigma = cfg.dp.noise_multiplier * cfg.dp.max_grad_norm * max_w
                noise_rng = random.Random(cfg.seed + r_id * 100000)
                agg_delta = [v + noise_rng.gauss(0.0, central_sigma) for v in agg_delta]

            new_global = [g + d for g, d in zip(global_params, agg_delta, strict=True)]
            self.model.set_parameters(new_global)
            self.accountant.step()

            val_loss: float | None = None
            if x_val and y_val and isinstance(self.model, LinearLogisticIDS):
                val_loss = self.model.evaluate_loss(x_val, y_val)

            mean_tr = sum(u.train_loss for u in finite_updates) / len(finite_updates)
            comm_bytes = sum(u.bytes_sent for u in updates) + len(new_global) * 8 * len(selected)
            res = RoundResult(
                round_id=r_id,
                participating_clients=tuple(u.client_id for u in updates),
                mean_train_loss=round(mean_tr, 6),
                global_val_loss=round(val_loss, 6) if val_loss is not None else None,
                total_bytes_communicated=comm_bytes,
                elapsed_seconds=round(time.monotonic() - t0, 6),
                client_updates=tuple(updates),
                rejected_nonfinite_clients=tuple(rejected_ids),
                quarantined_attributed_clients=tuple(quarantined_ids),
            )
            self.history.append(res)

            if self.checkpoint_dir is not None:
                self._save_checkpoint(r_id, new_global)

        return self.history

    def _save_checkpoint(self, round_id: int, params: Sequence[float]) -> None:
        assert self.checkpoint_dir is not None
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        ckpt = self.checkpoint_dir / f"checkpoint_round_{round_id:03d}.json"
        tmp = self.checkpoint_dir / f".checkpoint_round_{round_id:03d}.tmp"
        payload = {
            "round_id": round_id,
            "n_features": self.model.num_features,
            "aggregation": self.config.aggregation,
            "seed": self.config.seed,
            "parameters": list(params),
        }
        tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, ckpt)

    @staticmethod
    def load_checkpoint(ckpt_path: Path) -> dict[str, object]:
        """Load a saved FL round checkpoint JSON."""
        data = json.loads(ckpt_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "parameters" not in data:
            raise ValueError(f"Invalid checkpoint structure: '{ckpt_path}'")
        return data
