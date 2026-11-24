"""Federated aggregation strategies: FedAvg, Coordinate Median, Trimmed Mean, Krum, Multi-Krum.

Algorithmic Assumptions & Limitations:
- FedAvg: Optimal under honest clients; vulnerable to a single unbounded Byzantine update.
- Coordinate Median / Trimmed Mean: Tolerate up to <50% (or beta < 0.5) coordinate outliers;
  can degrade under extreme Non-IID label skew where honest updates naturally diverge.
- Krum / Multi-Krum: Require n >= 2f + 3 clients (where f is assumed Byzantine count);
  assumes honest updates cluster in L2 distance, which weakens under severe Non-IID skew.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from dafidaf.federated.client import ClientUpdate


class AggregationError(ValueError):
    """Raised when aggregation preconditions (e.g., n >= 2f + 3 for Krum) are violated."""


def filter_finite_updates(
    updates: Sequence[ClientUpdate],
) -> tuple[list[ClientUpdate], list[str]]:
    """Separate finite client updates from corrupted NaN/Inf updates."""
    valid: list[ClientUpdate] = []
    rejected: list[str] = []
    for u in updates:
        if all(math.isfinite(v) for v in u.delta_params):
            valid.append(u)
        else:
            rejected.append(u.client_id)
    return valid, rejected


def _validate_updates(updates: Sequence[ClientUpdate]) -> int:
    if not updates:
        raise AggregationError("Cannot aggregate an empty list of client updates.")
    dim = len(updates[0].delta_params)
    if dim == 0:
        raise AggregationError("Client update parameter vector cannot be empty.")
    for u in updates:
        if not u.client_id or not u.client_id.strip():
            raise AggregationError("Client update must have a non-empty client_id.")
        if u.num_samples <= 0:
            raise AggregationError(
                f"Client '{u.client_id}' reported invalid num_samples={u.num_samples} (must > 0)."
            )
        if len(u.delta_params) != dim:
            raise AggregationError("All client updates must have identical parameter dimension.")
        if not all(math.isfinite(v) for v in u.delta_params):
            raise AggregationError(
                f"Non-finite (NaN/Inf) parameter value detected in update from '{u.client_id}'."
            )
    return dim


def fedavg(updates: Sequence[ClientUpdate]) -> list[float]:
    """Sample-weighted Federated Averaging (McMahan et al.)."""
    dim = _validate_updates(updates)
    total_n = sum(u.num_samples for u in updates)
    agg = [0.0] * dim
    for u in updates:
        w = u.num_samples / total_n
        for j in range(dim):
            agg[j] += w * u.delta_params[j]
    return agg


def coordinate_median(updates: Sequence[ClientUpdate]) -> list[float]:
    """Coordinate-wise median aggregation."""
    dim = _validate_updates(updates)
    n = len(updates)
    agg = [0.0] * dim
    for j in range(dim):
        col = sorted(u.delta_params[j] for u in updates)
        mid = n // 2
        agg[j] = col[mid] if n % 2 == 1 else 0.5 * (col[mid - 1] + col[mid])
    return agg


def trimmed_mean(updates: Sequence[ClientUpdate], trim_ratio: float = 0.2) -> list[float]:
    """Coordinate-wise trimmed mean discarding top/bottom trim_ratio fraction."""
    dim = _validate_updates(updates)
    if not (0.0 <= trim_ratio < 0.5):
        raise AggregationError("trim_ratio must satisfy 0.0 <= trim_ratio < 0.5.")
    n = len(updates)
    k = int(math.floor(trim_ratio * n))
    if n - 2 * k < 1:
        raise AggregationError(f"trim_ratio={trim_ratio} trims all updates for n={n}.")
    agg = [0.0] * dim
    for j in range(dim):
        col = sorted(u.delta_params[j] for u in updates)
        kept = col[k : n - k] if k > 0 else col
        agg[j] = sum(kept) / len(kept)
    return agg


def _l2_dist_sq(a: Sequence[float], b: Sequence[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b, strict=True))


def krum(updates: Sequence[ClientUpdate], num_byzantine: int = 1) -> list[float]:
    """Single-Krum selection (requires n >= 2f + 3)."""
    return multi_krum(updates, num_byzantine=num_byzantine, m=1)


def multi_krum(
    updates: Sequence[ClientUpdate],
    num_byzantine: int = 1,
    m: int | None = None,
) -> list[float]:
    """Multi-Krum aggregation selecting m lowest-distance-score updates (requires n >= 2f + 3)."""
    dim = _validate_updates(updates)
    n = len(updates)
    f = num_byzantine
    if f < 0:
        raise AggregationError(f"num_byzantine must be >= 0; got f={f}.")
    if n < 2 * f + 3:
        raise AggregationError(
            f"Krum/Multi-Krum requires n >= 2f + 3; got n={n}, f={f} (minimum {2 * f + 3})."
        )
    keep_m = (n - f - 2) if m is None else m
    if not (1 <= keep_m <= n):
        raise AggregationError(f"Invalid Multi-Krum selection count m={keep_m} for n={n}.")

    neighbors = n - f - 2
    scores: list[tuple[float, int]] = []
    for i in range(n):
        dists = sorted(
            _l2_dist_sq(updates[i].delta_params, updates[k].delta_params)
            for k in range(n)
            if k != i
        )
        scores.append((sum(dists[:neighbors]), i))
    scores.sort(key=lambda x: (x[0], x[1]))
    chosen = [updates[idx] for _, idx in scores[:keep_m]]
    agg = [0.0] * dim
    for u in chosen:
        for j in range(dim):
            agg[j] += u.delta_params[j] / len(chosen)
    return agg


def aggregate_updates(
    updates: Sequence[ClientUpdate],
    *,
    method: str = "fedavg",
    trim_ratio: float = 0.2,
    num_byzantine: int = 1,
    multi_krum_m: int | None = None,
) -> list[float]:
    """Dispatch aggregation strategy by name."""
    if method == "fedavg":
        return fedavg(updates)
    if method == "median":
        return coordinate_median(updates)
    if method == "trimmed_mean":
        return trimmed_mean(updates, trim_ratio=trim_ratio)
    if method == "krum":
        return krum(updates, num_byzantine=num_byzantine)
    if method == "multi_krum":
        return multi_krum(updates, num_byzantine=num_byzantine, m=multi_krum_m)
    raise AggregationError(f"Unknown aggregation method: '{method}'")
