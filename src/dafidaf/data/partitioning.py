"""Chronological temporal splitting, event-level deduplication, and logical FL partitioning."""

from __future__ import annotations

import hashlib
import math
import random
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass


class TemporalLeakageError(RuntimeError):
    """Raised when a temporal split or client partition violates causal ordering."""


@dataclass(frozen=True, slots=True)
class TemporalSplitConfig:
    """Chronological 70/15/15 split configuration with embargo and active-flow exclusion."""

    train_ratio: float = 0.70
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    embargo_seconds: float = 300.0
    exclude_active_end_time: bool = True


@dataclass(frozen=True, slots=True)
class TemporalSplitResult:
    """Indices and audit metadata for a leakage-free chronological split."""

    train_indices: tuple[int, ...]
    val_indices: tuple[int, ...]
    test_indices: tuple[int, ...]
    discarded_embargo: int
    discarded_active_endtime: int
    train_end_ts: float
    val_start_ts: float
    val_end_ts: float
    test_start_ts: float


@dataclass(frozen=True, slots=True)
class ClientPartitionResult:
    """Simulated logical gateway FL client assignments strictly within training indices."""

    strategy: str
    seed: int
    n_clients: int
    partition_type: str  # Always explicitly "simulated_logical_gateway"
    client_indices: dict[str, tuple[int, ...]]


def deduplicate_event_flows(
    timestamps: Sequence[float],
    feature_rows: Sequence[Sequence[float | None]],
    stream_id: str = "default",
) -> tuple[int, ...]:
    """Deduplicate exact event-level flows keyed on (stream_id, ts, feature_hash).

    Preserves legitimate recurring traffic that shares feature vectors at distinct timestamps.
    """
    seen: set[tuple[str, float, str]] = set()
    kept: list[int] = []
    for i, (ts, row) in enumerate(zip(timestamps, feature_rows, strict=True)):
        sig = hashlib.blake2b(repr(tuple(row)).encode("utf-8"), digest_size=12).hexdigest()
        key = (stream_id, ts, sig)
        if key not in seen:
            seen.add(key)
            kept.append(i)
    return tuple(kept)


def chronological_split(
    timestamps: Sequence[float],
    durations: Sequence[float] | None = None,
    config: TemporalSplitConfig | None = None,
) -> TemporalSplitResult:
    """Perform leakage-free chronological splitting with embargo and active-flow exclusion."""
    cfg = config or TemporalSplitConfig()
    n = len(timestamps)
    if n < 10:
        raise ValueError("Need at least 10 timestamped records for chronological splitting.")
    if abs((cfg.train_ratio + cfg.val_ratio + cfg.test_ratio) - 1.0) > 1e-6:
        raise ValueError("Split ratios must sum to 1.0.")

    durs = durations if durations is not None else [0.0] * n
    # Deterministic stable sort by (timestamp, original_index)
    order = sorted(range(n), key=lambda i: (timestamps[i], i))

    i_tr = max(1, int(cfg.train_ratio * n))
    i_va = max(i_tr + 1, int((cfg.train_ratio + cfg.val_ratio) * n))
    t_tr_end = float(timestamps[order[i_tr - 1]])
    t_va_end = float(timestamps[order[i_va - 1]])

    val_floor = t_tr_end + cfg.embargo_seconds
    test_floor = t_va_end + cfg.embargo_seconds

    train_idx: list[int] = []
    val_idx: list[int] = []
    test_idx: list[int] = []
    disc_emb = 0
    disc_end = 0

    for idx in order:
        ts = float(timestamps[idx])
        dur = max(0.0, float(durs[idx]))
        if ts <= t_tr_end:
            crosses_train = (
                (ts + dur) > t_tr_end if cfg.embargo_seconds <= 0 else (ts + dur) >= val_floor
            )
            if cfg.exclude_active_end_time and crosses_train:
                disc_end += 1
            else:
                train_idx.append(idx)
        elif ts < val_floor:
            disc_emb += 1
        elif ts <= t_va_end:
            crosses_val = (
                (ts + dur) > t_va_end if cfg.embargo_seconds <= 0 else (ts + dur) >= test_floor
            )
            if cfg.exclude_active_end_time and crosses_val:
                disc_end += 1
            else:
                val_idx.append(idx)
        elif ts < test_floor:
            disc_emb += 1
        else:
            test_idx.append(idx)

    if not train_idx or not val_idx or not test_idx:
        raise ValueError(
            "Chronological split produced an empty partition "
            f"(train={len(train_idx)}, val={len(val_idx)}, test={len(test_idx)}); "
            "check embargo_seconds relative to capture span."
        )

    # Hard causal leakage assertions
    if train_idx and val_idx:
        if max(timestamps[i] for i in train_idx) > min(timestamps[i] for i in val_idx):
            raise TemporalLeakageError("Causal violation: Train timestamp exceeds Val timestamp.")
    if val_idx and test_idx:
        if max(timestamps[i] for i in val_idx) > min(timestamps[i] for i in test_idx):
            raise TemporalLeakageError("Causal violation: Val timestamp exceeds Test timestamp.")

    return TemporalSplitResult(
        train_indices=tuple(train_idx),
        val_indices=tuple(val_idx),
        test_indices=tuple(test_idx),
        discarded_embargo=disc_emb,
        discarded_active_endtime=disc_end,
        train_end_ts=t_tr_end,
        val_start_ts=min(timestamps[i] for i in val_idx) if val_idx else val_floor,
        val_end_ts=t_va_end,
        test_start_ts=min(timestamps[i] for i in test_idx) if test_idx else test_floor,
    )


def _sample_dirichlet(rng: random.Random, k: int, alpha: float) -> list[float]:
    draws = [rng.gammavariate(alpha, 1.0) for _ in range(k)]
    total = sum(draws)
    if total <= 0:
        return [1.0 / k] * k
    return [d / total for d in draws]


def partition_fl_clients(
    train_indices: Sequence[int],
    labels: Sequence[int],
    *,
    n_clients: int = 10,
    strategy: str = "iid",
    seed: int = 42,
    dirichlet_alpha: float = 0.5,
    quantity_sigma: float = 0.8,
    feature_scores: Sequence[float] | None = None,
    timestamps: Sequence[float] | None = None,
    val_start_ts: float | None = None,
) -> ClientPartitionResult:
    """Partition ONLY training indices into K simulated logical gateway clients."""
    if n_clients < 2:
        raise ValueError("n_clients must be >= 2.")
    if not train_indices:
        raise ValueError("train_indices cannot be empty.")

    if timestamps is not None and val_start_ts is not None:
        max_tr = max(timestamps[i] for i in train_indices)
        if max_tr >= val_start_ts:
            raise TemporalLeakageError(
                f"Client partition refused: train timestamp {max_tr} >= val_start_ts {val_start_ts}"
            )

    rng = random.Random(seed)
    buckets: list[list[int]] = [[] for _ in range(n_clients)]

    if strategy == "iid":
        by_cls: defaultdict[int, list[int]] = defaultdict(list)
        for idx in train_indices:
            by_cls[labels[idx]].append(idx)
        for idxs in by_cls.values():
            shuffled = list(idxs)
            rng.shuffle(shuffled)
            for pos, idx in enumerate(shuffled):
                buckets[pos % n_clients].append(idx)

    elif strategy == "label_skew":
        by_cls = defaultdict(list)
        for idx in train_indices:
            by_cls[labels[idx]].append(idx)
        for idxs in by_cls.values():
            shuffled = list(idxs)
            rng.shuffle(shuffled)
            props = _sample_dirichlet(rng, n_clients, dirichlet_alpha)
            cursor = 0
            for c_i, p in enumerate(props):
                cnt = (
                    int(round(p * len(shuffled))) if c_i < n_clients - 1 else len(shuffled) - cursor
                )
                cnt = max(0, min(cnt, len(shuffled) - cursor))
                buckets[c_i].extend(shuffled[cursor : cursor + cnt])
                cursor += cnt

    elif strategy == "quantity_skew":
        shuffled = list(train_indices)
        rng.shuffle(shuffled)
        weights = [rng.lognormvariate(0.0, quantity_sigma) for _ in range(n_clients)]
        wsum = sum(weights)
        cursor = 0
        for c_i, w in enumerate(weights):
            cnt = (
                int(round(len(shuffled) * w / wsum))
                if c_i < n_clients - 1
                else len(shuffled) - cursor
            )
            cnt = max(1, min(cnt, len(shuffled) - cursor))
            buckets[c_i].extend(shuffled[cursor : cursor + cnt])
            cursor += cnt

    elif strategy == "feature_skew":
        if feature_scores is None:
            raise ValueError("feature_scores required for feature_skew partitioning.")
        ranked = sorted(train_indices, key=lambda i: (feature_scores[i], i))
        chunk = max(1, math.ceil(len(ranked) / n_clients))
        for c_i in range(n_clients):
            buckets[c_i].extend(ranked[c_i * chunk : (c_i + 1) * chunk])

    elif strategy == "combined":
        by_cls = defaultdict(list)
        for idx in train_indices:
            by_cls[labels[idx]].append(idx)
        qty_w = [rng.lognormvariate(0.0, quantity_sigma) for _ in range(n_clients)]
        for idxs in by_cls.values():
            shuffled = list(idxs)
            rng.shuffle(shuffled)
            d_props = _sample_dirichlet(rng, n_clients, dirichlet_alpha)
            comb = [d * q for d, q in zip(d_props, qty_w, strict=True)]
            csum = sum(comb) or 1.0
            props = [x / csum for x in comb]
            cursor = 0
            for c_i, p in enumerate(props):
                cnt = (
                    int(round(p * len(shuffled))) if c_i < n_clients - 1 else len(shuffled) - cursor
                )
                cnt = max(0, min(cnt, len(shuffled) - cursor))
                buckets[c_i].extend(shuffled[cursor : cursor + cnt])
                cursor += cnt
    else:
        raise ValueError(f"Unsupported FL partition strategy: '{strategy}'")

    # Ensure every simulated client has at least 1 sample by borrowing from largest bucket
    for c_i in range(n_clients):
        if not buckets[c_i]:
            donor = max(range(n_clients), key=lambda k: len(buckets[k]))
            if len(buckets[donor]) > 1:
                buckets[c_i].append(buckets[donor].pop())

    client_map = {f"sim_gw_{i + 1:02d}": tuple(sorted(b)) for i, b in enumerate(buckets)}
    return ClientPartitionResult(
        strategy=strategy,
        seed=seed,
        n_clients=n_clients,
        partition_type="simulated_logical_gateway",
        client_indices=client_map,
    )
