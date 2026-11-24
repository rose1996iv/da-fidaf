"""Gate C unit tests: synthetic drift, detectors, poisoning, Byzantine, adaptation, attribution."""

from __future__ import annotations

from dafidaf.attacks import (
    ByzantineConfig,
    PoisoningConfig,
    apply_byzantine_update,
    apply_data_poisoning,
)
from dafidaf.attribution import DriftAttackAttributor
from dafidaf.drift import (
    ContinualAdapter,
    DriftSpec,
    FeatureDriftDetector,
    PageHinkleyDetector,
    apply_synthetic_drift,
)
from dafidaf.federated import ClientUpdate
from dafidaf.models import LinearLogisticIDS


def test_synthetic_drift_schedules_and_detectors() -> None:
    x_base = [[float(i % 5) * 0.2, 0.1, -0.1] for i in range(100)]
    y_base = [i % 2 for i in range(100)]
    spec = DriftSpec(
        schedule="gradual",
        mechanism="covariate_shift",
        onset_round=3,
        duration_rounds=2,
        severity=2.0,
    )

    x_pre, _, m_pre = apply_synthetic_drift(x_base, y_base, spec, round_id=2)
    x_post, _, m_post = apply_synthetic_drift(x_base, y_base, spec, round_id=4)
    assert m_pre["intensity"] == 0.0 and x_pre == x_base
    assert m_post["intensity"] == 1.0 and m_post["is_synthetic"] is True

    det = FeatureDriftDetector(psi_threshold=0.25).fit_reference(x_base)
    assert det.detect(x_pre).drift_detected is False
    assert det.detect(x_post).drift_detected is True

    ph = PageHinkleyDetector(delta=0.005, threshold=0.15, min_samples=3)
    triggered = any(ph.update(v) for v in [0.1, 0.1, 0.1, 0.6, 0.7, 0.8])
    assert triggered is True


def test_poisoning_isolation_and_byzantine_transform() -> None:
    x_orig = [[0.5, 0.5] for _ in range(20)]
    y_orig = [0] * 10 + [1] * 10
    x_copy = [list(r) for r in x_orig]
    y_copy = list(y_orig)

    x_p, y_p, meta = apply_data_poisoning(
        x_orig, y_orig, PoisoningConfig(attack_type="label_flip", poison_fraction=0.5, seed=42)
    )
    assert x_orig == x_copy and y_orig == y_copy  # Original never mutated
    assert meta["poisoned_samples"] == 10
    assert y_p != y_orig

    upd = ClientUpdate("sim_gw_01", True, 50, (0.2, 0.3), 0.4, None, 16)
    byz_u = apply_byzantine_update(
        2,
        upd,
        ByzantineConfig(
            attack_type="sign_flip", malicious_clients=("sim_gw_01",), scale_factor=5.0
        ),
    )
    assert byz_u.delta_params == (-1.0, -1.5)


def test_attribution_distinguishes_benign_drift_malicious_and_uncertain() -> None:
    honest = [
        ClientUpdate(f"sim_gw_{i:02d}", True, 50, (0.2, 0.2, 0.1), 0.3, None, 24)
        for i in range(1, 7)
    ]
    benign_drift = ClientUpdate("sim_gw_07", True, 50, (0.3, 0.25, 0.15), 0.4, None, 24)
    byzantine = ClientUpdate("sim_gw_08", True, 50, (-2.0, -2.0, -1.0), 1.5, None, 24)
    ambiguous = ClientUpdate("sim_gw_09", True, 50, (0.01, -0.01, 0.0), 0.5, None, 24)

    decisions = DriftAttackAttributor().attribute_round(
        round_id=5,
        updates=honest + [benign_drift, byzantine, ambiguous],
        client_max_psi={"sim_gw_07": 0.85, "sim_gw_08": 0.02, "sim_gw_09": 0.40},
    )
    by_id = {d.client_id: d for d in decisions}
    assert by_id["sim_gw_07"].verdict == "benign_distribution_drift"
    assert by_id["sim_gw_08"].verdict == "malicious_byzantine_update"
    assert by_id["sim_gw_09"].verdict == "uncertain_insufficient_evidence"


def test_continual_adaptation_tracks_forgetting() -> None:
    model = LinearLogisticIDS(2, seed=42)
    x_old = [[2.0, 2.0]] * 10 + [[-2.0, -2.0]] * 10
    y_old = [1] * 10 + [0] * 10
    model.fit_local(x_old, y_old, epochs=5, lr=0.1, seed=42)

    x_new = [[1.5, 2.5]] * 10 + [[-1.5, -2.5]] * 10
    res = ContinualAdapter(strategy="replay").adapt(
        model, x_new, y_old, x_old, y_old, epochs=2, seed=42
    )
    assert res.strategy == "replay"
    assert res.new_loss_after < 0.5
