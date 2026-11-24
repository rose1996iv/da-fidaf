"""Phase 3B.2 unit regression tests: LF checksums, attribution v2, genuine E6 ablation."""

from __future__ import annotations

import hashlib
from pathlib import Path

from dafidaf.attacks import ByzantineConfig, apply_byzantine_update
from dafidaf.attribution import AttributionConfig, DriftAttackAttributor
from dafidaf.federated import ClientUpdate, FederatedConfig, FederatedTrainer, SimulatedClient
from dafidaf.models import LinearLogisticIDS
from dafidaf.orchestration.runner import _write_run_report


def test_lf_canonical_sha256_matches_raw_disk_bytes(tmp_path: Path) -> None:
    run_dir = _write_run_report(tmp_path, "test_lf_run", {"metric": 0.75, "ok": True})
    rep = run_dir / "run_report.json"
    sha_file = run_dir / "run_report.sha256"

    raw_bytes = rep.read_bytes()
    assert b"\r\n" not in raw_bytes
    actual_sha = hashlib.sha256(raw_bytes).hexdigest()
    recorded_sha = sha_file.read_text(encoding="utf-8").strip().split()[0]
    assert actual_sha == recorded_sha


def test_attribution_v2_catches_feature_noise_poisoning_and_protects_honest_noniid() -> None:
    att = DriftAttackAttributor(
        AttributionConfig(val_loss_poison_delta=0.03, val_loss_excess_over_median=0.02)
    )
    honest = [
        ClientUpdate(f"sim_gw_{i:02d}", True, 100, (0.1, 0.1, 0.1), 0.3, None, 24)
        for i in range(1, 8)
    ]
    # Honest Non-IID minority client with extreme norm/angle but benign val_loss_delta
    honest_skewed = ClientUpdate("sim_gw_08", True, 50, (-0.5, -0.5, -0.5), 0.3, None, 24)
    # Benign covariate-drifted client (high PSI, aligned, benign val_loss_delta)
    benign_drift = ClientUpdate("sim_gw_09", True, 100, (0.15, 0.12, 0.10), 0.3, None, 24)
    # Feature-noise poisoned client (high PSI = 2.5 mimics drift, but spikes clean val loss!)
    noise_poison = ClientUpdate("sim_gw_10", True, 100, (0.05, -0.05, 0.02), 0.6, None, 24)

    psis = {f"sim_gw_{i:02d}": 0.02 for i in range(1, 9)}
    psis["sim_gw_09"] = 1.80
    psis["sim_gw_10"] = 2.50

    vdeltas = {f"sim_gw_{i:02d}": -0.01 for i in range(1, 8)}
    vdeltas["sim_gw_08"] = -0.008  # Benign on clean validation
    vdeltas["sim_gw_09"] = -0.005  # Benign drift on clean validation
    vdeltas["sim_gw_10"] = 0.085  # Harms clean validation!

    decs = att.attribute_round(
        3,
        honest + [honest_skewed, benign_drift, noise_poison],
        client_max_psi=psis,
        client_val_loss_delta=vdeltas,
    )
    by_id = {d.client_id: d.verdict for d in decs}
    assert by_id["sim_gw_10"] == "malicious_data_poisoning"
    assert by_id["sim_gw_09"] == "benign_distribution_drift"
    assert not by_id["sim_gw_08"].startswith("malicious_")


def test_genuine_attribution_ablation_code_isolation() -> None:
    x_d = [[2.0, 2.0]] * 12 + [[-2.0, -2.0]] * 12
    y_d = [1] * 12 + [0] * 12
    clients = [SimulatedClient(f"sim_gw_{i:02d}", x_d, y_d) for i in range(1, 7)]
    byz = ByzantineConfig(
        attack_type="sign_flip", malicious_clients=("sim_gw_01",), scale_factor=10.0
    )

    def hook(r: int, u: ClientUpdate) -> ClientUpdate:
        return apply_byzantine_update(r, u, byz)

    # 1. without_attribution: attribution_filter is None -> 0 calls, 0 quarantined
    m_no_attr = LinearLogisticIDS(2, seed=42)
    t_no_attr = FederatedTrainer(
        m_no_attr,
        clients,
        FederatedConfig(rounds=3, aggregation="fedavg", seed=42),
        update_hook=hook,
        attribution_filter=None,
    )
    h_no_attr = t_no_attr.run()
    assert all(r.quarantined_attributed_clients == () for r in h_no_attr)

    # 2. full_dafidaf: attribution_filter genuinely quarantines flagged malicious client
    call_count = 0
    att = DriftAttackAttributor()

    def attr_filter(r_id: int, _gparams, ups):
        nonlocal call_count
        call_count += 1
        decs = att.attribute_round(r_id, ups)
        bad = {d.client_id for d in decs if d.verdict.startswith("malicious_")}
        kept = [u for u in ups if u.client_id not in bad]
        return kept, sorted(bad)

    m_full = LinearLogisticIDS(2, seed=42)
    t_full = FederatedTrainer(
        m_full,
        clients,
        FederatedConfig(rounds=3, aggregation="fedavg", seed=42),
        update_hook=hook,
        attribution_filter=attr_filter,
    )
    h_full = t_full.run()
    assert call_count == 3
    assert any("sim_gw_01" in r.quarantined_attributed_clients for r in h_full)
    # Quarantining the sign-flip attacker measurably alters global parameters vs without_attribution
    assert m_full.get_parameters() != m_no_attr.get_parameters()
