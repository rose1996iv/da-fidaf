"""Versioned preprocessing provenance metadata (strictly secret-free)."""

from __future__ import annotations

import json
import platform
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PreprocessingProvenance:
    """Reproducible, sanitized provenance record for a DA-FIDAF data run."""

    generated_utc: str
    dataset_id: str
    source_file: str
    source_sha256: str | None
    preprocessing_version: str
    feature_schema_version: str
    label_mapping_version: str
    seed: int
    temporal_split_policy: str
    embargo_seconds: float | None
    client_partition_strategy: str
    client_partition_type: str
    python_version: str
    platform_info: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")


def build_provenance(
    *,
    dataset_id: str,
    source_file: str,
    source_sha256: str | None,
    seed: int,
    temporal_split_policy: str,
    embargo_seconds: float | None,
    client_partition_strategy: str,
    preprocessing_version: str = "phase2_v1.0",
    feature_schema_version: str = "1.0.0",
    label_mapping_version: str = "1.0.0",
) -> PreprocessingProvenance:
    return PreprocessingProvenance(
        generated_utc=datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        dataset_id=dataset_id,
        source_file=source_file,
        source_sha256=source_sha256,
        preprocessing_version=preprocessing_version,
        feature_schema_version=feature_schema_version,
        label_mapping_version=label_mapping_version,
        seed=seed,
        temporal_split_policy=temporal_split_policy,
        embargo_seconds=embargo_seconds,
        client_partition_strategy=client_partition_strategy,
        client_partition_type="simulated_logical_gateway",
        python_version=platform.python_version(),
        platform_info=platform.system(),
    )
