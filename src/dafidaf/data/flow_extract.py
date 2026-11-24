"""Production `flow_extract_v1` module for LINKTYPE_LINUX_SLL (113) captures.

Preserves the Phase 1F/1G validated design:
- Supports PCAPNG v1.0 and classic libpcap v2.4 with LINKTYPE_LINUX_SLL (113).
- Explicitly drops and counts SLL 0x0003 (ETH_P_ALL), ARP, fragments, and EOF tails.
- Canonical bidirectional 5-tuples with deterministic causal flow eviction.
- Explicit `null` for 1-packet IAT and UDP TCP-flag features.
- Stream A and Stream B must remain separated via `stream_id`.
"""

from __future__ import annotations

import ipaddress
import json
import math
import struct
import zipfile
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO

from dafidaf.data.adapters import _validate_safe_path

FLOW_EXTRACT_VERSION = "flow_extract_v1.0"
SUPPORTED_LINKTYPE_SLL = 113


@dataclass(frozen=True, slots=True)
class FlowExtractConfig:
    """Configuration for deterministic `flow_extract_v1` extraction."""

    stream_id: str = "stream_a"
    idle_timeout_s: int = 120
    active_timeout_s: int = 600
    source_archive_sha256: str | None = None


@dataclass(frozen=True, slots=True)
class FlowRecord:
    """Single extracted bidirectional TCP/UDP flow record with explicit null semantics."""

    stream_id: str
    first_ts_us: int
    last_ts_us: int
    protocol: int
    src_port: int
    dst_port: int
    duration_s: float
    tot_pkts: int
    fwd_pkts: int
    bwd_pkts: int
    tot_bytes: int
    fwd_bytes: int
    bwd_bytes: int
    pkt_len_min: int
    pkt_len_mean: float
    pkt_len_max: int
    pkt_len_std: float
    iat_mean_s: float | None
    iat_max_s: float | None
    iat_std_s: float | None
    tcp_syn_cnt: int | None
    tcp_ack_cnt: int | None
    tcp_fin_cnt: int | None
    tcp_rst_cnt: int | None
    tcp_psh_cnt: int | None


@dataclass(frozen=True, slots=True)
class FlowExtractResult:
    """Extraction output plus packet-accounting provenance."""

    flows: tuple[FlowRecord, ...]
    packet_counters: dict[str, int]
    provenance: dict[str, object]

    def write_provenance_sidecar(self, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(self.provenance, indent=2) + "\n", encoding="utf-8")


def extract_flows_v1(
    packets: Sequence[tuple[int, int, int, bytes]],
    config: FlowExtractConfig | None = None,
) -> FlowExtractResult:
    """Deterministically extract bidirectional flows from SLL (113) packet tuples.

    Args:
        packets: Sequence of `(ts_us, packet_index, orig_len, raw_sll_bytes)`.
        config: Flow extraction configuration.
    """
    cfg = config or FlowExtractConfig()
    ordered = sorted(packets, key=lambda x: (x[0], x[1]))
    counters: Counter[str] = Counter()
    idle_us = cfg.idle_timeout_s * 1_000_000
    active_us = cfg.active_timeout_s * 1_000_000

    active: dict[tuple[tuple[str, int], tuple[str, int], int], dict[str, object]] = {}
    completed: list[FlowRecord] = []

    def finalize(st: dict[str, object]) -> FlowRecord:
        n = int(st["tot_pkts"])  # type: ignore[arg-type]
        first_ts = int(st["first_ts"])  # type: ignore[arg-type]
        last_ts = int(st["last_ts"])  # type: ignore[arg-type]
        lens: list[int] = st["lens"]  # type: ignore[assignment]
        iats: list[float] = st["iats"]  # type: ignore[assignment]
        l_mean = sum(lens) / n
        l_var = sum((x - l_mean) ** 2 for x in lens) / (n - 1) if n > 1 else 0.0
        if iats:
            i_mean: float | None = round(sum(iats) / len(iats), 6)
            i_max: float | None = round(max(iats), 6)
            i_std: float | None = round(
                math.sqrt(sum((x - sum(iats) / len(iats)) ** 2 for x in iats) / (len(iats) - 1))
                if len(iats) > 1
                else 0.0,
                6,
            )
        else:
            i_mean = i_max = i_std = None
        proto = int(st["proto"])  # type: ignore[arg-type]
        is_tcp = proto == 6
        return FlowRecord(
            stream_id=cfg.stream_id,
            first_ts_us=first_ts,
            last_ts_us=last_ts,
            protocol=proto,
            src_port=int(st["fwd_sport"]),  # type: ignore[arg-type]
            dst_port=int(st["fwd_dport"]),  # type: ignore[arg-type]
            duration_s=round((last_ts - first_ts) / 1_000_000.0, 6),
            tot_pkts=n,
            fwd_pkts=int(st["fwd_pkts"]),  # type: ignore[arg-type]
            bwd_pkts=int(st["bwd_pkts"]),  # type: ignore[arg-type]
            tot_bytes=int(st["tot_bytes"]),  # type: ignore[arg-type]
            fwd_bytes=int(st["fwd_bytes"]),  # type: ignore[arg-type]
            bwd_bytes=int(st["bwd_bytes"]),  # type: ignore[arg-type]
            pkt_len_min=min(lens),
            pkt_len_mean=round(l_mean, 4),
            pkt_len_max=max(lens),
            pkt_len_std=round(math.sqrt(l_var), 4),
            iat_mean_s=i_mean,
            iat_max_s=i_max,
            iat_std_s=i_std,
            tcp_syn_cnt=int(st["syn"]) if is_tcp else None,  # type: ignore[arg-type]
            tcp_ack_cnt=int(st["ack"]) if is_tcp else None,  # type: ignore[arg-type]
            tcp_fin_cnt=int(st["fin"]) if is_tcp else None,  # type: ignore[arg-type]
            tcp_rst_cnt=int(st["rst"]) if is_tcp else None,  # type: ignore[arg-type]
            tcp_psh_cnt=int(st["psh"]) if is_tcp else None,  # type: ignore[arg-type]
        )

    for ts_us, _pkt_idx, orig_len, pkt in ordered:
        counters["total_input_packets"] += 1
        if len(pkt) < 16:
            counters["dropped_sll_short"] += 1
            continue
        ethertype = struct.unpack_from(">H", pkt, 14)[0]
        if ethertype == 0x0003:
            counters["dropped_sll_0x0003"] += 1
            continue
        if ethertype == 0x0806:
            counters["dropped_arp"] += 1
            continue

        l3 = pkt[16:]
        if ethertype == 0x0800:
            if len(l3) < 20 or (l3[0] >> 4) != 4:
                counters["dropped_ipv4_malformed"] += 1
                continue
            ihl = (l3[0] & 0x0F) * 4
            if ihl < 20 or len(l3) < ihl:
                counters["dropped_ipv4_malformed"] += 1
                continue
            flags_frag = struct.unpack_from(">H", l3, 6)[0]
            if (flags_frag & 0x1FFF) > 0:
                counters["dropped_noninitial_fragment"] += 1
                continue
            l4_p = l3[9]
            sip = str(ipaddress.IPv4Address(l3[12:16]))
            dip = str(ipaddress.IPv4Address(l3[16:20]))
            l4 = l3[ihl:]
        elif ethertype == 0x86DD:
            if len(l3) < 40 or (l3[0] >> 4) != 6:
                counters["dropped_ipv6_malformed"] += 1
                continue
            sip = str(ipaddress.IPv6Address(l3[8:24]))
            dip = str(ipaddress.IPv6Address(l3[24:40]))
            l4_p = l3[6]
            offset = 40
            ext_hops = 0
            while l4_p in (0, 43, 60) and ext_hops < 6:
                if len(l3) < offset + 2:
                    l4_p = -1
                    break
                next_hdr = l3[offset]
                hdr_len = (l3[offset + 1] + 1) * 8
                if len(l3) < offset + hdr_len:
                    l4_p = -1
                    break
                l4_p = next_hdr
                offset += hdr_len
                ext_hops += 1
            if l4_p == -1:
                counters["dropped_ipv6_malformed"] += 1
                continue
            if l4_p == 44:
                counters["dropped_ipv6_fragment"] += 1
                continue
            if l4_p in (0, 43, 60):
                counters["dropped_ipv6_ext_limit"] += 1
                continue
            l4 = l3[offset:]
        else:
            counters["dropped_unsupported_ethertype"] += 1
            continue

        if l4_p not in (6, 17):
            counters["dropped_non_tcp_udp"] += 1
            continue
        if (l4_p == 6 and len(l4) < 20) or (l4_p == 17 and len(l4) < 8):
            counters["dropped_l4_short"] += 1
            continue

        sp, dp = struct.unpack_from(">HH", l4, 0)
        tcp_flags = l4[13] if l4_p == 6 else 0
        ep1, ep2 = (sip, sp), (dip, dp)
        fkey = (min(ep1, ep2), max(ep1, ep2), l4_p)
        counters["accepted_tcp_udp_packets"] += 1

        st = active.get(fkey)
        if st is not None:
            last_ts = int(st["last_ts"])  # type: ignore[arg-type]
            first_ts = int(st["first_ts"])  # type: ignore[arg-type]
            if (ts_us - last_ts) > idle_us or (ts_us - first_ts) > active_us:
                completed.append(finalize(st))
                st = None

        if st is None:
            active[fkey] = {
                "first_ts": ts_us,
                "last_ts": ts_us,
                "proto": l4_p,
                "fwd_ep": ep1,
                "fwd_sport": sp,
                "fwd_dport": dp,
                "tot_pkts": 1,
                "fwd_pkts": 1,
                "bwd_pkts": 0,
                "tot_bytes": orig_len,
                "fwd_bytes": orig_len,
                "bwd_bytes": 0,
                "lens": [orig_len],
                "iats": [],
                "syn": 1 if (tcp_flags & 0x02) else 0,
                "ack": 1 if (tcp_flags & 0x10) else 0,
                "fin": 1 if (tcp_flags & 0x01) else 0,
                "rst": 1 if (tcp_flags & 0x04) else 0,
                "psh": 1 if (tcp_flags & 0x08) else 0,
            }
        else:
            last_ts = int(st["last_ts"])  # type: ignore[arg-type]
            st["iats"].append(max(0.0, (ts_us - last_ts) / 1_000_000.0))  # type: ignore[union-attr]
            st["last_ts"] = ts_us
            st["tot_pkts"] = int(st["tot_pkts"]) + 1  # type: ignore[arg-type]
            st["tot_bytes"] = int(st["tot_bytes"]) + orig_len  # type: ignore[arg-type]
            st["lens"].append(orig_len)  # type: ignore[union-attr]
            if ep1 == st["fwd_ep"]:
                st["fwd_pkts"] = int(st["fwd_pkts"]) + 1  # type: ignore[arg-type]
                st["fwd_bytes"] = int(st["fwd_bytes"]) + orig_len  # type: ignore[arg-type]
            else:
                st["bwd_pkts"] = int(st["bwd_pkts"]) + 1  # type: ignore[arg-type]
                st["bwd_bytes"] = int(st["bwd_bytes"]) + orig_len  # type: ignore[arg-type]
            if l4_p == 6:
                if tcp_flags & 0x02:
                    st["syn"] = int(st["syn"]) + 1  # type: ignore[arg-type]
                if tcp_flags & 0x10:
                    st["ack"] = int(st["ack"]) + 1  # type: ignore[arg-type]
                if tcp_flags & 0x01:
                    st["fin"] = int(st["fin"]) + 1  # type: ignore[arg-type]
                if tcp_flags & 0x04:
                    st["rst"] = int(st["rst"]) + 1  # type: ignore[arg-type]
                if tcp_flags & 0x08:
                    st["psh"] = int(st["psh"]) + 1  # type: ignore[arg-type]

    for st in active.values():
        completed.append(finalize(st))

    completed.sort(key=lambda r: (r.first_ts_us, r.protocol, r.src_port, r.dst_port, r.tot_pkts))
    provenance: dict[str, object] = {
        "spec_version": FLOW_EXTRACT_VERSION,
        "generated_utc": datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "supported_linktype": SUPPORTED_LINKTYPE_SLL,
        "config": asdict(cfg),
        "packet_counters": dict(counters),
        "extracted_flow_count": len(completed),
    }
    return FlowExtractResult(
        flows=tuple(completed),
        packet_counters=dict(counters),
        provenance=provenance,
    )


def read_sll_packets_from_stream(
    stream: BinaryIO,
    *,
    max_packets: int | None = None,
) -> tuple[list[tuple[int, int, int, bytes]], dict[str, int]]:
    """Read LINKTYPE_LINUX_SLL (113) packets from a PCAPNG v1.0 or classic libpcap stream.

    Strictly read-only; handles incomplete trailing records/blocks via explicit counters.
    """
    counters: Counter[str] = Counter()
    packets: list[tuple[int, int, int, bytes]] = []
    magic_bytes = stream.read(4)
    if len(magic_bytes) < 4:
        counters["dropped_truncated_tail"] += 1
        return packets, dict(counters)

    # 1. PCAPNG v1.0 (Section Header Block magic = 0x0A0D0D0A)
    if magic_bytes == b"\x0a\x0d\x0d\x0a":
        endian = "<"
        if_linktypes: list[int] = []
        if_tsresol_us: list[float] = []
        pkt_idx = 0
        first_block = True

        while True:
            if first_block:
                btype_raw = magic_bytes
                first_block = False
            else:
                btype_raw = stream.read(4)
                if not btype_raw:
                    break
                if len(btype_raw) < 4:
                    counters["dropped_truncated_tail"] += 1
                    break

            blen_raw = stream.read(4)
            if len(blen_raw) < 4:
                counters["dropped_truncated_tail"] += 1
                break

            if btype_raw == b"\x0a\x0d\x0d\x0a":
                # Peek byte-order magic inside SHB body to determine endianness
                bom_raw = stream.read(4)
                if len(bom_raw) < 4:
                    counters["dropped_truncated_tail"] += 1
                    break
                if bom_raw == b"\x4d\x3c\x2b\x1a":
                    endian = "<"
                elif bom_raw == b"\x1a\x2b\x3c\x4d":
                    endian = ">"
                else:
                    counters["dropped_malformed_block"] += 1
                    break
                blen = struct.unpack(f"{endian}I", blen_raw)[0]
                if blen < 28:
                    counters["dropped_malformed_block"] += 1
                    break
                rest = stream.read(blen - 12)
                if len(rest) < blen - 12:
                    counters["dropped_truncated_tail"] += 1
                    break
                if_linktypes = []
                if_tsresol_us = []
                counters["pcapng_shb_blocks"] += 1
                continue

            btype = struct.unpack(f"{endian}I", btype_raw)[0]
            blen = struct.unpack(f"{endian}I", blen_raw)[0]
            if blen < 12:
                counters["dropped_malformed_block"] += 1
                break
            body_and_tail = stream.read(blen - 8)
            if len(body_and_tail) < blen - 8:
                counters["dropped_truncated_tail"] += 1
                break
            body = body_and_tail[:-4]

            if btype == 0x00000001:  # Interface Description Block (IDB)
                if len(body) < 8:
                    counters["dropped_malformed_block"] += 1
                    continue
                linktype = struct.unpack_from(f"{endian}H", body, 0)[0]
                if_linktypes.append(linktype)
                if_tsresol_us.append(1.0)  # Default 10^-6 s = 1 us
                counters["pcapng_idb_blocks"] += 1
            elif btype == 0x00000006:  # Enhanced Packet Block (EPB)
                if len(body) < 20:
                    counters["dropped_malformed_block"] += 1
                    continue
                iface_id, ts_hi, ts_lo, cap_len, orig_len = struct.unpack_from(
                    f"{endian}IIIII", body, 0
                )
                if (
                    iface_id >= len(if_linktypes)
                    or if_linktypes[iface_id] != SUPPORTED_LINKTYPE_SLL
                ):
                    counters["dropped_unsupported_linktype"] += 1
                    continue
                if len(body) < 20 + cap_len:
                    counters["dropped_truncated_tail"] += 1
                    break
                ts_raw = (ts_hi << 32) | ts_lo
                ts_us = int(round(ts_raw * if_tsresol_us[iface_id]))
                raw_pkt = body[20 : 20 + cap_len]
                packets.append((ts_us, pkt_idx, orig_len, raw_pkt))
                pkt_idx += 1
                if max_packets is not None and len(packets) >= max_packets:
                    break
            elif btype == 0x00000003:  # Simple Packet Block (SPB)
                if not if_linktypes or if_linktypes[0] != SUPPORTED_LINKTYPE_SLL:
                    counters["dropped_unsupported_linktype"] += 1
                    continue
                if len(body) < 4:
                    counters["dropped_malformed_block"] += 1
                    continue
                orig_len = struct.unpack_from(f"{endian}I", body, 0)[0]
                packets.append((0, pkt_idx, orig_len, body[4:]))
                pkt_idx += 1
                if max_packets is not None and len(packets) >= max_packets:
                    break
            else:
                counters["pcapng_other_blocks"] += 1
        return packets, dict(counters)

    # 2. Classic libpcap v2.4
    magic_le = struct.unpack("<I", magic_bytes)[0]
    if magic_le == 0xA1B2C3D4:
        endian, is_ns = "<", False
    elif magic_le == 0xD4C3B2A1:
        endian, is_ns = ">", False
    elif magic_le == 0xA1B23C4D:
        endian, is_ns = "<", True
    elif magic_le == 0x4D3CB2A1:
        endian, is_ns = ">", True
    else:
        raise ValueError(f"Unsupported capture magic bytes: {magic_bytes.hex()}")

    ghdr_rest = stream.read(20)
    if len(ghdr_rest) < 20:
        counters["dropped_truncated_tail"] += 1
        return packets, dict(counters)
    _vmaj, _vmin, _tz, _sig, _snap, linktype = struct.unpack(f"{endian}HHiiii", ghdr_rest)
    if (linktype & 0x0FFFFFFF) != SUPPORTED_LINKTYPE_SLL:
        raise ValueError(
            f"Unsupported libpcap linktype {linktype}; expected LINKTYPE_LINUX_SLL (113)."
        )

    pkt_idx = 0
    while True:
        phdr = stream.read(16)
        if not phdr:
            break
        if len(phdr) < 16:
            counters["dropped_truncated_tail"] += 1
            break
        ts_sec, ts_sub, incl_len, orig_len = struct.unpack(f"{endian}IIII", phdr)
        raw_pkt = stream.read(incl_len)
        if len(raw_pkt) < incl_len:
            counters["dropped_truncated_tail"] += 1
            break
        ts_us = ts_sec * 1_000_000 + (ts_sub // 1000 if is_ns else ts_sub)
        packets.append((ts_us, pkt_idx, orig_len, raw_pkt))
        pkt_idx += 1
        if max_packets is not None and len(packets) >= max_packets:
            break

    return packets, dict(counters)


def extract_flows_from_zip_member(
    zip_path: Path,
    member_name: str,
    *,
    config: FlowExtractConfig | None = None,
    allowed_root: Path | None = None,
    max_packets: int | None = None,
) -> FlowExtractResult:
    """Stream a PCAPNG/libpcap member directly from a ZIP archive without disk extraction."""
    safe_zip = _validate_safe_path(zip_path, allowed_root)
    with zipfile.ZipFile(safe_zip, "r") as zf:
        with zf.open(member_name, "r") as member_stream:
            pkts, container_counters = read_sll_packets_from_stream(
                member_stream, max_packets=max_packets
            )
    res = extract_flows_v1(pkts, config=config)
    merged_counters = dict(res.packet_counters)
    for k, v in container_counters.items():
        merged_counters[k] = merged_counters.get(k, 0) + v
    merged_prov = dict(res.provenance)
    merged_prov["source_zip"] = safe_zip.name
    merged_prov["source_member"] = member_name
    merged_prov["packet_counters"] = merged_counters
    return FlowExtractResult(
        flows=res.flows,
        packet_counters=merged_counters,
        provenance=merged_prov,
    )
