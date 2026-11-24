"""Workstream A: Data engineering, schemas, adapters, flow extraction, and partitioning."""

from dafidaf.data.adapters import (
    CICIoT2023Adapter,
    DatasetAdapter,
    DatasetAdapterError,
    EdgeIIoTsetAdapter,
    LoadedDataset,
    TonIoTNetworkAdapter,
)
from dafidaf.data.flow_extract import (
    FLOW_EXTRACT_VERSION,
    FlowExtractConfig,
    FlowExtractResult,
    extract_flows_from_zip_member,
    extract_flows_v1,
    read_sll_packets_from_stream,
)
from dafidaf.data.partitioning import (
    ClientPartitionResult,
    TemporalLeakageError,
    TemporalSplitConfig,
    TemporalSplitResult,
    chronological_split,
    deduplicate_event_flows,
    partition_fl_clients,
)
from dafidaf.data.preprocessing import PreprocessorConfig, TrainOnlyPreprocessor
from dafidaf.data.provenance import PreprocessingProvenance, build_provenance
from dafidaf.data.schemas import (
    E5OntologyBlockedError,
    FeatureSpec,
    LabelOntology,
    assert_cross_dataset_ontology_ready,
)

__all__ = [
    "CICIoT2023Adapter",
    "ClientPartitionResult",
    "DatasetAdapter",
    "DatasetAdapterError",
    "E5OntologyBlockedError",
    "EdgeIIoTsetAdapter",
    "FLOW_EXTRACT_VERSION",
    "FeatureSpec",
    "FlowExtractConfig",
    "FlowExtractResult",
    "LabelOntology",
    "LoadedDataset",
    "PreprocessingProvenance",
    "PreprocessorConfig",
    "TemporalLeakageError",
    "TemporalSplitConfig",
    "TemporalSplitResult",
    "TonIoTNetworkAdapter",
    "TrainOnlyPreprocessor",
    "assert_cross_dataset_ontology_ready",
    "build_provenance",
    "chronological_split",
    "deduplicate_event_flows",
    "extract_flows_from_zip_member",
    "extract_flows_v1",
    "partition_fl_clients",
    "read_sll_packets_from_stream",
]
