"""Gate A unit tests: adapters, schemas, preprocessing, flow_extract_v1, splits, partitions."""

from __future__ import annotations

import ipaddress
import struct
from pathlib import Path

import pytest

from dafidaf.data import (
    CICIoT2023Adapter,
    DatasetAdapterError,
    E5OntologyBlockedError,
    EdgeIIoTsetAdapter,
    FlowExtractConfig,
    TemporalLeakageError,
    TemporalSplitConfig,
    TonIoTNetworkAdapter,
    TrainOnlyPreprocessor,
    assert_cross_dataset_ontology_ready,
    build_provenance,
    chronological_split,
    deduplicate_event_flows,
    extract_flows_v1,
    partition_fl_clients,
)
from dafidaf.data.schemas import (
    CICIOT2023_LABEL_ONTOLOGY,
    EDGE_IIOT_LABEL_ONTOLOGY,
    TON_IOT_LABEL_ONTOLOGY,
)


def _make_sll_ipv4_tcp(src_ip: str, dst_ip: str, sp: int, dp: int, flags: int = 0x02) -> bytes:
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
    tcp_hdr = struct.pack(">HHIIBBHHH", sp, dp, 1, 0, 0x50, flags, 8192, 0, 0)
    return sll + ip_hdr + tcp_hdr


def _make_sll_ipv4_udp(src_ip: str, dst_ip: str, sp: int, dp: int) -> bytes:
    sll = struct.pack(">HHH8sH", 0, 1, 6, b"\xaa\xbb\xcc\xdd\xee\xff\x00\x00", 0x0800)
    ip_hdr = struct.pack(
        ">BBHHHBBH4s4s",
        0x45,
        0,
        28,
        2,
        0,
        64,
        17,
        0,
        ipaddress.IPv4Address(src_ip).packed,
        ipaddress.IPv4Address(dst_ip).packed,
    )
    udp_hdr = struct.pack(">HHHH", sp, dp, 8, 0)
    return sll + ip_hdr + udp_hdr


def test_ton_iot_adapter_loads_and_sanitizes(tmp_path: Path) -> None:
    csv_file = tmp_path / "ton_sample.csv"
    csv_file.write_text(
        "ts,src_ip,src_port,dst_ip,dst_port,duration,src_bytes,dst_bytes,missed_bytes,"
        "src_pkts,src_ip_bytes,dst_pkts,dst_ip_bytes,http_request_body_len,"
        "http_response_body_len,label,type\n"
        "1554198358,10.0.0.1,1234,10.0.0.2,80,1.5,100,200,0,2,140,2,240,0,0,0,normal\n"
        "1554198360,10.0.0.1,1235,10.0.0.2,80,inf,50,0,0,1,90,0,0,-,0,1,ddos\n",
        encoding="utf-8",
    )
    ds = TonIoTNetworkAdapter().load(csv_file, allowed_root=tmp_path)
    assert len(ds.features) == 2
    assert ds.binary_labels == (0, 1)
    assert ds.coarse_labels == ("benign", "dos_ddos")
    assert ds.timestamps == (1554198358.0, 1554198360.0)
    assert ds.inf_sanitized_count == 1
    assert ds.missing_counts["duration"] == 1
    assert ds.missing_counts["http_request_body_len"] == 1
    assert ds.source_sha256 is not None


def test_adapter_blocks_path_traversal(tmp_path: Path) -> None:
    sub = tmp_path / "allowed"
    sub.mkdir()
    outside = tmp_path / "outside.csv"
    outside.write_text("Label,f1\nBENIGN,1.0\n", encoding="utf-8")
    with pytest.raises(DatasetAdapterError, match="Path traversal"):
        CICIoT2023Adapter().load(outside, allowed_root=sub)


def test_edge_and_ciciot_adapters_and_e5_gate(tmp_path: Path) -> None:
    cic = tmp_path / "cic.csv"
    cic.write_text(
        "Header_Length,Rate,Label\n54,10.0,BENIGN\n54,99.0,DDOS-SYN_FLOOD\n", encoding="utf-8"
    )
    ds_c = CICIoT2023Adapter().load(cic)
    assert ds_c.timestamps is None
    assert ds_c.binary_labels == (0, 1)

    edge_cols = list(EdgeIIoTsetAdapter.numeric_subset) + [
        "frame.time",
        "ip.src_host",
        "Attack_type",
    ]
    row1 = ["0"] * len(EdgeIIoTsetAdapter.numeric_subset) + ["6.0", "192.168.0.1", "Normal"]
    row2 = ["1"] * len(EdgeIIoTsetAdapter.numeric_subset) + [
        "192.168.0.1",
        "192.168.0.2",
        "DDoS_UDP",
    ]
    edge = tmp_path / "edge.csv"
    edge.write_text(
        ",".join(edge_cols) + "\n" + ",".join(row1) + "\n" + ",".join(row2) + "\n",
        encoding="utf-8",
    )
    ds_e = EdgeIIoTsetAdapter().load(edge)
    assert ds_e.timestamps is None
    assert ds_e.binary_labels == (0, 1)
    assert "frame.time" in ds_e.excluded_columns

    with pytest.raises(E5OntologyBlockedError):
        assert_cross_dataset_ontology_ready(
            (TON_IOT_LABEL_ONTOLOGY, CICIOT2023_LABEL_ONTOLOGY, EDGE_IIOT_LABEL_ONTOLOGY)
        )


def test_train_only_preprocessor_does_not_leak_test_data() -> None:
    x_tr = [[1.0, 10.0], [2.0, None], [3.0, 20.0], [4.0, 30.0]]
    x_te = [[1000.0, 9999.0]]
    pre = TrainOnlyPreprocessor().fit(x_tr, ["a", "b"])
    st_before = pre.state
    _ = pre.transform(x_te)
    assert pre.state == st_before
    # Missingness indicator added for col "b"
    out = pre.transform([[2.0, None]])
    assert len(out[0]) == 3
    assert out[0][2] == 1.0


def test_flow_extract_v1_handles_0003_arp_tcp_udp_and_determinism() -> None:
    pkt_0003 = struct.pack(">HHH8sH", 4, 1, 6, b"\x00" * 8, 0x0003) + b"\x0f\x00" * 20
    pkt_arp = struct.pack(">HHH8sH", 1, 1, 6, b"\x00" * 8, 0x0806) + b"\x00" * 28
    pkt_tcp1 = _make_sll_ipv4_tcp("10.0.0.1", "10.0.0.2", 50000, 1883, flags=0x02)
    pkt_tcp2 = _make_sll_ipv4_tcp("10.0.0.2", "10.0.0.1", 1883, 50000, flags=0x12)
    pkt_udp1 = _make_sll_ipv4_udp("10.0.0.5", "10.0.0.6", 55000, 53)

    stream = [
        (1_000_000, 0, len(pkt_0003), pkt_0003),
        (1_100_000, 1, len(pkt_arp), pkt_arp),
        (2_000_000, 2, len(pkt_tcp1), pkt_tcp1),
        (2_500_000, 3, len(pkt_tcp2), pkt_tcp2),
        (3_000_000, 4, len(pkt_udp1), pkt_udp1),
    ]
    cfg = FlowExtractConfig(stream_id="stream_a", idle_timeout_s=120)
    r1 = extract_flows_v1(stream, cfg)
    r2 = extract_flows_v1(list(reversed(stream)), cfg)

    assert r1.flows == r2.flows
    assert r1.packet_counters["dropped_sll_0x0003"] == 1
    assert r1.packet_counters["dropped_arp"] == 1
    assert len(r1.flows) == 2

    tcp_f = next(f for f in r1.flows if f.protocol == 6)
    udp_f = next(f for f in r1.flows if f.protocol == 17)
    assert tcp_f.fwd_pkts == 1 and tcp_f.bwd_pkts == 1
    assert tcp_f.tcp_syn_cnt == 2 and tcp_f.iat_mean_s == 0.5
    assert udp_f.tcp_syn_cnt is None and udp_f.iat_mean_s is None


def test_chronological_split_embargo_dedup_and_fl_partitions(tmp_path: Path) -> None:
    ts = [1000.0 + i * 100.0 for i in range(100)]
    durs = [500.0 if i == 69 else 1.0 for i in range(100)]
    feats = [[1.0, 2.0] for _ in range(100)]
    # Event dedup preserves recurring identical features at distinct timestamps
    kept = deduplicate_event_flows(ts, feats)
    assert len(kept) == 100

    split = chronological_split(ts, durs, TemporalSplitConfig(embargo_seconds=300.0))
    assert split.discarded_embargo > 0
    assert split.discarded_active_endtime == 1
    assert max(ts[i] for i in split.train_indices) + 300.0 <= min(ts[i] for i in split.val_indices)

    labels = [i % 2 for i in range(100)]
    for strat in ("iid", "label_skew", "quantity_skew", "combined"):
        part = partition_fl_clients(
            split.train_indices,
            labels,
            n_clients=10,
            strategy=strat,
            seed=42,
            timestamps=ts,
            val_start_ts=split.val_start_ts,
        )
        assert part.partition_type == "simulated_logical_gateway"
        assert all(cid.startswith("sim_gw_") for cid in part.client_indices)

    with pytest.raises(TemporalLeakageError):
        partition_fl_clients(
            list(split.train_indices) + [split.val_indices[0]],
            labels,
            n_clients=5,
            timestamps=ts,
            val_start_ts=split.val_start_ts,
        )

    prov = build_provenance(
        dataset_id="ToN-IoT",
        source_file="sample.csv",
        source_sha256="abc123",
        seed=42,
        temporal_split_policy="70_15_15",
        embargo_seconds=300.0,
        client_partition_strategy="label_skew",
    )
    out_p = tmp_path / "prov.json"
    prov.write_json(out_p)
    assert out_p.is_file()
