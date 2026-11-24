"""Explainable Drift-vs-Attack Attribution Engine for DA-FIDAF.

Treats attribution as an empirical research hypothesis with explicit uncertainty:
never forces a malicious verdict when evidence is ambiguous.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from dafidaf.federated.aggregation import coordinate_median, filter_finite_updates
from dafidaf.federated.client import ClientUpdate


@dataclass(frozen=True, slots=True)
class AttributionConfig:
    """Evidence thresholds for drift-vs-attack attribution."""

    psi_drift_threshold: float = 0.25
    norm_ratio_malicious_threshold: float = 3.5
    norm_ratio_severe_threshold: float = 6.0
    cosine_inversion_threshold: float = -0.25
    cosine_benign_min: float = 0.10
    min_global_drift_fraction: float = 0.30
    val_loss_poison_delta: float = 0.03
    val_loss_excess_over_median: float = 0.02


@dataclass(frozen=True, slots=True)
class AttributionEvidence:
    """Structured per-client, per-round evidence record."""

    round_id: int
    client_id: str
    feature_max_psi: float | None
    update_l2_norm: float
    median_l2_norm: float
    norm_ratio_to_median: float
    cosine_to_median: float
    fraction_clients_drifting: float
    val_loss_delta: float | None = None
    val_loss_excess: float | None = None


@dataclass(frozen=True, slots=True)
class AttributionDecision:
    """Explainable attribution output with confidence and uncertainty."""

    round_id: int
    client_id: str
    verdict: str
    confidence: float
    uncertainty: float
    evidence: AttributionEvidence
    rationale: str


def _l2_norm(vec: Sequence[float]) -> float:
    return math.sqrt(sum(v * v for v in vec))


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    na = _l2_norm(a)
    nb = _l2_norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return sum(x * y for x, y in zip(a, b, strict=True)) / (na * nb)


class DriftAttackAttributor:
    """Distinguishes benign distribution drift from malicious updates/poisoning."""

    def __init__(self, config: AttributionConfig | None = None) -> None:
        self.config = config or AttributionConfig()

    def attribute_round(
        self,
        round_id: int,
        updates: Sequence[ClientUpdate],
        *,
        client_max_psi: Mapping[str, float] | None = None,
        client_val_loss_delta: Mapping[str, float] | None = None,
    ) -> list[AttributionDecision]:
        if not updates:
            return []
        cfg = self.config
        finite_updates, _ = filter_finite_updates(updates)
        med = (
            coordinate_median(finite_updates)
            if finite_updates
            else [0.0] * len(updates[0].delta_params)
        )
        med_norm = _l2_norm(med)
        eps = 1e-9

        psi_map = client_max_psi or {}
        vloss_map = client_val_loss_delta or {}
        finite_vloss = sorted(
            v for u in finite_updates if (v := vloss_map.get(u.client_id)) is not None
        )
        if finite_vloss:
            mid = len(finite_vloss) // 2
            med_vloss: float | None = (
                finite_vloss[mid]
                if len(finite_vloss) % 2 == 1
                else 0.5 * (finite_vloss[mid - 1] + finite_vloss[mid])
            )
        else:
            med_vloss = None

        drifting_cnt = sum(
            1 for u in updates if psi_map.get(u.client_id, 0.0) >= cfg.psi_drift_threshold
        )
        drift_frac = drifting_cnt / len(updates)

        decisions: list[AttributionDecision] = []
        for u in updates:
            feat_psi = psi_map.get(u.client_id)
            v_delta = vloss_map.get(u.client_id)
            v_excess = (
                (v_delta - med_vloss) if (v_delta is not None and med_vloss is not None) else None
            )
            if not all(math.isfinite(v) for v in u.delta_params):
                ev = AttributionEvidence(
                    round_id=round_id,
                    client_id=u.client_id,
                    feature_max_psi=round(feat_psi, 6) if feat_psi is not None else None,
                    update_l2_norm=math.inf,
                    median_l2_norm=round(med_norm, 6),
                    norm_ratio_to_median=math.inf,
                    cosine_to_median=0.0,
                    fraction_clients_drifting=round(drift_frac, 4),
                    val_loss_delta=round(v_delta, 6) if v_delta is not None else None,
                    val_loss_excess=round(v_excess, 6) if v_excess is not None else None,
                )
                decisions.append(
                    AttributionDecision(
                        round_id=round_id,
                        client_id=u.client_id,
                        verdict="malicious_byzantine_update",
                        confidence=0.99,
                        uncertainty=0.01,
                        evidence=ev,
                        rationale="Non-finite (NaN/Inf) parameter update detected.",
                    )
                )
                continue

            u_norm = _l2_norm(u.delta_params)
            norm_ratio = u_norm / max(med_norm, eps)
            cos_sim = _cosine(u.delta_params, med)

            ev = AttributionEvidence(
                round_id=round_id,
                client_id=u.client_id,
                feature_max_psi=round(feat_psi, 6) if feat_psi is not None else None,
                update_l2_norm=round(u_norm, 6),
                median_l2_norm=round(med_norm, 6),
                norm_ratio_to_median=round(norm_ratio, 4),
                cosine_to_median=round(cos_sim, 4),
                fraction_clients_drifting=round(drift_frac, 4),
                val_loss_delta=round(v_delta, 6) if v_delta is not None else None,
                val_loss_excess=round(v_excess, 6) if v_excess is not None else None,
            )

            has_feat_drift = feat_psi is not None and feat_psi >= cfg.psi_drift_threshold
            has_val_harm = (
                v_delta is not None
                and v_excess is not None
                and v_delta >= cfg.val_loss_poison_delta
                and v_excess >= cfg.val_loss_excess_over_median
            )
            has_val_benign = v_delta is not None and v_excess is not None and v_excess <= 0.005

            # 1. Clear Byzantine sign-flip or norm explosion without benign feature drift
            is_inverted = cos_sim <= cfg.cosine_inversion_threshold
            is_norm_extreme = norm_ratio >= cfg.norm_ratio_malicious_threshold
            is_norm_severe = norm_ratio >= cfg.norm_ratio_severe_threshold
            if is_inverted and is_norm_extreme and not has_val_benign:
                verdict = "malicious_byzantine_update"
                excess = min(5.0, norm_ratio - cfg.norm_ratio_malicious_threshold)
                conf = min(0.95, 0.70 + 0.05 * excess)
                rationale = (
                    f"Inverted update direction (cos={cos_sim:.3f}) with extreme norm ratio "
                    f"({norm_ratio:.2f}x median)."
                )
            elif (
                is_norm_extreme
                and (cos_sim < cfg.cosine_benign_min or is_norm_severe)
                and not has_feat_drift
                and not has_val_benign
            ):
                verdict = "malicious_model_update"
                excess = min(5.0, norm_ratio - cfg.norm_ratio_malicious_threshold)
                conf = min(0.90, 0.65 + 0.05 * excess)
                rationale = (
                    f"Extreme update norm ({norm_ratio:.2f}x median, cos={cos_sim:.3f}) "
                    "without corroborating feature distribution shift."
                )
            elif has_val_harm and (cos_sim < 0.50 or norm_ratio >= 1.2):
                verdict = "malicious_data_poisoning"
                conf = min(0.90, 0.72 + min(0.18, v_excess or 0.0))
                rationale = (
                    f"Clean-validation loss degradation (delta={v_delta:.4f}, "
                    f"excess={v_excess:.4f} over cohort median; cos={cos_sim:.3f}, "
                    f"max_psi={feat_psi}); flags poisoning even when feature noise elevates PSI."
                )
            elif (
                cos_sim <= -0.55 and norm_ratio >= 1.5 and not has_feat_drift and not has_val_benign
            ):
                verdict = "malicious_data_poisoning"
                conf = 0.72
                rationale = (
                    f"Strongly opposing update direction (cos={cos_sim:.3f}, "
                    f"norm_ratio={norm_ratio:.2f}x) on a stationary feature distribution "
                    "(consistent with label-flip/data poisoning)."
                )
            elif has_feat_drift and cos_sim >= cfg.cosine_benign_min and not is_norm_extreme:
                verdict = "benign_distribution_drift"
                conf = 0.80 if drift_frac >= cfg.min_global_drift_fraction else 0.65
                rationale = (
                    f"Observed feature shift (max_psi={feat_psi:.3f}) accompanied by coherent "
                    f"update alignment (cos={cos_sim:.3f}, norm_ratio={norm_ratio:.2f}x)."
                )
            elif not has_feat_drift and cos_sim >= cfg.cosine_benign_min and norm_ratio < 2.0:
                verdict = "normal_aligned_update"
                conf = 0.85
                rationale = (
                    "Update aligned with cohort median under stationary feature distribution."
                )
            else:
                verdict = "uncertain_insufficient_evidence"
                conf = 0.40
                rationale = (
                    f"Ambiguous evidence (cos={cos_sim:.3f}, norm_ratio={norm_ratio:.2f}x, "
                    f"max_psi={feat_psi}, val_loss_delta={v_delta}); abstaining."
                )

            decisions.append(
                AttributionDecision(
                    round_id=round_id,
                    client_id=u.client_id,
                    verdict=verdict,
                    confidence=round(conf, 4),
                    uncertainty=round(1.0 - conf, 4),
                    evidence=ev,
                    rationale=rationale,
                )
            )
        return decisions
