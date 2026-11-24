"""Framework-independent model interface and pure-Python regularized logistic IDS baseline."""

from __future__ import annotations

import math
import random
from abc import ABC, abstractmethod
from collections.abc import Sequence


def _sigmoid(z: float) -> float:
    if z >= 0.0:
        ez = math.exp(-min(z, 60.0))
        return 1.0 / (1.0 + ez)
    ez = math.exp(max(z, -60.0))
    return ez / (1.0 + ez)


class ModelInterface(ABC):
    """Minimal framework-independent model contract for FL orchestration."""

    @property
    @abstractmethod
    def num_features(self) -> int:
        """Expected input feature dimension."""

    @abstractmethod
    def get_parameters(self) -> list[float]:
        """Return flat copy of trainable parameters."""

    @abstractmethod
    def set_parameters(self, params: Sequence[float]) -> None:
        """Load flat parameter vector into the model."""

    @abstractmethod
    def predict_proba(self, x_rows: Sequence[Sequence[float]]) -> list[float]:
        """Return positive-class probability per row."""

    def predict(self, x_rows: Sequence[Sequence[float]], threshold: float = 0.5) -> list[int]:
        return [1 if p >= threshold else 0 for p in self.predict_proba(x_rows)]

    @abstractmethod
    def fit_local(
        self,
        x_rows: Sequence[Sequence[float]],
        y_rows: Sequence[int],
        *,
        epochs: int = 1,
        batch_size: int = 32,
        lr: float = 0.05,
        l2_reg: float = 1e-4,
        proximal_mu: float = 0.0,
        global_params: Sequence[float] | None = None,
        seed: int = 42,
    ) -> float:
        """Run deterministic local SGD (FedAvg when proximal_mu=0, FedProx when >0)."""


class LinearLogisticIDS(ModelInterface):
    """Deterministic L2-regularized binary logistic regression IDS baseline."""

    def __init__(self, n_features: int, seed: int = 42) -> None:
        if n_features < 1:
            raise ValueError("n_features must be >= 1.")
        self._n_features = n_features
        rng = random.Random(seed)
        scale = 0.05 / math.sqrt(n_features)
        # Last entry is bias term
        self._params: list[float] = [rng.uniform(-scale, scale) for _ in range(n_features)] + [0.0]

    @property
    def num_features(self) -> int:
        return self._n_features

    def get_parameters(self) -> list[float]:
        return list(self._params)

    def set_parameters(self, params: Sequence[float]) -> None:
        if len(params) != self._n_features + 1:
            raise ValueError(f"Expected {self._n_features + 1} params, got {len(params)}.")
        self._params = [float(p) for p in params]

    def predict_proba(self, x_rows: Sequence[Sequence[float]]) -> list[float]:
        w = self._params
        d = self._n_features
        b = w[d]
        probs: list[float] = []
        for row in x_rows:
            z = b + sum(w[j] * row[j] for j in range(d))
            probs.append(_sigmoid(z))
        return probs

    def evaluate_loss(self, x_rows: Sequence[Sequence[float]], y_rows: Sequence[int]) -> float:
        if not x_rows:
            return 0.0
        probs = self.predict_proba(x_rows)
        eps = 1e-12
        total = 0.0
        for p, y in zip(probs, y_rows, strict=True):
            pc = min(1.0 - eps, max(eps, p))
            total += -(y * math.log(pc) + (1 - y) * math.log(1.0 - pc))
        return total / len(x_rows)

    def fit_local(
        self,
        x_rows: Sequence[Sequence[float]],
        y_rows: Sequence[int],
        *,
        epochs: int = 1,
        batch_size: int = 32,
        lr: float = 0.05,
        l2_reg: float = 1e-4,
        proximal_mu: float = 0.0,
        global_params: Sequence[float] | None = None,
        seed: int = 42,
    ) -> float:
        n = len(x_rows)
        if n == 0:
            return 0.0
        d = self._n_features
        rng = random.Random(seed)
        indices = list(range(n))
        anchor = list(global_params) if global_params is not None else list(self._params)

        for _ep in range(max(1, epochs)):
            rng.shuffle(indices)
            for start in range(0, n, max(1, batch_size)):
                batch = indices[start : start + max(1, batch_size)]
                m = len(batch)
                grads = [0.0] * (d + 1)
                w = self._params
                b = w[d]
                for i in batch:
                    row = x_rows[i]
                    z = b + sum(w[j] * row[j] for j in range(d))
                    err = _sigmoid(z) - y_rows[i]
                    for j in range(d):
                        grads[j] += err * row[j]
                    grads[d] += err

                inv_m = 1.0 / m
                for j in range(d):
                    g = grads[j] * inv_m + l2_reg * w[j]
                    if proximal_mu > 0.0:
                        g += proximal_mu * (w[j] - anchor[j])
                    w[j] -= lr * g
                gb = grads[d] * inv_m
                if proximal_mu > 0.0:
                    gb += proximal_mu * (w[d] - anchor[d])
                w[d] -= lr * gb

        return self.evaluate_loss(x_rows, y_rows)
