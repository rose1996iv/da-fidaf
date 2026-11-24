"""L2 update clipping, exact RDP Gaussian accounting, and SecAgg threat-model interface.

Capability Disclosure:
- `clip_update_l2` and `add_gaussian_dp_noise` implement bounded L2 clipping and
  additive Gaussian perturbation with exact Renyi Differential Privacy (RDP)
  composition accounting (Mironov 2017, Propositions 3 & 7) valid for all sigma > 0
  and delta in (0, 1), without claiming subsampling amplification.
- Randomness uses Python's deterministic `random.Random` (Mersenne Twister) for
  reproducible research simulation ONLY; it is NOT a cryptographically secure CSPRNG
  for production deployment DP (`formal_deployment_dp_claim: False`).
- `SecureAggregationInterface` is a documented interface + threat model ONLY;
  cryptographic secure aggregation is NOT implemented and is explicitly reported
  as `secure_aggregation_active: False`.
"""

from __future__ import annotations

import math
import random
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass


class SecureAggregationNotImplementedError(NotImplementedError):
    """Raised if unimplemented cryptographic secure aggregation is invoked."""


@dataclass(frozen=True, slots=True)
class DPConfig:
    """Configuration for client-level L2 clipping and Gaussian DP noise."""

    enabled: bool = False
    max_grad_norm: float = 1.0
    noise_multiplier: float = 0.0
    delta: float = 1e-5
    dp_scope: str = "local_per_client"  # "local_per_client" or "central_aggregate"

    def __post_init__(self) -> None:
        if self.max_grad_norm <= 0.0 or not math.isfinite(self.max_grad_norm):
            raise ValueError(f"max_grad_norm must be finite and > 0; got {self.max_grad_norm}")
        if self.noise_multiplier < 0.0 or not math.isfinite(self.noise_multiplier):
            raise ValueError(
                f"noise_multiplier must be finite and >= 0; got {self.noise_multiplier}"
            )
        if not (0.0 < self.delta < 1.0) or not math.isfinite(self.delta):
            raise ValueError(f"delta must satisfy 0 < delta < 1; got {self.delta}")
        if self.dp_scope not in ("local_per_client", "central_aggregate"):
            raise ValueError(
                f"dp_scope must be 'local_per_client' or 'central_aggregate'; got {self.dp_scope!r}"
            )


def clip_update_l2(update: Sequence[float], max_norm: float) -> tuple[list[float], float]:
    """Clip a flat parameter update vector to L2 norm <= max_norm."""
    if max_norm <= 0.0 or not math.isfinite(max_norm):
        raise ValueError("max_norm must be finite and > 0.")
    vals = [float(v) for v in update]
    if not all(math.isfinite(v) for v in vals):
        raise ValueError("Cannot clip update containing NaN or Inf values.")
    norm = math.sqrt(sum(v * v for v in vals))
    if norm <= max_norm or norm == 0.0:
        return vals, norm
    scale = max_norm / norm
    return [v * scale for v in vals], norm


def add_gaussian_dp_noise(
    update: Sequence[float],
    *,
    max_norm: float,
    noise_multiplier: float,
    seed: int = 42,
) -> list[float]:
    """Apply L2 clipping followed by zero-mean Gaussian noise N(0, (sigma*C)^2)."""
    if noise_multiplier < 0.0 or not math.isfinite(noise_multiplier):
        raise ValueError("noise_multiplier must be finite and >= 0.")
    clipped, _ = clip_update_l2(update, max_norm)
    if noise_multiplier == 0.0:
        return clipped
    sigma = noise_multiplier * max_norm
    rng = random.Random(seed)
    return [v + rng.gauss(0.0, sigma) for v in clipped]


def compute_rdp_gaussian_epsilon(
    *,
    rounds: int,
    noise_multiplier: float,
    delta: float,
) -> float:
    """Exact closed-form RDP-to-(eps, delta) bound for T adaptive Gaussian rounds.

    For add/remove-one-client adjacency with L2 sensitivity C and noise std sigma*C,
    each round satisfies (alpha, alpha / (2*sigma^2))-RDP for all alpha > 1.
    Under adaptive composition across T rounds (no subsampling amplification assumed,
    hence valid conservatively for any participation rate q <= 1):
        eps_RDP(alpha) = T * alpha / (2 * sigma^2)
    Converting to (eps, delta)-DP via Mironov (2017) Proposition 3 and minimizing
    analytically over alpha > 1 gives:
        alpha* = 1 + sqrt(2 * sigma^2 * ln(1 / delta) / T)
        eps(delta) = T / (2 * sigma^2) + sqrt(2 * T * ln(1 / delta) / sigma^2)
    Valid for all sigma > 0, T >= 1, and 0 < delta < 1 (no eps <= 1 restriction).
    """
    if rounds < 0:
        raise ValueError("rounds must be >= 0.")
    if rounds == 0:
        return 0.0
    if not (0.0 < delta < 1.0):
        raise ValueError(f"delta must satisfy 0 < delta < 1; got {delta}")
    if noise_multiplier <= 0.0:
        return math.inf
    inv_sig2 = 1.0 / (noise_multiplier * noise_multiplier)
    return 0.5 * rounds * inv_sig2 + math.sqrt(2.0 * rounds * math.log(1.0 / delta) * inv_sig2)


class PrivacyAccountant:
    """Exact RDP Gaussian composition accountant (simulation-grade PRNG disclosed)."""

    def __init__(self, config: DPConfig) -> None:
        self.config = config
        self.rounds_accounted: int = 0
        self.cumulative_epsilon_upper: float = 0.0

    def step(self) -> float:
        self.rounds_accounted += 1
        if not self.config.enabled or self.config.noise_multiplier <= 0.0:
            self.cumulative_epsilon_upper = math.inf
            return self.cumulative_epsilon_upper
        self.cumulative_epsilon_upper = compute_rdp_gaussian_epsilon(
            rounds=self.rounds_accounted,
            noise_multiplier=self.config.noise_multiplier,
            delta=self.config.delta,
        )
        return self.cumulative_epsilon_upper

    def summary(self) -> dict[str, object]:
        return {
            "dp_enabled": self.config.enabled,
            "dp_scope": self.config.dp_scope,
            "max_grad_norm": self.config.max_grad_norm,
            "noise_multiplier": self.config.noise_multiplier,
            "delta": self.config.delta,
            "rounds_accounted": self.rounds_accounted,
            "cumulative_epsilon_upper": (
                None
                if math.isinf(self.cumulative_epsilon_upper)
                else round(self.cumulative_epsilon_upper, 6)
            ),
            "accounting_method": "exact_rdp_gaussian_composition_no_subsampling_amplification",
            "adjacency_assumption": "add_remove_one_client_l2_clip_C",
            "prng_mode": "simulation_only_mersenne_twister_non_cryptographic",
            "formal_deployment_dp_claim": False,
            "secure_aggregation_active": False,
        }


class SecureAggregationInterface(ABC):
    """Documented interface for future cryptographic secure aggregation (NOT active).

    Threat Model: Honest-but-curious aggregation server; protects individual client
    updates via pairwise masking / threshold secret sharing (e.g., Bonawitz et al.).
    """

    @abstractmethod
    def mask_update(self, client_id: str, update: Sequence[float], round_id: int) -> list[float]:
        """Mask a client update before transmission."""

    @abstractmethod
    def aggregate_masked(self, masked_updates: Sequence[Sequence[float]]) -> list[float]:
        """Recover aggregate sum from masked client updates."""
