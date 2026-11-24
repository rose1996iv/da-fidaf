"""Controlled synthetic drift generators, drift detectors, and continual adaptation."""

from __future__ import annotations

import bisect
import math
import random
from collections.abc import Sequence
from dataclasses import dataclass

from dafidaf.models.logistic import LinearLogisticIDS


@dataclass(frozen=True, slots=True)
class DriftSpec:
    """Versioned specification for explicitly labeled synthetic drift simulations."""

    schedule: str  # "abrupt", "gradual", "recurring"
    mechanism: str  # "covariate_shift", "prior_shift", "conditional_concept_drift"
    onset_round: int = 4
    duration_rounds: int = 3
    severity: float = 1.5
    seed: int = 42
    is_synthetic: bool = True


def _schedule_intensity(spec: DriftSpec, round_id: int) -> float:
    if round_id < spec.onset_round:
        return 0.0
    elapsed = round_id - spec.onset_round
    if spec.schedule == "abrupt":
        return 1.0
    if spec.schedule == "gradual":
        return min(1.0, (elapsed + 1) / max(1, spec.duration_rounds))
    if spec.schedule == "recurring":
        period = max(2, spec.duration_rounds)
        return 1.0 if ((elapsed // period) % 2 == 0) else 0.0
    raise ValueError(f"Unsupported drift schedule: '{spec.schedule}'")


def apply_synthetic_drift(
    x_rows: Sequence[Sequence[float]],
    y_rows: Sequence[int],
    spec: DriftSpec,
    *,
    round_id: int,
) -> tuple[list[list[float]], list[int], dict[str, object]]:
    """Apply controlled synthetic drift to in-memory copies (never mutates inputs)."""
    intensity = _schedule_intensity(spec, round_id)
    x_out = [list(r) for r in x_rows]
    y_out = [int(y) for y in y_rows]
    rng = random.Random(spec.seed + round_id)

    if intensity > 0.0 and x_out:
        d = len(x_out[0])
        if spec.mechanism == "covariate_shift":
            # Shift P_t(X) while keeping P(Y|X) intact
            shift = spec.severity * intensity
            for row in x_out:
                for j in range(min(3, d)):
                    row[j] += shift + rng.gauss(0.0, 0.1 * intensity)
        elif spec.mechanism == "prior_shift":
            # Rebalance P_t(Y) by duplicating/subsampling positive class in-memory
            pos_idx = [i for i, y in enumerate(y_out) if y == 1]
            neg_idx = [i for i, y in enumerate(y_out) if y == 0]
            if pos_idx and neg_idx:
                n_extra = int(round(len(pos_idx) * 0.5 * intensity * min(2.0, spec.severity)))
                for _ in range(n_extra):
                    pick = rng.choice(pos_idx)
                    x_out.append(list(x_out[pick]))
                    y_out.append(1)
        elif spec.mechanism == "conditional_concept_drift":
            # Alter P_t(Y|X) decision boundary for a fraction proportional to intensity
            flip_prob = min(0.5, 0.25 * spec.severity * intensity)
            for i, row in enumerate(x_out):
                if row[0] > 0.0 and rng.random() < flip_prob:
                    y_out[i] = 1 - y_out[i]
        else:
            raise ValueError(f"Unsupported drift mechanism: '{spec.mechanism}'")

    meta: dict[str, object] = {
        "is_synthetic": True,
        "schedule": spec.schedule,
        "mechanism": spec.mechanism,
        "round_id": round_id,
        "intensity": round(intensity, 4),
    }
    return x_out, y_out, meta


@dataclass(frozen=True, slots=True)
class DriftDetectionResult:
    """Feature-level covariate drift summary against a baseline reference window."""

    mean_psi: float
    max_psi: float
    mean_jsd_bits: float
    per_feature_psi: dict[str, float]
    drift_detected: bool
    threshold_psi: float


class FeatureDriftDetector:
    """Baseline-fitted PSI & JSD covariate shift detector."""

    def __init__(self, psi_threshold: float = 0.25, n_bins: int = 10) -> None:
        self.psi_threshold = psi_threshold
        self.n_bins = n_bins
        self._edges: list[list[float]] = []
        self._ref_probs: list[list[float]] = []
        self._feature_names: tuple[str, ...] = ()

    @staticmethod
    def _hist_probs(vals: Sequence[float], edges: Sequence[float]) -> list[float]:
        k = len(edges) + 1
        counts = [0] * k
        for v in vals:
            counts[bisect.bisect_right(edges, v)] += 1
        n = max(1, len(vals))
        eps = 1e-6
        probs = [(c / n) + eps for c in counts]
        s = sum(probs)
        return [p / s for p in probs]

    def fit_reference(
        self,
        x_ref: Sequence[Sequence[float]],
        feature_names: Sequence[str] | None = None,
    ) -> FeatureDriftDetector:
        if not x_ref:
            raise ValueError("Reference window cannot be empty.")
        d = len(x_ref[0])
        self._feature_names = (
            tuple(feature_names) if feature_names is not None else tuple(f"f{j}" for j in range(d))
        )
        self._edges = []
        self._ref_probs = []
        for j in range(d):
            col = sorted(r[j] for r in x_ref)
            m = len(col)
            edges = sorted(
                {col[min(m - 1, int(i * m / self.n_bins))] for i in range(1, self.n_bins)}
            )
            self._edges.append(edges)
            self._ref_probs.append(self._hist_probs(col, edges))
        return self

    def detect(self, x_curr: Sequence[Sequence[float]]) -> DriftDetectionResult:
        if not self._edges:
            raise RuntimeError("FeatureDriftDetector must call fit_reference() first.")
        if not x_curr:
            raise ValueError("Current window cannot be empty.")
        per_psi: dict[str, float] = {}
        jsds: list[float] = []
        for j, name in enumerate(self._feature_names):
            col = [r[j] for r in x_curr]
            pa = self._ref_probs[j]
            pb = self._hist_probs(col, self._edges[j])
            psi = sum((b - a) * math.log(b / a) for a, b in zip(pa, pb, strict=True))
            mm = [0.5 * (a + b) for a, b in zip(pa, pb, strict=True)]
            jsd = 0.5 * sum(a * math.log2(a / m) for a, m in zip(pa, mm, strict=True)) + 0.5 * sum(
                b * math.log2(b / m) for b, m in zip(pb, mm, strict=True)
            )
            per_psi[name] = round(psi, 6)
            jsds.append(jsd)

        vals = list(per_psi.values())
        mean_psi = sum(vals) / len(vals)
        max_psi = max(vals)
        mean_jsd = sum(jsds) / len(jsds)
        return DriftDetectionResult(
            mean_psi=round(mean_psi, 6),
            max_psi=round(max_psi, 6),
            mean_jsd_bits=round(mean_jsd, 6),
            per_feature_psi=per_psi,
            drift_detected=max_psi >= self.psi_threshold,
            threshold_psi=self.psi_threshold,
        )


class PageHinkleyDetector:
    """Sequential Page-Hinkley change detector for online error/loss streams."""

    def __init__(self, delta: float = 0.005, threshold: float = 0.2, min_samples: int = 3) -> None:
        self.delta = delta
        self.threshold = threshold
        self.min_samples = min_samples
        self._n = 0
        self._mean = 0.0
        self._cum = 0.0
        self._min_cum = 0.0

    def reset(self) -> None:
        """Reset cumulative statistics after a detected change point."""
        self._n = 0
        self._mean = 0.0
        self._cum = 0.0
        self._min_cum = 0.0

    def update(self, value: float) -> bool:
        self._n += 1
        self._mean += (value - self._mean) / self._n
        self._cum += value - self._mean - self.delta
        if self._cum < self._min_cum:
            self._min_cum = self._cum
        return self._n >= self.min_samples and (self._cum - self._min_cum) > self.threshold


@dataclass(frozen=True, slots=True)
class AdaptationResult:
    """Outcome of continual adaptation including catastrophic forgetting measurement."""

    strategy: str
    prior_loss_before: float
    prior_loss_after: float
    new_loss_after: float
    forgetting_delta: float  # > 0 indicates forgetting on prior distribution


class ContinualAdapter:
    """Continual adaptation supporting replay, regularized, and fine_tune strategies."""

    def __init__(
        self, strategy: str = "replay", replay_ratio: float = 0.5, reg_mu: float = 0.2
    ) -> None:
        if strategy not in ("replay", "regularized", "fine_tune"):
            raise ValueError(f"Unsupported adaptation strategy: '{strategy}'")
        self.strategy = strategy
        self.replay_ratio = replay_ratio
        self.reg_mu = reg_mu

    def adapt(
        self,
        model: LinearLogisticIDS,
        x_new: Sequence[Sequence[float]],
        y_new: Sequence[int],
        x_replay: Sequence[Sequence[float]],
        y_replay: Sequence[int],
        *,
        epochs: int = 3,
        lr: float = 0.05,
        seed: int = 42,
    ) -> AdaptationResult:
        prior_before = model.evaluate_loss(x_replay, y_replay)
        anchor = model.get_parameters()
        rng = random.Random(seed)

        if self.strategy == "replay" and x_replay:
            k_rep = max(1, int(round(len(x_new) * self.replay_ratio)))
            idxs = [rng.randrange(len(x_replay)) for _ in range(min(k_rep, len(x_replay)))]
            x_mix = [list(r) for r in x_new] + [list(x_replay[i]) for i in idxs]
            y_mix = [int(y) for y in y_new] + [int(y_replay[i]) for i in idxs]
            model.fit_local(x_mix, y_mix, epochs=epochs, lr=lr, seed=seed)
        elif self.strategy == "regularized":
            model.fit_local(
                x_new,
                y_new,
                epochs=epochs,
                lr=lr,
                proximal_mu=self.reg_mu,
                global_params=anchor,
                seed=seed,
            )
        else:
            model.fit_local(x_new, y_new, epochs=epochs, lr=lr, seed=seed)

        prior_after = model.evaluate_loss(x_replay, y_replay)
        new_after = model.evaluate_loss(x_new, y_new)
        return AdaptationResult(
            strategy=self.strategy,
            prior_loss_before=round(prior_before, 6),
            prior_loss_after=round(prior_after, 6),
            new_loss_after=round(new_after, 6),
            forgetting_delta=round(prior_after - prior_before, 6),
        )
