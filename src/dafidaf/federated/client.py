"""Simulated logical gateway FL client with strict local-state isolation."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from dafidaf.models.logistic import LinearLogisticIDS, ModelInterface


@dataclass(frozen=True, slots=True)
class ClientUpdate:
    """Model parameter delta and metadata returned by a simulated client."""

    client_id: str
    is_simulated: bool
    num_samples: int
    delta_params: tuple[float, ...]
    train_loss: float
    val_loss: float | None
    bytes_sent: int


class SimulatedClient:
    """Represents one simulated logical gateway client (explicitly NOT a physical device)."""

    def __init__(
        self,
        client_id: str,
        x_train: Sequence[Sequence[float]],
        y_train: Sequence[int],
        *,
        x_val: Sequence[Sequence[float]] | None = None,
        y_val: Sequence[int] | None = None,
    ) -> None:
        if not client_id.startswith("sim_"):
            raise ValueError(
                f"Simulated client_id must start with 'sim_' for explicit disclosure: '{client_id}'"
            )
        self.client_id = client_id
        self.is_simulated = True
        self.x_train = [list(r) for r in x_train]
        self.y_train = [int(y) for y in y_train]
        self.x_val = [list(r) for r in x_val] if x_val is not None else []
        self.y_val = [int(y) for y in y_val] if y_val is not None else []
        self.last_metrics: dict[str, float] = {}

    @property
    def num_samples(self) -> int:
        return len(self.x_train)

    def train_round(
        self,
        global_params: Sequence[float],
        *,
        epochs: int = 1,
        batch_size: int = 32,
        lr: float = 0.05,
        l2_reg: float = 1e-4,
        proximal_mu: float = 0.0,
        seed: int = 42,
        model_factory: type[ModelInterface] = LinearLogisticIDS,
    ) -> ClientUpdate:
        n_features = len(global_params) - 1
        local_model = model_factory(n_features, seed=seed)
        local_model.set_parameters(global_params)

        train_loss = local_model.fit_local(
            self.x_train,
            self.y_train,
            epochs=epochs,
            batch_size=batch_size,
            lr=lr,
            l2_reg=l2_reg,
            proximal_mu=proximal_mu,
            global_params=global_params,
            seed=seed,
        )
        new_params = local_model.get_parameters()
        delta = tuple(n - g for n, g in zip(new_params, global_params, strict=True))

        val_loss: float | None = None
        if self.x_val and isinstance(local_model, LinearLogisticIDS):
            val_loss = local_model.evaluate_loss(self.x_val, self.y_val)

        self.last_metrics = {"train_loss": train_loss}
        if val_loss is not None:
            self.last_metrics["val_loss"] = val_loss

        return ClientUpdate(
            client_id=self.client_id,
            is_simulated=True,
            num_samples=self.num_samples,
            delta_params=delta,
            train_loss=train_loss,
            val_loss=val_loss,
            bytes_sent=len(delta) * 8,  # float64 payload estimate
        )
