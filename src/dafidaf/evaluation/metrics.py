"""Imbalanced-IDS classification metrics, attribution metrics, and multi-seed statistics."""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class ClassificationMetrics:
    """Comprehensive binary IDS metrics prioritizing Macro-F1 and FPR/FNR."""

    n_samples: int
    accuracy: float
    precision: float
    recall: float
    f1: float
    macro_f1: float
    weighted_f1: float
    fpr: float
    fnr: float
    roc_auc: float | None
    pr_auc: float | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _compute_roc_auc(y_true: Sequence[int], y_scores: Sequence[float]) -> float | None:
    pos = [s for y, s in zip(y_true, y_scores, strict=True) if y == 1]
    neg = [s for y, s in zip(y_true, y_scores, strict=True) if y == 0]
    if not pos or not neg:
        return None
    # Mann-Whitney U rank statistic (exact with tie handling)
    pairs = sorted(zip(y_scores, y_true, strict=True), key=lambda x: x[0])
    n = len(pairs)
    rank_sum_pos = 0.0
    i = 0
    while i < n:
        j = i
        while j + 1 < n and pairs[j + 1][0] == pairs[i][0]:
            j += 1
        avg_rank = 0.5 * (i + j) + 1.0
        for k in range(i, j + 1):
            if pairs[k][1] == 1:
                rank_sum_pos += avg_rank
        i = j + 1
    n_pos = len(pos)
    n_neg = len(neg)
    u = rank_sum_pos - n_pos * (n_pos + 1) / 2.0
    return round(u / (n_pos * n_neg), 6)


def _compute_pr_auc(y_true: Sequence[int], y_scores: Sequence[float]) -> float | None:
    """Average Precision (step-function PR-AUC) with order-invariant tie grouping."""
    n_pos = sum(1 for y in y_true if y == 1)
    if n_pos == 0:
        return None
    pairs = sorted(zip(y_scores, y_true, strict=True), key=lambda x: x[0], reverse=True)
    tp = 0
    fp = 0
    ap = 0.0
    prev_rec = 0.0
    i = 0
    n = len(pairs)
    while i < n:
        score = pairs[i][0]
        j = i
        while j < n and pairs[j][0] == score:
            if pairs[j][1] == 1:
                tp += 1
            else:
                fp += 1
            j += 1
        rec = tp / n_pos
        prec = tp / (tp + fp)
        ap += (rec - prev_rec) * prec
        prev_rec = rec
        i = j
    return round(ap, 6)


def compute_classification_metrics(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    y_scores: Sequence[float] | None = None,
) -> ClassificationMetrics:
    n = len(y_true)
    if n == 0 or len(y_pred) != n:
        raise ValueError("y_true and y_pred must be non-empty and equal length.")

    tp = sum(1 for yt, yp in zip(y_true, y_pred, strict=True) if yt == 1 and yp == 1)
    tn = sum(1 for yt, yp in zip(y_true, y_pred, strict=True) if yt == 0 and yp == 0)
    fp = sum(1 for yt, yp in zip(y_true, y_pred, strict=True) if yt == 0 and yp == 1)
    fn = sum(1 for yt, yp in zip(y_true, y_pred, strict=True) if yt == 1 and yp == 0)

    acc = (tp + tn) / n
    prec1 = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec1 = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1_1 = (2 * prec1 * rec1 / (prec1 + rec1)) if (prec1 + rec1) > 0 else 0.0

    prec0 = tn / (tn + fn) if (tn + fn) > 0 else 0.0
    rec0 = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    f1_0 = (2 * prec0 * rec0 / (prec0 + rec0)) if (prec0 + rec0) > 0 else 0.0

    macro_f1 = 0.5 * (f1_0 + f1_1)
    n_pos = tp + fn
    n_neg = tn + fp
    weighted_f1 = (n_neg * f1_0 + n_pos * f1_1) / n
    fpr = fp / n_neg if n_neg > 0 else 0.0
    fnr = fn / n_pos if n_pos > 0 else 0.0

    roc = _compute_roc_auc(y_true, y_scores) if y_scores is not None else None
    pr = _compute_pr_auc(y_true, y_scores) if y_scores is not None else None

    return ClassificationMetrics(
        n_samples=n,
        accuracy=round(acc, 6),
        precision=round(prec1, 6),
        recall=round(rec1, 6),
        f1=round(f1_1, 6),
        macro_f1=round(macro_f1, 6),
        weighted_f1=round(weighted_f1, 6),
        fpr=round(fpr, 6),
        fnr=round(fnr, 6),
        roc_auc=roc,
        pr_auc=pr,
    )


@dataclass(frozen=True, slots=True)
class AttributionMetrics:
    """Evaluation of malicious-vs-benign attribution quality."""

    total_clients: int
    malicious_precision: float
    malicious_recall: float
    false_attribution_rate: float
    uncertain_rate: float


def compute_attribution_metrics(
    true_malicious_clients: set[str],
    decisions: Sequence[tuple[str, str]],
) -> AttributionMetrics:
    """Evaluate attribution decisions `(client_id, verdict)` against known malicious clients."""
    if not decisions:
        raise ValueError("decisions cannot be empty.")
    tp = fp = fn = tn = uncertain = 0
    for cid, verdict in decisions:
        is_true_mal = cid in true_malicious_clients
        if verdict == "uncertain_insufficient_evidence":
            uncertain += 1
            if is_true_mal:
                fn += 1
            else:
                tn += 1
            continue
        pred_mal = verdict.startswith("malicious_")
        if pred_mal and is_true_mal:
            tp += 1
        elif pred_mal and not is_true_mal:
            fp += 1
        elif not pred_mal and is_true_mal:
            fn += 1
        else:
            tn += 1

    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    far = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    return AttributionMetrics(
        total_clients=len(decisions),
        malicious_precision=round(prec, 4),
        malicious_recall=round(rec, 4),
        false_attribution_rate=round(far, 4),
        uncertain_rate=round(uncertain / len(decisions), 4),
    )


@dataclass(frozen=True, slots=True)
class MultiSeedSummary:
    """Multi-seed mean, std, and 95% bootstrap CI (refuses significance claims for n < 2)."""

    n_seeds: int
    mean: float
    std: float
    ci95_low: float | None
    ci95_high: float | None
    statistically_valid: bool


def summarize_multi_seed(
    values: Sequence[float], *, seed: int = 42, n_boot: int = 500
) -> MultiSeedSummary:
    n = len(values)
    if n == 0:
        raise ValueError("values cannot be empty.")
    mean = sum(values) / n
    if n < 2:
        return MultiSeedSummary(
            n_seeds=n,
            mean=round(mean, 6),
            std=0.0,
            ci95_low=None,
            ci95_high=None,
            statistically_valid=False,
        )
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    std = math.sqrt(var)
    if n < 3:
        # Percentile bootstrap with n=2 has only 4 resamples (~50% coverage, not 95%).
        return MultiSeedSummary(
            n_seeds=n,
            mean=round(mean, 6),
            std=round(std, 6),
            ci95_low=None,
            ci95_high=None,
            statistically_valid=False,
        )
    rng = random.Random(seed)
    boots = sorted(sum(rng.choice(values) for _ in range(n)) / n for _ in range(n_boot))
    lo = boots[int(0.025 * (n_boot - 1))]
    hi = boots[int(0.975 * (n_boot - 1))]
    return MultiSeedSummary(
        n_seeds=n,
        mean=round(mean, 6),
        std=round(std, 6),
        ci95_low=round(lo, 6),
        ci95_high=round(hi, 6),
        statistically_valid=True,
    )


def paired_effect_size_and_ci(
    baseline: Sequence[float],
    treatment: Sequence[float],
    *,
    seed: int = 42,
    n_boot: int = 500,
) -> dict[str, float | None]:
    """Paired mean difference, paired Cohen's d, and 95% bootstrap CI."""
    if len(baseline) != len(treatment) or len(baseline) < 2:
        return {"mean_diff": None, "cohens_d_paired": None, "ci95_low": None, "ci95_high": None}
    diffs = [t - b for b, t in zip(baseline, treatment, strict=True)]
    n = len(diffs)
    md = sum(diffs) / n
    sd = math.sqrt(sum((x - md) ** 2 for x in diffs) / (n - 1))
    if sd > 1e-12:
        d_val: float | None = round(md / sd, 6)
    elif abs(md) <= 1e-12:
        d_val = 0.0
    else:
        # Constant nonzero difference -> variance is 0, Cohen's d is undefined/infinite.
        d_val = None
    if n < 3:
        return {
            "mean_diff": round(md, 6),
            "cohens_d_paired": d_val,
            "ci95_low": None,
            "ci95_high": None,
        }
    rng = random.Random(seed)
    boots = sorted(sum(rng.choice(diffs) for _ in range(n)) / n for _ in range(n_boot))
    return {
        "mean_diff": round(md, 6),
        "cohens_d_paired": d_val,
        "ci95_low": round(boots[int(0.025 * (n_boot - 1))], 6),
        "ci95_high": round(boots[int(0.975 * (n_boot - 1))], 6),
    }
