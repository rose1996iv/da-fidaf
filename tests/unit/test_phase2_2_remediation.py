"""Phase 2.2 remediation regression tests covering Acceptance Gates G1 through G7."""

from __future__ import annotations

import io
import ipaddress
import math
import os
import struct
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from dafidaf.attacks import ByzantineConfig, apply_byzantine_update
from dafidaf.attribution import DriftAttackAttributor
from dafidaf.data import (
    DatasetAdapterError,
    FlowExtractConfig,
    TemporalSplitConfig,
    TonIoTNetworkAdapter,
    TrainOnlyPreprocessor,
    chronological_split,
    extract_flows_from_zip_member,
    extract_flows_v1,
    read_sll_packets_from_stream,
)
from dafidaf.drift import PageHinkleyDetector
from dafidaf.evaluation import (
    compute_classification_metrics,
    paired_effect_size_and_ci,
    summarize_multi_seed,
)
from dafidaf.federated import (
    AggregationError,
    ClientUpdate,
    FederatedConfig,
    FederatedTrainer,
    SimulatedClient,
    aggregate_updates,
)
from dafidaf.models import LinearLogisticIDS
from dafidaf.orchestration import cli as phase2_cli
from dafidaf.orchestration import run_experiment_from_yaml
from dafidaf.privacy.mechanisms import (
    DPConfig,
    PrivacyAccountant,
    compute_rdp_gaussian_epsilon,
)


def _sll_ipv4_tcp(src_ip: str, dst_ip: str, sp: int, dp: int, flags: int = 0x02) -> bytes:
    sll = struct.pack(">HHH8sH", 0, 1, 6, b"\xaa\xbb\xcc\xdd\xee\xff\x00\x00", 0x0800)
    ip_hdr = struct.pack(
        ">BBHHHBBH4s4s",
        0x45,
        0,
        40,
        1,
        0,
        64,
        6,
        0,
        ipaddress.IPv4Address(src_ip).packed,
        ipaddress.IPv4Address(dst_ip).packed,
    )
    tcp_hdr = struct.pack(">HHIIBBHHH", sp, dp, 1, 0, 0x50, flags, 4096, 0, 0)
    return sll + ip_hdr + tcp_hdr


def _build_pcapng_sll(packets: list[tuple[int, bytes]], trailing_junk: bytes = b"") -> bytes:
    buf = bytearray()
    # SHB (28 bytes)
    buf += struct.pack("<IIIHHqI", 0x0A0D0D0A, 28, 0x1A2B3C4D, 1, 0, -1, 28)
    # IDB (20 bytes, linktype=113 SLL)
    buf += struct.pack("<IIHHII", 0x00000001, 20, 113, 0, 65535, 20)
    for ts_us, raw in packets:
        pad = (4 - (len(raw) % 4)) % 4
        blen = 32 + len(raw) + pad
        ts_hi = (ts_us >> 32) & 0xFFFFFFFF
        ts_lo = ts_us & 0xFFFFFFFF
        buf += struct.pack("<IIIIIII", 0x00000006, blen, 0, ts_hi, ts_lo, len(raw), len(raw))
        buf += raw + (b"\x00" * pad)
        buf += struct.pack("<I", blen)
    buf += trailing_junk
    return bytes(buf)


# --- G1: Data Integrity & Leakage Prevention ---


def test_a1_flow_extract_zip_stream_pcapng_and_libpcap_with_truncated_tail(tmp_path: Path) -> None:
    p1 = _sll_ipv4_tcp("10.0.0.1", "10.0.0.2", 40000, 80, flags=0x02)
    p2 = _sll_ipv4_tcp("10.0.0.2", "10.0.0.1", 80, 40000, flags=0x12)
    pcapng_bytes = _build_pcapng_sll([(1_000_000, p1), (2_000_000, p2)], trailing_junk=b"\x06\x00")

    zip_path = tmp_path / "sample_sll.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("normal_1.pcap", pcapng_bytes)

    res = extract_flows_from_zip_member(
        zip_path,
        "normal_1.pcap",
        config=FlowExtractConfig(stream_id="stream_a"),
        allowed_root=tmp_path,
    )
    assert len(res.flows) == 1
    assert res.flows[0].tot_pkts == 2
    assert res.flows[0].fwd_pkts == 1 and res.flows[0].bwd_pkts == 1
    assert res.packet_counters["dropped_truncated_tail"] == 1
    assert res.provenance["source_member"] == "normal_1.pcap"

    # Also test classic libpcap v2.4 stream with truncated tail
    libpcap = bytearray(struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 113))
    libpcap += struct.pack("<IIII", 10, 500, len(p1), len(p1)) + p1
    libpcap += b"\x01\x02\x03"  # truncated packet header
    pkts, cnts = read_sll_packets_from_stream(io.BytesIO(bytes(libpcap)))
    assert len(pkts) == 1 and pkts[0][0] == 10_000_500
    assert cnts["dropped_truncated_tail"] == 1


def test_a2_chronological_split_active_flow_exclusion_when_embargo_zero() -> None:
    ts = [float(i * 10) for i in range(20)]
    durs = [0.0] * 20
    durs[13] = 50.0  # Last train sample at t=130 ending at t=180 (crosses into val!)
    res = chronological_split(
        ts, durs, TemporalSplitConfig(embargo_seconds=0.0, exclude_active_end_time=True)
    )
    assert 13 not in res.train_indices
    assert res.discarded_active_endtime == 1


def test_a3_adapter_drops_invalid_ts_and_blank_labels_without_coercion(tmp_path: Path) -> None:
    csv_file = tmp_path / "ton_bad_rows.csv"
    csv_file.write_text(
        "ts,duration,src_bytes,dst_bytes,missed_bytes,src_pkts,src_ip_bytes,"
        "dst_pkts,dst_ip_bytes,http_request_body_len,http_response_body_len,type\n"
        "1554198358,1.0,10,20,0,1,50,1,60,0,0,normal\n"
        "bad_ts,1.0,10,20,0,1,50,1,60,0,0,ddos\n"
        "1554198360,1.0,10,20,0,1,50,1,60,0,0,\n",
        encoding="utf-8",
    )
    ds = TonIoTNetworkAdapter().load(csv_file, allowed_root=tmp_path)
    assert len(ds.features) == 1
    assert ds.dropped_invalid_ts == 1
    assert ds.dropped_invalid_label == 1


def test_a4_preprocessor_rejects_non_train_split_and_sanitizes_inf() -> None:
    pre = TrainOnlyPreprocessor()
    with pytest.raises(RuntimeError, match="non-training split"):
        pre.fit([[1.0, 2.0]], ["a", "b"], split_name="test")

    pre.fit([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]], ["a", "b"], split_name="train")
    out = pre.transform([[float("inf"), float("-inf")]])
    # Inf values are imputed to train medians (2.0, 20.0), scaling to 0.0
    assert out[0][0] == 0.0 and out[0][1] == 0.0


def test_a5_flow_extract_ipv6_ext_header_and_empty_split_rejection() -> None:
    # SLL -> IPv6 (next_hdr=0 Hop-by-Hop, len=8 -> next_hdr=17 UDP) -> UDP
    sll = struct.pack(">HHH8sH", 0, 1, 6, b"\x00" * 8, 0x86DD)
    ipv6 = struct.pack(
        ">IHBB16s16s",
        6 << 28,
        16,
        0,  # Hop-by-Hop extension header
        64,
        ipaddress.IPv6Address("2001:db8::1").packed,
        ipaddress.IPv6Address("2001:db8::2").packed,
    )
    hbh = struct.pack(">BB6s", 17, 0, b"\x00" * 6)  # next=UDP, hdr_ext_len=0 (8 bytes)
    udp = struct.pack(">HHHH", 53000, 53, 8, 0)
    pkt = sll + ipv6 + hbh + udp
    res = extract_flows_v1([(1_000_000, 0, len(pkt), pkt)])
    assert len(res.flows) == 1 and res.flows[0].protocol == 17

    with pytest.raises(ValueError, match="empty partition"):
        chronological_split(
            [float(i) for i in range(20)], None, TemporalSplitConfig(embargo_seconds=1000.0)
        )


# --- G2: Federated Aggregation & Byzantine Robustness ---


def test_b1_nan_and_inf_rejected_by_aggregators_and_quarantined_by_trainer() -> None:
    honest = [
        ClientUpdate(f"sim_gw_{i:02d}", True, 100, (0.1, 0.2), 0.3, None, 16) for i in range(1, 7)
    ]
    nan_u = ClientUpdate("sim_gw_00", True, 100, (float("nan"), 0.2), 0.3, None, 16)
    inf_u = ClientUpdate("sim_gw_99", True, 100, (float("inf"), 0.2), 0.3, None, 16)

    for method in ("fedavg", "median", "trimmed_mean", "krum", "multi_krum"):
        with pytest.raises(AggregationError, match="Non-finite"):
            aggregate_updates([nan_u] + honest, method=method, num_byzantine=1)
        with pytest.raises(AggregationError, match="Non-finite"):
            aggregate_updates(honest + [inf_u], method=method, num_byzantine=1)

    # Trainer quarantines NaN Byzantine update and completes cleanly
    x_d = [[1.5, 1.5]] * 10 + [[-1.5, -1.5]] * 10
    y_d = [1] * 10 + [0] * 10
    clients = [SimulatedClient(f"sim_gw_{i:02d}", x_d, y_d) for i in range(1, 8)]

    def nan_hook(_r: int, u: ClientUpdate) -> ClientUpdate:
        if u.client_id == "sim_gw_01":
            return ClientUpdate(
                u.client_id, True, u.num_samples, (float("nan"), 0.0, 0.0), 1.0, None, 24
            )
        return u

    model = LinearLogisticIDS(2, seed=42)
    trainer = FederatedTrainer(
        model,
        clients,
        FederatedConfig(rounds=2, aggregation="krum", num_byzantine=1),
        update_hook=nan_hook,
    )
    hist = trainer.run()
    assert hist[0].rejected_nonfinite_clients == ("sim_gw_01",)
    assert all(math.isfinite(p) for p in model.get_parameters())


def test_b2_local_dp_preserves_byzantine_scaling_and_central_dp_clips() -> None:
    x_d = [[1.5, 1.5]] * 10 + [[-1.5, -1.5]] * 10
    y_d = [1] * 10 + [0] * 10
    clients = [SimulatedClient(f"sim_gw_{i:02d}", x_d, y_d) for i in range(1, 5)]
    byz = ByzantineConfig(
        attack_type="scaled_update", malicious_clients=("sim_gw_01",), scale_factor=20.0
    )

    def hook(r: int, u: ClientUpdate) -> ClientUpdate:
        return apply_byzantine_update(r, u, byz)

    # local_per_client: malicious client's 20x scaled update is NOT clipped by honest local DP
    t_local = FederatedTrainer(
        LinearLogisticIDS(2, seed=42),
        clients,
        FederatedConfig(
            rounds=1,
            dp=DPConfig(
                enabled=True, max_grad_norm=0.5, noise_multiplier=0.5, dp_scope="local_per_client"
            ),
        ),
        update_hook=hook,
    )
    h_local = t_local.run()
    byz_upd = next(u for u in h_local[0].client_updates if u.client_id == "sim_gw_01")
    norm_byz = math.sqrt(sum(v * v for v in byz_upd.delta_params))
    assert norm_byz > 2.0  # Unclipped by honest client DP

    # central_aggregate: server clips before aggregation so model parameters stay bounded
    m_central = LinearLogisticIDS(2, seed=42)
    t_central = FederatedTrainer(
        m_central,
        clients,
        FederatedConfig(
            rounds=1,
            dp=DPConfig(
                enabled=True, max_grad_norm=0.5, noise_multiplier=0.5, dp_scope="central_aggregate"
            ),
        ),
        update_hook=hook,
    )
    t_central.run()
    assert all(math.isfinite(p) and abs(p) < 5.0 for p in m_central.get_parameters())


def test_b3_and_b4_aggregator_validation_and_checkpoint_roundtrip(tmp_path: Path) -> None:
    zero_u = ClientUpdate("sim_gw_01", True, 0, (0.1, 0.2), 0.3, None, 16)
    with pytest.raises(AggregationError, match="num_samples"):
        aggregate_updates([zero_u], method="fedavg")

    good = [
        ClientUpdate(f"sim_gw_{i:02d}", True, 10, (0.1, 0.2), 0.3, None, 16) for i in range(1, 6)
    ]
    with pytest.raises(AggregationError, match="num_byzantine"):
        aggregate_updates(good, method="multi_krum", num_byzantine=-1)

    x_d = [[1.0, 1.0]] * 6 + [[-1.0, -1.0]] * 6
    y_d = [1] * 6 + [0] * 6
    m = LinearLogisticIDS(2, seed=7)
    tr = FederatedTrainer(
        m,
        [SimulatedClient("sim_gw_01", x_d, y_d)],
        FederatedConfig(rounds=1),
        checkpoint_dir=tmp_path,
    )
    tr.run()
    loaded = FederatedTrainer.load_checkpoint(tmp_path / "checkpoint_round_001.json")
    assert loaded["round_id"] == 1 and loaded["n_features"] == 2
    assert loaded["parameters"] == m.get_parameters()


# --- G3: Exact RDP Privacy Accounting ---


def test_p1_rdp_accountant_valid_across_all_sigma_and_rejects_invalid_delta() -> None:
    with pytest.raises(ValueError, match="delta"):
        DPConfig(enabled=True, max_grad_norm=1.0, noise_multiplier=1.0, delta=0.0)
    with pytest.raises(ValueError, match="delta"):
        DPConfig(enabled=True, max_grad_norm=1.0, noise_multiplier=1.0, delta=1.5)

    # Verify closed-form RDP minimum matches fine numerical grid search over alpha > 1 for sigma=0.5
    sigma, delta, rounds = 0.5, 1e-5, 5
    eps_exact = compute_rdp_gaussian_epsilon(rounds=rounds, noise_multiplier=sigma, delta=delta)
    grid_min = min(
        rounds * a / (2.0 * sigma * sigma) + math.log(1.0 / delta) / (a - 1.0)
        for a in [1.005 + 0.005 * k for k in range(1, 2000)]
    )
    assert eps_exact <= grid_min + 1e-9
    assert abs(eps_exact - grid_min) < 1e-4

    acc = PrivacyAccountant(
        DPConfig(enabled=True, max_grad_norm=1.0, noise_multiplier=sigma, delta=delta)
    )
    for _ in range(rounds):
        acc.step()
    summary = acc.summary()
    assert abs(float(summary["cumulative_epsilon_upper"]) - eps_exact) < 1e-5  # type: ignore[arg-type]
    assert summary["formal_deployment_dp_claim"] is False
    assert summary["secure_aggregation_active"] is False


# --- G4: Drift & Attack Attribution Validity ---


def test_c1_attributor_detects_scaled_update_and_nan_with_zero_far() -> None:
    honest = [
        ClientUpdate(f"sim_gw_{i:02d}", True, 100, (0.1, 0.1, 0.1, 0.1), 0.3, None, 32)
        for i in range(1, 9)
    ]
    scaled = ClientUpdate(
        "sim_gw_09", True, 100, (1.0, 1.0, 1.0, 1.0), 0.3, None, 32
    )  # +10x cos=1.0
    nan_u = ClientUpdate("sim_gw_10", True, 100, (float("nan"), 0.1, 0.1, 0.1), 0.3, None, 32)
    decs = DriftAttackAttributor().attribute_round(
        2, honest + [scaled, nan_u], client_max_psi={f"sim_gw_{i:02d}": 0.02 for i in range(1, 11)}
    )
    by_id = {d.client_id: d.verdict for d in decs}
    assert by_id["sim_gw_09"] == "malicious_model_update"
    assert by_id["sim_gw_10"] == "malicious_byzantine_update"
    assert all(not by_id[f"sim_gw_{i:02d}"].startswith("malicious_") for i in range(1, 9))


def test_c2_byzantine_random_update_deterministic_across_pythonhashseed() -> None:
    code = (
        "from dafidaf.federated.client import ClientUpdate;"
        "from dafidaf.attacks.simulators import ByzantineConfig, apply_byzantine_update;"
        "u = ClientUpdate('sim_gw_01', True, 50, (0.1, 0.2, 0.3), 0.5, None, 24);"
        "c = ByzantineConfig("
        "attack_type='random_update', malicious_clients=('sim_gw_01',), seed=42);"
        "print(apply_byzantine_update(1, u, c).delta_params)"
    )
    repo_src = str(Path(__file__).resolve().parents[2] / "src")
    env1 = {**os.environ, "PYTHONHASHSEED": "1", "PYTHONPATH": repo_src}
    env2 = {**os.environ, "PYTHONHASHSEED": "999", "PYTHONPATH": repo_src}
    out1 = subprocess.check_output([sys.executable, "-c", code], env=env1, text=True).strip()
    out2 = subprocess.check_output([sys.executable, "-c", code], env=env2, text=True).strip()
    assert out1 == out2


def test_c3_page_hinkley_reset_rearms_detector() -> None:
    ph = PageHinkleyDetector(delta=0.005, threshold=0.15, min_samples=3)
    assert any(ph.update(v) for v in [0.1, 0.1, 0.1, 0.7, 0.8]) is True
    ph.reset()
    assert ph.update(0.1) is False
    assert ph.update(0.1) is False


# --- G5: Evaluation & Statistical Validity ---


def test_d2_and_d3_pr_auc_tie_invariance_and_stats_guards() -> None:
    m1 = compute_classification_metrics([1, 1, 0, 0], [1, 1, 1, 1], [0.5, 0.5, 0.5, 0.5])
    m2 = compute_classification_metrics([0, 0, 1, 1], [1, 1, 1, 1], [0.5, 0.5, 0.5, 0.5])
    assert m1.pr_auc == 0.5 and m2.pr_auc == 0.5

    s2 = summarize_multi_seed([0.80, 0.90])
    assert s2.statistically_valid is False and s2.ci95_low is None

    pe = paired_effect_size_and_ci([0.80, 0.80, 0.80], [0.90, 0.90, 0.90])
    assert pe["mean_diff"] == 0.1 and pe["cohens_d_paired"] is None


# --- G6 & G7: Real YAML Execution & CLI Path Containment ---


def test_d1_real_yaml_refuses_silent_synthetic_fallback_and_runs_real_fixture(
    tmp_path: Path,
) -> None:
    # 1. Refuses silent fallback to synthetic when --dataset-csv is omitted
    cfg_path = tmp_path / "e1_test.yaml"
    cfg_path.write_text(
        "experiment_id: E1\n"
        "seed: 42\n"
        "seeds_multi_run: [42, 101, 202]\n"
        "datasets:\n"
        "  primary: ToN-IoT (fixture)\n"
        "temporal_protocol:\n"
        "  split_ratios: [0.70, 0.15, 0.15]\n"
        "  embargo_seconds: 10\n"
        "federation:\n"
        "  n_clients: 4\n"
        "  rounds: 2\n"
        "  aggregation: trimmed_mean\n"
        "  partition_strategy: iid\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Refusing silent fallback to synthetic"):
        run_experiment_from_yaml(cfg_path)

    # 2. Rejects unknown YAML keys cleanly
    bad_cfg = tmp_path / "bad.yaml"
    bad_cfg.write_text("experiment_id: E1\nunknown_bogus_key: 123\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported top-level keys"):
        run_experiment_from_yaml(bad_cfg)

    # 3. Executes real adapter on ToN-IoT CSV fixture + multi-seed + non-overwriting run dirs
    csv_path = tmp_path / "ton_fixture.csv"
    lines = [
        "ts,duration,src_bytes,dst_bytes,missed_bytes,src_pkts,src_ip_bytes,"
        "dst_pkts,dst_ip_bytes,http_request_body_len,http_response_body_len,type"
    ]
    for i in range(60):
        ts = 1554198000 + i * 20
        is_atk = i % 3 == 0
        sbytes = 5000 + i if is_atk else 50 + (i % 10)
        lbl = "ddos" if is_atk else "normal"
        lines.append(f"{ts},1.0,{sbytes},100,0,5,{sbytes + 40},2,140,0,0,{lbl}")
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    runs_dir = tmp_path / "runs"
    out = run_experiment_from_yaml(
        cfg_path,
        runs_root=runs_dir,
        dataset_csv=csv_path,
        allowed_root=tmp_path,
        multi_seed=True,
    )
    assert out["mode"] == "real_dataset"
    assert out["seeds"] == [42, 101, 202]
    assert out["multi_seed_macro_f1"]["statistically_valid"] is True  # type: ignore[index]
    runs = out["runs"]
    assert isinstance(runs, list) and len(runs) == 3
    assert runs[0]["data_source"] == "REAL_DATASET"
    assert runs[0]["aggregation"] == "trimmed_mean"
    assert len({r["run_id"] for r in runs}) == 3  # Unique non-overwriting run_ids


def test_s1_cli_validate_dataset_blocks_path_outside_dataset_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    allowed = tmp_path / "allowed_data"
    allowed.mkdir()
    outside_csv = tmp_path / "outside.csv"
    outside_csv.write_text("Header_Length,Label\n54,BENIGN\n", encoding="utf-8")

    monkeypatch.setenv("DAFIDAF_DATA_ROOT", str(allowed))
    with pytest.raises(DatasetAdapterError, match="Path traversal"):
        phase2_cli.main(["validate-dataset", "--family", "ciciot2023", "--csv", str(outside_csv)])
