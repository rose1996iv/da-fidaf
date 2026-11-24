"""Read-only dataset adapters for ToN-IoT, CICIoT2023, and Edge-IIoTset."""

from __future__ import annotations

import csv
import hashlib
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from dafidaf.data.schemas import (
    CICIOT2023_LABEL_ONTOLOGY,
    EDGE_IIOT_LABEL_ONTOLOGY,
    TON_IOT_LABEL_ONTOLOGY,
    TON_IOT_NUMERIC_FEATURES,
    LabelOntology,
)


class DatasetAdapterError(ValueError):
    """Raised on schema mismatch, path traversal, or invalid dataset input."""


@dataclass(frozen=True, slots=True)
class LoadedDataset:
    """In-memory bounded tabular representation with explicit provenance and quality stats."""

    dataset_id: str
    source_path: str
    source_sha256: str | None
    feature_names: tuple[str, ...]
    features: tuple[tuple[float | None, ...], ...]
    binary_labels: tuple[int, ...]
    coarse_labels: tuple[str, ...]
    timestamps: tuple[float, ...] | None
    durations: tuple[float, ...] | None
    excluded_columns: tuple[str, ...]
    missing_counts: dict[str, int]
    inf_sanitized_count: int
    exact_duplicate_count: int
    dropped_invalid_ts: int = 0
    dropped_invalid_label: int = 0


def _safe_float(raw: str) -> tuple[float | None, bool]:
    s = raw.strip()
    if not s or s == "-" or s.lower() in ("nan", "null", "none", "na", "n/a", "?"):
        return None, False
    try:
        v = float(s)
    except ValueError:
        return None, False
    if math.isnan(v):
        return None, False
    if math.isinf(v):
        return None, True
    return v, False


def _sha256_if_feasible(path: Path, max_bytes: int = 200 * 1024 * 1024) -> str | None:
    if path.stat().st_size > max_bytes:
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(4 * 1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def _validate_safe_path(path: Path, allowed_root: Path | None) -> Path:
    resolved = path.resolve()
    if not resolved.is_file():
        raise DatasetAdapterError(f"Dataset file does not exist: '{resolved}'")
    if allowed_root is not None:
        root_res = allowed_root.resolve()
        try:
            resolved.relative_to(root_res)
        except ValueError as exc:
            raise DatasetAdapterError(
                f"Path traversal blocked: '{resolved}' is outside '{root_res}'"
            ) from exc
    return resolved


class DatasetAdapter(ABC):
    """Abstract read-only dataset adapter contract."""

    dataset_id: str
    ontology: LabelOntology
    excluded_columns: tuple[str, ...]

    @abstractmethod
    def load(
        self,
        csv_path: Path,
        *,
        max_rows: int | None = None,
        allowed_root: Path | None = None,
        compute_sha256: bool = True,
    ) -> LoadedDataset:
        """Load bounded rows with strict schema validation and provenance."""


class TonIoTNetworkAdapter(DatasetAdapter):
    """Adapter for ToN-IoT Processed_Network_dataset and train_test_network.csv."""

    dataset_id = "ToN-IoT"
    ontology = TON_IOT_LABEL_ONTOLOGY
    excluded_columns = (
        "src_ip",
        "dst_ip",
        "src_port",
        "dst_port",
        "ts",
        "label",
        "type",
    )

    def load(
        self,
        csv_path: Path,
        *,
        max_rows: int | None = None,
        allowed_root: Path | None = None,
        compute_sha256: bool = True,
    ) -> LoadedDataset:
        path = _validate_safe_path(csv_path, allowed_root)
        feat_names = tuple(f.name for f in TON_IOT_NUMERIC_FEATURES)

        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                raise DatasetAdapterError(f"Empty CSV: '{path}'")
            header = [h.strip() for h in header]
            idx = {h: i for i, h in enumerate(header)}

            missing_cols = [c for c in (*feat_names, "type") if c not in idx]
            if missing_cols:
                raise DatasetAdapterError(
                    f"ToN-IoT schema validation failed; missing columns: {missing_cols}"
                )

            has_ts = "ts" in idx
            ts_list: list[float] = []
            dur_list: list[float] = []
            feat_rows: list[tuple[float | None, ...]] = []
            bin_labels: list[int] = []
            coarse_labels: list[str] = []
            missing_counts = {c: 0 for c in feat_names}
            inf_count = 0
            seen: set[tuple[float | None, ...]] = set()
            dup_count = 0
            dropped_ts = 0
            dropped_lbl = 0

            for row in reader:
                if len(row) < len(header):
                    continue
                raw_type = row[idx["type"]].strip()
                try:
                    bin_lbl = self.ontology.to_binary(raw_type)
                    coarse_lbl = self.ontology.to_coarse(raw_type)
                except ValueError:
                    dropped_lbl += 1
                    continue

                tv: float | None = None
                if has_ts:
                    tv, _ = _safe_float(row[idx["ts"]])
                    if tv is None:
                        dropped_ts += 1
                        continue

                vals: list[float | None] = []
                for c in feat_names:
                    v, is_inf = _safe_float(row[idx[c]])
                    if is_inf:
                        inf_count += 1
                    if v is None:
                        missing_counts[c] += 1
                    vals.append(v)
                vt = tuple(vals)
                if vt in seen:
                    dup_count += 1
                else:
                    seen.add(vt)
                feat_rows.append(vt)

                bin_labels.append(bin_lbl)
                coarse_labels.append(coarse_lbl)

                dur_v = vt[0] if vt[0] is not None else 0.0
                dur_list.append(dur_v)
                if has_ts and tv is not None:
                    ts_list.append(tv)

                if max_rows is not None and len(feat_rows) >= max_rows:
                    break

        return LoadedDataset(
            dataset_id=self.dataset_id,
            source_path=path.name,
            source_sha256=_sha256_if_feasible(path) if compute_sha256 else None,
            feature_names=feat_names,
            features=tuple(feat_rows),
            binary_labels=tuple(bin_labels),
            coarse_labels=tuple(coarse_labels),
            timestamps=tuple(ts_list) if has_ts else None,
            durations=tuple(dur_list),
            excluded_columns=self.excluded_columns,
            missing_counts=missing_counts,
            inf_sanitized_count=inf_count,
            exact_duplicate_count=dup_count,
            dropped_invalid_ts=dropped_ts,
            dropped_invalid_label=dropped_lbl,
        )


class CICIoT2023Adapter(DatasetAdapter):
    """Adapter for CICIoT2023 MERGED_CSV (40-column labelled) files."""

    dataset_id = "CICIoT2023"
    ontology = CICIOT2023_LABEL_ONTOLOGY
    excluded_columns = ("Label",)

    def load(
        self,
        csv_path: Path,
        *,
        max_rows: int | None = None,
        allowed_root: Path | None = None,
        compute_sha256: bool = True,
    ) -> LoadedDataset:
        path = _validate_safe_path(csv_path, allowed_root)
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                raise DatasetAdapterError(f"Empty CSV: '{path}'")
            header = [h.strip() for h in header]
            if "Label" not in header:
                raise DatasetAdapterError(
                    "CICIoT2023 adapter requires labelled MERGED_CSV containing 'Label' column."
                )
            lbl_i = header.index("Label")
            feat_names = tuple(h for h in header if h != "Label")
            feat_is = [header.index(h) for h in feat_names]

            feat_rows: list[tuple[float | None, ...]] = []
            bin_labels: list[int] = []
            coarse_labels: list[str] = []
            missing_counts = {c: 0 for c in feat_names}
            inf_count = 0
            seen: set[tuple[float | None, ...]] = set()
            dup_count = 0
            dropped_lbl = 0

            for row in reader:
                if len(row) < len(header):
                    continue
                raw_lbl = row[lbl_i].strip()
                try:
                    bin_lbl = self.ontology.to_binary(raw_lbl)
                    coarse_lbl = self.ontology.to_coarse(raw_lbl)
                except ValueError:
                    dropped_lbl += 1
                    continue
                vals: list[float | None] = []
                for name, ci in zip(feat_names, feat_is, strict=True):
                    v, is_inf = _safe_float(row[ci])
                    if is_inf:
                        inf_count += 1
                    if v is None:
                        missing_counts[name] += 1
                    vals.append(v)
                vt = tuple(vals)
                if vt in seen:
                    dup_count += 1
                else:
                    seen.add(vt)
                feat_rows.append(vt)
                bin_labels.append(bin_lbl)
                coarse_labels.append(coarse_lbl)
                if max_rows is not None and len(feat_rows) >= max_rows:
                    break

        return LoadedDataset(
            dataset_id=self.dataset_id,
            source_path=path.name,
            source_sha256=_sha256_if_feasible(path) if compute_sha256 else None,
            feature_names=feat_names,
            features=tuple(feat_rows),
            binary_labels=tuple(bin_labels),
            coarse_labels=tuple(coarse_labels),
            timestamps=None,  # Verified absent in Phase 1A
            durations=None,
            excluded_columns=self.excluded_columns,
            missing_counts=missing_counts,
            inf_sanitized_count=inf_count,
            exact_duplicate_count=dup_count,
            dropped_invalid_ts=0,
            dropped_invalid_label=dropped_lbl,
        )


class EdgeIIoTsetAdapter(DatasetAdapter):
    """Adapter for Edge-IIoTset 63-column CSVs, stripping corrupted frame.time and IPs."""

    dataset_id = "Edge-IIoTset"
    ontology = EDGE_IIOT_LABEL_ONTOLOGY
    excluded_columns = (
        "frame.time",
        "ip.src_host",
        "ip.dst_host",
        "arp.src.proto_ipv4",
        "arp.dst.proto_ipv4",
        "tcp.srcport",
        "tcp.dstport",
        "udp.port",
        "Attack_label",
        "Attack_type",
    )
    numeric_subset = (
        "arp.opcode",
        "arp.hw.size",
        "icmp.checksum",
        "icmp.seq_le",
        "http.content_length",
        "tcp.ack",
        "tcp.checksum",
        "tcp.connection.fin",
        "tcp.connection.rst",
        "tcp.connection.syn",
        "tcp.connection.synack",
        "tcp.flags",
        "tcp.len",
        "tcp.seq",
        "udp.time_delta",
        "mqtt.len",
        "mbtcp.len",
    )

    def load(
        self,
        csv_path: Path,
        *,
        max_rows: int | None = None,
        allowed_root: Path | None = None,
        compute_sha256: bool = True,
    ) -> LoadedDataset:
        path = _validate_safe_path(csv_path, allowed_root)
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                raise DatasetAdapterError(f"Empty CSV: '{path}'")
            header = [h.strip() for h in header]
            idx = {h: i for i, h in enumerate(header)}
            missing_cols = [c for c in (*self.numeric_subset, "Attack_type") if c not in idx]
            if missing_cols:
                raise DatasetAdapterError(
                    f"Edge-IIoTset schema validation failed; missing: {missing_cols}"
                )

            feat_rows: list[tuple[float | None, ...]] = []
            bin_labels: list[int] = []
            coarse_labels: list[str] = []
            missing_counts = {c: 0 for c in self.numeric_subset}
            inf_count = 0
            seen: set[tuple[float | None, ...]] = set()
            dup_count = 0
            dropped_lbl = 0

            for row in reader:
                if len(row) < len(header):
                    continue
                raw_type = row[idx["Attack_type"]].strip()
                try:
                    bin_lbl = self.ontology.to_binary(raw_type)
                    coarse_lbl = self.ontology.to_coarse(raw_type)
                except ValueError:
                    dropped_lbl += 1
                    continue
                vals: list[float | None] = []
                for c in self.numeric_subset:
                    v, is_inf = _safe_float(row[idx[c]])
                    if is_inf:
                        inf_count += 1
                    if v is None:
                        missing_counts[c] += 1
                    vals.append(v)
                vt = tuple(vals)
                if vt in seen:
                    dup_count += 1
                else:
                    seen.add(vt)
                feat_rows.append(vt)
                bin_labels.append(bin_lbl)
                coarse_labels.append(coarse_lbl)
                if max_rows is not None and len(feat_rows) >= max_rows:
                    break

        return LoadedDataset(
            dataset_id=self.dataset_id,
            source_path=path.name,
            source_sha256=_sha256_if_feasible(path) if compute_sha256 else None,
            feature_names=self.numeric_subset,
            features=tuple(feat_rows),
            binary_labels=tuple(bin_labels),
            coarse_labels=tuple(coarse_labels),
            timestamps=None,  # frame.time verified corrupted/incomplete in Phase 1A
            durations=None,
            excluded_columns=self.excluded_columns,
            missing_counts=missing_counts,
            inf_sanitized_count=inf_count,
            exact_duplicate_count=dup_count,
            dropped_invalid_ts=0,
            dropped_invalid_label=dropped_lbl,
        )
